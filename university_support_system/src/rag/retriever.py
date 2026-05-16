"""
Hybrid retrieval for RAG.

Combines:
- BM25 keyword search
- Chroma semantic search
- Optional cross-encoder reranking
"""

from __future__ import annotations

import re
import threading
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
from src.core.source_owner_collections import (
    SourceOwnerCollectionBridge,
    resolve_source_owner_collection_bridge,
)
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

_RERANKER_SEMAPHORE: threading.BoundedSemaphore | None = None
_RERANKER_SEMAPHORE_LIMIT: int | None = None


def _reranker_semaphore() -> threading.BoundedSemaphore | None:
    global _RERANKER_SEMAPHORE, _RERANKER_SEMAPHORE_LIMIT
    limit = max(0, int(settings.rag.reranker_concurrency_limit or 0))
    if limit <= 0:
        return None
    if _RERANKER_SEMAPHORE is None or _RERANKER_SEMAPHORE_LIMIT != limit:
        _RERANKER_SEMAPHORE = threading.BoundedSemaphore(limit)
        _RERANKER_SEMAPHORE_LIMIT = limit
    return _RERANKER_SEMAPHORE


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
_SOURCE_CONSTRAINED_LOW_WEIGHT_WORDS = _FAQ_LOW_WEIGHT_WORDS | frozenset({
    "soru", "cevap", "konu", "hakkinda", "nedir", "olarak", "olan",
    "olmasi", "program", "programi", "programlar", "surec", "sureci",
    "kosul", "kosulu", "kosullari", "sart", "sarti", "sartlari",
})
_SOURCE_CONSTRAINED_NUMERIC_MARKERS = (
    "kac",
    "ne kadar",
    "en az",
    "ortalama",
    "ortalamasi",
    "gano",
    "gno",
    "akts",
    "kredi",
    "ucret",
)
_SOURCE_CONSTRAINED_NUMBER_RE = re.compile(r"\b\d+(?:[,.]\d+)?\b")
_CONCRETE_SOURCE_HINT_RE = re.compile(
    r"(?:\.(?:pdf|txt|html?|docx?|doc|csv|json)\b|[\\/])",
    re.IGNORECASE,
)
_SOURCE_CONSTRAINT_TOKEN_STOPWORDS = frozenset({
    "pdf", "txt", "html", "doc", "docx", "csv", "json", "yonerge", "belge",
})
_DEPARTMENT_SCOPED_QUERY_MARKERS = (
    "staj",
    "ders",
    "mufredat",
    "on kosul",
    "onkosul",
    "program",
    "bitirme",
    "yaz okulu",
    "laboratuvar",
    "uygulama",
)
_DEPARTMENT_SCOPE_GENERIC_VALUES = frozenset({"", "genel", "general", "ortak"})
_DEPARTMENT_SCOPE_SUFFIX_WORDS = frozenset({
    "bolum",
    "bolumu",
    "program",
    "programi",
    "fakulte",
    "fakultesi",
    "muhendisligi",
    "ogretmenligi",
    "egitimi",
    "lisans",
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
_MIN_CONVERSATION_SOURCE_HINT_CHARS = 4
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
    normalized_source_hints = _conversation_source_hint_variants(source_hints)
    normalized_topic_hint = topic_hint.strip().casefold() if topic_hint else None
    if not normalized_source_hints and not normalized_topic_hint:
        return results

    adjusted: List[Dict[str, Any]] = []
    for result in results:
        metadata = result.get("metadata") or {}
        source_text = _source_constraint_text(
            *(
                value
                for value in (
                    metadata.get("file_name"),
                    metadata.get("source"),
                    metadata.get("title"),
                    metadata.get("source_url"),
                    result.get("source"),
                )
            )
        )
        content_text = str(result.get("content") or "").casefold()
        boosted = float(result.get("score", 0.0))

        if normalized_source_hints and any(
            _source_hint_matches(source_text, hint)
            for hint in normalized_source_hints
        ):
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


def _conversation_source_hint_variants(source_hints: List[str] | None) -> List[str]:
    """Normalize concrete source hints and drop short generic fragments."""
    variants: set[str] = set()
    for hint in source_hints or []:
        normalized = normalize_text(hint).strip()
        if not normalized:
            continue
        separated = re.sub(r"[_\-.]+", " ", normalized).strip()
        for variant in (normalized, separated):
            compact_len = len(re.sub(r"\W+", "", variant))
            if compact_len >= _MIN_CONVERSATION_SOURCE_HINT_CHARS:
                variants.add(variant)
    return sorted(variants, key=len, reverse=True)


def _source_hint_matches(source_text: str, hint: str) -> bool:
    if not source_text or not hint:
        return False
    pattern = rf"(?<!\w){re.escape(hint)}(?!\w)"
    return re.search(pattern, source_text) is not None


def _source_constraint_text(*values: Any) -> str:
    normalized_parts: list[str] = []
    for value in values:
        if value is None:
            continue
        normalized = normalize_text(str(value))
        if not normalized:
            continue
        normalized_parts.append(normalized)
        normalized_parts.append(re.sub(r"[_\-.]+", " ", normalized))
    return " ".join(dict.fromkeys(part for part in normalized_parts if part))


def _normalized_source_constraints(source_hints: List[str] | None) -> tuple[str, ...]:
    constraints: list[str] = []
    for hint in source_hints or []:
        text = _source_constraint_text(hint)
        if text:
            constraints.append(text)
    return tuple(dict.fromkeys(constraints))


def _has_concrete_source_hints(source_hints: List[str] | None) -> bool:
    return any(
        bool(_CONCRETE_SOURCE_HINT_RE.search(str(hint or "")))
        for hint in source_hints or []
    )


def _candidate_source_text(candidate: Dict[str, Any]) -> str:
    metadata = candidate.get("metadata") or {}
    return _source_constraint_text(
        candidate.get("source"),
        metadata.get("source"),
        metadata.get("file_name"),
        metadata.get("title"),
        metadata.get("relative_path"),
        metadata.get("source_url"),
    )


def _document_source_text(document: Document) -> str:
    metadata = document.metadata or {}
    return _source_constraint_text(
        metadata.get("source"),
        metadata.get("file_name"),
        metadata.get("title"),
        metadata.get("relative_path"),
        metadata.get("source_url"),
    )


def _source_matches_constraints(source_text: str, constraints: tuple[str, ...]) -> bool:
    if not source_text or not constraints:
        return False
    source_tokens = {
        token
        for token in source_text.split()
        if len(token) >= 3 and token not in _SOURCE_CONSTRAINT_TOKEN_STOPWORDS
    }
    for constraint in constraints:
        if constraint in source_text or source_text in constraint:
            return True
        constraint_tokens = {
            token
            for token in constraint.split()
            if len(token) >= 3 and token not in _SOURCE_CONSTRAINT_TOKEN_STOPWORDS
        }
        if not constraint_tokens or not source_tokens:
            continue
        required_overlap = min(3, len(constraint_tokens))
        if len(source_tokens & constraint_tokens) >= required_overlap:
            return True
    return False


def _filter_candidates_by_source_constraints(
    candidates: List[Dict[str, Any]],
    source_constraints: tuple[str, ...],
) -> List[Dict[str, Any]]:
    if not candidates or not source_constraints:
        return candidates
    return [
        candidate
        for candidate in candidates
        if _source_matches_constraints(_candidate_source_text(candidate), source_constraints)
    ]


def _source_constrained_query_terms(query: str, topic_hint: str | None) -> tuple[str, ...]:
    raw_tokens = turkish_bm25_preprocess(f"{query} {topic_hint or ''}")
    terms = [
        token
        for token in raw_tokens
        if len(token) >= 3 and token not in _SOURCE_CONSTRAINED_LOW_WEIGHT_WORDS
    ]
    return tuple(dict.fromkeys(terms))


def _source_constrained_query_phrases(query: str) -> tuple[str, ...]:
    tokens = [
        token
        for token in normalize_text(query).split()
        if len(token) >= 3 and token not in _SOURCE_CONSTRAINED_LOW_WEIGHT_WORDS
    ]
    phrases: list[str] = []
    for size in (3, 2):
        for index in range(0, max(len(tokens) - size + 1, 0)):
            phrase = " ".join(tokens[index:index + size])
            if len(phrase) >= 7:
                phrases.append(phrase)
    return tuple(dict.fromkeys(phrases))


def _source_constrained_alignment_score(
    *,
    query: str,
    topic_hint: str | None,
    content: str,
) -> float:
    normalized_query = normalize_text(query)
    normalized_topic = normalize_text(topic_hint or "")
    normalized_content = normalize_text(content)
    score = 0.0

    asks_application = "basvur" in normalized_query
    asks_grade = any(
        marker in normalized_query
        for marker in ("not ort", "ortalama", "gano", "gno")
    )
    asks_numeric = any(marker in normalized_query for marker in _SOURCE_CONSTRAINED_NUMERIC_MARKERS)
    cap_topic = any(
        marker in f"{normalized_query} {normalized_topic}"
        for marker in ("cap", "cift anadal", "cift ana dal", "ikinci lisans")
    )
    yandal_topic = any(marker in f"{normalized_query} {normalized_topic}" for marker in ("yandal", "yan dal", "ydp"))

    if asks_application:
        if any(
            marker in normalized_content
            for marker in (
                "basvuru kabul kayit",
                "basvuru kosullari",
                "basvuru sartlari",
                "basvurabilmesi",
                "basvurusu sirasindaki",
            )
        ):
            score += 3.0
        if any(
            marker in normalized_content
            for marker in (
                "ayrilma",
                "ilisik kesilme",
                "mezuniyet kosullari",
                "mezun olabilmesi",
                "kaydi silinir",
                "devam edebilmesi",
            )
        ):
            score -= 2.0

    if asks_grade:
        if "not ortalamas" in normalized_content or "genel not ortalamas" in normalized_content:
            score += 1.0
        if "en az" in normalized_content and _SOURCE_CONSTRAINED_NUMBER_RE.search(normalized_content):
            score += 1.0

    if asks_numeric and _SOURCE_CONSTRAINED_NUMBER_RE.search(normalized_content):
        score += 0.5

    if cap_topic and not yandal_topic:
        if "cap" in normalized_content and "basvur" in normalized_content:
            score += 1.0
        if any(marker in normalized_content for marker in ("ydp", "yan dal", "yandal")):
            cap_application_chunk = any(
                marker in normalized_content
                for marker in (
                    "cap'a basvuru kabul",
                    "cap a basvuru kabul",
                    "cap basvuru kabul",
                    "cap'a basvurabilmesi",
                    "cap a basvurabilmesi",
                )
            )
            if not cap_application_chunk:
                score -= 4.0

    return score


def _source_constrained_lexical_score(
    *,
    query: str,
    topic_hint: str | None,
    content: str,
) -> float:
    terms = _source_constrained_query_terms(query, topic_hint)
    if not terms:
        return 0.0

    normalized_content = normalize_text(content)
    if not normalized_content:
        return 0.0

    content_tokens = set(turkish_bm25_preprocess(normalized_content))
    token_score = 0.0
    for term in terms:
        if term in content_tokens:
            token_score += 1.0 if len(term) >= 5 else 0.7
        elif len(term) >= 5 and term in normalized_content:
            token_score += 0.5

    phrase_score = sum(
        1.5
        for phrase in _source_constrained_query_phrases(query)
        if phrase in normalized_content
    )
    normalized_query = normalize_text(query)
    numeric_score = 0.0
    if (
        any(marker in normalized_query for marker in _SOURCE_CONSTRAINED_NUMERIC_MARKERS)
        and _SOURCE_CONSTRAINED_NUMBER_RE.search(normalized_content)
    ):
        numeric_score = 1.0

    return (
        token_score
        + phrase_score
        + numeric_score
        + _source_constrained_alignment_score(
            query=query,
            topic_hint=topic_hint,
            content=content,
        )
    )


def _source_constrained_recall_score(lexical_score: float) -> float:
    return round(min(0.86, 0.44 + (lexical_score * 0.045)), 6)


def _apply_source_constrained_post_rerank_bias(
    results: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    adjusted: list[dict[str, Any]] = []
    changed = False
    for item in results:
        candidate = dict(item)
        metadata = dict(candidate.get("metadata") or {})
        if metadata.get("source_constrained_recall"):
            lexical_score = float(metadata.get("source_constrained_lexical_score") or 0.0)
            alignment_score = max(float(metadata.get("source_constrained_alignment_score") or 0.0), 0.0)
            boost = min(0.34, (lexical_score * 0.015) + (alignment_score * 0.025))
            if boost > 0:
                original_score = float(candidate.get("score", 0.0))
                candidate["score"] = round(original_score + boost, 6)
                metadata["source_constrained_post_rerank_boost"] = round(boost, 6)
                candidate["metadata"] = metadata
                changed = True
        adjusted.append(candidate)

    if changed:
        adjusted.sort(key=lambda candidate: float(candidate.get("score", 0.0)), reverse=True)
    return adjusted


def _source_constrained_is_application_evidence(
    *,
    query: str,
    content: str,
) -> bool:
    normalized_query = normalize_text(query)
    normalized_content = normalize_text(content)
    asks_application = "basvur" in normalized_query
    if not asks_application:
        return True

    app_markers = (
        "basvuru kabul kayit",
        "basvuru kosullari",
        "basvuru sartlari",
        "basvurabilmesi",
        "basvurusu sirasindaki",
        "basvurularin degerlendirilmesinde",
    )
    if not any(marker in normalized_content for marker in app_markers):
        return False

    cap_topic = any(marker in normalized_query for marker in ("cap", "cift anadal", "cift ana dal"))
    yandal_topic = any(marker in normalized_query for marker in ("ydp", "yandal", "yan dal"))
    if cap_topic and not yandal_topic:
        yandal_markers = ("ydp", "yandal", "yan dal")
        cap_application_markers = (
            "cap'a basvuru kabul",
            "cap a basvuru kabul",
            "cap basvuru kabul",
            "cap'a basvurabilmesi",
            "cap a basvurabilmesi",
        )
        if any(marker in normalized_content for marker in yandal_markers) and not any(
            marker in normalized_content for marker in cap_application_markers
        ):
            return False

    return True


def _filter_source_constrained_by_query_facet(
    results: List[Dict[str, Any]],
    *,
    query: str,
) -> List[Dict[str, Any]]:
    if not results:
        return results

    normalized_query = normalize_text(query)
    if "basvur" not in normalized_query:
        return results

    facet_matches = [
        item
        for item in results
        if _source_constrained_is_application_evidence(
            query=query,
            content=str(item.get("content") or ""),
        )
    ]
    if not facet_matches:
        return results
    return facet_matches


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

    adjusted = False
    for item in results:
        metadata = item.get("metadata") or {}
        if _department_metadata_matches(metadata, student_department):
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


def _normalize_department_scope_text(value: Any) -> str:
    normalized = normalize_text(str(value or ""))
    normalized = re.sub(r"[_\-.]+", " ", normalized)
    return " ".join(normalized.split())


def _department_scope_tokens(value: str) -> set[str]:
    return {
        token
        for token in _normalize_department_scope_text(value).split()
        if len(token) >= 3 and token not in _DEPARTMENT_SCOPE_SUFFIX_WORDS
    }


def _department_metadata_texts(metadata: Dict[str, Any]) -> list[str]:
    texts: list[str] = []
    for key in (
        "bolum_adi",
        "bolum",
        "department_name",
        "program_name",
        "program",
        "source",
        "file_name",
        "relative_path",
    ):
        text = _normalize_department_scope_text(metadata.get(key))
        if not text or text in _DEPARTMENT_SCOPE_GENERIC_VALUES:
            continue
        texts.append(text)
    return list(dict.fromkeys(texts))


def _department_metadata_matches(metadata: Dict[str, Any], student_department: str | None) -> bool:
    requested = _normalize_department_scope_text(student_department)
    if not requested or requested in _DEPARTMENT_SCOPE_GENERIC_VALUES:
        return False

    requested_tokens = _department_scope_tokens(requested)
    for candidate in _department_metadata_texts(metadata):
        if candidate in _DEPARTMENT_SCOPE_GENERIC_VALUES:
            continue
        if requested == candidate or requested in candidate or candidate in requested:
            return True
        candidate_tokens = _department_scope_tokens(candidate)
        if not requested_tokens or not candidate_tokens:
            continue
        overlap = requested_tokens & candidate_tokens
        required_overlap = 1 if min(len(requested_tokens), len(candidate_tokens)) <= 1 else 2
        if len(overlap) >= required_overlap:
            return True
    return False


def _query_may_need_department_scoped_documents(query: str) -> bool:
    normalized_query = normalize_text(query)
    return any(marker in normalized_query for marker in _DEPARTMENT_SCOPED_QUERY_MARKERS)


def _department_scoped_recall_score(lexical_score: float) -> float:
    return round(min(0.82, 0.40 + (lexical_score * 0.05)), 6)


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

    @staticmethod
    def _resource_cache_get(cache: dict, key: Any) -> Any | None:
        """Return a cached value and mark it as recently used."""
        if key not in cache:
            return None
        value = cache.pop(key)
        cache[key] = value
        return value

    @staticmethod
    def _resource_cache_put(
        cache: dict,
        key: Any,
        value: Any,
        *,
        max_entries: int,
        label: str,
    ) -> None:
        """Put a value into a small LRU-style cache."""
        if max_entries <= 0:
            cache.clear()
            return
        if key in cache:
            cache.pop(key)
        cache[key] = value
        while len(cache) > max_entries:
            evicted_key = next(iter(cache))
            cache.pop(evicted_key, None)
            logger.info(
                "bm25_resource_cache_evicted",
                cache=label,
                key=str(evicted_key),
                max_entries=max_entries,
            )

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
        metadata = candidate.get("metadata") or {}
        for key in ("retrieval_collection", "source_constrained_recall_collection"):
            collection_name = str(metadata.get(key) or "").strip()
            if collection_name and collection_name != "__multi__":
                return collection_name

        department_value = department
        if department_value is None:
            department_value = metadata.get("department")
        if not department_value:
            return None

        try:
            return collection_name_for_department(Department(department_value))
        except ValueError:
            return None

    def _load_documents_for_collection(self, collection_name: str) -> List[Document]:
        """Load BM25 cache documents for a collection on demand."""
        cached_documents = self._resource_cache_get(self._BM25_DOCUMENT_CACHE, collection_name)
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

    @staticmethod
    def _metadata_int(value: Any, default: int = 0) -> int:
        """Best-effort int parser for Chroma metadata values."""
        try:
            return int(str(value))
        except (TypeError, ValueError):
            return default

    @classmethod
    def _parent_child_sort_key(cls, candidate: Dict[str, Any]) -> tuple[int, int]:
        """Order chunks inside a parent-child group."""
        metadata = candidate.get("metadata") or {}
        return (
            cls._metadata_int(metadata.get("parent_child_index"), 10**9),
            cls._metadata_int(metadata.get("chunk_index"), 10**9),
        )

    @classmethod
    def _select_parent_context_window(
        cls,
        related_candidates: List[Dict[str, Any]],
        *,
        hit_metadata: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Keep a bounded parent context window around the hit child."""
        max_chars = max(int(settings.rag.parent_context_max_chars or 0), 0)
        if max_chars <= 0:
            return related_candidates

        total_chars = sum(len(str(item.get("content") or "")) for item in related_candidates)
        if total_chars <= max_chars:
            return related_candidates

        hit_child_index = cls._metadata_int(hit_metadata.get("parent_child_index"), -1)
        hit_chunk_index = cls._metadata_int(hit_metadata.get("chunk_index"), -1)
        hit_index = 0
        for index, item in enumerate(related_candidates):
            item_metadata = item.get("metadata") or {}
            if (
                cls._metadata_int(item_metadata.get("parent_child_index"), -2) == hit_child_index
                and cls._metadata_int(item_metadata.get("chunk_index"), -2) == hit_chunk_index
            ):
                hit_index = index
                break

        selected = {hit_index}
        current_chars = len(str(related_candidates[hit_index].get("content") or ""))
        left = hit_index - 1
        right = hit_index + 1
        while left >= 0 or right < len(related_candidates):
            added = False
            if right < len(related_candidates):
                candidate_len = len(str(related_candidates[right].get("content") or ""))
                if current_chars + candidate_len <= max_chars:
                    selected.add(right)
                    current_chars += candidate_len
                    added = True
                right += 1
            if left >= 0:
                candidate_len = len(str(related_candidates[left].get("content") or ""))
                if current_chars + candidate_len <= max_chars:
                    selected.add(left)
                    current_chars += candidate_len
                    added = True
                left -= 1
            if not added and (right >= len(related_candidates) and left < 0):
                break
            if not added and current_chars >= max_chars:
                break
        return [item for index, item in enumerate(related_candidates) if index in selected]

    def _expand_parent_child_context(
        self,
        candidate: Dict[str, Any],
        *,
        department: Department | str | None = None,
    ) -> Dict[str, Any] | None:
        """Expand a child hit to its bounded parent context when available."""
        metadata = dict(candidate.get("metadata") or {})
        parent_id = str(metadata.get("parent_id") or "").strip()
        parent_child_count = self._metadata_int(metadata.get("parent_child_count"), 1)
        if (
            not settings.rag.parent_child_chunking_enabled
            or not parent_id
            or parent_child_count <= 1
        ):
            return None

        document_key = _metadata_identity_key(metadata)
        collection_name = self._resolve_collection_name_for_candidate(candidate, department=department)
        if not collection_name:
            return None

        related_candidates: List[Dict[str, Any]] = []
        for document in self._load_documents_for_collection(collection_name):
            doc_metadata = dict(document.metadata or {})
            if _metadata_identity_key(doc_metadata) != document_key:
                continue
            if str(doc_metadata.get("parent_id") or "").strip() != parent_id:
                continue
            related_candidates.append(
                {
                    "content": document.page_content,
                    "metadata": doc_metadata,
                }
            )

        if len(related_candidates) <= 1:
            return None

        related_candidates.sort(key=self._parent_child_sort_key)
        related_candidates = self._select_parent_context_window(
            related_candidates,
            hit_metadata=metadata,
        )
        merged_content = merge_chunk_texts(item["content"] for item in related_candidates)
        if not merged_content:
            return None

        metadata["context_expanded"] = True
        metadata["parent_context_expanded"] = True
        metadata["merged_chunk_count"] = len(related_candidates)
        metadata["merged_parent_id"] = parent_id
        metadata["merged_parent_child_indexes"] = ",".join(
            str(item["metadata"].get("parent_child_index", ""))
            for item in related_candidates
            if item["metadata"].get("parent_child_index") is not None
        )
        return {
            **candidate,
            "content": merged_content,
            "metadata": metadata,
        }

    def _expand_candidate_context(
        self,
        candidate: Dict[str, Any],
        *,
        department: Department | str | None = None,
    ) -> Dict[str, Any]:
        """Expand a result to the full MADDE span when the hit is only one sub-chunk."""
        parent_expanded = self._expand_parent_child_context(candidate, department=department)
        if parent_expanded is not None:
            return parent_expanded

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
        *,
        source_owner_bridge: SourceOwnerCollectionBridge | None = None,
    ) -> List[Dict[str, Any]]:
        """Collect candidates from primary collections, then fallback if needed."""
        candidates: List[Dict[str, Any]] = []
        for collection_name in primary_collections:
            candidates.extend(
                self._annotate_collection_candidates(
                    self._search_collection_candidates(collection_name, expanded_query),
                    collection_name=collection_name,
                    source_owner_bridge=source_owner_bridge,
                )
            )

        if not fallback_collections:
            return candidates

        should_fallback, fallback_reason, primary_top_score = self._should_collect_fallback_candidates(candidates)
        if not should_fallback:
            return candidates

        logger.info(
            "hybrid_search_fallback",
            query=query,
            collections=fallback_collections,
            reason=fallback_reason,
            primary_top_score=primary_top_score,
        )
        for collection_name in fallback_collections:
            candidates.extend(
                self._annotate_collection_candidates(
                    self._search_collection_candidates(collection_name, expanded_query),
                    collection_name=collection_name,
                    source_owner_bridge=source_owner_bridge,
                )
            )
        return candidates

    @staticmethod
    def _should_collect_fallback_candidates(
        primary_candidates: List[Dict[str, Any]],
    ) -> tuple[bool, str, float | None]:
        """Decide whether fallback collections should augment weak primary hits."""
        if not primary_candidates:
            return True, "empty_primary", None

        threshold = float(settings.rag.fallback_primary_score_threshold or 0.0)
        if threshold <= 0:
            return False, "disabled", None

        primary_top_score = max(float(candidate.get("score", 0.0)) for candidate in primary_candidates)
        if primary_top_score < threshold:
            return True, "weak_primary_score", round(primary_top_score, 6)
        return False, "primary_score_ok", round(primary_top_score, 6)

    @staticmethod
    def _annotate_collection_candidates(
        candidates: List[Dict[str, Any]],
        *,
        collection_name: str,
        source_owner_bridge: SourceOwnerCollectionBridge | None = None,
    ) -> List[Dict[str, Any]]:
        """Attach collection/bridge diagnostics to retriever candidates."""
        if not candidates:
            return candidates
        support_collections = set(source_owner_bridge.support_collections if source_owner_bridge else ())
        bridge_active = bool(source_owner_bridge and source_owner_bridge.active)
        annotated: list[dict[str, Any]] = []
        for candidate in candidates:
            item = dict(candidate)
            metadata = dict(item.get("metadata") or {})
            metadata.setdefault("retrieval_collection", collection_name)
            if bridge_active:
                if collection_name in support_collections:
                    metadata["retrieval_collection_role"] = "source_owner_support"
                    metadata["source_owner_collection_bridge"] = source_owner_bridge.as_metadata()
                else:
                    metadata.setdefault("retrieval_collection_role", "source_owner_primary")
            item["metadata"] = metadata
            annotated.append(item)
        return annotated

    def _source_documents_for_recall(self, collection_name: str) -> List[Document]:
        """Return collection documents for source-constrained lexical recall."""
        cached_documents = self._resource_cache_get(self._BM25_DOCUMENT_CACHE, collection_name)
        if cached_documents is not None:
            return cached_documents

        try:
            indexer = self._get_indexer(collection_name)
            return self._load_bm25_documents(collection_name, indexer)
        except Exception:
            logger.warning(
                "source_constrained_recall_documents_unavailable",
                collection=collection_name,
                exc_info=True,
            )
            return []

    def _augment_candidates_with_source_constrained_recall(
        self,
        candidates: List[Dict[str, Any]],
        *,
        query: str,
        collection_names: List[str],
        source_constraints: tuple[str, ...],
        topic_hint: str | None,
        source_owner_bridge: SourceOwnerCollectionBridge | None = None,
    ) -> List[Dict[str, Any]]:
        """Add high-signal lexical hits from contract/conversation-constrained sources."""
        if (
            not settings.rag.source_constrained_recall_enabled
            or not source_constraints
            or not collection_names
        ):
            return candidates

        recalled: list[dict[str, Any]] = []
        max_per_collection = max(settings.rag.source_constrained_recall_max_per_collection, 0)
        max_total = max(settings.rag.source_constrained_recall_max_total, 0)
        if max_per_collection <= 0 or max_total <= 0:
            return candidates

        for collection_name in collection_names:
            collection_recalled: list[tuple[float, dict[str, Any]]] = []
            for document in self._source_documents_for_recall(collection_name):
                source_text = _document_source_text(document)
                if not _source_matches_constraints(source_text, source_constraints):
                    continue

                lexical_score = _source_constrained_lexical_score(
                    query=query,
                    topic_hint=topic_hint,
                    content=document.page_content,
                )
                if lexical_score < 3.0:
                    continue
                alignment_score = _source_constrained_alignment_score(
                    query=query,
                    topic_hint=topic_hint,
                    content=document.page_content,
                )

                metadata = dict(document.metadata or {})
                metadata["source_constrained_recall"] = True
                metadata["source_constrained_recall_collection"] = collection_name
                metadata.setdefault("retrieval_collection", collection_name)
                if (
                    source_owner_bridge
                    and collection_name in set(source_owner_bridge.support_collections)
                ):
                    metadata["retrieval_collection_role"] = "source_owner_support"
                    metadata["source_owner_collection_bridge"] = source_owner_bridge.as_metadata()
                metadata["source_constrained_lexical_score"] = round(lexical_score, 4)
                metadata["source_constrained_alignment_score"] = round(alignment_score, 4)
                metadata.setdefault("score_type", "source_constrained_recall")
                candidate = {
                    "content": document.page_content,
                    "source": metadata.get("source") or metadata.get("file_name") or "bilinmiyor",
                    "category": metadata.get("category", "genel"),
                    "score": _source_constrained_recall_score(lexical_score),
                    "metadata": metadata,
                }
                collection_recalled.append((lexical_score, candidate))

            collection_recalled.sort(
                key=lambda pair: (
                    pair[0],
                    float(pair[1].get("score", 0.0)),
                ),
                reverse=True,
            )
            recalled.extend(candidate for _, candidate in collection_recalled[:max_per_collection])
            if len(recalled) >= max_total:
                break

        if not recalled:
            return candidates

        logger.info(
            "source_constrained_recall_applied",
            query=query,
            added_count=min(len(recalled), max_total),
            constraints=list(source_constraints),
            collections=collection_names,
        )
        return deduplicate_candidate_dicts([*candidates, *recalled[:max_total]])

    def _department_scoped_recall_collections(
        self,
        *,
        query: str,
        primary_collections: List[str],
        fallback_collections: List[str],
        student_department: str | None,
    ) -> list[str]:
        """Return collections worth scanning for department-specific documents."""
        if not student_department or not _query_may_need_department_scoped_documents(query):
            return []

        collections: list[str] = []
        for collection_name in [*primary_collections, *fallback_collections]:
            if collection_name not in collections:
                collections.append(collection_name)

        academic_collection = collection_name_for_department(Department.ACADEMIC_PROGRAMS)
        if academic_collection not in collections:
            collections.append(academic_collection)
        return collections

    def _augment_candidates_with_department_scoped_recall(
        self,
        candidates: List[Dict[str, Any]],
        *,
        query: str,
        collection_names: List[str],
        student_department: str | None,
        topic_hint: str | None,
        source_owner_bridge: SourceOwnerCollectionBridge | None = None,
    ) -> List[Dict[str, Any]]:
        """Add relevant department-specific documents when a program is explicitly known."""
        if (
            not settings.rag.department_scoped_recall_enabled
            or not student_department
            or not collection_names
            or not _query_may_need_department_scoped_documents(query)
        ):
            return candidates

        max_per_collection = max(settings.rag.department_scoped_recall_max_per_collection, 0)
        max_total = max(settings.rag.department_scoped_recall_max_total, 0)
        min_lexical_score = float(settings.rag.department_scoped_recall_min_lexical_score)
        if max_per_collection <= 0 or max_total <= 0:
            return candidates

        recalled: list[dict[str, Any]] = []
        support_collections = set(source_owner_bridge.support_collections if source_owner_bridge else ())
        for collection_name in collection_names:
            collection_recalled: list[tuple[float, dict[str, Any]]] = []
            for document in self._source_documents_for_recall(collection_name):
                metadata = dict(document.metadata or {})
                if not _department_metadata_matches(metadata, student_department):
                    continue

                lexical_score = _source_constrained_lexical_score(
                    query=query,
                    topic_hint=topic_hint,
                    content=document.page_content,
                )
                if lexical_score < min_lexical_score:
                    continue

                metadata["department_scoped_recall"] = True
                metadata["department_scoped_recall_collection"] = collection_name
                metadata["department_scoped_recall_student_department"] = student_department
                metadata["department_scoped_lexical_score"] = round(lexical_score, 4)
                metadata.setdefault("retrieval_collection", collection_name)
                if source_owner_bridge and collection_name in support_collections:
                    metadata["retrieval_collection_role"] = "source_owner_support"
                    metadata["source_owner_collection_bridge"] = source_owner_bridge.as_metadata()
                metadata.setdefault("score_type", "department_scoped_recall")
                candidate = {
                    "content": document.page_content,
                    "source": metadata.get("source") or metadata.get("file_name") or "bilinmiyor",
                    "category": metadata.get("category", "genel"),
                    "score": _department_scoped_recall_score(lexical_score),
                    "metadata": metadata,
                }
                collection_recalled.append((lexical_score, candidate))

            collection_recalled.sort(
                key=lambda pair: (
                    pair[0],
                    float(pair[1].get("score", 0.0)),
                ),
                reverse=True,
            )
            recalled.extend(candidate for _, candidate in collection_recalled[:max_per_collection])
            if len(recalled) >= max_total:
                break

        if not recalled:
            return candidates

        logger.info(
            "department_scoped_recall_applied",
            query=query,
            student_department=student_department,
            added_count=min(len(recalled), max_total),
            collections=collection_names,
        )
        return deduplicate_candidate_dicts([*candidates, *recalled[:max_total]])

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
        source_owner: str | None = None,
        reranker_candidate_limit: int | None = None,
    ) -> str:
        """Build a stable cache key for a search request."""
        normalized_hints = "|".join(sorted(hint.strip().casefold() for hint in (source_hints or []) if hint))
        normalized_topic = (topic_hint or "").strip().casefold()
        normalized_dept = (student_department or "").strip().casefold()
        normalized_owner = (source_owner or "").strip().casefold()
        return (
            f"{query}::{top_k}::"
            f"{'|'.join(primary_collections)}::"
            f"{'|'.join(fallback_collections)}::"
            f"{normalized_hints}::"
            f"{normalized_topic}::"
            f"{normalized_dept}::"
            f"{normalized_owner}::"
            f"{reranker_candidate_limit or ''}"
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
        source_constrained: bool = False,
        reranker_candidate_limit: int | None = None,
    ) -> List[Dict[str, Any]]:
        """Apply reranker policy and return ranked candidates."""
        reranker_limit = self._reranker_candidate_limit(
            search_scope,
            query_type,
            top_k,
            query=query,
        )
        if source_constrained:
            reranker_limit = max(
                reranker_limit,
                min(
                    len(candidates),
                    top_k + settings.rag.source_constrained_reranker_extra,
                ),
            )
        if reranker_candidate_limit is not None:
            reranker_limit = min(reranker_limit, max(1, int(reranker_candidate_limit)))
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
        semaphore = _reranker_semaphore()
        if semaphore is None:
            return self.reranker.rerank(clean_query, reranker_candidates, top_k=top_k)
        wait_started = time.perf_counter()
        with semaphore:
            logger.info(
                "reranker_concurrency_guard",
                query=query,
                limit=settings.rag.reranker_concurrency_limit,
                waited_ms=round((time.perf_counter() - wait_started) * 1000, 1),
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
        cached_documents = self._resource_cache_get(self._BM25_DOCUMENT_CACHE, collection_name)
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
            self._resource_cache_put(
                self._BM25_DOCUMENT_CACHE,
                collection_name,
                documents,
                max_entries=settings.cache.bm25_document_cache_max_collections,
                label="documents",
            )
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
        cached_retriever = self._resource_cache_get(self._BM25_RETRIEVER_CACHE, cache_key)
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
            self._resource_cache_put(
                self._BM25_RETRIEVER_CACHE,
                cache_key,
                bm25_retriever,
                max_entries=settings.cache.bm25_retriever_cache_max_entries,
                label="retrievers",
            )
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
        source_owner: str | None = None,
        reranker_candidate_limit: int | None = None,
    ) -> List[Dict[str, Any]]:
        """Run hybrid retrieval and return ranked results."""
        start_time = time.perf_counter()
        k = top_k or self.k
        primary_collections, fallback_collections = self._resolve_search_collections(
            query=query,
            department=department,
        )
        source_owner_bridge = resolve_source_owner_collection_bridge(
            source_owner=source_owner,
            query=query,
            department=department,
            source_hints=source_hints,
            topic_hint=topic_hint,
        )
        if source_owner_bridge.active:
            for collection_name in source_owner_bridge.support_collections:
                if collection_name not in primary_collections and collection_name not in fallback_collections:
                    primary_collections.append(collection_name)
            logger.info(
                "source_owner_collection_bridge_applied",
                source_owner=source_owner_bridge.source_owner,
                support_collections=list(source_owner_bridge.support_collections),
                reason=source_owner_bridge.reason,
                activated_by=list(source_owner_bridge.activated_by),
            )

        cache_key = self._build_cache_key(
            query=query,
            top_k=k,
            primary_collections=primary_collections,
            fallback_collections=fallback_collections,
            source_hints=source_hints,
            topic_hint=topic_hint,
            student_department=student_department,
            source_owner=source_owner,
            reranker_candidate_limit=reranker_candidate_limit,
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
            source_owner_bridge=source_owner_bridge,
        )
        source_constraints = _normalized_source_constraints(source_hints)
        hard_constrain_sources = _has_concrete_source_hints(source_hints)
        if not candidates:
            candidates = self._augment_candidates_with_source_constrained_recall(
                [],
                query=query,
                collection_names=[*primary_collections, *fallback_collections],
                source_constraints=source_constraints,
                topic_hint=topic_hint,
                source_owner_bridge=source_owner_bridge,
            )
        if not candidates:
            logger.warning("hybrid_search_no_candidates", query=query, collections=primary_collections)
            return []

        candidates = deduplicate_candidate_dicts(candidates)
        candidates = self._augment_candidates_with_source_constrained_recall(
            candidates,
            query=query,
            collection_names=primary_collections,
            source_constraints=source_constraints,
            topic_hint=topic_hint,
            source_owner_bridge=source_owner_bridge,
        )
        if hard_constrain_sources:
            constrained_candidates = _filter_candidates_by_source_constraints(
                candidates,
                source_constraints,
            )
            if constrained_candidates:
                candidates = constrained_candidates
            else:
                logger.info(
                    "source_constrained_filter_empty",
                    query=query,
                    constraints=list(source_constraints),
                    collections=primary_collections,
                )
                return []
        if not hard_constrain_sources:
            department_recall_collections = self._department_scoped_recall_collections(
                query=query,
                primary_collections=primary_collections,
                fallback_collections=fallback_collections,
                student_department=student_department,
            )
            candidates = self._augment_candidates_with_department_scoped_recall(
                candidates,
                query=query,
                collection_names=department_recall_collections,
                student_department=student_department,
                topic_hint=topic_hint,
                source_owner_bridge=source_owner_bridge,
            )
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
            source_constrained=bool(source_constraints),
            reranker_candidate_limit=reranker_candidate_limit,
        )
        if source_constraints:
            results = _apply_source_constrained_post_rerank_bias(results)
            results = _filter_source_constrained_by_query_facet(results, query=query)
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
