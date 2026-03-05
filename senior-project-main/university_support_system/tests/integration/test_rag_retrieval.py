"""
RAG Retrieval Integration Testleri

ChromaDB'nin çalışıyor ve indekslenmiş olması gerekir.
Gerçek embedding modeli ve cross-encoder kullanılır.

Çalıştırma:
    python -m pytest tests/integration/ -v --tb=short
    python -m pytest tests/integration/ -v -m integration
"""

import time

import pytest

from tests.integration.conftest import chromadb_available, collection_has_data


@chromadb_available
class TestChromaDBConnectivity:
    """ChromaDB bağlantı testleri."""

    def test_heartbeat(self):
        import httpx

        r = httpx.get("http://localhost:8100/api/v1/heartbeat", timeout=5.0)
        assert r.status_code == 200

    def test_collections_endpoint(self):
        import httpx

        r = httpx.get("http://localhost:8100/api/v1/collections", timeout=5.0)
        assert r.status_code == 200
        assert isinstance(r.json(), list)


@chromadb_available
@collection_has_data
class TestCollectionState:
    """Koleksiyon durum testleri."""

    def test_collection_exists(self):
        from src.rag.indexer import ChromaIndexer

        indexer = ChromaIndexer()
        try:
            count = indexer.count()
            assert count > 0, "Koleksiyon boş"
        finally:
            indexer.close()

    def test_collection_has_expected_count(self):
        from src.rag.indexer import ChromaIndexer

        indexer = ChromaIndexer()
        try:
            count = indexer.count()
            assert count > 100, f"Beklenen: >100 chunk, Bulunan: {count}"
        finally:
            indexer.close()

    def test_documents_have_metadata(self):
        from src.rag.indexer import ChromaIndexer

        indexer = ChromaIndexer()
        try:
            data = indexer.get_all()
            assert data.get("metadatas"), "Metadata bulunamadı"
            first_meta = data["metadatas"][0]
            assert "source" in first_meta, "source metadata alanı eksik"
        finally:
            indexer.close()


@chromadb_available
@collection_has_data
class TestSemanticSearch:
    """Doğrudan ChromaDB semantik arama testleri."""

    def test_query_returns_results(self):
        from src.rag.embedder import Embedder
        from src.rag.indexer import ChromaIndexer

        embedder = Embedder()
        indexer = ChromaIndexer()
        try:
            query_vec = embedder.embed_single("ÇAP başvurusu", is_query=True)
            results = indexer.query(query_vec, n_results=5)
            assert results.get("documents")
            assert len(results["documents"][0]) > 0
        finally:
            indexer.close()

    def test_query_returns_distances(self):
        from src.rag.embedder import Embedder
        from src.rag.indexer import ChromaIndexer

        embedder = Embedder()
        indexer = ChromaIndexer()
        try:
            query_vec = embedder.embed_single("kayıt dondurma", is_query=True)
            results = indexer.query(query_vec, n_results=3)
            assert results.get("distances")
            distances = results["distances"][0]
            assert all(isinstance(d, float) for d in distances)
        finally:
            indexer.close()


@chromadb_available
@collection_has_data
class TestHybridSearch:
    """Tam hibrit arama pipeline testleri (BM25 + Semantic + Cross-Encoder)."""

    def test_search_returns_results(self, hybrid_retriever):
        results = hybrid_retriever.search("ÇAP başvurusu için gereken not ortalaması")
        assert len(results) > 0

    def test_results_have_required_fields(self, hybrid_retriever):
        results = hybrid_retriever.search("kayıt dondurma süresi")
        assert len(results) > 0
        for r in results:
            assert "content" in r
            assert "source" in r
            assert "score" in r
            assert isinstance(r["score"], (int, float))

    def test_results_sorted_by_score(self, hybrid_retriever):
        results = hybrid_retriever.search("yatay geçiş şartları")
        if len(results) > 1:
            scores = [r["score"] for r in results]
            assert scores == sorted(scores, reverse=True)

    def test_cap_query_returns_cap_source(self, hybrid_retriever):
        results = hybrid_retriever.search("Çift ana dal programına başvuru şartları")
        assert len(results) > 0
        sources = [r["source"].lower() for r in results[:3]]
        assert any(
            "cift" in s or "çift" in s or "anadal" in s or "çap" in s
            for s in sources
        ), f"ÇAP kaynağı top-3'te bulunamadı: {sources}"

    def test_yatay_gecis_query(self, hybrid_retriever):
        results = hybrid_retriever.search("Yatay geçiş için gerekli belgeler")
        assert len(results) > 0
        sources = [r["source"].lower() for r in results[:3]]
        assert any(
            "yatay" in s or "gecis" in s or "geçiş" in s
            for s in sources
        ), f"Yatay geçiş kaynağı top-3'te bulunamadı: {sources}"

    def test_top_k_parameter(self, hybrid_retriever):
        results_3 = hybrid_retriever.search("staj süresi", top_k=3)
        results_5 = hybrid_retriever.search("staj süresi", top_k=5)
        assert len(results_3) <= 3
        assert len(results_5) <= 5

    def test_performance_under_threshold(self, hybrid_retriever):
        """İlk çağrı model yükleme nedeniyle yavaş olabilir, ikinci çağrıyı ölç."""
        hybrid_retriever.search("ısınma sorgusu")

        start = time.perf_counter()
        hybrid_retriever.search("sınav itiraz süresi")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert elapsed_ms < 40000, f"Arama {elapsed_ms:.0f}ms sürdü (>40s)"


@chromadb_available
@collection_has_data
class TestQueryCache:
    """Sorgu cache testleri (gerçek arama ile)."""

    def test_cache_hit_faster(self):
        from src.rag.retriever import HybridRetriever

        retriever = HybridRetriever(cache_ttl=60)
        try:
            start1 = time.perf_counter()
            retriever.search("cache test sorgusu")
            first_ms = (time.perf_counter() - start1) * 1000

            start2 = time.perf_counter()
            retriever.search("cache test sorgusu")
            second_ms = (time.perf_counter() - start2) * 1000

            assert second_ms < first_ms, (
                f"Cache hit ({second_ms:.0f}ms) ilk aramadan ({first_ms:.0f}ms) yavaş"
            )
        finally:
            retriever.close()

    def test_cache_returns_same_results(self):
        from src.rag.retriever import HybridRetriever

        retriever = HybridRetriever(cache_ttl=60)
        try:
            results1 = retriever.search("cache tutarlılık testi")
            results2 = retriever.search("cache tutarlılık testi")

            assert len(results1) == len(results2)
            for r1, r2 in zip(results1, results2):
                assert r1["source"] == r2["source"]
                assert r1["score"] == r2["score"]
        finally:
            retriever.close()


@chromadb_available
@collection_has_data
class TestTestQuestions:
    """Test soruları dosyasıyla tam değerlendirme."""

    def test_at_least_70_percent_precision_at_3(self, hybrid_retriever, test_questions):
        """Precision@3 en az %70 olmalı."""
        correct = 0
        total = len(test_questions)

        for q in test_questions:
            results = hybrid_retriever.search(q["question"], top_k=5)
            sources = [r["source"].lower() for r in results[:3]]
            if any(
                any(p.lower() in s for p in q["expected_source_patterns"])
                for s in sources
            ):
                correct += 1

        precision = correct / total if total > 0 else 0
        assert precision >= 0.70, (
            f"Precision@3 = {precision:.1%} (hedef: ≥70%, "
            f"{correct}/{total} doğru)"
        )
