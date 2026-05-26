"""Shadow decision contract and JSONL trace helpers.

The models in this module are diagnostic-only. They describe the decision the
current runtime appears to be making, but they do not drive routing, retrieval,
or synthesis behavior.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from src.core.config import settings
from src.core.constants import Department, TaskType
from src.core.source_ownership import (
    resolve_source_ownership,
    source_owner_from_capability,
)
from src.db.conversation_context import ConversationResolution
from src.db.schemas import DepartmentResponse, RoutingResult, UserQueryResponse

logger = logging.getLogger(__name__)

DECISION_CONTRACT_METADATA_SCHEMA = "omu.decision_contract.v1"


class QueryDecision(BaseModel):
    original: str
    effective: str
    normalized: str | None = None


class ConversationDecision(BaseModel):
    is_follow_up: bool = False
    used_context: bool = False
    active_topic: str | None = None
    frame: dict[str, Any] = Field(default_factory=dict)


class IntentDecision(BaseModel):
    primary: str | None = None
    secondary: list[str] = Field(default_factory=list)
    confidence: float | None = None
    complexity: str | None = None
    is_personal: bool = False
    requires_auth: bool = False
    task_type: str | None = None


class DepartmentsDecision(BaseModel):
    primary: str | None = None
    secondary: list[str] = Field(default_factory=list)
    strategy: str | None = None


class SourceOwnerDecision(BaseModel):
    primary: str | None = None
    fallbacks: list[str] = Field(default_factory=list)
    confidence: float | None = None
    reasoning: str | None = None


class CapabilityDecision(BaseModel):
    allowed: list[str] = Field(default_factory=list)
    selected: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)
    missing_params: list[str] = Field(default_factory=list)
    confidence: float | None = None
    apply: bool | None = None
    fallback: str | None = None


class SlotsDecision(BaseModel):
    required: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    clarification_policy: str | None = None


class RetrievalDecision(BaseModel):
    collections_primary: list[str] = Field(default_factory=list)
    collections_fallback: list[str] = Field(default_factory=list)
    source_hints: list[str] = Field(default_factory=list)
    must_answer: list[str] = Field(default_factory=list)


class EvidenceDecision(BaseModel):
    preferred_sources: list[str] = Field(default_factory=list)
    avoid_sources: list[str] = Field(default_factory=list)
    top_sources: list[str] = Field(default_factory=list)


class AnswerDecision(BaseModel):
    final_owner: str | None = None
    synthesis_policy: str | None = None
    judge_policy: str | None = None
    used_global_synthesis: bool = False


class CacheDecision(BaseModel):
    lookup_policy: str | None = None
    store_policy: str | None = None


class LatencyBudgetDecision(BaseModel):
    query_class: str | None = None
    max_expected_seconds: float | None = None


class ValidatorDecision(BaseModel):
    applied: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ProducerTraceDecision(BaseModel):
    router: dict[str, Any] = Field(default_factory=dict)
    capability_planner: dict[str, Any] = Field(default_factory=dict)
    source_owner: dict[str, Any] = Field(default_factory=dict)
    cache: dict[str, Any] = Field(default_factory=dict)
    deterministic_rules: list[str] = Field(default_factory=list)


class DecisionContract(BaseModel):
    contract_version: str = "0.1"
    query: QueryDecision
    conversation: ConversationDecision = Field(default_factory=ConversationDecision)
    intent: IntentDecision = Field(default_factory=IntentDecision)
    departments: DepartmentsDecision = Field(default_factory=DepartmentsDecision)
    source_owner: SourceOwnerDecision = Field(default_factory=SourceOwnerDecision)
    capabilities: CapabilityDecision = Field(default_factory=CapabilityDecision)
    slots: SlotsDecision = Field(default_factory=SlotsDecision)
    retrieval: RetrievalDecision = Field(default_factory=RetrievalDecision)
    evidence: EvidenceDecision = Field(default_factory=EvidenceDecision)
    answer: AnswerDecision = Field(default_factory=AnswerDecision)
    cache: CacheDecision = Field(default_factory=CacheDecision)
    latency_budget: LatencyBudgetDecision = Field(default_factory=LatencyBudgetDecision)
    validators: ValidatorDecision = Field(default_factory=ValidatorDecision)
    producer_trace: ProducerTraceDecision = Field(default_factory=ProducerTraceDecision)


class DecisionTraceRecord(BaseModel):
    trace_id: str | None = None
    span_id: str | None = None
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    runtime_mode: str | None = None
    channel: str | None = None
    context_id: str | None = None
    query_log_id: int | None = None
    is_authenticated: bool = False
    shadow_decision_contract: DecisionContract
    contract_vs_runtime_diff: list[str] = Field(default_factory=list)
    runtime: dict[str, Any] = Field(default_factory=dict)
    latency_breakdown: dict[str, float] = Field(default_factory=dict)
    llm_call_count: int = 0
    llm_roles_used: list[str] = Field(default_factory=list)
    llm_usage: list[dict[str, Any]] = Field(default_factory=list)
    judge_result: dict[str, Any] = Field(default_factory=dict)
    answer_validation_result: dict[str, Any] = Field(default_factory=dict)
    answer_coverage_result: dict[str, Any] = Field(default_factory=dict)
    answer_value_conflict_result: dict[str, Any] = Field(default_factory=dict)
    final_answer_preview: str | None = None
    warnings: list[str] = Field(default_factory=list)


def _enum_value(value: Any) -> str | None:
    if value is None:
        return None
    enum_value = getattr(value, "value", None)
    return str(enum_value if enum_value is not None else value)


def _list_enum_values(values: Any) -> list[str]:
    if not values:
        return []
    return [value for value in (_enum_value(item) for item in values) if value]


def _compact_strings(values: Any) -> list[str]:
    if not values:
        return []
    result: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in result:
            result.append(text)
    return result


def _planner_action(planner_payload: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(planner_payload, dict):
        return {}
    action = planner_payload.get("action")
    return dict(action) if isinstance(action, dict) else {}


def _planner_scope(planner_payload: dict[str, Any] | None) -> list[str]:
    if not isinstance(planner_payload, dict):
        return []
    capabilities = planner_payload.get("available_capabilities")
    if isinstance(capabilities, list):
        return _compact_strings(capabilities)
    scope = planner_payload.get("scope")
    if isinstance(scope, list):
        return _compact_strings(scope)
    if isinstance(scope, str):
        return _compact_strings(scope.split(","))
    return []


def _source_owner_from_capability(capability: str | None) -> str | None:
    return source_owner_from_capability(capability)


def _source_owner_from_task_type(task_type: TaskType | str | None) -> str | None:
    value = _enum_value(task_type)
    if value in {TaskType.TUITION_QUERY.value, TaskType.PAYMENT_QUERY.value}:
        return "tuition_fee_catalog"
    if value == TaskType.COURSE_QUERY.value:
        return "curriculum_catalog"
    if value in {TaskType.REGISTRATION_QUERY.value, TaskType.PROCEDURE_QUERY.value}:
        return "student_affairs_policy"
    if value == TaskType.SCHOLARSHIP_QUERY.value:
        return "student_affairs_policy"
    if value == TaskType.DATA_QUERY.value:
        return "personal_student_data"
    return None


def _infer_source_owner(
    *,
    original_query: str,
    effective_query: str,
    routing: RoutingResult | None,
    planner_payload: dict[str, Any] | None,
    final_response: UserQueryResponse | None,
    source_owner_override: str | None,
    source_owner_payload: dict[str, Any] | None = None,
) -> SourceOwnerDecision:
    payload_decision = _source_owner_decision_from_payload(source_owner_payload)
    if payload_decision is not None:
        return payload_decision

    action = _planner_action(planner_payload)
    intent = routing.intent if routing else None
    resolution = resolve_source_ownership(
        original_query=original_query,
        effective_query=effective_query,
        capability=action.get("capability"),
        primary_intent=intent.primary_intent if intent else None,
        target_capability=intent.target_capability if intent else None,
        task_type=routing.task_type if routing else None,
        is_personal=bool(intent and intent.is_personal),
        confidence=(
            _safe_float(action.get("confidence"))
            if action.get("capability")
            else (routing.confidence if routing else None)
        ),
        final_departments=list(final_response.departments_involved or []) if final_response else [],
        override=source_owner_override,
    )
    return SourceOwnerDecision(
        primary=resolution.primary,
        fallbacks=resolution.fallbacks,
        confidence=resolution.confidence,
        reasoning=resolution.reasoning,
    )


def _source_owner_decision_from_payload(
    payload: dict[str, Any] | None,
) -> SourceOwnerDecision | None:
    if not isinstance(payload, dict):
        return None
    primary = str(payload.get("primary") or "").strip() or None
    fallbacks = _compact_strings(payload.get("fallbacks") or [])
    reasoning = str(payload.get("reasoning") or "").strip() or None
    if primary is None and not fallbacks and reasoning is None:
        return None
    return SourceOwnerDecision(
        primary=primary,
        fallbacks=fallbacks,
        confidence=_safe_float(payload.get("confidence")),
        reasoning=reasoning,
    )


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _conversation_frame(conversation: ConversationResolution | None) -> dict[str, Any]:
    if conversation is None:
        return {}
    frame = {
        "department_hints": _list_enum_values(conversation.department_hints),
        "source_hints": _compact_strings(conversation.source_hints),
        "rewrite_method": conversation.rewrite_method,
        "standalone_query": conversation.standalone_query,
        "announcement_context": bool(conversation.announcement_context),
    }
    task_type_hint = getattr(conversation, "task_type_hint", None)
    student_type_hint = getattr(conversation, "student_type_hint", None)
    if task_type_hint is not None:
        frame["task_type_hint"] = _enum_value(task_type_hint)
    if student_type_hint:
        frame["student_type_hint"] = student_type_hint
    return {key: value for key, value in frame.items() if value not in (None, [], {})}


def _top_evidence_sources(
    responses: list[DepartmentResponse],
    final_response: UserQueryResponse | None,
) -> list[str]:
    sources: list[str] = []
    for response in responses:
        for source in response.sources[:3]:
            metadata = source.metadata or {}
            source_name = str(metadata.get("source") or metadata.get("title") or "").strip()
            if source_name and source_name not in sources:
                sources.append(source_name)
    if final_response is not None:
        for source in final_response.sources[:5]:
            metadata = source.metadata or {}
            source_name = str(metadata.get("source") or metadata.get("title") or "").strip()
            if source_name and source_name not in sources:
                sources.append(source_name)
    return sources[:8]


def _runtime_payload(
    *,
    responses: list[DepartmentResponse],
    final_response: UserQueryResponse | None,
    selected_specialists: list[str],
) -> dict[str, Any]:
    specialist_selections = _specialist_selections_from_responses(responses)
    retrieval_execution = _retrieval_execution_from_responses(responses)
    if final_response is None:
        return {
            "selected_specialists": selected_specialists,
            "specialist_selections": specialist_selections,
            "retrieval_execution": retrieval_execution,
            "department_response_count": len(responses),
        }
    return {
        "selected_departments": list(final_response.departments_involved or []),
        "selected_specialists": selected_specialists,
        "specialist_selections": specialist_selections,
        "retrieval_execution": retrieval_execution,
        "generation_modes": list(final_response.generation_modes or []),
        "routing_strategy": final_response.routing_strategy,
        "response_time_ms": final_response.response_time_ms,
        "source_count": len(final_response.sources or []),
        "department_response_count": len(responses),
    }


def _retrieval_execution_from_responses(responses: list[DepartmentResponse]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for response in responses:
        metadata = dict(response.metadata or {})
        stats = metadata.get("retrieval_execution_stats")
        if not isinstance(stats, dict):
            packet = metadata.get("evidence_packet")
            stats = packet.get("retrieval_execution_stats") if isinstance(packet, dict) else None
        if not isinstance(stats, dict):
            continue
        item = dict(stats)
        item.setdefault("department", response.department.value)
        selection = metadata.get("specialist_selection")
        if isinstance(selection, dict):
            item.setdefault("specialist", selection.get("selected_agent_id"))
        items.append(item)
    return items


def _specialist_selections_from_responses(responses: list[DepartmentResponse]) -> list[dict[str, Any]]:
    selections: list[dict[str, Any]] = []
    for response in responses:
        metadata = dict(response.metadata or {})
        selection = metadata.get("specialist_selection")
        if isinstance(selection, dict):
            selections.append(dict(selection))
            continue
        selected_agent_id = metadata.get("selected_agent_id") or metadata.get("agent_id")
        if selected_agent_id:
            selections.append(
                {
                    "schema": "omu.specialist_selection.legacy",
                    "mode": "legacy_response_metadata",
                    "department": response.department.value,
                    "selected_agent_id": str(selected_agent_id),
                    "selected_by": "unknown",
                    "reason": "response_metadata_without_selector_diagnostics",
                }
            )
    return selections


def _selected_specialists_from_responses(responses: list[DepartmentResponse]) -> list[str]:
    specialists: list[str] = []
    for response in responses:
        metadata = dict(response.metadata or {})
        selection = metadata.get("specialist_selection")
        selection_agent_id = (
            selection.get("selected_agent_id")
            if isinstance(selection, dict)
            else None
        )
        agent_id = str(
            selection_agent_id
            or metadata.get("selected_agent_id")
            or metadata.get("agent_id")
            or ""
        ).strip()
        if agent_id and agent_id not in specialists:
            specialists.append(agent_id)
    return specialists


def _latency_breakdown(profiler_snapshot: dict[str, Any] | None) -> dict[str, float]:
    if not profiler_snapshot:
        return {}
    totals: dict[str, float] = {}
    for event in profiler_snapshot.get("events") or []:
        if not isinstance(event, dict):
            continue
        name = str(event.get("name") or "").strip()
        duration = _safe_float(event.get("duration_ms"))
        if not name or duration is None:
            continue
        totals[name] = round(totals.get(name, 0.0) + duration, 3)
    return totals


def _llm_usage(profiler_snapshot: dict[str, Any] | None) -> tuple[int, list[str], list[dict[str, Any]]]:
    attributes = (profiler_snapshot or {}).get("attributes") or {}
    usage = attributes.get("llm_usage") or []
    if not isinstance(usage, list):
        return 0, [], []
    roles: list[str] = []
    compact_usage: list[dict[str, Any]] = []
    for item in usage:
        if not isinstance(item, dict):
            continue
        role = str(item.get("model_role") or item.get("role") or "").strip()
        if role and role not in roles:
            roles.append(role)
        compact_usage.append(
            {
                key: item.get(key)
                for key in (
                    "kind",
                    "model_role",
                    "provider",
                    "provider_label",
                    "display_name",
                    "model",
                    "path",
                    "status",
                    "json_mode",
                    "llm_profile",
                    "llm_operating_profile",
                    "fallback_from",
                    "fallback_from_label",
                    "fallback_from_model",
                    "prompt_chars",
                    "system_chars",
                    "estimated_input_tokens",
                    "api_key_fingerprint",
                    "api_key_index",
                    "api_key_count",
                    "provider_org_fingerprint",
                    "error_type",
                    "error_message",
                )
                if item.get(key) is not None
            }
        )
    return len(compact_usage), roles, compact_usage


def _judge_result(profiler_snapshot: dict[str, Any] | None) -> dict[str, Any]:
    attributes = (profiler_snapshot or {}).get("attributes") or {}
    value = attributes.get("main_judge") or attributes.get("answer_judge")
    return dict(value) if isinstance(value, dict) else {}


def _answer_validation_result(profiler_snapshot: dict[str, Any] | None) -> dict[str, Any]:
    attributes = (profiler_snapshot or {}).get("attributes") or {}
    value = attributes.get("evidence_answer_validator")
    return dict(value) if isinstance(value, dict) else {}


def _answer_coverage_result(profiler_snapshot: dict[str, Any] | None) -> dict[str, Any]:
    attributes = (profiler_snapshot or {}).get("attributes") or {}
    value = attributes.get("answer_coverage_validator")
    return dict(value) if isinstance(value, dict) else {}


def _answer_value_conflict_result(profiler_snapshot: dict[str, Any] | None) -> dict[str, Any]:
    attributes = (profiler_snapshot or {}).get("attributes") or {}
    value = attributes.get("answer_value_conflict_validator")
    return dict(value) if isinstance(value, dict) else {}


def _answer_length_result(profiler_snapshot: dict[str, Any] | None) -> dict[str, Any]:
    attributes = (profiler_snapshot or {}).get("attributes") or {}
    value = attributes.get("answer_length")
    return dict(value) if isinstance(value, dict) else {}


def build_shadow_decision_contract(
    *,
    original_query: str,
    effective_query: str,
    routing: RoutingResult | None = None,
    conversation_resolution: ConversationResolution | None = None,
    capability_planner_payload: dict[str, Any] | None = None,
    responses: list[DepartmentResponse] | None = None,
    final_response: UserQueryResponse | None = None,
    final_answer_owner: str | None = None,
    used_global_synthesis: bool = False,
    cache_lookup_policy: str | None = None,
    cache_store_policy: str | None = None,
    source_owner_override: str | None = None,
    source_owner_payload: dict[str, Any] | None = None,
    deterministic_rules: list[str] | None = None,
) -> DecisionContract:
    responses = list(responses or [])
    action = _planner_action(capability_planner_payload)
    intent = routing.intent if routing is not None else None
    departments = _list_enum_values(routing.departments if routing else [])
    primary_department = departments[0] if departments else None

    required_slots = list(intent.required_slots if intent else [])
    missing_slots = list(intent.missing_slots if intent else [])
    missing_params = _compact_strings(action.get("missing_params") or [])
    answer_contract = action.get("answer_contract") if isinstance(action.get("answer_contract"), dict) else {}
    evidence_contract = action.get("evidence_contract") if isinstance(action.get("evidence_contract"), dict) else {}

    validators: list[str] = []
    if intent and intent.is_personal:
        validators.append("auth_required")
    if required_slots or missing_slots or missing_params:
        validators.append("slot_check")
    if action.get("capability"):
        validators.append("capability_validation")
    source_owner_decision = _infer_source_owner(
        original_query=original_query,
        effective_query=effective_query,
        routing=routing,
        planner_payload=capability_planner_payload,
        final_response=final_response,
        source_owner_override=source_owner_override,
        source_owner_payload=source_owner_payload,
    )
    warnings: list[str] = []
    if source_owner_decision.primary is None:
        warnings.append("source_owner_unresolved")
    cache_trace = {
        key: value
        for key, value in {
            "lookup_policy": cache_lookup_policy,
            "store_policy": cache_store_policy,
        }.items()
        if value is not None
    }
    source_owner_trace = dict(source_owner_payload or {})
    if source_owner_override and not source_owner_trace:
        source_owner_trace = {"override": source_owner_override}

    return DecisionContract(
        query=QueryDecision(original=original_query, effective=effective_query, normalized=effective_query),
        conversation=ConversationDecision(
            is_follow_up=bool(conversation_resolution and conversation_resolution.is_follow_up),
            used_context=bool(conversation_resolution and conversation_resolution.used_context),
            active_topic=conversation_resolution.active_topic if conversation_resolution else None,
            frame=_conversation_frame(conversation_resolution),
        ),
        intent=IntentDecision(
            primary=(intent.primary_intent if intent else None) or action.get("intent"),
            confidence=routing.confidence if routing is not None else _safe_float(action.get("confidence")),
            complexity=intent.complexity if intent else None,
            is_personal=bool(intent and intent.is_personal),
            requires_auth=bool(intent and intent.is_personal),
            task_type=_enum_value(routing.task_type if routing else None),
        ),
        departments=DepartmentsDecision(
            primary=primary_department,
            secondary=departments[1:],
            strategy=_enum_value(routing.strategy if routing else None),
        ),
        source_owner=source_owner_decision,
        capabilities=CapabilityDecision(
            allowed=_planner_scope(capability_planner_payload),
            selected=str(action.get("capability") or "") or None,
            params=dict(action.get("params") or {}),
            missing_params=missing_params,
            confidence=_safe_float(action.get("confidence")),
            apply=capability_planner_payload.get("apply") if isinstance(capability_planner_payload, dict) else None,
            fallback=action.get("fallback") or action.get("fallback_route"),
        ),
        slots=SlotsDecision(
            required=_compact_strings(required_slots),
            missing=_compact_strings([*missing_slots, *missing_params]),
            clarification_policy="required" if missing_slots or missing_params else None,
        ),
        retrieval=RetrievalDecision(
            source_hints=_compact_strings(conversation_resolution.source_hints if conversation_resolution else []),
            must_answer=_compact_strings(answer_contract.get("must_answer") or []),
        ),
        evidence=EvidenceDecision(
            preferred_sources=_compact_strings(evidence_contract.get("preferred_sources") or []),
            avoid_sources=_compact_strings(evidence_contract.get("avoid_sources") or []),
            top_sources=_top_evidence_sources(responses, final_response),
        ),
        answer=AnswerDecision(
            final_owner=final_answer_owner,
            synthesis_policy="global_synthesis" if used_global_synthesis else "runtime_default",
            judge_policy="main_judge_if_enabled",
            used_global_synthesis=used_global_synthesis,
        ),
        cache=CacheDecision(lookup_policy=cache_lookup_policy, store_policy=cache_store_policy),
        validators=ValidatorDecision(applied=validators, warnings=warnings),
        producer_trace=ProducerTraceDecision(
            router=routing.model_dump(mode="json") if routing else {},
            capability_planner=capability_planner_payload or {},
            source_owner=source_owner_trace,
            cache=cache_trace,
            deterministic_rules=list(deterministic_rules or []),
        ),
    )


def decision_contract_to_metadata(
    contract: DecisionContract,
    *,
    producer: str = "main_orchestrator",
    stage: str = "runtime",
) -> dict[str, Any]:
    """Serialize a read-only runtime decision contract for A2A metadata."""
    return {
        "schema": DECISION_CONTRACT_METADATA_SCHEMA,
        "producer": producer,
        "mode": "read_only",
        "stage": stage,
        "contract_version": contract.contract_version,
        "contract": contract.model_dump(mode="json", exclude_none=True),
    }


def build_decision_trace_record(
    *,
    original_query: str,
    effective_query: str,
    trace_metadata: dict[str, Any] | None = None,
    runtime_mode: str | None = None,
    channel: str | None = None,
    context_id: str | None = None,
    query_log_id: int | None = None,
    is_authenticated: bool = False,
    routing: RoutingResult | None = None,
    conversation_resolution: ConversationResolution | None = None,
    capability_planner_payload: dict[str, Any] | None = None,
    responses: list[DepartmentResponse] | None = None,
    final_response: UserQueryResponse | None = None,
    final_answer_owner: str | None = None,
    used_global_synthesis: bool = False,
    cache_lookup_policy: str | None = None,
    cache_store_policy: str | None = None,
    selected_specialists: list[str] | None = None,
    profiler_snapshot: dict[str, Any] | None = None,
    include_answer_preview: bool = False,
    source_owner_override: str | None = None,
    source_owner_payload: dict[str, Any] | None = None,
    deterministic_rules: list[str] | None = None,
) -> DecisionTraceRecord:
    responses = list(responses or [])
    trace_metadata = dict(trace_metadata or {})
    runtime_selected_specialists = list(
        selected_specialists or _selected_specialists_from_responses(responses)
    )
    contract = build_shadow_decision_contract(
        original_query=original_query,
        effective_query=effective_query,
        routing=routing,
        conversation_resolution=conversation_resolution,
        capability_planner_payload=capability_planner_payload,
        responses=responses,
        final_response=final_response,
        final_answer_owner=final_answer_owner,
        used_global_synthesis=used_global_synthesis,
        cache_lookup_policy=cache_lookup_policy,
        cache_store_policy=cache_store_policy,
        source_owner_override=source_owner_override,
        source_owner_payload=source_owner_payload,
        deterministic_rules=deterministic_rules,
    )
    llm_count, llm_roles, llm_usage = _llm_usage(profiler_snapshot)
    answer_preview = None
    if include_answer_preview and final_response is not None:
        answer_preview = final_response.answer[: settings.decision_trace.max_answer_preview_chars]
    runtime_payload = _runtime_payload(
        responses=responses,
        final_response=final_response,
        selected_specialists=runtime_selected_specialists,
    )
    branch_dispatch_gate = (
        (profiler_snapshot or {}).get("attributes") or {}
    ).get("branch_dispatch_gate")
    if isinstance(branch_dispatch_gate, dict):
        runtime_payload["branch_dispatch_gate"] = dict(branch_dispatch_gate)
    response_filter = (
        (profiler_snapshot or {}).get("attributes") or {}
    ).get("response_filter")
    if isinstance(response_filter, dict):
        runtime_payload["response_filter"] = dict(response_filter)
    judge_result = _judge_result(profiler_snapshot)
    answer_validation_result = _answer_validation_result(profiler_snapshot)
    answer_coverage_result = _answer_coverage_result(profiler_snapshot)
    answer_value_conflict_result = _answer_value_conflict_result(profiler_snapshot)
    answer_length_result = _answer_length_result(profiler_snapshot)
    if answer_length_result:
        runtime_payload["answer_length"] = answer_length_result
    runtime_payload["decision_path"] = {
        "router": {
            "departments": [
                item
                for item in [contract.departments.primary, *contract.departments.secondary]
                if item
            ],
            "primary_department": contract.departments.primary,
            "strategy": contract.departments.strategy,
            "task_type": contract.intent.task_type,
            "intent": contract.intent.primary,
        },
        "capability": {
            "selected": contract.capabilities.selected,
            "apply": contract.capabilities.apply,
            "confidence": contract.capabilities.confidence,
        },
        "source_owner": {
            "primary": contract.source_owner.primary,
            "reasoning": contract.source_owner.reasoning,
        },
        "specialists": list(runtime_selected_specialists),
        "evidence": {
            "top_sources": list(contract.evidence.top_sources),
        },
        "answer": {
            "final_owner": contract.answer.final_owner,
            "synthesis_policy": contract.answer.synthesis_policy,
            "used_global_synthesis": contract.answer.used_global_synthesis,
        },
        "quality": {
            "judge_action": judge_result.get("action"),
            "validator_status": answer_validation_result.get("status"),
            "validator_mode": answer_validation_result.get("mode"),
            "coverage_status": answer_coverage_result.get("status"),
            "coverage_facet": answer_coverage_result.get("expected_facet"),
            "value_conflict_status": answer_value_conflict_result.get("status"),
            "primary_answer_value": answer_value_conflict_result.get("primary_answer_value"),
            "answer_length_policy": answer_length_result.get("policy"),
            "answer_length_warning": answer_length_result.get("warning"),
        },
    }

    return DecisionTraceRecord(
        trace_id=trace_metadata.get("trace_id"),
        span_id=trace_metadata.get("span_id"),
        runtime_mode=runtime_mode,
        channel=channel,
        context_id=context_id,
        query_log_id=query_log_id,
        is_authenticated=is_authenticated,
        shadow_decision_contract=contract,
        runtime=runtime_payload,
        latency_breakdown=_latency_breakdown(profiler_snapshot),
        llm_call_count=llm_count,
        llm_roles_used=llm_roles,
        llm_usage=llm_usage,
        judge_result=judge_result,
        answer_validation_result=answer_validation_result,
        answer_coverage_result=answer_coverage_result,
        answer_value_conflict_result=answer_value_conflict_result,
        final_answer_preview=answer_preview,
    )


def resolve_decision_trace_path(output_path: str | Path | None = None) -> Path:
    configured = Path(output_path or settings.decision_trace.output_path)
    if configured.is_absolute():
        return configured
    return settings.base_dir / configured


def write_decision_trace_record(
    record: DecisionTraceRecord,
    *,
    output_path: str | Path | None = None,
) -> Path:
    path = resolve_decision_trace_path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = record.model_dump(mode="json", exclude_none=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
        handle.write("\n")
    logger.info("decision_trace_written path=%s trace_id=%s", path, record.trace_id)
    return path
