import pytest
from unittest.mock import AsyncMock

from src.a2a import A2AQueryPayload, build_department_response_task, build_query_task
from src.core.config import settings
from src.core.constants import ConfidenceLevel, Department, RoutingStrategy, TaskType
from src.core.profiling import QueryProfiler, activate_profiler
from src.core.text_normalization import normalize_text
from src.db.schemas import DepartmentResponse, RoutingResult
import src.orchestrators.department_dispatch as department_dispatch_module
from src.orchestrators.department_dispatch import dispatch_multi_intent_subtasks
from src.orchestrators.main import MainOrchestrator
from src.orchestrators.multi_intent import (
    compose_multi_intent_fallback_answer,
    plan_multi_intent_query,
)
from src.orchestrators.response_utils import append_generation_summary


def test_multi_intent_planner_splits_compound_query_without_cap_date_leak():
    query = (
        "Bilgisayar Mühendisliği öğrencisiyim. Yaz okulunda ders almak istiyorum "
        "ama aynı dönemde zorunlu stajım da var; ayrıca harç borcum varsa ders kaydı "
        "yapabilir miyim, yaz okulunda kaç ders/kredi alabilirim, stajla çakışırsa "
        "ne olur ve bu süreçte ÇAP başvurusu ya da ders saydırma/önkoşul açısından "
        "dikkat etmem gereken akademik şartlar nelerdir?"
    )

    plan = plan_multi_intent_query(
        query,
        mode="pilot",
        student_department="Bilgisayar Mühendisliği",
    )

    ids = {subtask.subtask_id for subtask in plan.subtasks}
    assert plan.status == "planned"
    assert plan.is_actionable(threshold=0.72)
    assert "summer_school_conditions" in ids
    assert "internship_overlap" in ids
    assert "payment_debt_registration" in ids
    assert "prerequisite_check" in ids
    assert "course_transfer_or_exemption" in ids
    assert "cap_eligibility" in ids
    assert "academic_calendar_date" not in ids
    assert len(plan.subtasks) <= 6


def test_multi_intent_planner_leaves_single_intent_on_legacy_path():
    plan = plan_multi_intent_query(
        "ÇAP başvuru şartları nelerdir?",
        mode="pilot",
        student_department=None,
    )

    assert plan.status == "not_compound"
    assert not plan.is_actionable(threshold=0.72)


def test_multi_intent_fallback_composes_by_subtask_title():
    plan = plan_multi_intent_query(
        "Yaz okulunda stajla çakışırsa ders alabilir miyim ve harç borcum varsa kayıt yapabilir miyim?",
        mode="pilot",
    )
    responses = [
        DepartmentResponse(
            department=subtask.department,
            answer=f"{subtask.user_facing_title} cevabi",
            metadata={"multi_intent_subtask": subtask.to_metadata()},
        )
        for subtask in plan.subtasks[:2]
    ]

    answer = compose_multi_intent_fallback_answer(responses)
    normalized = normalize_text(answer)

    assert "yaz okulu" in normalized or "stajla cakisma" in normalized
    assert "cevabi" in normalized


class _FakeOrchestrator:
    def __init__(self, department: Department):
        self.department = department


class _FakeTransport:
    def __init__(self):
        self.calls = []

    async def dispatch(
        self,
        *,
        department,
        orchestrator,
        query,
        context_id,
        task_type,
        metadata,
        disable_specialist_llm,
    ):
        self.calls.append(
            {
                "department": department,
                "query": query,
                "task_type": task_type,
                "metadata": metadata,
                "disable_specialist_llm": disable_specialist_llm,
            }
        )
        request_task = build_query_task(
            A2AQueryPayload(
                query_text=query,
                context_id=context_id,
                task_type=task_type.value if task_type else None,
            )
        )
        return build_department_response_task(
            DepartmentResponse(
                department=department,
                answer=f"{department.value} subtask cevabi",
                metadata={"specialist_selection": {"selected_agent_id": "registration_agent"}},
            ),
            request_task=request_task,
            emitter_id=f"{department.value}_orchestrator",
            emitter_name=f"{department.value} Orchestrator",
        )


@pytest.mark.asyncio
async def test_dispatch_multi_intent_subtasks_uses_subtask_queries_and_metadata():
    plan = plan_multi_intent_query(
        "Yaz okulunda stajla çakışırsa ders alabilir miyim ve harç borcum varsa kayıt yapabilir miyim?",
        mode="pilot",
    )
    transport = _FakeTransport()

    responses = await dispatch_multi_intent_subtasks(
        department_orchestrators={
            Department.STUDENT_AFFAIRS: _FakeOrchestrator(Department.STUDENT_AFFAIRS),
            Department.ACADEMIC_PROGRAMS: _FakeOrchestrator(Department.ACADEMIC_PROGRAMS),
            Department.FINANCE: _FakeOrchestrator(Department.FINANCE),
        },
        plan=plan,
        context_id="ctx-1",
        metadata={"original_query": plan.original_query},
        transport=transport,
    )

    assert len(responses) == len(plan.subtasks)
    assert {call["query"] for call in transport.calls} == {
        subtask.effective_question for subtask in plan.subtasks
    }
    assert all(call["disable_specialist_llm"] for call in transport.calls)
    assert all(isinstance(call["task_type"], TaskType) for call in transport.calls)
    assert all("multi_intent_subtask" in response.metadata for response in responses)


def test_generation_summary_mentions_multi_intent_planner():
    response = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Alt baslik cevabi",
        metadata={
            "specialist_selection": {"selected_agent_id": "registration_agent"},
            "multi_intent_subtask": {
                "subtask_id": "payment_debt_registration",
                "user_facing_title": "Harç borcu ve kayıt",
            },
        },
    )

    answer = append_generation_summary(
        "Final cevap",
        [response],
        routing_strategy="parallel",
        agents_involved=["registration_agent", "orchestrator"],
    )

    normalized = normalize_text(answer)
    assert "alt baslik planlayici" in normalized
    assert "kayit isleri" in normalized


@pytest.mark.asyncio
async def test_main_orchestrator_pilot_uses_multi_intent_subtask_path(monkeypatch):
    monkeypatch.setattr(settings.multi_intent_planner, "mode", "pilot")
    monkeypatch.setattr(settings.capability_planner, "mode", "off")
    monkeypatch.setattr(settings.server, "response_debug_enabled", True)
    monkeypatch.setattr(settings.llm, "main_judge_enabled", False)

    router = AsyncMock()
    router.route = AsyncMock(
        return_value=RoutingResult(
            departments=[
                Department.STUDENT_AFFAIRS,
                Department.ACADEMIC_PROGRAMS,
                Department.FINANCE,
            ],
            confidence=0.9,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.PARALLEL,
            reasoning="compound query",
            task_type=TaskType.PROCEDURE_QUERY,
        )
    )
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=1001)
    telemetry.finalize_query_log = AsyncMock()
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(
        return_value=(
            "Yaz okulu:\nKaynaklara göre ders alma sınırına bakılmalıdır.\n\n"
            "Harç borcu ve kayıt:\nÖdeme yapılmadan ders kaydı yapılamaz."
        )
    )
    transport = _FakeTransport()
    monkeypatch.setattr(
        department_dispatch_module,
        "build_department_transport",
        lambda: transport,
    )

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={
            Department.STUDENT_AFFAIRS: _FakeOrchestrator(Department.STUDENT_AFFAIRS),
            Department.ACADEMIC_PROGRAMS: _FakeOrchestrator(Department.ACADEMIC_PROGRAMS),
            Department.FINANCE: _FakeOrchestrator(Department.FINANCE),
        },
        telemetry_service=telemetry,
        llm_service=llm_service,
    )

    profiler = QueryProfiler(label="multi-intent-test")
    with activate_profiler(profiler):
        response = await orchestrator.handle_query(
            (
                "Yaz okulunda ders almak istiyorum ama stajım da var; harç borcum varsa "
                "ders kaydı yapabilir miyim, ÇAP ve önkoşul açısından neye dikkat etmeliyim?"
            ),
            context_id="ctx-multi",
            disable_cache=True,
        )

    assert len(transport.calls) >= 4
    assert "Yaz okulu:" in response.answer
    assert "Harç borcu ve kayıt:" in response.answer
    assert response.routing_strategy == RoutingStrategy.PARALLEL.value
    assert response.diagnostics is not None
    assert response.diagnostics.answer_debug_report is not None
    assert response.diagnostics.answer_debug_report["multi_intent"]["applied"] is True
