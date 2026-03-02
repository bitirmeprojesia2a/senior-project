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

    retriever = HybridRetriever(collection_name="student_affairs_docs")
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


def _detect_query_topic(query: str) -> Optional[str]:
    """Sorgudaki ana konu anahtar kelimesini tespit eder."""
    q = query.lower()
    for topic in _TOPIC_KEYS_BY_LENGTH:
        if topic in q:
            return topic
    return None


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
        collection_name: str = "student_affairs_docs",
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
        self.indexer = ChromaIndexer(collection_name=collection_name)
        self.embedder = Embedder()
        self.reranker = CrossEncoderReranker()

        self._ensemble: Optional[EnsembleRetriever] = None
        self._bm25_doc_count = 0
        self._cache = _QueryCache(ttl=cache_ttl)

    def _ensure_ensemble(self) -> EnsembleRetriever:
        """Ensemble retriever'ı tembel (lazy) olarak başlatır."""
        if self._ensemble is not None:
            return self._ensemble

        logger.info("building_hybrid_retriever", collection=self.collection_name)

        internal_k = self.k * self.OVERSAMPLE_FACTOR

        # 1. Chroma Retriever (Semantic)
        chroma_retriever = ChromaRestRetriever(
            indexer=self.indexer, embedder=self.embedder, k=internal_k
        )

        # 2. BM25 hazırlık — page_content ORİJİNAL metin olmalı
        #    (compound split ve tokenizasyon preprocess_func icerisinde yapilir)
        #    Boylece EnsembleRetriever dedup'i dogru calisir cunku
        #    BM25 ve ChromaDB ayni page_content'e sahip olur.
        logger.info("fetching_data_for_bm25_index")
        all_data = self.indexer.get_all()

        documents: List[Document] = []
        if all_data.get("documents"):
            docs = all_data["documents"]
            metas = all_data.get("metadatas", [])
            for i, text in enumerate(docs):
                meta = metas[i] if metas and i < len(metas) else {}
                documents.append(
                    Document(page_content=text, metadata=meta)
                )

        self._bm25_doc_count = len(documents)

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
        self._ensemble = EnsembleRetriever(
            retrievers=[bm25_retriever, chroma_retriever],
            weights=[self.bm25_weight, self.chroma_weight],
        )

        logger.info(
            "hybrid_retriever_ready",
            bm25_docs=self._bm25_doc_count,
            bm25_weight=self.bm25_weight,
            chroma_weight=self.chroma_weight,
        )
        return self._ensemble

    def search(
        self,
        query: str,
        top_k: int | None = None,
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

        # 0. Cache kontrolü
        cache_key = f"{query}::{k}"
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
        )

        try:
            # 2. Ensemble ile oversampled arama
            ensemble = self._ensure_ensemble()
            raw_docs = ensemble.invoke(expanded_query)
        except Exception:
            logger.exception("ensemble_search_failed", query=query)
            return []

        # 3. Deduplicate — aynı belgenin BM25 ve ChromaDB versiyonlarında
        #    en yüksek similarity_score korunur (BM25'te 0.0, ChromaDB'de gerçek skor)
        candidates: List[Dict[str, Any]] = []
        seen_contents: Dict[str, int] = {}  # content_key → candidates index

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
        self.indexer.close()


# ══════════════════════════════════════════════════════════════════════
# Geriye Uyumluluk API
# ══════════════════════════════════════════════════════════════════════

def build_hybrid_retriever(
    collection_name: str = "student_affairs_docs",
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
    return retriever._ensure_ensemble()
