"""Orchestrator testleri."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.core.constants import ConfidenceLevel, Department, RoutingStrategy, TaskType
from src.db.schemas import DepartmentResponse, RAGSource, RoutingResult
from src.orchestrators.department import DepartmentOrchestrator
from src.orchestrators.main import MainOrchestrator


class _FakeAgent:
    def __init__(self, name: str, department: Department):
        self.name = name
        self.department = department
        self.agent_id = f"{name}_agent"
        self.definition = SimpleNamespace(
            name=f"{name.title()} Agent",
            description=f"{name} aciklamasi",
        )
        self.handle_task = AsyncMock(
            return_value=DepartmentResponse(
                department=department,
                answer=f"{name} yaniti",
                sources=[],
            )
        )


class _FakeDepartmentOrchestrator:
    def __init__(self, department: Department, answer: str):
        self.department = department
        self.handle = AsyncMock(
            return_value=DepartmentResponse(
                department=department,
                answer=answer,
                sources=[],
            )
        )


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
    announcement_agent.handle_task = AsyncMock(
        return_value=DepartmentResponse(
            department=Department.STUDENT_AFFAIRS,
            answer="Ilgili duyurular:\n1. Cap Basvurulari Acildi",
            sources=[
                RAGSource(
                    content="Cap basvurulari acildi.",
                    score=1.0,
                    metadata={"record_type": "announcement"},
                )
            ],
        )
    )
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=303)
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

    response = await orchestrator.handle_query("Cap basvurulari ne zaman?", context_id="ctx-announce")

    assert "Akademik program cevabi" in response.answer
    assert "Ilgili duyurular" in response.answer
    assert response.departments_involved == ["academic_programs"]
    assert any(source.metadata.get("record_type") == "announcement" for source in response.sources)
    announcement_agent.handle_task.assert_awaited_once()
    telemetry.record_agent_task.assert_awaited_once()


@pytest.mark.asyncio
async def test_main_orchestrator_uses_announcement_fallback_when_no_department_selected():
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

    assert response.answer == "announcement yaniti"
    announcement_agent.handle_task.assert_awaited_once()
    telemetry.record_agent_task.assert_awaited_once()
    telemetry.finalize_query_log.assert_awaited_once()
