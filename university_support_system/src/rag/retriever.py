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
from src.core.constants import Department, collection_name_for_department
from src.rag.candidate_utils import (
    deduplicate_candidate_dicts,
    deduplicate_documents,
    sort_candidates_by_score,
)
from src.rag.query_cache import _QueryCache as _SharedQueryCache
from src.rag.query_preprocessor import QueryPreprocessor
from src.rag.search_planner import (
    OFF_TOPIC_PENALTY as _SHARED_OFF_TOPIC_PENALTY,
    _apply_finance_source_penalty as _shared_apply_finance_source_penalty,
    _apply_source_relevance as _shared_apply_source_relevance,
    _detect_query_topic as _shared_detect_query_topic,
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
    "lisansustu": "lisans ustu",
    "çiftanadal": "çift ana dal",
    "lisansüstü": "lisans üstü",
}


def turkish_bm25_preprocess(text: str) -> List[str]:
    """Normalize and tokenize Turkish text for BM25."""
    if not text:
        return []

    normalized_text = text.lower()
    for compound, split in _COMPOUND_SPLITS.items():
        normalized_text = normalized_text.replace(compound, split)

    normalized_text = _PUNCTUATION_RE.sub(" ", normalized_text)
    normalized_text = _WHITESPACE_RE.sub(" ", normalized_text).strip()

    tokens = normalized_text.split()
    return [token for token in tokens if len(token) > 1]


OFF_TOPIC_PENALTY = _SHARED_OFF_TOPIC_PENALTY
CONVERSATION_SOURCE_HINT_BOOST = 0.08
CONVERSATION_TOPIC_HINT_BOOST = 0.04


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
        from src.rag.embedder import Embedder
        from src.rag.reranker import CrossEncoderReranker

        self.embedder = Embedder()
        self.reranker = CrossEncoderReranker()

        self._indexers: Dict[str, ChromaIndexer] = {}
        self._ensembles: Dict[str, EnsembleRetriever] = {}
        self._bm25_doc_counts: Dict[str, int] = {}
        self._cache = _QueryCache(ttl=cache_ttl)

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
        finally:
            retriever.close()

    @staticmethod
    def _sort_candidates_by_score(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort candidates by score descending."""
        return sort_candidates_by_score(candidates)

    def _reranker_candidate_limit(self, collection_name: str, query_type: str, top_k: int) -> int:
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
            base_limit = max(base_limit, top_k + 4)

        return max(top_k, base_limit)

    def _should_skip_reranker(
        self,
        collection_name: str,
        query_type: str,
        candidates: List[Dict[str, Any]],
        top_k: int,
    ) -> bool:
        """Skip reranker in narrow high-signal scenarios to save latency."""
        if len(candidates) <= top_k:
            return True

        if (
            settings.rag.skip_reranker_for_finance_narrow_queries
            and collection_name == collection_name_for_department(Department.FINANCE)
            and query_type in {"factual", "procedural"}
        ):
            return True

        if (
            settings.rag.skip_reranker_for_student_affairs_procedural
            and collection_name == collection_name_for_department(Department.STUDENT_AFFAIRS)
            and query_type == "procedural"
        ):
            return True

        if (
            settings.rag.skip_reranker_for_academic_programs_procedural
            and collection_name == collection_name_for_department(Department.ACADEMIC_PROGRAMS)
            and query_type == "procedural"
        ):
            return True

        return False

    def _rank_without_reranker(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """Use fusion score ordering when reranker is skipped."""
        _ = query
        return self._sort_candidates_by_score(candidates)[:top_k]

    def _resolve_search_collections(
        self,
        query: str,
        department: Department | str | None,
    ) -> tuple[List[str], List[str]]:
        """Resolve primary and fallback collections for the query."""
        if department is not None:
            primary_departments, fallback_departments = _plan_search_departments(query, department)
            return (
                [collection_name_for_department(dep) for dep in primary_departments],
                [collection_name_for_department(dep) for dep in fallback_departments],
            )

        if self.collection_name is not None:
            return [self.collection_name], []

        primary_departments, fallback_departments = _plan_search_departments(query)
        return (
            [collection_name_for_department(dep) for dep in primary_departments],
            [collection_name_for_department(dep) for dep in fallback_departments],
        )

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

    @staticmethod
    def _build_cache_key(
        query: str,
        top_k: int,
        primary_collections: List[str],
        fallback_collections: List[str],
        source_hints: List[str] | None = None,
        topic_hint: str | None = None,
    ) -> str:
        """Build a stable cache key for a search request."""
        normalized_hints = "|".join(sorted(hint.strip().casefold() for hint in (source_hints or []) if hint))
        normalized_topic = (topic_hint or "").strip().casefold()
        return (
            f"{query}::{top_k}::"
            f"{'|'.join(primary_collections)}::"
            f"{'|'.join(fallback_collections)}::"
            f"{normalized_hints}::"
            f"{normalized_topic}"
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
        query_type: str,
        candidates: List[Dict[str, Any]],
        search_scope: str,
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """Apply reranker policy and return ranked candidates."""
        reranker_limit = self._reranker_candidate_limit(search_scope, query_type, top_k)
        reranker_candidates = candidates[:reranker_limit]

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
            collection=search_scope,
            query_type=query_type,
            original_candidate_count=len(candidates),
            reranker_candidate_count=len(reranker_candidates),
            top_k=top_k,
        )
        return self.reranker.rerank(query, reranker_candidates, top_k=top_k)

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
            results = [result for result in results if result["score"] >= self.min_score]

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
        if cached_documents is not None:
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
        if cached_retriever is not None:
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
        )
        cached = self._try_cache_hit(
            cache_key=cache_key,
            query=query,
            start_time=start_time,
        )
        if cached is not None:
            return cached

        expanded_query = self.query_preprocessor.preprocess(query)
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
        candidates = _apply_finance_source_penalty(candidates, query, search_scope)
        candidates = self._sort_candidates_by_score(candidates)
        results = self._rank_candidates(
            query=query,
            query_type=query_type,
            candidates=candidates,
            search_scope=search_scope,
            top_k=k,
        )
        results = _apply_finance_source_penalty(results, query, search_scope)
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
