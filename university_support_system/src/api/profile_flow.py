"""API katmani icin profil ve auth baglami yardimcilari."""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from src.db import AuthService, extract_profile_from_text
from src.db.schemas import AuthenticatedUserQueryRequest, UserQueryResponse

_PROFILE_PROMPT = (
    "Merhaba, hoş geldiniz. Size yardımcı olabilmem için öncelikle "
    "ad soyad, öğrenci numarası, bölüm, fakülte ve öğrenci tipi/uyruk bilgilerinizi paylaşın."
)


async def resolve_auth_inputs(
    *,
    student_id: int | None,
    student_department: str | None,
    student_faculty: str | None,
    student_type: str | None,
    full_name: str | None,
    student_number: str | None,
    is_authenticated: bool,
    session_token: str | None,
    slack_user_id: str | None,
    auth_service: AuthService,
    allow_slack_identity: bool = False,
    allow_trusted_identity_claims: bool = False,
) -> dict[str, Any]:
    """Gelen API istegi icin auth baglamini cozumler."""
    if session_token:
        resolved = await auth_service.resolve_auth_context(session_token=session_token)
        if resolved is None:
            raise HTTPException(status_code=401, detail="Gecersiz veya suresi dolmus oturum.")
        return {
            "student_id": resolved.student_db_id,
            "student_department": resolved.student_department,
            "student_faculty": resolved.student_faculty,
            "student_type": resolved.student_type,
            "full_name": resolved.full_name,
            "student_number": resolved.student_number,
            "is_authenticated": True,
            "slack_user_id": resolved.slack_user_id or slack_user_id,
            "auth_state": "verified",
            "verification_source": "session_token",
        }

    if slack_user_id and allow_slack_identity:
        resolved = await auth_service.resolve_auth_context(slack_user_id=slack_user_id)
        if resolved is not None:
            return {
                "student_id": resolved.student_db_id,
                "student_department": resolved.student_department,
                "student_faculty": resolved.student_faculty,
                "student_type": resolved.student_type,
                "full_name": resolved.full_name,
                "student_number": resolved.student_number,
                "is_authenticated": True,
                "slack_user_id": resolved.slack_user_id,
                "auth_state": "verified",
                "verification_source": "slack_mapping",
            }

    if allow_trusted_identity_claims and is_authenticated and student_id is not None:
        return {
            "student_id": student_id,
            "student_department": student_department,
            "student_faculty": student_faculty,
            "student_type": student_type,
            "full_name": full_name,
            "student_number": student_number,
            "is_authenticated": True,
            "slack_user_id": slack_user_id,
            "auth_state": "verified",
            "verification_source": "trusted_internal",
        }

    auth_state = (
        "declared"
        if any(
            value
            for value in (
                student_department,
                student_faculty,
                student_type,
                full_name,
                student_number,
            )
        )
        else "anonymous"
    )
    return {
        "student_id": None,
        "student_department": student_department,
        "student_faculty": student_faculty,
        "student_type": student_type,
        "full_name": full_name,
        "student_number": student_number,
        "is_authenticated": False,
        "slack_user_id": slack_user_id,
        "auth_state": auth_state,
        "verification_source": None,
    }


def build_profile_required_response(*, context_id: str) -> UserQueryResponse:
    """Profil bilgisi eksikse istenecek standart onboarding cevabi."""
    return UserQueryResponse(
        answer=_PROFILE_PROMPT,
        departments_involved=[],
        sources=[],
        response_time_ms=0.0,
        query_id=context_id,
    )


def build_profile_saved_response(
    *,
    context_id: str,
    full_name: str,
    department: str,
    faculty: str,
    student_type: str | None,
) -> UserQueryResponse:
    """Profil kaydedildiginde gosterilecek standart cevap."""
    first_name = (full_name.split() or [full_name])[0]
    student_type_note = f" / {student_type}" if student_type else ""
    return UserQueryResponse(
        answer=(
            f"Tesekkur ederim {first_name}. {department} / {faculty}{student_type_note} bilgilerini kaydettim. "
            "Artik sorularini bu baglami kullanarak daha dogru yanitlayabilirim."
        ),
        departments_involved=[],
        sources=[],
        response_time_ms=0.0,
        query_id=context_id,
    )


def extract_profile_payload(payload: AuthenticatedUserQueryRequest) -> dict[str, str] | None:
    """Structured alanlardan veya ham metinden profil payload'i cikarir."""
    structured = {
        "full_name": (payload.full_name or "").strip(),
        "student_number": (payload.student_number or "").strip(),
        "department": (payload.student_department or "").strip(),
        "faculty": (payload.student_faculty or "").strip(),
        "student_type": (payload.student_type or "").strip(),
    }
    if structured["full_name"] and structured["student_number"] and structured["department"] and structured["faculty"]:
        return structured

    parsed = extract_profile_from_text(payload.query)
    if parsed is None:
        return None
    return {
        "full_name": parsed["full_name"],
        "student_number": parsed["student_number"],
        "department": parsed["department"],
        "faculty": parsed["faculty"],
        "student_type": parsed.get("student_type", ""),
    }
