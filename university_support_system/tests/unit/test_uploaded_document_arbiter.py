"""Uploaded document context arbiter tests."""

from __future__ import annotations

import pytest

from src.transcripts import DocumentContextTarget, UploadedDocumentArbiter
from src.transcripts.document_intent import DocumentQuestionIntent
from src.transcripts.service import DocumentField, TranscriptDocument, TranscriptCourse


def _transcript() -> TranscriptDocument:
    return TranscriptDocument(
        filename="transkript.txt",
        text="transkript",
        document_type="transcript",
        courses=(
            TranscriptCourse(code="BIL101", name="Programlamaya Giris", credit=3, akts=5, grade="AA"),
            TranscriptCourse(code="MAT101", name="Matematik I", credit=4, akts=6, grade="FF"),
        ),
        total_akts=11,
        total_credit=7,
        gpa=3.12,
        program_name="Bilgisayar Muhendisligi",
    )


def _generic_document() -> TranscriptDocument:
    return TranscriptDocument(
        filename="ogrenci-belgesi.txt",
        text="Adi Soyadi Test Ogrenci\nBaba Adi Mehmet\nBolum Bilgisayar Muhendisligi",
        document_type="generic_document",
        fields=(
            DocumentField(key="adi soyadi", label="Adi Soyadi", value="Test Ogrenci"),
            DocumentField(key="baba adi", label="Baba Adi", value="Mehmet"),
            DocumentField(key="kan grubu", label="Kan Grubu", value="A Rh+"),
        ),
        parse_confidence="medium",
    )


def _staj_form_document() -> TranscriptDocument:
    return TranscriptDocument(
        filename="zorunlu-staj-formu.txt",
        text=(
            "Zorunlu Staj Formu\n"
            "Adi Soyadi Test Ogrenci\n"
            "En Son Mezun Oldugu Okul Sehit Ozcan Kan Fen Lisesi\n"
            "Staja Baslama Tarihi\n"
            "Suresi(gun)\n"
        ),
        document_type="generic_document",
        fields=(
            DocumentField(
                key="en son mezun oldugu okul",
                label="En Son Mezun Oldugu Okul",
                value="Sehit Ozcan Kan Fen Lisesi",
            ),
            DocumentField(key="suresi gun", label="Suresi(gun)", value="", state="empty"),
        ),
        parse_confidence="medium",
    )


def _adli_sicil_document() -> TranscriptDocument:
    return TranscriptDocument(
        filename="adli-sicil.txt",
        text="ADLI SICIL KAYDI\nDOGUM TARIHI 01.01.2000\nANNE ADI / BABA ADI HURIYE / MUCAHIT",
        document_type="generic_document",
        fields=(
            DocumentField(key="dogum tarihi", label="Dogum Tarihi", value="01.01.2000"),
            DocumentField(key="anne adi baba adi", label="Anne Adi / Baba Adi", value="HURIYE / MUCAHIT"),
        ),
        parse_confidence="medium",
    )


def _schedule_document() -> TranscriptDocument:
    return TranscriptDocument(
        filename="2025-26 Lisans_Ders_Programi_Bahar_Bilgisayar_Muh.pdf",
        text=(
            "Bilgisayar Muhendisligi Lisans Ders Programi Bahar\n"
            "4. SINIF\nSali Yaz. Muh. Lab.\nCuma\n"
        ),
        document_type="schedule_document",
        parse_confidence="medium",
    )


@pytest.mark.asyncio
async def test_arbiter_routes_grade_metric_to_uploaded_document():
    decision = await UploadedDocumentArbiter().decide(
        query="Kac tane AA dersim var?",
        document=_transcript(),
        last_query="Hangi dersleri almisim?",
    )

    assert decision.target == DocumentContextTarget.UPLOADED_DOCUMENT
    assert decision.reason == "transcript_grade_metric"


@pytest.mark.asyncio
async def test_arbiter_routes_clear_institutional_question_to_rag():
    decision = await UploadedDocumentArbiter().decide(
        query="Harc borcum varsa ders kaydi yapabilir miyim?",
        document=_transcript(),
        last_query="Hangi dersleri almisim?",
    )

    assert decision.target == DocumentContextTarget.INSTITUTIONAL_RAG
    assert decision.reason == "institutional_marker_without_document_reference"


@pytest.mark.asyncio
async def test_arbiter_keeps_explicit_document_reference_on_document():
    decision = await UploadedDocumentArbiter().decide(
        query="Bu belgeye gore harc borcum var mi?",
        document=_transcript(),
        last_query="Mezun olmam icin kac akts gerekiyor bu belgeyi incele?",
    )

    assert decision.target == DocumentContextTarget.UPLOADED_DOCUMENT
    assert decision.document_intent == DocumentQuestionIntent.DOCUMENT_SUMMARY


@pytest.mark.asyncio
async def test_arbiter_uses_llm_for_gray_area():
    class _FakeLLM:
        async def generate(self, prompt, system=None, json_mode=False, **kwargs):
            assert json_mode is True
            return (
                '{"target":"uploaded_document","document_intent":"document_summary","confidence":0.74,'
                '"reason":"llm_gray_area","effective_query":"Not dagilimimi belgeye gore ozetle"}'
            )

    decision = await UploadedDocumentArbiter(llm_service=_FakeLLM()).decide(
        query="Bunu biraz acabilir misin?",
        document=_transcript(),
        last_query=None,
    )

    assert decision.target == DocumentContextTarget.UPLOADED_DOCUMENT
    assert decision.reason == "llm_gray_area"
    assert decision.document_intent == DocumentQuestionIntent.DOCUMENT_SUMMARY
    assert decision.effective_query == "Not dagilimimi belgeye gore ozetle"


@pytest.mark.asyncio
async def test_arbiter_routes_generic_document_field_question_to_document():
    decision = await UploadedDocumentArbiter().decide(
        query="Baba adi neymis?",
        document=_generic_document(),
        last_query="Bu belgede ne goruyorsun?",
    )

    assert decision.target == DocumentContextTarget.UPLOADED_DOCUMENT
    assert decision.reason == "generic_document_field_inventory_match"


@pytest.mark.asyncio
async def test_arbiter_routes_belgede_question_to_document():
    decision = await UploadedDocumentArbiter().decide(
        query="Belgede baba adi ne olarak geciyor?",
        document=_generic_document(),
        last_query="Bu belgede ne goruyorsun?",
    )

    assert decision.target == DocumentContextTarget.UPLOADED_DOCUMENT
    assert decision.document_intent == DocumentQuestionIntent.DOCUMENT_FIELD_LOOKUP


@pytest.mark.asyncio
async def test_arbiter_routes_inventory_field_even_when_field_is_not_hardcoded():
    decision = await UploadedDocumentArbiter().decide(
        query="Kan grubu neymis?",
        document=_generic_document(),
        last_query="Bu belgede ne goruyorsun?",
    )

    assert decision.target == DocumentContextTarget.UPLOADED_DOCUMENT
    assert decision.reason == "generic_document_field_inventory_match"


@pytest.mark.asyncio
async def test_arbiter_routes_generic_document_procedure_followup_to_document():
    decision = await UploadedDocumentArbiter().decide(
        query="Nereye teslim ediliyor?",
        document=_generic_document(),
        last_query="Bu belgede neler var?",
    )

    assert decision.target == DocumentContextTarget.UPLOADED_DOCUMENT
    assert decision.document_intent == DocumentQuestionIntent.DOCUMENT_PROCEDURE


@pytest.mark.asyncio
@pytest.mark.parametrize("query", ["Bu belge ne?", "Bu belge ne ise yariyor?"])
async def test_arbiter_routes_generic_document_purpose_question_to_document(query):
    decision = await UploadedDocumentArbiter().decide(
        query=query,
        document=_generic_document(),
        last_query=None,
    )

    assert decision.target == DocumentContextTarget.UPLOADED_DOCUMENT


@pytest.mark.asyncio
async def test_arbiter_keeps_institutional_query_out_of_generic_document():
    decision = await UploadedDocumentArbiter().decide(
        query="Ders kaydi nasil yapilir?",
        document=_generic_document(),
        last_query="Bu belgede neler var?",
    )

    assert decision.target == DocumentContextTarget.INSTITUTIONAL_RAG
    assert decision.reason == "institutional_marker_without_document_reference"


@pytest.mark.asyncio
async def test_arbiter_routes_graduation_akts_out_of_generic_document():
    decision = await UploadedDocumentArbiter().decide(
        query="Lisans icin kac AKTS tamamlamaliyim?",
        document=_generic_document(),
        last_query="Bu belgede neler var?",
    )

    assert decision.target == DocumentContextTarget.INSTITUTIONAL_RAG
    assert decision.reason == "institutional_marker_without_document_reference"


@pytest.mark.asyncio
async def test_arbiter_routes_generic_document_field_inventory_question_to_summary():
    decision = await UploadedDocumentArbiter().decide(
        query="Hangi alanlar var?",
        document=_generic_document(),
        last_query="Bu belgede neler var?",
    )

    assert decision.target == DocumentContextTarget.UPLOADED_DOCUMENT
    assert decision.document_intent == DocumentQuestionIntent.DOCUMENT_SUMMARY


@pytest.mark.asyncio
async def test_arbiter_keeps_empty_field_inventory_followup_on_document():
    decision = await UploadedDocumentArbiter().decide(
        query="Digerleri bos mu?",
        document=_staj_form_document(),
        last_query="Hangi alanlar var belgede ve degerleri ne?",
    )

    assert decision.target == DocumentContextTarget.UPLOADED_DOCUMENT
    assert decision.document_intent == DocumentQuestionIntent.DOCUMENT_SUMMARY
    assert decision.reason == "field_inventory_followup"


@pytest.mark.asyncio
async def test_arbiter_routes_short_date_followup_after_institutional_query_to_rag():
    decision = await UploadedDocumentArbiter().decide(
        query="Tarihleri neler?",
        document=_staj_form_document(),
        last_query="CAP basvuru tarihleri neler?",
    )

    assert decision.target == DocumentContextTarget.INSTITUTIONAL_RAG
    assert decision.reason == "short_followup_after_institutional_query"


@pytest.mark.asyncio
async def test_arbiter_routes_generic_document_continuation_to_document_summary():
    decision = await UploadedDocumentArbiter().decide(
        query="Biraz daha detayli aciklar misin?",
        document=_staj_form_document(),
        last_query="Bu belge ne?",
    )

    assert decision.target == DocumentContextTarget.UPLOADED_DOCUMENT
    assert decision.document_intent == DocumentQuestionIntent.DOCUMENT_SUMMARY
    assert decision.reason == "document_continuation_followup"


@pytest.mark.asyncio
async def test_arbiter_prefers_field_match_before_institutional_marker_for_generic_document():
    decision = await UploadedDocumentArbiter().decide(
        query="En son mezun oldugu okul neymis ogrencinin?",
        document=_staj_form_document(),
        last_query="Belgede hangi alanlar var?",
    )

    assert decision.target == DocumentContextTarget.UPLOADED_DOCUMENT
    assert decision.document_intent == DocumentQuestionIntent.DOCUMENT_FIELD_LOOKUP
    assert decision.reason == "generic_document_field_inventory_match"


@pytest.mark.asyncio
async def test_arbiter_routes_exam_calendar_question_out_of_active_document():
    decision = await UploadedDocumentArbiter().decide(
        query="Butunleme sinav tarihleri nedir?",
        document=_staj_form_document(),
        last_query="Bu belge ne?",
    )

    assert decision.target == DocumentContextTarget.INSTITUTIONAL_RAG
    assert decision.reason == "institutional_marker_without_document_reference"


@pytest.mark.asyncio
async def test_arbiter_routes_ubys_web_address_out_of_active_document():
    decision = await UploadedDocumentArbiter().decide(
        query="UBYS nin web adresi ne?",
        document=_staj_form_document(),
        last_query="Eposta adresi ne ogrencinin?",
    )

    assert decision.target == DocumentContextTarget.INSTITUTIONAL_RAG
    assert decision.reason == "institutional_marker_without_document_reference"


@pytest.mark.asyncio
async def test_arbiter_keeps_birth_date_correction_on_generic_document():
    first = await UploadedDocumentArbiter().decide(
        query="Dogrum tarihi bilgisi var mi?",
        document=_adli_sicil_document(),
        last_query="Belge ne zaman alinmis?",
    )
    second = await UploadedDocumentArbiter().decide(
        query="Dogum tarihi sordum",
        document=_adli_sicil_document(),
        last_query="Dogrum tarihi bilgisi var mi?",
    )

    assert first.target == DocumentContextTarget.UPLOADED_DOCUMENT
    assert first.document_intent == DocumentQuestionIntent.DOCUMENT_FIELD_LOOKUP
    assert second.target == DocumentContextTarget.UPLOADED_DOCUMENT
    assert second.document_intent == DocumentQuestionIntent.DOCUMENT_FIELD_LOOKUP


@pytest.mark.asyncio
async def test_arbiter_uses_previous_query_when_user_says_not_document():
    decision = await UploadedDocumentArbiter().decide(
        query="Belge icin sormuyorum",
        document=_generic_document(),
        last_query="Lisans icin kac AKTS?",
    )

    assert decision.target == DocumentContextTarget.INSTITUTIONAL_RAG
    assert decision.effective_query == "Lisans icin kac AKTS?"


@pytest.mark.asyncio
async def test_arbiter_routes_uploaded_schedule_detail_question_to_hybrid_rag():
    decision = await UploadedDocumentArbiter().decide(
        query="4. siniflarin cuma dersi var mi bu programa gore?",
        document=_schedule_document(),
        last_query="Bu belge nedir?",
    )

    assert decision.target == DocumentContextTarget.HYBRID_DOCUMENT_RAG
    assert decision.document_intent == DocumentQuestionIntent.HYBRID_DOCUMENT_RAG
    assert decision.reason == "schedule_document_detail_question"


@pytest.mark.asyncio
async def test_arbiter_keeps_uploaded_schedule_summary_on_document():
    decision = await UploadedDocumentArbiter().decide(
        query="Bu belge nedir?",
        document=_schedule_document(),
        last_query=None,
    )

    assert decision.target == DocumentContextTarget.UPLOADED_DOCUMENT
    assert decision.document_intent == DocumentQuestionIntent.DOCUMENT_SUMMARY

