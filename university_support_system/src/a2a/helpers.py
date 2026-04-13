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
    DataPart,
    Message,
    Role,
    Task,
    TaskState,
    TaskStatus,
    TextPart,
)
from pydantic import ValidationError

from src.db.schemas import DepartmentResponse
from src.orchestrators.response_utils import response_core_answer

_DEPARTMENT_RESPONSE_SCHEMA = "omu.department_response.v1"


@dataclass(frozen=True)
class A2AQueryPayload:
    """A2A task metadata içinde taşınan sorgu yükü."""

    query_text: str
    context_id: str
    task_type: str | None = None
    original_query: str | None = None
    resolved_query: str | None = None
    student_id: int | None = None
    student_number: str | None = None
    student_full_name: str | None = None
    student_department: str | None = None
    student_faculty: str | None = None
    student_type: str | None = None
    llm_profile: str | None = None
    is_authenticated: bool = False
    routing_reason: str | None = None
    conversation_is_follow_up: bool = False
    conversation_topic: str | None = None
    conversation_source_refs: list[str] | None = None
    priority: str = "NORMAL"
    force_llm_synthesis: bool = False
    query_complexity: str | None = None
    is_personal_query: bool = False

    def to_metadata(self) -> dict[str, Any]:
        return {
            "query_text": self.query_text,
            "context_id": self.context_id,
            "task_type": self.task_type,
            "original_query": self.original_query,
            "resolved_query": self.resolved_query,
            "student_id": self.student_id,
            "student_department": self.student_department,
            "student_faculty": self.student_faculty,
            "student_type": self.student_type,
            "llm_profile": self.llm_profile,
            "is_authenticated": self.is_authenticated,
            "routing_reason": self.routing_reason,
            "conversation_is_follow_up": self.conversation_is_follow_up,
            "conversation_topic": self.conversation_topic,
            "conversation_source_refs": list(self.conversation_source_refs or []),
            "priority": self.priority,
            "force_llm_synthesis": self.force_llm_synthesis,
            "query_complexity": self.query_complexity,
            "is_personal_query": self.is_personal_query,
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


def build_department_response_task(
    response: DepartmentResponse,
    *,
    request_task: Task,
    emitter_id: str,
    emitter_name: str,
    task_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Task:
    """DepartmentResponse nesnesini A2A tamamlanmis task'ine sarar."""
    response_task_id = task_id or str(uuid4())
    response_payload = response.model_dump(mode="json")
    response_text = response_core_answer(response)
    merged_metadata = {
        "parent_task_id": request_task.id,
        "emitter_id": emitter_id,
        "emitter_name": emitter_name,
        "response_schema": _DEPARTMENT_RESPONSE_SCHEMA,
    }
    if metadata:
        merged_metadata.update(metadata)

    message = build_text_message(
        response_text,
        context_id=request_task.contextId,
        role=Role.agent,
        task_id=response_task_id,
        metadata={
            "department": response.department.value,
            "success": response.success,
            "emitter_id": emitter_id,
            "emitter_name": emitter_name,
        },
    )
    status = TaskStatus(
        state=TaskState.completed,
        message=message,
        timestamp=datetime.now(UTC).isoformat(),
    )
    artifact = build_text_artifact(
        response_text,
        name=f"{response.department.value}_response_text",
        metadata={
            "department": response.department.value,
            "success": response.success,
            "emitter_id": emitter_id,
            "emitter_name": emitter_name,
            "schema": "text/plain",
        },
    )
    structured_artifact = Artifact(
        artifactId=str(uuid4()),
        name=f"{response.department.value}_response_data",
        description="Structured department response payload",
        extensions=[_DEPARTMENT_RESPONSE_SCHEMA],
        metadata={
            "department": response.department.value,
            "success": response.success,
            "emitter_id": emitter_id,
            "emitter_name": emitter_name,
            "schema": _DEPARTMENT_RESPONSE_SCHEMA,
        },
        parts=[
            DataPart(
                data=response_payload,
                metadata={
                    "schema": _DEPARTMENT_RESPONSE_SCHEMA,
                    "department": response.department.value,
                },
            )
        ],
    )
    return Task(
        id=response_task_id,
        contextId=request_task.contextId,
        status=status,
        metadata=merged_metadata,
        artifacts=[artifact, structured_artifact],
        history=[request_task.status.message, message] if request_task.status.message is not None else [message],
    )


def extract_department_response(task: Task) -> DepartmentResponse | None:
    """A2A response task artifact veya legacy metadata'sindan DepartmentResponse cikarir."""
    for artifact in getattr(task, "artifacts", None) or []:
        for part in getattr(artifact, "parts", None) or []:
            root = getattr(part, "root", part)
            data = getattr(root, "data", None)
            if isinstance(data, dict):
                metadata = getattr(root, "metadata", {}) or {}
                schema = metadata.get("schema") or (getattr(artifact, "metadata", None) or {}).get("schema")
                if schema in {_DEPARTMENT_RESPONSE_SCHEMA, None}:
                    try:
                        return DepartmentResponse.model_validate(data)
                    except ValidationError:
                        continue

    metadata = getattr(task, "metadata", None) or {}
    payload = metadata.get("department_response")
    if isinstance(payload, dict):
        return DepartmentResponse.model_validate(payload)
    return None


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
