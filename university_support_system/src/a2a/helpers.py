"""A2A SDK yardımcıları."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentProvider,
    AgentSkill,
    Artifact,
    Message,
    Role,
    Task,
    TaskState,
    TaskStatus,
    TextPart,
)


@dataclass(frozen=True)
class A2AQueryPayload:
    """A2A task metadata içinde taşınan sorgu yükü."""

    query_text: str
    context_id: str
    task_type: str | None = None
    student_id: int | None = None
    is_authenticated: bool = False
    routing_reason: str | None = None
    priority: str = "NORMAL"

    def to_metadata(self) -> dict[str, Any]:
        return {
            "query_text": self.query_text,
            "context_id": self.context_id,
            "task_type": self.task_type,
            "student_id": self.student_id,
            "is_authenticated": self.is_authenticated,
            "routing_reason": self.routing_reason,
            "priority": self.priority,
        }


def build_text_message(
    text: str,
    *,
    context_id: str,
    role: Role,
    task_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Message:
    """Basit text tabanlı A2A mesajı üretir."""
    return Message(
        contextId=context_id,
        messageId=str(uuid4()),
        role=role,
        taskId=task_id,
        metadata=metadata or {},
        parts=[TextPart(text=text)],
    )


def build_text_artifact(
    text: str,
    *,
    name: str = "response",
    metadata: dict[str, Any] | None = None,
) -> Artifact:
    """Metin artifact'i üretir."""
    return Artifact(
        artifactId=str(uuid4()),
        name=name,
        metadata=metadata or {},
        parts=[TextPart(text=text)],
    )


def build_query_task(
    payload: A2AQueryPayload,
    *,
    task_id: str | None = None,
    state: TaskState = TaskState.submitted,
) -> Task:
    """Kullanıcı sorgusu için A2A task oluşturur."""
    task_id = task_id or str(uuid4())
    message = build_text_message(
        payload.query_text,
        context_id=payload.context_id,
        role=Role.user,
        task_id=task_id,
        metadata=payload.to_metadata(),
    )
    status = TaskStatus(
        state=state,
        message=message,
        timestamp=datetime.now(UTC).isoformat(),
    )
    return Task(
        id=task_id,
        contextId=payload.context_id,
        status=status,
        metadata=payload.to_metadata(),
    )


def build_agent_card(
    *,
    agent_id: str,
    name: str,
    description: str,
    url: str,
    version: str = "0.1.0",
    skills: list[AgentSkill],
) -> AgentCard:
    """Uzman ajan veya orkestratör için AgentCard üretir."""
    return AgentCard(
        name=name,
        description=description,
        url=url,
        version=version,
        provider=AgentProvider(
            organization="Ondokuz Mayis Universitesi",
            url="https://omu.edu.tr",
        ),
        capabilities=AgentCapabilities(
            streaming=True,
            pushNotifications=False,
            stateTransitionHistory=True,
        ),
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=skills,
    )
