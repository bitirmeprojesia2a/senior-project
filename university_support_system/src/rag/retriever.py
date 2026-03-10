"""
Hibrit Arama (Hybrid Search) Modulu — v3.0

BM25 (keyword) + ChromaDB (semantic) + Cross-Encoder Reranking.

v3.0 Degisiklikler:
    - Cross-encoder reranking (seroe/bge-reranker-v2-m3-turkish-triplet)
    - BM25 page_content orijinal metin (dedup tutarliligi)
    - Semantic skor kaybi duzeltmesi (max score korunur)
    - min_score filtresi (config'den okunur)
    - Compound word split preprocess_func icerisinde

Kullanim:
    from src.rag.retriever import HybridRetriever

    from src.core.constants import Department, collection_name_for_department

    retriever = HybridRetriever(
        collection_name=collection_name_for_department(Department.STUDENT_AFFAIRS)
    )
    results = retriever.search("Cift anadal basvurusu nasil yapilir?")
"""

import re
import time
from typing import Any, Dict, List, Optional

import structlog
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever

from src.core.config import settings
from src.core.constants import (
    Department,
    collection_name_for_department,
    get_department_config,
    normalize_department_value,
)
from src.rag.indexer import ChromaIndexer
from src.rag.embedder import Embedder
from src.rag.query_preprocessor import QueryPreprocessor
from src.rag.reranker import CrossEncoderReranker

logger = structlog.get_logger()


# ── Türkçe BM25 Tokenizer ────────────────────────────────────────────

_PUNCTUATION_RE = re.compile(r"[^\w\s]")
_WHITESPACE_RE = re.compile(r"\s+")


def turkish_bm25_preprocess(text: str) -> List[str]:
    """
    Turkce metin icin BM25 tokenizer.

    Bu fonksiyon hem belge indekslemede hem sorgu zamaninda cagrilir.
    Compound word split + noktalama temizleme + tokenizasyon yapar.
    Boylece BM25 Document'inin page_content'i orijinal metin olabilir
    ve EnsembleRetriever dedup'i dogru calisir.

    Args:
        text: Tokenize edilecek metin.

    Returns:
        Token listesi (kucuk harfli, compound-split, noktalama temiz).
    """
    if not text:
        return []

    text = text.lower()

    # Compound word split (anadal → ana dal, yandal → yan dal)
    for compound, split in _COMPOUND_SPLITS.items():
        text = text.replace(compound, split)

    text = _PUNCTUATION_RE.sub(" ", text)
    text = _WHITESPACE_RE.sub(" ", text).strip()

    tokens = text.split()
    tokens = [t for t in tokens if len(t) > 1]

    return tokens


# BM25 tokenizer icinde kullanilan compound word splits
_COMPOUND_SPLITS = {
    "anadal": "ana dal",
    "yandal": "yan dal",
    "çiftanadal": "çift ana dal",
    "lisansüstü": "lisans üstü",
}


# ── Kaynak Uyumluluğu (Source Relevance) ─────────────────────────────
# Sorgu konusu ile kaynak dosya adı arasında uyumsuzluk varsa
# cross-encoder skoruna hafif penalty uygulanır.
# Konu tespiti yapılamayan sorgularda hiçbir etki olmaz.

OFF_TOPIC_PENALTY = 0.75


def _turkish_lower(text: str) -> str:
    """Python'un İ→i̇ (combining dot) sorununu düzelten Türkçe lowercase."""
    return text.replace("İ", "i").replace("I", "ı").lower()

_TOPIC_SOURCE_PATTERNS: Dict[str, List[str]] = {
    "çap": ["cift_anadal", "çift ana dal", "çap"],
    "çift anadal": ["cift_anadal", "çift ana dal", "çap"],
    "çift ana dal": ["cift_anadal", "çift ana dal", "çap"],
    "ikinci lisans": ["cift_anadal", "çift ana dal", "çap"],
    "yan dal": ["cift_anadal", "yan dal", "yandal"],
    "yandal": ["cift_anadal", "yan dal", "yandal"],
    "ydp": ["cift_anadal", "yan dal", "yandal"],
    "yatay geçiş": ["yatay_gecis", "yatay geçiş"],
    "dikey geçiş": ["dikey_gecis", "dikey geçiş"],
    "staj": ["staj", "intörn"],
    "yaz okulu": ["yaz_okulu", "yaz okulu"],
    "erasmus": ["erasmus", "değişim", "uluslararası"],
    "mevlana": ["mevlana", "değişim"],
    "farabi": ["farabi", "değişim"],
    "muafiyet": ["muafiyet"],
    "disiplin": ["disiplin"],
}

# Uzun kalıplar önce eşleşmeli (örn. "çift ana dal" > "çap")
_TOPIC_KEYS_BY_LENGTH = sorted(_TOPIC_SOURCE_PATTERNS.keys(), key=len, reverse=True)

_DEPARTMENT_KEYWORDS: Dict[Department, List[str]] = {
    department: list(get_department_config(department).keywords)
    for department in Department
}


def _detect_query_topic(query: str) -> Optional[str]:
    """Sorgudaki ana konu anahtar kelimesini tespit eder."""
    q = query.lower()
    for topic in _TOPIC_KEYS_BY_LENGTH:
        if topic in q:
            return topic
    return None


def _score_departments(query: str) -> Dict[Department, int]:
    """Sorgu için departman bazlı anahtar kelime skoru üretir."""
    q = _turkish_lower(query)
    scores: Dict[Department, int] = {}
    for department, keywords in _DEPARTMENT_KEYWORDS.items():
        score = sum(1 for keyword in keywords if _turkish_lower(keyword) in q)
        scores[department] = score
    return scores


def _plan_search_departments(
    query: str,
    explicit_department: Department | str | None = None,
) -> tuple[List[Department], List[Department]]:
    """Sorgu için birincil ve fallback departman planını belirler."""
    if explicit_department is not None:
        normalized = explicit_department if isinstance(explicit_department, Department) else normalize_department_value(explicit_department)
        department = normalized if isinstance(normalized, Department) else Department(normalized)
        return [department], []

    scores = _score_departments(query)
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    top_department, top_score = ranked[0]
    second_department, second_score = ranked[1]

    if top_score == 0:
        return [department for department, _ in ranked], []

    if second_score > 0 and second_score >= top_score - 1:
        primary = [top_department, second_department]
        fallback = [department for department, score in ranked[2:] if score > 0]
        return primary, fallback

    fallback = [second_department] if second_score > 0 else []
    return [top_department], fallback


def _apply_source_relevance(
    results: List[Dict[str, Any]],
    query: str,
    penalty: float = OFF_TOPIC_PENALTY,
) -> List[Dict[str, Any]]:
    """
    Konu-kaynak uyumsuzlugu olan sonuclara penalty uygular.

    - Konu tespiti yapilamazsa sonuclar aynen doner (guvenli).
    - On-topic sonuclara dokunulmaz.
    - Off-topic sonuclarin skoru *= penalty ile azaltilir ve yeniden siralanir.
    """
    topic = _detect_query_topic(query)
    if not topic:
        return results

    expected = _TOPIC_SOURCE_PATTERNS.get(topic, [])
    if not expected:
        return results

    adjusted = False
    for r in results:
        src = _turkish_lower(r["source"])
        on_topic = any(p in src for p in expected)
        if not on_topic:
            r["score"] = round(r["score"] * penalty, 4)
            adjusted = True

    if adjusted:
        results.sort(key=lambda c: c["score"], reverse=True)
        logger.debug(
            "source_relevance_applied",
            topic=topic,
            adjusted_scores=[(r["source"], r["score"]) for r in results[:5]],
        )

    return results



# ══════════════════════════════════════════════════════════════════════
# ChromaDB LangChain Retriever Wrapper
# ══════════════════════════════════════════════════════════════════════

class ChromaRestRetriever(BaseRetriever):
    """LangChain uyumlu ChromaDB REST API Retriever."""

    indexer: Any
    embedder: Any
    k: int = 5

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        query_vector = self.embedder.embed_single(query, is_query=True)
        results = self.indexer.query(query_embedding=query_vector, n_results=self.k)

        documents = []
        if results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            metadatas = results["metadatas"][0] if results.get("metadatas") else []
            distances = results["distances"][0] if results.get("distances") else []
            for i, doc_text in enumerate(docs):
                meta = metadatas[i] if i < len(metadatas) else {}
                dist = distances[i] if i < len(distances) else 0.0
                meta["similarity_score"] = round(1 - dist, 4)
                documents.append(Document(page_content=doc_text, metadata=meta))

        return documents


# ══════════════════════════════════════════════════════════════════════
# Sorgu Cache
# ══════════════════════════════════════════════════════════════════════

class _QueryCache:
    """TTL tabanlı in-memory sorgu cache'i."""

    def __init__(self, ttl: int = 300):
        self._store: Dict[str, tuple] = {}
        self._ttl = ttl

    def get(self, key: str) -> List[Dict[str, Any]] | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        timestamp, results = entry
        if time.time() - timestamp < self._ttl:
            return results
        del self._store[key]
        return None

    def put(self, key: str, results: List[Dict[str, Any]]) -> None:
        self._store[key] = (time.time(), results)

    def invalidate(self) -> None:
        self._store.clear()

    @property
    def size(self) -> int:
        return len(self._store)


# ══════════════════════════════════════════════════════════════════════
# Hibrit Arama Sınıfı (Ana Sınıf)
# ══════════════════════════════════════════════════════════════════════

class HybridRetriever:
    """
    BM25 + ChromaDB + Cross-Encoder Reranking.

    Akis:
        Sorgu → QueryPreprocessor → EnsembleRetriever (BM25+ChromaDB)
        → Dedup (max score) → Cross-Encoder Rerank → Source Relevance
        → min_score filtre → Top-K

    Args:
        collection_name: ChromaDB koleksiyon adi.
        k: Dondurelecek sonuc sayisi.
        bm25_weight: BM25 agirligi (0.0-1.0).
        chroma_weight: Vektor arama agirligi (0.0-1.0).
        enable_query_expansion: Sinonim genisletme aktif mi?
        min_score: Minimum cross-encoder skoru. None ise config'den.
    """

    OVERSAMPLE_FACTOR = 4

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

        self.query_preprocessor = QueryPreprocessor(
            enable_expansion=enable_query_expansion
        )
        self.embedder = Embedder()
        self.reranker = CrossEncoderReranker()

        self._indexers: Dict[str, ChromaIndexer] = {}
        self._ensembles: Dict[str, EnsembleRetriever] = {}
        self._bm25_doc_counts: Dict[str, int] = {}
        self._cache = _QueryCache(ttl=cache_ttl)

    def _get_indexer(self, collection_name: str) -> ChromaIndexer:
        """Koleksiyon için indexer örneğini döndürür."""
        indexer = self._indexers.get(collection_name)
        if indexer is None:
            indexer = ChromaIndexer(collection_name=collection_name)
            self._indexers[collection_name] = indexer
        return indexer

    def _ensure_ensemble(self, collection_name: str) -> EnsembleRetriever:
        """Ensemble retriever'ı tembel (lazy) olarak başlatır."""
        ensemble = self._ensembles.get(collection_name)
        if ensemble is not None:
            return ensemble

        logger.info("building_hybrid_retriever", collection=collection_name)

        internal_k = self.k * self.OVERSAMPLE_FACTOR
        indexer = self._get_indexer(collection_name)

        # 1. Chroma Retriever (Semantic)
        chroma_retriever = ChromaRestRetriever(
            indexer=indexer, embedder=self.embedder, k=internal_k
        )

        # 2. BM25 hazırlık — page_content ORİJİNAL metin olmalı
        #    (compound split ve tokenizasyon preprocess_func icerisinde yapilir)
        #    Boylece EnsembleRetriever dedup'i dogru calisir cunku
        #    BM25 ve ChromaDB ayni page_content'e sahip olur.
        logger.info("fetching_data_for_bm25_index")
        all_data = indexer.get_all()

        documents: List[Document] = []
        if all_data.get("documents"):
            docs = all_data["documents"]
            metas = all_data.get("metadatas", [])
            for i, text in enumerate(docs):
                meta = metas[i] if metas and i < len(metas) else {}
                documents.append(
                    Document(page_content=text, metadata=meta)
                )

        self._bm25_doc_counts[collection_name] = len(documents)

        # 3. BM25 — Türkçe tokenizer ile
        logger.info("initializing_bm25_engine", total_docs=len(documents))
        if documents:
            bm25_retriever = BM25Retriever.from_documents(
                documents,
                preprocess_func=turkish_bm25_preprocess,
            )
            bm25_retriever.k = internal_k
        else:
            logger.warning("no_documents_for_bm25")
            bm25_retriever = BM25Retriever.from_documents(
                [Document(page_content="boş")],
                preprocess_func=turkish_bm25_preprocess,
            )
            bm25_retriever.k = internal_k

        # 4. Ensemble (RRF Fusion)
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
        """Aynı içeriğe sahip adayları tekilleştirir."""
        candidates: List[Dict[str, Any]] = []
        seen_contents: Dict[str, int] = {}

        for doc in raw_docs:
            content = doc.page_content
            content_key = content[:200]
            sim_score = doc.metadata.get("similarity_score", 0.0)

            if content_key in seen_contents:
                idx = seen_contents[content_key]
                if sim_score > candidates[idx]["score"]:
                    candidates[idx]["score"] = sim_score
                continue

            seen_contents[content_key] = len(candidates)
            candidates.append(
                {
                    "content": content,
                    "source": doc.metadata.get("source", "bilinmiyor"),
                    "category": doc.metadata.get("category", "genel"),
                    "score": sim_score,
                    "metadata": dict(doc.metadata),
                }
            )

        return candidates

    def _search_collection_candidates(
        self,
        collection_name: str,
        expanded_query: str,
    ) -> List[Dict[str, Any]]:
        """Tek koleksiyonda aday belge araması yapar."""
        try:
            ensemble = self._ensure_ensemble(collection_name)
            raw_docs = ensemble.invoke(expanded_query)
        except Exception:
            logger.exception("ensemble_search_failed", query=expanded_query, collection=collection_name)
            return []

        return self._deduplicate_candidates(raw_docs)

    def search(
        self,
        query: str,
        top_k: int | None = None,
        department: Department | str | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Hibrit arama: Ön İşleme → BM25 + Vektör → RRF → Re-rank.

        Args:
            query: Kullanıcının sorusu.
            top_k: Döndürülecek sonuç sayısı.

        Returns:
            Re-rank edilmiş sonuç listesi.
        """
        start_time = time.perf_counter()
        k = top_k or self.k
        if department is not None:
            primary_departments, fallback_departments = _plan_search_departments(query, department)
            primary_collections = [collection_name_for_department(dep) for dep in primary_departments]
            fallback_collections = [collection_name_for_department(dep) for dep in fallback_departments]
        elif self.collection_name is not None:
            primary_collections = [self.collection_name]
            fallback_collections = []
        else:
            primary_departments, fallback_departments = _plan_search_departments(query, department)
            primary_collections = [collection_name_for_department(dep) for dep in primary_departments]
            fallback_collections = [collection_name_for_department(dep) for dep in fallback_departments]

        # 0. Cache kontrolü
        cache_key = f"{query}::{k}::{'|'.join(primary_collections)}::{'|'.join(fallback_collections)}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "hybrid_search_cache_hit",
                query=query,
                results_count=len(cached),
                elapsed_ms=round(elapsed_ms, 1),
            )
            return cached

        # 1. Sorgu on isleme (BM25 + Semantic arama icin)
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

        # 2. Önce birincil koleksiyonlarda ara
        candidates: List[Dict[str, Any]] = []
        for collection_name in primary_collections:
            candidates.extend(self._search_collection_candidates(collection_name, expanded_query))

        # 3. Sonuç yoksa kontrollü fallback
        if not candidates and fallback_collections:
            logger.info("hybrid_search_fallback", query=query, collections=fallback_collections)
            for collection_name in fallback_collections:
                candidates.extend(self._search_collection_candidates(collection_name, expanded_query))

        if not candidates:
            logger.warning("hybrid_search_no_candidates", query=query, collections=primary_collections)
            return []

        candidates = self._deduplicate_candidates(
            [Document(page_content=c["content"], metadata={**c["metadata"], "similarity_score": c["score"]}) for c in candidates]
        )

        # 4. Cross-encoder reranking (orijinal sorgu ile — model anlami kavrar)
        results = self.reranker.rerank(query, candidates, top_k=k)

        # 5. Kaynak uyumluluğu — off-topic sonuçları hafifçe aşağı it
        results = _apply_source_relevance(results, query)

        # 6. min_score filtresi
        if self.min_score > 0:
            results = [r for r in results if r["score"] >= self.min_score]

        # 7. Cache'e yaz
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

    def close(self) -> None:
        """Kaynaklari serbest birakir."""
        for indexer in self._indexers.values():
            indexer.close()
        self._indexers.clear()
        self._ensembles.clear()
        self._bm25_doc_counts.clear()


# ══════════════════════════════════════════════════════════════════════
# Geriye Uyumluluk API
# ══════════════════════════════════════════════════════════════════════

def build_hybrid_retriever(
    collection_name: str,
    k: int = 5,
    bm25_weight: float = 0.5,
    chroma_weight: float = 0.5,
) -> EnsembleRetriever:
    """
    Geriye uyumlu API. Yeni kod için HybridRetriever kullanın.

    Dahili olarak HybridRetriever oluşturur ve EnsembleRetriever'ını döndürür.
    """
    retriever = HybridRetriever(
        collection_name=collection_name,
        k=k,
        bm25_weight=bm25_weight,
        chroma_weight=chroma_weight,
    )
    return retriever._ensure_ensemble(collection_name)
