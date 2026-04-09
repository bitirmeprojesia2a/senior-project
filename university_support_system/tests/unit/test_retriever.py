"""
Retriever Unit Testleri

BM25 tokenizer, deduplication, source relevance ve HybridRetriever mantığını test eder.
Ağır bağımlılıklar (ChromaDB, Embedder, CrossEncoder) mock'lanır.
"""

from unittest.mock import MagicMock, patch, call

import pytest
from langchain_core.documents import Document

from src.core.constants import Department
from src.rag.candidate_utils import deduplicate_documents
from src.rag.retriever import (
    OFF_TOPIC_PENALTY,
    HybridRetriever,
    _QueryCache,
    _apply_source_relevance,
    _detect_query_topic,
    _plan_search_departments,
    _score_departments,
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


class TestDepartmentPlanningFallbacks:
    """Retriever fallback planlama testleri."""

    def test_plan_search_departments_without_signal(self):
        primary, fallback = _plan_search_departments("Merhaba bugün nasılsın?")
        assert primary == list(Department)
        assert fallback == []

    def test_plan_search_departments_with_close_scores(self):
        primary, fallback = _plan_search_departments("ÇAP ve yatay geçiş koşulları nelerdir?")
        assert Department.STUDENT_AFFAIRS in primary
        assert Department.ACADEMIC_PROGRAMS in primary
        assert fallback == []
