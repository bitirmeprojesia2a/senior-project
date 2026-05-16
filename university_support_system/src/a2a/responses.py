"""A2A AgentResponse contract and legacy adapters."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from src.core.constants import Department
from src.db.schemas import DepartmentResponse, RAGSource


class AgentResponse(BaseModel):
    """Published A2A response payload.

    This is the domain payload carried inside an A2A Task artifact. It is
    intentionally agent-oriented; department is optional context instead of the
    root identity of the response.
    """

    agent_id: str | None = None
    agent_name: str | None = None
    agent_role: str | None = None
    capability: str | None = None
    department: Department | None = None
    answer: str
    sources: list[RAGSource] = Field(default_factory=list)
    db_data: dict[str, Any] | None = None
    generation_mode: str | None = None
    include_contact_suggestion: bool = False
    success: bool = True
    response_time_ms: float | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


_LEGACY_METADATA_KEYS = frozenset({
    "remote_profile",
    "remote_profiles",
    "transport",
    "protocol",
    "selected_agent_id",
    "specialist_selection",
    "transport_error",
    "detail",
    "endpoint",
    "attempt",
    "timeout_seconds",
    "http_status",
    "circuit_failures",
    "circuit_opened_until",
})


_TRACE_METADATA_KEYS = frozenset({
    "answer_coverage",
    "answer_coverage_validator",
    "answer_validation",
    "answer_value_conflict",
    "answer_value_conflict_validator",
    "branch_dispatch_gate",
    "capability_planner",
    "decision_contract",
    "resolved_decision",
    "evidence_packet",
    "final_answer_owner",
    "final_attempt_provider_error_stats",
    "llm_key_distribution",
    "llm_usage",
    "provider_org_fingerprints",
    "quality_check",
    "retrieval_execution_policy",
    "retrieval_execution_stats",
    "specialist_response_mode",
    "specialist_selection",
    "source_owner",
})


def department_response_to_agent_response(
    response: DepartmentResponse | AgentResponse,
    *,
    agent_id: str | None = None,
    agent_name: str | None = None,
    agent_role: str | None = None,
    capability: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> AgentResponse:
    """Convert the legacy internal response model to the A2A AgentResponse."""
    if isinstance(response, AgentResponse):
        update_data = {}
        if agent_id and not response.agent_id:
            update_data["agent_id"] = agent_id
        if agent_name and not response.agent_name:
            update_data["agent_name"] = agent_name
        if agent_role and not response.agent_role:
            update_data["agent_role"] = agent_role
        if capability and not response.capability:
            update_data["capability"] = capability
        if metadata:
            update_data["metadata"] = {**response.metadata, **metadata}
        return response.model_copy(update=update_data) if update_data else response

    response_metadata: dict[str, Any] = {
        "legacy_department": response.department.value,
        **dict(response.metadata or {}),
    }
    if metadata:
        response_metadata.update(metadata)
    return AgentResponse(
        agent_id=agent_id,
        agent_name=agent_name,
        agent_role=agent_role,
        capability=capability,
        department=response.department,
        answer=response.answer,
        sources=response.sources,
        db_data=response.db_data,
        generation_mode=response.generation_mode,
        include_contact_suggestion=response.include_contact_suggestion,
        success=response.success,
        response_time_ms=response.response_time_ms,
        error=response.error,
        metadata=response_metadata,
    )


def agent_response_to_department_response(
    response: AgentResponse | DepartmentResponse,
    *,
    fallback_department: Department | None = None,
) -> DepartmentResponse | None:
    """Map an A2A AgentResponse back to the legacy internal response model."""
    if isinstance(response, DepartmentResponse):
        return response
    department = response.department or fallback_department
    if department is None:
        return None
    legacy_metadata = {
        key: value
        for key, value in dict(response.metadata or {}).items()
        if key.startswith("remote_") or key in _LEGACY_METADATA_KEYS or key in _TRACE_METADATA_KEYS
    }
    return DepartmentResponse(
        department=department,
        answer=response.answer,
        sources=response.sources,
        db_data=response.db_data,
        generation_mode=response.generation_mode,
        include_contact_suggestion=response.include_contact_suggestion,
        success=response.success,
        response_time_ms=response.response_time_ms,
        error=response.error,
        metadata=legacy_metadata,
    )


def validate_agent_response(payload: dict[str, Any]) -> AgentResponse:
    """Validate a wire payload as the published AgentResponse contract."""
    return AgentResponse.model_validate(payload)


def validate_legacy_department_response(payload: dict[str, Any]) -> DepartmentResponse:
    """Validate a legacy DepartmentResponse payload."""
    return DepartmentResponse.model_validate(payload)


def build_failed_agent_response(
    *,
    department: Department,
    answer: str,
    error_code: str,
    detail: str,
    agent_id: str | None = None,
    agent_name: str | None = None,
    agent_role: str | None = None,
    capability: str | None = None,
    db_data: dict[str, Any] | None = None,
    generation_mode: str = "kural",
) -> AgentResponse:
    """Build a standard failed AgentResponse for A2A transport errors."""
    error_data = {"transport_error": detail}
    if db_data:
        error_data.update(db_data)
    return AgentResponse(
        agent_id=agent_id,
        agent_name=agent_name,
        agent_role=agent_role,
        capability=capability,
        department=department,
        answer=answer,
        sources=[],
        generation_mode=generation_mode,
        success=False,
        error=error_code,
        db_data=error_data,
        metadata={"legacy_department": department.value},
    )


__all__ = [
    "AgentResponse",
    "agent_response_to_department_response",
    "build_failed_agent_response",
    "department_response_to_agent_response",
    "validate_agent_response",
    "validate_legacy_department_response",
]
