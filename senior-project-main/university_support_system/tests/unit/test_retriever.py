"""
Retriever Unit Testleri

BM25 tokenizer, deduplication, source relevance ve HybridRetriever mantığını test eder.
Ağır bağımlılıklar (ChromaDB, Embedder, CrossEncoder) mock'lanır.
"""

from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document

from src.rag.retriever import (
    OFF_TOPIC_PENALTY,
    _QueryCache,
    _apply_source_relevance,
    _detect_query_topic,
    turkish_bm25_preprocess,
)


# ═══════════════════════════════════════════════════
# turkish_bm25_preprocess Testleri
# ═══════════════════════════════════════════════════

class TestTurkishBm25Preprocess:
    """BM25 Türkçe tokenizer testleri."""

    def test_lowercase(self):
        tokens = turkish_bm25_preprocess("Merhaba DÜNYA")
        assert all(t == t.lower() for t in tokens)

    def test_compound_word_split(self):
        tokens = turkish_bm25_preprocess("anadal programı")
        assert "ana" in tokens
        assert "dal" in tokens

    def test_yandal_split(self):
        tokens = turkish_bm25_preprocess("yandal başvurusu")
        assert "yan" in tokens
        assert "dal" in tokens

    def test_punctuation_removed(self):
        tokens = turkish_bm25_preprocess("Kayıt, nasıl yapılır?")
        for t in tokens:
            assert "," not in t
            assert "?" not in t

    def test_single_char_tokens_removed(self):
        tokens = turkish_bm25_preprocess("A ve B arası")
        assert "a" not in tokens
        assert "b" not in tokens

    def test_empty_input(self):
        assert turkish_bm25_preprocess("") == []

    def test_whitespace_normalization(self):
        tokens = turkish_bm25_preprocess("kayıt   dondurma    işlemi")
        assert tokens == ["kayıt", "dondurma", "işlemi"]


# ═══════════════════════════════════════════════════
# _detect_query_topic Testleri
# ═══════════════════════════════════════════════════

class TestDetectQueryTopic:
    """Sorgu konu tespiti testleri."""

    def test_cap_detected(self):
        assert _detect_query_topic("ÇAP başvurusu nasıl yapılır") is not None
        topic = _detect_query_topic("çap not ortalaması")
        assert topic == "çap"

    def test_yatay_gecis_detected(self):
        topic = _detect_query_topic("yatay geçiş şartları")
        assert topic == "yatay geçiş"

    def test_staj_detected(self):
        topic = _detect_query_topic("staj süresi kaç gündür")
        assert topic == "staj"

    def test_yaz_okulu_detected(self):
        topic = _detect_query_topic("yaz okulu harç ücreti")
        assert topic == "yaz okulu"

    def test_longer_match_preferred(self):
        """'çift ana dal' 'çap'tan daha uzun, önce eşleşmeli."""
        topic = _detect_query_topic("çift ana dal not ortalaması")
        assert topic == "çift ana dal"

    def test_no_topic_detected(self):
        assert _detect_query_topic("merhaba dünya") is None

    def test_empty_query(self):
        assert _detect_query_topic("") is None


# ═══════════════════════════════════════════════════
# _apply_source_relevance Testleri
# ═══════════════════════════════════════════════════

class TestApplySourceRelevance:
    """Kaynak uyumluluğu penalty testleri."""

    def _make_result(self, source: str, score: float) -> dict:
        return {"source": source, "score": score, "content": "test"}

    def test_on_topic_not_penalized(self):
        results = [
            self._make_result("yonerge_cift_anadal_yandal.pdf", 0.9),
            self._make_result("ÇİFT ANA DAL PROGRAMI.pdf", 0.8),
        ]
        adjusted = _apply_source_relevance(results, "çap başvurusu")

        assert adjusted[0]["score"] == 0.9
        assert adjusted[1]["score"] == 0.8

    def test_off_topic_penalized(self):
        results = [
            self._make_result("yonerge_cift_anadal_yandal.pdf", 0.9),
            self._make_result("yonerge_yatay_gecis.pdf", 0.85),
        ]
        adjusted = _apply_source_relevance(results, "çap başvurusu")

        assert adjusted[0]["score"] == 0.9
        assert adjusted[1]["score"] == round(0.85 * OFF_TOPIC_PENALTY, 4)

    def test_resorted_after_penalty(self):
        results = [
            self._make_result("yonerge_yatay_gecis.pdf", 0.95),
            self._make_result("yonerge_cift_anadal_yandal.pdf", 0.80),
        ]
        adjusted = _apply_source_relevance(results, "çap başvurusu")

        assert adjusted[0]["source"] == "yonerge_cift_anadal_yandal.pdf"

    def test_no_topic_no_change(self):
        results = [
            self._make_result("any_file.pdf", 0.9),
            self._make_result("another.pdf", 0.7),
        ]
        adjusted = _apply_source_relevance(results, "merhaba dünya")

        assert adjusted[0]["score"] == 0.9
        assert adjusted[1]["score"] == 0.7

    def test_empty_results(self):
        assert _apply_source_relevance([], "çap başvurusu") == []

    def test_custom_penalty(self):
        results = [
            self._make_result("yonerge_yatay_gecis.pdf", 1.0),
        ]
        adjusted = _apply_source_relevance(results, "çap başvurusu", penalty=0.5)

        assert adjusted[0]["score"] == 0.5

    def test_yatay_gecis_topic(self):
        results = [
            self._make_result("yonerge_yatay_gecis.pdf", 0.9),
            self._make_result("yonerge_cift_anadal_yandal.pdf", 0.85),
        ]
        adjusted = _apply_source_relevance(results, "yatay geçiş şartları")

        assert adjusted[0]["score"] == 0.9
        assert adjusted[1]["score"] == round(0.85 * OFF_TOPIC_PENALTY, 4)


# ═══════════════════════════════════════════════════
# Deduplication Logic (Fonksiyonel Test)
# ═══════════════════════════════════════════════════

class TestDeduplicationLogic:
    """Retriever'daki dedup mantığını bağımsız test eder."""

    def _run_dedup(self, raw_docs):
        """Retriever'daki dedup mantığını simüle eder."""
        candidates = []
        seen_contents = {}

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
            candidates.append({
                "content": content,
                "source": doc.metadata.get("source", "bilinmiyor"),
                "score": sim_score,
            })

        return candidates

    def test_dedup_removes_duplicate(self):
        docs = [
            Document(page_content="Aynı içerik", metadata={"similarity_score": 0.0}),
            Document(page_content="Aynı içerik", metadata={"similarity_score": 0.8}),
        ]
        results = self._run_dedup(docs)
        assert len(results) == 1

    def test_dedup_keeps_max_score(self):
        docs = [
            Document(page_content="Aynı içerik", metadata={"similarity_score": 0.0}),
            Document(page_content="Aynı içerik", metadata={"similarity_score": 0.8}),
        ]
        results = self._run_dedup(docs)
        assert results[0]["score"] == 0.8

    def test_dedup_keeps_max_score_reverse_order(self):
        docs = [
            Document(page_content="Aynı içerik", metadata={"similarity_score": 0.8}),
            Document(page_content="Aynı içerik", metadata={"similarity_score": 0.0}),
        ]
        results = self._run_dedup(docs)
        assert results[0]["score"] == 0.8

    def test_dedup_different_content_kept(self):
        docs = [
            Document(page_content="İçerik A", metadata={"similarity_score": 0.7}),
            Document(page_content="İçerik B", metadata={"similarity_score": 0.6}),
        ]
        results = self._run_dedup(docs)
        assert len(results) == 2

    def test_dedup_empty_list(self):
        assert self._run_dedup([]) == []


# ═══════════════════════════════════════════════════
# _QueryCache Testleri
# ═══════════════════════════════════════════════════

class TestQueryCache:
    """In-memory sorgu cache testleri."""

    def test_put_and_get(self):
        cache = _QueryCache(ttl=300)
        data = [{"content": "test", "score": 0.9}]
        cache.put("key1", data)
        assert cache.get("key1") == data

    def test_miss_returns_none(self):
        cache = _QueryCache(ttl=300)
        assert cache.get("nonexistent") is None

    def test_expired_entry_returns_none(self):
        cache = _QueryCache(ttl=0)
        cache.put("key1", [{"content": "test"}])
        import time
        time.sleep(0.01)
        assert cache.get("key1") is None

    def test_invalidate_clears_all(self):
        cache = _QueryCache(ttl=300)
        cache.put("k1", [])
        cache.put("k2", [])
        assert cache.size == 2
        cache.invalidate()
        assert cache.size == 0

    def test_size_property(self):
        cache = _QueryCache(ttl=300)
        assert cache.size == 0
        cache.put("k1", [])
        assert cache.size == 1

    def test_different_keys_independent(self):
        cache = _QueryCache(ttl=300)
        cache.put("q1::5", [{"score": 0.9}])
        cache.put("q2::5", [{"score": 0.7}])
        assert cache.get("q1::5")[0]["score"] == 0.9
        assert cache.get("q2::5")[0]["score"] == 0.7
