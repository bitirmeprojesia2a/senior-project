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
            full_name=resolved["full_name"] or payload.full_name or "Ogrenci",
            student_number=resolved["student_number"],
            department=resolved["student_department"] or payload.student_department or "",
            faculty=resolved["student_faculty"] or payload.student_faculty or "",
            student_type=None,
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
    )
    return payload.context_id or "api-a2a-context", resolved


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
    }
