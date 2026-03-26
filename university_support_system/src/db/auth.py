"""OTP ve oturum yonetimi icin yardimci servisler."""

from __future__ import annotations

from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from secrets import compare_digest, randbelow, token_urlsafe
from typing import Callable

from sqlalchemy import Select, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db.connection import get_session
from src.db.models import OTPCode, SlackStudentMapping, Student, VerificationSession


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    if len(local) <= 2:
        masked_local = local[:1] + "*"
    else:
        masked_local = local[:2] + "*" * max(1, len(local) - 2)
    return f"{masked_local}@{domain}" if domain else masked_local


def _hash_otp(code: str) -> str:
    return sha256(code.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class AuthContext:
    """Cozumlenmis kimlik baglami."""

    student_db_id: int
    student_number: str
    full_name: str
    slack_user_id: str | None
    session_token: str | None
    expires_at: datetime | None
    is_authenticated: bool = True


class AuthService:
    """OTP ve dogrulama oturumu yonetim servisi."""

    def __init__(
        self,
        *,
        session_provider: Callable[[], AbstractAsyncContextManager[AsyncSession]] = get_session,
        now_provider: Callable[[], datetime] = _utcnow,
        otp_generator: Callable[[int], str] | None = None,
    ) -> None:
        self._session_provider = session_provider
        self._now_provider = now_provider
        self._otp_generator = otp_generator or self._default_otp_generator

    async def request_otp(
        self,
        *,
        student_number: str,
        slack_user_id: str | None = None,
    ) -> dict | None:
        """Ogrenci mevcutsa yeni bir OTP kaydi olusturur."""

        async with self._session_provider() as session:
            student = await self._find_student_by_number(session, student_number)
            if student is None:
                return None

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
                code_hash=_hash_otp(otp_code),
                expires_at=expires_at,
                used=False,
                failed_attempts=0,
            )
            session.add(otp_record)
            await session.flush()

            return {
                "student_db_id": student.id,
                "student_number": student.student_id,
                "full_name": student.full_name,
                "masked_email": _mask_email(student.email),
                "delivery_channel": "email_stub",
                "expires_at": expires_at,
                "slack_user_id": slack_user_id,
                "otp_preview_code": otp_code if settings.server.debug else None,
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
            student = await self._find_student_by_number(session, student_number)
            if student is None:
                return None

            otp_record = await self._find_latest_otp(session, student.id)
            if otp_record is None:
                return {
                    "success": False,
                    "reason": "otp_not_found",
                    "message": "Aktif bir OTP kaydi bulunamadi.",
                }

            now = self._now_provider()
            otp_expires_at = _ensure_aware(otp_record.expires_at)
            if otp_expires_at is not None and otp_expires_at <= now:
                otp_record.used = True
                await session.flush()
                return {
                    "success": False,
                    "reason": "otp_expired",
                    "message": "OTP suresi doldu. Lutfen yeni bir kod isteyin.",
                }

            if not compare_digest(otp_record.code_hash, _hash_otp(otp_code)):
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
                mapping = await self._find_slack_mapping(session, slack_user_id)
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
                    slack_user_id=session_row.slack_user_id,
                    session_token=session_row.session_token,
                    expires_at=_ensure_aware(session_row.expires_at),
                )

            if slack_user_id:
                result = await session.execute(
                    select(SlackStudentMapping, Student)
                    .join(Student, Student.id == SlackStudentMapping.student_id)
                    .where(
                        SlackStudentMapping.slack_user_id == slack_user_id,
                        SlackStudentMapping.is_active.is_(True),
                    )
                )
                row = result.first()
                if row is None:
                    return None
                mapping, student = row
                return AuthContext(
                    student_db_id=student.id,
                    student_number=student.student_id,
                    full_name=student.full_name,
                    slack_user_id=mapping.slack_user_id,
                    session_token=None,
                    expires_at=None,
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

    @staticmethod
    def _default_otp_generator(length: int) -> str:
        digits = [str(randbelow(10)) for _ in range(length)]
        return "".join(digits)

    @staticmethod
    async def _find_student_by_number(session: AsyncSession, student_number: str) -> Student | None:
        result = await session.execute(
            select(Student).where(Student.student_id == student_number)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def _find_slack_mapping(
        session: AsyncSession,
        slack_user_id: str,
    ) -> SlackStudentMapping | None:
        result = await session.execute(
            select(SlackStudentMapping).where(
                SlackStudentMapping.slack_user_id == slack_user_id
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def _find_latest_otp(session: AsyncSession, student_db_id: int) -> OTPCode | None:
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
