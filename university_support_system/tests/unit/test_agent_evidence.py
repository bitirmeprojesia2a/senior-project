"""Specialist answer evidence extraction tests."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.core.config import settings
from src.core.constants import Department, TaskType
from src.core.policy_facets import align_policy_evidence, resolve_policy_facet
from src.core.text_normalization import normalize_text
from src.quality.evidence import extract_factual_claims, select_evidence_sentences


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


def test_evidence_extraction_merges_pdf_soft_breaks_for_gpa_threshold():
    content = (
        "MADDE 5 - CAP'a basvuru, kabul ve kayit kosullari sunlardir:\n"
        "e) Ogrencinin CAP'a basvurabilmesi icin basvurdugu yari yila kadar "
        "ana dal lisans programinda yer alan tum dersleri almis ve basarmis "
        "olmasi, basvurusu sirasindaki ana dal not\n"
        "ortalamasinin 4,00 uzerinden en az 3,00 olmasi ve ana dal diploma "
        "programinin ilgili sinifinda basari siralamasi itibari ile en az "
        "ilk % 20'sinde bulunmasi gerekir.\n"
        "i) CAP basvurularinin degerlendirilmesinde once ana dal not "
        "ortalamasina bakilir."
    )

    excerpt = select_evidence_sentences(
        "CAP basvurusu icin not ortalamasi kac olmali?",
        content,
        max_sentences=3,
        min_score=0.30,
    )
    facts = extract_factual_claims(content)

    assert "ana dal not ortalamasinin 4,00 uzerinden en az 3,00" in normalize_text(excerpt)
    assert any("3,00" in fact and "not ortalamas" in fact for fact in facts)


def test_policy_facet_bias_demotes_completion_clause_for_application_question():
    results = [
        {
            "content": (
                "Ogrencinin CAP'a basvurabilmesi icin ana dal not ortalamasinin "
                "4,00 uzerinden en az 3,00 olmasi gerekir."
            ),
            "source": "yonerge_cift_anadal_yandal.pdf",
            "score": 0.62,
            "metadata": {"source": "yonerge_cift_anadal_yandal.pdf"},
        },
        {
            "content": (
                "Ogrencinin CAP'tan mezun olabilmesi icin ana dal genel not "
                "ortalamasinin 4,00 uzerinden en az 2,75 olmasi gerekir."
            ),
            "source": "yonerge_cift_anadal_yandal.pdf",
            "score": 0.7,
            "metadata": {"source": "yonerge_cift_anadal_yandal.pdf"},
        },
    ]

    adjusted = BaseSpecialistAgent._apply_plan_evidence_source_bias(
        results,
        {
            "evidence_contract": {"preferred_sources": ["yonerge_cift_anadal_yandal.pdf"]},
            "policy_facet": {
                "facet": "application_gpa_eligibility",
                "target_program": "double_major",
                "prefer_evidence_markers": ["basvurabilmesi", "not ortalamasi"],
                "avoid_evidence_markers": ["mezun olabilmesi"],
                "program_prefer_evidence_markers": ["cap", "cift ana dal"],
                "program_avoid_evidence_markers": ["yan dal programina"],
                "reason": "application_or_eligibility_query_without_completion_request",
            },
        },
    )

    assert "3,00" in adjusted[0]["content"]
    assert adjusted[0]["metadata"]["policy_facet"]["facet"] == "application_gpa_eligibility"
    assert float(adjusted[0]["score"]) > float(adjusted[1]["score"])


def test_policy_facet_registry_builds_generic_query_frame_and_alignment():
    frame = resolve_policy_facet(
        query="CAP basvurusu icin not ortalamasi kac olmali?",
        params={
            "question_type": "eligibility",
            "must_answer": ["not ortalamasi", "basvuru sartlari"],
        },
        answer_contract={"must_answer": ["not ortalamasi kosulu"]},
    )

    cap_alignment = align_policy_evidence(
        frame,
        content="CAP'a basvurabilmesi icin ana dal not ortalamasinin en az 3,00 olmasi gerekir.",
    )
    minor_alignment = align_policy_evidence(
        frame,
        content="Yan dal programina basvurabilmek icin not ortalamasinin en az 2,00 olmasi sarttir.",
    )

    assert frame["facet"] == "eligibility"
    assert frame["target_program"] == "double_major"
    assert cap_alignment["status"] == "match"
    assert minor_alignment["status"] == "conflict"
    assert "minor" in minor_alignment["conflict_programs"]


def test_policy_facet_bias_demotes_minor_threshold_for_cap_question():
    results = [
        {
            "content": (
                "Ogrencinin CAP'a basvurabilmesi icin ana dal not ortalamasinin "
                "4,00 uzerinden en az 3,00 olmasi gerekir."
            ),
            "source": "cift_ana_dal_ikinci_lisans_ve_yan_dal_programi.pdf",
            "score": 0.62,
            "metadata": {"source": "cift_ana_dal_ikinci_lisans_ve_yan_dal_programi.pdf"},
        },
        {
            "content": (
                "Yan dal programina basvurabilmek icin ogrencinin not "
                "ortalamasinin 4,00 uzerinden en az 2,00 olmasi sarttir."
            ),
            "source": "cift_ana_dal_ikinci_lisans_ve_yan_dal_programi.pdf",
            "score": 0.68,
            "metadata": {"source": "cift_ana_dal_ikinci_lisans_ve_yan_dal_programi.pdf"},
        },
    ]

    adjusted = BaseSpecialistAgent._apply_plan_evidence_source_bias(
        results,
        {
            "policy_facet": {
                "facet": "application_gpa_eligibility",
                "target_program": "double_major",
                "prefer_evidence_markers": ["basvurabilmesi", "not ortalamasi"],
                "avoid_evidence_markers": [],
                "program_prefer_evidence_markers": ["cap", "cift ana dal"],
                "program_avoid_evidence_markers": ["yan dal programina"],
                "reason": "application_or_eligibility_query_without_completion_request",
            },
        },
    )

    assert "3,00" in adjusted[0]["content"]
    assert "2,00" in adjusted[1]["content"]
    assert float(adjusted[0]["score"]) > float(adjusted[1]["score"])


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
    assert list(packet.keys()).count("department") == 1
    assert packet["final_answer_owner"] == "main_orchestrator"
    assert packet["specialist_response_mode"] == "evidence_packet"
    assert response.metadata["final_answer_owner"] == "main_orchestrator"
    assert packet["confidence"] == "high"
    assert packet["selected_sources"][0]["source"] == "yonetmelik.pdf"
    assert packet["facts"]


@pytest.mark.asyncio
async def test_specialist_contact_fetcher_uses_signature_instead_of_typeerror_fallback():
    calls: list[dict] = []

    async def legacy_contact_fetcher(*, department, agent_id):
        calls.append({"department": department, "agent_id": agent_id})
        return []

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
        contact_fetcher=legacy_contact_fetcher,
    )

    contacts = await agent._fetch_contacts(
        department=Department.STUDENT_AFFAIRS,
        agent_id="test_agent",
        include_generic=False,
    )

    assert contacts == []
    assert calls == [{"department": Department.STUDENT_AFFAIRS, "agent_id": "test_agent"}]


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


@pytest.mark.asyncio
async def test_specialist_agent_carries_source_owner_policy_diagnostics(monkeypatch):
    monkeypatch.setattr(settings.source_owner_policy, "mode", "advisory")
    llm_service = AsyncMock()
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
                "source_owner": {
                    "schema": "omu.source_owner.v1",
                    "primary": "student_affairs_policy",
                    "reasoning": "task_type",
                },
            }
        )
    )

    assert response.metadata["source_owner"]["primary"] == "student_affairs_policy"
    assert response.metadata["source_owner_policy"]["status"] == "applied"
    assert response.sources[0].metadata["source_owner_compatible"] is True
    assert response.metadata["evidence_packet"]["source_owner"]["primary"] == "student_affairs_policy"
    assert response.answer.startswith("Kaynak bilgisi final cevap için hazırlandı.")
