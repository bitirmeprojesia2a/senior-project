"""Response post-processing tests."""

from src.core.constants import Department
from src.core.text_normalization import normalize_text
from src.db.schemas import DepartmentResponse, RAGSource
from src.orchestrators.response_utils import (
    append_generation_summary,
    append_source_summary,
    clean_final_answer,
    compose_department_answers,
    filter_low_confidence_responses,
)
from src.quality.answer_filter import check_answer_quality, quality_issue_blocks_answer


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


def test_quality_filter_flags_foreign_bad_tokens_after_repair():
    result = check_answer_quality("Detayli bilgi icin duyurulari takip etmeniz necessaire.")

    assert result.needs_rewrite is True
    assert "necessaire" in [token.lower() for token in result.bad_tokens]


def test_quality_filter_flags_mixed_necessary_suffix():
    result = check_answer_quality("Bu kosullari saglamaniz necessarytir.")

    assert result.needs_rewrite is True
    assert "necessarytir" in [token.lower() for token in result.bad_tokens]


def test_quality_filter_flags_portuguese_following_leak():
    result = check_answer_quality("Basvuru sureci seguintek sekilde isler.")

    assert result.needs_rewrite is True
    assert "seguintek" in [token.lower() for token in result.bad_tokens]
    assert quality_issue_blocks_answer(result) is True


def test_quality_filter_flags_portuguese_following_with_turkish_suffix():
    result = check_answer_quality("Yaz okulu katilimcilari icin gerekli sartlar siguientesintilar.")

    assert result.needs_rewrite is True
    assert "siguientesintilar" in [token.lower() for token in result.bad_tokens]
    assert quality_issue_blocks_answer(result) is True


def test_quality_filter_does_not_block_minor_language_issue():
    result = check_answer_quality(
        "Basvuru sureci specifically ve additionally duyurularda aciklanir."
    )

    assert result.needs_rewrite is True
    assert result.has_suspicious_english is True
    assert quality_issue_blocks_answer(result) is False


def test_append_generation_summary_shows_global_llm_synthesis():
    response = DepartmentResponse(
        department=Department.ACADEMIC_PROGRAMS,
        answer="Kaynakli ara cevap",
        sources=[RAGSource(content="kaynak", score=0.9)],
        generation_mode="rag",
    )

    answer = append_generation_summary(
        "Final cevap",
        [response],
        used_global_synthesis=True,
    )

    assert "- Final Sentez: LLM" in answer
    assert "- RAG" in answer


def test_append_generation_summary_explains_parallel_agent_flow():
    responses = [
        DepartmentResponse(
            department=Department.STUDENT_AFFAIRS,
            answer="Ogrenci isleri cevabi",
            generation_mode="rag",
        ),
        DepartmentResponse(
            department=Department.ACADEMIC_PROGRAMS,
            answer="Akademik cevap",
            generation_mode="vt",
        ),
    ]

    answer = append_generation_summary(
        "Final cevap",
        responses,
        used_global_synthesis=True,
        routing_strategy="parallel",
        agents_involved=["student_affairs", "academic_programs", "orchestrator"],
    )

    assert "- Çalışma biçimi: Paralel" in answer
    assert "- Ajan akışı: Paralel: Öğrenci İşleri + Akademik Programlar; Son: Orkestratör" in answer
    assert "- Pipeline:" not in answer
    assert "- Routing:" not in answer


def test_append_generation_summary_displays_specialist_agents_in_flow():
    responses = [
        DepartmentResponse(
            department=Department.STUDENT_AFFAIRS,
            answer="Kayit cevabi",
            generation_mode="rag",
            metadata={"specialist_selection": {"selected_agent_id": "registration_agent"}},
        ),
        DepartmentResponse(
            department=Department.ACADEMIC_PROGRAMS,
            answer="Mevzuat cevabi",
            generation_mode="rag",
            metadata={"specialist_selection": {"selected_agent_id": "regulation_agent"}},
        ),
    ]

    answer = append_generation_summary(
        "Final cevap",
        responses,
        used_global_synthesis=True,
        routing_strategy="parallel",
        agents_involved=["registration_agent", "regulation_agent", "orchestrator"],
    )
    normalized = normalize_text(answer)

    assert "kayit isleri" in normalized
    assert "mevzuat" in normalized
    assert "ogrenci isleri + akademik programlar" not in normalized


def test_append_source_summary_counts_duplicate_document_chunks():
    response = DepartmentResponse(
        department=Department.ACADEMIC_PROGRAMS,
        answer="Kaynakli ara cevap",
        sources=[
            RAGSource(content="parca 1", score=0.9, metadata={"source": "yonerge.pdf"}),
            RAGSource(content="parca 2", score=0.8, metadata={"source": "yonerge.pdf"}),
            RAGSource(content="parca 3", score=0.7, metadata={"source": "takvim.pdf"}),
        ],
        generation_mode="rag",
    )

    answer = append_source_summary("Final cevap", [response])

    assert "- Belge: yonerge.pdf (2 parça)" in answer
    assert "- Belge: takvim.pdf" in answer


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
    assert "şu şekild" in cleaned
    assert "bilgi" in cleaned
    assert "birden fazla kaynaktan" in cleaned
    assert "belirli bir miktarda" in cleaned


def test_clean_final_answer_replaces_english_word_with_turkish_suffix():
    answer = "Stajı yapıp successini kanıtlayamadığınız sürece mezun olamazsınız."

    cleaned = clean_final_answer(answer)

    assert "success" not in cleaned.lower()
    assert "başarısını" in cleaned.lower()


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
    assert "aşağıdaki" in cleaned
    assert "önce online" in cleaned
    assert "lütfen" in cleaned.lower()


def test_clean_final_answer_replaces_portuguese_following_leak():
    cleaned = clean_final_answer("Basvuru sureci seguintek sekilde isler.")

    assert "seguintek" not in cleaned.lower()
    assert "şu şekilde" in cleaned.lower()


def test_clean_final_answer_naturalizes_level_akts_rule_text():
    cleaned = clean_final_answer(
        "Normal dort yillik lisans programindan mezun olmak icin toplam 240 AKTS tamamlanmalidir."
    )

    assert "dört yıllık" in cleaned
    assert "tamamlanmalıdır" in cleaned


def test_clean_final_answer_replaces_mixed_spanish_leaks():
    answer = "Not cizelgesi ve dilekce ile basvuru yapmaniz da necessario podria."

    cleaned = clean_final_answer(answer)

    assert "necessario" not in cleaned
    assert "podria" not in cleaned
    assert "gerekli" in cleaned


def test_clean_final_answer_replaces_recent_foreign_and_broken_tokens():
    answer = "Bilgisayar muhendisligi ile ilgili hangi Informationen almak istiyorsunuz? Kayıp veya ztr edilen kart yenilenir."

    cleaned = clean_final_answer(answer)

    assert "Informationen" not in cleaned
    assert " ztr " not in f" {cleaned} "
    assert "bilgi" in cleaned.lower()
    assert "zayi edilen" in cleaned.lower()


def test_clean_final_answer_replaces_slack_observed_bad_tokens():
    answer = "Ogrenci isleri departamento gore benötilen sartlar ve condiğini saglamalisiniz. Bu durum znajabilir."

    cleaned = clean_final_answer(answer)

    assert "departamento" not in cleaned
    assert "benötilen" not in cleaned
    assert "condi" not in cleaned
    assert "znajabilir" not in cleaned


def test_clean_final_answer_removes_contact_footer_before_metadata():
    answer = (
        "BIL203 dersinin on kosulu BIL104 dersidir.\n\n"
        "---\n"
        "Daha iyi yardımcı olabilmem için sorunuzu daha detaylı açıklayabilirsiniz "
        "ya da ilgili sekreterin iletişim bilgilerini paylaşırım. \"İletişim bilgisi\" yazarak ulaşabilirsiniz.\n\n"
        "Üretim Türü:\n- VT"
    )

    cleaned = clean_final_answer(answer)

    assert "Daha iyi yardımcı" not in cleaned
    assert "BIL203 dersinin on kosulu" in cleaned


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


def test_filter_low_confidence_responses_keeps_exact_tuition_owner_only():
    finance = DepartmentResponse(
        department=Department.FINANCE,
        answer="Yillik ucret: 1.759,00 TL. Donemlik ucret: 879,50 TL.",
        db_data={"annual_amount": 1759.0, "semester_amount": 879.5},
        generation_mode="vt",
        metadata={"source_owner": "tuition_fee_catalog"},
    )
    academic = DepartmentResponse(
        department=Department.ACADEMIC_PROGRAMS,
        answer="Uzaktan egitim yonergesinde baska bilgiler vardir.",
        sources=[
            RAGSource(
                content="alakasiz akademik kaynak",
                score=0.91,
                metadata={"score_type": "reranker"},
            )
        ],
        generation_mode="rag",
    )

    filtered = filter_low_confidence_responses([finance, academic])

    assert filtered == [finance]


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
    assert "net bilgi bulunamadı" in cleaned


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
