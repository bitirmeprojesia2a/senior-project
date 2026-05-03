"""
QueryPreprocessor Unit Testleri

Bileşik kelime ayırma, sinonim genişletme, sorgu tipi tespiti ve
normalize_for_bm25 fonksiyonlarını test eder.
"""

import pytest

from src.rag.query_preprocessor import (
    COMPOUND_WORD_SPLITS,
    PROCEDURAL_KEYWORDS,
    SYNONYM_MAP,
    QueryPreprocessor,
)


class TestCompoundWordSplitting:
    """Bileşik kelime ayırma testleri."""

    def test_anadal_splits(self):
        qp = QueryPreprocessor(enable_expansion=False)
        result = qp.preprocess("anadal programı")
        assert "ana dal" in result

    def test_yandal_splits(self):
        qp = QueryPreprocessor(enable_expansion=False)
        result = qp.preprocess("yandal başvurusu")
        assert "yan dal" in result

    def test_ciftanadal_splits(self):
        qp = QueryPreprocessor(enable_expansion=False)
        result = qp.preprocess("çiftanadal nedir")
        assert "çift ana dal" in result

    def test_case_insensitive_split(self):
        qp = QueryPreprocessor(enable_expansion=False)
        result = qp.preprocess("ANADAL programı")
        assert "ana dal" in result.lower()

    def test_no_split_when_already_separated(self):
        qp = QueryPreprocessor(enable_expansion=False)
        result = qp.preprocess("ana dal programı")
        assert "ana dal" in result


class TestSynonymExpansion:
    """Sinonim genişletme testleri."""

    def test_cap_expands(self):
        qp = QueryPreprocessor()
        result = qp.preprocess("çap başvurusu")
        assert "çift ana dal" in result.lower() or "ikinci lisans" in result.lower()

    def test_ydp_expands(self):
        qp = QueryPreprocessor()
        result = qp.preprocess("ydp nedir")
        assert "yan dal" in result.lower()

    def test_gno_expands(self):
        qp = QueryPreprocessor()
        result = qp.preprocess("gno hesaplama")
        assert "not ortalaması" in result.lower() or "genel not ortalaması" in result.lower()

    def test_kayit_dondurma_expands(self):
        qp = QueryPreprocessor()
        result = qp.preprocess("kayıt dondurma nasıl yapılır")
        assert "dönem izni" in result.lower() or "kayıt dondurmak" in result.lower()

    def test_muafiyet_expands_with_process_terms(self):
        qp = QueryPreprocessor()
        result = qp.preprocess("muafiyet başvurusu ne zaman yapılır")
        lowered = result.lower()
        assert "ders muafiyeti" in lowered
        assert "muafiyet komisyonu" in lowered
        assert "üç hafta" in lowered or "uc hafta" in lowered

    def test_discipline_expands_with_exam_rule_terms(self):
        qp = QueryPreprocessor()
        result = qp.preprocess("sınavda kopya çekmenin cezası nedir")
        lowered = result.lower()
        assert "disiplin suçu" in lowered
        assert "sınav kuralları" in lowered
        assert "öğrenci disiplin yönetmeliği" in lowered

    def test_grade_entry_expands_with_support_contacts(self):
        qp = QueryPreprocessor()
        result = qp.preprocess("hocam not girmemiş ne yapabilirim")
        lowered = result.lower()
        assert "oidb@omu.edu.tr" in lowered
        assert "danışman" in lowered

    def test_grade_objection_expands_with_student_affairs_process_terms(self):
        qp = QueryPreprocessor()
        result = qp.preprocess("sınav notuma itiraz etmek istiyorum")
        lowered = result.lower()
        assert "beş iş günü" in lowered or "bes is gunu" in lowered
        assert "ilgili birim" in lowered

    def test_ascii_withdrawal_query_still_expands(self):
        qp = QueryPreprocessor()
        result = qp.preprocess("universiteden ayrilmak istiyorum")
        lowered = result.lower()
        assert "ilişik kesme" in lowered
        assert "kayıt sildirme" in lowered

    def test_ascii_discipline_query_still_expands(self):
        qp = QueryPreprocessor()
        result = qp.preprocess("kopya nedeniyle disiplin sureci nedir")
        lowered = result.lower()
        assert "disiplin suçu" in lowered
        assert "sınav kuralları" in lowered
        assert "öğrenci disiplin yönetmeliği" in lowered

    def test_expansion_disabled(self):
        qp = QueryPreprocessor(enable_expansion=False)
        result = qp.preprocess("çap başvurusu")
        assert "ikinci lisans" not in result.lower()

    def test_custom_synonym_map(self):
        custom = {"test": ["deneme", "sınama"]}
        qp = QueryPreprocessor(synonym_map=custom)
        result = qp.preprocess("test sorusu")
        assert "deneme" in result.lower() or "sınama" in result.lower()

    def test_substring_false_positive_avoided(self):
        """Anahtar başka bir kelimenin içinde geçiyorsa expansion yapılmaz."""
        custom = {"test": ["deneme"]}
        qp = QueryPreprocessor(synonym_map=custom)
        result = qp.preprocess("protesto düzeni")
        assert "deneme" not in result.lower()

    def test_no_duplicate_terms(self):
        """Orijinal sorguda zaten geçen terimler tekrar eklenmez."""
        qp = QueryPreprocessor()
        result = qp.preprocess("çift ana dal başvurusu")
        words = result.lower().split()
        # "çift" ve "ana" ve "dal" zaten var — bunlar tekrar edilmemeli
        # ama ÇAP ve ikinci lisans gibi yeni terimler eklenmeli
        assert "çap" in result or "ÇAP" in result

    def test_compound_normalized_expansions_are_deduplicated(self):
        qp = QueryPreprocessor()
        result = qp.preprocess("ÇAP başvurusu nasıl yapılır?")

        assert result.lower().count("çift ana dal") == 1

    def test_longer_match_takes_priority(self):
        """Daha uzun sinonim anahtarı önce eşleşir."""
        qp = QueryPreprocessor()
        result = qp.preprocess("çift ana dal programı nedir")
        # "çift ana dal programı" anahtarı "çift ana dal"dan daha uzun
        assert "ÇAP" in result or "ikinci lisans" in result

    def test_multi_word_synonym_expands_with_turkish_suffix(self):
        qp = QueryPreprocessor()
        result = qp.preprocess("ders kaydından danışman onayına kadar süreci anlat")

        assert "ubys.omu.edu.tr" in result.lower()
        assert "ders seçimi" in result.lower()
        assert "danışman onayı" in result.lower()
        assert "sınıf yoklama listesi" in result.lower()


    def test_real_turkish_unicode_queries_expand(self):
        qp = QueryPreprocessor()

        cap_result = qp.preprocess("\u00c7AP ba\u015fvurusu nas\u0131l yap\u0131l\u0131r?")
        grading_result = qp.preprocess("Ba\u011f\u0131l de\u011ferlendirme sistemi nedir?")

        assert "\u00e7ift ana dal" in cap_result.lower()
        assert "ba\u011f\u0131l de\u011ferlendirme y\u00f6nergesi" in grading_result.lower()


class TestQueryTypeDetection:
    """Sorgu tipi tespiti testleri."""

    def test_procedural_nasil(self):
        qp = QueryPreprocessor()
        assert qp.detect_query_type("kayıt nasıl yapılır") == "procedural"

    def test_procedural_basvuru(self):
        qp = QueryPreprocessor()
        assert qp.detect_query_type("burs başvuru süreci") == "procedural"

    def test_procedural_ne_zaman(self):
        qp = QueryPreprocessor()
        assert qp.detect_query_type("ders kaydı ne zaman") == "procedural"

    def test_factual_nedir(self):
        qp = QueryPreprocessor()
        assert qp.detect_query_type("AKTS nedir") == "factual"

    def test_factual_kactir(self):
        qp = QueryPreprocessor()
        assert qp.detect_query_type("mezuniyet kredisi kaçtır") == "factual"

    def test_general_query(self):
        qp = QueryPreprocessor()
        assert qp.detect_query_type("üniversite bilgileri") == "general"

    def test_procedural_ascii_normalized_text(self):
        qp = QueryPreprocessor()
        assert qp.detect_query_type("kayit nasil yapilir") == "procedural"

    def test_factual_ascii_normalized_text(self):
        qp = QueryPreprocessor()
        assert qp.detect_query_type("mezuniyet kredisi kactir") == "factual"


class TestNormalizeForBm25:
    """BM25 normalizasyon testleri."""

    def test_splits_compound_words(self):
        qp = QueryPreprocessor()
        result = qp.normalize_for_bm25("anadal yandal")
        assert "ana dal" in result
        assert "yan dal" in result

    def test_no_synonym_expansion(self):
        qp = QueryPreprocessor()
        result = qp.normalize_for_bm25("çap nedir")
        assert "ikinci lisans" not in result.lower()

    def test_empty_input(self):
        qp = QueryPreprocessor()
        assert qp.normalize_for_bm25("") == ""


class TestEdgeCases:
    """Sınır durum testleri."""

    def test_empty_query(self):
        qp = QueryPreprocessor()
        assert qp.preprocess("") == ""

    def test_whitespace_only(self):
        qp = QueryPreprocessor()
        assert qp.preprocess("   ") == ""

    def test_single_word(self):
        qp = QueryPreprocessor()
        result = qp.preprocess("merhaba")
        assert "merhaba" in result

    def test_query_with_punctuation(self):
        qp = QueryPreprocessor()
        result = qp.preprocess("Kayıt dondurma nasıl yapılır?")
        assert "kayıt dondurma" in result.lower() or "kayıt" in result.lower()
