"""Etkinlik sorgulama yardimcilari."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
import re

from sqlalchemy import Select, and_, case, or_, select

from src.core.constants import Department
from src.core.text_normalization import iter_alias_matches_longest_first, normalize_text
from src.db.connection import get_session
from src.db.support_models import Event, EventLink

_EVENT_STOPWORDS = {
    "acaba",
    "ait",
    "ama",
    "ben",
    "bir",
    "bu",
    "da",
    "daha",
    "de",
    "etkinlik",
    "etkinlikler",
    "gibi",
    "hangi",
    "icin",
    "ile",
    "mi",
    "mu",
    "nedir",
    "ne",
    "neler",
    "olan",
    "olarak",
    "son",
    "ve",
    "var",
}
_EVENT_UNIT_ALIASES: dict[str, tuple[str, ...]] = {
    "Bilgisayar Muhendisligi": (
        "bilgisayar muhendisligi",
        "bilgisayar muhendisligi bolumu",
        "bil muh",
        "bilgisayar muh",
    ),
    "Matematik ve Fen Bilimleri Egitimi": (
        "matematik ve fen bilimleri egitimi",
        "matematik fen bilimleri egitimi",
        "mfbeb",
    ),
    "Guzel Sanatlar Egitimi": (
        "guzel sanatlar egitimi",
        "guzel sanatlar egitimi bolumu",
        "guzel sanatlar",
    ),
    "Elektrik Elektronik Muhendisligi": (
        "elektrik elektronik muhendisligi",
        "elektrik elektronik muhendisligi bolumu",
        "elektrik elktronik muhendisligi",
        "elektrik-elektronik muhendisligi",
        "elektrik elektronik",
        "elektrik elktronik",
        "eem",
        "eem bolumu",
        "eem muhendisligi",
        "ee muh",
    ),
    "Fizik": (
        "fizik bolumu",
        "fizik",
    ),
    "Istatistik": (
        "istatistik bolumu",
        "istatistik",
        "istat",
    ),
}
_EVENT_UNIT_FACULTY: dict[str, str] = {
    "Bilgisayar Muhendisligi": "Muhendislik Fakultesi",
    "Matematik ve Fen Bilimleri Egitimi": "Egitim Fakultesi",
    "Guzel Sanatlar Egitimi": "Egitim Fakultesi",
    "Elektrik Elektronik Muhendisligi": "Muhendislik Fakultesi",
    "Fizik": "Fen Edebiyat Fakultesi",
    "Istatistik": "Fen Edebiyat Fakultesi",
}
_EVENT_FACULTY_ALIASES: dict[str, tuple[str, ...]] = {
    "Muhendislik Fakultesi": (
        "muhendislik fakultesi",
        "muhendislik fakultesindeki",
        "muhendislikteki",
    ),
    "Fen Fakultesi": (
        "fen fakultesi",
        "fen fakultesindeki",
        "fendeki",
    ),
    "Egitim Fakultesi": (
        "egitim fakultesi",
        "egitim fakultesindeki",
        "egitimdeki",
    ),
    "Fen Edebiyat Fakultesi": (
        "fen edebiyat fakultesi",
        "fen edebiyattaki",
        "fen edebiyatteki",
        "fen edebiyatta",
    ),
}


@dataclass(frozen=True)
class EventLinkRecord:
    """Small view model for stored event child links."""

    label: str
    url: str
    link_type: str


@dataclass(frozen=True)
class EventRecord:
    """Agent katmanina donen etkinlik ozet modeli."""

    id: int
    title: str
    display_summary: str | None
    summary: str | None
    original_text: str | None
    source_url: str | None
    faculty: str | None
    unit_name: str | None
    department: str | None
    event_type: str | None
    location: str | None
    organizer: str | None
    starts_at: datetime | None
    ends_at: datetime | None
    all_day: bool
    links: tuple[EventLinkRecord, ...] = field(default_factory=tuple)


def extract_event_keywords(query_text: str) -> list[str]:
    """Sorgudan etkinlik aramada kullanilacak anahtar kelimeleri ayiklar."""

    tokens = re.findall(r"[a-zA-Z0-9çğıöşüÇĞİÖŞÜ]{3,}", query_text.casefold())
    seen: set[str] = set()
    keywords: list[str] = []

    for token in tokens:
        if token in _EVENT_STOPWORDS:
            continue
        if token in seen:
            continue
        seen.add(token)
        keywords.append(token)

    return keywords[:6]


def _detect_unit_scope(query_text: str) -> str | None:
    normalized_query = normalize_text(query_text)
    for unit_name, alias in iter_alias_matches_longest_first(_EVENT_UNIT_ALIASES.items()):
        if alias in normalized_query:
            return unit_name
    return None


def _detect_faculty_scope(query_text: str) -> str | None:
    normalized_query = normalize_text(query_text)
    for faculty_name, alias in iter_alias_matches_longest_first(_EVENT_FACULTY_ALIASES.items()):
        if alias in normalized_query:
            return faculty_name
    return None


def _apply_department_filters(
    stmt: Select[tuple[Event]],
    *,
    department: Department | str | list[str] | tuple[str, ...] | None,
    faculty: str | None,
    include_general_faculty: bool = True,
    unit_name: str | None = None,
    include_general_unit: bool = True,
) -> Select[tuple[Event]]:
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
                Event.department.in_(department_values),
                Event.department.is_(None),
            )
        )
    if faculty:
        if include_general_faculty:
            stmt = stmt.where(
                or_(
                    Event.faculty == faculty,
                    Event.faculty.is_(None),
                )
            )
        else:
            stmt = stmt.where(Event.faculty == faculty)
    if unit_name:
        if include_general_unit:
            stmt = stmt.where(
                or_(
                    Event.unit_name == unit_name,
                    Event.unit_name.is_(None),
                )
            )
        else:
            stmt = stmt.where(Event.unit_name == unit_name)
    return stmt


def _apply_keyword_filters(
    stmt: Select[tuple[Event]],
    *,
    keywords: list[str],
) -> Select[tuple[Event]]:
    if not keywords:
        return stmt

    keyword_clauses = []
    for keyword in keywords:
        pattern = f"%{keyword}%"
        keyword_clauses.append(
            or_(
                Event.title.ilike(pattern),
                Event.summary.ilike(pattern),
                Event.original_text.ilike(pattern),
                Event.location.ilike(pattern),
                Event.organizer.ilike(pattern),
                Event.event_type.ilike(pattern),
            )
        )
    return stmt.where(or_(*keyword_clauses))


def _should_apply_keyword_filter(
    query_text: str,
    *,
    faculty: str | None,
    unit_name: str | None,
    keywords: list[str],
) -> bool:
    if not keywords:
        return False
    normalized_query = normalize_text(query_text)
    if (faculty or unit_name) and "etkinlik" in normalized_query:
        return False
    return True


def _event_keyword_match_score(
    event: Event,
    *,
    keywords: list[str],
    query_text: str,
) -> int:
    if not keywords:
        return 0

    title = normalize_text(event.title or "")
    summary = normalize_text(event.summary or "")
    original = normalize_text(event.original_text or "")
    location = normalize_text(event.location or "")
    organizer = normalize_text(event.organizer or "")
    event_type = normalize_text(event.event_type or "")
    query = normalize_text(query_text)

    score = 0
    for keyword in keywords:
        normalized_keyword = normalize_text(keyword)
        if normalized_keyword in title:
            score += 5
        elif normalized_keyword in event_type:
            score += 4
        elif normalized_keyword in location:
            score += 3
        elif normalized_keyword in organizer:
            score += 3
        elif normalized_keyword in summary:
            score += 2
        elif normalized_keyword in original:
            score += 1

    if event.unit_name and normalize_text(event.unit_name) in query:
        score += 2
    if event.faculty and normalize_text(event.faculty) in query:
        score += 1
    return score


def _to_event_record(event: Event, links: list[EventLink]) -> EventRecord:
    ordered_links = sorted(links, key=lambda item: (item.sort_order, item.id))
    return EventRecord(
        id=int(event.id),
        title=event.title,
        display_summary=event.display_summary,
        summary=event.summary,
        original_text=event.original_text,
        source_url=event.source_url,
        faculty=event.faculty,
        unit_name=event.unit_name,
        department=event.department,
        event_type=event.event_type,
        location=event.location,
        organizer=event.organizer,
        starts_at=event.starts_at,
        ends_at=event.ends_at,
        all_day=bool(event.all_day),
        links=tuple(
            EventLinkRecord(
                label=link.label,
                url=link.url,
                link_type=link.link_type,
            )
            for link in ordered_links
        ),
    )


def _resolve_time_window(
    query_text: str,
    *,
    now: datetime,
) -> tuple[datetime, datetime] | None:
    normalized_query = normalize_text(query_text)

    if "bugun" in normalized_query:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return start, start + timedelta(days=1)
    if "yarin" in normalized_query:
        start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return start, start + timedelta(days=1)
    if "bu hafta" in normalized_query or "haftaya" in normalized_query:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return start, start + timedelta(days=7)
    if "bu ay" in normalized_query or "yaklasan" in normalized_query or "yakinda" in normalized_query:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return start, start + timedelta(days=30)
    return None


async def fetch_relevant_events(
    query_text: str,
    *,
    department: Department | str | list[str] | tuple[str, ...] | None = None,
    faculty: str | None = None,
    unit_name: str | None = None,
    limit: int = 5,
    now: datetime | None = None,
    include_past_days: int = 30,
) -> list[EventRecord]:
    """Etkinlik sorulari icin aktif event kayitlarini getir."""

    now = now or datetime.now(UTC)
    detected_unit_name = _detect_unit_scope(query_text)
    detected_faculty = _detect_faculty_scope(query_text)
    inferred_faculty = _EVENT_UNIT_FACULTY.get(detected_unit_name or "")
    effective_unit_name = detected_unit_name or unit_name
    effective_faculty = detected_faculty or inferred_faculty or faculty
    keywords = extract_event_keywords(query_text)
    time_window = _resolve_time_window(query_text, now=now)
    default_window_start = now - timedelta(days=include_past_days)
    default_window_end = now + timedelta(days=120)
    apply_keyword_filter = _should_apply_keyword_filter(
        query_text,
        faculty=effective_faculty,
        unit_name=effective_unit_name,
        keywords=keywords,
    )

    async with get_session() as session:
        stmt = select(Event).where(Event.is_active.is_(True))
        stmt = _apply_department_filters(
            stmt,
            department=department,
            faculty=effective_faculty,
            unit_name=effective_unit_name,
        )
        if time_window is not None:
            window_start, window_end = time_window
            stmt = stmt.where(
                Event.starts_at.is_not(None),
                Event.starts_at >= window_start,
                Event.starts_at < window_end,
            )
        else:
            stmt = stmt.where(
                Event.starts_at.is_not(None),
                Event.starts_at >= default_window_start,
                Event.starts_at < default_window_end,
            )
        if apply_keyword_filter:
            stmt = _apply_keyword_filters(stmt, keywords=keywords)
        stmt = stmt.order_by(
            case((and_(Event.starts_at.is_not(None), Event.starts_at >= now), 0), else_=1),
            Event.starts_at.asc().nulls_last(),
            Event.id.desc(),
        ).limit(max(limit * 10, 20))

        rows = list((await session.execute(stmt)).scalars().all())
        if apply_keyword_filter:
            rows = [
                item
                for item in rows
                if _event_keyword_match_score(item, keywords=keywords, query_text=query_text) > 0
            ]
            rows.sort(
                key=lambda item: (
                    0 if item.starts_at is not None and item.starts_at >= now else 1,
                    -_event_keyword_match_score(item, keywords=keywords, query_text=query_text),
                    item.starts_at or datetime.max.replace(tzinfo=UTC),
                    int(item.id),
                )
            )
        rows = rows[:limit]
        if not rows:
            return []

        event_ids = [int(row.id) for row in rows]
        link_rows = list(
            (
                await session.execute(
                    select(EventLink).where(EventLink.event_id.in_(event_ids))
                )
            )
            .scalars()
            .all()
        )
        links_by_event_id: dict[int, list[EventLink]] = {}
        for link in link_rows:
            links_by_event_id.setdefault(int(link.event_id), []).append(link)

        return [
            _to_event_record(row, links_by_event_id.get(int(row.id), []))
            for row in rows
        ]
