"""Helpers for building department-orchestrator tasks."""

from __future__ import annotations

from a2a.types import Task

from src.a2a import A2AQueryPayload, build_query_task
from src.core.constants import TaskType

SPECIALIST_METADATA_PASSTHROUGH_KEYS = (
    "disable_specialist_llm",
    "llm_profile",
    "query_log_id",
    "force_llm_synthesis",
    "query_complexity",
    "is_personal_query",
    "final_answer_owner",
    "specialist_response_mode",
    "capability_planner",
    "source_owner",
    "policy_facet",
    "answer_contract",
    "decision_contract",
    "resolved_decision",
    "runtime_authority",
    "specialist_selection",
    "original_query",
    "resolved_query",
    "conversation_is_follow_up",
    "conversation_topic",
    "conversation_source_refs",
    "trace_id",
    "span_id",
    "parent_span_id",
    "branch_role",
    "retrieval_execution_policy",
)


def extract_query_from_task(task: Task) -> str:
    """Extract the first text content from an A2A task message."""
    message = task.status.message
    if message is None:
        return ""
    for part in message.parts:
        text = getattr(part, "text", None)
        if text:
            return str(text)
        root = getattr(part, "root", None)
        text = getattr(root, "text", None)
        if text:
            return str(text)
    return ""


def build_request_task(
    *,
    query_text: str,
    context_id: str,
    task_type: TaskType | None,
    metadata: dict | None,
) -> Task:
    """Build the outer department request task."""
    meta = metadata or {}
    payload = A2AQueryPayload(
        query_text=query_text,
        context_id=context_id,
        task_type=task_type.value if task_type else None,
        original_query=meta.get("original_query"),
        resolved_query=meta.get("resolved_query"),
        routing_reason=meta.get("routing_reason"),
        is_authenticated=bool(meta.get("is_authenticated", False)),
        student_id=meta.get("student_id"),
        student_number=meta.get("student_number"),
        student_full_name=meta.get("student_full_name"),
        student_department=meta.get("student_department"),
        student_faculty=meta.get("student_faculty"),
        student_type=meta.get("student_type"),
        llm_profile=meta.get("llm_profile"),
        conversation_is_follow_up=bool(meta.get("conversation_is_follow_up", False)),
        conversation_topic=meta.get("conversation_topic"),
        conversation_source_refs=list(meta.get("conversation_source_refs") or []),
        force_llm_synthesis=bool(meta.get("force_llm_synthesis", False)),
        query_complexity=meta.get("query_complexity"),
        is_personal_query=bool(meta.get("is_personal_query", False)),
        final_answer_owner=meta.get("final_answer_owner"),
        specialist_response_mode=meta.get("specialist_response_mode"),
        capability_planner=meta.get("capability_planner"),
        source_owner=meta.get("source_owner"),
        policy_facet=meta.get("policy_facet"),
        answer_contract=meta.get("answer_contract"),
        decision_contract=meta.get("decision_contract"),
        resolved_decision=meta.get("resolved_decision"),
        runtime_authority=meta.get("runtime_authority"),
        specialist_selection=meta.get("specialist_selection"),
        trace_id=meta.get("trace_id"),
        span_id=meta.get("span_id"),
        parent_span_id=meta.get("parent_span_id"),
        branch_role=meta.get("branch_role"),
        retrieval_execution_policy=meta.get("retrieval_execution_policy"),
    )
    return build_query_task(payload)


def build_specialist_task(
    *,
    query_text: str,
    context_id: str,
    task_type: TaskType | None,
    metadata: dict,
) -> tuple[A2AQueryPayload, Task]:
    """Build the inner specialist-agent task and payload."""
    payload = A2AQueryPayload(
        query_text=query_text,
        context_id=context_id,
        task_type=task_type.value if task_type else None,
        original_query=metadata.get("original_query"),
        resolved_query=metadata.get("resolved_query"),
        routing_reason=metadata.get("routing_reason"),
        is_authenticated=bool(metadata.get("is_authenticated", False)),
        student_id=metadata.get("student_id"),
        student_number=metadata.get("student_number"),
        student_full_name=metadata.get("student_full_name"),
        student_department=metadata.get("student_department"),
        student_faculty=metadata.get("student_faculty"),
        student_type=metadata.get("student_type"),
        llm_profile=metadata.get("llm_profile"),
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
        answer_contract=metadata.get("answer_contract"),
        decision_contract=metadata.get("decision_contract"),
        resolved_decision=metadata.get("resolved_decision"),
        runtime_authority=metadata.get("runtime_authority"),
        specialist_selection=metadata.get("specialist_selection"),
        trace_id=metadata.get("trace_id"),
        span_id=metadata.get("span_id"),
        parent_span_id=metadata.get("parent_span_id"),
        branch_role=metadata.get("branch_role"),
        retrieval_execution_policy=metadata.get("retrieval_execution_policy"),
    )
    task = build_query_task(payload)
    for key in SPECIALIST_METADATA_PASSTHROUGH_KEYS:
        if key in metadata:
            task.metadata[key] = metadata[key]
    return payload, task
