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

from src.a2a.responses import (
    AgentResponse,
    agent_response_to_department_response,
    department_response_to_agent_response,
    validate_agent_response,
    validate_legacy_department_response,
)
from src.a2a.schemas import AGENT_RESPONSE_SCHEMA, DEPARTMENT_RESPONSE_SCHEMA
from src.a2a.state import STATE_TRANSITIONS_METADATA_KEY, build_state_transition, response_state_transitions
from src.a2a.tracing import ensure_trace_metadata, trace_metadata
from src.core.config import settings
from src.db.schemas import DepartmentResponse
from src.orchestrators.response_utils import response_core_answer


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
    final_answer_owner: str | None = None
    specialist_response_mode: str | None = None
    capability_planner: dict[str, Any] | None = None
    source_owner: dict[str, Any] | None = None
    policy_facet: dict[str, Any] | None = None
    answer_contract: dict[str, Any] | None = None
    decision_contract: dict[str, Any] | None = None
    resolved_decision: dict[str, Any] | None = None
    runtime_authority: dict[str, Any] | None = None
    branch_dispatch_gate: dict[str, Any] | None = None
    specialist_selection: dict[str, Any] | None = None
    branch_role: str | None = None
    retrieval_execution_policy: dict[str, Any] | None = None
    trace_id: str | None = None
    span_id: str | None = None
    parent_span_id: str | None = None

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
            "final_answer_owner": self.final_answer_owner,
            "specialist_response_mode": self.specialist_response_mode,
            "capability_planner": dict(self.capability_planner) if self.capability_planner else None,
            "source_owner": dict(self.source_owner) if self.source_owner else None,
            "policy_facet": dict(self.policy_facet) if self.policy_facet else None,
            "answer_contract": dict(self.answer_contract) if self.answer_contract else None,
            "decision_contract": dict(self.decision_contract) if self.decision_contract else None,
            "resolved_decision": dict(self.resolved_decision) if self.resolved_decision else None,
            "runtime_authority": (
                dict(self.runtime_authority) if self.runtime_authority else None
            ),
            "branch_dispatch_gate": (
                dict(self.branch_dispatch_gate) if self.branch_dispatch_gate else None
            ),
            "specialist_selection": (
                dict(self.specialist_selection) if self.specialist_selection else None
            ),
            "branch_role": self.branch_role,
            "retrieval_execution_policy": (
                dict(self.retrieval_execution_policy)
                if self.retrieval_execution_policy
                else None
            ),
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
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
    metadata = ensure_trace_metadata(
        payload.to_metadata(),
        trace_id=payload.trace_id,
        span_id=payload.span_id,
        parent_span_id=payload.parent_span_id,
    )
    message = build_text_message(
        payload.query_text,
        context_id=payload.context_id,
        role=Role.user,
        task_id=task_id,
        metadata=metadata,
    )
    status = TaskStatus(
        state=state,
        message=message,
        timestamp=datetime.now(UTC).isoformat(),
    )
    metadata[STATE_TRANSITIONS_METADATA_KEY] = [
        build_state_transition(
            state,
            actor_id="user",
            actor_role="user",
            task_id=task_id,
            message_id=message.messageId,
            timestamp=status.timestamp,
        )
    ]
    return Task(
        id=task_id,
        contextId=payload.context_id,
        status=status,
        metadata=metadata,
    )


def build_agent_response_task(
    response: DepartmentResponse | AgentResponse,
    *,
    request_task: Task,
    emitter_id: str,
    emitter_name: str,
    task_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Task:
    """Wrap the shared agent response payload in an A2A task."""
    response_task_id = task_id or str(uuid4())
    response = department_response_to_agent_response(
        response,
        agent_id=emitter_id,
        agent_name=emitter_name,
        agent_role=(metadata or {}).get("agent_role"),
        capability=(metadata or {}).get("capability"),
        metadata=metadata,
    )
    legacy_response = agent_response_to_department_response(response)
    response_payload = response.model_dump(mode="json", exclude_none=True)
    response_text = response_core_answer(legacy_response) if legacy_response else response.answer
    response_target = (
        response.department.value
        if response.department is not None
        else response.capability or response.agent_id or "agent"
    )
    inherited_trace = trace_metadata(request_task.metadata)
    merged_metadata = {
        "parent_task_id": request_task.id,
        "emitter_id": emitter_id,
        "emitter_name": emitter_name,
        "response_schema": AGENT_RESPONSE_SCHEMA,
        "agent_response_schema": AGENT_RESPONSE_SCHEMA,
        "legacy_response_schema": DEPARTMENT_RESPONSE_SCHEMA,
    }
    merged_metadata.update(inherited_trace)
    if metadata:
        merged_metadata.update(metadata)
    output_trace = trace_metadata(merged_metadata)

    message = build_text_message(
        response_text,
        context_id=request_task.contextId,
        role=Role.agent,
        task_id=response_task_id,
        metadata={
            "agent_id": response.agent_id,
            "agent_name": response.agent_name,
            "agent_role": response.agent_role,
            "capability": response.capability,
            "department": response.department.value if response.department else None,
            "success": response.success,
            "emitter_id": emitter_id,
            "emitter_name": emitter_name,
            "response_schema": AGENT_RESPONSE_SCHEMA,
            **output_trace,
        },
    )
    status = TaskStatus(
        state=TaskState.completed,
        message=message,
        timestamp=datetime.now(UTC).isoformat(),
    )
    merged_metadata[STATE_TRANSITIONS_METADATA_KEY] = response_state_transitions(
        request_task,
        response_task_id=response_task_id,
        response_message_id=message.messageId,
        actor_id=emitter_id,
    )
    artifact = build_text_artifact(
        response_text,
        name=f"{response_target}_response_text",
        metadata={
            "agent_id": response.agent_id,
            "agent_name": response.agent_name,
            "agent_role": response.agent_role,
            "capability": response.capability,
            "department": response.department.value if response.department else None,
            "success": response.success,
            "emitter_id": emitter_id,
            "emitter_name": emitter_name,
            "schema": "text/plain",
            **output_trace,
        },
    )
    structured_artifact = Artifact(
        artifactId=str(uuid4()),
        name=f"{response_target}_agent_response_data",
        description="Structured agent response payload",
        extensions=[AGENT_RESPONSE_SCHEMA, DEPARTMENT_RESPONSE_SCHEMA],
        metadata={
            "agent_id": response.agent_id,
            "agent_name": response.agent_name,
            "agent_role": response.agent_role,
            "capability": response.capability,
            "department": response.department.value if response.department else None,
            "success": response.success,
            "emitter_id": emitter_id,
            "emitter_name": emitter_name,
            "schema": AGENT_RESPONSE_SCHEMA,
            "agent_response_schema": AGENT_RESPONSE_SCHEMA,
            "legacy_schema": DEPARTMENT_RESPONSE_SCHEMA,
            **output_trace,
        },
        parts=[
            DataPart(
                data=response_payload,
                metadata={
                    "schema": AGENT_RESPONSE_SCHEMA,
                    "agent_response_schema": AGENT_RESPONSE_SCHEMA,
                    "legacy_schema": DEPARTMENT_RESPONSE_SCHEMA,
                    "agent_id": response.agent_id,
                    "agent_name": response.agent_name,
                    "agent_role": response.agent_role,
                    "capability": response.capability,
                    "department": response.department.value if response.department else None,
                    **output_trace,
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


def build_department_response_task(
    response: DepartmentResponse | AgentResponse,
    *,
    request_task: Task,
    emitter_id: str,
    emitter_name: str,
    task_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Task:
    """Backward-compatible alias for the generic AgentResponse task builder."""
    return build_agent_response_task(
        response,
        request_task=request_task,
        emitter_id=emitter_id,
        emitter_name=emitter_name,
        task_id=task_id,
        metadata=metadata,
    )


def extract_agent_response(task: Task) -> AgentResponse | None:
    """A2A AgentResponse artifact veya legacy payload'dan generic response cikarir."""
    for artifact in getattr(task, "artifacts", None) or []:
        artifact_metadata = getattr(artifact, "metadata", None) or {}
        artifact_extensions = set(getattr(artifact, "extensions", None) or [])
        for part in getattr(artifact, "parts", None) or []:
            root = getattr(part, "root", part)
            data = getattr(root, "data", None)
            if isinstance(data, dict):
                metadata = getattr(root, "metadata", {}) or {}
                schema = metadata.get("schema") or artifact_metadata.get("schema")
                legacy_schema = metadata.get("legacy_schema") or artifact_metadata.get("legacy_schema")
                known_schema = (
                    schema in {AGENT_RESPONSE_SCHEMA, DEPARTMENT_RESPONSE_SCHEMA, None}
                    or legacy_schema == DEPARTMENT_RESPONSE_SCHEMA
                    or AGENT_RESPONSE_SCHEMA in artifact_extensions
                    or DEPARTMENT_RESPONSE_SCHEMA in artifact_extensions
                )
                if known_schema:
                    try:
                        return validate_agent_response(data)
                    except ValidationError:
                        try:
                            legacy_response = validate_legacy_department_response(data)
                            return department_response_to_agent_response(legacy_response)
                        except ValidationError:
                            continue

    metadata = getattr(task, "metadata", None) or {}
    payload = metadata.get("department_response")
    if isinstance(payload, dict):
        try:
            return validate_agent_response(payload)
        except ValidationError:
            return department_response_to_agent_response(validate_legacy_department_response(payload))
    return None


def extract_department_response(task: Task) -> DepartmentResponse | None:
    """Legacy DepartmentResponse modelini A2A AgentResponse artifact'inden cikarir."""
    response = extract_agent_response(task)
    if response is None:
        return None
    return agent_response_to_department_response(response)


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
            organization=settings.institution.name_ascii,
            url=settings.institution.homepage_url,
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
