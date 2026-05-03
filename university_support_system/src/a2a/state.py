"""A2A task state transition metadata helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from a2a.types import Message, Task, TaskState

STATE_TRANSITIONS_METADATA_KEY = "state_transitions"


def _state_value(state: TaskState | str) -> str:
    return str(getattr(state, "value", state))


def _utc_timestamp() -> str:
    return datetime.now(UTC).isoformat()


def build_state_transition(
    state: TaskState | str,
    *,
    actor_id: str | None = None,
    actor_role: str | None = None,
    task_id: str | None = None,
    message_id: str | None = None,
    timestamp: str | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    """Build a compact transition entry suitable for task metadata."""
    transition: dict[str, Any] = {
        "state": _state_value(state),
        "timestamp": timestamp or _utc_timestamp(),
    }
    optional_fields = {
        "actor_id": actor_id,
        "actor_role": actor_role,
        "task_id": task_id,
        "message_id": message_id,
        "reason": reason,
    }
    transition.update({key: value for key, value in optional_fields.items() if value})
    return transition


def metadata_state_transitions(metadata: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Return sanitized transition entries from metadata."""
    raw_transitions = (metadata or {}).get(STATE_TRANSITIONS_METADATA_KEY)
    if not isinstance(raw_transitions, list):
        return []
    return [item for item in raw_transitions if isinstance(item, dict) and item.get("state")]


def task_state_transitions(task: Task) -> list[dict[str, Any]]:
    """Read explicit transition history, falling back to the task's current status."""
    transitions = metadata_state_transitions(task.metadata)
    if transitions:
        return list(transitions)
    status = getattr(task, "status", None)
    if status is None:
        return []
    message = getattr(status, "message", None)
    return [
        build_state_transition(
            getattr(status, "state", TaskState.unknown),
            task_id=task.id,
            message_id=getattr(message, "messageId", None),
            timestamp=getattr(status, "timestamp", None),
        )
    ]


def submitted_transition_from_message(
    message: Message,
    *,
    task_id: str,
    actor_id: str = "user",
) -> dict[str, Any]:
    """Create a submitted transition for a JSON-RPC message/send request."""
    return build_state_transition(
        TaskState.submitted,
        actor_id=actor_id,
        actor_role="user",
        task_id=task_id,
        message_id=message.messageId,
    )


def response_state_transitions(
    request_task: Task,
    *,
    response_task_id: str,
    response_message_id: str,
    actor_id: str,
    actor_role: str = "agent",
) -> list[dict[str, Any]]:
    """Create a synchronous submitted/working/completed transition history."""
    transitions = task_state_transitions(request_task)
    transitions.append(
        build_state_transition(
            TaskState.working,
            actor_id=actor_id,
            actor_role=actor_role,
            task_id=request_task.id,
        )
    )
    transitions.append(
        build_state_transition(
            TaskState.completed,
            actor_id=actor_id,
            actor_role=actor_role,
            task_id=response_task_id,
            message_id=response_message_id,
        )
    )
    return transitions
