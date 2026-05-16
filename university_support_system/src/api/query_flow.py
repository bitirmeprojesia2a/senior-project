"""Request context helpers for query and internal A2A endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from src.api.profile_flow import (
    build_profile_required_response,
    build_profile_saved_response,
    extract_profile_payload,
    resolve_auth_inputs,
)
from src.db import AuthService, ProfileContextService, looks_like_profile_submission
from src.db.schemas import (
    AuthenticatedUserQueryRequest,
    UserQueryResponse,
)


@dataclass(frozen=True)
class QueryContextResolution:
    """Resolved user/profile context for query handling."""

    context_id: str
    resolved: dict
    immediate_response: UserQueryResponse | None = None


async def resolve_query_context(
    *,
    payload: AuthenticatedUserQueryRequest,
    auth_service: AuthService,
    profile_service: ProfileContextService,
) -> QueryContextResolution:
    """Resolve auth and profile context for the public query endpoint."""
    context_id = payload.context_id or str(uuid4())
    resolved = await resolve_auth_inputs(
        student_id=payload.student_id,
        student_department=payload.student_department,
        student_faculty=payload.student_faculty,
        student_type=payload.student_type,
        full_name=payload.full_name,
        student_number=payload.student_number,
        is_authenticated=payload.is_authenticated,
        session_token=payload.session_token,
        slack_user_id=payload.slack_user_id,
        auth_service=auth_service,
        allow_slack_identity=False,
    )

    profile = await profile_service.get_context(context_id=context_id)
    if resolved["is_authenticated"]:
        profile = await profile_service.upsert_profile(
            context_id=context_id,
            user_id=payload.user_id or resolved["slack_user_id"],
            full_name=resolved["full_name"] or payload.full_name or "Öğrenci",
            student_number=resolved["student_number"],
            department=resolved["student_department"] or payload.student_department or "",
            faculty=resolved["student_faculty"] or payload.student_faculty or "",
            student_type=resolved["student_type"],
            is_verified=True,
            student_db_id=resolved["student_id"],
        )
    elif profile is None:
        profile_payload = extract_profile_payload(payload)
        if profile_payload is None:
            return QueryContextResolution(
                context_id=context_id,
                resolved=resolved,
                immediate_response=build_profile_required_response(context_id=context_id),
            )

        profile = await profile_service.upsert_profile(
            context_id=context_id,
            user_id=payload.user_id,
            full_name=profile_payload["full_name"],
            student_number=profile_payload["student_number"],
            department=profile_payload["department"],
            faculty=profile_payload["faculty"],
            student_type=profile_payload.get("student_type") or None,
            is_verified=False,
            student_db_id=None,
        )
        if looks_like_profile_submission(payload.query):
            return QueryContextResolution(
                context_id=context_id,
                resolved=resolved,
                immediate_response=build_profile_saved_response(
                    context_id=context_id,
                    full_name=profile.full_name,
                    department=profile.department,
                    faculty=profile.faculty,
                    student_type=profile.student_type,
                ),
            )

    if profile is not None:
        resolved["full_name"] = resolved["full_name"] or profile.full_name
        resolved["student_number"] = resolved["student_number"] or profile.student_number
        resolved["student_department"] = resolved["student_department"] or profile.department
        resolved["student_faculty"] = resolved["student_faculty"] or profile.faculty
        resolved["student_type"] = resolved["student_type"] or profile.student_type

    return QueryContextResolution(context_id=context_id, resolved=resolved)


async def resolve_dispatch_context(
    *,
    payload: Any,
    auth_service: AuthService,
) -> tuple[str, dict]:
    """Resolve auth context for the internal A2A dispatch endpoint."""
    resolved = await resolve_auth_inputs(
        student_id=payload.student_id,
        student_department=payload.student_department,
        student_faculty=payload.student_faculty,
        student_type=payload.student_type,
        full_name=payload.full_name,
        student_number=payload.student_number,
        is_authenticated=payload.is_authenticated,
        session_token=payload.session_token,
        slack_user_id=payload.slack_user_id,
        auth_service=auth_service,
        allow_slack_identity=True,
        allow_trusted_identity_claims=True,
    )
    return payload.context_id or str(uuid4()), resolved


def build_dispatch_metadata(
    *,
    payload: Any,
    resolved: dict,
) -> dict:
    """Build normalized metadata for internal department dispatch."""
    return {
        "user_id": payload.user_id or resolved["slack_user_id"],
        "student_id": resolved["student_id"],
        "student_number": resolved["student_number"],
        "student_full_name": resolved["full_name"],
        "student_department": resolved["student_department"],
        "student_faculty": resolved["student_faculty"],
        "student_type": resolved["student_type"],
        "llm_profile": payload.llm_profile,
        "is_authenticated": resolved["is_authenticated"],
        "routing_reason": "api_a2a_dispatch",
        "original_query": payload.original_query,
        "resolved_query": payload.resolved_query,
        "conversation_is_follow_up": payload.conversation_is_follow_up,
        "conversation_topic": payload.conversation_topic,
        "conversation_source_refs": list(payload.conversation_source_refs or []),
        "force_llm_synthesis": payload.force_llm_synthesis,
        "query_complexity": payload.query_complexity,
        "is_personal_query": payload.is_personal_query,
        "final_answer_owner": payload.final_answer_owner,
        "specialist_response_mode": payload.specialist_response_mode,
        "capability_planner": getattr(payload, "capability_planner", None),
        "source_owner": getattr(payload, "source_owner", None),
        "policy_facet": getattr(payload, "policy_facet", None),
        "decision_contract": getattr(payload, "decision_contract", None),
        "resolved_decision": getattr(payload, "resolved_decision", None),
        "runtime_authority": getattr(payload, "runtime_authority", None),
        "branch_dispatch_gate": getattr(payload, "branch_dispatch_gate", None),
        "branch_role": getattr(payload, "branch_role", None),
        "retrieval_execution_policy": getattr(payload, "retrieval_execution_policy", None),
        "disable_specialist_llm": payload.disable_specialist_llm,
        "trace_id": payload.trace_id,
        "span_id": payload.span_id,
        "parent_span_id": payload.parent_span_id,
    }
