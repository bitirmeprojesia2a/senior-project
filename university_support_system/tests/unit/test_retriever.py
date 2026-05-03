"""
Retriever Unit Testleri

BM25 tokenizer, deduplication, source relevance ve HybridRetriever mantığını test eder.
Ağır bağımlılıklar (ChromaDB, Embedder, CrossEncoder) mock'lanır.
"""

import time
from unittest.mock import MagicMock, patch, call
from fnmatch import fnmatch

import pytest
from langchain_core.documents import Document

from src.core.config import settings
from src.core.constants import Department
from src.rag.candidate_utils import deduplicate_documents, sort_candidates_by_score
from src.rag.retriever import (
    OFF_TOPIC_PENALTY,
    HybridRetriever,
    _QueryCache,
    _extract_relevant_faq_block,
    _apply_source_relevance,
    _detect_query_topic,
    _plan_search_departments,
    _score_departments,
    turkish_bm25_preprocess,
)


class _FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    def get(self, key: str) -> str | None:
        return self.store.get(key)

    def set(self, key: str, value: str, ex: int | None = None) -> None:
        _ = ex
        self.store[key] = value

    def delete(self, *keys: str) -> None:
        for key in keys:
            self.store.pop(key, None)

    def scan(self, cursor: int = 0, match: str | None = None, count: int = 200):
        _ = count
        keys = [
            key
            for key in self.store
            if match is None or fnmatch(key, match)
        ]
        return 0, keys


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
        assert tokens[:3] == ["kayıt", "kayit", "dondurma"]
        assert "işlemi" in tokens
        assert "islemi" in tokens

    def test_ascii_variants_are_added_for_turkish_tokens(self):
        tokens = turkish_bm25_preprocess("ÇAP başvurusu")
        assert "çap" in tokens
        assert "cap" in tokens
        assert "başvuru" in tokens
        assert "basvuru" in tokens

    def test_possessive_suffixes_are_reduced_for_recall(self):
        tokens = turkish_bm25_preprocess("Sınav notuma nasıl itiraz ederim?")
        assert "not" in tokens
        assert "sinav" in tokens

    def test_ogrenci_not_stripped_to_ogren(self):
        """-ci eki kaldirildi; 'ogrenci' -> 'ogren' hatasi olmamali."""
        tokens = turkish_bm25_preprocess("öğrenci belgesi")
        assert "ogren" not in tokens
        assert "öğrenci" in tokens

    def test_devamsizlik_no_bogus_split(self):
        """Bilesik bolme 'devam sizlik' uretmemeli."""
        tokens = turkish_bm25_preprocess("devamsızlık sınırı")
        assert "sizlik" not in tokens
        assert "sızlık" not in tokens


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
        return deduplicate_documents(raw_docs)

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

    def test_dedup_keeps_same_filename_different_relative_path(self):
        docs = [
            Document(
                page_content="Ayni madde metni",
                metadata={
                    "source": "ortak.pdf",
                    "relative_path": "a/ortak.pdf",
                    "madde_no": "5",
                    "chunk_index": 1,
                },
            ),
            Document(
                page_content="Ayni madde metni",
                metadata={
                    "source": "ortak.pdf",
                    "relative_path": "b/ortak.pdf",
                    "madde_no": "5",
                    "chunk_index": 1,
                },
            ),
        ]

        results = self._run_dedup(docs)

        assert len(results) == 2

    def test_dedup_preserves_retrieval_rank_for_zero_score_candidates(self):
        docs = [
            Document(page_content="Ilk aday", metadata={}),
            Document(page_content="Ikinci aday", metadata={}),
        ]

        results = self._run_dedup(docs)

        assert results[0]["metadata"]["retrieval_rank"] == 0
        assert results[1]["metadata"]["retrieval_rank"] == 1

    def test_dedup_assigns_rank_fusion_score_to_bm25_only_candidates(self):
        docs = [
            Document(page_content="Tam kelime eslesen BM25 adayi", metadata={}),
            Document(page_content="Ikinci BM25 adayi", metadata={}),
        ]

        results = self._run_dedup(docs)

        assert results[0]["score"] > results[1]["score"] > 0
        assert results[0]["metadata"]["score_type"] == "rank_fusion"
        assert results[0]["metadata"]["retrieval_score"] == results[0]["score"]

    def test_sort_candidates_by_score_uses_retrieval_rank_as_tiebreaker(self):
        candidates = [
            {
                "source": "ikinci.txt",
                "content": "B",
                "score": 0.3,
                "metadata": {"retrieval_rank": 1},
            },
            {
                "source": "ilk.txt",
                "content": "A",
                "score": 0.3,
                "metadata": {"retrieval_rank": 0},
            },
        ]

        sorted_candidates = sort_candidates_by_score(candidates)

        assert [item["source"] for item in sorted_candidates] == ["ilk.txt", "ikinci.txt"]


def test_extract_relevant_faq_block_prefers_matching_question_for_grade_objection():
    content = (
        "Muafiyet talep ettiğim dersin notu en az ne olmadır?\n"
        "Bir dersten muaf olabilmesi için notunun en az CC ve üzeri olması gerekir.\n\n"
        "Sınav sonuçlarına nasıl itiraz edebilirim?\n"
        "Akademik takvimde belirtilen sınav not girişlerinin öğrenci otomasyon sistemine "
        "girilmesinin son gününden itibaren beş iş günü içerisinde ilgili birime "
        "(Bölüm Başkanlığına ) dilekçe vererek itiraz edebilirsiniz."
    )

    extracted = _extract_relevant_faq_block(
        content,
        "Sinav notuma itiraz etmek istiyorum. Basvuru sureci ve suresi nedir? beş iş günü bölüm başkanlığı",
    )

    lowered = extracted.lower()
    assert "sınav sonuçlarına nasıl itiraz edebilirim" in lowered
    assert "beş iş günü" in lowered

    def test_dedup_keeps_distinct_chunk_identities_with_same_content(self):
        docs = [
            Document(
                page_content="MADDE 5 - Basvuru kosullari",
                metadata={
                    "source": "yonerge.pdf",
                    "similarity_score": 0.51,
                    "chunk_index": 10,
                    "sub_chunk": "1/2",
                    "madde_no": "5",
                },
            ),
            Document(
                page_content="MADDE 5 - Basvuru kosullari",
                metadata={
                    "source": "yonerge.pdf",
                    "similarity_score": 0.73,
                    "chunk_index": 11,
                    "sub_chunk": "2/2",
                    "madde_no": "5",
                },
            ),
        ]

        results = self._run_dedup(docs)

        assert len(results) == 2

    def test_dedup_preserves_score_metadata(self):
        docs = [
            Document(
                page_content="AynÄ± iÃ§erik",
                metadata={"similarity_score": 0.42, "source": "cap.pdf"},
            ),
        ]

        results = deduplicate_documents(docs)

        assert results[0]["score"] == 0.42
        assert results[0]["metadata"]["score_type"] == "semantic_similarity"
        assert results[0]["metadata"]["retrieval_score"] == 0.42


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

    def test_put_stores_copy_of_input(self):
        cache = _QueryCache(ttl=300)
        data = [{"content": "test", "metadata": {"score": 0.9}}]

        cache.put("key1", data)
        data[0]["metadata"]["score"] = 0.1

        assert cache.get("key1")[0]["metadata"]["score"] == 0.9

    def test_get_returns_copy_of_cached_results(self):
        cache = _QueryCache(ttl=300)
        cache.put("key1", [{"content": "test", "metadata": {"score": 0.9}}])

        first_read = cache.get("key1")
        first_read[0]["metadata"]["score"] = 0.1

        second_read = cache.get("key1")
        assert second_read[0]["metadata"]["score"] == 0.9

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

    def test_disabled_cache_is_noop(self):
        cache = _QueryCache(ttl=300, enabled=False)
        cache.put("q1", [{"score": 0.9}])

        assert cache.get("q1") is None
        assert cache.size == 0

    def test_query_cache_restores_results_from_redis(self, monkeypatch):
        fake_redis = _FakeRedis()
        monkeypatch.setattr("src.cache.runtime_redis.get_runtime_redis", lambda: fake_redis)
        monkeypatch.setattr(settings.cache, "enabled", True)
        monkeypatch.setattr(settings.cache, "retriever_query_cache_enabled", True)
        monkeypatch.setattr(settings.cache, "redis_retriever_query_cache_enabled", True)
        monkeypatch.setattr(settings.redis, "enabled", True)

        writer = _QueryCache(ttl=300, enabled=True)
        reader = _QueryCache(ttl=300, enabled=True)

        writer.put("same-query", [{"content": "test", "score": 0.91}])

        restored = reader.get("same-query")

        assert restored == [{"content": "test", "score": 0.91}]
        assert reader.size == 1

    def test_query_cache_invalidate_clears_redis_namespace(self, monkeypatch):
        fake_redis = _FakeRedis()
        monkeypatch.setattr("src.cache.runtime_redis.get_runtime_redis", lambda: fake_redis)
        monkeypatch.setattr(settings.cache, "enabled", True)
        monkeypatch.setattr(settings.cache, "retriever_query_cache_enabled", True)
        monkeypatch.setattr(settings.cache, "redis_retriever_query_cache_enabled", True)
        monkeypatch.setattr(settings.redis, "enabled", True)

        cache = _QueryCache(ttl=300, enabled=True)
        cache.put("q1", [{"score": 0.9}])
        cache.put("q2", [{"score": 0.7}])

        assert _QueryCache.distributed_size() == 2

        cache.invalidate()

        assert _QueryCache.distributed_size() == 0
        assert cache.size == 0


class TestDepartmentPlanning:
    """Retriever departman planlama testleri."""

    def test_score_departments_finance_query(self):
        scores = _score_departments("Harç ödeme dekontumu nasıl alırım?")
        assert scores[Department.FINANCE] > 0
        assert scores[Department.FINANCE] >= scores[Department.STUDENT_AFFAIRS]

    def test_score_departments_academic_programs_query(self):
        scores = _score_departments("Müfredat ve ders planı nerede yayınlanır?")
        assert scores[Department.ACADEMIC_PROGRAMS] > 0

    def test_plan_search_departments_with_explicit_department(self):
        primary, fallback = _plan_search_departments("rastgele sorgu", Department.FINANCE)
        assert primary == [Department.FINANCE]
        assert fallback == []


class TestHybridRetrieverDepartmentSearch:
    """HybridRetriever koleksiyon planlama testleri."""

    @staticmethod
    def _make_candidate(source: str, score: float = 0.9) -> dict:
        return {
            "content": f"{source} icin test icerigi",
            "source": source,
            "category": "genel",
            "score": score,
            "metadata": {"source": source, "category": "genel"},
        }

    def _make_retriever(self) -> HybridRetriever:
        retriever = object.__new__(HybridRetriever)
        retriever.k = 5
        retriever.min_score = 0.0
        retriever.query_preprocessor = MagicMock()
        retriever.query_preprocessor.preprocess.side_effect = lambda query: query
        retriever.query_preprocessor.detect_query_type.return_value = "general"
        retriever.reranker = MagicMock()
        retriever.reranker.rerank.side_effect = lambda query, candidates, top_k: candidates[:top_k]
        retriever._cache = _QueryCache(ttl=300)
        retriever._BM25_DOCUMENT_CACHE = {}
        return retriever

    def test_search_uses_only_explicit_department_collection(self):
        retriever = self._make_retriever()
        retriever.collection_name = None
        retriever._search_collection_candidates = MagicMock(
            return_value=[self._make_candidate("harc_odeme_yonerge.pdf")]
        )

        results = HybridRetriever.search(
            retriever,
            "Harc borcumu nasil ogrenirim?",
            department=Department.FINANCE,
        )

        assert len(results) == 1
        assert retriever._search_collection_candidates.call_args_list == [
            call("finance_docs", "Harc borcumu nasil ogrenirim?")
        ]

    def test_search_uses_fallback_collections_when_primary_is_empty(self):
        retriever = self._make_retriever()
        retriever.collection_name = None
        retriever._search_collection_candidates = MagicMock(
            side_effect=[
                [],
                [],
                [self._make_candidate("harc_duyurusu.pdf")],
                [],
            ]
        )

        with patch(
            "src.rag.retriever._plan_search_departments",
            return_value=(
                [Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS],
                [Department.FINANCE],
            ),
        ):
            results = HybridRetriever.search(retriever, "Belirsiz bir sorgu")

        assert len(results) == 1
        assert retriever._search_collection_candidates.call_args_list == [
            call("student_affairs_docs", "Belirsiz bir sorgu"),
            call("academic_programs_docs", "Belirsiz bir sorgu"),
            call("finance_docs", "Belirsiz bir sorgu"),
        ]

    def test_search_cache_key_depends_on_department_plan(self):
        retriever = self._make_retriever()
        retriever.collection_name = None
        retriever._search_collection_candidates = MagicMock(
            side_effect=[
                [self._make_candidate("finans_kaynak.pdf")],
                [self._make_candidate("akademik_program.pdf")],
            ]
        )

        finance_results = HybridRetriever.search(
            retriever,
            "Ayni soru",
            department=Department.FINANCE,
        )
        academic_results = HybridRetriever.search(
            retriever,
            "Ayni soru",
            department=Department.ACADEMIC_PROGRAMS,
        )

        assert finance_results[0]["source"] == "finans_kaynak.pdf"
        assert academic_results[0]["source"] == "akademik_program.pdf"
        assert retriever._search_collection_candidates.call_args_list == [
            call("finance_docs", "Ayni soru"),
            call("academic_programs_docs", "Ayni soru"),
        ]

    def test_search_uses_explicit_constructor_collection(self):
        retriever = self._make_retriever()
        retriever.collection_name = "academic_programs_docs"
        retriever._search_collection_candidates = MagicMock(
            return_value=[self._make_candidate("mufredat_belgesi.pdf")]
        )

        results = HybridRetriever.search(retriever, "Rastgele bir soru")

        assert len(results) == 1
        assert retriever._search_collection_candidates.call_args_list == [
            call("academic_programs_docs", "Rastgele bir soru")
        ]

    def test_enrich_results_merges_adjacent_sub_chunks_for_same_madde(self):
        retriever = self._make_retriever()
        retriever.collection_name = None
        retriever._BM25_DOCUMENT_CACHE["academic_programs_docs"] = [
            Document(
                page_content="MADDE 5 - CAP basvuru kosullari.\nBASLANGIC-ORTAK gecis kosullari ve ilk sartlar.",
                metadata={
                    "source": "yonerge_cift_anadal_yandal.pdf",
                    "department": "academic_programs",
                    "madde_no": "5",
                    "sub_chunk": "1/3",
                    "chunk_index": 10,
                },
            ),
            Document(
                page_content=(
                    "[MADDE 5 - CAP basvuru kosullari.]\n"
                    "BASLANGIC-ORTAK gecis kosullari ve ilk sartlar. ORTA-ORTAK "
                    "basvuru tarihleri ve not ortalamasi."
                ),
                metadata={
                    "source": "yonerge_cift_anadal_yandal.pdf",
                    "department": "academic_programs",
                    "madde_no": "5",
                    "sub_chunk": "2/3",
                    "chunk_index": 11,
                },
            ),
            Document(
                page_content=(
                    "[MADDE 5 - CAP basvuru kosullari.]\n"
                    "ORTA-ORTAK basvuru tarihleri ve not ortalamasi. SON-TAMAM "
                    "hak kazanan ogrenciler ilan edilir."
                ),
                metadata={
                    "source": "yonerge_cift_anadal_yandal.pdf",
                    "department": "academic_programs",
                    "madde_no": "5",
                    "sub_chunk": "3/3",
                    "chunk_index": 12,
                },
            ),
        ]

        enriched = HybridRetriever.enrich_results(
            retriever,
            [
                {
                    "content": "[MADDE 5 - CAP basvuru kosullari.]\nBASLANGIC-ORTAK gecis kosullari ve ilk sartlar. ORTA-ORTAK basvuru tarihleri ve not ortalamasi.",
                    "source": "yonerge_cift_anadal_yandal.pdf",
                    "score": 0.84,
                    "metadata": {
                        "source": "yonerge_cift_anadal_yandal.pdf",
                        "department": "academic_programs",
                        "madde_no": "5",
                        "sub_chunk": "2/3",
                        "chunk_index": 11,
                    },
                }
            ],
            department=Department.ACADEMIC_PROGRAMS,
        )

        assert len(enriched) == 1
        assert "BASLANGIC-ORTAK" in enriched[0]["content"]
        assert "SON-TAMAM" in enriched[0]["content"]
        assert enriched[0]["content"].count("MADDE 5 - CAP basvuru kosullari.") == 1
        assert enriched[0]["metadata"]["context_expanded"] is True
        assert enriched[0]["metadata"]["merged_chunk_count"] == 3

    def test_enrich_results_uses_relative_path_for_same_filename(self):
        retriever = self._make_retriever()
        retriever.collection_name = None
        retriever._BM25_DOCUMENT_CACHE["academic_programs_docs"] = [
            Document(
                page_content="A klasoru ilk parca.",
                metadata={
                    "source": "ortak.pdf",
                    "relative_path": "a/ortak.pdf",
                    "department": "academic_programs",
                    "madde_no": "5",
                    "sub_chunk": "1/2",
                    "chunk_index": 1,
                },
            ),
            Document(
                page_content="A klasoru ikinci parca.",
                metadata={
                    "source": "ortak.pdf",
                    "relative_path": "a/ortak.pdf",
                    "department": "academic_programs",
                    "madde_no": "5",
                    "sub_chunk": "2/2",
                    "chunk_index": 2,
                },
            ),
            Document(
                page_content="B klasoru ilk parca.",
                metadata={
                    "source": "ortak.pdf",
                    "relative_path": "b/ortak.pdf",
                    "department": "academic_programs",
                    "madde_no": "5",
                    "sub_chunk": "1/2",
                    "chunk_index": 1,
                },
            ),
            Document(
                page_content="B klasoru ikinci parca.",
                metadata={
                    "source": "ortak.pdf",
                    "relative_path": "b/ortak.pdf",
                    "department": "academic_programs",
                    "madde_no": "5",
                    "sub_chunk": "2/2",
                    "chunk_index": 2,
                },
            ),
        ]

        enriched = HybridRetriever.enrich_results(
            retriever,
            [
                {
                    "content": "B klasoru ilk parca.",
                    "source": "ortak.pdf",
                    "score": 0.8,
                    "metadata": {
                        "source": "ortak.pdf",
                        "relative_path": "b/ortak.pdf",
                        "department": "academic_programs",
                        "madde_no": "5",
                        "sub_chunk": "1/2",
                        "chunk_index": 1,
                    },
                }
            ],
            department=Department.ACADEMIC_PROGRAMS,
        )

        assert len(enriched) == 1
        assert "B klasoru ilk parca" in enriched[0]["content"]
        assert "B klasoru ikinci parca" in enriched[0]["content"]
        assert "A klasoru" not in enriched[0]["content"]
        assert enriched[0]["metadata"]["merged_chunk_count"] == 2

    def test_enrich_results_deduplicates_repeated_expanded_rows(self):
        retriever = self._make_retriever()
        retriever.collection_name = None
        retriever._BM25_DOCUMENT_CACHE["academic_programs_docs"] = [
            Document(
                page_content="MADDE 5 - CAP basvuru kosullari.\nIlk parca.",
                metadata={
                    "source": "yonerge_cift_anadal_yandal.pdf",
                    "department": "academic_programs",
                    "madde_no": "5",
                    "sub_chunk": "1/2",
                    "chunk_index": 1,
                },
            ),
            Document(
                page_content="[MADDE 5 - CAP basvuru kosullari.]\nIlk parca. Ikinci parca.",
                metadata={
                    "source": "yonerge_cift_anadal_yandal.pdf",
                    "department": "academic_programs",
                    "madde_no": "5",
                    "sub_chunk": "2/2",
                    "chunk_index": 2,
                },
            ),
        ]

        enriched = HybridRetriever.enrich_results(
            retriever,
            [
                {
                    "content": "MADDE 5 - CAP basvuru kosullari.\nIlk parca.",
                    "source": "yonerge_cift_anadal_yandal.pdf",
                    "score": 0.42,
                    "metadata": {
                        "source": "yonerge_cift_anadal_yandal.pdf",
                        "department": "academic_programs",
                        "madde_no": "5",
                        "sub_chunk": "1/2",
                        "chunk_index": 1,
                    },
                },
                {
                    "content": "[MADDE 5 - CAP basvuru kosullari.]\nIlk parca. Ikinci parca.",
                    "source": "yonerge_cift_anadal_yandal.pdf",
                    "score": 0.84,
                    "metadata": {
                        "source": "yonerge_cift_anadal_yandal.pdf",
                        "department": "academic_programs",
                        "madde_no": "5",
                        "sub_chunk": "2/2",
                        "chunk_index": 2,
                    },
                },
            ],
            department=Department.ACADEMIC_PROGRAMS,
        )

        assert len(enriched) == 1
        assert enriched[0]["score"] == 0.84

    def test_search_does_not_reuse_query_cache_when_disabled(self, monkeypatch):
        retriever = self._make_retriever()
        retriever.collection_name = "finance_docs"
        retriever._search_collection_candidates = MagicMock(
            side_effect=[
                [self._make_candidate("ilk_sonuc.pdf")],
                [self._make_candidate("ikinci_sonuc.pdf")],
            ]
        )
        monkeypatch.setattr(settings.cache, "enabled", True)
        monkeypatch.setattr(settings.cache, "retriever_query_cache_enabled", False)
        retriever._cache = _QueryCache(ttl=300, enabled=False)

        first = HybridRetriever.search(retriever, "Ayni soru")
        second = HybridRetriever.search(retriever, "Ayni soru")

        assert first[0]["source"] == "ilk_sonuc.pdf"
        assert second[0]["source"] == "ikinci_sonuc.pdf"
        assert retriever._search_collection_candidates.call_count == 2


class TestHybridRetrieverScoreThresholds:
    """Score-type bazli final filtreleme davranisini korur."""

    def test_finalize_results_uses_stricter_threshold_for_reranker_scores(self):
        retriever = object.__new__(HybridRetriever)
        retriever.min_score = 0.05
        retriever._cache = _QueryCache(ttl=300)

        finalized = HybridRetriever._finalize_results(
            retriever,
            query="merhaba dunya",
            query_type="general",
            results=[
                {
                    "content": "Retrieval ile bulunan kabul edilebilir sonuc",
                    "source": "retrieval.pdf",
                    "score": 0.06,
                    "metadata": {"score_type": "retrieval"},
                },
                {
                    "content": "Reranker skoru esik altinda sonuc",
                    "source": "weak_reranker.pdf",
                    "score": 0.22,
                    "metadata": {"score_type": "reranker"},
                },
                {
                    "content": "Reranker skoru kabul edilebilir sonuc",
                    "source": "strong_reranker.pdf",
                    "score": 0.24,
                    "metadata": {"score_type": "reranker"},
                },
            ],
            cache_key="threshold-test",
            start_time=time.perf_counter(),
        )

        assert [item["source"] for item in finalized] == [
            "retrieval.pdf",
            "strong_reranker.pdf",
        ]


class TestDepartmentPlanningFallbacks:
    """Retriever fallback planlama testleri."""

    def test_plan_search_departments_without_signal(self):
        primary, fallback = _plan_search_departments("Merhaba bugün nasılsın?")
        assert primary == [Department.STUDENT_AFFAIRS]
        assert fallback == [Department.ACADEMIC_PROGRAMS, Department.FINANCE]

    def test_plan_search_departments_with_close_scores(self):
        primary, fallback = _plan_search_departments("ÇAP ve yatay geçiş koşulları nelerdir?")
        assert Department.STUDENT_AFFAIRS in primary
        assert Department.ACADEMIC_PROGRAMS in primary
        assert fallback == []
