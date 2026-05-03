"""Auth servisi testleri."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.config import settings
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

    def _factory(*, otp_generator=None, email_service=None, now_provider=None):
        return AuthService(
            session_provider=session_provider,
            now_provider=now_provider or (lambda: datetime(2026, 3, 26, 12, 0, tzinfo=timezone.utc)),
            otp_generator=otp_generator,
            email_service=email_service,
        )

    return _factory


@pytest.fixture
async def seeded_student(db_session):
    student = Student(
        student_id="20210001",
        full_name="Ahmet Yilmaz",
        email="20210001@stu.omu.edu.tr",
        department="bilgisayar_muhendisligi",
        faculty="Muhendislik Fakultesi",
        student_type="domestic",
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
    email_service = type(
        "FakeEmailService",
        (),
        {"send_otp_email": AsyncMock(return_value=None)},
    )()
    service = auth_service_factory(otp_generator=lambda _: "123456", email_service=email_service)

    result = await service.request_otp(student_number="20210001", slack_user_id="U123")

    assert result is not None
    assert result["success"] is True
    assert result["student_number"] == "20210001"
    assert result["masked_email"].endswith("@stu.omu.edu.tr")
    assert result["otp_preview_code"] is None
    email_service.send_otp_email.assert_awaited_once()


@pytest.mark.asyncio
async def test_request_otp_throttles_immediate_repeat(auth_service_factory, seeded_student):
    email_service = type(
        "FakeEmailService",
        (),
        {"send_otp_email": AsyncMock(return_value=None)},
    )()
    service = auth_service_factory(otp_generator=lambda _: "123456", email_service=email_service)

    first = await service.request_otp(student_number="20210001", slack_user_id="U123")
    second = await service.request_otp(student_number="20210001", slack_user_id="U123")

    assert first is not None
    assert first["success"] is True
    assert second is not None
    assert second["success"] is False
    assert second["reason"] == "otp_recently_requested"


@pytest.mark.asyncio
async def test_verify_otp_creates_session_and_slack_mapping(auth_service_factory, seeded_student):
    email_service = type(
        "FakeEmailService",
        (),
        {"send_otp_email": AsyncMock(return_value=None)},
    )()
    service = auth_service_factory(otp_generator=lambda _: "123456", email_service=email_service)
    await service.request_otp(student_number="20210001", slack_user_id="U123")

    result = await service.verify_otp(
        student_number="20210001",
        otp_code="123456",
        slack_user_id="U123",
    )

    assert result is not None
    assert result["success"] is True
    assert result["session_token"]
    assert result["student_department"] == "bilgisayar_muhendisligi"
    assert result["student_type"] == "domestic"

    resolved = await service.resolve_auth_context(session_token=result["session_token"])
    assert resolved is not None
    assert resolved.student_number == "20210001"
    assert resolved.student_department == "bilgisayar_muhendisligi"
    assert resolved.student_faculty == "Muhendislik Fakultesi"
    assert resolved.student_type == "domestic"

    resolved_from_slack = await service.resolve_auth_context(slack_user_id="U123")
    assert resolved_from_slack is not None
    assert resolved_from_slack.student_db_id == seeded_student.id
    assert resolved_from_slack.student_department == "bilgisayar_muhendisligi"


@pytest.mark.asyncio
async def test_verify_otp_rejects_invalid_code_and_keeps_attempt_count(auth_service_factory, seeded_student):
    email_service = type(
        "FakeEmailService",
        (),
        {"send_otp_email": AsyncMock(return_value=None)},
    )()
    service = auth_service_factory(otp_generator=lambda _: "123456", email_service=email_service)
    await service.request_otp(student_number="20210001")

    result = await service.verify_otp(student_number="20210001", otp_code="000000")

    assert result is not None
    assert result["success"] is False
    assert result["reason"] == "otp_invalid"
    assert result["remaining_attempts"] == 4


@pytest.mark.asyncio
async def test_resolve_auth_context_rejects_expired_session(auth_service_factory, seeded_student):
    email_service = type(
        "FakeEmailService",
        (),
        {"send_otp_email": AsyncMock(return_value=None)},
    )()
    service = auth_service_factory(otp_generator=lambda _: "123456", email_service=email_service)
    await service.request_otp(student_number="20210001", slack_user_id="U123")
    result = await service.verify_otp(
        student_number="20210001",
        otp_code="123456",
        slack_user_id="U123",
    )

    expired_service = auth_service_factory(
        now_provider=lambda: datetime(2026, 3, 26, 12, 0, tzinfo=timezone.utc)
        + timedelta(hours=settings.auth.session_ttl_hours + 1),
    )

    assert await expired_service.resolve_auth_context(session_token=result["session_token"]) is None
    assert await expired_service.resolve_auth_context(slack_user_id="U123") is None


@pytest.mark.asyncio
async def test_invalidate_session_marks_session_inactive(auth_service_factory, seeded_student):
    email_service = type(
        "FakeEmailService",
        (),
        {"send_otp_email": AsyncMock(return_value=None)},
    )()
    service = auth_service_factory(otp_generator=lambda _: "123456", email_service=email_service)
    await service.request_otp(student_number="20210001")
    result = await service.verify_otp(student_number="20210001", otp_code="123456")

    invalidated = await service.invalidate_session(result["session_token"])

    assert invalidated is True
    assert await service.resolve_auth_context(session_token=result["session_token"]) is None
    assert await service.resolve_auth_context(slack_user_id="U123") is None


@pytest.mark.asyncio
async def test_invalidate_slack_sessions_marks_all_user_sessions_inactive(
    auth_service_factory,
    seeded_student,
    db_session,
):
    now = datetime(2026, 3, 26, 12, 0, tzinfo=timezone.utc)
    db_session.add_all(
        [
            VerificationSession(
                student_id=seeded_student.id,
                slack_user_id="U123",
                session_token="old-session",
                expires_at=now + timedelta(hours=1),
                is_active=True,
            ),
            VerificationSession(
                student_id=seeded_student.id,
                slack_user_id="U123",
                session_token="new-session",
                expires_at=now + timedelta(hours=2),
                is_active=True,
            ),
        ]
    )
    await db_session.commit()
    service = auth_service_factory()

    invalidated = await service.invalidate_slack_sessions("U123")

    assert invalidated is True
    assert await service.resolve_auth_context(slack_user_id="U123") is None
    assert await service.resolve_auth_context(session_token="old-session") is None
    assert await service.resolve_auth_context(session_token="new-session") is None
