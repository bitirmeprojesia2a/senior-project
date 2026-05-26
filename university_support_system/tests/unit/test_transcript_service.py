"""Transcript parsing and scoped QA tests."""

from __future__ import annotations

from datetime import time

import pytest

from src.transcripts import TranscriptProcessor, is_transcript_followup_query, is_uploaded_document_followup_query
import src.transcripts.service as transcript_service
from src.transcripts.service import DocumentField, TranscriptDocument, TranscriptProcessingError


SAMPLE_TRANSCRIPT = """\
Ondokuz Mayis Universitesi Transkript
Genel Not Ortalamasi 3,12
Toplam AKTS 90
Toplam Kredi 60
BIL101 Programlamaya Giris 3 5 AA
MAT101 Matematik I 4 6 FF
FIZ101 Fizik I 3 4 BB
"""


@pytest.mark.asyncio
async def test_transcript_processor_extracts_totals_and_failed_courses():
    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="transkript.txt",
        content=SAMPLE_TRANSCRIPT.encode("utf-8"),
        mimetype="text/plain",
    )

    assert document.total_akts == 90
    assert document.total_credit == 60
    assert document.gpa == 3.12
    assert [course.code for course in document.failed_courses] == ["MAT101"]

    answer = await processor.answer_question(document=document, query="Toplam AKTS'im kac?")
    assert "toplam AKTS: 90" in answer


@pytest.mark.asyncio
async def test_transcript_processor_falls_back_to_llm_for_open_ended_question():
    class _FakeLLM:
        async def generate(self, prompt, system=None, json_mode=False, **kwargs):
            assert "Programlamaya Giris" in prompt
            assert kwargs["model_role"] == "final_refinement"
            return "Transkriptte genel durum iyi; bir basarisiz ders gorunuyor."

    processor = TranscriptProcessor(llm_service=_FakeLLM())
    document = processor.process_bytes(
        filename="transkript.txt",
        content=SAMPLE_TRANSCRIPT.encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(document=document, query="Bu transkripti yorumlar misin?")

    assert "basarisiz ders" in answer


def test_transcript_followup_query_requires_personal_transcript_signal():
    assert is_transcript_followup_query("Toplam AKTS'im kac?") is True
    assert is_transcript_followup_query("Kac tane AA dersim var?") is True
    assert is_transcript_followup_query("Dis hekimligi icin kac AKTS gerekir?") is False
    assert is_uploaded_document_followup_query("Belgeye gore cevaplamadin?") is True


def test_transcript_processor_rejects_unreasonable_total_akts():
    transcript = """\
Ondokuz Mayis Universitesi Transkript
Genel Not Ortalamasi 3,76
Toplam AKTS 1357
Toplam Kredi 147
BIL101 Programlamaya Giris 3 5 AA
MAT101 Matematik I 4 6 BB
"""
    processor = TranscriptProcessor()

    document = processor.process_bytes(
        filename="transkript.txt",
        content=transcript.encode("utf-8"),
        mimetype="text/plain",
    )

    assert document.total_akts == 11
    assert any("AKTS" in warning for warning in document.warnings)


def test_transcript_processor_ignores_header_like_program_labels():
    transcript = """\
Program T?r? Anadal Kredi T?r? AKTS
Program(KEA/ASI): Bilgisayar Muhendisligi
Toplam AKTS 211
BIL101 Programlamaya Giris 3 5 AA
MAT101 Matematik I 4 6 BB
"""
    processor = TranscriptProcessor()

    document = processor.process_bytes(
        filename="transkript.txt",
        content=transcript.encode("utf-8"),
        mimetype="text/plain",
    )

    assert document.program_name == "Bilgisayar Muhendisligi"


def test_transcript_processor_prefers_letter_grade_over_pass_status():
    transcript = """\
Ondokuz Mayis Universitesi Transkript
Toplam AKTS 11
BIL101 Programlamaya Giris 3 5 AA G
MAT101 Matematik I 4 6 BB G
"""
    processor = TranscriptProcessor()

    document = processor.process_bytes(
        filename="transkript.txt",
        content=transcript.encode("utf-8"),
        mimetype="text/plain",
    )

    assert [(course.code, course.grade) for course in document.courses] == [("BIL101", "AA"), ("MAT101", "BB")]


@pytest.mark.asyncio
async def test_transcript_graduation_answer_uses_program_level_from_document():
    transcript = """\
Ondokuz Mayis Universitesi Transkript
Program(KEA/ASI): Bilgisayar Muhendisligi
Toplam AKTS 211
BIL101 Programlamaya Giris 3 5 AA
MAT101 Matematik I 4 6 BB
"""
    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="transkript.txt",
        content=transcript.encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(
        document=document,
        query="Mezun olmam icin kac akts gerekiyor bu belgeyi incele?",
    )

    assert "240 AKTS" in answer
    assert "29 AKTS" in answer


@pytest.mark.asyncio
async def test_transcript_answer_lists_taken_courses_for_hangi_dersleri_almisim():
    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="transkript.txt",
        content=SAMPLE_TRANSCRIPT.encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(document=document, query="Hangi dersleri almisim su ana kadar?")

    assert "BIL101 Programlamaya Giris" in answer
    assert "MAT101 Matematik I" in answer


@pytest.mark.asyncio
async def test_transcript_answer_lists_taken_courses_for_third_person_upload_question():
    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="transkript.txt",
        content=SAMPLE_TRANSCRIPT.encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(document=document, query="Su ana kadar hangi dersleri almis bu ogrenci?")

    assert "BIL101 Programlamaya Giris" in answer
    assert "MAT101 Matematik I" in answer


@pytest.mark.asyncio
async def test_transcript_answer_filters_taken_courses_by_requested_term():
    transcript = """\
Ondokuz Mayis Universitesi Transkript
2025-2026 Guz Donemi
BIL101 Programlamaya Giris 3 5 AA
MAT101 Matematik I 4 6 BB
2025-2026 Bahar Donemi
BIL104 Programlamaya Giris II 3 5 BA
BIL108 Elektrik Devreleri ve Elektronik 4 6 BB
"""
    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="transkript.txt",
        content=transcript.encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(
        document=document,
        query="2025-2026 Bahar doneminde hangi dersleri almisim?",
    )

    assert "2025-2026 Bahar" in answer
    assert "BIL104 Programlamaya Giris II" in answer
    assert "BIL108 Elektrik Devreleri ve Elektronik" in answer
    assert "BIL101 Programlamaya Giris" not in answer


@pytest.mark.asyncio
async def test_transcript_answer_does_not_dump_all_courses_when_term_cannot_be_matched():
    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="transkript.txt",
        content=SAMPLE_TRANSCRIPT.encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(
        document=document,
        query="2026-2026 Bahar doneminde hangi dersleri almisim?",
    )

    assert "2026 Bahar" in answer
    assert "BIL101 Programlamaya Giris" not in answer


@pytest.mark.asyncio
async def test_transcript_answer_counts_letter_grade_courses():
    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="transkript.txt",
        content=SAMPLE_TRANSCRIPT.encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(document=document, query="Kac tane AA dersim var?")

    assert "AA notlu 1 ders" in answer
    assert "BIL101 Programlamaya Giris" in answer


@pytest.mark.asyncio
async def test_transcript_answer_counts_letter_grade_correction_query():
    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="transkript.txt",
        content=SAMPLE_TRANSCRIPT.encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(document=document, query="Emin misin bir suru AA var")

    assert "AA notlu 1 ders" in answer


@pytest.mark.asyncio
async def test_transcript_answer_summarizes_grade_distribution():
    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="transkript.txt",
        content=SAMPLE_TRANSCRIPT.encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(document=document, query="Not dagilimim nasil?")

    assert "AA: 1 ders" in answer
    assert "BB: 1 ders" in answer
    assert "FF: 1 ders" in answer


@pytest.mark.asyncio
async def test_transcript_gpa_scenario_does_not_collapse_to_current_gpa_only():
    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="transkript.txt",
        content=SAMPLE_TRANSCRIPT.encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(
        document=document,
        query="Bu donem 4 ortalama yaparsam genel ortalamam kac olur?",
    )

    assert "3,12" in answer
    assert "3,41" in answer
    assert "30 kredi" in answer
    assert "3,41" in answer


@pytest.mark.asyncio
async def test_transcript_gpa_improvement_question_gets_interpretive_answer():
    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="transkript.txt",
        content=SAMPLE_TRANSCRIPT.encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(
        document=document,
        query="Arttirabilir miyim bu donem 4 ortalama yaparsam?",
    )

    assert "yükselir" in answer
    assert "Kesin hesap" in answer


@pytest.mark.asyncio
async def test_transcript_gpa_advice_question_gets_actionable_answer():
    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="transkript.txt",
        content=SAMPLE_TRANSCRIPT.encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(document=document, query="Bu ortalamayi nasil arttiririm?")

    assert "Mevcut GNO" in answer
    assert "kredi/AKTS" in answer


@pytest.mark.asyncio
async def test_transcript_current_gpa_question_still_returns_current_gpa():
    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="transkript.txt",
        content=SAMPLE_TRANSCRIPT.encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(document=document, query="Genel ortalamam nedir?")

    assert "3,12" in answer
    assert "ortalama" in answer


@pytest.mark.asyncio
async def test_transcript_historical_term_gpa_question_does_not_trigger_projection():
    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="transkript.txt",
        content=SAMPLE_TRANSCRIPT.encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(document=document, query="Hangi donemlerde 4 ortalama yapmisim?")

    assert "4,00" in answer
    assert "Formül" not in answer


@pytest.mark.asyncio
async def test_generic_uploaded_document_is_not_reported_as_transcript():
    class _FakeLLM:
        async def generate(self, prompt, system=None, json_mode=False, **kwargs):
            assert "belge metni" in prompt
            return "Belgeye g?re ba?vuru dilek?esi teslim edilmelidir."

    processor = TranscriptProcessor(llm_service=_FakeLLM())
    document = processor.process_bytes(
        filename="dilekce.txt",
        content="Bu belge staj basvurusu icin teslim edilecek dilekce ornegidir.".encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(document=document, query="Bu belgeyi ozetler misin?")

    assert document.document_type == "form_document"
    assert document.facts is not None
    assert document.facts.document_type == "form_document"
    assert "Transkript" not in answer
    assert "Belgeye g?re" in answer


@pytest.mark.asyncio
async def test_course_schedule_pdf_is_not_classified_as_transcript_even_with_course_like_rows(monkeypatch):
    class _FakeLLM:
        async def generate(self, prompt, system=None, json_mode=False, **kwargs):
            assert "Ders Programi" in prompt
            return "Bu belge Bilgisayar Muhendisligi bahar donemi ders programidir."

    monkeypatch.setattr(
        transcript_service,
        "_extract_pdf_text",
        lambda content: (
            "ONDOKUZ MAYIS UNIVERSITESI\n"
            "Bilgisayar Muhendisligi Lisans Ders Programi Bahar\n"
            "Pazartesi 08:15-09:00 MF205 Matematik-II\n"
            "Sali 09:15-10:00 MF201 Programlamaya Giris 9 12\n"
        ),
    )
    processor = TranscriptProcessor(llm_service=_FakeLLM())
    document = processor.process_bytes(
        filename="2025-26 Lisans_Ders_Programi_Bahar_Bilgisayar_Muh.pdf",
        content=b"%PDF-1.4 fake",
        mimetype="application/pdf",
    )

    answer = await processor.answer_question(document=document, query="Bu belge ne?")

    assert document.document_type == "schedule_document"
    assert "transkript" not in answer.lower()
    assert "ders program" in answer.lower()


def test_image_only_course_schedule_pdf_uses_filename_fallback_when_ocr_is_empty(monkeypatch):
    monkeypatch.setattr(transcript_service, "_extract_pdf_text", lambda content: "")
    monkeypatch.setattr(transcript_service, "_extract_pdf_ocr_text", lambda content: "")

    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="2025-26 Lisans_Ders_Programi_Bahar_Bilgisayar_Muh.pdf",
        content=b"%PDF-1.4 fake",
        mimetype="application/pdf",
    )

    assert document.document_type == "schedule_document"
    assert document.extraction_mode == "pdf_filename_fallback"
    assert document.facts is not None
    assert document.facts.document_type == "schedule_document"


@pytest.mark.asyncio
async def test_schedule_document_answers_from_uploaded_structured_slots():
    processor = TranscriptProcessor()
    document = TranscriptDocument(
        filename="ders-programi.pdf",
        text="Bilgisayar Muhendisligi ders programi",
        document_type="schedule_document",
        schedule_slots=(
            {
                "schedule_group": "4. SINIF",
                "day_of_week": "Sali",
                "start_time": time(10, 15),
                "end_time": time(11, 0),
                "course_name": "Yaz. Muh. Lab.",
                "classroom": "Z08 + L19 / R19",
            },
            {
                "schedule_group": "4. SINIF",
                "day_of_week": "Cuma",
                "start_time": time(8, 15),
                "end_time": time(9, 0),
                "course_name": "Bitirme Projesi",
                "classroom": "Seminer Salonu",
            },
        ),
    )

    answer = await processor.answer_question(
        document=document,
        query="4. siniflarin cuma dersi var mi bu programa gore?",
        document_intent="hybrid_document_rag",
    )

    assert "Cuma" in answer
    assert "Bitirme Projesi" in answer


@pytest.mark.asyncio
async def test_schedule_document_summary_uses_title_when_rows_are_not_parsed():
    processor = TranscriptProcessor()
    document = TranscriptDocument(
        filename="2025-26 Lisans_Ders_Programi_Bahar_Bilgisayar_Muh.pdf",
        text="2025-26 Lisans_Ders_Programi_Bahar_Bilgisayar_Muh.pdf",
        document_type="schedule_document",
        extraction_mode="pdf_filename_fallback",
    )

    answer = await processor.answer_question(document=document, query="Bu belge nedir?")

    assert "ders programi belgesi" in answer
    assert "2025-26 Lisans_Ders_Programi_Bahar_Bilgisayar_Muh" in answer
    assert "yapilandirilmis ders programi" in answer


@pytest.mark.asyncio
async def test_schedule_document_extracts_simple_ocr_text_rows(monkeypatch):
    monkeypatch.setattr(
        transcript_service,
        "_extract_pdf_text",
        lambda content: (
            "Bilgisayar Muhendisligi Lisans Ders Programi Bahar\n"
            "4. SINIF\n"
            "Cuma 08:15-09:00 BIL400 Bitirme Projesi Seminer Salonu\n"
        ),
    )
    monkeypatch.setattr(transcript_service, "_extract_schedule_slots_from_pdf_content", lambda **kwargs: [])

    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="2025-26 Lisans_Ders_Programi_Bahar_Bilgisayar_Muh.pdf",
        content=b"%PDF fake",
        mimetype="application/pdf",
    )

    answer = await processor.answer_question(
        document=document,
        query="4. siniflarin cuma dersi var mi?",
        document_intent="hybrid_document_rag",
    )

    assert document.schedule_slots
    assert "Bitirme Projesi" in answer
    assert "Cuma" in answer


@pytest.mark.asyncio
async def test_generic_document_extracts_inventory_fields_and_answers_directly():
    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="ogrenci-belgesi.txt",
        content=(
            "Ogrenci Belgesi\n"
            "Adi Soyadi: Test Ogrenci\n"
            "Baba Adi Mehmet\n"
            "Kan Grubu: A Rh+\n"
            "Bolum Bilgisayar Muhendisligi\n"
        ).encode("utf-8"),
        mimetype="text/plain",
    )

    assert document.document_type == "student_document"
    assert document.facts is not None
    assert document.facts.person_name == "Test Ogrenci"
    assert {field.key: field.value for field in document.fields}["kan grubu"] == "A Rh+"

    answer = await processor.answer_question(document=document, query="Kan grubu neymis?")

    assert "A Rh+" in answer


@pytest.mark.asyncio
async def test_generic_document_missing_inventory_field_does_not_invent():
    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="ogrenci-belgesi.txt",
        content="Ogrenci Belgesi\nAdi Soyadi: Test Ogrenci\nBaba Adi Mehmet\n".encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(document=document, query="Kan grubu ne?")

    assert "bulamad" in answer


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query",
    ["TC kimlik neymis?", "Ad soyadi neymis?", "eposta adresi neymis?"],
)
async def test_generic_document_blank_form_fields_are_reported_as_present_without_value(query):
    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="zorunlu-staj-formu.txt",
        content=(
            "Zorunlu Staj Formu\n"
            "Adi Soyadi    T.C. Kimlik No    Ogrenci No\n"
            "E-posta Adresi    Telefon No\n"
            "Staj Baslangic Tarihi    Staj Bitis Tarihi\n"
        ).encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(document=document, query=query)

    assert "alani var" in answer
    assert "guvenilir bicimde bulamadim" not in answer


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("Kisinin adi neymis?", "Test Ogrenci"),
        ("Ad soyad", "Test Ogrenci"),
        ("Telefon nosu ne?", "05304344630"),
        ("eposta adresi neymis?", "omer@example.com"),
    ],
)
async def test_generic_document_field_lookup_understands_natural_field_phrases(query, expected):
    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="zorunlu-staj-formu.txt",
        content=(
            "Zorunlu Staj Formu\n"
            "Adi Soyadi: Test Ogrenci\n"
            "E-posta Adresi: omer@example.com\n"
            "Telefon No: 05304344630\n"
            "Adresi: Ankara\n"
        ).encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(document=document, query=query)

    assert expected in answer


@pytest.mark.asyncio
async def test_generic_document_field_lookup_handles_labels_with_institutional_words():
    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="zorunlu-staj-formu.txt",
        content=(
            "Zorunlu Staj Formu\n"
            "En Son Mezun Oldugu Okul: Sehit Ozcan Kan Fen Lisesi\n"
            "Bolum: Sayisal\n"
        ).encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(
        document=document,
        query="En son mezun oldugu okul neymis ogrencinin?",
    )

    assert "Sehit Ozcan Kan Fen Lisesi" in answer


@pytest.mark.asyncio
async def test_generic_document_field_lookup_handles_birth_date_typo():
    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="adli-sicil.txt",
        content="Dogum Tarihi: 01.01.2000\nBelge Tarihi: 11.05.2026\n".encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(
        document=document,
        query="Dogrum tarihi bilgisi var mi?",
        document_intent="document_field_lookup",
    )

    assert "01.01.2000" in answer


@pytest.mark.asyncio
async def test_generic_document_field_lookup_uses_llm_mapper_for_unusual_phrasing():
    class _MapperLLM:
        async def generate(self, prompt, system=None, json_mode=False, **kwargs):
            assert json_mode is True
            assert "field_key" in prompt
            assert "maili" in prompt
            return '{"field_key": "e posta adresi", "confidence": 0.91, "reason": "mail means email"}'

    processor = TranscriptProcessor(llm_service=_MapperLLM())
    document = processor.process_bytes(
        filename="zorunlu-staj-formu.txt",
        content=(
            "Zorunlu Staj Formu\n"
            "Adi Soyadi: Test Ogrenci\n"
            "E-posta Adresi: omer@example.com\n"
            "Telefon No: 05304344630\n"
        ).encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(document=document, query="Kisinin maili hangisi?")

    assert "omer@example.com" in answer


@pytest.mark.asyncio
async def test_generic_document_field_lookup_keeps_deterministic_answer_if_mapper_fails():
    class _FailingMapperLLM:
        async def generate(self, prompt, system=None, json_mode=False, **kwargs):
            raise RuntimeError("limit")

    processor = TranscriptProcessor(llm_service=_FailingMapperLLM())
    document = processor.process_bytes(
        filename="zorunlu-staj-formu.txt",
        content="Telefon No: 05304344630\n".encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(document=document, query="Telefon nosu ne?")

    assert "05304344630" in answer


@pytest.mark.asyncio
async def test_generic_document_answers_criminal_record_result_from_text():
    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="adli-sicil.txt",
        content=(
            "ADLI SICIL KAYDI SORGULAMASI SONUCLARI:\n"
            "YUKARIDA KIMLIK BILGILERI BULUNAN KISININ ADLI SICIL KAYDI YOKTUR.\n"
            "YUKARIDA KIMLIK BILGILERI BULUNAN SAHSIN ADLI SICIL ARSIV KAYDI YOKTUR.\n"
            "NOT: BU SORGULAMA YUKARIDAKI BILGILERE GORE YAPILMISTIR."
        ).encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(document=document, query="Adli sicil kaydi var mi bu kisinin?")

    assert "yoktur" in answer.lower()
    assert "NOT" not in answer


@pytest.mark.asyncio
async def test_generic_document_field_inventory_lists_extracted_values_without_llm():
    class _UnexpectedLLM:
        async def generate(self, *args, **kwargs):
            raise AssertionError("field inventory should not call llm")

    processor = TranscriptProcessor(llm_service=_UnexpectedLLM())
    document = processor.process_bytes(
        filename="zorunlu-staj-formu.txt",
        content=(
            "Zorunlu Staj Formu\n"
            "Adi Soyadi: Test Ogrenci\n"
            "E-posta Adresi: omer@example.com\n"
            "Telefon No: 05304344630\n"
        ).encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(document=document, query="Belgede hangi alanlar var ve degerleri ne?")

    assert "Adi Soyadi: Test Ogrenci" in answer
    assert "E-posta Adresi: omer@example.com" in answer
    assert "Telefon No: 05304344630" in answer


@pytest.mark.asyncio
async def test_generic_document_empty_field_followup_lists_empty_fields():
    processor = TranscriptProcessor()
    document = TranscriptDocument(
        filename="zorunlu-staj-formu.txt",
        text="Zorunlu Staj Formu\nAdi Soyadi: Test Ogrenci\nStaja Baslama Tarihi\nSuresi(gun)\n",
        document_type="generic_document",
        fields=(
            DocumentField(key="adi soyadi", label="Adi Soyadi", value="Test Ogrenci", state="filled"),
            DocumentField(key="staja baslama tarihi", label="Staja Baslama Tarihi", value="", state="empty"),
            DocumentField(key="suresi gun", label="Suresi(gun)", value="", state="empty"),
        ),
    )

    answer = await processor.answer_question(document=document, query="Digerleri bos mu?")

    assert "okunamayan alanlar" in answer
    assert "Staja Baslama Tarihi" in answer


def test_generic_document_extraction_debug_counts_blank_form_fields():
    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="zorunlu-staj-formu.txt",
        content=(
            "Zorunlu Staj Formu\n"
            "Adi Soyadi    T.C. Kimlik No    Ogrenci No\n"
            "E-posta Adresi    Telefon No\n"
            "Telefon No: 0555 000 00 00\n"
        ).encode("utf-8"),
        mimetype="text/plain",
    )

    assert document.extraction_debug["field_count"] >= 4
    assert document.extraction_debug["filled_field_count"] >= 1
    assert document.extraction_debug["empty_field_count"] >= 3
    assert any(field.key == "tc kimlik no" and field.state == "empty" for field in document.fields)
    assert any(field.key == "telefon no" and field.state == "filled" for field in document.fields)


def test_generic_document_does_not_treat_adjacent_labels_as_values():
    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="zorunlu-staj-formu.txt",
        content=(
            "Zorunlu Staj Formu\n"
            "Adi Soyadi    T.C. Kimlik No    Fakulte/YO/MYO    Bolum/Program\n"
            "Ogrenci No    Ogretim Yili    E-posta Adresi    Telefon No\n"
            "Isveren veya Yetkili Adi Soyadi    Gorev ve Unvani    Imza/Kase\n"
        ).encode("utf-8"),
        mimetype="text/plain",
    )

    fields = {field.key: field for field in document.fields}

    assert fields["adi soyadi"].state == "empty"
    assert fields["ogrenci no"].state == "empty"
    assert fields["e posta adresi"].state == "empty"
    assert fields["telefon no"].state == "empty"


def test_generic_pdf_form_fields_override_empty_text_labels(monkeypatch):
    monkeypatch.setattr(
        transcript_service,
        "_extract_pdf_text",
        lambda content: "Zorunlu Staj Formu\nE-posta Adresi    Telefon No\n",
    )
    monkeypatch.setattr(
        transcript_service,
        "_extract_pdf_form_fields",
        lambda content: [
            DocumentField(
                key="e posta adresi",
                label="E-posta adresi",
                value="omer@example.com",
                confidence="high",
                state="filled",
                source="pdf_form",
            )
        ],
    )

    processor = TranscriptProcessor()
    document = processor.process_bytes(
        filename="zorunlu-staj-formu.pdf",
        content=b"pdf-bytes",
        mimetype="application/pdf",
    )

    field = next(field for field in document.fields if field.key == "e posta adresi")
    assert field.value == "omer@example.com"
    assert field.source == "pdf_form"


@pytest.mark.asyncio
async def test_generic_document_open_question_does_not_become_missing_field():
    class _FakeLLM:
        async def generate(self, prompt, system=None, json_mode=False, **kwargs):
            assert "Zorunlu Staj Formu" in prompt
            return "Bu belge zorunlu staj basvurusu icin kullanilan bir formdur."

    processor = TranscriptProcessor(llm_service=_FakeLLM())
    document = processor.process_bytes(
        filename="zorunlu-staj-formu.txt",
        content=(
            "Zorunlu Staj Formu\n"
            "Adi Soyadi:\n"
            "Staj Baslangic Tarihi:\n"
            "Isyeri Yetkilisi Imza/Kase:\n"
        ).encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(document=document, query="Bu belgeyi yorumlar misin nedir bu?")

    assert "zorunlu staj" in answer
    assert "bulamad" not in answer


@pytest.mark.asyncio
async def test_generic_document_procedure_question_uses_document_qa():
    class _FakeLLM:
        async def generate(self, prompt, system=None, json_mode=False, **kwargs):
            assert "teslim" in prompt.lower()
            return "Belge staj basvuru surecinde ilgili bolum/staj komisyonuna teslim edilmek uzere doldurulur."

    processor = TranscriptProcessor(llm_service=_FakeLLM())
    document = processor.process_bytes(
        filename="zorunlu-staj-formu.txt",
        content=(
            "Zorunlu Staj Formu\n"
            "Staj yapacak ogrenci tarafindan doldurulur.\n"
            "Bolum staj komisyonu onayi ve isyeri yetkilisi imza/kase alani bulunur.\n"
        ).encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(document=document, query="Nereye teslim ediliyor bu belge?")

    assert "teslim" in answer
    assert "bulamad" not in answer


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("Bu belge ne?", "staj formudur"),
        ("Bu belge ne ise yariyor?", "staj basvurusu icin kullanilir"),
    ],
)
async def test_generic_document_purpose_questions_do_not_become_field_lookup(query, expected):
    class _FakeLLM:
        async def generate(self, prompt, system=None, json_mode=False, **kwargs):
            assert query in prompt
            return f"Bu belge zorunlu {expected}."

    processor = TranscriptProcessor(llm_service=_FakeLLM())
    document = processor.process_bytes(
        filename="zorunlu-staj-formu.txt",
        content=(
            "Zorunlu Staj Formu\n"
            "Ogrenci bilgileri, staj tarihleri, isyeri bilgileri ve imza/kase alanlari bulunur.\n"
        ).encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(document=document, query=query)

    assert expected in answer
    assert "bulamad" not in answer
    assert '"?"' not in answer


@pytest.mark.asyncio
async def test_generic_document_llm_answer_repairs_broken_foreign_token():
    class _RepairLLM:
        def __init__(self):
            self.calls = 0

        async def generate(self, prompt, system=None, json_mode=False, **kwargs):
            self.calls += 1
            if self.calls == 1:
                return "Ara sinav haftasi 15-23 Kasim 2025 tanggalarinda duzenlenir."
            assert "Onceki cevap" in prompt
            return "Ara sinav haftasi 15-23 Kasim 2025 tarihleri arasinda duzenlenir."

    llm = _RepairLLM()
    processor = TranscriptProcessor(llm_service=llm)
    document = processor.process_bytes(
        filename="akademik-takvim.txt",
        content="2025-2026 Genel Akademik Takvim\nAra sinav haftasi 15-23 Kasim 2025\n".encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(document=document, query="Sinavlar ne zaman?")

    assert llm.calls == 2
    assert "tangg" not in answer
    assert "tarihleri arasinda" in answer


def test_image_without_ocr_dependency_returns_controlled_error():
    processor = TranscriptProcessor()

    with pytest.raises(TranscriptProcessingError):
        processor.process_bytes(filename="transkript.png", content=b"not-an-image", mimetype="image/png")


def test_image_transcript_uses_ocr_text(monkeypatch):
    monkeypatch.setattr(transcript_service, "_extract_image_ocr_text", lambda content: SAMPLE_TRANSCRIPT)
    processor = TranscriptProcessor()

    document = processor.process_bytes(
        filename="transkript.png",
        content=b"image-bytes",
        mimetype="image/png",
    )

    assert document.extraction_mode == "image_ocr"
    assert document.total_akts == 90
    assert [course.code for course in document.failed_courses] == ["MAT101"]


def test_scanned_pdf_falls_back_to_ocr(monkeypatch):
    monkeypatch.setattr(transcript_service, "_extract_pdf_text", lambda content: "")
    monkeypatch.setattr(transcript_service, "_extract_pdf_ocr_text", lambda content: SAMPLE_TRANSCRIPT)
    processor = TranscriptProcessor()

    document = processor.process_bytes(
        filename="transkript.pdf",
        content=b"pdf-bytes",
        mimetype="application/pdf",
    )

    assert document.extraction_mode == "pdf_ocr"
    assert any("OCR" in warning for warning in document.warnings)
    assert document.total_credit == 60


def test_pdf_reader_error_still_falls_back_to_ocr(monkeypatch):
    def _raise_pdf_error(content):
        raise TranscriptProcessingError("PDF dosyasi okunamadi.")

    monkeypatch.setattr(transcript_service, "_extract_pdf_text", _raise_pdf_error)
    monkeypatch.setattr(transcript_service, "_extract_pdf_ocr_text", lambda content: SAMPLE_TRANSCRIPT)
    processor = TranscriptProcessor()

    document = processor.process_bytes(
        filename="transkript.pdf",
        content=b"pdf-bytes",
        mimetype="application/pdf",
    )

    assert document.extraction_mode == "pdf_ocr"
    assert document.total_akts == 90
    assert any("OCR" in warning for warning in document.warnings)


def test_uploaded_document_facts_are_populated_for_transcripts():
    processor = TranscriptProcessor()

    document = processor.process_bytes(
        filename="transkript.txt",
        content=SAMPLE_TRANSCRIPT.encode("utf-8"),
        mimetype="text/plain",
    )

    assert document.facts is not None
    assert document.facts.document_type == "transcript"
    assert document.facts.transcript_courses == document.courses
    assert any(field.key == "toplam akts" and field.value == "90" for field in document.facts.fields)


def test_uploaded_document_classifier_uses_specific_document_types():
    processor = TranscriptProcessor()

    staj_form = processor.process_bytes(
        filename="zorunlu-staj-formu.txt",
        content="Zorunlu Staj Formu\nAdi Soyadi: Test Ogrenci\n".encode("utf-8"),
        mimetype="text/plain",
    )
    adli_sicil = processor.process_bytes(
        filename="adli-sicil-kaydi.txt",
        content=(
            "ADLI SICIL KAYDI SORGULAMASI SONUCLARI:\n"
            "YUKARIDA KIMLIK BILGILERI BULUNAN KISININ ADLI SICIL KAYDI YOKTUR.\n"
            "YUKARIDA KIMLIK BILGILERI BULUNAN SAHSIN ADLI SICIL ARSIV KAYDI YOKTUR.\n"
        ).encode("utf-8"),
        mimetype="text/plain",
    )

    assert staj_form.document_type == "form_document"
    assert staj_form.facts is not None
    assert staj_form.facts.person_name == "Test Ogrenci"
    assert adli_sicil.document_type == "criminal_record"
    assert adli_sicil.facts is not None
    assert adli_sicil.facts.status == "adli_sicil_ve_arsiv_kaydi_yok"


def test_course_like_rows_without_transcript_evidence_do_not_become_transcript():
    processor = TranscriptProcessor()

    document = processor.process_bytes(
        filename="ders-listesi.txt",
        content=(
            "BIL101 Programlamaya Giris 3 5\n"
            "MAT101 Matematik I 4 6\n"
            "Bu belge yalnizca ders listesi ornegidir.\n"
        ).encode("utf-8"),
        mimetype="text/plain",
    )

    assert document.document_type == "generic_document"
    assert not document.courses

