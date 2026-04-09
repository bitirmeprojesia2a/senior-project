"""Orchestrator testleri."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.a2a import A2AQueryPayload, build_department_response_task, build_query_task
from src.core.constants import ConfidenceLevel, Department, RoutingStrategy, TaskType
from src.db.schemas import DepartmentResponse, RAGSource, RoutingResult
from src.orchestrators.department import DepartmentOrchestrator
from src.orchestrators.main import MainOrchestrator
from src.orchestrators.response_utils import filter_low_confidence_responses
from src.orchestrators.synthesis_utils import build_global_synthesis_prompt


class _FakeAgent:
    def __init__(self, name: str, department: Department):
        self.name = name
        self.department = department
        self.agent_id = f"{name}_agent"
        self.definition = SimpleNamespace(
            name=f"{name.title()} Agent",
            description=f"{name} aciklamasi",
        )

        async def _handle_task(task):
            return build_department_response_task(
                DepartmentResponse(
                    department=department,
                    answer=f"{name} yaniti",
                    sources=[],
                ),
                request_task=task,
                emitter_id=self.agent_id,
                emitter_name=self.definition.name,
            )

        self.handle_task = AsyncMock(side_effect=_handle_task)


class _FakeDepartmentOrchestrator:
    def __init__(self, department: Department, answer: str):
        self.department = department
        response = DepartmentResponse(
            department=department,
            answer=answer,
            sources=[],
        )
        self.handle = AsyncMock(
            return_value=response
        )

        async def _handle_task(task, *args, **kwargs):
            return build_department_response_task(
                response,
                request_task=task,
                emitter_id=f"{department.value}_orchestrator",
                emitter_name=f"{department.value} Orchestrator",
            )

        self.handle_task = AsyncMock(side_effect=_handle_task)


@pytest.mark.asyncio
async def test_department_orchestrator_routes_to_matching_agent():
    registration = _FakeAgent("registration", Department.STUDENT_AFFAIRS)
    fallback = _FakeAgent("fallback", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    orchestrator = DepartmentOrchestrator(
        department=Department.STUDENT_AFFAIRS,
        agents={TaskType.REGISTRATION_QUERY: registration},
        fallback_agent=fallback,
        telemetry_service=telemetry,
    )

    response = await orchestrator.handle(
        query_text="Ders kaydi ne zaman?",
        context_id="ctx-1",
        task_type=TaskType.REGISTRATION_QUERY,
    )

    assert response.answer == "registration yaniti"
    registration.handle_task.assert_awaited_once()
    fallback.handle_task.assert_not_awaited()
    telemetry.record_agent_task.assert_awaited_once()


@pytest.mark.asyncio
async def test_department_orchestrator_uses_fallback_agent_when_task_type_missing():
    fallback = _FakeAgent("fallback", Department.FINANCE)
    telemetry = AsyncMock()
    orchestrator = DepartmentOrchestrator(
        department=Department.FINANCE,
        agents={},
        fallback_agent=fallback,
        telemetry_service=telemetry,
    )

    response = await orchestrator.handle(
        query_text="Belirsiz bir finans sorgusu",
        context_id="ctx-2",
        task_type=None,
    )

    assert response.answer == "fallback yaniti"
    fallback.handle_task.assert_awaited_once()
    telemetry.record_agent_task.assert_awaited_once()


@pytest.mark.asyncio
async def test_main_orchestrator_combines_parallel_department_responses():
    router = AsyncMock()
    router.route = AsyncMock(
        return_value=RoutingResult(
            departments=[Department.STUDENT_AFFAIRS, Department.FINANCE],
            confidence=0.81,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.PARALLEL,
            reasoning="Coklu departman sorgusu",
            task_type=TaskType.REGISTRATION_QUERY,
        )
    )
    student_orchestrator = _FakeDepartmentOrchestrator(Department.STUDENT_AFFAIRS, "ogrenci isleri cevabi")
    finance_orchestrator = _FakeDepartmentOrchestrator(Department.FINANCE, "finans cevabi")
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=101)
    telemetry.finalize_query_log = AsyncMock()

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={
            Department.STUDENT_AFFAIRS: student_orchestrator,
            Department.FINANCE: finance_orchestrator,
        },
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
    )

    response = await orchestrator.handle_query("Yatay gecis harc durumu nedir?", context_id="ctx-3")

    assert "ogrenci isleri cevabi" in response.answer
    assert "finans cevabi" in response.answer
    assert set(response.departments_involved) == {"student_affairs", "finance"}
    telemetry.create_query_log.assert_awaited_once()
    telemetry.finalize_query_log.assert_awaited_once()


@pytest.mark.asyncio
async def test_main_orchestrator_appends_related_announcements_when_available():
    router = AsyncMock()
    router.route = AsyncMock(
        return_value=RoutingResult(
            departments=[Department.ACADEMIC_PROGRAMS],
            confidence=0.88,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.DIRECT,
            reasoning="Cap ve mufredat sorgusu",
            task_type=TaskType.PROCEDURE_QUERY,
        )
    )
    academic_orchestrator = _FakeDepartmentOrchestrator(
        Department.ACADEMIC_PROGRAMS,
        "Akademik program cevabi",
    )
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)

    async def _announcement_handle_task(task):
        return build_department_response_task(
            DepartmentResponse(
                department=Department.STUDENT_AFFAIRS,
                answer="Ilgili duyurular:\n1. Cap Basvurulari Acildi",
                sources=[
                    RAGSource(
                        content="Cap basvurulari acildi.",
                        score=1.0,
                        metadata={"record_type": "announcement"},
                    )
                ],
            ),
            request_task=task,
            emitter_id=announcement_agent.agent_id,
            emitter_name=announcement_agent.definition.name,
        )

    announcement_agent.handle_task = AsyncMock(side_effect=_announcement_handle_task)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=303)
    telemetry.finalize_query_log = AsyncMock()
    telemetry.record_agent_task = AsyncMock()
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(
        return_value="Akademik program cevabi\n\nIlgili duyurular:\n1. Cap Basvurulari Acildi"
    )

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={
            Department.ACADEMIC_PROGRAMS: academic_orchestrator,
        },
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
        llm_service=llm_service,
    )

    response = await orchestrator.handle_query("Cap basvurulari ne zaman?", context_id="ctx-announce")

    assert "Akademik program cevabi" in response.answer
    assert "Ilgili duyurular" in response.answer
    assert "Kaynak Ozeti:" in response.answer
    assert "Duyuru kaydi:" in response.answer
    assert response.departments_involved == ["academic_programs"]
    assert any(source.metadata.get("record_type") == "announcement" for source in response.sources)
    announcement_agent.handle_task.assert_awaited_once()
    telemetry.record_agent_task.assert_awaited_once()


@pytest.mark.asyncio
async def test_main_orchestrator_skips_related_announcements_for_contact_queries():
    router = AsyncMock()
    router.route = AsyncMock(
        return_value=RoutingResult(
            departments=[Department.ACADEMIC_PROGRAMS],
            confidence=0.91,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.DIRECT,
            reasoning="Iletisim sorgusu",
            task_type=TaskType.PROCEDURE_QUERY,
        )
    )
    academic_orchestrator = _FakeDepartmentOrchestrator(
        Department.ACADEMIC_PROGRAMS,
        "Ilgili birim iletisim bilgileri:\n- Program Isleri Ofisi",
    )
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=304)
    telemetry.finalize_query_log = AsyncMock()
    telemetry.record_agent_task = AsyncMock()

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={
            Department.ACADEMIC_PROGRAMS: academic_orchestrator,
        },
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
    )

    response = await orchestrator.handle_query("Iletisim bilgisi", context_id="ctx-contact")

    assert "Program Isleri Ofisi" in response.answer
    assert "Ilgili duyurular" not in response.answer
    assert "Kaynak Ozeti:" in response.answer
    assert "Ofis iletisim kaydi: Akademik Programlar" in response.answer
    announcement_agent.handle_task.assert_not_awaited()


@pytest.mark.asyncio
async def test_main_orchestrator_skips_related_announcements_for_static_queries():
    router = AsyncMock()
    router.route = AsyncMock(
        return_value=RoutingResult(
            departments=[Department.ACADEMIC_PROGRAMS],
            confidence=0.93,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.DIRECT,
            reasoning="Statik akademik sorgu",
            task_type=TaskType.COURSE_QUERY,
        )
    )
    academic_orchestrator = _FakeDepartmentOrchestrator(
        Department.ACADEMIC_PROGRAMS,
        "BIL104 dersinin onkosulu BIL103'tur.",
    )
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=305)
    telemetry.finalize_query_log = AsyncMock()
    telemetry.record_agent_task = AsyncMock()

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={
            Department.ACADEMIC_PROGRAMS: academic_orchestrator,
        },
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
    )

    response = await orchestrator.handle_query("BIL104 dersinin on kosulu nedir?", context_id="ctx-static")

    assert "BIL104 dersinin onkosulu" in response.answer
    assert "Ilgili duyurular" not in response.answer
    announcement_agent.handle_task.assert_not_awaited()


def test_filter_low_confidence_responses_drops_weak_rag_noise_when_strong_answer_exists():
    weak = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Zayif RAG yaniti",
        sources=[
            RAGSource(
                content="Alakasiz belge parcasi",
                score=0.0003,
                metadata={"source": "ogrenci_isleri.pdf"},
            )
        ],
    )
    strong = DepartmentResponse(
        department=Department.ACADEMIC_PROGRAMS,
        answer="Guclu akademik cevap",
        sources=[
            RAGSource(
                content="CAP yonergesi ilgili maddeler",
                score=0.12,
                metadata={"source": "yonerge_cift_anadal_yandal.pdf"},
            )
        ],
    )
    announcement = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Ilgili duyurular:\n1. CAP Basvurulari Acildi",
        sources=[
            RAGSource(
                content="CAP Basvurulari Acildi",
                score=1.0,
                metadata={"record_type": "announcement"},
            )
        ],
    )

    filtered = filter_low_confidence_responses([weak, strong, announcement])

    assert weak not in filtered
    assert strong in filtered
    assert announcement in filtered


def test_build_global_synthesis_prompt_keeps_substantial_department_context():
    long_tail = "SON-BOLUM-TAM-METIN"
    academic_answer = "Akademik cevap " + ("detay " * 160) + long_tail
    finance_answer = "Finans cevap " + ("kosul " * 160) + long_tail

    prompt, meaningful = build_global_synthesis_prompt(
        "CAP ve harc durumu nedir?",
        [
            DepartmentResponse(
                department=Department.ACADEMIC_PROGRAMS,
                answer=academic_answer,
                sources=[],
            ),
            DepartmentResponse(
                department=Department.FINANCE,
                answer=finance_answer,
                sources=[],
            ),
        ],
    )

    assert len(meaningful) == 2
    assert long_tail in prompt


@pytest.mark.asyncio
async def test_main_orchestrator_returns_clarification_when_no_department_selected():
    router = AsyncMock()
    router.route = AsyncMock(
        return_value=RoutingResult(
            departments=[],
            confidence=0.1,
            confidence_level=ConfidenceLevel.LOW,
            strategy=RoutingStrategy.CLARIFICATION,
            reasoning="Departman secilemedi",
            task_type=None,
        )
    )
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=202)
    telemetry.finalize_query_log = AsyncMock()
    telemetry.record_agent_task = AsyncMock()

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={},
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
    )

    response = await orchestrator.handle_query("Merhaba", context_id="ctx-4")

    assert "belirleyemedim" in response.answer
    assert "Ogrenci Isleri" in response.answer
    assert response.departments_involved == []
    announcement_agent.handle_task.assert_not_awaited()
