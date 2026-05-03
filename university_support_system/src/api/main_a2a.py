"""Main orchestrator A2A protocol helpers."""

from __future__ import annotations

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
    MessageSendParams,
    Role,
    Task,
    TaskState,
    TaskStatus,
)

from src.a2a import USER_QUERY_RESPONSE_SCHEMA, build_text_artifact, build_text_message
from src.a2a.agent_card_security import a2a_hmac_security_requirement, a2a_hmac_security_schemes
from src.a2a.state import (
    STATE_TRANSITIONS_METADATA_KEY,
    build_state_transition,
    submitted_transition_from_message,
)
from src.a2a.tracing import trace_metadata
from src.core.config import settings
from src.db.schemas import UserQueryResponse


def message_text(message: Message) -> str:
    parts = getattr(message, "parts", None) or []
    text_parts: list[str] = []
    for part in parts:
        root = getattr(part, "root", part)
        text = getattr(root, "text", None)
        if text:
            text_parts.append(str(text))
    return "\n".join(text_parts).strip()


def message_metadata(params: MessageSendParams) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    message_metadata = getattr(params.message, "metadata", None) or {}
    if isinstance(message_metadata, dict):
        metadata.update(message_metadata)
    params_metadata = getattr(params, "metadata", None) or {}
    if isinstance(params_metadata, dict):
        metadata.update(params_metadata)
    return metadata


def main_base_url() -> str:
    configured = (settings.server.public_url or "").strip().rstrip("/")
    if configured:
        return configured
    host = "localhost" if settings.server.host in {"0.0.0.0", "::"} else settings.server.host
    return f"http://{host}:{settings.server.port}"


def main_a2a_url() -> str:
    return f"{main_base_url()}/a2a"


def build_main_agent_card() -> AgentCard:
    return AgentCard(
        name="OMU Main Orchestrator",
        description="OMU destek sistemi icin ana A2A orkestrator ajani.",
        url=main_a2a_url(),
        version=settings.server.app_version,
        provider=AgentProvider(
            organization="Ondokuz Mayis Universitesi",
            url="https://www.omu.edu.tr",
        ),
        capabilities=AgentCapabilities(
            streaming=False,
            pushNotifications=False,
            stateTransitionHistory=True,
        ),
        security=a2a_hmac_security_requirement(),
        securitySchemes=a2a_hmac_security_schemes(),
        defaultInputModes=["text/plain", "application/json"],
        defaultOutputModes=["text/plain", "application/json"],
        skills=[
            AgentSkill(
                id="university_support_query",
                name="University Support Query",
                description=(
                    "Departman, capability ve specialist A2A servislerine "
                    "orkestre edilen destek sorgulari."
                ),
                tags=[
                    "main_orchestrator",
                    "student_affairs",
                    "academic_programs",
                    "finance",
                    "announcement",
                    "event",
                ],
                inputModes=["text/plain", "application/json"],
                outputModes=["text/plain", "application/json"],
            )
        ],
    )


def build_main_agent_card_payload() -> dict[str, Any]:
    return {
        "service_id": "main_orchestrator",
        "name": "OMU Main Orchestrator",
        "url": main_a2a_url(),
        "version": settings.server.app_version,
        "build": settings.server.build_metadata(),
        "capabilities": {
            "a2a_jsonrpc": True,
            "a2a_transport_protocol": settings.a2a.transport_protocol,
            "response_schema": USER_QUERY_RESPONSE_SCHEMA,
            "service_build": settings.server.build_metadata(),
            "service_runtime_label": settings.server.runtime_label,
            "agent_card_path": "/.well-known/agent.json",
            "jsonrpc_path": "/a2a",
            "service_target_kind": "main_orchestrator",
            "service_target": "main_orchestrator",
        },
        "orchestrates": [
            "student_affairs",
            "academic_programs",
            "finance",
            "announcement",
            "event",
        ],
    }


def build_main_agent_status_payload() -> dict[str, Any]:
    card_payload = build_main_agent_card_payload()
    capabilities = card_payload["capabilities"]
    return {
        "agent_id": "main_orchestrator",
        "name": "OMU Main Orchestrator",
        "department": "system",
        "role": "main_orchestrator",
        "description": "Ana sorgu yonlendirme ve birlestirme orkestratoru.",
        "endpoint": main_base_url(),
        "is_active": True,
        "last_heartbeat": datetime.now(UTC).isoformat(),
        "is_stale": False,
        "capabilities": capabilities,
        "service_build": capabilities["service_build"],
        "service_runtime_label": capabilities["service_runtime_label"],
        "is_published_service": True,
    }


def build_user_query_response_task(
    response: UserQueryResponse,
    *,
    request_message: Message,
    trace: dict[str, Any] | None = None,
) -> Task:
    context_id = request_message.contextId or response.query_id or str(uuid4())
    task_id = request_message.taskId or str(uuid4())
    response_text = response.answer
    response_payload = response.model_dump(mode="json")
    request_trace = trace_metadata(trace) or trace_metadata(request_message.metadata)
    response_message = build_text_message(
        response_text,
        context_id=context_id,
        role=Role.agent,
        task_id=task_id,
        metadata={
            "success": True,
            "emitter_id": "main_orchestrator",
            "emitter_name": "OMU Main Orchestrator",
            "departments_involved": response.departments_involved,
            **request_trace,
        },
    )
    status = TaskStatus(
        state=TaskState.completed,
        message=response_message,
        timestamp=datetime.now(UTC).isoformat(),
    )
    structured_artifact = Artifact(
        artifactId=str(uuid4()),
        name="main_orchestrator_response_data",
        description="Structured main orchestrator user query response payload",
        extensions=[USER_QUERY_RESPONSE_SCHEMA],
        metadata={
            "schema": USER_QUERY_RESPONSE_SCHEMA,
            "emitter_id": "main_orchestrator",
            "emitter_name": "OMU Main Orchestrator",
            **request_trace,
        },
        parts=[
            DataPart(
                data=response_payload,
                metadata={
                    "schema": USER_QUERY_RESPONSE_SCHEMA,
                    **request_trace,
                },
            )
        ],
    )
    task_metadata = {
        "parent_message_id": request_message.messageId,
        "emitter_id": "main_orchestrator",
        "emitter_name": "OMU Main Orchestrator",
        "response_schema": USER_QUERY_RESPONSE_SCHEMA,
        **request_trace,
    }
    task_metadata[STATE_TRANSITIONS_METADATA_KEY] = [
        submitted_transition_from_message(
            request_message,
            task_id=task_id,
        ),
        build_state_transition(
            TaskState.working,
            actor_id="main_orchestrator",
            actor_role="agent",
            task_id=task_id,
        ),
        build_state_transition(
            TaskState.completed,
            actor_id="main_orchestrator",
            actor_role="agent",
            task_id=task_id,
            message_id=response_message.messageId,
        ),
    ]
    return Task(
        id=task_id,
        contextId=context_id,
        status=status,
        metadata=task_metadata,
        artifacts=[
            build_text_artifact(
                response_text,
                name="main_orchestrator_response_text",
                metadata={
                    "schema": "text/plain",
                    "emitter_id": "main_orchestrator",
                    **request_trace,
                },
            ),
            structured_artifact,
        ],
        history=[request_message, response_message],
    )
