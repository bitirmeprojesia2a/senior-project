"""Helpers for building department-orchestrator tasks."""

from __future__ import annotations

from a2a.types import Task

from src.a2a import A2AQueryPayload, build_query_task
from src.core.constants import TaskType

SPECIALIST_METADATA_PASSTHROUGH_KEYS = (
    "disable_specialist_llm",
    "llm_profile",
    "query_log_id",
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
    payload = A2AQueryPayload(
        query_text=query_text,
        context_id=context_id,
        task_type=task_type.value if task_type else None,
        routing_reason=(metadata or {}).get("routing_reason"),
        is_authenticated=bool((metadata or {}).get("is_authenticated", False)),
        student_id=(metadata or {}).get("student_id"),
        student_number=(metadata or {}).get("student_number"),
        student_full_name=(metadata or {}).get("student_full_name"),
        student_department=(metadata or {}).get("student_department"),
        student_faculty=(metadata or {}).get("student_faculty"),
        student_type=(metadata or {}).get("student_type"),
        llm_profile=(metadata or {}).get("llm_profile"),
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
    for key in SPECIALIST_METADATA_PASSTHROUGH_KEYS:
        if key in metadata:
            task.metadata[key] = metadata[key]
    return payload, task
