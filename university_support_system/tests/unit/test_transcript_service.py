"""Transcript parsing and scoped QA tests."""

from __future__ import annotations

import pytest

from src.transcripts import TranscriptProcessor, is_transcript_followup_query
from src.transcripts.service import TranscriptProcessingError


SAMPLE_TRANSCRIPT = """\
Ondokuz Mayis Universitesi Transkript
Genel Not Ortalaması 3,12
Toplam AKTS 90
Toplam Kredi 60
BIL101 Programlamaya Giriş 3 5 AA
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

    answer = await processor.answer_question(document=document, query="Toplam AKTS'im kaç?")
    assert answer == "Transkriptte görünen toplam AKTS: 90."


@pytest.mark.asyncio
async def test_transcript_processor_falls_back_to_llm_for_open_ended_question():
    class _FakeLLM:
        async def generate(self, prompt, system=None, json_mode=False, **kwargs):
            assert "Programlamaya Giriş" in prompt
            assert kwargs["model_role"] == "final_refinement"
            return "Transkriptte genel durum iyi; bir başarısız ders görünüyor."

    processor = TranscriptProcessor(llm_service=_FakeLLM())
    document = processor.process_bytes(
        filename="transkript.txt",
        content=SAMPLE_TRANSCRIPT.encode("utf-8"),
        mimetype="text/plain",
    )

    answer = await processor.answer_question(document=document, query="Bu transkripti yorumlar mısın?")

    assert "başarısız ders" in answer


def test_transcript_followup_query_requires_personal_transcript_signal():
    assert is_transcript_followup_query("Toplam AKTS'im kaç?") is True
    assert is_transcript_followup_query("Diş hekimliği için kaç AKTS gerekir?") is False


def test_image_without_ocr_dependency_returns_controlled_error():
    processor = TranscriptProcessor()

    with pytest.raises(TranscriptProcessingError):
        processor.process_bytes(filename="transkript.png", content=b"not-an-image", mimetype="image/png")
