"""Query helpers for auth-related database lookups."""

from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.auth_models import OTPCode, SlackStudentMapping
from src.db.student_models import Student


async def find_student_by_number(session: AsyncSession, student_number: str) -> Student | None:
    result = await session.execute(
        select(Student).where(Student.student_id == student_number)
    )
    return result.scalar_one_or_none()


async def find_slack_mapping(
    session: AsyncSession,
    slack_user_id: str,
) -> SlackStudentMapping | None:
    result = await session.execute(
        select(SlackStudentMapping).where(
            SlackStudentMapping.slack_user_id == slack_user_id
        )
    )
    return result.scalar_one_or_none()


async def find_latest_otp(session: AsyncSession, student_db_id: int) -> OTPCode | None:
    query: Select[tuple[OTPCode]] = (
        select(OTPCode)
        .where(
            OTPCode.student_id == student_db_id,
            OTPCode.used.is_(False),
        )
        .order_by(OTPCode.id.desc())
        .limit(1)
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()
