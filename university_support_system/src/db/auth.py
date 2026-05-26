"""OTP ve oturum yonetimi icin yardimci servisler."""

from __future__ import annotations

from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from secrets import compare_digest, randbelow, token_urlsafe
from typing import Callable

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db.connection import get_session
from src.db.auth_queries import (
    find_latest_otp,
    find_slack_mapping,
    find_student_by_number,
)
from src.db.auth_utils import ensure_aware, hash_otp, mask_email, utcnow
from src.db.auth_models import OTPCode, SlackStudentMapping, VerificationSession
from src.db.student_models import Student
from src.notifications import EmailService


@dataclass(frozen=True)
class AuthContext:
    """Cozumlenmis kimlik baglami."""

    student_db_id: int
    student_number: str
    full_name: str
    student_department: str
    student_faculty: str
    slack_user_id: str | None
    session_token: str | None
    expires_at: datetime | None
    is_authenticated: bool = True
    student_type: str | None = None


class AuthService:
    """OTP ve dogrulama oturumu yonetim servisi."""

    def __init__(
        self,
        *,
        session_provider: Callable[[], AbstractAsyncContextManager[AsyncSession]] = get_session,
        now_provider: Callable[[], datetime] = utcnow,
        otp_generator: Callable[[int], str] | None = None,
        email_service: EmailService | None = None,
    ) -> None:
        self._session_provider = session_provider
        self._now_provider = now_provider
        self._otp_generator = otp_generator or self._default_otp_generator
        self._email_service = email_service or EmailService()

    async def request_otp(
        self,
        *,
        student_number: str,
        slack_user_id: str | None = None,
    ) -> dict | None:
        """Ogrenci mevcutsa yeni bir OTP kaydi olusturur."""

        async with self._session_provider() as session:
            student = await find_student_by_number(session, student_number)
            if student is None:
                return None
            if not self._is_current_student(student):
                return {
                    "success": False,
                    "reason": "student_not_active",
                    "message": "OTP dogrulamasi yalnizca aktif ogrenciler icin kullanilabilir.",
                }
            if not self._has_allowed_student_email(student.email):
                return {
                    "success": False,
                    "reason": "invalid_student_email",
                    "message": (
                        "Dogrulama kodu gonderebilmem icin ogrenci hesabina ait "
                        f"@{settings.auth.allowed_student_email_domain} uzantili e-posta kaydi gerekli."
                    ),
                }

            latest_otp = await find_latest_otp(session, student.id)
            if self._is_otp_request_throttled(latest_otp):
                return {
                    "success": False,
                    "reason": "otp_recently_requested",
                    "message": (
                        "Yakinda bir dogrulama kodu gonderildi. "
                        "Lutfen kisa bir sure bekleyip tekrar deneyin."
                    ),
                }

            now = self._now_provider()
            expires_at = now + timedelta(minutes=settings.auth.otp_ttl_minutes)
            otp_code = self._otp_generator(settings.auth.otp_length)

            await session.execute(
                update(OTPCode)
                .where(
                    OTPCode.student_id == student.id,
                    OTPCode.used.is_(False),
                )
                .values(used=True)
            )

            otp_record = OTPCode(
                student_id=student.id,
                code_hash=hash_otp(otp_code),
                expires_at=expires_at,
                used=False,
                failed_attempts=0,
            )
            session.add(otp_record)
            await session.flush()

            await self._email_service.send_otp_email(
                to_email=student.email,
                full_name=student.full_name,
                otp_code=otp_code,
                expires_in_minutes=settings.auth.otp_ttl_minutes,
            )

            return {
                "success": True,
                "student_db_id": student.id,
                "student_number": student.student_id,
                "full_name": student.full_name,
                "student_department": student.department,
                "student_faculty": student.faculty,
                "student_type": student.student_type,
                "masked_email": mask_email(student.email),
                "delivery_channel": "email_smtp",
                "expires_at": expires_at,
                "slack_user_id": slack_user_id,
                "otp_preview_code": None,
            }

    async def verify_otp(
        self,
        *,
        student_number: str,
        otp_code: str,
        slack_user_id: str | None = None,
    ) -> dict | None:
        """OTP'yi dogrular, oturum olusturur ve gerekirse Slack eslemesini kaydeder."""

        async with self._session_provider() as session:
            student = await find_student_by_number(session, student_number)
            if student is None:
                return None

            otp_record = await find_latest_otp(session, student.id)
            if otp_record is None:
                return {
                    "success": False,
                    "reason": "otp_not_found",
                    "message": "Aktif bir OTP kaydi bulunamadi.",
                }

            now = self._now_provider()
            otp_expires_at = ensure_aware(otp_record.expires_at)
            if otp_expires_at is not None and otp_expires_at <= now:
                otp_record.used = True
                await session.flush()
                return {
                    "success": False,
                    "reason": "otp_expired",
                    "message": "OTP suresi doldu. Lutfen yeni bir kod isteyin.",
                }

            if not compare_digest(otp_record.code_hash, hash_otp(otp_code)):
                otp_record.failed_attempts += 1
                if otp_record.failed_attempts >= settings.auth.max_failed_attempts:
                    otp_record.used = True
                await session.flush()
                return {
                    "success": False,
                    "reason": "otp_invalid",
                    "message": "OTP kodu gecersiz.",
                    "remaining_attempts": max(
                        0,
                        settings.auth.max_failed_attempts - otp_record.failed_attempts,
                    ),
                }

            otp_record.used = True

            session_token = token_urlsafe(32)
            session_expires_at = now + timedelta(hours=settings.auth.session_ttl_hours)
            verification_session = VerificationSession(
                student_id=student.id,
                slack_user_id=slack_user_id or "api_user",
                session_token=session_token,
                expires_at=session_expires_at,
                is_active=True,
            )
            session.add(verification_session)

            if slack_user_id:
                mapping = await find_slack_mapping(session, slack_user_id)
                if mapping is None:
                    session.add(
                        SlackStudentMapping(
                            slack_user_id=slack_user_id,
                            student_id=student.id,
                            is_active=True,
                        )
                    )
                else:
                    mapping.student_id = student.id
                    mapping.is_active = True
                    mapping.verified_at = now

            await session.flush()

            return {
                "success": True,
                "student_db_id": student.id,
                "student_number": student.student_id,
                "full_name": student.full_name,
                "student_department": student.department,
                "student_faculty": student.faculty,
                "student_type": student.student_type,
                "session_token": session_token,
                "expires_at": session_expires_at,
                "slack_user_id": slack_user_id,
                "is_authenticated": True,
            }

    async def resolve_auth_context(
        self,
        *,
        session_token: str | None = None,
        slack_user_id: str | None = None,
    ) -> AuthContext | None:
        """Session token veya Slack eslemesi ile auth durumunu cozumler."""

        async with self._session_provider() as session:
            if session_token:
                result = await session.execute(
                    select(VerificationSession, Student)
                    .join(Student, Student.id == VerificationSession.student_id)
                    .where(
                        VerificationSession.session_token == session_token,
                        VerificationSession.is_active.is_(True),
                        VerificationSession.expires_at > self._now_provider(),
                    )
                )
                row = result.first()
                if row is None:
                    return None
                session_row, student = row
                return AuthContext(
                    student_db_id=student.id,
                    student_number=student.student_id,
                    full_name=student.full_name,
                    student_department=student.department,
                    student_faculty=student.faculty,
                    slack_user_id=session_row.slack_user_id,
                    session_token=session_row.session_token,
                    expires_at=ensure_aware(session_row.expires_at),
                    student_type=student.student_type,
                )

            if slack_user_id:
                result = await session.execute(
                    select(VerificationSession, Student)
                    .join(Student, Student.id == VerificationSession.student_id)
                    .where(
                        VerificationSession.slack_user_id == slack_user_id,
                        VerificationSession.is_active.is_(True),
                        VerificationSession.expires_at > self._now_provider(),
                    )
                    .order_by(VerificationSession.expires_at.desc())
                )
                row = result.first()
                if row is None:
                    return None
                session_row, student = row
                return AuthContext(
                    student_db_id=student.id,
                    student_number=student.student_id,
                    full_name=student.full_name,
                    student_department=student.department,
                    student_faculty=student.faculty,
                    slack_user_id=session_row.slack_user_id,
                    session_token=session_row.session_token,
                    expires_at=ensure_aware(session_row.expires_at),
                    student_type=student.student_type,
                )

        return None

    async def invalidate_session(self, session_token: str) -> bool:
        """Dogrulama oturumunu pasif hale getirir."""

        async with self._session_provider() as session:
            result = await session.execute(
                update(VerificationSession)
                .where(VerificationSession.session_token == session_token)
                .values(is_active=False)
                .returning(VerificationSession.id)
            )
            return result.scalar_one_or_none() is not None

    async def invalidate_slack_sessions(self, slack_user_id: str) -> bool:
        """Slack kullanicisinin tum aktif dogrulama oturumlarini pasif hale getirir."""

        async with self._session_provider() as session:
            result = await session.execute(
                update(VerificationSession)
                .where(
                    VerificationSession.slack_user_id == slack_user_id,
                    VerificationSession.is_active.is_(True),
                )
                .values(is_active=False)
                .returning(VerificationSession.id)
            )
            return bool(result.scalars().all())

    @staticmethod
    def _default_otp_generator(length: int) -> str:
        digits = [str(randbelow(10)) for _ in range(length)]
        return "".join(digits)

    @staticmethod
    def _is_current_student(student: Student) -> bool:
        return student.registration_status == "active"

    @staticmethod
    def _has_allowed_student_email(email: str) -> bool:
        domain = email.partition("@")[2].lower()
        allowed = settings.auth.allowed_student_email_domain.lower()
        return domain == allowed

    def _is_otp_request_throttled(self, latest_otp: OTPCode | None) -> bool:
        if latest_otp is None:
            return False
        created_at = ensure_aware(getattr(latest_otp, "created_at", None))
        if created_at is None:
            return False
        cooldown = timedelta(seconds=settings.auth.otp_request_cooldown_seconds)
        return created_at + cooldown > self._now_provider()
