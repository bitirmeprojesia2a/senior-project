"""Auth servisi testleri."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.db.auth import AuthService
from src.db.models import OTPCode, SlackStudentMapping, Student, VerificationSession


@pytest.fixture
def auth_service_factory(db_engine):
    session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    @asynccontextmanager
    async def session_provider():
        async with session_factory() as session:
            yield session
            await session.commit()

    def _factory(*, otp_generator=None):
        return AuthService(
            session_provider=session_provider,
            now_provider=lambda: datetime(2026, 3, 26, 12, 0, tzinfo=timezone.utc),
            otp_generator=otp_generator,
        )

    return _factory


@pytest.fixture
async def seeded_student(db_session):
    student = Student(
        student_id="20210001",
        full_name="Ahmet Yilmaz",
        email="ahmet.yilmaz@uni.edu.tr",
        department="bilgisayar_muhendisligi",
        faculty="Muhendislik Fakultesi",
        class_year=3,
        enrollment_year=2021,
        registration_status="active",
        gpa=3.25,
        total_credits=240,
        completed_credits=180,
        current_semester="2025-2026-bahar",
    )
    db_session.add(student)
    await db_session.commit()
    await db_session.refresh(student)
    return student


@pytest.mark.asyncio
async def test_request_otp_creates_record_and_returns_preview(auth_service_factory, seeded_student):
    service = auth_service_factory(otp_generator=lambda _: "123456")

    result = await service.request_otp(student_number="20210001", slack_user_id="U123")

    assert result is not None
    assert result["student_number"] == "20210001"
    assert result["masked_email"].startswith("ah")
    assert result["otp_preview_code"] == "123456"


@pytest.mark.asyncio
async def test_verify_otp_creates_session_and_slack_mapping(auth_service_factory, seeded_student):
    service = auth_service_factory(otp_generator=lambda _: "123456")
    await service.request_otp(student_number="20210001", slack_user_id="U123")

    result = await service.verify_otp(
        student_number="20210001",
        otp_code="123456",
        slack_user_id="U123",
    )

    assert result is not None
    assert result["success"] is True
    assert result["session_token"]

    resolved = await service.resolve_auth_context(session_token=result["session_token"])
    assert resolved is not None
    assert resolved.student_number == "20210001"

    resolved_from_slack = await service.resolve_auth_context(slack_user_id="U123")
    assert resolved_from_slack is not None
    assert resolved_from_slack.student_db_id == seeded_student.id


@pytest.mark.asyncio
async def test_verify_otp_rejects_invalid_code_and_keeps_attempt_count(auth_service_factory, seeded_student):
    service = auth_service_factory(otp_generator=lambda _: "123456")
    await service.request_otp(student_number="20210001")

    result = await service.verify_otp(student_number="20210001", otp_code="000000")

    assert result is not None
    assert result["success"] is False
    assert result["reason"] == "otp_invalid"
    assert result["remaining_attempts"] == 4


@pytest.mark.asyncio
async def test_invalidate_session_marks_session_inactive(auth_service_factory, seeded_student):
    service = auth_service_factory(otp_generator=lambda _: "123456")
    await service.request_otp(student_number="20210001")
    result = await service.verify_otp(student_number="20210001", otp_code="123456")

    invalidated = await service.invalidate_session(result["session_token"])

    assert invalidated is True
    assert await service.resolve_auth_context(session_token=result["session_token"]) is None
