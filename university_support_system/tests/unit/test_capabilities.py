from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.a2a.helpers import A2AQueryPayload
from src.a2a.helpers import build_query_task
from src.agents.academic.international_agent import InternationalAgent
from src.agents.base import BaseSpecialistAgent
from src.agents.academic.curriculum_agent import CurriculumAgent
from src.agents.finance.tuition_agent import TuitionAgent
from src.agents.student.registration_agent import RegistrationAgent
from src.capabilities import announcement_executor, curriculum_executor, event_executor, finance_executor
from src.capabilities.academic_formatting import deterministic_answer_for_result
from src.capabilities.executor import execute_capability_action
from src.capabilities.models import CapabilityAction, ExecutionResult
from src.capabilities.planner import parse_planner_response, plan_capability_action
from src.capabilities.registry import validate_capability_action
from src.core.config import CapabilityPlannerSettings, settings
from src.core.constants import ConfidenceLevel, Department, RoutingStrategy, TaskType
from src.db.conversation_context import ConversationResolution
from src.db.announcements import AnnouncementRecord
from src.db.events import EventRecord
from src.db.schemas import RoutingResult
from src.orchestrators.main import MainOrchestrator


def test_capability_planner_defaults_to_router_first_decision():
    settings = CapabilityPlannerSettings()

    assert settings.mode == "on"
    assert settings.enabled is True
    assert settings.should_apply is True
    assert settings.pre_route_enabled is False
    assert settings.scope_set == {
        "academic_programs",
        "student_affairs",
        "finance",
        "announcement",
        "event",
    }


def test_capability_planner_rollout_modes():
    assert CapabilityPlannerSettings(mode="shadow").enabled is True
    assert CapabilityPlannerSettings(mode="shadow").should_apply is False
    assert CapabilityPlannerSettings(mode="pilot").should_apply is True
    assert CapabilityPlannerSettings(mode="on").should_apply is True


def test_deterministic_formatter_uses_ascii_safe_fallback_text():
    answer = deterministic_answer_for_result(
        query="EEM mufredatinda Veri Yapilari var mi?",
        capability="course.exists_in_program",
        records=[],
        metadata={
            "program": "Elektrik-Elektronik Muhendisligi",
            "course": "Veri Yapilari",
        },
        message=None,
    )

    assert "mufredat veritabaninda" in answer
    assert "kayit bulunamadi" in answer
    assert "\u00c3" not in answer


def test_registry_validates_missing_params():
    action = CapabilityAction(
        capability="course.exists_in_program",
        params={"program": "Bilgisayar Muhendisligi"},
    )

    result = validate_capability_action(action)

    assert result.valid is False
    assert result.error == "missing_params"
    assert "course" in result.missing_params


def test_parse_planner_response_accepts_json_fence():
    response = """```json
    {"capability":"course.detail","params":{"course_code":"BIL203"},"confidence":0.82}
    ```"""

    action = parse_planner_response(response)

    assert action is not None
    assert action.capability == "course.detail"
    assert action.params["course_code"] == "BIL203"
    assert action.confidence == pytest.approx(0.82)


def test_parse_planner_response_accepts_plan_contract_fields():
    response = {
        "capability": "student_affairs.policy_lookup",
        "intent": "single_exam_eligibility",
        "params": {
            "query": "Hic almadigim bir dersten tek derse girebilir miyim?",
            "topic": "tek ders",
        },
        "answer_contract": {
            "must_answer": ["hic alinmamis ders", "devam sarti"],
        },
        "evidence_contract": {
            "preferred_sources": ["sik_sorulan_sorular", "on_lisans_yonetmeligi"],
        },
        "fallback_route": "rag",
        "confidence": 0.91,
    }

    action = parse_planner_response(response)

    assert action is not None
    assert action.capability == "student_affairs.policy_lookup"
    assert action.intent == "single_exam_eligibility"
    assert action.answer_contract["must_answer"] == ["hic alinmamis ders", "devam sarti"]
    plan = action.to_plan_decision()
    assert plan.capability == action.capability
    assert plan.evidence_contract["preferred_sources"][0] == "sik_sorulan_sorular"


def test_registry_validates_student_affairs_policy_lookup():
    action = CapabilityAction(
        capability="student_affairs.policy_lookup",
        params={"query": "Yaz okulu uzerinden cozum var mi?"},
        confidence=0.8,
    )

    result = validate_capability_action(action)

    assert result.valid is True


def test_registry_validates_international_policy_lookup():
    action = CapabilityAction(
        capability="international.policy_lookup",
        params={"query": "Uluslararasi ogrenci olarak kayit icin hangi belgeler gerekir?"},
        confidence=0.9,
    )

    result = validate_capability_action(action)

    assert result.valid is True


def test_parse_planner_response_accepts_international_policy_contract():
    response = {
        "capability": "international.policy_lookup",
        "intent": "international_registration_documents",
        "params": {
            "query": "Uluslararasi ogrenci olarak kayit icin hangi belgeler gerekir?",
            "topic": "uluslararasi kayit",
        },
        "answer_contract": {
            "must_answer": ["kayit icin gerekli belgeler", "basvuru/kesin kayit ayrimi"],
        },
        "evidence_contract": {
            "preferred_sources": ["uluslararasi ogrenci kayit"],
            "avoid_sources": ["konukevi", "ozel ogrenci"],
        },
        "confidence": 0.9,
    }

    action = parse_planner_response(response)

    assert action is not None
    assert action.capability == "international.policy_lookup"
    assert action.intent == "international_registration_documents"
    assert action.evidence_contract["avoid_sources"] == ["konukevi", "ozel ogrenci"]


def test_conversation_resolution_builds_frame_for_planner_context():
    resolution = ConversationResolution(
        original_query="Kac AKTS?",
        effective_query="BIL203 kac AKTS?",
        is_follow_up=True,
        used_context=True,
        active_topic="Mufredat ve Ders Yapisi",
        department_hints=[Department.ACADEMIC_PROGRAMS],
        source_hints=["BIL203"],
        task_type_hint=TaskType.COURSE_QUERY,
        standalone_query="BIL203 kac AKTS?",
    )

    assert resolution.frame is not None
    frame = resolution.frame.to_prompt_context()
    assert frame["active_course_code"] == "BIL203"
    assert frame["department_hints"] == ["academic_programs"]
    assert frame["task_type_hint"] == "course_query"


@pytest.mark.asyncio
async def test_planner_uses_routing_role_and_returns_action():
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(
        return_value={
            "capability": "curriculum.semester_courses",
            "params": {"program": "Bilgisayar Muhendisligi", "semester": 5},
            "confidence": 0.9,
        }
    )

    action = await plan_capability_action(
        query="Bilgisayar muhendisligi 5. yariyil dersleri neler?",
        departments=[Department.ACADEMIC_PROGRAMS],
        llm_service=llm_service,
        context={},
        timeout_seconds=2,
    )

    assert action is not None
    assert action.capability == "curriculum.semester_courses"
    llm_service.generate.assert_awaited_once()
    _, kwargs = llm_service.generate.call_args
    assert kwargs["model_role"] == "routing"
    assert kwargs["json_mode"] is True


@pytest.mark.asyncio
async def test_main_orchestrator_shadow_mode_plans_without_applying(monkeypatch):
    planner_settings = CapabilityPlannerSettings(mode="shadow")
    monkeypatch.setattr(settings, "capability_planner", planner_settings)
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(
        return_value={
            "capability": "course.detail",
            "params": {"course_code": "BIL203"},
            "confidence": 0.9,
        }
    )
    orchestrator = MainOrchestrator(
        department_orchestrators={},
        announcement_agent=object(),
        event_agent=object(),
        telemetry_service=object(),
        llm_service=llm_service,
    )

    payload = await orchestrator._maybe_plan_capability(
        query="BIL203 kac AKTS?",
        routing=_routing_result([Department.ACADEMIC_PROGRAMS]),
        conversation_resolution=_conversation_resolution("BIL203 kac AKTS?"),
        student_department=None,
        student_faculty=None,
        llm_profile=None,
    )

    assert payload is not None
    assert payload["mode"] == "shadow"
    assert payload["apply"] is False
    assert payload["action"]["capability"] == "course.detail"
    llm_service.generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_main_orchestrator_on_mode_plans_against_full_scope(monkeypatch):
    planner_settings = CapabilityPlannerSettings(mode="on")
    monkeypatch.setattr(settings, "capability_planner", planner_settings)
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(
        return_value={
            "capability": "calendar.academic_date",
            "params": {
                "query": "Bilgisayar muhendisligi icin bahar donemi son ders tarihi nedir?"
            },
            "confidence": 0.92,
        }
    )
    orchestrator = MainOrchestrator(
        department_orchestrators={},
        announcement_agent=object(),
        event_agent=object(),
        telemetry_service=object(),
        llm_service=llm_service,
    )

    payload = await orchestrator._maybe_plan_capability(
        query="Bilgisayar muhendisligi icin bahar donemi son ders tarihi nedir?",
        routing=_routing_result([Department.ACADEMIC_PROGRAMS]),
        conversation_resolution=_conversation_resolution(
            "Bilgisayar muhendisligi icin bahar donemi son ders tarihi nedir?"
        ),
        student_department=None,
        student_faculty=None,
        llm_profile=None,
    )

    assert payload is not None
    assert payload["apply"] is True
    assert payload["action"]["capability"] == "calendar.academic_date"
    assert payload["plan_decision"]["capability"] == "calendar.academic_date"
    assert payload["legacy_routing"]["departments"] == ["academic_programs"]
    prompt = llm_service.generate.await_args.args[0]
    assert "calendar.academic_date" in prompt
    assert "course.exists_in_program" in prompt
    assert "announcement.search" in prompt
    assert "event.search" in prompt


@pytest.mark.asyncio
async def test_main_orchestrator_pre_route_planner_can_build_owner_routing(monkeypatch):
    planner_settings = CapabilityPlannerSettings(
        mode="on",
        pre_route_enabled=True,
        pre_route_confidence_threshold=0.75,
    )
    monkeypatch.setattr(settings, "capability_planner", planner_settings)
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(
        return_value={
            "capability": "calendar.academic_date",
            "departments": ["student_affairs"],
            "params": {"query": "Akademik takvimde derslerin bitimi ne zaman?"},
            "confidence": 0.9,
        }
    )
    orchestrator = MainOrchestrator(
        department_orchestrators={},
        announcement_agent=object(),
        event_agent=object(),
        telemetry_service=object(),
        llm_service=llm_service,
    )

    payload = await orchestrator._maybe_plan_capability_pre_route(
        query="Akademik takvimde derslerin bitimi ne zaman?",
        conversation_resolution=_conversation_resolution(
            "Akademik takvimde derslerin bitimi ne zaman?"
        ),
        student_department=None,
        student_faculty=None,
        student_type=None,
        llm_profile=None,
    )
    routing = orchestrator._routing_from_capability_payload(payload)

    assert payload is not None
    assert payload["pre_route"] is True
    assert routing is not None
    assert routing.departments == [Department.STUDENT_AFFAIRS]
    assert routing.reasoning and "legacy router skipped" in routing.reasoning
    llm_service.generate.assert_awaited_once()


def test_main_orchestrator_pre_route_planner_rejects_low_confidence():
    payload = {
        "apply": True,
        "pre_route": True,
        "action": {
            "capability": "calendar.academic_date",
            "departments": ["student_affairs"],
            "params": {"query": "Akademik takvim"},
            "confidence": 0.5,
        },
    }

    assert MainOrchestrator._routing_from_capability_payload(payload) is None


@pytest.mark.asyncio
async def test_main_orchestrator_preserves_calendar_row_query_when_planner_uses_broad_label(monkeypatch):
    planner_settings = CapabilityPlannerSettings(mode="on")
    monkeypatch.setattr(settings, "capability_planner", planner_settings)
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(
        return_value={
            "capability": "calendar.academic_date",
            "params": {"query": "Akademik takvim"},
            "confidence": 0.91,
        }
    )
    orchestrator = MainOrchestrator(
        department_orchestrators={},
        announcement_agent=object(),
        event_agent=object(),
        telemetry_service=object(),
        llm_service=llm_service,
    )

    payload = await orchestrator._maybe_plan_capability(
        query="Akademik takvimde derslerin bitimi ne zaman?",
        routing=_routing_result([Department.STUDENT_AFFAIRS]),
        conversation_resolution=_conversation_resolution(
            "Akademik takvimde derslerin bitimi ne zaman?"
        ),
        student_department=None,
        student_faculty=None,
        llm_profile=None,
    )

    assert payload is not None
    assert payload["action"]["capability"] == "calendar.academic_date"
    assert (
        payload["action"]["params"]["query"]
        == "Akademik takvimde derslerin bitimi ne zaman?"
    )


def test_capability_routing_uses_planner_selected_departments(monkeypatch):
    planner_settings = CapabilityPlannerSettings(mode="on")
    monkeypatch.setattr(settings, "capability_planner", planner_settings)
    orchestrator = MainOrchestrator(
        department_orchestrators={},
        announcement_agent=object(),
        event_agent=object(),
        telemetry_service=object(),
        llm_service=AsyncMock(),
    )

    routing = _routing_result([Department.ACADEMIC_PROGRAMS])
    payload = {
        "mode": "on",
        "apply": True,
        "action": {
            "capability": "calendar.academic_date",
            "departments": ["student_affairs"],
            "params": {"query": "Bahar donemi son ders tarihi nedir?"},
            "confidence": 0.9,
        },
    }

    updated = orchestrator._routing_for_capability_owner(routing, payload)

    assert updated is not None
    assert updated.departments == [Department.STUDENT_AFFAIRS]
    assert updated.strategy == RoutingStrategy.DIRECT


def test_capability_routing_does_not_infer_department_when_planner_omits_it(monkeypatch):
    planner_settings = CapabilityPlannerSettings(mode="on")
    monkeypatch.setattr(settings, "capability_planner", planner_settings)
    orchestrator = MainOrchestrator(
        department_orchestrators={},
        announcement_agent=object(),
        event_agent=object(),
        telemetry_service=object(),
        llm_service=AsyncMock(),
    )

    routing = _routing_result([Department.ACADEMIC_PROGRAMS])
    payload = {
        "mode": "on",
        "apply": True,
        "action": {
            "capability": "student_affairs.policy_lookup",
            "params": {"query": "Hic almadigim dersten tek derse girebilir miyim?"},
            "confidence": 0.9,
        },
    }

    updated = orchestrator._routing_for_capability_owner(routing, payload)

    assert updated is None


def test_capability_routing_keeps_international_policy_on_planner_department(monkeypatch):
    planner_settings = CapabilityPlannerSettings(mode="on")
    monkeypatch.setattr(settings, "capability_planner", planner_settings)
    orchestrator = MainOrchestrator(
        department_orchestrators={},
        announcement_agent=object(),
        event_agent=object(),
        telemetry_service=object(),
        llm_service=AsyncMock(),
    )

    routing = _routing_result([Department.STUDENT_AFFAIRS])
    payload = {
        "mode": "on",
        "apply": True,
        "action": {
            "capability": "international.policy_lookup",
            "departments": ["academic_programs"],
            "params": {
                "query": "Uluslararasi ogrenci olarak kayit icin hangi belgeler gerekir?"
            },
            "confidence": 0.9,
        },
    }

    updated = orchestrator._routing_for_capability_owner(routing, payload)

    assert updated is not None
    assert updated.departments == [Department.ACADEMIC_PROGRAMS]
    assert updated.strategy == RoutingStrategy.DIRECT


@pytest.mark.asyncio
async def test_main_orchestrator_pilot_skips_multi_department_planner(monkeypatch):
    planner_settings = CapabilityPlannerSettings(mode="pilot")
    monkeypatch.setattr(settings, "capability_planner", planner_settings)
    llm_service = AsyncMock()
    orchestrator = MainOrchestrator(
        department_orchestrators={},
        announcement_agent=object(),
        event_agent=object(),
        telemetry_service=object(),
        llm_service=llm_service,
    )

    payload = await orchestrator._maybe_plan_capability(
        query="CAP basvuru tarihleri ne zaman?",
        routing=_routing_result([Department.ACADEMIC_PROGRAMS, Department.STUDENT_AFFAIRS]),
        conversation_resolution=_conversation_resolution("CAP basvuru tarihleri ne zaman?"),
        student_department=None,
        student_faculty=None,
        llm_profile=None,
    )

    assert payload is not None
    assert payload["apply"] is False
    assert payload["skipped"] == "pilot_requires_single_scoped_department"
    assert payload["plan_decision"] is None
    assert payload["legacy_routing"]["departments"] == [
        "academic_programs",
        "student_affairs",
    ]
    llm_service.generate.assert_not_called()


@pytest.mark.asyncio
async def test_main_orchestrator_pilot_applies_single_academic_plan(monkeypatch):
    planner_settings = CapabilityPlannerSettings(mode="pilot")
    monkeypatch.setattr(settings, "capability_planner", planner_settings)
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(
        return_value={
            "capability": "curriculum.semester_courses",
            "params": {"program": "Bilgisayar Muhendisligi", "semester": 5},
            "confidence": 0.88,
        }
    )
    orchestrator = MainOrchestrator(
        department_orchestrators={},
        announcement_agent=object(),
        event_agent=object(),
        telemetry_service=object(),
        llm_service=llm_service,
    )

    payload = await orchestrator._maybe_plan_capability(
        query="Bilgisayar Muhendisligi 5. yariyil dersleri neler?",
        routing=_routing_result([Department.ACADEMIC_PROGRAMS]),
        conversation_resolution=_conversation_resolution(
            "Bilgisayar Muhendisligi 5. yariyil dersleri neler?"
        ),
        student_department=None,
        student_faculty=None,
        llm_profile=None,
    )

    assert payload is not None
    assert payload["apply"] is True
    assert payload["action"]["capability"] == "curriculum.semester_courses"
    assert payload["action"]["params"]["semester"] == 5


@pytest.mark.asyncio
async def test_main_orchestrator_pilot_applies_single_student_affairs_calendar_plan(monkeypatch):
    planner_settings = CapabilityPlannerSettings(mode="pilot", scope="student_affairs")
    monkeypatch.setattr(settings, "capability_planner", planner_settings)
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(
        return_value={
            "capability": "calendar.academic_date",
            "params": {"query": "Akademik takvimde derslerin bitimi ne zaman?"},
            "confidence": 0.91,
        }
    )
    orchestrator = MainOrchestrator(
        department_orchestrators={},
        announcement_agent=object(),
        event_agent=object(),
        telemetry_service=object(),
        llm_service=llm_service,
    )

    payload = await orchestrator._maybe_plan_capability(
        query="Akademik takvimde derslerin bitimi ne zaman?",
        routing=_routing_result([Department.STUDENT_AFFAIRS]),
        conversation_resolution=_conversation_resolution(
            "Akademik takvimde derslerin bitimi ne zaman?"
        ),
        student_department=None,
        student_faculty=None,
        llm_profile=None,
    )

    assert payload is not None
    assert payload["apply"] is True
    assert payload["action"]["capability"] == "calendar.academic_date"
    llm_service.generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_main_orchestrator_pilot_applies_single_finance_plan(monkeypatch):
    planner_settings = CapabilityPlannerSettings(mode="pilot", scope="finance")
    monkeypatch.setattr(settings, "capability_planner", planner_settings)
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(
        return_value={
            "capability": "finance.tuition_fee",
            "params": {
                "student_type": "domestic",
                "unit_name": "egitim fakultesi",
                "query": "Fizik ogretmenligi ucreti ne kadar?",
            },
            "confidence": 0.91,
        }
    )
    orchestrator = MainOrchestrator(
        department_orchestrators={},
        announcement_agent=object(),
        event_agent=object(),
        telemetry_service=object(),
        llm_service=llm_service,
    )

    payload = await orchestrator._maybe_plan_capability(
        query="Fizik ogretmenligi ucreti ne kadar?",
        routing=_routing_result([Department.FINANCE]),
        conversation_resolution=_conversation_resolution(
            "Fizik ogretmenligi ucreti ne kadar?"
        ),
        student_department=None,
        student_faculty=None,
        student_type="domestic",
        llm_profile=None,
    )

    assert payload is not None
    assert payload["apply"] is True
    assert payload["action"]["capability"] == "finance.tuition_fee"
    llm_service.generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_short_circuit_gate_shadow_records_but_allows_legacy(monkeypatch):
    monkeypatch.setattr(
        settings,
        "capability_planner",
        CapabilityPlannerSettings(mode="shadow", scope="event"),
    )
    monkeypatch.setattr(settings.llm, "query_normalization_enabled", True)
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(
        return_value=(
            '{"capability":"none",'
            '"params":{},'
            '"confidence":0.88,'
            '"fallback":"rag",'
            '"reasoning":"etkinlik degil"}'
        )
    )
    orchestrator = MainOrchestrator(
        department_orchestrators={},
        announcement_agent=object(),
        event_agent=object(),
        telemetry_service=object(),
        llm_service=llm_service,
    )

    decision = await orchestrator._evaluate_short_circuit_gate(
        query="Bu hafta seminer var mi?",
        capability="event",
        llm_profile=None,
        heuristic_reason="Erken etkinlik sinyali.",
    )

    assert decision["allow"] is True
    assert decision["confirmed"] is False
    assert decision["mode"] == "shadow"
    assert decision["target_capability"] == "none"
    llm_service.generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_short_circuit_gate_pilot_blocks_unconfirmed_heuristic(monkeypatch):
    monkeypatch.setattr(
        settings,
        "capability_planner",
        CapabilityPlannerSettings(mode="pilot", scope="event"),
    )
    monkeypatch.setattr(settings.llm, "query_normalization_enabled", True)
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(
        return_value=(
            '{"capability":"none",'
            '"params":{},'
            '"confidence":0.92,'
            '"fallback":"rag",'
            '"reasoning":"kayit sorusu"}'
        )
    )
    orchestrator = MainOrchestrator(
        department_orchestrators={},
        announcement_agent=object(),
        event_agent=object(),
        telemetry_service=object(),
        llm_service=llm_service,
    )

    decision = await orchestrator._evaluate_short_circuit_gate(
        query="Ders kaydi ne zaman?",
        capability="event",
        llm_profile=None,
        heuristic_reason="Erken etkinlik sinyali.",
    )

    assert decision["allow"] is False
    assert decision["confirmed"] is False
    assert decision["mode"] == "pilot"
    assert decision["target_capability"] == "none"


@pytest.mark.asyncio
async def test_short_circuit_gate_pilot_allows_confirmed_capability(monkeypatch):
    monkeypatch.setattr(
        settings,
        "capability_planner",
        CapabilityPlannerSettings(mode="pilot", scope="announcement"),
    )
    monkeypatch.setattr(settings.llm, "query_normalization_enabled", True)
    llm_service = AsyncMock()
    llm_service.generate = AsyncMock(
        return_value=(
            '{"capability":"announcement.search",'
            '"params":{"query":"Guncel duyurular nelerdir?"},'
            '"confidence":0.91,'
            '"reasoning":"duyuru arama"}'
        )
    )
    orchestrator = MainOrchestrator(
        department_orchestrators={},
        announcement_agent=object(),
        event_agent=object(),
        telemetry_service=object(),
        llm_service=llm_service,
    )

    decision = await orchestrator._evaluate_short_circuit_gate(
        query="Guncel duyurular",
        capability="announcement",
        llm_profile=None,
        heuristic_reason="Duyuru keyword sinyali.",
    )

    assert decision["allow"] is True
    assert decision["confirmed"] is True
    assert decision["target_capability"] == "announcement.search"
    assert decision["routing_reason"] == "duyuru arama"


@pytest.mark.asyncio
async def test_executor_announcement_search_uses_existing_fetcher(monkeypatch):
    async def fake_fetch_relevant_announcements(query_text, **kwargs):
        return [
            AnnouncementRecord(
                id=10,
                title="Sinav Programi Duyurusu",
                display_summary="Program yayinlandi.",
                summary="Program yayinlandi.",
                original_text="Program yayinlandi.",
                source_url="https://omu.edu.tr/duyuru",
                faculty=kwargs.get("faculty"),
                unit_name=kwargs.get("unit_name"),
                department="student_affairs",
                published_at=None,
            )
        ]

    monkeypatch.setattr(
        announcement_executor,
        "fetch_relevant_announcements",
        fake_fetch_relevant_announcements,
    )

    result = await execute_capability_action(
        {
            "capability": "announcement.search",
            "params": {
                "query": "Sinav programi duyurusu var mi?",
                "faculty": "Muhendislik Fakultesi",
                "limit": 3,
            },
            "confidence": 0.9,
        }
    )

    assert result.success is True
    assert result.capability == "announcement.search"
    assert result.records[0]["title"] == "Sinav Programi Duyurusu"
    assert result.metadata["record_count"] == 1
    assert result.fallback_allowed is False


@pytest.mark.asyncio
async def test_executor_event_search_uses_existing_fetcher(monkeypatch):
    async def fake_fetch_relevant_events(query_text, **kwargs):
        return [
            EventRecord(
                id=20,
                title="Yapay Zeka Semineri",
                display_summary="Seminer duyurusu.",
                summary="Seminer duyurusu.",
                original_text="Seminer duyurusu.",
                source_url="https://omu.edu.tr/etkinlik",
                faculty=kwargs.get("faculty"),
                unit_name=kwargs.get("unit_name"),
                department="academic_programs",
                event_type="seminer",
                location="Mavi Salon",
                organizer="Bilgisayar Muhendisligi",
                starts_at=None,
                ends_at=None,
                all_day=True,
            )
        ]

    monkeypatch.setattr(
        event_executor,
        "fetch_relevant_events",
        fake_fetch_relevant_events,
    )

    result = await execute_capability_action(
        {
            "capability": "event.search",
            "params": {
                "query": "Bu hafta seminer var mi?",
                "unit_name": "Bilgisayar Muhendisligi",
            },
            "confidence": 0.9,
        }
    )

    assert result.success is True
    assert result.capability == "event.search"
    assert result.records[0]["title"] == "Yapay Zeka Semineri"
    assert result.records[0]["location"] == "Mavi Salon"
    assert result.fallback_allowed is False


@pytest.mark.asyncio
async def test_executor_course_exists_uses_program_and_course(monkeypatch):
    async def fake_fetch_courses_by_title(query_text, department=None, limit=5):
        return [
            {
                "course_code": "BIL203",
                "course_name": "Veri Yapilari",
                "department": department,
                "curriculum_semester": 3,
                "akts": 5,
            }
        ]

    monkeypatch.setattr(
        curriculum_executor,
        "fetch_courses_by_title",
        fake_fetch_courses_by_title,
    )

    result = await execute_capability_action(
        {
            "capability": "course.exists_in_program",
            "params": {
                "program": "Bilgisayar Muhendisligi",
                "course": "Veri Yapilari",
            },
            "confidence": 0.9,
        }
    )

    assert result.success is True
    assert result.capability == "course.exists_in_program"
    assert result.metadata["exists"] is True
    assert result.records[0]["course_code"] == "BIL203"


@pytest.mark.asyncio
async def test_executor_weekly_program_maps_seventh_semester_to_fourth_class(monkeypatch):
    async def fake_fetch_schedule_slots_by_department(department):
        assert department == "Bilgisayar Muhendisligi"
        return [
            {
                "term": "guz",
                "schedule_group": "4. SINIF",
                "course_name": "Bilgi Guvenligi",
                "day_of_week": "Pazartesi",
                "start_time": "09:15:00",
            },
            {
                "term": "bahar",
                "schedule_group": "4. SINIF",
                "course_name": "Bitirme Projesi",
                "day_of_week": "Persembe",
                "start_time": "08:15:00",
            },
            {
                "term": "guz",
                "schedule_group": "3. SINIF",
                "course_name": "Sistem Programlama",
                "day_of_week": "Persembe",
                "start_time": "09:15:00",
            },
        ]

    monkeypatch.setattr(
        curriculum_executor,
        "fetch_schedule_slots_by_department",
        fake_fetch_schedule_slots_by_department,
    )

    result = await execute_capability_action(
        {
            "capability": "schedule.weekly_program",
            "params": {
                "program": "Bilgisayar Muhendisligi",
                "semester": 7,
            },
            "confidence": 0.9,
        }
    )

    assert result.success is True
    assert result.records == [
        {
            "term": "guz",
            "schedule_group": "4. SINIF",
            "course_name": "Bilgi Guvenligi",
            "day_of_week": "Pazartesi",
            "start_time": "09:15:00",
        }
    ]
    assert result.metadata["class_year"] == 4
    assert result.metadata["term"] == "guz"


@pytest.mark.asyncio
async def test_executor_calendar_academic_date_uses_structured_calendar():
    result = await execute_capability_action(
        {
            "capability": "calendar.academic_date",
            "params": {
                "query": "Bilgisayar muhendisligi icin bahar donemi son ders tarihi nedir?"
            },
            "confidence": 0.9,
        }
    )

    assert result.success is True
    assert result.capability == "calendar.academic_date"
    assert result.records
    assert result.records[0]["label"] == "Derslerin Bitimi"
    assert "22 May" in result.metadata["answer"]


@pytest.mark.asyncio
async def test_executor_calendar_academic_date_allows_rag_fallback_when_no_row():
    result = await execute_capability_action(
        {
            "capability": "calendar.academic_date",
            "params": {"query": "Yaz okulu basvuru tarihleri ne zaman?"},
            "confidence": 0.9,
        }
    )

    assert result.success is True
    assert result.records == []
    assert result.fallback_allowed is True
    assert result.authoritative_no_records is False


@pytest.mark.asyncio
async def test_executor_policy_lookup_is_whitelisted_planning_result():
    result = await execute_capability_action(
        {
            "capability": "student_affairs.policy_lookup",
            "params": {
                "query": "Hic almadigim bir dersten tek derse girebilir miyim?",
                "topic": "tek ders",
                "must_answer": ["devam sarti"],
            },
            "confidence": 0.9,
        }
    )

    assert result.success is True
    assert result.capability == "student_affairs.policy_lookup"
    assert result.metadata["policy_lookup"] is True
    assert result.metadata["must_answer"] == ["devam sarti"]


@pytest.mark.asyncio
async def test_executor_international_policy_lookup_is_whitelisted_planning_result():
    result = await execute_capability_action(
        {
            "capability": "international.policy_lookup",
            "params": {
                "query": "Uluslararasi ogrenci olarak kayit icin hangi belgeler gerekir?",
                "topic": "uluslararasi kayit",
                "preferred_sources": ["uluslararasi ogrenci kayit"],
                "avoid_sources": ["konukevi"],
            },
            "confidence": 0.9,
        }
    )

    assert result.success is True
    assert result.capability == "international.policy_lookup"
    assert result.metadata["policy_lookup"] is True
    assert result.metadata["preferred_sources"] == ["uluslararasi ogrenci kayit"]
    assert result.metadata["avoid_sources"] == ["konukevi"]


def test_plan_evidence_source_bias_boosts_preferred_and_penalizes_avoid_sources():
    results = [
        {
            "source": "ogrenci_konukevi_uygulama_yonergesi.pdf",
            "content": "Konukevi icin belge talebi bilgileri.",
            "score": 0.8,
        },
        {
            "source": "uluslararasi_ogrenci_kayit_taahhut_ve_evrak_teslim_formu.pdf",
            "content": "Uluslararasi ogrenci kayit ve evrak teslim sureci.",
            "score": 0.5,
        },
    ]

    adjusted = BaseSpecialistAgent._apply_plan_evidence_source_bias(
        results,
        {
            "evidence_contract": {
                "preferred_sources": ["uluslararasi ogrenci kayit", "evrak teslim"],
                "avoid_sources": ["konukevi"],
            }
        },
    )

    assert adjusted[0]["source"] == "uluslararasi_ogrenci_kayit_taahhut_ve_evrak_teslim_formu.pdf"
    assert adjusted[0]["score"] > results[1]["score"]
    assert adjusted[1]["score"] < results[0]["score"]


@pytest.mark.asyncio
async def test_executor_finance_tuition_fee_uses_catalog(monkeypatch):
    async def fake_catalog_lookup(*, student_type, unit_name, academic_year=None):
        assert student_type == "domestic"
        assert unit_name == "egitim fakultesi"
        return {
            "academic_year": "2025-2026",
            "student_type": "domestic",
            "unit_name": "Egitim Fakultesi",
            "annual_amount": 1759.0,
            "semester_amount": 879.5,
            "currency": "TRY",
            "source_document": "turk_ogrenci_ucretleri.pdf",
        }

    monkeypatch.setattr(
        finance_executor,
        "fetch_tuition_fee_catalog_entry",
        fake_catalog_lookup,
    )

    result = await execute_capability_action(
        {
            "capability": "finance.tuition_fee",
            "params": {
                "student_type": "Turk ogrenci",
                "unit_name": "egitim fakultesi",
                "query": "Fizik ogretmenligi ucreti ne kadar?",
            },
            "confidence": 0.9,
        }
    )

    assert result.success is True
    assert result.capability == "finance.tuition_fee"
    assert result.records[0]["annual_amount"] == 1759.0


@pytest.mark.asyncio
async def test_executor_rejects_missing_required_params_without_crashing():
    result = await execute_capability_action(
        {
            "capability": "curriculum.semester_courses",
            "params": {"program": "Bilgisayar Muhendisligi"},
            "confidence": 0.9,
        }
    )

    assert result.success is False
    assert result.error == "missing_params"
    assert "semester" in result.missing_params


@pytest.mark.asyncio
async def test_executor_unknown_capability_allows_legacy_fallback():
    result = await execute_capability_action(
        {
            "capability": "course.not_registered",
            "params": {"course_code": "BIL203"},
            "confidence": 0.9,
        }
    )

    assert result.success is False
    assert result.error == "unknown_capability"
    assert result.fallback_allowed is True


def test_a2a_payload_carries_capability_planner_metadata():
    payload = A2AQueryPayload(
        query_text="BIL203 kac AKTS?",
        context_id="ctx-1",
        capability_planner={
            "mode": "pilot",
            "apply": True,
            "action": {"capability": "course.detail", "params": {"course_code": "BIL203"}},
        },
    )

    metadata = payload.to_metadata()

    assert metadata["capability_planner"]["mode"] == "pilot"
    assert metadata["capability_planner"]["apply"] is True


@pytest.mark.asyncio
async def test_curriculum_agent_uses_capability_payload_when_apply_true(monkeypatch):
    async def fake_execute(action):
        return ExecutionResult(
            success=True,
            capability=action.capability,
            params=dict(action.params),
            records=[
                {
                    "course_code": "BIL203",
                    "course_name": "Veri Yapilari",
                    "credits": 3,
                    "akts": 5,
                }
            ],
            metadata={"course_code": "BIL203"},
            authoritative_no_records=True,
            fallback_allowed=False,
        )

    monkeypatch.setattr(
        "src.agents.academic.curriculum_agent.execute_capability_action",
        fake_execute,
    )
    monkeypatch.setattr(settings.capability_planner, "synthesize_with_llm", False)

    task = build_query_task(
        A2AQueryPayload(
            query_text="BIL203 kac AKTS?",
            context_id="ctx-capability-agent",
            capability_planner={
                "mode": "pilot",
                "apply": True,
                "action": {
                    "capability": "course.detail",
                    "params": {"course_code": "BIL203"},
                    "confidence": 0.9,
                },
            },
        )
    )
    agent = CurriculumAgent(llm_service=AsyncMock())

    response = await agent.handle_department_task(task)

    assert response.generation_mode == "vt"
    assert response.db_data["capability"] == "course.detail"
    assert "5 AKTS" in response.answer


@pytest.mark.asyncio
async def test_registration_agent_uses_calendar_capability_payload():
    task = build_query_task(
        A2AQueryPayload(
            query_text="Akademik takvimde derslerin bitimi ne zaman?",
            context_id="ctx-calendar-capability",
            capability_planner={
                "mode": "pilot",
                "apply": True,
                "action": {
                    "capability": "calendar.academic_date",
                    "params": {
                        "query": "Akademik takvimde derslerin bitimi ne zaman?"
                    },
                    "confidence": 0.9,
                },
            },
        )
    )
    agent = RegistrationAgent(llm_service=AsyncMock())

    response = await agent.handle_department_task(task)

    assert response.generation_mode == "vt"
    assert response.db_data["capability"] == "calendar.academic_date"
    assert "derslerin bitimi" in response.answer
    assert "22 May" in response.answer


def test_registration_agent_prepares_policy_lookup_task_for_rag_pipeline():
    task = build_query_task(
        A2AQueryPayload(
            query_text="Hic almadigim bir dersten tek derse girebilir miyim?",
            context_id="ctx-policy-capability",
            capability_planner={
                "mode": "pilot",
                "apply": True,
                "action": {
                    "capability": "student_affairs.policy_lookup",
                    "intent": "single_exam_eligibility",
                    "params": {
                        "query": "Hic almadigim bir dersten tek derse girebilir miyim?",
                        "topic": "tek ders",
                        "question_type": "eligibility",
                        "must_answer": ["hic alinmamis ders", "devam sarti"],
                    },
                    "answer_contract": {
                        "must_answer": ["hic alinmamis ders", "devam sarti"],
                    },
                    "evidence_contract": {
                        "preferred_sources": ["sik_sorulan_sorular"],
                    },
                    "confidence": 0.9,
                },
            },
        )
    )
    agent = RegistrationAgent(llm_service=AsyncMock())

    prepared = agent._prepare_policy_lookup_task(
        task,
        "Hic almadigim bir dersten tek derse girebilir miyim?",
        task.metadata or {},
    )

    assert prepared.metadata["force_llm_synthesis"] is True
    assert prepared.metadata["policy_lookup"]["topic"] == "tek ders"
    assert "Hic almadigim bir dersten tek derse girebilir miyim?" in prepared.metadata["retrieval_query"]
    assert "tek ders" in prepared.metadata["retrieval_query"]
    assert "devam sarti" in prepared.metadata["retrieval_query"]
    assert "sik_sorulan_sorular" in prepared.metadata["retrieval_query"]
    assert prepared.metadata["conversation_source_refs"] == ["sik_sorulan_sorular"]
    assert prepared.metadata["plan_decision"]["capability"] == "student_affairs.policy_lookup"
    assert prepared.metadata["answer_contract"]["must_answer"] == [
        "hic alinmamis ders",
        "devam sarti",
    ]


def test_international_agent_prepares_policy_lookup_task_for_rag_pipeline():
    task = build_query_task(
        A2AQueryPayload(
            query_text="Uluslararasi ogrenci olarak kayit icin hangi belgeler gerekir?",
            context_id="ctx-international-policy-capability",
            capability_planner={
                "mode": "on",
                "apply": True,
                "action": {
                    "capability": "international.policy_lookup",
                    "intent": "international_registration_documents",
                    "params": {
                        "query": "Uluslararasi ogrenci olarak kayit icin hangi belgeler gerekir?",
                        "topic": "uluslararasi kayit",
                        "question_type": "required_documents",
                        "must_answer": ["gerekli belgeler", "basvuru/kesin kayit ayrimi"],
                        "preferred_sources": ["uluslararasi ogrenci kayit"],
                        "avoid_sources": ["konukevi", "ozel ogrenci"],
                    },
                    "answer_contract": {
                        "must_answer": ["kayit icin gerekli belgeler"],
                    },
                    "evidence_contract": {
                        "preferred_sources": ["uluslararasi ogrenci kayit"],
                        "avoid_sources": ["konukevi", "ozel ogrenci"],
                    },
                    "confidence": 0.9,
                },
            },
        )
    )
    agent = InternationalAgent(llm_service=AsyncMock())

    prepared = agent._prepare_policy_lookup_task(
        task,
        "Uluslararasi ogrenci olarak kayit icin hangi belgeler gerekir?",
        task.metadata or {},
    )

    assert prepared.metadata["force_llm_synthesis"] is True
    assert prepared.metadata["policy_lookup"]["topic"] == "uluslararasi kayit"
    assert (
        prepared.metadata["retrieval_query"]
        == "Uluslararasi ogrenci olarak kayit icin hangi belgeler gerekir?"
    )
    assert prepared.metadata["conversation_source_refs"] == ["uluslararasi ogrenci kayit"]
    assert prepared.metadata["plan_decision"]["capability"] == "international.policy_lookup"
    assert prepared.metadata["evidence_contract"]["avoid_sources"] == [
        "konukevi",
        "ozel ogrenci",
    ]


@pytest.mark.asyncio
async def test_tuition_agent_uses_finance_capability_payload(monkeypatch):
    async def fake_execute(action):
        return ExecutionResult(
            success=True,
            capability=action.capability,
            params=dict(action.params),
            records=[
                {
                    "academic_year": "2025-2026",
                    "student_type": "domestic",
                    "unit_name": "Egitim Fakultesi",
                    "annual_amount": 1759.0,
                    "semester_amount": 879.5,
                    "source_document": "turk_ogrenci_ucretleri.pdf",
                }
            ],
            metadata={
                "student_type": "domestic",
                "unit_name": "egitim fakultesi",
                "source_document": "turk_ogrenci_ucretleri.pdf",
            },
            fallback_allowed=False,
        )

    monkeypatch.setattr(
        "src.agents.finance.tuition_agent.execute_capability_action",
        fake_execute,
    )
    task = build_query_task(
        A2AQueryPayload(
            query_text="Fizik ogretmenligi ucreti ne kadar?",
            context_id="ctx-finance-capability",
            capability_planner={
                "mode": "pilot",
                "apply": True,
                "action": {
                    "capability": "finance.tuition_fee",
                    "params": {
                        "student_type": "domestic",
                        "unit_name": "egitim fakultesi",
                    },
                    "confidence": 0.9,
                },
            },
        )
    )
    agent = TuitionAgent(llm_service=AsyncMock())

    response = await agent.handle_department_task(task)

    assert response.generation_mode == "vt"
    assert response.db_data["capability"] == "finance.tuition_fee"
    assert "1.759,00 TL" in response.answer
    assert "879,50 TL" in response.answer


@pytest.mark.asyncio
async def test_tuition_agent_ignores_finance_capability_for_policy_query(monkeypatch):
    execute_mock = AsyncMock()
    monkeypatch.setattr(
        "src.agents.finance.tuition_agent.execute_capability_action",
        execute_mock,
    )
    agent = TuitionAgent(llm_service=AsyncMock())

    response = await agent._try_handle_capability_plan(
        "Harc borcum olsaydi CAP'a basvurabilir miydim?",
        {
            "capability_planner": {
                "mode": "pilot",
                "apply": True,
                "action": {
                    "capability": "finance.tuition_fee",
                    "params": {
                        "student_type": "domestic",
                        "unit_name": "egitim fakultesi",
                    },
                    "confidence": 0.9,
                },
            }
        },
        student_type="domestic",
        requested_unit="egitim fakultesi",
    )

    assert response is None
    execute_mock.assert_not_called()


@pytest.mark.asyncio
async def test_curriculum_agent_ignores_low_confidence_capability_plan(monkeypatch):
    execute_mock = AsyncMock()
    monkeypatch.setattr(
        "src.agents.academic.curriculum_agent.execute_capability_action",
        execute_mock,
    )
    monkeypatch.setattr(settings.capability_planner, "confidence_threshold", 0.8)
    agent = CurriculumAgent(llm_service=AsyncMock())

    response = await agent._try_handle_capability_plan(
        "BIL203 kac AKTS?",
        {
            "capability_planner": {
                "mode": "pilot",
                "apply": True,
                "action": {
                    "capability": "course.detail",
                    "params": {"course_code": "BIL203"},
                    "confidence": 0.4,
                },
            }
        },
    )

    assert response is None
    execute_mock.assert_not_called()


@pytest.mark.asyncio
async def test_curriculum_agent_falls_back_when_capability_execution_fails(monkeypatch):
    async def fake_execute(action):
        return ExecutionResult(
            success=False,
            capability=action.capability,
            params=dict(action.params),
            error="executor_error",
            fallback_allowed=True,
        )

    monkeypatch.setattr(
        "src.agents.academic.curriculum_agent.execute_capability_action",
        fake_execute,
    )
    agent = CurriculumAgent(llm_service=AsyncMock())

    response = await agent._try_handle_capability_plan(
        "BIL203 kac AKTS?",
        {
            "capability_planner": {
                "mode": "pilot",
                "apply": True,
                "action": {
                    "capability": "course.detail",
                    "params": {"course_code": "BIL203"},
                    "confidence": 0.9,
                },
            }
        },
    )

    assert response is None


def _routing_result(departments: list[Department]) -> RoutingResult:
    return RoutingResult(
        departments=departments,
        confidence=0.9,
        confidence_level=ConfidenceLevel.HIGH,
        strategy=RoutingStrategy.DIRECT,
        reasoning="test",
    )


def _conversation_resolution(query: str) -> ConversationResolution:
    return ConversationResolution(
        original_query=query,
        effective_query=query,
        is_follow_up=False,
        used_context=False,
        active_topic=None,
        department_hints=[],
        source_hints=[],
        standalone_query=query,
    )
