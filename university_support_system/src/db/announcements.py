"""Duyuru sorgulama yardimcilari."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import re

from sqlalchemy import Select, desc, or_, select

from src.core.constants import Department
from src.db.connection import get_session
from src.db.models import Announcement

_ANNOUNCEMENT_STOPWORDS = {
    "acaba",
    "ait",
    "ama",
    "ben",
    "bir",
    "biri",
    "bu",
    "da",
    "daha",
    "de",
    "duyuru",
    "duyurular",
    "duyurulari",
    "duyuruları",
    "gibi",
    "guncel",
    "güncel",
    "hangi",
    "icin",
    "için",
    "ile",
    "mi",
    "mu",
    "mı",
    "mü",
    "nasil",
    "nasıl",
    "nedir",
    "ne",
    "neler",
    "olan",
    "olarak",
    "son",
    "ve",
    "var",
}


@dataclass(frozen=True)
class AnnouncementRecord:
    """Agent katmanina donen duyuru ozet modeli."""

    id: int
    title: str
    summary: str | None
    original_text: str | None
    source_url: str | None
    faculty: str | None
    department: str | None
    published_at: datetime | None


def extract_announcement_keywords(query_text: str) -> list[str]:
    """Sorgudan duyuru aramada kullanilacak anahtar kelimeleri ayiklar."""

    tokens = re.findall(r"[a-zA-Z0-9çğıöşüÇĞİÖŞÜ]{3,}", query_text.casefold())
    seen: set[str] = set()
    keywords: list[str] = []

    for token in tokens:
        if token in _ANNOUNCEMENT_STOPWORDS:
            continue
        if token in seen:
            continue
        seen.add(token)
        keywords.append(token)

    return keywords[:6]


def _apply_department_filters(
    stmt: Select[tuple[Announcement]],
    *,
    department: Department | str | list[str] | tuple[str, ...] | None,
    faculty: str | None,
) -> Select[tuple[Announcement]]:
    department_values: list[str] = []
    if isinstance(department, Department):
        department_values = [department.value]
    elif isinstance(department, (list, tuple)):
        department_values = [str(item).strip() for item in department if str(item).strip()]
    elif department:
        department_values = [str(department).strip()]

    if department_values:
        stmt = stmt.where(
            or_(
                Announcement.department.in_(department_values),
                Announcement.department.is_(None),
            )
        )
    if faculty:
        stmt = stmt.where(
            or_(
                Announcement.faculty == faculty,
                Announcement.faculty.is_(None),
            )
        )
    return stmt


async def fetch_relevant_announcements(
    query_text: str,
    *,
    department: Department | str | list[str] | tuple[str, ...] | None = None,
    faculty: str | None = None,
    limit: int = 3,
    recent_days: int = 14,
) -> list[AnnouncementRecord]:
    """Sorgu ile ilgili aktif duyurulari getirir."""

    keywords = extract_announcement_keywords(query_text)
    recent_cutoff = datetime.now(UTC) - timedelta(days=recent_days)

    base_stmt = select(Announcement).where(Announcement.is_active.is_(True))
    base_stmt = _apply_department_filters(
        base_stmt,
        department=department,
        faculty=faculty,
    )

    async with get_session() as session:
        targeted_stmt = base_stmt.where(
            or_(
                Announcement.published_at.is_(None),
                Announcement.published_at >= recent_cutoff,
            )
        )

        if keywords:
            keyword_clauses = []
            for keyword in keywords:
                pattern = f"%{keyword}%"
                keyword_clauses.append(
                    or_(
                        Announcement.title.ilike(pattern),
                        Announcement.summary.ilike(pattern),
                        Announcement.original_text.ilike(pattern),
                    )
                )
            targeted_stmt = targeted_stmt.where(or_(*keyword_clauses))

        targeted_stmt = targeted_stmt.order_by(
            desc(Announcement.published_at),
            desc(Announcement.id),
        ).limit(limit)

        announcements = list((await session.execute(targeted_stmt)).scalars().all())

        if not announcements:
            fallback_stmt = base_stmt.order_by(
                desc(Announcement.published_at),
                desc(Announcement.id),
            ).limit(limit)
            announcements = list((await session.execute(fallback_stmt)).scalars().all())

        return [
            AnnouncementRecord(
                id=int(item.id),
                title=item.title,
                summary=item.summary,
                original_text=item.original_text,
                source_url=item.source_url,
                faculty=item.faculty,
                department=item.department,
                published_at=item.published_at,
            )
            for item in announcements
        ]
