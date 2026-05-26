"""Execution helpers for standalone A2A agent services."""

from __future__ import annotations

from typing import Any

from a2a.types import Message, MessageSendParams, Task

from src.a2a import (
    A2AQueryPayload,
    SpecialistTarget,
    build_agent_response_task,
    build_query_task,
    extract_agent_response,
    extract_department_response,
)
from src.api.a2a_dispatch import (
    A2ADispatchRequest,
    CapabilityDispatchRequest,
    SpecialistDispatchRequest,
)
from src.api.query_flow import build_dispatch_metadata, resolve_dispatch_context
from src.core.constants import Capability, Department
from src.core.profiling import QueryProfiler, activate_profiler
from src.db import AuthService
from src.db.schemas import DepartmentResponse
from src.orchestrators.department_task_utils import build_specialist_task
from src.orchestrators.task_builders import (
    build_announcement_request_task,
    build_event_request_task,
)


def message_text(message: Message) -> str:
    parts = []
    for part in message.parts:
        root = getattr(part, "root", part)
        text = getattr(root, "text", None)
        if text:
            parts.append(str(text))
    return "\n".join(parts).strip()


def message_metadata(params: MessageSendParams) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    if isinstance(params.metadata, dict):
        metadata.update(params.metadata)
    if isinstance(params.message.metadata, dict):
        metadata.update(params.message.metadata)
    return metadata


def task_type_value(value: Any) -> str | None:
    if value is None:
        return None
    return getattr(value, "value", value)


def _remote_profile_metadata(
    *,
    profiler: QueryProfiler,
    agent_id: str | None,
    agent_role: str,
) -> dict[str, Any]:
    snapshot = profiler.snapshot()
    profile_item = {
        "agent_id": agent_id,
        "agent_role": agent_role,
        "profile": snapshot,
    }
    return {
        "remote_agent_id": agent_id,
        "remote_agent_role": agent_role,
        "remote_profile": snapshot,
        "remote_profiles": [profile_item],
    }


def _with_response_metadata(
    response: DepartmentResponse,
    metadata: dict[str, Any],
) -> DepartmentResponse:
    existing = dict(response.metadata or {})
    merged = {**existing, **metadata}
    remote_profiles: list[dict[str, Any]] = []
    for item in existing.get("remote_profiles") or []:
        if isinstance(item, dict):
            remote_profiles.append(dict(item))
    for item in metadata.get("remote_profiles") or []:
        if isinstance(item, dict):
            remote_profiles.append(dict(item))
    if remote_profiles:
        merged["remote_profiles"] = remote_profiles
    return response.model_copy(
        update={"metadata": merged},
        deep=True,
    )


def department_payload_from_message(
    *,
    department: Department,
    message: Message,
    metadata: dict[str, Any],
    query_text: str,
    context_id: str,
) -> A2ADispatchRequest:
    return A2ADispatchRequest(
        department=department,
        query=query_text,
        context_id=context_id,
        user_id=metadata.get("user_id"),
        full_name=metadata.get("full_name") or metadata.get("student_full_name"),
        student_number=metadata.get("student_number"),
        student_id=metadata.get("student_id"),
        student_department=metadata.get("student_department"),
        student_faculty=metadata.get("student_faculty"),
        student_type=metadata.get("student_type"),
        llm_profile=metadata.get("llm_profile"),
        is_authenticated=bool(metadata.get("is_authenticated", False)),
        session_token=metadata.get("session_token"),
        slack_user_id=metadata.get("slack_user_id"),
        task_type=metadata.get("task_type"),
        original_query=metadata.get("original_query"),
        resolved_query=metadata.get("resolved_query"),
        conversation_is_follow_up=bool(metadata.get("conversation_is_follow_up", False)),
        conversation_topic=metadata.get("conversation_topic"),
        conversation_source_refs=list(metadata.get("conversation_source_refs") or []),
        force_llm_synthesis=bool(metadata.get("force_llm_synthesis", False)),
        query_complexity=metadata.get("query_complexity"),
        is_personal_query=bool(metadata.get("is_personal_query", False)),
        final_answer_owner=metadata.get("final_answer_owner"),
        specialist_response_mode=metadata.get("specialist_response_mode"),
        capability_planner=metadata.get("capability_planner"),
        source_owner=metadata.get("source_owner"),
        policy_facet=metadata.get("policy_facet"),
        decision_contract=metadata.get("decision_contract"),
        resolved_decision=metadata.get("resolved_decision"),
        runtime_authority=metadata.get("runtime_authority"),
        branch_dispatch_gate=metadata.get("branch_dispatch_gate"),
        branch_role=metadata.get("branch_role"),
        retrieval_execution_policy=metadata.get("retrieval_execution_policy"),
        disable_specialist_llm=bool(metadata.get("disable_specialist_llm", False)),
        trace_id=metadata.get("trace_id"),
        span_id=metadata.get("span_id"),
        parent_span_id=metadata.get("parent_span_id"),
    )


async def execute_department_dispatch(
    *,
    payload: A2ADispatchRequest,
    handler: Any,
    auth_service: AuthService,
) -> tuple[DepartmentResponse, str, dict[str, Any]]:
    context_id, resolved = await resolve_dispatch_context(
        payload=payload,
        auth_service=auth_service,
    )
    profiler = QueryProfiler(label=f"remote_department:{payload.department.value}")
    with activate_profiler(profiler):
        response = await handler.handle(
            query_text=payload.query,
            context_id=context_id,
            task_type=payload.task_type,
            metadata=build_dispatch_metadata(payload=payload, resolved=resolved),
        )
    response = _with_response_metadata(
        response,
        _remote_profile_metadata(
            profiler=profiler,
            agent_id=f"{payload.department.value}_orchestrator",
            agent_role="department_orchestrator",
        ),
    )
    return response, context_id, resolved


async def execute_department_message_send(
    *,
    payload: A2ADispatchRequest,
    message: Message,
    handler: Any,
    auth_service: AuthService,
    emitter_id: str,
    emitter_name: str,
) -> Task:
    response, context_id, resolved = await execute_department_dispatch(
        payload=payload,
        handler=handler,
        auth_service=auth_service,
    )
    request_task = build_query_task(
        A2AQueryPayload(
            query_text=payload.query,
            context_id=context_id,
            task_type=task_type_value(payload.task_type),
            original_query=payload.original_query,
            resolved_query=payload.resolved_query,
            student_id=resolved["student_id"],
            student_number=resolved["student_number"],
            student_full_name=resolved["full_name"],
            student_department=resolved["student_department"],
            student_faculty=resolved["student_faculty"],
            student_type=resolved["student_type"],
            llm_profile=payload.llm_profile,
            is_authenticated=resolved["is_authenticated"],
            conversation_is_follow_up=payload.conversation_is_follow_up,
            conversation_topic=payload.conversation_topic,
            conversation_source_refs=list(payload.conversation_source_refs or []),
            force_llm_synthesis=payload.force_llm_synthesis,
            query_complexity=payload.query_complexity,
            is_personal_query=payload.is_personal_query,
            final_answer_owner=payload.final_answer_owner,
            specialist_response_mode=payload.specialist_response_mode,
            capability_planner=payload.capability_planner,
            source_owner=payload.source_owner,
            policy_facet=payload.policy_facet,
            decision_contract=payload.decision_contract,
            resolved_decision=payload.resolved_decision,
            runtime_authority=payload.runtime_authority,
            branch_dispatch_gate=payload.branch_dispatch_gate,
            branch_role=payload.branch_role,
            retrieval_execution_policy=payload.retrieval_execution_policy,
            trace_id=payload.trace_id,
            span_id=payload.span_id,
            parent_span_id=payload.parent_span_id,
        ),
        task_id=message.taskId,
    )
    return build_agent_response_task(
        response,
        request_task=request_task,
        emitter_id=emitter_id,
        emitter_name=emitter_name,
        metadata={"transport": "jsonrpc", "method": "message/send"},
    )


def capability_payload_from_message(
    *,
    capability: Capability,
    metadata: dict[str, Any],
    query_text: str,
    context_id: str,
) -> CapabilityDispatchRequest:
    return CapabilityDispatchRequest(
        capability=capability,
        query=query_text,
        context_id=context_id,
        routing_reason=metadata.get("routing_reason"),
        departments=list(metadata.get("departments") or []),
        faculty=metadata.get("faculty"),
        unit_name=metadata.get("unit_name"),
        conversation_source_refs=list(metadata.get("conversation_source_refs") or []),
        allow_latest_fallback=bool(metadata.get("allow_latest_fallback", True)),
        probe_mode=metadata.get("probe_mode"),
        require_keyword_match=bool(metadata.get("require_keyword_match", False)),
        minimum_match_score=metadata.get("minimum_match_score"),
        recent_days=metadata.get("recent_days"),
        limit=int(metadata.get("limit") or 5),
        decision_contract=metadata.get("decision_contract"),
        resolved_decision=metadata.get("resolved_decision"),
        runtime_authority=metadata.get("runtime_authority"),
        trace_id=metadata.get("trace_id"),
        span_id=metadata.get("span_id"),
        parent_span_id=metadata.get("parent_span_id"),
    )


def build_capability_request_task(payload: CapabilityDispatchRequest) -> Task:
    if payload.capability is Capability.ANNOUNCEMENT:
        request_task = build_announcement_request_task(
            query=payload.query,
            context_id=payload.context_id or "",
            routing_reason=payload.routing_reason,
            departments=payload.departments,
            faculty=payload.faculty,
            unit_name=payload.unit_name,
            conversation_source_refs=payload.conversation_source_refs,
            decision_contract=payload.decision_contract,
            resolved_decision=payload.resolved_decision,
            runtime_authority=payload.runtime_authority,
            trace_id=payload.trace_id,
            span_id=payload.span_id,
            parent_span_id=payload.parent_span_id,
        )
        request_task.metadata["allow_latest_fallback"] = payload.allow_latest_fallback
        if payload.probe_mode:
            request_task.metadata["probe_mode"] = payload.probe_mode
        request_task.metadata["require_keyword_match"] = payload.require_keyword_match
        if payload.minimum_match_score is not None:
            request_task.metadata["minimum_match_score"] = payload.minimum_match_score
        if payload.recent_days is not None:
            request_task.metadata["recent_days"] = payload.recent_days
        return request_task

    return build_event_request_task(
        query=payload.query,
        context_id=payload.context_id or "",
        routing_reason=payload.routing_reason,
        departments=payload.departments,
        faculty=payload.faculty,
        unit_name=payload.unit_name,
        limit=payload.limit,
        decision_contract=payload.decision_contract,
        resolved_decision=payload.resolved_decision,
        runtime_authority=payload.runtime_authority,
        trace_id=payload.trace_id,
        span_id=payload.span_id,
        parent_span_id=payload.parent_span_id,
    )


async def execute_capability_message_send(
    *,
    payload: CapabilityDispatchRequest,
    handler: Any,
) -> Task:
    request_task = build_capability_request_task(payload)
    response_task = await handler.handle_task(request_task)
    if extract_agent_response(response_task) is None:
        raise ValueError(f"{payload.capability.value} capability agent gecerli response dondurmedi.")
    return response_task


async def execute_capability_dispatch(
    *,
    payload: CapabilityDispatchRequest,
    handler: Any,
) -> DepartmentResponse:
    response_task = await execute_capability_message_send(payload=payload, handler=handler)
    response = extract_department_response(response_task)
    if response is None:
        raise ValueError(f"{payload.capability.value} capability agent gecerli response dondurmedi.")
    return response


def specialist_payload_from_message(
    *,
    target: SpecialistTarget,
    metadata: dict[str, Any],
    query_text: str,
    context_id: str,
) -> SpecialistDispatchRequest:
    return SpecialistDispatchRequest(
        department=target.department,
        agent_id=target.agent_id,
        query=query_text,
        context_id=context_id,
        task_type=metadata.get("task_type"),
        student_id=metadata.get("student_id"),
        student_department=metadata.get("student_department"),
        student_faculty=metadata.get("student_faculty"),
        student_type=metadata.get("student_type"),
        llm_profile=metadata.get("llm_profile"),
        is_authenticated=bool(metadata.get("is_authenticated", False)),
        original_query=metadata.get("original_query"),
        resolved_query=metadata.get("resolved_query"),
        conversation_is_follow_up=bool(metadata.get("conversation_is_follow_up", False)),
        conversation_topic=metadata.get("conversation_topic"),
        conversation_source_refs=list(metadata.get("conversation_source_refs") or []),
        force_llm_synthesis=bool(metadata.get("force_llm_synthesis", False)),
        query_complexity=metadata.get("query_complexity"),
        is_personal_query=bool(metadata.get("is_personal_query", False)),
        final_answer_owner=metadata.get("final_answer_owner"),
        specialist_response_mode=metadata.get("specialist_response_mode"),
        capability_planner=metadata.get("capability_planner"),
        source_owner=metadata.get("source_owner"),
        policy_facet=metadata.get("policy_facet"),
        decision_contract=metadata.get("decision_contract"),
        resolved_decision=metadata.get("resolved_decision"),
        runtime_authority=metadata.get("runtime_authority"),
        branch_dispatch_gate=metadata.get("branch_dispatch_gate"),
        specialist_selection=metadata.get("specialist_selection"),
        branch_role=metadata.get("branch_role"),
        retrieval_execution_policy=metadata.get("retrieval_execution_policy"),
        disable_specialist_llm=bool(metadata.get("disable_specialist_llm", False)),
        trace_id=metadata.get("trace_id"),
        span_id=metadata.get("span_id"),
        parent_span_id=metadata.get("parent_span_id"),
    )


def build_specialist_dispatch_metadata(payload: SpecialistDispatchRequest) -> dict[str, Any]:
    return {
        "student_id": payload.student_id,
        "student_department": payload.student_department,
        "student_faculty": payload.student_faculty,
        "student_type": payload.student_type,
        "llm_profile": payload.llm_profile,
        "is_authenticated": payload.is_authenticated,
        "original_query": payload.original_query,
        "resolved_query": payload.resolved_query,
        "conversation_is_follow_up": payload.conversation_is_follow_up,
        "conversation_topic": payload.conversation_topic,
        "conversation_source_refs": list(payload.conversation_source_refs),
        "force_llm_synthesis": payload.force_llm_synthesis,
        "query_complexity": payload.query_complexity,
        "is_personal_query": payload.is_personal_query,
        "final_answer_owner": payload.final_answer_owner,
        "specialist_response_mode": payload.specialist_response_mode,
        "capability_planner": payload.capability_planner,
        "source_owner": payload.source_owner,
        "policy_facet": payload.policy_facet,
        "decision_contract": payload.decision_contract,
        "resolved_decision": payload.resolved_decision,
        "runtime_authority": payload.runtime_authority,
        "branch_dispatch_gate": payload.branch_dispatch_gate,
        "specialist_selection": payload.specialist_selection,
        "branch_role": payload.branch_role,
        "retrieval_execution_policy": payload.retrieval_execution_policy,
        "disable_specialist_llm": payload.disable_specialist_llm,
        "trace_id": payload.trace_id,
        "span_id": payload.span_id,
        "parent_span_id": payload.parent_span_id,
    }


async def execute_specialist_message_send(
    *,
    payload: SpecialistDispatchRequest,
    message: Message | None,
    handler: Any,
) -> Task:
    metadata = build_specialist_dispatch_metadata(payload)
    _, request_task = build_specialist_task(
        query_text=payload.query,
        context_id=payload.context_id or "",
        task_type=payload.task_type,
        metadata=metadata,
    )
    if message is not None and message.taskId:
        request_task.id = message.taskId
    profiler = QueryProfiler(label=f"remote_specialist:{payload.agent_id}")
    with activate_profiler(profiler):
        response_task = await handler.handle_task(request_task)
    response = extract_agent_response(response_task)
    if response is None:
        raise ValueError(f"{payload.agent_id} specialist agent gecerli response dondurmedi.")
    response = response.model_copy(
        update={
            "metadata": {
                **dict(response.metadata or {}),
                **_remote_profile_metadata(
                    profiler=profiler,
                    agent_id=payload.agent_id,
                    agent_role="specialist_agent",
                ),
            }
        },
        deep=True,
    )
    emitter_name = getattr(getattr(handler, "definition", None), "name", payload.agent_id)
    return build_agent_response_task(
        response,
        request_task=request_task,
        emitter_id=getattr(handler, "agent_id", payload.agent_id),
        emitter_name=emitter_name,
        metadata=dict(response.metadata or {}),
    )


async def execute_specialist_dispatch(
    *,
    payload: SpecialistDispatchRequest,
    handler: Any,
) -> DepartmentResponse:
    response_task = await execute_specialist_message_send(
        payload=payload,
        message=None,
        handler=handler,
    )
    response = extract_department_response(response_task)
    if response is None:
        raise ValueError(f"{payload.agent_id} specialist agent gecerli response dondurmedi.")
    return response


__all__ = [
    "build_capability_request_task",
    "build_specialist_dispatch_metadata",
    "capability_payload_from_message",
    "department_payload_from_message",
    "execute_capability_dispatch",
    "execute_capability_message_send",
    "execute_department_dispatch",
    "execute_department_message_send",
    "execute_specialist_dispatch",
    "execute_specialist_message_send",
    "message_metadata",
    "message_text",
    "specialist_payload_from_message",
    "task_type_value",
]
