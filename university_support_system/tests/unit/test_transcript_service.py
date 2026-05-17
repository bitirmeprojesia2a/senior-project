"""Transcript parsing and scoped QA tests."""

from __future__ import annotations

import pytest

from src.transcripts import TranscriptProcessor, is_transcript_followup_query
import src.transcripts.service as transcript_service
from src.transcripts.service import TranscriptProcessingError


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
    assert is_transcript_followup_query("Dis hekimligi icin kac AKTS gerekir?") is False


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
