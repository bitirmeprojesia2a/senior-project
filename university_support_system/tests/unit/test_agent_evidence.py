"""Specialist answer evidence extraction tests."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.core.constants import Department, TaskType


def test_evidence_extraction_keeps_query_relevant_specific_sentences():
    content = (
        "Genel tanitim metni ogrenci isleri hakkinda bilgi verir. "
        "MADDE 19 - Ogrenci basarisiz oldugu bir secmeli ders yerine sonraki donemde devam etmek kaydiyla baska bir secmeli ders alabilir. "
        "Araya giren bir baska aciklama cumlesi daha eklendi. "
        "Bu paragraf spor etkinlikleri ve topluluk duyurulari hakkindadir. "
        "Bu cumle yemekhane duyurulari hakkindadir. "
        "Bu cumle kutuphane calisma saatleri hakkindadir. "
        "Bu cumle kampus ulasim bilgileri hakkindadir. "
        "MADDE 17 - Devam kosulu teorik derslerde yuzde 70, uygulamalarda yuzde 80 olarak uygulanir. "
        "Son bolum ilgisiz web sayfasi aciklamasidir."
    )

    excerpt = BaseSpecialistAgent._extract_evidence_content(
        "Basarisiz oldugum secmeli ders yerine baska secmeli alirsam devam kosulu nasil degisir?",
        content,
    )

    assert "MADDE 19" in excerpt
    assert "MADDE 17" in excerpt
    assert "spor etkinlikleri" not in excerpt


def test_specialist_agent_builds_evidence_packet_from_results():
    agent = BaseSpecialistAgent(
        AgentDefinition(
            agent_id="test_agent",
            name="Test Agent",
            department=Department.STUDENT_AFFAIRS,
            description="test",
            task_types=(TaskType.PROCEDURE_QUERY,),
            examples=(),
            tags=(),
        ),
        llm_service=AsyncMock(),
    )

    response = agent._build_department_response(
        answer="Devam kosulu teorik derslerde yuzde 70 olarak uygulanir.",
        query_text="Devam kosulu nedir?",
        results=[
            {
                "content": "MADDE 17 - Devam kosulu teorik derslerde yuzde 70, uygulamalarda yuzde 80 olarak uygulanir.",
                "source": "yonetmelik.pdf",
                "score": 0.88,
                "metadata": {"score_type": "reranker"},
            }
        ],
        generation_mode="rag+llm",
        final_answer_owner="main_orchestrator",
        specialist_response_mode="evidence_packet",
    )

    packet = response.metadata["evidence_packet"]
    assert packet["version"] == 1
    assert packet["department"] == Department.STUDENT_AFFAIRS.value
    assert packet["final_answer_owner"] == "main_orchestrator"
    assert packet["specialist_response_mode"] == "evidence_packet"
    assert response.metadata["final_answer_owner"] == "main_orchestrator"
    assert packet["confidence"] == "high"
    assert packet["selected_sources"][0]["source"] == "yonetmelik.pdf"
    assert packet["facts"]


class _FakeRetriever:
    def search(self, *args, **kwargs):
        return [
            {
                "content": (
                    "MADDE 17 - Devam kosulu teorik derslerde yuzde 70, "
                    "uygulamalarda yuzde 80 olarak uygulanir."
                ),
                "source": "yonetmelik.pdf",
                "score": 0.88,
                "metadata": {"score_type": "reranker"},
            }
        ]


@pytest.mark.asyncio
async def test_specialist_agent_evidence_packet_mode_skips_llm_generation():
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(return_value="Uzman LLM cevabi")
    agent = BaseSpecialistAgent(
        AgentDefinition(
            agent_id="test_agent",
            name="Test Agent",
            department=Department.STUDENT_AFFAIRS,
            description="test",
            task_types=(TaskType.PROCEDURE_QUERY,),
            examples=(),
            tags=(),
        ),
        llm_service=llm_service,
    )
    agent._get_retriever = lambda: _FakeRetriever()  # type: ignore[method-assign]

    response = await agent.handle_department_task(
        SimpleNamespace(
            metadata={
                "query_text": "Devam kosulu nedir?",
                "final_answer_owner": "main_orchestrator",
                "specialist_response_mode": "evidence_packet",
            }
        )
    )

    llm_service.generate.assert_not_awaited()
    assert response.generation_mode == "rag"
    assert response.metadata["final_answer_owner"] == "main_orchestrator"
    assert response.metadata["specialist_response_mode"] == "evidence_packet"
    assert response.metadata["evidence_packet"]["selected_sources"]
    assert response.answer.startswith("Kaynak bilgisi final cevap için hazırlandı.")
