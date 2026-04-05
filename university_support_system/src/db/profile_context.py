"""Sohbet baglaminda kullanici profilini yoneten servis."""

from __future__ import annotations

import re
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.auth import AuthContext
from src.db.auth_models import UserProfileContext
from src.db.auth_utils import utcnow
from src.db.connection import get_session


_FULL_NAME_PATTERN = re.compile(r"(?:ad\s*soyad|isim)\s*[:\-]\s*(?P<value>.+)", re.IGNORECASE)
_STUDENT_NUMBER_PATTERN = re.compile(
    r"(?:ogrenci\s*(?:no|numarasi|numarasi)|numara)\s*[:\-]\s*(?P<value>\d{6,20})",
    re.IGNORECASE,
)
_DEPARTMENT_PATTERN = re.compile(r"(?:bolum|bölüm|program)\s*[:\-]\s*(?P<value>.+)", re.IGNORECASE)
_FACULTY_PATTERN = re.compile(r"(?:fakulte|fakülte)\s*[:\-]\s*(?P<value>.+)", re.IGNORECASE)
_STUDENT_TYPE_PATTERN = re.compile(
    r"(?:uyruk|ogrenci\s*(?:turu|tipi)|student\s*type)\s*[:\-]\s*(?P<value>.+)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ProfileContextData:
    """Sohbet icin kayitli profil baglami."""

    context_id: str
    user_id: str | None
    full_name: str
    student_number: str | None
    department: str
    faculty: str
    student_type: str | None
    student_db_id: int | None
    is_verified: bool
    last_seen_at: datetime

    @property
    def first_name(self) -> str:
        return (self.full_name.split() or [self.full_name])[0]


def extract_profile_from_text(text: str) -> dict[str, str] | None:
    """Etiketli kullanici mesajindan profil bilgilerini ayiklar."""

    if not text.strip():
        return None

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return None

    values: dict[str, str] = {}
    for line in lines:
        full_name = _FULL_NAME_PATTERN.search(line)
        if full_name:
            values["full_name"] = full_name.group("value").strip()
            continue

        student_number = _STUDENT_NUMBER_PATTERN.search(line)
        if student_number:
            values["student_number"] = student_number.group("value").strip()
            continue

        department = _DEPARTMENT_PATTERN.search(line)
        if department:
            values["department"] = department.group("value").strip()
            continue

        faculty = _FACULTY_PATTERN.search(line)
        if faculty:
            values["faculty"] = faculty.group("value").strip()
            continue

        student_type = _STUDENT_TYPE_PATTERN.search(line)
        if student_type:
            values["student_type"] = student_type.group("value").strip()

    required = {"full_name", "student_number", "department", "faculty"}
    if required.issubset(values):
        return values
    return None


def looks_like_profile_submission(text: str) -> bool:
    """Mesaj agirlikli olarak profil girisi mi anlamaya calisir."""

    parsed = extract_profile_from_text(text)
    if parsed is None:
        return False
    lowered = text.casefold()
    return "?" not in text and "nasil" not in lowered and "nedir" not in lowered


class ProfileContextService:
    """Profil baglamini kaydeder ve gerekirse auth bilgisiyle gunceller."""

    def __init__(
        self,
        *,
        session_provider: Callable[[], AbstractAsyncContextManager[AsyncSession]] = get_session,
        now_provider: Callable[[], datetime] = utcnow,
    ) -> None:
        self._session_provider = session_provider
        self._now_provider = now_provider

    async def get_context(self, *, context_id: str) -> ProfileContextData | None:
        async with self._session_provider() as session:
            result = await session.execute(
                select(UserProfileContext).where(UserProfileContext.context_id == context_id)
            )
            row = result.scalar_one_or_none()
            if row is None:
                return None
            row.last_seen_at = self._now_provider()
            await session.flush()
            return self._to_data(row)

    async def upsert_profile(
        self,
        *,
        context_id: str,
        user_id: str | None,
        full_name: str,
        student_number: str | None,
        department: str,
        faculty: str,
        student_type: str | None = None,
        is_verified: bool = False,
        student_db_id: int | None = None,
    ) -> ProfileContextData:
        async with self._session_provider() as session:
            result = await session.execute(
                select(UserProfileContext).where(UserProfileContext.context_id == context_id)
            )
            row = result.scalar_one_or_none()
            if row is None:
                row = UserProfileContext(
                    context_id=context_id,
                    user_id=user_id,
                    full_name=full_name,
                    student_number=student_number,
                    department=department,
                    faculty=faculty,
                    student_type=student_type,
                    student_db_id=student_db_id,
                    is_verified=is_verified,
                    last_seen_at=self._now_provider(),
                )
                session.add(row)
            else:
                row.user_id = user_id or row.user_id
                row.full_name = full_name
                row.student_number = student_number or row.student_number
                row.department = department
                row.faculty = faculty
                row.student_type = student_type or row.student_type
                row.student_db_id = student_db_id or row.student_db_id
                row.is_verified = row.is_verified or is_verified
                row.last_seen_at = self._now_provider()

            await session.flush()
            return self._to_data(row)

    async def sync_from_auth_context(
        self,
        *,
        context_id: str,
        user_id: str | None,
        auth_context: AuthContext,
        faculty: str | None = None,
    ) -> ProfileContextData:
        return await self.upsert_profile(
            context_id=context_id,
            user_id=user_id,
            full_name=auth_context.full_name,
            student_number=auth_context.student_number,
            department=auth_context.student_department,
            faculty=faculty or auth_context.student_faculty,
            student_type=None,
            is_verified=True,
            student_db_id=auth_context.student_db_id,
        )

    @staticmethod
    def _to_data(row: UserProfileContext) -> ProfileContextData:
        return ProfileContextData(
            context_id=row.context_id,
            user_id=row.user_id,
            full_name=row.full_name,
            student_number=row.student_number,
            department=row.department,
            faculty=row.faculty,
            student_type=row.student_type,
            student_db_id=row.student_db_id,
            is_verified=row.is_verified,
            last_seen_at=row.last_seen_at,
        )
