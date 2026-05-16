import json
from pathlib import Path

from src.core.constants import ConfidenceLevel, Department, RoutingStrategy, TaskType
from src.core.source_ownership import resolve_source_ownership, resolve_source_owner_routing_policy
from src.db.conversation_context import ConversationResolution
from src.db.schemas import DepartmentResponse, IntentAnalysis, RAGSource, RoutingResult, UserQueryResponse
from src.diagnostics.decision_contract import (
    DECISION_CONTRACT_METADATA_SCHEMA,
    build_decision_trace_record,
    build_shadow_decision_contract,
    decision_contract_to_metadata,
    write_decision_trace_record,
)


def _conversation() -> ConversationResolution:
    return ConversationResolution(
        original_query="Harc ucreti ne kadar?",
        effective_query="Harc ucreti ne kadar?",
        is_follow_up=False,
        used_context=False,
        active_topic=None,
        department_hints=[],
        source_hints=["tuition_catalog"],
    )


def test_build_decision_trace_record_maps_capability_source_owner():
    routing = RoutingResult(
        departments=[Department.FINANCE],
        confidence=0.91,
        confidence_level=ConfidenceLevel.HIGH,
        strategy=RoutingStrategy.DIRECT,
        reasoning="Finance question",
        task_type=TaskType.TUITION_QUERY,
        intent=IntentAnalysis(primary_intent="tuition_fee"),
    )
    final_response = UserQueryResponse(
        answer="Structured answer",
        departments_involved=["finance"],
        generation_modes=["vt"],
        sources=[
            RAGSource(
                content="Fee row",
                score=1.0,
                metadata={"source": "tuition_catalog_2026"},
            )
        ],
        response_time_ms=123.4,
        query_id="ctx-1",
        routing_strategy="direct",
    )
    planner_payload = {
        "apply": True,
        "available_capabilities": ["finance.tuition_fee"],
        "action": {
            "capability": "finance.tuition_fee",
            "confidence": 0.88,
            "params": {"program": "Computer Engineering"},
        },
    }

    record = build_decision_trace_record(
        original_query="Harc ucreti ne kadar?",
        effective_query="Harc ucreti ne kadar?",
        trace_metadata={"trace_id": "trace-1", "span_id": "span-1"},
        runtime_mode="http",
        channel="api_or_a2a",
        context_id="ctx-1",
        routing=routing,
        conversation_resolution=_conversation(),
        capability_planner_payload=planner_payload,
        final_response=final_response,
        final_answer_owner="main_orchestrator",
        cache_lookup_policy="capability_planner_enabled",
        cache_store_policy="global_synthesis",
    )

    contract = record.shadow_decision_contract
    assert contract.source_owner.primary == "tuition_fee_catalog"
    assert contract.capabilities.selected == "finance.tuition_fee"
    assert contract.departments.primary == "finance"
    assert contract.evidence.top_sources == ["tuition_catalog_2026"]
    assert record.trace_id == "trace-1"
    assert record.runtime["response_time_ms"] == 123.4
    path = record.runtime["decision_path"]
    assert path["router"]["primary_department"] == "finance"
    assert path["capability"]["selected"] == "finance.tuition_fee"
    assert path["source_owner"]["primary"] == "tuition_fee_catalog"
    assert path["answer"]["final_owner"] == "main_orchestrator"


def test_special_fee_scope_overrides_regular_tuition_capability_owner():
    owner = resolve_source_ownership(
        original_query="Yaz okulu ucreti Turk ogrenci icin ne kadar?",
        effective_query="Yaz okulu ucreti Turk ogrenci icin ne kadar?",
        capability="finance.tuition_fee",
        task_type=TaskType.TUITION_QUERY,
    )

    assert owner.primary == "student_affairs_policy"
    assert owner.fallbacks == ["tuition_fee_catalog"]
    assert owner.reasoning == "source_registry:special_fee_policy_scope"


def test_decision_trace_runtime_carries_specialist_selection_diagnostics():
    final_response = UserQueryResponse(
        answer="Kayit cevabi",
        departments_involved=["student_affairs"],
        generation_modes=["llm"],
        response_time_ms=111.0,
        query_id="ctx-selector",
    )
    specialist_selection = {
        "schema": "omu.specialist_selection.v1",
        "mode": "contract_first_keyword_fallback",
        "department": "student_affairs",
        "selected_agent_id": "registration_agent",
        "selected_by": "contract",
        "legacy_keyword": {
            "agent_id": "internship_agent",
            "matches_selected": False,
            "used_as_fallback": False,
        },
    }
    response = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Kayit cevabi",
        sources=[],
        metadata={
            "selected_agent_id": "registration_agent",
            "specialist_selection": specialist_selection,
        },
    )

    record = build_decision_trace_record(
        original_query="Staj basvurusu yerine kayit dondurma sureci nedir?",
        effective_query="Staj basvurusu yerine kayit dondurma sureci nedir?",
        context_id="ctx-selector",
        responses=[response],
        final_response=final_response,
    )

    assert record.runtime["selected_specialists"] == ["registration_agent"]
    assert record.runtime["specialist_selections"] == [specialist_selection]


def test_decision_trace_carries_evidence_answer_validator_result():
    final_response = UserQueryResponse(
        answer="Kaynakta net bilgi yok.",
        departments_involved=["student_affairs"],
        generation_modes=["llm"],
        response_time_ms=111.0,
        query_id="ctx-validator",
    )

    record = build_decision_trace_record(
        original_query="CAP icin not ortalamasi kac olmali?",
        effective_query="CAP icin not ortalamasi kac olmali?",
        context_id="ctx-validator",
        final_response=final_response,
        profiler_snapshot={
            "attributes": {
                "evidence_answer_validator": {
                    "status": "fail",
                    "reason": "answer_denies_available_evidence",
                    "missing_values": ["3,00"],
                }
            }
        },
    )

    assert record.answer_validation_result["status"] == "fail"
    assert record.answer_validation_result["missing_values"] == ["3,00"]
    assert record.runtime["decision_path"]["quality"]["validator_status"] == "fail"


def test_decision_trace_carries_answer_coverage_shadow_result():
    record = build_decision_trace_record(
        original_query="CAP basvurusu nasil yapilir?",
        effective_query="CAP basvurusu nasil yapilir?",
        context_id="ctx-coverage",
        final_response=UserQueryResponse(
            answer="CAP icin GANO en az 3,00 olmalidir.",
            departments_involved=["student_affairs"],
            generation_modes=["llm"],
            response_time_ms=20.0,
            query_id="ctx-coverage",
        ),
        profiler_snapshot={
            "attributes": {
                "answer_coverage_validator": {
                    "mode": "shadow",
                    "status": "check",
                    "expected_facet": "application_process",
                    "reason": "answer_missing_process_markers",
                }
            }
        },
    )

    assert record.answer_coverage_result["status"] == "check"
    assert record.runtime["decision_path"]["quality"]["coverage_status"] == "check"
    assert record.runtime["decision_path"]["quality"]["coverage_facet"] == "application_process"


def test_decision_trace_carries_answer_value_conflict_shadow_result():
    record = build_decision_trace_record(
        original_query="Peki not ortalamasi kac olmali?",
        effective_query="CAP icin not ortalamasi kac olmali?",
        context_id="ctx-value-conflict",
        final_response=UserQueryResponse(
            answer="Not ortalamasi en az 2,00 olmalidir; CAP icin 3,00 olabilir.",
            departments_involved=["student_affairs"],
            generation_modes=["llm"],
            response_time_ms=20.0,
            query_id="ctx-value-conflict",
        ),
        profiler_snapshot={
            "attributes": {
                "answer_value_conflict_validator": {
                    "mode": "shadow",
                    "status": "check",
                    "reason": "multiple_competing_threshold_values",
                    "primary_answer_value": "2,00",
                    "competing_values": ["3,00"],
                }
            }
        },
    )

    assert record.answer_value_conflict_result["status"] == "check"
    assert record.answer_value_conflict_result["primary_answer_value"] == "2,00"
    assert record.runtime["decision_path"]["quality"]["value_conflict_status"] == "check"
    assert record.runtime["decision_path"]["quality"]["primary_answer_value"] == "2,00"


def test_decision_trace_preserves_llm_key_diagnostics():
    record = build_decision_trace_record(
        original_query="CAP basvurusu nasil yapilir?",
        effective_query="CAP basvurusu nasil yapilir?",
        context_id="ctx-key-diagnostics",
        final_response=UserQueryResponse(
            answer="Cevap",
            departments_involved=["student_affairs"],
            generation_modes=["llm"],
            response_time_ms=20.0,
            query_id="ctx-key-diagnostics",
        ),
        profiler_snapshot={
            "attributes": {
                "llm_usage": [
                    {
                        "kind": "generate",
                        "model_role": "routing",
                        "provider": "openai_compatible",
                        "provider_label": "groq",
                        "model": "llama-3.3-70b-versatile",
                        "path": "primary",
                        "status": "success",
                        "api_key_fingerprint": "abc123",
                        "api_key_index": 7,
                        "api_key_count": 53,
                        "provider_org_fingerprint": "orgfp",
                    }
                ]
            }
        },
    )

    assert record.llm_usage[0]["api_key_fingerprint"] == "abc123"
    assert record.llm_usage[0]["api_key_index"] == 7
    assert record.llm_usage[0]["api_key_count"] == 53
    assert record.llm_usage[0]["provider_org_fingerprint"] == "orgfp"


def test_runtime_decision_contract_metadata_is_read_only_and_uses_source_owner_payload():
    routing = RoutingResult(
        departments=[Department.STUDENT_AFFAIRS],
        confidence=0.82,
        confidence_level=ConfidenceLevel.HIGH,
        strategy=RoutingStrategy.DIRECT,
        reasoning="Student affairs policy",
        task_type=TaskType.PROCEDURE_QUERY,
        intent=IntentAnalysis(primary_intent="registration_policy"),
    )
    source_owner_payload = {
        "schema": "omu.source_owner.v1",
        "primary": "student_affairs_policy",
        "fallbacks": [],
        "confidence": 0.82,
        "reasoning": "task_type",
    }

    contract = build_shadow_decision_contract(
        original_query="Kayit dondurma nasil yapilir?",
        effective_query="Kayit dondurma nasil yapilir?",
        routing=routing,
        conversation_resolution=_conversation(),
        cache_lookup_policy="capability_planner_enabled",
        source_owner_payload=source_owner_payload,
        final_answer_owner="main_orchestrator",
    )
    metadata = decision_contract_to_metadata(
        contract,
        producer="main_orchestrator",
        stage="department_dispatch",
    )

    assert metadata["schema"] == DECISION_CONTRACT_METADATA_SCHEMA
    assert metadata["mode"] == "read_only"
    assert metadata["stage"] == "department_dispatch"
    assert metadata["contract"]["source_owner"]["primary"] == "student_affairs_policy"
    assert metadata["contract"]["producer_trace"]["source_owner"]["reasoning"] == "task_type"
    assert metadata["contract"]["producer_trace"]["cache"]["lookup_policy"] == "capability_planner_enabled"


def test_source_owner_registry_prefers_calendar_owner_over_student_affairs_task_type():
    routing = RoutingResult(
        departments=[Department.STUDENT_AFFAIRS],
        confidence=0.88,
        confidence_level=ConfidenceLevel.HIGH,
        strategy=RoutingStrategy.DIRECT,
        reasoning="Calendar date handled by student affairs pipeline",
        task_type=TaskType.REGISTRATION_QUERY,
        intent=IntentAnalysis(primary_intent="academic_calendar"),
    )
    final_response = UserQueryResponse(
        answer="Final sinavlari 3 Ocak'ta baslar.",
        departments_involved=["student_affairs"],
        generation_modes=["vt"],
        response_time_ms=100.0,
        query_id="ctx-calendar",
    )

    record = build_decision_trace_record(
        original_query="Final sinavlari ne zaman basliyor?",
        effective_query="Final sinavlari ne zaman basliyor?",
        context_id="ctx-calendar",
        routing=routing,
        conversation_resolution=_conversation(),
        final_response=final_response,
        final_answer_owner="main_orchestrator",
    )

    owner = record.shadow_decision_contract.source_owner
    assert owner.primary == "academic_calendar"
    assert owner.fallbacks == ["student_affairs_policy"]
    assert owner.reasoning == "source_registry:academic_calendar"


def test_source_owner_registry_prefers_international_policy_for_foreign_student_domain():
    routing = RoutingResult(
        departments=[Department.ACADEMIC_PROGRAMS, Department.STUDENT_AFFAIRS],
        confidence=0.87,
        confidence_level=ConfidenceLevel.HIGH,
        strategy=RoutingStrategy.PARALLEL,
        reasoning="International registration and residence process",
        task_type=TaskType.REGISTRATION_QUERY,
        intent=IntentAnalysis(primary_intent="kayit"),
    )
    final_response = UserQueryResponse(
        answer="Kayit ve ikamet belgeleri listelenir.",
        departments_involved=["academic_programs", "student_affairs"],
        generation_modes=["llm"],
        response_time_ms=100.0,
        query_id="ctx-international",
    )

    record = build_decision_trace_record(
        original_query="Yabanci ogrenci kayit belgeleri ve ikamet izni icin neler gerekir?",
        effective_query="Yabanci ogrenci kayit belgeleri ve ikamet izni icin neler gerekir?",
        context_id="ctx-international",
        routing=routing,
        conversation_resolution=_conversation(),
        final_response=final_response,
        final_answer_owner="main_orchestrator",
    )

    owner = record.shadow_decision_contract.source_owner
    assert owner.primary == "international_policy"
    assert owner.fallbacks == ["student_affairs_policy"]
    assert owner.reasoning == "source_registry:international_policy"


def test_source_owner_routing_policy_names_owner_primary_branch():
    policy = resolve_source_owner_routing_policy(
        source_owner="student_affairs_policy",
        capability="student_affairs.policy_lookup",
    )

    assert policy is not None
    assert policy.primary_department is Department.STUDENT_AFFAIRS
    assert list(policy.support_departments) == [
        Department.ACADEMIC_PROGRAMS,
        Department.FINANCE,
    ]


def test_source_owner_routing_policy_falls_back_to_owner_when_capability_missing():
    policy = resolve_source_owner_routing_policy(
        source_owner="curriculum_catalog",
        capability=None,
    )

    assert policy is not None
    assert policy.primary_department is Department.ACADEMIC_PROGRAMS


def test_write_decision_trace_record_appends_jsonl():
    final_response = UserQueryResponse(
        answer="Answer",
        departments_involved=["event"],
        generation_modes=["vt"],
        response_time_ms=42.0,
        query_id="ctx-event",
    )
    record = build_decision_trace_record(
        original_query="Bugun etkinlik var mi?",
        effective_query="Bugun etkinlik var mi?",
        trace_metadata={"trace_id": "trace-event"},
        context_id="ctx-event",
        final_response=final_response,
        source_owner_override="event_search",
        deterministic_rules=["event_short_circuit"],
    )

    output_path = Path("tmp/test_decision_trace.jsonl")
    output_path.unlink(missing_ok=True)
    output_path = write_decision_trace_record(record, output_path=output_path)

    lines = output_path.read_text(encoding="utf-8").splitlines()
    output_path.unlink(missing_ok=True)
    assert len(lines) == 1
    payload = json.loads(lines[0])
    contract = payload["shadow_decision_contract"]
    assert contract["source_owner"]["primary"] == "event_search"
    assert contract["producer_trace"]["deterministic_rules"] == ["event_short_circuit"]
