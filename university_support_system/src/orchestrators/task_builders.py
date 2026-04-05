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
        routing_reason=metadata.get("routing_reason"),
        is_authenticated=bool(metadata.get("is_authenticated", False)),
        student_id=metadata.get("student_id"),
        student_number=metadata.get("student_number"),
        student_full_name=metadata.get("student_full_name"),
        student_department=metadata.get("student_department"),
        student_faculty=metadata.get("student_faculty"),
        student_type=metadata.get("student_type"),
        llm_profile=metadata.get("llm_profile"),
    )
    task = build_query_task(payload)
    if disable_specialist_llm:
        task.metadata["disable_specialist_llm"] = True
    for key in (
        "original_query",
        "resolved_query",
        "conversation_is_follow_up",
        "conversation_topic",
        "conversation_source_refs",
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
):
    task = build_query_task(
        A2AQueryPayload(
            query_text=query,
            context_id=context_id,
            routing_reason=routing_reason,
        )
    )
    if departments:
        task.metadata["departments"] = departments
    return task
