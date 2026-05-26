"""Orchestrator testleri."""

import asyncio
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.a2a import A2AQueryPayload, build_department_response_task, build_query_task
from src.cache import question_cache
from src.capabilities.models import CapabilityAction
from src.core.config import settings
from src.core.answer_contracts import resolve_answer_contract
from src.core.constants import ConfidenceLevel, Department, RoutingStrategy, TaskType
from src.core.messages import CONTACT_SUGGESTION
from src.core.profiling import QueryProfiler, activate_profiler
from src.db.conversation_context import ConversationResolution
from src.db.events import EventLinkRecord, EventRecord
from src.db.schemas import DepartmentResponse, IntentAnalysis, RAGSource, RoutingResult
from src.agents.academic.curriculum_agent import CurriculumAgent
from src.orchestrators.department import DepartmentOrchestrator, _is_transport_timeout_error
from src.orchestrators.defaults import RemoteDepartmentTarget
from src.orchestrators.department_dispatch import dispatch_to_departments
from src.orchestrators.department_factories import build_student_affairs_orchestrator
from src.orchestrators.department_task_utils import build_specialist_task
from src.orchestrators.task_builders import build_department_request_task
from src.orchestrators.announcement_utils import request_announcement_response
from src.orchestrators.event_utils import request_event_response
from src.orchestrators.main import MainOrchestrator
import src.orchestrators.main as main_module
from src.orchestrators.query_policy import (
    augment_query_for_department,
    build_missing_slot_clarification_message,
    looks_like_announcement_query,
    looks_like_event_query,
    requires_academic_department_clarification,
    should_allow_announcement_latest_fallback,
    should_fetch_related_announcements,
    should_keep_announcement_follow_up,
    should_use_global_synthesis,
)
from src.orchestrators.response_utils import (
    build_response_filter_diagnostics,
    filter_low_confidence_responses,
)
from src.orchestrators.synthesis_utils import (
    build_evidence_packet_fallback_answer,
    build_global_synthesis_prompt,
)
from src.orchestrators.user_response_builders import build_final_user_response


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


def test_main_capability_param_bool_accepts_turkish_no():
    assert (
        MainOrchestrator._capability_param_bool(
            {"allow_latest_fallback": "hayır"},
            "allow_latest_fallback",
            default=True,
        )
        is False
    )


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


class _FakeDepartmentTransport:
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
                "context_id": context_id,
                "task_type": task_type,
                "metadata": dict(metadata or {}),
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
                answer=f"{department.value} transport cevabi",
                sources=[],
            ),
            request_task=request_task,
            emitter_id=f"{department.value}_transport",
            emitter_name=f"{department.value} Transport",
        )


def test_calendar_follow_up_does_not_stay_in_announcement_flow():
    assert should_keep_announcement_follow_up("Takvimde hangi tarihler verilmis?") is False
    assert should_keep_announcement_follow_up("Hangi tarihler?") is False


def test_related_announcements_not_fetched_for_calendar_follow_up():
    assert should_fetch_related_announcements("CAP takvimde hangi tarihler verilmis?") is False


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
async def test_department_orchestrator_passes_conversation_metadata_without_unused_pii():
    registration = _FakeAgent("registration", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    orchestrator = DepartmentOrchestrator(
        department=Department.STUDENT_AFFAIRS,
        agents={TaskType.REGISTRATION_QUERY: registration},
        fallback_agent=registration,
        telemetry_service=telemetry,
    )

    await orchestrator.handle(
        query_text="CAP icin son tarih ne zaman?",
        context_id="ctx-meta-1",
        task_type=TaskType.REGISTRATION_QUERY,
        metadata={
            "original_query": "Son tarih ne zaman?",
            "resolved_query": "CAP icin son tarih ne zaman?",
            "conversation_is_follow_up": True,
            "conversation_topic": "CAP / Cift Anadal",
            "conversation_source_refs": ["yonerge_cift_anadal_yandal.pdf"],
            "student_id": 42,
            "student_number": "20210001",
            "student_full_name": "Ahmet Yilmaz",
            "trace_id": "trace-department-1",
            "span_id": "span-department-1",
        },
    )

    task = registration.handle_task.await_args.args[0]
    assert task.metadata["conversation_is_follow_up"] is True
    assert task.metadata["conversation_topic"] == "CAP / Cift Anadal"
    assert task.metadata["conversation_source_refs"] == ["yonerge_cift_anadal_yandal.pdf"]
    assert task.metadata["student_id"] == 42
    assert "student_number" not in task.metadata
    assert "student_full_name" not in task.metadata
    assert task.metadata["trace_id"] == "trace-department-1"
    assert task.metadata["parent_span_id"] == "span-department-1"
    assert task.metadata["span_id"] != "span-department-1"


@pytest.mark.asyncio
async def test_dispatch_to_departments_raises_when_all_parallel_branches_fail():
    failed_orchestrator = SimpleNamespace(
        department=Department.STUDENT_AFFAIRS,
        handle_task=AsyncMock(side_effect=RuntimeError("student affairs failed")),
    )
    invalid_orchestrator = SimpleNamespace(
        department=Department.FINANCE,
        handle_task=AsyncMock(return_value=SimpleNamespace(artifacts=[])),
    )

    routing = RoutingResult(
        departments=[Department.STUDENT_AFFAIRS, Department.FINANCE],
        confidence=0.81,
        confidence_level=ConfidenceLevel.HIGH,
        strategy=RoutingStrategy.PARALLEL,
        reasoning="Coklu departman sorgusu",
        task_type=TaskType.REGISTRATION_QUERY,
    )

    with pytest.raises(RuntimeError, match="gecerli yanit alinamadi"):
        await dispatch_to_departments(
            department_orchestrators={
                Department.STUDENT_AFFAIRS: failed_orchestrator,
                Department.FINANCE: invalid_orchestrator,
            },
            query="Yatay gecis harc durumu nedir?",
            context_id="ctx-dispatch-fail",
            routing=routing,
            metadata={},
        )


@pytest.mark.asyncio
async def test_dispatch_to_departments_uses_transport_abstraction():
    orchestrator = SimpleNamespace(
        department=Department.STUDENT_AFFAIRS,
        handle_task=AsyncMock(side_effect=AssertionError("direct call should not be used")),
    )
    routing = RoutingResult(
        departments=[Department.STUDENT_AFFAIRS],
        confidence=0.88,
        confidence_level=ConfidenceLevel.HIGH,
        strategy=RoutingStrategy.DIRECT,
        reasoning="Kayit sorgusu",
        task_type=TaskType.REGISTRATION_QUERY,
    )
    transport = _FakeDepartmentTransport()

    responses = await dispatch_to_departments(
        department_orchestrators={Department.STUDENT_AFFAIRS: orchestrator},
        query="Ders kaydi nasil yapilir?",
        context_id="ctx-a2a-transport",
        routing=routing,
        metadata={},
        transport=transport,
    )

    assert responses[0].answer == "student_affairs transport cevabi"
    assert transport.calls[0]["department"] == Department.STUDENT_AFFAIRS
    orchestrator.handle_task.assert_not_awaited()


@pytest.mark.asyncio
async def test_dispatch_to_departments_recomputes_branch_task_types_per_department():
    student_orchestrator = SimpleNamespace(
        department=Department.STUDENT_AFFAIRS,
        handle_task=AsyncMock(),
    )
    finance_orchestrator = SimpleNamespace(
        department=Department.FINANCE,
        handle_task=AsyncMock(),
    )
    academic_orchestrator = SimpleNamespace(
        department=Department.ACADEMIC_PROGRAMS,
        handle_task=AsyncMock(),
    )
    routing = RoutingResult(
        departments=[
            Department.ACADEMIC_PROGRAMS,
            Department.STUDENT_AFFAIRS,
            Department.FINANCE,
        ],
        confidence=0.91,
        confidence_level=ConfidenceLevel.HIGH,
        strategy=RoutingStrategy.PARALLEL,
        reasoning="Uluslararasi kayit ve ucret sorgusu",
        task_type=TaskType.TUITION_QUERY,
    )
    transport = _FakeDepartmentTransport()

    await dispatch_to_departments(
        department_orchestrators={
            Department.ACADEMIC_PROGRAMS: academic_orchestrator,
            Department.STUDENT_AFFAIRS: student_orchestrator,
            Department.FINANCE: finance_orchestrator,
        },
        query=(
            "Uluslararasi ogrenci kayit olurken ogrenim ucretini nereye yatirir "
            "ve ikamet belgesi gerekir mi?"
        ),
        context_id="ctx-branch-task-types",
        routing=routing,
        metadata={},
        transport=transport,
    )

    calls_by_department = {
        call["department"]: call["task_type"]
        for call in transport.calls
    }

    assert calls_by_department[Department.FINANCE] == TaskType.TUITION_QUERY
    assert calls_by_department[Department.STUDENT_AFFAIRS] == TaskType.REGISTRATION_QUERY
    assert calls_by_department[Department.ACADEMIC_PROGRAMS] == TaskType.PROCEDURE_QUERY
    assert all(call["disable_specialist_llm"] is True for call in transport.calls)


@pytest.mark.asyncio
async def test_branch_dispatch_gate_prunes_academic_for_student_affairs_policy_process():
    student_orchestrator = SimpleNamespace(
        department=Department.STUDENT_AFFAIRS,
        handle_task=AsyncMock(),
    )
    academic_orchestrator = SimpleNamespace(
        department=Department.ACADEMIC_PROGRAMS,
        handle_task=AsyncMock(),
    )
    routing = RoutingResult(
        departments=[Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS],
        confidence=0.91,
        confidence_level=ConfidenceLevel.HIGH,
        strategy=RoutingStrategy.PARALLEL,
        reasoning="Muafiyet basvuru sureci",
        task_type=TaskType.REGISTRATION_QUERY,
    )
    transport = _FakeDepartmentTransport()

    await dispatch_to_departments(
        department_orchestrators={
            Department.STUDENT_AFFAIRS: student_orchestrator,
            Department.ACADEMIC_PROGRAMS: academic_orchestrator,
        },
        query="Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?",
        context_id="ctx-branch-gate-student-policy",
        routing=routing,
        metadata={
            "capability_planner": {
                "action": {
                    "capability": "student_affairs.policy_lookup",
                    "params": {
                        "topic": "muafiyet basvurusu",
                        "question_type": "deadline",
                    },
                }
            },
            "source_owner": {"primary": "student_affairs_policy"},
        },
        transport=transport,
    )

    assert [call["department"] for call in transport.calls] == [Department.STUDENT_AFFAIRS]
    gate = transport.calls[0]["metadata"]["branch_dispatch_gate"]
    assert gate["applied"] is True
    assert gate["kept_departments"] == ["student_affairs"]
    assert gate["pruned_departments"] == ["academic_programs"]
    assert transport.calls[0]["disable_specialist_llm"] is False


@pytest.mark.asyncio
async def test_branch_dispatch_gate_keeps_academic_for_student_affairs_policy_conditions():
    student_orchestrator = SimpleNamespace(
        department=Department.STUDENT_AFFAIRS,
        handle_task=AsyncMock(),
    )
    academic_orchestrator = SimpleNamespace(
        department=Department.ACADEMIC_PROGRAMS,
        handle_task=AsyncMock(),
    )
    routing = RoutingResult(
        departments=[Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS],
        confidence=0.91,
        confidence_level=ConfidenceLevel.HIGH,
        strategy=RoutingStrategy.PARALLEL,
        reasoning="CAP basvuru sureci ve kosullari",
        task_type=TaskType.REGISTRATION_QUERY,
    )
    transport = _FakeDepartmentTransport()

    await dispatch_to_departments(
        department_orchestrators={
            Department.STUDENT_AFFAIRS: student_orchestrator,
            Department.ACADEMIC_PROGRAMS: academic_orchestrator,
        },
        query="CAP basvurusu nasil yapilir ve GNO sarti nedir?",
        context_id="ctx-branch-gate-cap",
        routing=routing,
        metadata={
            "capability_planner": {
                "action": {
                    "capability": "student_affairs.policy_lookup",
                    "params": {
                        "topic": "cift anadal basvuru sartlari",
                        "question_type": "conditions",
                    },
                    "answer_contract": {"must_answer": ["GNO kosulu", "basvuru sureci"]},
                }
            },
            "source_owner": {"primary": "student_affairs_policy"},
        },
        transport=transport,
    )

    calls_by_department = {call["department"]: call for call in transport.calls}
    assert set(calls_by_department) == {Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS}
    assert calls_by_department[Department.ACADEMIC_PROGRAMS]["task_type"] == TaskType.PROCEDURE_QUERY
    gate = calls_by_department[Department.STUDENT_AFFAIRS]["metadata"]["branch_dispatch_gate"]
    assert gate["reason"] == "student_affairs_policy_contract_gate"
    assert gate["pruned_departments"] == []


@pytest.mark.asyncio
async def test_branch_dispatch_gate_restores_student_affairs_owner_primary_branch():
    student_orchestrator = SimpleNamespace(
        department=Department.STUDENT_AFFAIRS,
        handle_task=AsyncMock(),
    )
    academic_orchestrator = SimpleNamespace(
        department=Department.ACADEMIC_PROGRAMS,
        handle_task=AsyncMock(),
    )
    routing = RoutingResult(
        departments=[Department.ACADEMIC_PROGRAMS],
        confidence=0.9,
        confidence_level=ConfidenceLevel.HIGH,
        strategy=RoutingStrategy.DIRECT,
        reasoning="CAP not ortalamasi onceki akademik kaynak baglamina baglandi",
        task_type=TaskType.PROCEDURE_QUERY,
    )
    transport = _FakeDepartmentTransport()

    await dispatch_to_departments(
        department_orchestrators={
            Department.STUDENT_AFFAIRS: student_orchestrator,
            Department.ACADEMIC_PROGRAMS: academic_orchestrator,
        },
        query="CAP basvurusu icin not ortalamasi kac olmali?",
        context_id="ctx-branch-restore-student-owner",
        routing=routing,
        metadata={
            "capability_planner": {
                "action": {
                    "capability": "student_affairs.policy_lookup",
                    "params": {
                        "topic": "CAP / Cift Anadal",
                        "question_type": "eligibility",
                    },
                    "answer_contract": {"must_answer": ["GNO kosulu"]},
                }
            },
            "source_owner": {"primary": "student_affairs_policy"},
        },
        transport=transport,
    )

    calls_by_department = {call["department"]: call for call in transport.calls}
    assert set(calls_by_department) == {Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS}
    assert all(call["disable_specialist_llm"] is True for call in transport.calls)
    gate = calls_by_department[Department.STUDENT_AFFAIRS]["metadata"]["branch_dispatch_gate"]
    assert gate["applied"] is True
    assert gate["original_departments"] == ["academic_programs"]
    assert gate["restored_departments"] == ["student_affairs"]
    assert gate["router_departments"] == ["academic_programs"]
    assert gate["restored_primary_department"] == "student_affairs"
    assert gate["support_departments"] == ["academic_programs", "finance"]
    assert gate["owner_routing_policy"]["reason"] == "student_affairs_policy_primary"
    assert gate["kept_departments"] == ["student_affairs", "academic_programs"]
    assert gate["pruned_departments"] == []
    assert gate["reason"] == "student_affairs_policy_contract_gate"
    assert calls_by_department[Department.STUDENT_AFFAIRS]["task_type"] == TaskType.PROCEDURE_QUERY
    assert calls_by_department[Department.ACADEMIC_PROGRAMS]["task_type"] == TaskType.PROCEDURE_QUERY


@pytest.mark.asyncio
async def test_branch_dispatch_gate_keeps_academic_support_for_special_long_graduation_akts():
    student_orchestrator = SimpleNamespace(
        department=Department.STUDENT_AFFAIRS,
        handle_task=AsyncMock(),
    )
    academic_orchestrator = SimpleNamespace(
        department=Department.ACADEMIC_PROGRAMS,
        handle_task=AsyncMock(),
    )
    routing = RoutingResult(
        departments=[Department.ACADEMIC_PROGRAMS],
        confidence=0.9,
        confidence_level=ConfidenceLevel.HIGH,
        strategy=RoutingStrategy.DIRECT,
        reasoning="Dis hekimligi akademik program sorgusu",
        task_type=TaskType.PROCEDURE_QUERY,
    )
    transport = _FakeDepartmentTransport()
    contract = resolve_answer_contract(
        "Dis hekimliginden mezun olmak icin kac AKTS lazim?"
    )
    assert contract is not None

    await dispatch_to_departments(
        department_orchestrators={
            Department.STUDENT_AFFAIRS: student_orchestrator,
            Department.ACADEMIC_PROGRAMS: academic_orchestrator,
        },
        query="Dis hekimliginden mezun olmak icin kac AKTS lazim?",
        context_id="ctx-branch-special-long-graduation-akts",
        routing=routing,
        metadata={
            "capability_planner": {
                "action": {
                    "capability": contract.capability,
                    "intent": contract.contract_id,
                    "params": {
                        "policy_facet": contract.facet,
                        "answer_contract": contract.to_metadata(),
                    },
                    "answer_contract": contract.to_metadata(),
                }
            },
            "source_owner": {"primary": contract.source_owner},
        },
        transport=transport,
    )

    calls_by_department = {call["department"]: call for call in transport.calls}
    assert set(calls_by_department) == {Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS}
    gate = calls_by_department[Department.STUDENT_AFFAIRS]["metadata"]["branch_dispatch_gate"]
    assert gate["reason"] == "graduation_akts_program_specific_support_branch"
    assert gate["restored_departments"] == ["student_affairs"]


@pytest.mark.asyncio
async def test_branch_dispatch_gate_prunes_student_affairs_for_international_policy():
    student_orchestrator = SimpleNamespace(
        department=Department.STUDENT_AFFAIRS,
        handle_task=AsyncMock(),
    )
    academic_orchestrator = SimpleNamespace(
        department=Department.ACADEMIC_PROGRAMS,
        handle_task=AsyncMock(),
    )
    routing = RoutingResult(
        departments=[Department.ACADEMIC_PROGRAMS, Department.STUDENT_AFFAIRS],
        confidence=0.9,
        confidence_level=ConfidenceLevel.HIGH,
        strategy=RoutingStrategy.PARALLEL,
        reasoning="Uluslararasi kayit belgeleri",
        task_type=TaskType.REGISTRATION_QUERY,
    )
    transport = _FakeDepartmentTransport()

    await dispatch_to_departments(
        department_orchestrators={
            Department.ACADEMIC_PROGRAMS: academic_orchestrator,
            Department.STUDENT_AFFAIRS: student_orchestrator,
        },
        query="Yabanci ogrenci kayit belgeleri ve ikamet izni icin neler gerekir?",
        context_id="ctx-branch-gate-international",
        routing=routing,
        metadata={
            "capability_planner": {
                "action": {"capability": "international.policy_lookup"}
            },
            "source_owner": {"primary": "international_policy"},
        },
        transport=transport,
    )

    assert [call["department"] for call in transport.calls] == [Department.ACADEMIC_PROGRAMS]
    gate = transport.calls[0]["metadata"]["branch_dispatch_gate"]
    assert gate["applied"] is True
    assert gate["pruned_departments"] == ["student_affairs"]


@pytest.mark.asyncio
async def test_dispatch_keeps_specialist_llm_disabled_for_multi_department_force_llm():
    student_orchestrator = SimpleNamespace(
        department=Department.STUDENT_AFFAIRS,
        handle_task=AsyncMock(),
    )
    finance_orchestrator = SimpleNamespace(
        department=Department.FINANCE,
        handle_task=AsyncMock(),
    )
    routing = RoutingResult(
        departments=[Department.STUDENT_AFFAIRS, Department.FINANCE],
        confidence=0.91,
        confidence_level=ConfidenceLevel.HIGH,
        strategy=RoutingStrategy.PARALLEL,
        reasoning="Kayit ve ucret birlikte soruldu",
        task_type=TaskType.PROCEDURE_QUERY,
    )
    transport = _FakeDepartmentTransport()

    await dispatch_to_departments(
        department_orchestrators={
            Department.STUDENT_AFFAIRS: student_orchestrator,
            Department.FINANCE: finance_orchestrator,
        },
        query="Kayit yenileme ve harc odeme sureci nasil isler?",
        context_id="ctx-multi-force-llm",
        routing=routing,
        metadata={"force_llm_synthesis": True},
        transport=transport,
    )

    assert len(transport.calls) == 2
    assert all(call["disable_specialist_llm"] is True for call in transport.calls)


@pytest.mark.asyncio
async def test_dispatch_allows_force_llm_for_single_department():
    student_orchestrator = SimpleNamespace(
        department=Department.STUDENT_AFFAIRS,
        handle_task=AsyncMock(),
    )
    routing = RoutingResult(
        departments=[Department.STUDENT_AFFAIRS],
        confidence=0.9,
        confidence_level=ConfidenceLevel.HIGH,
        strategy=RoutingStrategy.DIRECT,
        reasoning="Tek departmanli surec sorusu",
        task_type=TaskType.REGISTRATION_QUERY,
    )
    transport = _FakeDepartmentTransport()

    await dispatch_to_departments(
        department_orchestrators={Department.STUDENT_AFFAIRS: student_orchestrator},
        query="Ders kaydi surecini ayrintili anlatir misin?",
        context_id="ctx-single-force-llm",
        routing=routing,
        metadata={"force_llm_synthesis": True},
        transport=transport,
    )

    assert len(transport.calls) == 1
    assert transport.calls[0]["disable_specialist_llm"] is False


@pytest.mark.asyncio
async def test_student_affairs_factory_prefers_registration_agent_for_admin_workflows():
    registration = _FakeAgent("registration", Department.STUDENT_AFFAIRS)
    graduation = _FakeAgent("graduation", Department.STUDENT_AFFAIRS)
    internship = _FakeAgent("internship", Department.STUDENT_AFFAIRS)
    student_life = _FakeAgent("student_life", Department.STUDENT_AFFAIRS)
    orchestrator = build_student_affairs_orchestrator(
        [registration, graduation, internship, student_life]
    )

    assert (
        orchestrator._select_agent(
            TaskType.PROCEDURE_QUERY,
            "Sinav notuma itiraz etmek istiyorum.",
        ).agent_id
        == "registration_agent"
    )
    assert (
        orchestrator._select_agent(
            TaskType.PROCEDURE_QUERY,
            "Staj sureci nasil isler?",
            metadata={
                "capability_planner": {
                    "action": {
                        "capability": "student_affairs.policy_lookup",
                        "params": {"topic": "staj"},
                    }
                },
                "source_owner": {"primary": "student_affairs_policy"},
            },
        ).agent_id
        == "internship_agent"
    )


@pytest.mark.asyncio
async def test_main_orchestrator_combines_parallel_department_responses(monkeypatch):
    monkeypatch.setattr(settings.capability_planner, "mode", "off")

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
    assert response.generation_modes
    telemetry.create_query_log.assert_awaited_once()
    telemetry.finalize_query_log.assert_awaited_once()


def test_main_orchestrator_http_mode_uses_remote_department_targets(monkeypatch):
    monkeypatch.setattr(settings.a2a, "mode", "http")

    orchestrator = MainOrchestrator(
        router=AsyncMock(),
        announcement_agent=_FakeAgent("announcement", Department.STUDENT_AFFAIRS),
        telemetry_service=AsyncMock(),
    )

    assert set(orchestrator.department_orchestrators) == set(Department)
    assert all(
        isinstance(target, RemoteDepartmentTarget)
        for target in orchestrator.department_orchestrators.values()
    )


@pytest.mark.asyncio
async def test_main_orchestrator_filters_related_announcements_when_strong_answer_exists():
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
        "Akademik program cevabi: CAP basvurusu icin not ortalamasi en az 3,00 olmali ve ilk %20 kosulu saglanmalidir.",
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
    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={
            Department.ACADEMIC_PROGRAMS: academic_orchestrator,
        },
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
    )

    response = await orchestrator.handle_query("Cap basvurulari acildi mi?", context_id="ctx-announce")

    assert "Akademik program cevabi" in response.answer
    assert "Ilgili duyurular" not in response.answer
    assert "Duyuru kaydi:" not in response.answer
    assert response.departments_involved == ["academic_programs"]
    assert all(source.metadata.get("record_type") != "announcement" for source in response.sources)
    announcement_agent.handle_task.assert_awaited_once()
    telemetry.record_agent_task.assert_awaited_once()


def test_should_fetch_related_announcements_requires_subject_signal():
    assert should_fetch_related_announcements(
        "Bilgisayar muhendisligi ara sinav programi nereden takip edilir?"
    )
    assert not should_fetch_related_announcements("Ders kaydi ne zaman basliyor?")
    assert not should_fetch_related_announcements(
        "Kayit yenileme ucreti ne kadar ve ne zaman yapilir?"
    )
    assert not should_fetch_related_announcements("Final sinavlari ne zaman?")
    assert not should_fetch_related_announcements(
        "Final sinavlarinin girilmesinin son gunu ne zaman?"
    )


def test_announcement_latest_fallback_is_only_for_generic_latest_queries():
    assert looks_like_announcement_query("Sinav programi var mi?")
    assert looks_like_announcement_query("Bahar donemi final sinavi programi")
    assert looks_like_announcement_query("Guncel duyur")
    assert should_allow_announcement_latest_fallback("Guncel duyurular neler?")
    assert not should_allow_announcement_latest_fallback("Sinav takvimi var mi?")
    assert not should_allow_announcement_latest_fallback("CAP basvurusu ile ilgili son duyurular neler?")
    assert not should_allow_announcement_latest_fallback("Cift anadal duyurularini istiyorum")
    assert not looks_like_announcement_query("Final sinavlarinin girilmesinin son gunu ne zaman?")


def test_transport_timeout_errors_are_detected_for_no_fallback_policy():
    assert _is_transport_timeout_error("a2a_transport_timeout")
    assert _is_transport_timeout_error("httpx.ReadTimeout")
    assert not _is_transport_timeout_error("a2a_transport_failed")


def test_specialist_task_preserves_retrieval_execution_metadata():
    policy = {
        "schema": "omu.retrieval_execution_policy.v1",
        "branch_role": "primary",
        "reranker_candidate_limit": 8,
        "max_multi_query_variants": 1,
    }

    payload, task = build_specialist_task(
        query_text="Yatay gecis muafiyet basvurusu ne zaman?",
        context_id="ctx-retrieval-policy",
        task_type=TaskType.PROCEDURE_QUERY,
        metadata={
            "branch_role": "primary",
            "retrieval_execution_policy": policy,
            "source_owner": {"primary": "student_affairs_policy"},
        },
    )

    assert payload.branch_role == "primary"
    assert payload.retrieval_execution_policy == policy
    assert task.metadata["branch_role"] == "primary"
    assert task.metadata["retrieval_execution_policy"]["reranker_candidate_limit"] == 8


def test_department_request_task_preserves_retrieval_execution_metadata():
    policy = {
        "schema": "omu.retrieval_execution_policy.v1",
        "branch_role": "support",
        "top_k": 4,
        "reranker_candidate_limit": 4,
        "max_multi_query_variants": 0,
    }

    task = build_department_request_task(
        department=Department.ACADEMIC_PROGRAMS,
        query="Yatay gecis muafiyet basvurusu ne zaman?",
        context_id="ctx-branch-policy",
        task_type=TaskType.PROCEDURE_QUERY,
        metadata={
            "branch_role": "support",
            "retrieval_execution_policy": policy,
            "source_owner": {"primary": "student_affairs_policy"},
            "branch_dispatch_gate": {"schema": "omu.branch_dispatch_gate.v1"},
        },
    )

    assert task.metadata["branch_role"] == "support"
    assert task.metadata["retrieval_execution_policy"]["top_k"] == 4
    assert task.metadata["retrieval_execution_policy"]["reranker_candidate_limit"] == 4


def test_announcement_follow_up_stops_on_clear_topic_shift():
    assert should_keep_announcement_follow_up("Detay linki var mi?")
    assert should_keep_announcement_follow_up("2. duyuruyu ozetle")
    assert not should_keep_announcement_follow_up("Staj basvurusu nasil yapilir?")
    assert not should_keep_announcement_follow_up("Kayit tarihleri ne zaman?")
    assert not should_keep_announcement_follow_up("Final sinavlari ne zaman?")
    assert not should_allow_announcement_latest_fallback("Sinav programi var mi?")


def test_response_debug_summary_can_be_hidden(monkeypatch):
    monkeypatch.setattr(settings.server, "response_debug_enabled", False)
    response = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Kimlik kartı için başvuru yapmalısınız.",
        sources=[
            RAGSource(
                content="Kimlik kartı yönergesi",
                score=0.9,
                metadata={"source": "kimlik_kartı_yönergesi.pdf"},
            )
        ],
        generation_mode="rag",
    )

    user_response = build_final_user_response(
        answer=response.answer,
        responses=[response],
        department_responses=[response],
        context_id="ctx-debug-hidden",
        response_time_ms=1.0,
        student_full_name=None,
    )

    assert "Üretim Türü:" not in user_response.answer
    assert "Uretim Turu:" not in user_response.answer
    assert "Kaynak Özeti:" not in user_response.answer
    assert "Kaynak Ozeti:" not in user_response.answer


def test_finance_query_augmentation_does_not_override_explicit_fee_unit():
    query = "Dis hekimligi donem ucreti ne kadar Turk ogrenciyim"

    augmented = augment_query_for_department(
        Department.FINANCE,
        query,
        {"student_faculty": "Muhendislik Fakultesi"},
    )

    assert augmented == query


def test_finance_query_augmentation_uses_profile_for_generic_fee_query():
    augmented = augment_query_for_department(
        Department.FINANCE,
        "Donem ucreti ne kadar?",
        {"student_faculty": "Muhendislik Fakultesi"},
    )

    assert augmented == "Muhendislik Fakultesi icin: Donem ucreti ne kadar?"


def test_schedule_group_formatter_does_not_truncate_rows():
    rows = [
        {
            "day_of_week": "Pazartesi",
            "start_time": f"{8 + index:02d}:15:00",
            "end_time": f"{9 + index:02d}:00:00",
            "course_name": f"Ders {index}",
            "schedule_group": "1. sinif",
            "classroom": "Z01",
            "instructor": "",
        }
        for index in range(7)
    ]

    lines = CurriculumAgent._format_schedule_rows_by_group(
        rows,
        max_rows_per_group=len(rows),
    )

    assert sum(1 for line in lines if line.startswith("- ")) == 7
    assert not any("satir daha" in line for line in lines)


def test_schedule_term_extraction_maps_curriculum_semester_parity():
    assert CurriculumAgent._extract_schedule_term_key("7. yariyil ders programi") == "guz"
    assert CurriculumAgent._extract_schedule_term_key("8. yariyil ders programi") == "bahar"
    assert CurriculumAgent._extract_schedule_term_key("4. sinif ilk donem ders programi") == "guz"


def test_schedule_term_selection_uses_odd_semester_as_fall():
    rows = [
        {
            "academic_year": "2025-2026",
            "term": "bahar",
            "course_name": "Bahar Dersi",
        },
        {
            "academic_year": "2025-2026",
            "term": "guz",
            "course_name": "Guz Dersi",
        },
    ]

    selected, term_context = CurriculumAgent._select_schedule_rows_for_term(
        "Bilgisayar muhendisligi 7. yariyil dersleri neler?",
        rows,
    )

    assert [row["course_name"] for row in selected] == ["Guz Dersi"]
    assert term_context == "2025-2026 guz"


@pytest.mark.asyncio
async def test_main_records_department_context_required_clarification():
    router = AsyncMock()
    router.route = AsyncMock(
        return_value=RoutingResult(
            departments=[Department.ACADEMIC_PROGRAMS],
            confidence=0.9,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.DIRECT,
            reasoning="Akademik program sorusu",
            task_type=TaskType.COURSE_QUERY,
        )
    )
    clarification = DepartmentResponse(
        department=Department.ACADEMIC_PROGRAMS,
        answer="Fakulte, bolum veya program bilgisini belirtir misiniz?",
        success=False,
        error="department_context_required",
    )

    async def _handle_academic_task(task, *args, **kwargs):
        return build_department_response_task(
            clarification,
            request_task=task,
            emitter_id="academic_programs_orchestrator",
            emitter_name="Academic Programs Orchestrator",
        )

    academic_orchestrator = SimpleNamespace(
        department=Department.ACADEMIC_PROGRAMS,
        handle_task=AsyncMock(side_effect=_handle_academic_task),
    )
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=705)
    telemetry.finalize_query_log = AsyncMock()
    conversation_service = AsyncMock()
    conversation_service.resolve_query = AsyncMock(
        return_value=ConversationResolution(
            original_query="4. Sinif ilk donem dersleri hakkinda bilgi almak istiyorum",
            effective_query="4. Sinif ilk donem dersleri hakkinda bilgi almak istiyorum",
            is_follow_up=False,
            used_context=False,
            active_topic="Mufredat ve Ders Yapisi",
            department_hints=[],
            source_hints=[],
        )
    )
    conversation_service.record_turn = AsyncMock()

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={Department.ACADEMIC_PROGRAMS: academic_orchestrator},
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
        conversation_service=conversation_service,
    )

    response = await orchestrator.handle_query(
        "4. Sinif ilk donem dersleri hakkinda bilgi almak istiyorum",
        context_id="ctx-dept-clarification-record",
    )

    assert "program bilgisini" in response.answer
    conversation_service.record_turn.assert_awaited_once()
    record_kwargs = conversation_service.record_turn.await_args.kwargs
    assert record_kwargs["user_query"] == "4. Sinif ilk donem dersleri hakkinda bilgi almak istiyorum"
    assert record_kwargs["resolved_query"] == "4. Sinif ilk donem dersleri hakkinda bilgi almak istiyorum"
    assert record_kwargs["task_type"] == TaskType.COURSE_QUERY
    assert record_kwargs["departments"] == [Department.ACADEMIC_PROGRAMS.value]


def test_build_missing_slot_clarification_uses_llm_slot_metadata():
    intent = IntentAnalysis(
        primary_intent="tuition",
        required_slots=["student_type", "faculty_or_program"],
        missing_slots=["student_type"],
    )

    message = build_missing_slot_clarification_message(intent=intent, metadata={})

    assert message is not None
    assert "Türk öğrenci" in message
    assert "uluslararası öğrenci" in message


def test_build_missing_slot_clarification_ignores_student_type_for_cap_query():
    intent = IntentAnalysis(
        primary_intent="cap_yap",
        required_slots=["student_type"],
        missing_slots=["student_type"],
    )

    message = build_missing_slot_clarification_message(
        intent=intent,
        metadata={},
        query="CAP'a basvurabilir miyim?",
    )

    assert message is None


def test_build_missing_slot_clarification_keeps_student_type_for_fee_amount_query():
    intent = IntentAnalysis(
        primary_intent="tuition",
        required_slots=["student_type"],
        missing_slots=["student_type"],
    )

    message = build_missing_slot_clarification_message(
        intent=intent,
        metadata={},
        query="Fizik ogretmenligi ucreti ne kadar?",
    )

    assert message is not None
    assert "Türk öğrenci" in message


def test_build_missing_slot_clarification_ignores_student_type_for_hypothetical_fee_condition():
    intent = IntentAnalysis(
        primary_intent="tuition",
        required_slots=["student_type"],
        missing_slots=["student_type"],
    )

    message = build_missing_slot_clarification_message(
        intent=intent,
        metadata={},
        query="CAP basvurusu icin harc borcum olsaydi basvurabilir miydim?",
    )

    assert message is None


def test_build_missing_slot_clarification_ignores_fee_program_slots_for_payment_condition():
    intent = IntentAnalysis(
        primary_intent="tuition",
        required_slots=["student_type", "faculty_or_program"],
        missing_slots=["student_type", "faculty_or_program"],
    )

    message = build_missing_slot_clarification_message(
        intent=intent,
        metadata={},
        query="Harc borcum olsaydi basvurabilir miydim?",
    )

    assert message is None


def test_build_missing_slot_clarification_ignores_application_type_when_query_names_cap():
    intent = IntentAnalysis(
        primary_intent="unknown",
        required_slots=["application_type"],
        missing_slots=["application_type"],
    )

    message = build_missing_slot_clarification_message(
        intent=intent,
        metadata={},
        query="CAP basvurusu tarihleri ne zaman?",
    )

    assert message is None


def test_build_missing_slot_clarification_ignores_application_type_for_fee_debt_policy():
    intent = IntentAnalysis(
        primary_intent="unknown",
        required_slots=["application_type"],
        missing_slots=["application_type"],
    )

    message = build_missing_slot_clarification_message(
        intent=intent,
        metadata={},
        query="Tarih degil harc borcu soruyorum yaz okulu icin",
    )

    assert message is None


def test_build_missing_slot_clarification_ignores_session_filled_slots():
    intent = IntentAnalysis(
        primary_intent="tuition",
        required_slots=["student_type"],
        missing_slots=["student_type"],
    )

    message = build_missing_slot_clarification_message(
        intent=intent,
        metadata={"student_type": "Turk ogrenci"},
    )

    assert message is None


def test_build_missing_slot_clarification_ignores_academic_calendar_slots():
    intent = IntentAnalysis(
        primary_intent="academic_calendar",
        required_slots=["faculty_or_program"],
        missing_slots=["faculty_or_program"],
    )

    message = build_missing_slot_clarification_message(intent=intent, metadata={})

    assert message is None


def test_build_missing_slot_clarification_uses_program_named_in_query():
    intent = IntentAnalysis(
        primary_intent="summer_school",
        required_slots=["faculty_or_program"],
        missing_slots=["faculty_or_program"],
    )

    message = build_missing_slot_clarification_message(
        intent=intent,
        metadata={},
        query="Fizik ogretmenligi bolumu ogrencisiyim yaz okuluna katilabilir miyim?",
    )

    assert message is None


def test_build_missing_slot_clarification_ignores_program_for_international_registration_docs():
    intent = IntentAnalysis(
        primary_intent="international_registration",
        required_slots=["faculty_or_program"],
        missing_slots=["faculty_or_program"],
    )

    message = build_missing_slot_clarification_message(
        intent=intent,
        metadata={},
        query="Uluslararasi ogrenci olarak kayit icin hangi belgeler gerekir?",
    )

    assert message is None


def test_academic_department_clarification_does_not_trigger_for_application_eligibility():
    assert not requires_academic_department_clarification(
        query="Capa basvurabilir miyim?",
        departments=[Department.ACADEMIC_PROGRAMS],
        task_type=None,
        student_department=None,
    )


def test_main_records_academic_department_clarification_for_followup_slot_answer():
    import inspect

    source = inspect.getsource(MainOrchestrator.handle_query)
    assert "record_academic_department_clarification" in source
    assert "ACADEMIC_DEPARTMENT_CLARIFICATION_MESSAGE" in source


def test_general_akts_rule_detector_handles_tamamlamali_wording():
    from src.agents.student.graduation_utils import is_general_akts_rule_query

    assert is_general_akts_rule_query("Onlisans ogrencileri kac AKTS tamamlamali?")


@pytest.mark.asyncio
async def test_announcement_http_mode_keeps_remote_failure_without_local_fallback(monkeypatch):
    import src.orchestrators.announcement_utils as announcement_utils_module

    class _FailingCapabilityTransport:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        async def dispatch(self, *, capability, payload):
            return DepartmentResponse(
                department=Department.STUDENT_AFFAIRS,
                answer="Duyuru remote hata cevabi",
                sources=[],
                success=False,
                error="a2a_capability_transport_failed",
            )

    monkeypatch.setattr(settings.a2a, "mode", "http")
    monkeypatch.setattr(
        announcement_utils_module,
        "HttpA2ACapabilityTransport",
        _FailingCapabilityTransport,
    )
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()

    response = await request_announcement_response(
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
        query="Guncel duyurular neler?",
        context_id="ctx-ann-http-failure",
        routing_reason=None,
        query_log_id=None,
        task_type=TaskType.PROCEDURE_QUERY,
    )

    assert response.success is False
    assert response.error == "a2a_capability_transport_failed"
    announcement_agent.handle_task.assert_not_awaited()
    telemetry.record_agent_task.assert_awaited_once()


@pytest.mark.asyncio
async def test_event_http_mode_keeps_remote_failure_without_local_fallback(monkeypatch):
    import src.orchestrators.event_utils as event_utils_module

    class _FailingCapabilityTransport:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        async def dispatch(self, *, capability, payload):
            return DepartmentResponse(
                department=Department.STUDENT_AFFAIRS,
                answer="Etkinlik remote hata cevabi",
                sources=[],
                success=False,
                error="a2a_capability_transport_failed",
            )

    monkeypatch.setattr(settings.a2a, "mode", "http")
    monkeypatch.setattr(
        event_utils_module,
        "HttpA2ACapabilityTransport",
        _FailingCapabilityTransport,
    )
    event_agent = _FakeAgent("event", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()

    response = await request_event_response(
        event_agent=event_agent,
        telemetry_service=telemetry,
        query="Bu hafta etkinlik var mi?",
        context_id="ctx-event-http-failure",
        routing_reason=None,
        query_log_id=None,
        task_type=TaskType.PROCEDURE_QUERY,
    )

    assert response.success is False
    assert response.error == "a2a_capability_transport_failed"
    event_agent.handle_task.assert_not_awaited()
    telemetry.record_agent_task.assert_awaited_once()


def test_announcement_scope_uses_student_unit_for_exam_schedule_queries():
    scope = MainOrchestrator._resolve_announcement_scope(
        query="Sinav takvimi var mi?",
        conversation_resolution=ConversationResolution(
            original_query="Sinav takvimi var mi?",
            effective_query="Sinav takvimi var mi?",
            is_follow_up=False,
            used_context=False,
            active_topic=None,
            department_hints=[],
            source_hints=[],
        ),
        student_department="Bilgisayar Muhendisligi",
        student_faculty="Muhendislik Fakultesi",
    )

    assert scope == {
        "faculty": "Muhendislik Fakultesi",
        "unit_name": "Bilgisayar Muhendisligi",
    }


def test_announcement_scope_prefers_explicit_unit_over_student_profile():
    scope = MainOrchestrator._resolve_announcement_scope(
        query="Elektrik elektronik muhendisligi ders programi var mi?",
        conversation_resolution=ConversationResolution(
            original_query="Elektrik elektronik muhendisligi ders programi var mi?",
            effective_query="Elektrik elektronik muhendisligi ders programi var mi?",
            is_follow_up=False,
            used_context=False,
            active_topic=None,
            department_hints=[],
            source_hints=[],
        ),
        student_department="Bilgisayar Muhendisligi",
        student_faculty="Muhendislik Fakultesi",
    )

    assert scope == {
        "faculty": None,
        "unit_name": "Elektrik Elektronik Muhendisligi",
    }


def test_announcement_scope_does_not_mix_explicit_other_unit_with_profile_faculty():
    scope = MainOrchestrator._resolve_announcement_scope(
        query="Fizik ders programi var mi?",
        conversation_resolution=ConversationResolution(
            original_query="Fizik ders programi var mi?",
            effective_query="Fizik ders programi var mi?",
            is_follow_up=False,
            used_context=False,
            active_topic=None,
            department_hints=[],
            source_hints=[],
        ),
        student_department="Bilgisayar Muhendisligi",
        student_faculty="Muhendislik Fakultesi",
    )

    assert scope == {
        "faculty": None,
        "unit_name": "Fizik",
    }


def test_looks_like_event_query_requires_explicit_event_intent():
    assert looks_like_event_query("Muhendislik fakultesindeki etkinlikler neler?")
    assert looks_like_event_query("Bu hafta seminer var mi?")
    assert not looks_like_event_query("Ders kaydi ne zaman basliyor?")


def test_event_scope_does_not_force_student_unit_for_other_units():
    scope = MainOrchestrator._resolve_event_scope(
        query="Fizik etkinlikleri neler?",
        student_department="Bilgisayar Muhendisligi",
        student_faculty="Muhendislik Fakultesi",
    )

    assert scope == {
        "faculty": None,
        "unit_name": None,
    }


def test_event_scope_uses_student_unit_only_when_query_mentions_it():
    scope = MainOrchestrator._resolve_event_scope(
        query="Bilgisayar Muhendisligi etkinlikleri neler?",
        student_department="Bilgisayar Muhendisligi",
        student_faculty="Muhendislik Fakultesi",
    )

    assert scope == {
        "faculty": None,
        "unit_name": "Bilgisayar Muhendisligi",
    }


def test_academic_department_clarification_accepts_known_program_name():
    assert not requires_academic_department_clarification(
        query="Matematik Ogretmenligi 4. yariyil dersleri nelerdir?",
        departments=[Department.ACADEMIC_PROGRAMS],
        task_type=TaskType.COURSE_QUERY,
        student_department=None,
    )
    assert requires_academic_department_clarification(
        query="4. yariyil dersleri nelerdir?",
        departments=[Department.ACADEMIC_PROGRAMS],
        task_type=TaskType.COURSE_QUERY,
        student_department=None,
    )


def test_selected_specialists_from_responses_prefers_specialist_selection():
    responses = [
        DepartmentResponse(
            department=Department.STUDENT_AFFAIRS,
            answer="Kayit cevabi",
            metadata={"specialist_selection": {"selected_agent_id": "registration_agent"}},
        ),
        DepartmentResponse(
            department=Department.ACADEMIC_PROGRAMS,
            answer="Mevzuat cevabi",
            metadata={"agent_id": "regulation_agent"},
        ),
    ]

    assert MainOrchestrator._selected_specialists_from_responses(responses) == [
        "registration_agent",
        "regulation_agent",
    ]


@pytest.mark.asyncio
async def test_main_orchestrator_records_canonical_memory_answer_without_contact_suffix():
    router = AsyncMock()
    router.route = AsyncMock(
        return_value=RoutingResult(
            departments=[Department.STUDENT_AFFAIRS],
            confidence=0.9,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.DIRECT,
            reasoning="Kayit sorgusu",
            task_type=TaskType.REGISTRATION_QUERY,
        )
    )
    student_orchestrator = _FakeDepartmentOrchestrator(
        Department.STUDENT_AFFAIRS,
        "Kayit islemi icin ogrenci isleriyle gorusebilirsiniz.",
    )
    response_with_contact = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Kayit islemi icin ogrenci isleriyle gorusebilirsiniz.",
        include_contact_suggestion=True,
        sources=[],
    )
    student_orchestrator.handle = AsyncMock(return_value=response_with_contact)
    student_orchestrator.handle_task = AsyncMock(
        side_effect=lambda task, *args, **kwargs: build_department_response_task(
            response_with_contact,
            request_task=task,
            emitter_id=f"{Department.STUDENT_AFFAIRS.value}_orchestrator",
            emitter_name=f"{Department.STUDENT_AFFAIRS.value} Orchestrator",
        )
    )
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=404)
    telemetry.finalize_query_log = AsyncMock()
    conversation_service = AsyncMock()
    conversation_service.resolve_query = AsyncMock(
        return_value=ConversationResolution(
            original_query="Kayit nasil yenilenir?",
            effective_query="Kayit nasil yenilenir?",
            is_follow_up=False,
            used_context=False,
            active_topic=None,
            department_hints=[],
            source_hints=[],
        )
    )
    conversation_service.record_turn = AsyncMock()

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={
            Department.STUDENT_AFFAIRS: student_orchestrator,
        },
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
        conversation_service=conversation_service,
    )

    response = await orchestrator.handle_query(
        "Kayit nasil yenilenir?",
        context_id="ctx-memory-1",
    )

    assert CONTACT_SUGGESTION not in response.answer
    record_kwargs = conversation_service.record_turn.await_args.kwargs
    assert CONTACT_SUGGESTION not in record_kwargs["assistant_answer"]
    assert "Kaynak Ozeti:" not in record_kwargs["assistant_answer"]
    assert "Kaynak Özeti:" not in record_kwargs["assistant_answer"]
    assert "Uretim Turu:" not in record_kwargs["assistant_answer"]
    assert "Üretim Türü:" not in record_kwargs["assistant_answer"]


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
    assert "Kaynak Özeti:" in response.answer
    assert "Ofis iletisim kaydi: Akademik Programlar" in response.answer
    announcement_agent.handle_task.assert_not_awaited()
    task = academic_orchestrator.handle_task.await_args.args[0]
    assert task.metadata["final_answer_owner"] == "department_orchestrator"
    assert task.metadata["specialist_response_mode"] == "answer"


@pytest.mark.asyncio
async def test_main_orchestrator_marks_single_department_source_queries_for_main_final_answer():
    router = AsyncMock()
    router.route = AsyncMock(
        return_value=RoutingResult(
            departments=[Department.STUDENT_AFFAIRS],
            confidence=0.9,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.DIRECT,
            reasoning="Kaynakli ogrenci isleri sorusu",
            task_type=TaskType.REGISTRATION_QUERY,
            intent=IntentAnalysis(
                primary_intent="registration",
                is_personal=False,
                target_capability="none",
            ),
        )
    )
    response = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Kaynak bilgisi final cevap için hazırlandı.",
        sources=[
            RAGSource(
                content="Ders kaydi UBYS uzerinden yapilir.",
                score=0.86,
                metadata={"source": "sik_sorulan_sorular.txt", "score_type": "reranker"},
            )
        ],
        metadata={
            "evidence_packet": {
                "version": 1,
                "department": "student_affairs",
                "final_answer_owner": "main_orchestrator",
                "specialist_response_mode": "evidence_packet",
                "confidence": "high",
                "facts": [
                    {
                        "claim": "Ders kaydi UBYS uzerinden yapilir.",
                        "source": "sik_sorulan_sorular.txt",
                        "score": 0.86,
                        "support": "Ders kaydi UBYS uzerinden yapilir.",
                    }
                ],
                "selected_sources": [
                    {
                        "source": "sik_sorulan_sorular.txt",
                        "score": 0.86,
                        "snippet": "Ders kaydi UBYS uzerinden yapilir.",
                    }
                ],
            }
        },
        generation_mode="rag",
    )
    student_orchestrator = _FakeDepartmentOrchestrator(
        Department.STUDENT_AFFAIRS,
        response.answer,
    )
    student_orchestrator.handle_task = AsyncMock(
        side_effect=lambda task, *args, **kwargs: build_department_response_task(
            response,
            request_task=task,
            emitter_id=f"{Department.STUDENT_AFFAIRS.value}_orchestrator",
            emitter_name=f"{Department.STUDENT_AFFAIRS.value} Orchestrator",
        )
    )
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(return_value="Final cevap.")
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=307)
    telemetry.finalize_query_log = AsyncMock()
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={Department.STUDENT_AFFAIRS: student_orchestrator},
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
        llm_service=llm_service,
    )

    await orchestrator.handle_query("Ders kaydi nasil yapilir?", context_id="ctx-main-owner")

    task = student_orchestrator.handle_task.await_args.args[0]
    assert task.metadata["final_answer_owner"] == "main_orchestrator"
    assert task.metadata["specialist_response_mode"] == "evidence_packet"
    llm_service.generate.assert_awaited()


@pytest.mark.asyncio
async def test_main_orchestrator_records_a2a_department_transport_failure():
    router = AsyncMock()
    router.route = AsyncMock(
        return_value=RoutingResult(
            departments=[Department.ACADEMIC_PROGRAMS],
            confidence=0.91,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.DIRECT,
            reasoning="Akademik sorgu",
            task_type=TaskType.PROCEDURE_QUERY,
        )
    )

    class _FailedDepartmentOrchestrator:
        department = Department.ACADEMIC_PROGRAMS

        async def handle_task(self, task, *args, **kwargs):
            return build_department_response_task(
                DepartmentResponse(
                    department=Department.ACADEMIC_PROGRAMS,
                    answer="Akademik Programlar agent servisi zamaninda yanit veremedi.",
                    generation_mode="kural",
                    success=False,
                    error="a2a_transport_failed",
                ),
                request_task=task,
                emitter_id="academic_programs_orchestrator",
                emitter_name="academic_programs Orchestrator",
            )

    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=306)
    telemetry.finalize_query_log = AsyncMock()
    telemetry.record_agent_task = AsyncMock()

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={
            Department.ACADEMIC_PROGRAMS: _FailedDepartmentOrchestrator(),
        },
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
    )

    await orchestrator.handle_query("Formasyon dersleri nasil islenir?", context_id="ctx-a2a-fail")

    telemetry.record_agent_task.assert_awaited_once()
    kwargs = telemetry.record_agent_task.await_args.kwargs
    assert kwargs["sender"].agent_id == "main_orchestrator"
    assert kwargs["receiver"].agent_id == "academic_programs_orchestrator"
    assert kwargs["response"].error == "a2a_transport_failed"
    assert kwargs["payload"]["query_text"] == "Formasyon dersleri nasil islenir?"


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
    assert announcement not in filtered


def test_filter_low_confidence_responses_respects_score_type_thresholds():
    weak_reranker = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Sinirda ama zayif reranker yaniti",
        sources=[
            RAGSource(
                content="Yetersiz eslesen kaynak",
                score=0.22,
                metadata={
                    "source": "ogrenci_isleri.pdf",
                    "score_type": "reranker",
                },
            )
        ],
    )
    acceptable_retrieval = DepartmentResponse(
        department=Department.FINANCE,
        answer="Retrieval skoru yeterli cevap",
        sources=[
            RAGSource(
                content="Yeterli retrieval eslesmesi",
                score=0.06,
                metadata={
                    "source": "harc_duyurusu.pdf",
                    "score_type": "retrieval",
                },
            )
        ],
    )
    strong = DepartmentResponse(
        department=Department.ACADEMIC_PROGRAMS,
        answer="Guclu akademik cevap",
        sources=[
            RAGSource(
                content="CAP yonergesi ilgili maddeler",
                score=0.31,
                metadata={
                    "source": "yonerge_cift_anadal_yandal.pdf",
                    "score_type": "reranker",
                },
            )
        ],
    )

    filtered = filter_low_confidence_responses(
        [weak_reranker, acceptable_retrieval, strong]
    )

    assert weak_reranker not in filtered
    assert acceptable_retrieval in filtered
    assert strong in filtered


def test_filter_low_confidence_responses_preserves_source_owner_evidence_branch():
    student_affairs_primary = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Kaynak bilgisi final cevap icin hazirlandi.",
        sources=[
            RAGSource(
                content="CAP icin not ortalamasi en az 3,00 olmalidir.",
                score=0.001,
                metadata={"source": "cift_anadal_yonergesi.pdf"},
            )
        ],
        metadata={
            "specialist_selection": {"selected_agent_id": "registration_agent"},
            "evidence_packet": {
                "source_owner": "student_affairs_policy",
                "facts": [{"claim": "CAP icin not ortalamasi en az 3,00 olmalidir."}],
            },
        },
    )
    academic_support = DepartmentResponse(
        department=Department.ACADEMIC_PROGRAMS,
        answer="Akademik program kaynaklarina gore en az 3,00 gerekir.",
        sources=[
            RAGSource(
                content="Ana dal not ortalamasi 4,00 uzerinden en az 3,00 olmalidir.",
                score=0.45,
                metadata={"source": "yonerge_cift_anadal_yandal.pdf"},
            )
        ],
        metadata={"specialist_selection": {"selected_agent_id": "regulation_agent"}},
    )

    filtered = filter_low_confidence_responses(
        [academic_support, student_affairs_primary],
        source_owner="student_affairs_policy",
    )
    diagnostics = build_response_filter_diagnostics(
        original=[academic_support, student_affairs_primary],
        filtered=filtered,
        source_owner="student_affairs_policy",
    )

    assert student_affairs_primary in filtered
    assert filtered[0] is student_affairs_primary
    assert academic_support in filtered
    assert diagnostics["dropped_count"] == 0
    assert diagnostics["primary_department"] == "student_affairs"


def test_response_filter_diagnostics_reports_dropped_branch_reason():
    weak_no_info = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Bu konuda elimdeki kaynaklarda net bilgi bulunamadi.",
        sources=[],
        metadata={"specialist_selection": {"selected_agent_id": "registration_agent"}},
    )
    strong = DepartmentResponse(
        department=Department.ACADEMIC_PROGRAMS,
        answer="Guclu akademik cevap",
        sources=[
            RAGSource(
                content="CAP yonergesi ilgili maddeler",
                score=0.40,
                metadata={"source": "yonerge_cift_anadal_yandal.pdf"},
            )
        ],
    )

    filtered = filter_low_confidence_responses(
        [weak_no_info, strong],
        source_owner="student_affairs_policy",
    )
    diagnostics = build_response_filter_diagnostics(
        original=[weak_no_info, strong],
        filtered=filtered,
        source_owner="student_affairs_policy",
    )

    assert weak_no_info not in filtered
    assert diagnostics["dropped_count"] == 1
    assert diagnostics["dropped"][0]["department"] == "student_affairs"
    assert diagnostics["dropped"][0]["no_info"] is True
    assert diagnostics["dropped"][0]["source_owner_primary"] is True


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
    assert "[Akademik Programlar]" not in prompt
    assert "Departman ozeti:" not in prompt


def test_build_global_synthesis_prompt_generates_prompt_for_single_department():
    prompt, meaningful = build_global_synthesis_prompt(
        "Ders kaydini nasil yapacagim?",
        [
            DepartmentResponse(
                department=Department.STUDENT_AFFAIRS,
                answer="Ders kaydi ogrenci bilgi sistemi uzerinden yapilir ve danisman onayi gerekir.",
                sources=[
                    RAGSource(
                        content="Ders kaydi ogrenci bilgi sistemi uzerinden yapilir. Danisman onayi gerekir.",
                        score=0.82,
                        metadata={"source": "sik_sorulan_sorular.txt"},
                    )
                ],
            )
        ],
    )

    assert len(meaningful) == 1
    # Tek departman icin de sentez promptu uretiliyor
    assert prompt != ""
    assert "Kullanıcı sorusu" in prompt
    assert "Aşağıdaki JSON yalnızca iç bağlamdır" in prompt


def test_build_global_synthesis_prompt_prefers_evidence_packet():
    prompt, meaningful = build_global_synthesis_prompt(
        "CAP basvurusu icin GANO sarti nedir?",
        [
            DepartmentResponse(
                department=Department.ACADEMIC_PROGRAMS,
                answer="Ara cevap burada yalnizca destekleyici ozettir.",
                sources=[
                    RAGSource(
                        content="Ham kaynak metni final prompt icin ikincil kalmali.",
                        score=0.81,
                        metadata={"source": "ham_kaynak.pdf"},
                    )
                ],
                metadata={
                    "evidence_packet": {
                        "version": 1,
                        "department": "academic_programs",
                        "query_interpretation": "CAP GANO kosulu soruluyor.",
                        "confidence": "high",
                        "facts": [
                            {
                                "claim": "CAP basvurusu icin GANO en az 2.00 olmalidir.",
                                "source": "yonerge_cift_anadal_yandal.pdf",
                                "score": 0.91,
                                "support": "Basvuru icin genel not ortalamasi 2.00 ve uzeri olmalidir.",
                            }
                        ],
                        "limits": ["Basvuru tarihleri bu kaynakta yer almiyor."],
                        "selected_sources": [
                            {
                                "source": "yonerge_cift_anadal_yandal.pdf",
                                "score": 0.91,
                                "snippet": "GANO 2.00 ve uzeri olmalidir.",
                            }
                        ],
                    }
                },
            )
        ],
    )

    assert len(meaningful) == 1
    assert "evidence_packet" in prompt
    assert "CAP basvurusu icin GANO en az 2.00 olmalidir." in prompt
    assert "Basvuru tarihleri bu kaynakta yer almiyor." in prompt
    assert "yonerge_cift_anadal_yandal.pdf" in prompt


def test_build_global_synthesis_prompt_adds_synthesis_value_contract():
    retention_claim = (
        "Not ortalamasinin 4,00 uzerinden en az 2,00 olmasi sarttir; "
        "saglayamayan ogrencinin cift ana dal kaydi silinir."
    )
    application_claim = (
        "Ana dal not ortalamasinin 4,00 uzerinden en az 3,00 olmasi ve ana dal "
        "diploma programinin ilgili sinifinda basari siralamasi itibari ile en az ilk "
        "% 20'sinde bulunmasi gerekir."
    )
    prompt, meaningful = build_global_synthesis_prompt(
        "Peki not ortalamasi kac olmali?",
        [
            DepartmentResponse(
                department=Department.STUDENT_AFFAIRS,
                answer="Kaynak bilgisi final cevap icin hazirlandi.",
                sources=[],
                metadata={
                    "evidence_packet": {
                        "version": 1,
                        "department": "student_affairs",
                        "final_answer_owner": "main_orchestrator",
                        "specialist_response_mode": "evidence_packet",
                        "confidence": "high",
                        "facts": [
                            {
                                "claim": retention_claim,
                                "source": "yonerge_cift_anadal_yandal.pdf",
                                "policy_alignment": {
                                    "status": "match",
                                    "matched_programs": ["double_major"],
                                },
                            },
                            {
                                "claim": application_claim,
                                "source": "yonerge_cift_anadal_yandal.pdf",
                                "policy_alignment": {
                                    "status": "match",
                                    "matched_programs": ["double_major"],
                                },
                            },
                        ],
                    }
                },
            )
        ],
    )

    assert len(meaningful) == 1
    assert "synthesis_value_contract" in prompt
    assert '"primary_values": [\n      "3,00"\n    ]' in prompt
    assert '"secondary_values": [\n      "2,00"\n    ]' in prompt
    assert "secondary_values/conflicting_values icindeki degerleri" in prompt


def test_global_synthesis_marks_evidence_packet_mode_as_non_final_answer():
    prompt, meaningful = build_global_synthesis_prompt(
        "Devam kosulu nedir?",
        [
            DepartmentResponse(
                department=Department.STUDENT_AFFAIRS,
                answer="Kaynak bilgisi final cevap için hazırlandı.",
                sources=[
                    RAGSource(
                        content="Devam kosulu teorik derslerde yuzde 70 olarak uygulanir.",
                        score=0.88,
                        metadata={"source": "yonetmelik.pdf"},
                    )
                ],
                metadata={
                    "evidence_packet": {
                        "version": 1,
                        "department": "student_affairs",
                        "final_answer_owner": "main_orchestrator",
                        "specialist_response_mode": "evidence_packet",
                        "confidence": "high",
                        "facts": [
                            {
                                "claim": "Devam kosulu teorik derslerde yuzde 70 olarak uygulanir.",
                                "source": "yonetmelik.pdf",
                                "score": 0.88,
                                "support": "Devam kosulu teorik derslerde yuzde 70 olarak uygulanir.",
                            }
                        ],
                        "selected_sources": [
                            {
                                "source": "yonetmelik.pdf",
                                "score": 0.88,
                                "snippet": "Devam kosulu teorik derslerde yuzde 70 olarak uygulanir.",
                            }
                        ],
                    }
                },
            )
        ],
    )

    assert len(meaningful) == 1
    assert "Uzman ajan final cevap yazmadi" in prompt
    assert "Devam kosulu teorik derslerde yuzde 70 olarak uygulanir." in prompt


def test_global_synthesis_accepts_context_required_clarification_response():
    responses = [
        DepartmentResponse(
            department=Department.STUDENT_AFFAIRS,
            answer="Ders kaydi UBYS uzerinden yapilir ve danisman onayi gerekir.",
            sources=[
                RAGSource(
                    content="UBYS uzerinden ders secilir ve danisman onayi gerekir.",
                    score=0.82,
                    metadata={"source": "sik_sorulan_sorular.txt"},
                )
            ],
            success=True,
        ),
        DepartmentResponse(
            department=Department.FINANCE,
            answer=(
                "Dogru ucreti paylasabilmem icin ogrenci tipi ve birim bilgisi gerekiyor."
            ),
            sources=[],
            success=False,
            error="student_type_context_required",
        ),
    ]

    assert should_use_global_synthesis(
        query="Kayit yenileme doneminde harc ucretimi yatirdiktan sonra ders kaydini nasil yapacagim?",
        responses=responses,
    ) is True

    prompt, meaningful = build_global_synthesis_prompt(
        "Kayit yenileme doneminde harc ucretimi yatirdiktan sonra ders kaydini nasil yapacagim?",
        responses,
    )

    assert len(meaningful) == 2
    assert '"department": "finance"' in prompt


def test_build_final_user_response_marks_global_synthesis_as_llm():
    response = build_final_user_response(
        answer="Birlesik final cevap.",
        responses=[
            DepartmentResponse(
                department=Department.STUDENT_AFFAIRS,
                answer="Ogrenci isleri yaniti",
                sources=[
                    RAGSource(
                        content="Ders kaydi UBYS uzerinden yapilir.",
                        score=0.81,
                        metadata={"source": "sik_sorulan_sorular.txt"},
                    )
                ],
                generation_mode="rag",
            ),
            DepartmentResponse(
                department=Department.FINANCE,
                answer="Ucret bilgisi icin ogrenci tipi gereklidir.",
                sources=[],
                generation_mode="kural",
                success=False,
                error="student_type_context_required",
            ),
        ],
        department_responses=[],
        context_id="ctx-global-llm",
        response_time_ms=12.5,
        student_full_name=None,
        used_global_synthesis=True,
    )

    assert response.generation_modes[0] == "llm"
    assert "llm" in response.generation_modes


def test_build_final_user_response_includes_llm_diagnostics_from_profiler():
    profiler = QueryProfiler(label="response-diagnostics")
    profiler.append_attribute_list(
        "llm_usage",
        {
            "kind": "generate",
            "model_role": "routing",
            "provider": "openai_compatible",
            "provider_label": "groq",
            "display_name": "groq",
            "model": "llama-3.1-8b-instant",
            "path": "primary",
            "status": "success",
            "json_mode": True,
        },
    )

    with activate_profiler(profiler):
        response = build_final_user_response(
            answer="Birlesik final cevap.",
            responses=[
                DepartmentResponse(
                    department=Department.STUDENT_AFFAIRS,
                    answer="Ogrenci isleri yaniti",
                    sources=[],
                    generation_mode="rag",
                )
            ],
            department_responses=[],
            context_id="ctx-diagnostics",
            response_time_ms=10.0,
            student_full_name=None,
        )

    assert response.diagnostics is not None
    assert response.diagnostics.llm_usage[0]["model_role"] == "routing"
    assert response.diagnostics.llm_usage[0]["provider_label"] == "groq"
    assert response.diagnostics.llm_usage[0]["model"] == "llama-3.1-8b-instant"
    assert response.diagnostics.local_profile is not None
    assert response.diagnostics.local_profile["attributes"]["answer_length"]["policy"] == "normal"


def test_build_final_user_response_includes_answer_debug_report():
    profiler = QueryProfiler(label="debug-report")
    with activate_profiler(profiler):
        response = build_final_user_response(
            answer="Kaynakli cevap.",
            responses=[
                DepartmentResponse(
                    department=Department.STUDENT_AFFAIRS,
                    answer="Kayit cevabi",
                    sources=[
                        RAGSource(
                            content="Ders kaydi icin harc odenir.",
                            score=0.88,
                            metadata={
                                "source": "sik_sorulan_sorular.txt",
                                "score_type": "reranker",
                                "chunk_index": 3,
                            },
                        )
                    ],
                    generation_mode="rag",
                    metadata={
                        "specialist_selection": {"selected_agent_id": "registration_agent"},
                        "answer_contract": {"contract_id": "payment_debt_course_registration"},
                        "source_owner": {"primary": "student_affairs_policy"},
                    },
                )
            ],
            department_responses=[],
            context_id="ctx-debug-report",
            response_time_ms=10.0,
            student_full_name=None,
        )

    assert response.diagnostics is not None
    report = response.diagnostics.answer_debug_report
    assert report is not None
    assert report["schema"] == "omu.answer_debug_report.v1"
    assert report["routes"][0]["agent"] == "registration_agent"
    assert report["sources"][0]["source"] == "sik_sorulan_sorular.txt"
    assert report["sources"][0]["chunk_index"] == 3
    assert report["contracts"][0]["agent"] == "registration_agent"
    assert report["answer_length"]["policy"] == "normal"


def test_should_use_global_synthesis_skips_when_all_meaningful_answers_are_non_rag():
    responses = [
        DepartmentResponse(
            department=Department.STUDENT_AFFAIRS,
            answer="Veritabanindaki en yakin kayit donemi 2026-Guz icin 26.08.2026 - 06.09.2026 tarihleri arasinda planlanmistir.",
            db_data={"semester": "2026-Guz"},
            sources=[],
            success=True,
        ),
        DepartmentResponse(
            department=Department.FINANCE,
            answer="Ogrenim ucreti ogrenci turune ve birime gore degisiyor.",
            sources=[],
            success=False,
            error="student_type_context_required",
        ),
    ]

    assert should_use_global_synthesis(
        query="Kayit yenileme ucreti ne kadar ve ne zaman yapilir?",
        responses=responses,
    ) is False


def test_filter_low_confidence_responses_drops_no_source_no_info_branch():
    academic = DepartmentResponse(
        department=Department.ACADEMIC_PROGRAMS,
        answer="Erasmus basvurulari duyurularda belirtilen tarihler arasinda online yapilir.",
        sources=[
            RAGSource(
                content="Erasmus basvurulari online yapilir.",
                score=0.63,
                metadata={"score_type": "reranker", "source": "erasmus.pdf"},
            )
        ],
        generation_mode="rag",
    )
    finance_no_info = DepartmentResponse(
        department=Department.FINANCE,
        answer=(
            "Bu konuda elimde yeterli kaynak bulunamadi. "
            "Soruyu biraz daha detaylandirirsan veya ilgili birimle iletisime gecersen daha net yardimci olabilirim."
        ),
        generation_mode="kural",
    )

    filtered = filter_low_confidence_responses([academic, finance_no_info])

    assert filtered == [academic]
    # Tek departman + kaynak varsa artik global synthesis aktif
    # (ancak _compose_final_answer basarili cevabi tekrar senteze gondermez)
    assert should_use_global_synthesis(
        query="Erasmus bursu ne kadar ve nasil basvurulur?",
        responses=filtered,
    ) is True


@pytest.mark.asyncio
async def test_compose_final_answer_uses_final_refinement_for_single_department_response():
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(return_value="Final LLM cevabi.")
    orchestrator = MainOrchestrator(
        router=AsyncMock(),
        department_orchestrators={},
        announcement_agent=_FakeAgent("announcement", Department.STUDENT_AFFAIRS),
        telemetry_service=AsyncMock(),
        llm_service=llm_service,
    )

    responses = [
        DepartmentResponse(
            department=Department.STUDENT_AFFAIRS,
            answer="Ders kaydi ogrenci bilgi sistemi uzerinden yapilir.",
            sources=[
                RAGSource(
                    content="Ders kaydi ogrenci bilgi sistemi uzerinden yapilir.",
                    score=0.84,
                    metadata={"source": "sik_sorulan_sorular.txt", "score_type": "reranker"},
                )
            ],
            success=True,
            generation_mode="rag",
        )
    ]

    answer, used_global_synthesis = await orchestrator._compose_final_answer(
        query="Ders kaydini nasil yapacagim?",
        responses=responses,
        llm_profile="balanced",
    )

    assert used_global_synthesis is True
    assert answer.startswith("Final LLM cevabi.")
    llm_service.generate.assert_awaited_once()
    assert llm_service.generate.await_args.kwargs["model_role"] == "final_refinement"


@pytest.mark.asyncio
async def test_compose_final_answer_skips_llm_when_main_contract_is_deterministic():
    from src.core.answer_contracts import resolve_answer_contract

    query = "Bilgisayar Muhendisligi ders programi ne?"
    contract = resolve_answer_contract(query)
    assert contract is not None
    assert contract.synthesis_policy == "deterministic"

    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(return_value="Final LLM cevabi.")
    orchestrator = MainOrchestrator(
        router=AsyncMock(),
        department_orchestrators={},
        announcement_agent=_FakeAgent("announcement", Department.STUDENT_AFFAIRS),
        telemetry_service=AsyncMock(),
        llm_service=llm_service,
    )
    responses = [
        DepartmentResponse(
            department=Department.ACADEMIC_PROGRAMS,
            answer="Bilgisayar Muhendisligi ders programi: Pazartesi 09:00.",
            sources=[
                RAGSource(
                    content="Bilgisayar Muhendisligi ders programi: Pazartesi 09:00.",
                    score=1.0,
                    metadata={"source": "weekly_schedule"},
                )
            ],
            db_data={"query_type": "schedule_lookup"},
            success=True,
            generation_mode="kural",
            metadata={"answer_contract": contract.to_metadata()},
        )
    ]

    answer, used_global_synthesis = await orchestrator._compose_final_answer(
        query=query,
        responses=responses,
        llm_profile="balanced",
        answer_contract=contract,
    )

    assert used_global_synthesis is False
    assert "Pazartesi 09:00" in answer
    llm_service.generate.assert_not_awaited()


def test_contract_validation_fallback_for_cap_eligibility_is_contract_safe():
    from src.core.answer_contracts import (
        resolve_answer_contract,
        validate_answer_against_contract,
    )

    query = "Çapa başvurabilir miyim?"
    contract = resolve_answer_contract(query)
    fallback = MainOrchestrator._contract_validation_fallback(
        query=query,
        contract=contract,
    )

    assert fallback is not None
    assert "3,00" in fallback
    assert "ilk %20" in fallback
    assert "120 AKTS" not in fallback
    assert validate_answer_against_contract(
        query=query,
        answer=fallback,
        contract=contract,
    )["status"] == "pass"


def test_contract_validation_fallback_for_special_long_graduation_akts_is_safe():
    from src.core.answer_contracts import (
        resolve_answer_contract,
        validate_answer_against_contract,
    )

    query = "Diş hekimliğinden mezun olmak için kaç AKTS lazım?"
    contract = resolve_answer_contract(query)
    fallback = MainOrchestrator._contract_validation_fallback(
        query=query,
        contract=contract,
    )

    assert fallback is not None
    assert "doğrulanmış toplam AKTS koşulu yok" in fallback
    assert "240 AKTS" not in fallback
    assert validate_answer_against_contract(
        query=query,
        answer=fallback,
        contract=contract,
    )["status"] == "pass"


@pytest.mark.asyncio
async def test_final_quality_gate_tolerates_minor_issue_when_repair_times_out():
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(side_effect=asyncio.TimeoutError())
    orchestrator = MainOrchestrator(
        router=AsyncMock(),
        department_orchestrators={},
        announcement_agent=_FakeAgent("announcement", Department.STUDENT_AFFAIRS),
        telemetry_service=AsyncMock(),
        llm_service=llm_service,
    )

    answer = await orchestrator._apply_final_quality_gate(
        query="Basvuru sureci ne zaman?",
        answer="Basvuru sureci before ve during duyurularda aciklanir.",
        llm_profile="balanced",
    )

    assert "güvenilir biçimde sentezleyemiyorum" not in answer
    assert "before" in answer
    llm_service.generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_compose_final_answer_uses_evidence_packet_fallback_when_final_llm_fails():
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(side_effect=asyncio.TimeoutError())
    orchestrator = MainOrchestrator(
        router=AsyncMock(),
        department_orchestrators={},
        announcement_agent=_FakeAgent("announcement", Department.STUDENT_AFFAIRS),
        telemetry_service=AsyncMock(),
        llm_service=llm_service,
    )

    responses = [
        DepartmentResponse(
            department=Department.STUDENT_AFFAIRS,
            answer="Kaynak bilgisi final cevap için hazırlandı.",
            sources=[
                RAGSource(
                    content="Devam kosulu teorik derslerde yuzde 70, uygulamalarda yuzde 80 olarak uygulanir.",
                    score=0.88,
                    metadata={"source": "yonetmelik.pdf", "score_type": "reranker"},
                )
            ],
            success=True,
            generation_mode="rag",
            metadata={
                "final_answer_owner": "main_orchestrator",
                "specialist_response_mode": "evidence_packet",
                "evidence_packet": {
                    "version": 1,
                    "department": "student_affairs",
                    "final_answer_owner": "main_orchestrator",
                    "specialist_response_mode": "evidence_packet",
                    "confidence": "high",
                    "facts": [
                        {
                            "claim": "Devam kosulu teorik derslerde yuzde 70, uygulamalarda yuzde 80 olarak uygulanir.",
                            "source": "yonetmelik.pdf",
                            "score": 0.88,
                            "support": "Devam kosulu teorik derslerde yuzde 70, uygulamalarda yuzde 80 olarak uygulanir.",
                        }
                    ],
                },
            },
        )
    ]

    answer, used_global_synthesis = await orchestrator._compose_final_answer(
        query="Devam kosulu nedir?",
        responses=responses,
        llm_profile="balanced",
    )

    assert used_global_synthesis is False
    assert "Kaynak bilgisi final cevap" not in answer
    assert "Devam kosulu teorik derslerde yuzde 70" in answer
    llm_service.generate.assert_awaited_once()


def test_evidence_packet_fallback_can_use_sources_when_packet_is_missing():
    responses = [
        DepartmentResponse(
            department=Department.ACADEMIC_PROGRAMS,
            answer="Kaynak bilgisi final cevap icin hazirlandi.",
            sources=[
                RAGSource(
                    content=(
                        "CAP'a basvurularda ana dal not ortalamasinin 4,00 uzerinden "
                        "en az 3,00 olmasi ve basari siralamasi itibariyle ilk yuzde "
                        "20 icinde bulunmasi gerekir."
                    ),
                    score=0.91,
                    metadata={"source": "yonerge_cift_anadal_yandal.pdf"},
                )
            ],
            success=True,
            generation_mode="rag",
        )
    ]

    answer = build_evidence_packet_fallback_answer(
        responses,
        query="cap basvurusu icin not ortalamasi kac olmali",
    )

    assert answer is not None
    assert "3,00" in answer
    assert "not ortalamas" in answer


@pytest.mark.asyncio
async def test_compose_final_answer_keeps_global_synthesis_role_for_multi_department_response():
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(return_value="Birlesik final LLM cevabi.")
    orchestrator = MainOrchestrator(
        router=AsyncMock(),
        department_orchestrators={},
        announcement_agent=_FakeAgent("announcement", Department.STUDENT_AFFAIRS),
        telemetry_service=AsyncMock(),
        llm_service=llm_service,
    )

    responses = [
        DepartmentResponse(
            department=Department.STUDENT_AFFAIRS,
            answer="Kayit islemleri ogrenci bilgi sistemi uzerinden yapilir.",
            sources=[
                RAGSource(
                    content="Kayit islemleri ogrenci bilgi sistemi uzerinden yapilir.",
                    score=0.84,
                    metadata={"source": "sik_sorulan_sorular.txt", "score_type": "reranker"},
                )
            ],
            success=True,
            generation_mode="rag",
        ),
        DepartmentResponse(
            department=Department.FINANCE,
            answer="Ogrenim ucreti ogrenci turune gore degisir.",
            sources=[
                RAGSource(
                    content="Ogrenim ucreti ogrenci turune gore degisir.",
                    score=0.79,
                    metadata={"source": "ucret_tablosu.pdf", "score_type": "reranker"},
                )
            ],
            success=True,
            generation_mode="rag",
        ),
    ]

    answer, used_global_synthesis = await orchestrator._compose_final_answer(
        query="Kayit yenileme ucreti ne kadar ve ders kaydi nasil yapilir?",
        responses=responses,
        llm_profile="balanced",
    )

    assert used_global_synthesis is True
    assert answer.startswith("Birlesik final LLM cevabi.")
    llm_service.generate.assert_awaited_once()
    assert llm_service.generate.await_args.kwargs["model_role"] == "global_synthesis"


def test_build_final_user_response_keeps_routed_departments_after_answer_filtering():
    academic = DepartmentResponse(
        department=Department.ACADEMIC_PROGRAMS,
        answer="Erasmus basvurulari duyurularda belirtilen tarihler arasinda online yapilir.",
        sources=[
            RAGSource(
                content="Erasmus basvurulari online yapilir.",
                score=0.63,
                metadata={"score_type": "reranker", "source": "erasmus.pdf"},
            )
        ],
        generation_mode="rag",
    )
    finance_no_info = DepartmentResponse(
        department=Department.FINANCE,
        answer="Bu konuda elimde yeterli kaynak bulunamadi.",
        generation_mode="kural",
    )

    response = build_final_user_response(
        answer=academic.answer,
        responses=[academic],
        department_responses=[academic, finance_no_info],
        context_id="ctx-surface-departments",
        response_time_ms=12.5,
        student_full_name=None,
    )

    assert set(response.departments_involved) == {"academic_programs", "finance"}
    assert "Bu konuda elimde yeterli kaynak bulunamadi" not in response.answer


@pytest.mark.asyncio
async def test_main_orchestrator_returns_smalltalk_for_greeting_without_routing():
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

    assert "Merhaba" in response.answer
    assert "yardımcı olabilirim" in response.answer
    assert response.departments_involved == []
    router.route.assert_not_awaited()
    announcement_agent.handle_task.assert_not_awaited()


@pytest.mark.asyncio
async def test_main_orchestrator_uses_missing_slot_clarification_before_dispatch():
    router = AsyncMock()
    router.route = AsyncMock(
        return_value=RoutingResult(
            departments=[Department.FINANCE],
            confidence=0.86,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.DIRECT,
            reasoning="Ucret sorgusu ogrenci turu eksik",
            task_type=TaskType.TUITION_QUERY,
            intent=IntentAnalysis(
                primary_intent="tuition",
                required_slots=["student_type", "faculty_or_program"],
                missing_slots=["student_type"],
            ),
        )
    )
    finance_orchestrator = _FakeDepartmentOrchestrator(
        Department.FINANCE,
        "Finans cevabi",
    )
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=203)
    telemetry.finalize_query_log = AsyncMock()
    telemetry.record_agent_task = AsyncMock()

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={Department.FINANCE: finance_orchestrator},
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
    )

    response = await orchestrator.handle_query(
        "Elektrik elektronik muhendisligi ogrenim ucreti ne kadar?",
        context_id="ctx-missing-slot",
    )

    assert "Türk öğrenci" in response.answer
    assert "uluslararası öğrenci" in response.answer
    assert response.departments_involved == [Department.FINANCE.value]
    finance_orchestrator.handle_task.assert_not_awaited()


@pytest.mark.asyncio
async def test_main_orchestrator_returns_acknowledgement_for_thanks_without_routing():
    router = AsyncMock()
    router.route = AsyncMock()
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=203)
    telemetry.finalize_query_log = AsyncMock()

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={},
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
    )

    response = await orchestrator.handle_query("Tesekkurler", context_id="ctx-ack-1")

    assert "Rica ederim" in response.answer
    assert response.departments_involved == []
    router.route.assert_not_awaited()
    announcement_agent.handle_task.assert_not_awaited()


@pytest.mark.asyncio
async def test_main_orchestrator_returns_smalltalk_for_naber_without_routing():
    router = AsyncMock()
    router.route = AsyncMock()
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=204)
    telemetry.finalize_query_log = AsyncMock()

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={},
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
    )

    response = await orchestrator.handle_query("Selam", context_id="ctx-smalltalk")

    assert "Merhaba" in response.answer
    assert response.departments_involved == []
    router.route.assert_not_awaited()
    announcement_agent.handle_task.assert_not_awaited()


@pytest.mark.asyncio
async def test_main_orchestrator_returns_acknowledgement_for_short_confirmation_without_routing():
    router = AsyncMock()
    router.route = AsyncMock()
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=204)
    telemetry.finalize_query_log = AsyncMock()

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={},
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
    )

    response = await orchestrator.handle_query("Evet", context_id="ctx-ack-2")

    assert "Hazırım" in response.answer
    assert response.departments_involved == []
    router.route.assert_not_awaited()
    announcement_agent.handle_task.assert_not_awaited()


@pytest.mark.asyncio
async def test_main_orchestrator_uses_question_cache_when_enabled(monkeypatch):
    question_cache.clear()
    question_cache.configure(ttl_seconds=300, enabled=True)
    monkeypatch.setattr(settings.cache, "enabled", True)
    monkeypatch.setattr(settings.cache, "question_cache_enabled", True)
    monkeypatch.setattr(settings.capability_planner, "mode", "off")

    router = AsyncMock()
    router.route = AsyncMock(
        return_value=RoutingResult(
            departments=[Department.STUDENT_AFFAIRS],
            confidence=0.92,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.DIRECT,
            reasoning="Kayit sorusu",
            task_type=TaskType.REGISTRATION_QUERY,
        )
    )
    student_orchestrator = _FakeDepartmentOrchestrator(
        Department.STUDENT_AFFAIRS,
        "Kayit cevabi",
    )
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(side_effect=[501, 502])
    telemetry.finalize_query_log = AsyncMock()

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={Department.STUDENT_AFFAIRS: student_orchestrator},
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
    )

    first = await orchestrator.handle_query("Ders kaydi ne zaman basliyor?", context_id="ctx-cache-1")
    second = await orchestrator.handle_query("Ders kaydi ne zaman basliyor?", context_id="ctx-cache-2")

    assert "Kayit cevabi" in first.answer
    assert "Kayit cevabi" in second.answer
    assert first.query_id == "ctx-cache-1"
    assert second.query_id == "ctx-cache-2"
    assert router.route.await_count == 1
    assert student_orchestrator.handle_task.await_count == 1
    assert telemetry.finalize_query_log.await_count == 2
    assert telemetry.create_query_log.await_args_list[0].kwargs["metadata_extra"]["cache"]["question_cache"] == "miss"
    assert telemetry.create_query_log.await_args_list[1].kwargs["metadata_extra"]["cache"]["question_cache"] == "hit"

    question_cache.clear()


@pytest.mark.asyncio
async def test_main_orchestrator_skips_question_cache_when_disabled(monkeypatch):
    question_cache.clear()
    question_cache.configure(ttl_seconds=300, enabled=True)
    monkeypatch.setattr(settings.cache, "enabled", True)
    monkeypatch.setattr(settings.cache, "question_cache_enabled", False)

    router = AsyncMock()
    router.route = AsyncMock(
        return_value=RoutingResult(
            departments=[Department.STUDENT_AFFAIRS],
            confidence=0.92,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.DIRECT,
            reasoning="Kayit sorusu",
            task_type=TaskType.REGISTRATION_QUERY,
        )
    )
    student_orchestrator = _FakeDepartmentOrchestrator(
        Department.STUDENT_AFFAIRS,
        "Kayit cevabi",
    )
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(side_effect=[601, 602])
    telemetry.finalize_query_log = AsyncMock()

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={Department.STUDENT_AFFAIRS: student_orchestrator},
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
    )

    await orchestrator.handle_query("Ders kaydi ne zaman basliyor?", context_id="ctx-nocache-1")
    await orchestrator.handle_query("Ders kaydi ne zaman basliyor?", context_id="ctx-nocache-2")

    assert router.route.await_count == 2
    assert student_orchestrator.handle_task.await_count == 2

    question_cache.clear()
    monkeypatch.setattr(settings.cache, "question_cache_enabled", True)


@pytest.mark.asyncio
async def test_main_orchestrator_skips_question_cache_when_request_disabled(monkeypatch):
    question_cache.clear()
    question_cache.configure(ttl_seconds=300, enabled=True)
    monkeypatch.setattr(settings.cache, "enabled", True)
    monkeypatch.setattr(settings.cache, "question_cache_enabled", True)

    router = AsyncMock()
    router.route = AsyncMock(
        return_value=RoutingResult(
            departments=[Department.STUDENT_AFFAIRS],
            confidence=0.92,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.DIRECT,
            reasoning="Kayit sorusu",
            task_type=TaskType.REGISTRATION_QUERY,
        )
    )
    student_orchestrator = _FakeDepartmentOrchestrator(
        Department.STUDENT_AFFAIRS,
        "Kayit cevabi",
    )
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(side_effect=[651, 652])
    telemetry.finalize_query_log = AsyncMock()

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={Department.STUDENT_AFFAIRS: student_orchestrator},
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
    )

    await orchestrator.handle_query(
        "Ders kaydi ne zaman basliyor?",
        context_id="ctx-request-nocache-1",
        disable_cache=True,
    )
    await orchestrator.handle_query(
        "Ders kaydi ne zaman basliyor?",
        context_id="ctx-request-nocache-2",
        disable_cache=True,
    )

    assert router.route.await_count == 2
    assert student_orchestrator.handle_task.await_count == 2
    assert question_cache.size == 0
    assert telemetry.create_query_log.await_args_list[0].kwargs["metadata_extra"]["cache"]["question_cache"] == "bypass"
    assert telemetry.create_query_log.await_args_list[1].kwargs["metadata_extra"]["cache"]["question_cache"] == "bypass"

    question_cache.clear()


@pytest.mark.asyncio
async def test_main_orchestrator_does_not_question_cache_announcement_queries(monkeypatch):
    question_cache.clear()
    question_cache.configure(ttl_seconds=300, enabled=True)
    monkeypatch.setattr(settings.cache, "enabled", True)
    monkeypatch.setattr(settings.cache, "question_cache_enabled", True)
    monkeypatch.setattr(settings.capability_planner, "mode", "pilot")
    monkeypatch.setattr(settings.capability_planner, "scope", "announcement")

    async def _plan_capability_action(*args, **kwargs):
        return CapabilityAction(
            capability="announcement.search",
            params={"query": "Son duyurular neler?"},
            confidence=0.95,
            reasoning="duyuru aramasi",
        )

    monkeypatch.setattr(
        main_module,
        "plan_capability_action",
        _plan_capability_action,
    )

    router = AsyncMock()
    router.route = AsyncMock()
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=701)
    telemetry.finalize_query_log = AsyncMock()
    telemetry.record_agent_task = AsyncMock()

    async def _announcement_handle_task(task):
        return build_department_response_task(
            DepartmentResponse(
                department=Department.STUDENT_AFFAIRS,
                answer="Ilgili duyurular:\n1. Guncel duyuru",
                sources=[
                    RAGSource(
                        content="Guncel duyuru icerigi",
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

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={},
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
    )

    await orchestrator.handle_query("Son duyurular neler?", context_id="ctx-ann-cache-1")
    await orchestrator.handle_query("Son duyurular neler?", context_id="ctx-ann-cache-2")

    assert announcement_agent.handle_task.await_count == 2
    assert question_cache.size == 0


@pytest.mark.asyncio
async def test_announcement_gate_params_are_passed_to_existing_agent(monkeypatch):
    monkeypatch.setattr(settings.capability_planner, "mode", "pilot")
    monkeypatch.setattr(settings.capability_planner, "scope", "announcement")

    async def _plan_capability_action(*args, **kwargs):
        return CapabilityAction(
            capability="announcement.search",
            params={
                "query": "Son duyurular neler?",
                "unit_name": "Bilgisayar Muhendisligi",
                "limit": 2,
                "allow_latest_fallback": False,
            },
            confidence=0.95,
            reasoning="duyuru aramasi",
        )

    monkeypatch.setattr(
        main_module,
        "plan_capability_action",
        _plan_capability_action,
    )

    router = AsyncMock()
    router.route = AsyncMock()
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=706)
    telemetry.finalize_query_log = AsyncMock()
    telemetry.record_agent_task = AsyncMock()

    async def _announcement_handle_task(task):
        assert task.metadata["unit_name"] == "Bilgisayar Muhendisligi"
        assert task.metadata["limit"] == 2
        assert task.metadata["allow_latest_fallback"] is False
        return build_department_response_task(
            DepartmentResponse(
                department=Department.STUDENT_AFFAIRS,
                answer="Ilgili duyurular:\n1. Planli duyuru",
                sources=[
                    RAGSource(
                        content="Planli duyuru icerigi",
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
    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={},
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
    )

    response = await orchestrator.handle_query("Son duyurular neler?", context_id="ctx-ann-gate")

    assert "Planli duyuru" in response.answer
    assert response.departments_involved == ["announcement"]
    router.route.assert_not_awaited()
    announcement_agent.handle_task.assert_awaited_once()


@pytest.mark.asyncio
async def test_main_orchestrator_normalizes_short_announcement_before_routing(monkeypatch):
    monkeypatch.setattr(settings.llm, "query_normalization_enabled", True)
    router = AsyncMock()
    router.route = AsyncMock(
        return_value=RoutingResult(
            departments=[],
            confidence=0.91,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.DIRECT,
            reasoning="Duyuru sorgusu",
            task_type=None,
            intent=IntentAnalysis(
                primary_intent="announcement",
                target_capability="announcement",
                confidence=0.91,
            ),
        )
    )
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(
        return_value=(
            '{"canonical_query":"Guncel duyurular nelerdir?",'
            '"is_personal":false,'
            '"primary_intent":"announcement",'
            '"target_capability":"announcement",'
            '"confidence":0.91,'
            '"reasoning":"duyuru sorgusu"}'
        )
    )
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=705)
    telemetry.finalize_query_log = AsyncMock()
    telemetry.record_agent_task = AsyncMock()

    async def _announcement_handle_task(task):
        return build_department_response_task(
            DepartmentResponse(
                department=Department.STUDENT_AFFAIRS,
                answer="Ilgili duyurular:\n1. Guncel duyuru",
                sources=[
                    RAGSource(
                        content="Guncel duyuru icerigi",
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
    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={},
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
        llm_service=llm_service,
    )

    response = await orchestrator.handle_query("Guncel duyur", context_id="ctx-ann-normalize")

    assert "Guncel duyuru" in response.answer
    assert response.departments_involved == ["announcement"]
    router.route.assert_awaited_once()
    announcement_agent.handle_task.assert_awaited_once()


@pytest.mark.asyncio
async def test_main_orchestrator_short_circuits_event_queries(monkeypatch):
    monkeypatch.setattr(settings.capability_planner, "mode", "off")
    question_cache.clear()
    question_cache.configure(ttl_seconds=300, enabled=True)
    monkeypatch.setattr(settings.cache, "enabled", True)
    monkeypatch.setattr(settings.cache, "question_cache_enabled", True)

    router = AsyncMock()
    router.route = AsyncMock(
        return_value=RoutingResult(
            departments=[],
            confidence=0.94,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.CLARIFICATION,
            reasoning="Routing LLM etkinlik capability'sini secti.",
            task_type=TaskType.PROCEDURE_QUERY,
            intent=IntentAnalysis(
                complexity="simple",
                is_personal=False,
                force_llm_synthesis=False,
                query_type="factual",
                reasoning="etkinlik aramasi",
                primary_intent="event",
                target_capability="event",
                required_slots=[],
                missing_slots=[],
            ),
        )
    )
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=702)
    telemetry.finalize_query_log = AsyncMock()

    monkeypatch.setattr(
        "src.agents.event.agent.fetch_relevant_events",
        AsyncMock(
            return_value=[
                EventRecord(
                    id=1,
                    title="Yapay Zeka Semineri",
                    display_summary="Bolume ozel seminer",
                    summary="Bolume ozel seminer",
                    original_text="Bolume ozel seminer",
                    source_url="https://omu.edu.tr/tr/etkinlikler/yapay-zeka-semineri",
                    faculty="Muhendislik Fakultesi",
                    unit_name="Bilgisayar Muhendisligi",
                    department="academic_programs",
                    event_type="seminer",
                    location="Mavi Salon",
                    organizer="Bilgisayar Muhendisligi Bolumu",
                    starts_at=None,
                    ends_at=None,
                    all_day=True,
                    links=(
                        EventLinkRecord(
                            label="Program PDF",
                            url="https://omu.edu.tr/program.pdf",
                            link_type="attachment",
                        ),
                    ),
                )
            ]
        ),
    )

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={},
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
    )

    response = await orchestrator.handle_query(
        "Bilgisayar muhendisligindeki etkinlikler neler?",
        context_id="ctx-event-1",
    )

    assert "Yapay Zeka Semineri" in response.answer
    assert "Mavi Salon" in response.answer
    assert response.departments_involved == ["event"]
    assert response.generation_modes == ["vt"]
    assert router.route.await_count == 1
    assert announcement_agent.handle_task.await_count == 0
    assert question_cache.size == 0


@pytest.mark.asyncio
async def test_event_gate_params_are_passed_to_existing_agent(monkeypatch):
    monkeypatch.setattr(settings.capability_planner, "mode", "pilot")
    monkeypatch.setattr(settings.capability_planner, "scope", "event")

    async def _plan_capability_action(*args, **kwargs):
        return CapabilityAction(
            capability="event.search",
            params={
                "query": "Bu hafta seminer var mi?",
                "unit_name": "Bilgisayar Muhendisligi",
                "limit": 3,
            },
            confidence=0.95,
            reasoning="etkinlik aramasi",
        )

    monkeypatch.setattr(
        main_module,
        "plan_capability_action",
        _plan_capability_action,
    )

    router = AsyncMock()
    router.route = AsyncMock()
    event_agent = _FakeAgent("event", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=707)
    telemetry.finalize_query_log = AsyncMock()
    telemetry.record_agent_task = AsyncMock()

    async def _event_handle_task(task):
        assert task.metadata["unit_name"] == "Bilgisayar Muhendisligi"
        assert task.metadata["limit"] == 3
        return build_department_response_task(
            DepartmentResponse(
                department=Department.STUDENT_AFFAIRS,
                answer="Buldugum ilgili etkinlikler:\n1. Planli seminer",
                sources=[],
                generation_mode="vt",
            ),
            request_task=task,
            emitter_id=event_agent.agent_id,
            emitter_name=event_agent.definition.name,
        )

    event_agent.handle_task = AsyncMock(side_effect=_event_handle_task)
    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={},
        event_agent=event_agent,
        telemetry_service=telemetry,
    )

    response = await orchestrator.handle_query("Bu hafta seminer var mi?", context_id="ctx-event-gate")

    assert "Planli seminer" in response.answer
    assert response.departments_involved == ["event"]
    router.route.assert_not_awaited()
    event_agent.handle_task.assert_awaited_once()


@pytest.mark.asyncio
async def test_main_orchestrator_explicit_event_query_uses_conversation_then_llm_route(monkeypatch):
    monkeypatch.setattr(settings.capability_planner, "mode", "off")
    router = AsyncMock()
    router.route = AsyncMock(
        return_value=RoutingResult(
            departments=[],
            confidence=0.94,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.CLARIFICATION,
            reasoning="Routing LLM etkinlik capability'sini secti.",
            task_type=TaskType.PROCEDURE_QUERY,
            intent=IntentAnalysis(
                complexity="simple",
                is_personal=False,
                force_llm_synthesis=False,
                query_type="factual",
                reasoning="etkinlik aramasi",
                primary_intent="event",
                target_capability="event",
                required_slots=[],
                missing_slots=[],
            ),
        )
    )
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=703)
    telemetry.finalize_query_log = AsyncMock()
    conversation_service = AsyncMock()
    conversation_service.resolve_query = AsyncMock(
        return_value=ConversationResolution(
            original_query="Bu hafta seminer var mi?",
            effective_query="Bu hafta seminer var mi?",
            is_follow_up=False,
            used_context=False,
            active_topic=None,
            department_hints=[],
            source_hints=[],
        )
    )
    conversation_service.record_turn = AsyncMock()

    monkeypatch.setattr(
        "src.agents.event.agent.fetch_relevant_events",
        AsyncMock(return_value=[]),
    )

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={},
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
        conversation_service=conversation_service,
    )

    response = await orchestrator.handle_query(
        "Bu hafta seminer var mi?",
        context_id="ctx-event-no-conv",
    )

    assert "etkinlik bulamadim" in response.answer
    assert "Kaynak Özeti:" in response.answer
    assert "etkinlik araması" in response.answer
    assert response.departments_involved == ["event"]
    router.route.assert_awaited_once()
    conversation_service.resolve_query.assert_awaited_once()
    conversation_service.record_turn.assert_awaited_once()


@pytest.mark.asyncio
async def test_main_orchestrator_explicit_personal_query_skips_conversation_resolution():
    router = AsyncMock()
    router.route = AsyncMock(
        return_value=RoutingResult(
            departments=[Department.FINANCE],
            confidence=0.9,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.DIRECT,
            reasoning="Kisisel finans sorgusu",
            task_type=TaskType.SCHOLARSHIP_QUERY,
        )
    )
    finance_orchestrator = _FakeDepartmentOrchestrator(
        Department.FINANCE,
        "Kisisel sorunuza yanit verebilmem icin kimliginizi dogrulamam gerekiyor.",
    )
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=704)
    telemetry.finalize_query_log = AsyncMock()
    conversation_service = AsyncMock()
    conversation_service.resolve_query = AsyncMock(
        side_effect=AssertionError("explicit personal query should not wait for conversation LLM")
    )
    conversation_service.record_turn = AsyncMock()

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={Department.FINANCE: finance_orchestrator},
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
        conversation_service=conversation_service,
    )

    response = await orchestrator.handle_query(
        "Burs aliyor muyum?",
        context_id="ctx-personal-no-conv",
    )

    assert "kimliginizi dogrulamam" in response.answer
    router.route.assert_awaited_once()
    conversation_service.resolve_query.assert_not_awaited()
    conversation_service.record_turn.assert_awaited_once()


@pytest.mark.asyncio
async def test_main_orchestrator_does_not_use_question_cache_for_follow_up(monkeypatch):
    question_cache.clear()
    question_cache.configure(ttl_seconds=300, enabled=True)
    monkeypatch.setattr(settings.cache, "enabled", True)
    monkeypatch.setattr(settings.cache, "question_cache_enabled", True)

    router = AsyncMock()
    router.route = AsyncMock(
        return_value=RoutingResult(
            departments=[Department.STUDENT_AFFAIRS],
            confidence=0.92,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.DIRECT,
            reasoning="Kayit sorusu",
            task_type=TaskType.REGISTRATION_QUERY,
        )
    )
    student_orchestrator = _FakeDepartmentOrchestrator(
        Department.STUDENT_AFFAIRS,
        "Kayit cevabi",
    )
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(side_effect=[801, 802])
    telemetry.finalize_query_log = AsyncMock()
    conversation_service = AsyncMock()
    conversation_service.resolve_query = AsyncMock(
        return_value=ConversationResolution(
            original_query="Peki ne zaman?",
            effective_query="Ders kaydi ne zaman basliyor?",
            is_follow_up=True,
            used_context=True,
            active_topic="Kayit",
            department_hints=[Department.STUDENT_AFFAIRS],
            source_hints=[],
        )
    )
    conversation_service.record_turn = AsyncMock()

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={Department.STUDENT_AFFAIRS: student_orchestrator},
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
        conversation_service=conversation_service,
    )

    await orchestrator.handle_query("Peki ne zaman?", context_id="ctx-followup-cache-1")
    await orchestrator.handle_query("Peki ne zaman?", context_id="ctx-followup-cache-2")

    assert router.route.await_count == 2
    assert student_orchestrator.handle_task.await_count == 2
    assert question_cache.size == 0


@pytest.mark.asyncio
async def test_main_orchestrator_does_not_store_question_cache_for_parallel_queries(monkeypatch):
    question_cache.clear()
    question_cache.configure(ttl_seconds=300, enabled=True)
    monkeypatch.setattr(settings.cache, "enabled", True)
    monkeypatch.setattr(settings.cache, "question_cache_enabled", True)
    monkeypatch.setattr(settings.capability_planner, "mode", "off")

    router = AsyncMock()
    router.route = AsyncMock(
        return_value=RoutingResult(
            departments=[Department.STUDENT_AFFAIRS, Department.FINANCE],
            confidence=0.91,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.PARALLEL,
            reasoning="Coklu departman sorgusu",
            task_type=TaskType.REGISTRATION_QUERY,
        )
    )
    student_orchestrator = _FakeDepartmentOrchestrator(
        Department.STUDENT_AFFAIRS,
        "Kayit donemi bilgisi",
    )
    finance_orchestrator = _FakeDepartmentOrchestrator(
        Department.FINANCE,
        "Ucret bilgisi icin ogrenci tipi gerekir",
    )
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(side_effect=[901, 902])
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

    await orchestrator.handle_query(
        "Kayit yenileme ucreti ne kadar ve ne zaman yapilir?",
        context_id="ctx-parallel-cache-1",
    )
    await orchestrator.handle_query(
        "Kayit yenileme ucreti ne kadar ve ne zaman yapilir?",
        context_id="ctx-parallel-cache-2",
    )

    assert router.route.await_count == 2
    assert student_orchestrator.handle_task.await_count == 2
    assert finance_orchestrator.handle_task.await_count == 2
    assert question_cache.size == 0


@pytest.mark.asyncio
async def test_main_orchestrator_does_not_store_question_cache_for_llm_answers(monkeypatch):
    question_cache.clear()
    question_cache.configure(ttl_seconds=300, enabled=True)
    monkeypatch.setattr(settings.cache, "enabled", True)
    monkeypatch.setattr(settings.cache, "question_cache_enabled", True)

    router = AsyncMock()
    router.route = AsyncMock(
        return_value=RoutingResult(
            departments=[Department.ACADEMIC_PROGRAMS],
            confidence=0.88,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.DIRECT,
            reasoning="Akademik sorgu",
            task_type=TaskType.COURSE_QUERY,
        )
    )
    llm_response = DepartmentResponse(
        department=Department.ACADEMIC_PROGRAMS,
        answer="LLM destekli akademik cevap",
        sources=[],
        generation_mode="llm",
    )
    academic_orchestrator = SimpleNamespace(
        department=Department.ACADEMIC_PROGRAMS,
        handle_task=AsyncMock(
            side_effect=lambda task, *args, **kwargs: build_department_response_task(
                llm_response,
                request_task=task,
                emitter_id="academic_programs_orchestrator",
                emitter_name="academic_programs Orchestrator",
            )
        ),
    )
    announcement_agent = _FakeAgent("announcement", Department.STUDENT_AFFAIRS)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(side_effect=[1001, 1002])
    telemetry.finalize_query_log = AsyncMock()

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={Department.ACADEMIC_PROGRAMS: academic_orchestrator},
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
    )

    await orchestrator.handle_query(
        "BIL104 dersinin kapsamli aciklamasi nedir?",
        context_id="ctx-llm-cache-1",
    )
    await orchestrator.handle_query(
        "BIL104 dersinin kapsamli aciklamasi nedir?",
        context_id="ctx-llm-cache-2",
    )

    assert router.route.await_count == 2
    assert academic_orchestrator.handle_task.await_count == 2
    assert question_cache.size == 0
