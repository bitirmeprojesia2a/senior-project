"""Helpers for orchestrator task construction."""

from __future__ import annotations

from src.a2a import A2AQueryPayload, build_query_task
from src.core.constants import Department, TaskType
from src.orchestrators.query_policy import augment_query_for_department


def build_department_request_task(
    *,
    department: Department,
    query: str,
    context_id: str,
    task_type: TaskType | None,
    metadata: dict,
    disable_specialist_llm: bool = False,
):
    augmented_query = augment_query_for_department(department, query, metadata)
    payload = A2AQueryPayload(
        query_text=augmented_query,
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
        trace_id=metadata.get("trace_id"),
        span_id=metadata.get("span_id"),
        parent_span_id=metadata.get("parent_span_id"),
    )
    task = build_query_task(payload)
    if disable_specialist_llm:
        task.metadata["disable_specialist_llm"] = True
    for key in (
        "original_query",
        "resolved_query",
        "force_llm_synthesis",
        "query_complexity",
        "is_personal_query",
        "final_answer_owner",
        "specialist_response_mode",
        "conversation_is_follow_up",
        "conversation_topic",
        "conversation_source_refs",
        "trace_id",
        "span_id",
        "parent_span_id",
    ):
        if key in metadata:
            task.metadata[key] = metadata[key]
    return task


def build_announcement_request_task(
    *,
    query: str,
    context_id: str,
    routing_reason: str | None,
    departments: list[str] | None = None,
    faculty: str | None = None,
    unit_name: str | None = None,
    conversation_source_refs: list[str] | None = None,
    trace_id: str | None = None,
    span_id: str | None = None,
    parent_span_id: str | None = None,
):
    task = build_query_task(
        A2AQueryPayload(
            query_text=query,
            context_id=context_id,
            routing_reason=routing_reason,
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
        )
    )
    if departments:
        task.metadata["departments"] = departments
    if faculty:
        task.metadata["faculty"] = faculty
    if unit_name:
        task.metadata["unit_name"] = unit_name
    if conversation_source_refs:
        task.metadata["conversation_source_refs"] = list(conversation_source_refs)
    return task


def build_event_request_task(
    *,
    query: str,
    context_id: str,
    routing_reason: str | None = None,
    faculty: str | None = None,
    unit_name: str | None = None,
    limit: int | None = None,
    trace_id: str | None = None,
    span_id: str | None = None,
    parent_span_id: str | None = None,
):
    task = build_query_task(
        A2AQueryPayload(
            query_text=query,
            context_id=context_id,
            routing_reason=routing_reason,
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
        )
    )
    if faculty:
        task.metadata["faculty"] = faculty
    if unit_name:
        task.metadata["unit_name"] = unit_name
    if limit is not None:
        task.metadata["limit"] = int(limit)
    return task
