"""Response post-processing tests."""

from src.core.constants import Department
from src.db.schemas import DepartmentResponse, RAGSource
from src.orchestrators.response_utils import (
    clean_final_answer,
    compose_department_answers,
    filter_low_confidence_responses,
)


def test_clean_final_answer_removes_foreign_headings_and_english_lines():
    answer = (
        "Sonuc: Kayit yenileme ucreti doneme gore degisebilir.\n"
        "If the registration is canceled after renewal, the semester fee will not be refunded.\n"
        "Kanitlar:\n"
        "Staj defterini teslim etme suresiå…³äº bu konuda net bilgi bulunamadi."
    )

    cleaned = clean_final_answer(answer)

    assert "Sonuc:" not in cleaned
    assert "Kanitlar:" not in cleaned
    assert "registration is canceled" not in cleaned
    assert "å…³äº" not in cleaned
    assert "Staj defterini teslim etme suresi" in cleaned


def test_clean_final_answer_replaces_common_foreign_words_inline():
    answer = (
        "Kosullar following gibidir.\n"
        "Yaz okulu hakkinda informatie verir misin?\n"
        "Staj basvuru belgelerini several kaynaklardan alabilirsiniz.\n"
        "AKTS kredileri toplamı certain bir miktarda artirilabilir."
    )

    cleaned = clean_final_answer(answer)

    assert "following" not in cleaned
    assert "informatie" not in cleaned
    assert "several" not in cleaned
    assert "certain" not in cleaned
    assert "su sekild" in cleaned
    assert "bilgi" in cleaned
    assert "birden fazla kaynaktan" in cleaned
    assert "belirli bir miktarda" in cleaned


def test_clean_final_answer_replaces_english_word_with_turkish_suffix():
    answer = "Stajı yapıp successini kanıtlayamadığınız sürece mezun olamazsınız."

    cleaned = clean_final_answer(answer)

    assert "success" not in cleaned.lower()
    assert "basarisini" in cleaned.lower()


def test_clean_final_answer_replaces_additional_foreign_leaks():
    answer = (
        "Ayrintili bilgi icin siguientes maddelere bakin.\n"
        "Erasmus basvurusu icin once_online form doldurulur.\n"
        "Por favor belgeleri zamaninda teslim edin."
    )

    cleaned = clean_final_answer(answer)

    assert "siguientes" not in cleaned
    assert "once_online" not in cleaned
    assert "por favor" not in cleaned.lower()
    assert "asagidaki" in cleaned
    assert "once online" in cleaned
    assert "lutfen" in cleaned.lower()


def test_clean_final_answer_replaces_mixed_spanish_leaks():
    answer = "Not cizelgesi ve dilekce ile basvuru yapmaniz da necessario podria."

    cleaned = clean_final_answer(answer)

    assert "necessario" not in cleaned
    assert "podria" not in cleaned
    assert "gerekli" in cleaned


def test_clean_final_answer_removes_benchmark_and_prompt_like_prefixes():
    answer = (
        "Benchmark, Soru:\n"
        "Kayit dondurduktan sonra donuste ders secimi nasil yapilir?\n\n"
        "Yanit:\n"
        "Devam zorunlulugunuz degmez. Ders secimi akademik takvimde yapilir.\n"
        "Kaynak Bilgisi:\n"
        "yonetmelik.pdf"
    )

    cleaned = clean_final_answer(answer)

    assert "Benchmark" not in cleaned
    assert "Soru:" not in cleaned
    assert "Yanit:" not in cleaned
    assert "Kaynak Bilgisi" not in cleaned
    assert "devam zorunlulugunuz degismez" in cleaned.lower()


def test_clean_final_answer_normalizes_unicode_diacritic_leaks():
    answer = "Yatay geÃ§iÅŸ iÃ§in not ortalamasÄ±, Ã¼niversitenin kullandÄ±ÄŸÄ± há»‡ thá»‘nge gÃ¶re deÄŸiÅŸmektedir."

    cleaned = clean_final_answer(answer)

    assert "há»‡" not in cleaned
    assert "thá»‘nge" not in cleaned
    assert "not ortalamas" in cleaned.lower()


def test_filter_low_confidence_responses_keeps_only_announcement_when_other_answers_are_no_info():
    announcement = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Ilgili duyurular:\n1. Ara Sinav Programi\n   Detay: https://omu.edu.tr/duyuru/ara-sinav",
        sources=[
            RAGSource(
                content="Ara Sinav Programi",
                score=1.0,
                metadata={"record_type": "announcement", "title": "Ara Sinav Programi"},
            )
        ],
        generation_mode="vt",
    )
    rag_no_info = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi.",
        sources=[
            RAGSource(
                content="zayif kaynak",
                score=0.91,
                metadata={"score_type": "reranker"},
            )
        ],
        generation_mode="rag",
    )

    filtered = filter_low_confidence_responses([rag_no_info, announcement])

    assert filtered == [announcement]


def test_filter_low_confidence_responses_drops_announcement_when_strong_answer_exists():
    announcement = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Ilgili duyurular:\n1. Ara Sinav Programi\n   Detay: https://omu.edu.tr/duyuru/ara-sinav",
        sources=[
            RAGSource(
                content="Ara Sinav Programi",
                score=1.0,
                metadata={"record_type": "announcement", "title": "Ara Sinav Programi"},
            )
        ],
        generation_mode="vt",
    )
    strong_answer = DepartmentResponse(
        department=Department.ACADEMIC_PROGRAMS,
        answer="Muafiyet sonucu cikana kadar derslere devam etmeniz gerekir.",
        sources=[
            RAGSource(
                content="Muafiyet komisyon karari cikana kadar derslere devam edilir.",
                score=0.91,
                metadata={"score_type": "reranker"},
            )
        ],
        generation_mode="rag",
    )

    filtered = filter_low_confidence_responses([strong_answer, announcement])

    assert filtered == [strong_answer]


def test_compose_department_answers_prefers_announcement_when_other_answer_is_no_info():
    announcement = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Ilgili duyurular:\n1. Ara Sinav Programi\n   Detay: https://omu.edu.tr/duyuru/ara-sinav",
        sources=[
            RAGSource(
                content="Ara Sinav Programi",
                score=1.0,
                metadata={"record_type": "announcement", "title": "Ara Sinav Programi"},
            )
        ],
        generation_mode="vt",
    )
    rag_no_info = DepartmentResponse(
        department=Department.ACADEMIC_PROGRAMS,
        answer="Bu konuda elimdeki kaynaklarda net bilgi bulunamadi.",
        sources=[
            RAGSource(
                content="kaynak",
                score=0.88,
                metadata={"score_type": "reranker"},
            )
        ],
        generation_mode="rag",
    )

    composed = compose_department_answers([rag_no_info, announcement])

    assert composed.startswith("Ilgili duyurular:")


def test_clean_final_answer_deduplicates_repeated_sentences():
    answer = (
        "Kayit dondurma basvurusu akademik takvimde yapilir.\n"
        "Ogrenci isleri mudurlugu bilgi verir.\n"
        "Kayit dondurma basvurusu akademik takvimde yapilir.\n"
        "Detayli bilgi icin birimlere basvurabilirsiniz."
    )

    cleaned = clean_final_answer(answer)

    count = cleaned.lower().count("akademik takvimde yapilir")
    assert count == 1, f"Duplicate should be removed, found {count} occurrences"
    assert "Detayli bilgi" in cleaned


def test_clean_final_answer_removes_empty_markdown_headings():
    answer = (
        "### \n"
        "Kayit yenileme ucreti doneme gore degisebilir.\n"
        "## \n"
        "Daha fazla bilgi icin birime basvurunuz."
    )

    cleaned = clean_final_answer(answer)

    assert "###" not in cleaned.strip()
    assert "##" not in cleaned.strip()
    assert "Kayit yenileme" in cleaned


def test_clean_final_answer_removes_internal_no_sentence_leak():
    answer = "Final sinavlari hakkinda cumle bulunamadi. Ogrenci Isleri'ne yonlendir."

    cleaned = clean_final_answer(answer)

    assert "cumle bulunamadi" not in cleaned
    assert "yonlendir" not in cleaned
    assert "net bilgi bulunamadi" in cleaned


def test_clean_final_answer_drops_dangling_last_clause():
    answer = (
        "Ders kaydi akademik takvimde yapilir. "
        "Ogrenciler once alt donem derslerini alir. "
        "Ayrica GANO'su 1,80-2,49 arasi olan ogrenciler icin"
    )

    cleaned = clean_final_answer(answer)

    assert cleaned.endswith("Ogrenciler once alt donem derslerini alir.")
    assert "1,80-2,49" not in cleaned


def test_clean_final_answer_drops_dangling_last_clause_with_turkish_chars():
    answer = (
        "Ders kaydı akademik takvimde yapılır. "
        "Öğrenciler önce alt dönem derslerini alır. "
        "Ayrıca GANO'su 1,80-2,49 arası olan öğrenciler için"
    )

    cleaned = clean_final_answer(answer)

    assert cleaned.endswith("Öğrenciler önce alt dönem derslerini alır.")
    assert "1,80-2,49" not in cleaned


def test_clean_final_answer_separates_joined_turkish_approval_phrase():
    answer = "Danisman onayıgereken durumlarda danisman onayi alinmalidir."

    cleaned = clean_final_answer(answer)

    assert "onayıgereken" not in cleaned
    assert "onayi gereken" in cleaned
