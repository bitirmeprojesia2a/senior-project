"""
Hybrid retrieval for RAG.

Combines:
- BM25 keyword search
- Chroma semantic search
- Optional cross-encoder reranking
"""

from __future__ import annotations

import re
import time
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Optional

import structlog
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from src.core.config import settings
from src.core.constants import Department, academic_schedule_collection_name, collection_name_for_department
from src.core.text_normalization import normalize_text
from src.rag.candidate_utils import (
    deduplicate_candidate_dicts,
    deduplicate_documents,
    merge_chunk_texts,
    parse_sub_chunk_position,
    sort_candidates_by_score,
)
from src.rag.query_cache import _QueryCache as _SharedQueryCache
from src.rag.llm_query_expander import LLMQueryExpander
from src.rag.query_preprocessor import QueryPreprocessor
from src.rag.search_planner import (
    OFF_TOPIC_PENALTY as _SHARED_OFF_TOPIC_PENALTY,
    _CAP_PRIMARY_TOPICS as _SHARED_CAP_PRIMARY_TOPICS,
    _apply_education_level_penalty as _shared_apply_education_level_penalty,
    _apply_finance_source_penalty as _shared_apply_finance_source_penalty,
    _apply_query_profile_source_bias as _shared_apply_query_profile_source_bias,
    _looks_like_schedule_query as _shared_looks_like_schedule_query,
    _apply_source_relevance as _shared_apply_source_relevance,
    _apply_student_affairs_faq_bias as _shared_apply_student_affairs_faq_bias,
    _detect_query_topic as _shared_detect_query_topic,
    _detect_student_affairs_query_profile as _shared_detect_student_affairs_query_profile,
    _plan_search_departments as _shared_plan_search_departments,
    _score_departments as _shared_score_departments,
)

if TYPE_CHECKING:
    from src.rag.embedder import Embedder
    from src.rag.indexer import ChromaIndexer
    from src.rag.reranker import CrossEncoderReranker

logger = structlog.get_logger()


_PUNCTUATION_RE = re.compile(r"[^\w\s]")
_WHITESPACE_RE = re.compile(r"\s+")
_COMPOUND_SPLITS = {
    "anadal": "ana dal",
    "yandal": "yan dal",
    "ciftanadal": "cift ana dal",
    "çiftanadal": "çift ana dal",
    "onkosul": "on kosul",
    "önkoşul": "ön koşul",
    "onsart": "on sart",
    "önşart": "ön şart",
}

_AUGMENTATION_PREFIX_RE = re.compile(
    r"^(?:[\w\s/çğıöşüÇĞİÖŞÜ]+\s+(?:bolumu/programi|baglami|Fakultesi)\s+icin:\s*)+",
    re.IGNORECASE,
)
_FAQ_QUESTION_RE = re.compile(r"^\s*(?:\d+[\.\)]\s*)?(.{10,120}\?)\s*$", re.MULTILINE)
_FAQ_SOURCE_PATTERNS = ("sik_sorulan", "sikca_sorulan", "sss", "faq")
_FAQ_LOW_WEIGHT_WORDS = frozenset({
    "ne", "nasil", "nerede", "neden", "hangi", "kim", "kac",
    "mi", "mu", "icin", "ile", "ve", "bir", "var", "yok",
    "olur", "olmali", "gerekir", "yapmali", "kayit",
    "ogrenci", "universite", "belge", "bilgi",
})


def _strip_augmentation_prefix(query: str) -> str:
    """Remove orchestrator-injected prefixes so the reranker sees a clean query."""
    stripped = _AUGMENTATION_PREFIX_RE.sub("", query).strip()
    return stripped if len(stripped) >= 5 else query


def _faq_word_weight(word: str) -> float:
    return 0.3 if word in _FAQ_LOW_WEIGHT_WORDS else 1.0


def _is_faq_source(source: str) -> bool:
    lowered = normalize_text(source)
    return any(pattern in lowered for pattern in _FAQ_SOURCE_PATTERNS)


def _extract_relevant_faq_block(content: str, query: str, *, max_blocks: int = 2) -> str:
    """Trim FAQ-style content to the most relevant Q&A blocks before reranking."""
    questions = list(_FAQ_QUESTION_RE.finditer(content))
    if len(questions) < 2:
        return content

    query_words = set(normalize_text(query).split())
    scored_blocks: list[tuple[float, str]] = []
    for index, match in enumerate(questions):
        end = questions[index + 1].start() if index + 1 < len(questions) else len(content)
        block = content[match.start():end].strip()
        question_text = match.group(1) if match.group(1) else block.split("\n")[0]
        question_words = set(normalize_text(question_text).split())
        question_overlap = sum(_faq_word_weight(word) for word in query_words & question_words) * 2.0
        block_words = set(normalize_text(block).split())
        block_overlap = sum(_faq_word_weight(word) for word in query_words & block_words)
        scored_blocks.append((question_overlap + block_overlap, block))

    scored_blocks.sort(key=lambda pair: pair[0], reverse=True)
    top_blocks = [block for score, block in scored_blocks[:max_blocks] if score > 0]
    if not top_blocks:
        return scored_blocks[0][1] if scored_blocks else content
    return "\n\n".join(top_blocks)


def _select_reranker_query(query: str, expanded_query: str) -> str:
    """Prefer expanded query text for high-value student-affairs admin profiles."""
    profile = _detect_student_affairs_query_profile(query)
    if profile in {"grade_objection", "grade_entry", "grade_visibility", "withdrawal", "discipline", "muafiyet"}:
        return _strip_augmentation_prefix(expanded_query)
    topic = _shared_detect_query_topic(query)
    if topic and normalize_text(topic) in _SHARED_CAP_PRIMARY_TOPICS:
        return _strip_augmentation_prefix(expanded_query)
    return _strip_augmentation_prefix(query)


_TURKISH_SUFFIXES = (
    "lerin", "larin", "leri", "ları", "lari",
    "ler", "lar",
    "nin", "nın", "nın", "nun", "nün",
    "larımız", "lerimiz", "larimiz", "lerimiz",
    "larım", "lerim", "larim", "lerim",
    "dan", "den", "tan", "ten",
    "nda", "nde",
    "daki", "deki", "ndaki", "ndeki",
    "yla", "yle", "iyla", "iyle",
    "ını", "ini", "unu", "ünü",
    "ına", "ine", "una", "üne",
    "ında", "inde", "unda", "ünde",
    "uma", "üme", "ime", "ıma",
    "um", "üm",
    "ıdır", "idir", "udur", "üdür",
    "dır", "dir", "dur", "dür",
    "tır", "tir", "tur", "tür",
    "mış", "miş", "muş", "müş",
    "yor", "arak", "erek",
    "ması", "mesi",
    "mak", "mek",
    "ım", "im", "um", "üm",
    "ın", "in", "un", "ün",
    "da", "de", "ta", "te",
    "ya", "ye",
    "sı", "si", "su", "sü",
    "lık", "lik", "luk", "lük",
    "ca", "ce", "ça", "çe",
)


def _turkish_stem(token: str) -> str:
    """Aggressive but safe suffix stripping for BM25 recall."""
    if len(token) <= 3:
        return token
    stemmed = token
    for _ in range(2):
        for suffix in _TURKISH_SUFFIXES:
            if stemmed.endswith(suffix) and len(stemmed) - len(suffix) >= 2:
                stemmed = stemmed[: -len(suffix)]
                break
        else:
            break
    return stemmed


def _dedupe_tokens(tokens: List[str]) -> List[str]:
    """Preserve token order while removing exact duplicates."""
    seen: set[str] = set()
    deduped: List[str] = []
    for token in tokens:
        if token in seen:
            continue
        seen.add(token)
        deduped.append(token)
    return deduped


def turkish_bm25_preprocess(text: str) -> List[str]:
    """Normalize and tokenize Turkish text for BM25."""
    if not text:
        return []

    normalized_text = _BM25_NORMALIZER.normalize_for_bm25(text)
    normalized_text = normalized_text.lower()
    for compound, split in _COMPOUND_SPLITS.items():
        normalized_text = normalized_text.replace(compound, split)

    normalized_text = _PUNCTUATION_RE.sub(" ", normalized_text)
    normalized_text = _WHITESPACE_RE.sub(" ", normalized_text).strip()

    tokens = normalized_text.split()
    stemmed: List[str] = []
    for token in tokens:
        if len(token) <= 1:
            continue
        token_stem = _turkish_stem(token)
        stemmed.append(token_stem)
        ascii_stem = _turkish_stem(normalize_text(token))
        if ascii_stem and ascii_stem != token_stem:
            stemmed.append(ascii_stem)
    return _dedupe_tokens(stemmed)


OFF_TOPIC_PENALTY = _SHARED_OFF_TOPIC_PENALTY
CONVERSATION_SOURCE_HINT_BOOST = 0.08
CONVERSATION_TOPIC_HINT_BOOST = 0.04
_DEPARTMENT_METADATA_BOOST = 0.06
_RERANKER_MIN_SCORE_THRESHOLD = 0.23
_BM25_NORMALIZER = QueryPreprocessor(enable_expansion=False)


def _detect_query_topic(query: str) -> Optional[str]:
    """Backward-compatible wrapper around shared search planner logic."""
    return _shared_detect_query_topic(query)


def _score_departments(query: str) -> Dict[Department, int]:
    """Backward-compatible wrapper around shared search planner logic."""
    return _shared_score_departments(query)


def _plan_search_departments(
    query: str,
    explicit_department: Department | str | None = None,
) -> tuple[List[Department], List[Department]]:
    """Backward-compatible wrapper around shared search planner logic."""
    return _shared_plan_search_departments(query, explicit_department)


def _apply_source_relevance(
    results: List[Dict[str, Any]],
    query: str,
    penalty: float = OFF_TOPIC_PENALTY,
) -> List[Dict[str, Any]]:
    """Backward-compatible wrapper around shared search planner logic."""
    return _shared_apply_source_relevance(results, query, penalty)


def _apply_finance_source_penalty(
    results: List[Dict[str, Any]],
    query: str,
    collection_name: str,
) -> List[Dict[str, Any]]:
    """Backward-compatible wrapper around shared search planner logic."""
    return _shared_apply_finance_source_penalty(results, query, collection_name)


def _apply_student_affairs_faq_bias(
    results: List[Dict[str, Any]],
    query: str,
    collection_name: str,
) -> List[Dict[str, Any]]:
    """Backward-compatible wrapper for FAQ/student-affairs source biasing."""
    return _shared_apply_student_affairs_faq_bias(results, query, collection_name)


def _apply_query_profile_source_bias(
    results: List[Dict[str, Any]],
    query: str,
    collection_name: str,
) -> List[Dict[str, Any]]:
    """Backward-compatible wrapper for student-affairs query-profile biasing."""
    return _shared_apply_query_profile_source_bias(results, query, collection_name)


def _apply_education_level_penalty(
    results: List[Dict[str, Any]],
    query: str,
) -> List[Dict[str, Any]]:
    """Backward-compatible wrapper for lisans/lisansustu source penalty."""
    return _shared_apply_education_level_penalty(results, query)


def _detect_student_affairs_query_profile(query: str) -> Optional[str]:
    """Backward-compatible wrapper for student-affairs query profile detection."""
    return _shared_detect_student_affairs_query_profile(query)


def _looks_like_schedule_query(query: str) -> bool:
    """Backward-compatible wrapper for schedule-oriented academic queries."""
    return _shared_looks_like_schedule_query(query)


def _resolve_collection_plan(
    primary_departments: List[Department],
    fallback_departments: List[Department],
    query: str,
) -> tuple[List[str], List[str]]:
    """Map department routing into collection routing, with schedule-aware overrides."""

    def _append_unique(target: List[str], collection_name: str) -> None:
        if collection_name not in target:
            target.append(collection_name)

    primary_collections: List[str] = []
    fallback_collections: List[str] = []
    schedule_query = _looks_like_schedule_query(query)

    for dep in primary_departments:
        if dep == Department.ACADEMIC_PROGRAMS and schedule_query:
            _append_unique(primary_collections, academic_schedule_collection_name())
            _append_unique(fallback_collections, collection_name_for_department(dep))
        else:
            _append_unique(primary_collections, collection_name_for_department(dep))

    for dep in fallback_departments:
        _append_unique(fallback_collections, collection_name_for_department(dep))

    return primary_collections, fallback_collections


def _apply_conversation_source_hints(
    results: List[Dict[str, Any]],
    source_hints: List[str] | None,
    topic_hint: str | None,
) -> List[Dict[str, Any]]:
    """Boost likely follow-up sources using prior source and topic hints."""
    normalized_source_hints = [
        hint.strip().casefold()
        for hint in (source_hints or [])
        if hint and hint.strip()
    ]
    normalized_topic_hint = topic_hint.strip().casefold() if topic_hint else None
    if not normalized_source_hints and not normalized_topic_hint:
        return results

    adjusted: List[Dict[str, Any]] = []
    for result in results:
        metadata = result.get("metadata") or {}
        source_text = " ".join(
            str(value or "").casefold()
            for value in (
                metadata.get("file_name"),
                metadata.get("source"),
                metadata.get("title"),
                metadata.get("source_url"),
                result.get("source"),
            )
        )
        content_text = str(result.get("content") or "").casefold()
        boosted = float(result.get("score", 0.0))

        if normalized_source_hints and any(hint in source_text for hint in normalized_source_hints):
            boosted += CONVERSATION_SOURCE_HINT_BOOST

        if normalized_topic_hint and normalized_topic_hint in content_text:
            boosted += CONVERSATION_TOPIC_HINT_BOOST

        adjusted.append(
            {
                **result,
                "score": round(boosted, 6),
            }
        )
    return adjusted


def _apply_department_metadata_boost(
    results: List[Dict[str, Any]],
    student_department: str | None,
    boost: float = _DEPARTMENT_METADATA_BOOST,
) -> List[Dict[str, Any]]:
    """Boost results whose bolum metadata matches the student's department.

    General documents (bolum=genel or missing) are unaffected so they
    naturally mix with department-specific results based on relevance.
    """
    if not student_department:
        return results

    from src.core.text_normalization import normalize_text as _norm

    normalized_dept = _norm(student_department)
    adjusted = False
    for item in results:
        metadata = item.get("metadata") or {}
        bolum_adi = _norm(metadata.get("bolum_adi", ""))
        bolum_code = _norm(metadata.get("bolum", ""))

        if not bolum_adi or bolum_adi == "genel" or bolum_code == "genel":
            continue

        if normalized_dept in bolum_adi or bolum_code in normalized_dept:
            item["score"] = round(float(item.get("score", 0.0)) + boost, 4)
            adjusted = True

    if adjusted:
        results.sort(key=lambda c: c.get("score", 0.0), reverse=True)
        logger.debug(
            "department_metadata_boost_applied",
            student_department=student_department,
            top_sources=[(r.get("source", ""), r.get("score", 0.0)) for r in results[:3]],
        )
    return results


def _result_score_type(item: Dict[str, Any]) -> str:
    metadata = item.get("metadata") or {}
    return str(metadata.get("score_type", "retrieval")).strip().lower()


def _metadata_identity_key(metadata: Dict[str, Any]) -> str:
    """Return the stable document identity used when source filenames are ambiguous."""
    return str(
        metadata.get("relative_path")
        or metadata.get("file_path")
        or metadata.get("source")
        or ""
    )


class ChromaRestRetriever(BaseRetriever):
    """LangChain-compatible retriever backed by Chroma REST API."""

    indexer: Any
    embedder: Any
    k: int = 5

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> List[Document]:
        _ = run_manager
        query_vector = self.embedder.embed_single(query, is_query=True)
        results = self.indexer.query(query_embedding=query_vector, n_results=self.k)

        documents: List[Document] = []
        if results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            metadatas = results["metadatas"][0] if results.get("metadatas") else []
            distances = results["distances"][0] if results.get("distances") else []

            for index, doc_text in enumerate(docs):
                metadata = metadatas[index] if index < len(metadatas) else {}
                distance = distances[index] if index < len(distances) else 0.0
                metadata["similarity_score"] = round(1 - distance, 4)
                documents.append(Document(page_content=doc_text, metadata=metadata))

        return documents


class _QueryCache(_SharedQueryCache):
    """Backward-compatible cache wrapper."""


class HybridRetriever:
    """
    BM25 + ChromaDB + cross-encoder reranking.

    Flow:
    query -> preprocess -> BM25 + semantic retrieval -> dedup -> rerank -> penalties -> min_score
    """

    OVERSAMPLE_FACTOR = 4
    _BM25_DOCUMENT_CACHE: ClassVar[dict[str, List[Document]]] = {}
    _BM25_RETRIEVER_CACHE: ClassVar[dict[tuple[str, int], BM25Retriever]] = {}
    _WARMUP_PROBE_QUERIES: ClassVar[dict[str, str]] = {
        collection_name_for_department(Department.STUDENT_AFFAIRS): (
            "Kayit yenileme, ders kaydi ve danisman onayi nasil ilerler?"
        ),
        collection_name_for_department(Department.ACADEMIC_PROGRAMS): (
            "Muafiyet ve intibak basvurusu hangi belgelerle ve hangi surede yapilir?"
        ),
        collection_name_for_department(Department.FINANCE): (
            "Harc odemesi ve ogrenim ucreti nasil yatirilir?"
        ),
        academic_schedule_collection_name(): (
            "Haftalik ders programi ve derslik bilgisi nerede gorulur?"
        ),
    }

    @classmethod
    def clear_resource_cache(cls) -> None:
        """Paylasilan BM25 belge ve retriever cache'lerini temizler."""
        cls._BM25_DOCUMENT_CACHE.clear()
        cls._BM25_RETRIEVER_CACHE.clear()

    def __init__(
        self,
        collection_name: str | None = None,
        k: int = 5,
        bm25_weight: float = 0.5,
        chroma_weight: float = 0.5,
        enable_query_expansion: bool = True,
        min_score: float | None = None,
        cache_ttl: int = 300,
    ):
        self.collection_name = collection_name
        self.k = k
        self.bm25_weight = bm25_weight
        self.chroma_weight = chroma_weight
        self.min_score = min_score if min_score is not None else settings.rag.min_similarity

        self.query_preprocessor = QueryPreprocessor(enable_expansion=enable_query_expansion)
        self.llm_query_expander = LLMQueryExpander()
        from src.rag.embedder import Embedder
        from src.rag.reranker import CrossEncoderReranker

        self.embedder = Embedder()
        self.reranker = CrossEncoderReranker()

        self._indexers: Dict[str, ChromaIndexer] = {}
        self._ensembles: Dict[str, EnsembleRetriever] = {}
        self._bm25_doc_counts: Dict[str, int] = {}
        effective_cache_ttl = settings.cache.retriever_query_cache_ttl_seconds
        if cache_ttl != 300:
            effective_cache_ttl = cache_ttl
        self._cache = _QueryCache(
            ttl=effective_cache_ttl,
            enabled=(settings.cache.enabled and settings.cache.retriever_query_cache_enabled),
        )

    @classmethod
    def prewarm(
        cls,
        collection_names: List[str],
        *,
        k: int | None = None,
        include_reranker: bool = False,
    ) -> None:
        """Paylasilan retrieval kaynaklarini isitir."""
        if not collection_names:
            return

        retriever = cls(k=k or settings.rag.top_k)
        try:
            _ = retriever.embedder.model
            if include_reranker:
                _ = retriever.reranker.model
            for collection_name in collection_names:
                retriever._ensure_ensemble(collection_name)
                probe_query = cls._WARMUP_PROBE_QUERIES.get(collection_name, "Test sorgusu")
                retriever.embedder.embed_single(probe_query, is_query=True)
                candidates = retriever._search_collection_candidates(collection_name, probe_query)
                if include_reranker:
                    reranker_candidates = candidates[: max(1, min(retriever.k, 2))]
                    if not reranker_candidates:
                        reranker_candidates = [
                            {
                                "content": "Warm-up belge parcasi",
                                "score": 0.0,
                                "source": "__warmup__",
                                "metadata": {},
                            }
                        ]
                    retriever.reranker.rerank(
                        probe_query,
                        reranker_candidates,
                        top_k=min(len(reranker_candidates), retriever.k),
                    )
        finally:
            retriever.close()

    @staticmethod
    def _sort_candidates_by_score(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort candidates by score descending."""
        return sort_candidates_by_score(candidates)

    def _reranker_candidate_limit(
        self,
        collection_name: str,
        query_type: str,
        top_k: int,
        *,
        query: str,
    ) -> int:
        """Return reranker candidate pool size for the current collection/query type."""
        base_limit = settings.rag.reranker_candidate_limit_default

        if collection_name == collection_name_for_department(Department.FINANCE):
            base_limit = settings.rag.reranker_candidate_limit_finance
        elif collection_name == collection_name_for_department(Department.STUDENT_AFFAIRS):
            base_limit = settings.rag.reranker_candidate_limit_student_affairs
        elif collection_name == collection_name_for_department(Department.ACADEMIC_PROGRAMS):
            base_limit = settings.rag.reranker_candidate_limit_academic_programs

        if (
            collection_name == collection_name_for_department(Department.ACADEMIC_PROGRAMS)
            and query_type == "general"
        ):
            base_limit = max(base_limit, top_k + 1)

        profile = _detect_student_affairs_query_profile(query)
        if collection_name in {
            "__multi__",
            collection_name_for_department(Department.STUDENT_AFFAIRS),
        }:
            if profile in {
                "grade_objection",
                "grade_entry",
                "grade_visibility",
                "withdrawal",
                "discipline",
                "muafiyet",
                "course_registration",
            }:
                # Keep extra recall for admin/procedure-heavy student-affairs flows,
                # but avoid reranking very large pools that dominate dispatch latency.
                base_limit = max(base_limit, top_k + 1, 6)
            elif query_type == "procedural":
                base_limit = max(base_limit, top_k + 1, 6)
            elif profile == "international_registration":
                base_limit = max(base_limit, top_k + 1, 6)

        return max(top_k, base_limit)

    def _should_skip_reranker(
        self,
        collection_name: str,
        query_type: str,
        candidates: List[Dict[str, Any]],
        top_k: int,
    ) -> bool:
        """Skip reranker only when there are not enough candidates to compare."""
        return len(candidates) <= 1

    def _rank_without_reranker(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """Use fusion score ordering when reranker is skipped."""
        _ = query
        for candidate in candidates:
            metadata = candidate.setdefault("metadata", {})
            metadata.setdefault("retrieval_score", round(float(candidate.get("score", 0.0)), 4))
            metadata.setdefault("score_type", "retrieval")
        return self._sort_candidates_by_score(candidates)[:top_k]

    @staticmethod
    def _resolve_collection_name_for_candidate(
        candidate: Dict[str, Any],
        department: Department | str | None = None,
    ) -> str | None:
        """Infer the backing collection for a candidate from explicit or metadata department."""
        department_value = department
        if department_value is None:
            department_value = (candidate.get("metadata") or {}).get("department")
        if not department_value:
            return None

        try:
            return collection_name_for_department(Department(department_value))
        except ValueError:
            return None

    def _load_documents_for_collection(self, collection_name: str) -> List[Document]:
        """Load BM25 cache documents for a collection on demand."""
        cached_documents = self._BM25_DOCUMENT_CACHE.get(collection_name)
        if settings.cache.enabled and settings.cache.bm25_resource_cache_enabled and cached_documents is not None:
            return cached_documents

        indexer = self._get_indexer(collection_name)
        return self._load_bm25_documents(collection_name, indexer)

    @staticmethod
    def _candidate_sort_key(candidate: Dict[str, Any]) -> tuple[int, int]:
        """Order chunks by sub-chunk position first, then chunk index."""
        metadata = candidate.get("metadata") or {}
        position = parse_sub_chunk_position(metadata.get("sub_chunk"))
        if position is not None:
            return position[0], int(metadata.get("chunk_index", position[0]))
        return int(metadata.get("chunk_index", 10**9)), int(metadata.get("chunk_index", 10**9))

    def _expand_candidate_context(
        self,
        candidate: Dict[str, Any],
        *,
        department: Department | str | None = None,
    ) -> Dict[str, Any]:
        """Expand a result to the full MADDE span when the hit is only one sub-chunk."""
        metadata = dict(candidate.get("metadata") or {})
        source = metadata.get("source") or candidate.get("source")
        document_key = _metadata_identity_key(metadata)
        madde_no = metadata.get("madde_no")
        sub_chunk = metadata.get("sub_chunk")
        if not source or not madde_no or not sub_chunk:
            return candidate

        collection_name = self._resolve_collection_name_for_candidate(candidate, department=department)
        if not collection_name:
            return candidate

        documents = self._load_documents_for_collection(collection_name)
        related_candidates: List[Dict[str, Any]] = []
        for document in documents:
            doc_metadata = dict(document.metadata or {})
            if _metadata_identity_key(doc_metadata) != document_key:
                continue
            if str(doc_metadata.get("madde_no")) != str(madde_no):
                continue
            related_candidates.append(
                {
                    "content": document.page_content,
                    "metadata": doc_metadata,
                }
            )

        if len(related_candidates) <= 1:
            return candidate

        related_candidates.sort(key=self._candidate_sort_key)
        merged_content = merge_chunk_texts(item["content"] for item in related_candidates)
        if not merged_content:
            return candidate

        metadata["context_expanded"] = True
        metadata["merged_chunk_count"] = len(related_candidates)
        metadata["merged_sub_chunks"] = ",".join(
            str(item["metadata"].get("sub_chunk", "")) for item in related_candidates if item["metadata"].get("sub_chunk")
        )
        return {
            **candidate,
            "content": merged_content,
            "metadata": metadata,
        }

    def enrich_results(
        self,
        results: List[Dict[str, Any]],
        *,
        department: Department | str | None = None,
    ) -> List[Dict[str, Any]]:
        """Expand partial MADDE hits and deduplicate repeated source rows."""
        if not results:
            return []

        expanded = [
            self._expand_candidate_context(result, department=department)
            for result in results
        ]
        expanded = deduplicate_candidate_dicts(expanded)
        return self._sort_candidates_by_score(expanded)

    def _resolve_search_collections(
        self,
        query: str,
        department: Department | str | None,
    ) -> tuple[List[str], List[str]]:
        """Resolve primary and fallback collections for the query."""
        if department is not None:
            primary_departments, fallback_departments = _plan_search_departments(query, department)
            return _resolve_collection_plan(primary_departments, fallback_departments, query)

        if self.collection_name is not None:
            return [self.collection_name], []

        primary_departments, fallback_departments = _plan_search_departments(query)
        return _resolve_collection_plan(primary_departments, fallback_departments, query)

    def _collect_candidates(
        self,
        query: str,
        expanded_query: str,
        primary_collections: List[str],
        fallback_collections: List[str],
    ) -> List[Dict[str, Any]]:
        """Collect candidates from primary collections, then fallback if needed."""
        candidates: List[Dict[str, Any]] = []
        for collection_name in primary_collections:
            candidates.extend(self._search_collection_candidates(collection_name, expanded_query))

        if candidates or not fallback_collections:
            return candidates

        logger.info("hybrid_search_fallback", query=query, collections=fallback_collections)
        for collection_name in fallback_collections:
            candidates.extend(self._search_collection_candidates(collection_name, expanded_query))
        return candidates

    def _expand_query_for_search(self, query: str) -> str:
        """Apply deterministic expansion and optional LLM expansion."""
        rule_expanded_query = self.query_preprocessor.preprocess(query)
        llm_expander = getattr(self, "llm_query_expander", None)
        if llm_expander is None:
            return rule_expanded_query

        llm_result = llm_expander.expand(query, rule_expanded_query=rule_expanded_query)
        if llm_result is None:
            return rule_expanded_query

        logger.info(
            "llm_query_expanded",
            original=query,
            expanded=llm_result.expanded_query,
            added_terms=llm_result.added_terms,
        )
        return llm_result.expanded_query

    @staticmethod
    def _build_cache_key(
        query: str,
        top_k: int,
        primary_collections: List[str],
        fallback_collections: List[str],
        source_hints: List[str] | None = None,
        topic_hint: str | None = None,
        student_department: str | None = None,
    ) -> str:
        """Build a stable cache key for a search request."""
        normalized_hints = "|".join(sorted(hint.strip().casefold() for hint in (source_hints or []) if hint))
        normalized_topic = (topic_hint or "").strip().casefold()
        normalized_dept = (student_department or "").strip().casefold()
        return (
            f"{query}::{top_k}::"
            f"{'|'.join(primary_collections)}::"
            f"{'|'.join(fallback_collections)}::"
            f"{normalized_hints}::"
            f"{normalized_topic}::"
            f"{normalized_dept}"
        )

    def _try_cache_hit(
        self,
        *,
        cache_key: str,
        query: str,
        start_time: float,
    ) -> List[Dict[str, Any]] | None:
        """Return cached results if present and emit a cache-hit log."""
        cached = self._cache.get(cache_key)
        if cached is None:
            return None

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "hybrid_search_cache_hit",
            query=query,
            results_count=len(cached),
            elapsed_ms=round(elapsed_ms, 1),
        )
        return cached

    def _rank_candidates(
        self,
        *,
        query: str,
        expanded_query: str,
        query_type: str,
        candidates: List[Dict[str, Any]],
        search_scope: str,
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """Apply reranker policy and return ranked candidates."""
        reranker_limit = self._reranker_candidate_limit(
            search_scope,
            query_type,
            top_k,
            query=query,
        )
        reranker_candidates = candidates[:reranker_limit]
        clean_query = _select_reranker_query(query, expanded_query)
        reranker_candidates = [
            {
                **candidate,
                "content": _extract_relevant_faq_block(str(candidate.get("content", "")), clean_query)
                if _is_faq_source(str(candidate.get("source", "")))
                else candidate.get("content", ""),
            }
            for candidate in reranker_candidates
        ]

        if self._should_skip_reranker(search_scope, query_type, reranker_candidates, top_k):
            logger.info(
                "reranker_skipped",
                query=query,
                collection=search_scope,
                query_type=query_type,
                candidate_count=len(reranker_candidates),
                top_k=top_k,
            )
            return self._rank_without_reranker(query, reranker_candidates, top_k=top_k)

        logger.info(
            "reranker_limited",
            query=query,
            reranker_query=clean_query,
            collection=search_scope,
            query_type=query_type,
            original_candidate_count=len(candidates),
            reranker_candidate_count=len(reranker_candidates),
            top_k=top_k,
        )
        return self.reranker.rerank(clean_query, reranker_candidates, top_k=top_k)

    def _minimum_score_threshold_for(self, item: Dict[str, Any]) -> float:
        """Resolve score filtering threshold by score type."""
        score_type = _result_score_type(item)
        if score_type == "reranker":
            return max(self.min_score, _RERANKER_MIN_SCORE_THRESHOLD)
        return self.min_score

    def _finalize_results(
        self,
        *,
        query: str,
        query_type: str,
        results: List[Dict[str, Any]],
        cache_key: str,
        start_time: float,
    ) -> List[Dict[str, Any]]:
        """Apply final relevance filtering, cache, and completion logging."""
        results = _apply_source_relevance(results, query)

        if self.min_score > 0:
            results = [
                result
                for result in results
                if float(result.get("score", 0.0)) >= self._minimum_score_threshold_for(result)
            ]

        self._cache.put(cache_key, results)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "hybrid_search_complete",
            query=query,
            results_count=len(results),
            query_type=query_type,
            elapsed_ms=round(elapsed_ms, 1),
            cache_size=self._cache.size,
        )
        return results

    def _get_indexer(self, collection_name: str) -> ChromaIndexer:
        """Return the cached Chroma indexer for a collection."""
        indexer = self._indexers.get(collection_name)
        if indexer is None:
            from src.rag.indexer import ChromaIndexer

            indexer = ChromaIndexer(collection_name=collection_name)
            self._indexers[collection_name] = indexer
        return indexer

    def _load_bm25_documents(
        self,
        collection_name: str,
        indexer: ChromaIndexer,
    ) -> List[Document]:
        """Load and cache BM25 documents for a collection."""
        cached_documents = self._BM25_DOCUMENT_CACHE.get(collection_name)
        if settings.cache.enabled and settings.cache.bm25_resource_cache_enabled and cached_documents is not None:
            logger.info(
                "bm25_document_cache_hit",
                collection=collection_name,
                total_docs=len(cached_documents),
            )
            return cached_documents

        logger.info("fetching_data_for_bm25_index")
        all_data = indexer.get_all()

        documents: List[Document] = []
        if all_data.get("documents"):
            docs = all_data["documents"]
            metadatas = all_data.get("metadatas", [])
            for index, text in enumerate(docs):
                metadata = metadatas[index] if metadatas and index < len(metadatas) else {}
                documents.append(Document(page_content=text, metadata=metadata))

        if settings.cache.enabled and settings.cache.bm25_resource_cache_enabled:
            self._BM25_DOCUMENT_CACHE[collection_name] = documents
        logger.info(
            "bm25_documents_cached",
            collection=collection_name,
            total_docs=len(documents),
        )
        return documents

    def _build_bm25_retriever(
        self,
        collection_name: str,
        internal_k: int,
        documents: List[Document],
    ) -> BM25Retriever:
        """Build and cache BM25 retrievers per collection and k."""
        cache_key = (collection_name, internal_k)
        cached_retriever = self._BM25_RETRIEVER_CACHE.get(cache_key)
        if settings.cache.enabled and settings.cache.bm25_resource_cache_enabled and cached_retriever is not None:
            logger.info(
                "bm25_retriever_cache_hit",
                collection=collection_name,
                total_docs=len(documents),
                k=internal_k,
            )
            return cached_retriever

        logger.info("initializing_bm25_engine", total_docs=len(documents))
        source_documents = documents or [Document(page_content="bos")]
        if not documents:
            logger.warning("no_documents_for_bm25")

        bm25_retriever = BM25Retriever.from_documents(
            source_documents,
            preprocess_func=turkish_bm25_preprocess,
        )
        bm25_retriever.k = internal_k
        if settings.cache.enabled and settings.cache.bm25_resource_cache_enabled:
            self._BM25_RETRIEVER_CACHE[cache_key] = bm25_retriever
        return bm25_retriever

    def _ensure_ensemble(self, collection_name: str) -> EnsembleRetriever:
        """Build the ensemble retriever lazily for a collection."""
        ensemble = self._ensembles.get(collection_name)
        if ensemble is not None:
            return ensemble

        logger.info("building_hybrid_retriever", collection=collection_name)

        internal_k = self.k * self.OVERSAMPLE_FACTOR
        indexer = self._get_indexer(collection_name)

        chroma_retriever = ChromaRestRetriever(
            indexer=indexer,
            embedder=self.embedder,
            k=internal_k,
        )

        documents = self._load_bm25_documents(collection_name, indexer)
        self._bm25_doc_counts[collection_name] = len(documents)
        bm25_retriever = self._build_bm25_retriever(collection_name, internal_k, documents)

        ensemble = EnsembleRetriever(
            retrievers=[bm25_retriever, chroma_retriever],
            weights=[self.bm25_weight, self.chroma_weight],
        )
        self._ensembles[collection_name] = ensemble

        logger.info(
            "hybrid_retriever_ready",
            bm25_docs=self._bm25_doc_counts[collection_name],
            bm25_weight=self.bm25_weight,
            chroma_weight=self.chroma_weight,
            collection=collection_name,
        )
        return ensemble

    @staticmethod
    def _deduplicate_candidates(raw_docs: List[Document]) -> List[Dict[str, Any]]:
        """Deduplicate candidate documents by content prefix."""
        return deduplicate_documents(raw_docs)

    def _search_collection_candidates(
        self,
        collection_name: str,
        expanded_query: str,
    ) -> List[Dict[str, Any]]:
        """Run hybrid retrieval for a single collection."""
        try:
            ensemble = self._ensure_ensemble(collection_name)
            raw_docs = ensemble.invoke(expanded_query)
        except Exception:
            # Retrieval should degrade gracefully when a collection backend fails.
            logger.exception(
                "ensemble_search_failed",
                query=expanded_query,
                collection=collection_name,
            )
            return []

        return self._deduplicate_candidates(raw_docs)

    def search(
        self,
        query: str,
        top_k: int | None = None,
        department: Department | str | None = None,
        *,
        source_hints: List[str] | None = None,
        topic_hint: str | None = None,
        student_department: str | None = None,
    ) -> List[Dict[str, Any]]:
        """Run hybrid retrieval and return ranked results."""
        start_time = time.perf_counter()
        k = top_k or self.k
        primary_collections, fallback_collections = self._resolve_search_collections(
            query=query,
            department=department,
        )

        cache_key = self._build_cache_key(
            query=query,
            top_k=k,
            primary_collections=primary_collections,
            fallback_collections=fallback_collections,
            source_hints=source_hints,
            topic_hint=topic_hint,
            student_department=student_department,
        )
        cached = self._try_cache_hit(
            cache_key=cache_key,
            query=query,
            start_time=start_time,
        )
        if cached is not None:
            return cached

        expanded_query = self._expand_query_for_search(query)
        query_type = self.query_preprocessor.detect_query_type(query)

        logger.info(
            "hybrid_search_start",
            original_query=query,
            expanded_query=expanded_query,
            query_type=query_type,
            primary_collections=primary_collections,
            fallback_collections=fallback_collections,
        )

        candidates = self._collect_candidates(
            query=query,
            expanded_query=expanded_query,
            primary_collections=primary_collections,
            fallback_collections=fallback_collections,
        )
        if not candidates:
            logger.warning("hybrid_search_no_candidates", query=query, collections=primary_collections)
            return []

        candidates = deduplicate_candidate_dicts(candidates)
        candidates = _apply_conversation_source_hints(
            candidates,
            source_hints=source_hints,
            topic_hint=topic_hint,
        )

        search_scope = primary_collections[0] if len(primary_collections) == 1 else "__multi__"
        candidates = _apply_student_affairs_faq_bias(candidates, query, search_scope)
        candidates = _apply_query_profile_source_bias(candidates, query, search_scope)
        candidates = _apply_finance_source_penalty(candidates, query, search_scope)
        candidates = _apply_education_level_penalty(candidates, query)
        candidates = _apply_department_metadata_boost(candidates, student_department)
        candidates = self._sort_candidates_by_score(candidates)
        results = self._rank_candidates(
            query=query,
            expanded_query=expanded_query,
            query_type=query_type,
            candidates=candidates,
            search_scope=search_scope,
            top_k=k,
        )
        return self._finalize_results(
            query=query,
            query_type=query_type,
            results=results,
            cache_key=cache_key,
            start_time=start_time,
        )

    def close(self) -> None:
        """Release held resources."""
        for indexer in self._indexers.values():
            indexer.close()
        self._indexers.clear()
        self._ensembles.clear()
        self._bm25_doc_counts.clear()


def build_hybrid_retriever(
    collection_name: str,
    k: int = 5,
    bm25_weight: float = 0.5,
    chroma_weight: float = 0.5,
) -> EnsembleRetriever:
    """Backward-compatible helper that returns the ensemble retriever."""
    retriever = HybridRetriever(
        collection_name=collection_name,
        k=k,
        bm25_weight=bm25_weight,
        chroma_weight=chroma_weight,
    )
    return retriever._ensure_ensemble(collection_name)
