"""Event source registry and synchronization persistence helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
import hashlib
from typing import Any

from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.text_normalization import collapse_whitespace, normalize_text
from src.db.connection import get_session
from src.db.support_models import Event, EventLink, EventSource, EventSyncRun

_DEACTIVATION_GRACE_HOURS = 48


@dataclass(frozen=True)
class EventSourceRecord:
    """Serializable view of a configured event source."""

    id: int
    name: str
    source_type: str
    parser_key: str
    base_url: str | None
    list_url: str
    faculty: str | None
    unit_name: str | None
    department: str | None
    fetch_interval_minutes: int
    max_items_per_run: int
    parser_options: dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    last_success_at: datetime | None = None
    last_error: str | None = None


@dataclass(frozen=True)
class EventLinkCandidate:
    """Link metadata extracted from an event detail page."""

    label: str
    url: str
    link_type: str = "related"
    sort_order: int = 0


@dataclass(frozen=True)
class EventCandidate:
    """Normalized event payload ready to persist."""

    title: str
    source_url: str | None
    original_text: str | None
    summary: str | None = None
    display_summary: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    location: str | None = None
    organizer: str | None = None
    event_type: str | None = None
    all_day: bool = False
    faculty: str | None = None
    unit_name: str | None = None
    department: str | None = None
    links: tuple[EventLinkCandidate, ...] = ()


@dataclass(frozen=True)
class EventSyncStats:
    """Counts collected during an event sync run."""

    items_found: int = 0
    items_inserted: int = 0
    items_updated: int = 0
    items_deactivated: int = 0


def build_event_content_hash(
    *,
    title: str,
    source_url: str | None,
    original_text: str | None,
    starts_at: datetime | None,
    location: str | None,
) -> str:
    """Build a stable content hash for duplicate detection."""

    payload = "||".join(
        [
            normalize_text(collapse_whitespace(title)),
            normalize_text(source_url or ""),
            normalize_text(collapse_whitespace(original_text or "")),
            starts_at.isoformat() if starts_at else "",
            normalize_text(collapse_whitespace(location or "")),
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def summarize_event_text(
    *,
    title: str,
    original_text: str | None,
    location: str | None = None,
    max_chars: int = 280,
) -> str:
    """Produce a lightweight event summary without requiring LLM synthesis."""

    text = collapse_whitespace(original_text)
    if location:
        text = collapse_whitespace(f"{text} Konum: {location}".strip())
    if not text:
        return collapse_whitespace(title)
    if len(text) <= max_chars:
        return text
    return f"{text[: max_chars - 3].rstrip()}..."


def _source_to_record(source: EventSource) -> EventSourceRecord:
    return EventSourceRecord(
        id=int(source.id),
        name=source.name,
        source_type=source.source_type,
        parser_key=source.parser_key,
        base_url=source.base_url,
        list_url=source.list_url,
        faculty=source.faculty,
        unit_name=source.unit_name,
        department=source.department,
        fetch_interval_minutes=int(source.fetch_interval_minutes),
        max_items_per_run=int(source.max_items_per_run),
        parser_options=dict(source.parser_options or {}),
        is_active=bool(source.is_active),
        last_success_at=source.last_success_at,
        last_error=source.last_error,
    )


async def fetch_active_event_sources(
    *,
    source_id: int | None = None,
) -> list[EventSourceRecord]:
    """Return active event sources from the registry."""

    async with get_session() as session:
        query = select(EventSource).where(EventSource.is_active.is_(True))
        if source_id is not None:
            query = query.where(EventSource.id == source_id)
        query = query.order_by(EventSource.id.asc())
        rows = list((await session.execute(query)).scalars().all())
        return [_source_to_record(row) for row in rows]


async def get_or_create_event_source(
    session: AsyncSession,
    *,
    name: str,
    list_url: str,
    source_type: str = "html_list",
    parser_key: str = "generic_html",
    base_url: str | None = None,
    faculty: str | None = None,
    unit_name: str | None = None,
    department: str | None = None,
    fetch_interval_minutes: int = 360,
    max_items_per_run: int = 20,
    parser_options: dict[str, Any] | None = None,
    is_active: bool = True,
) -> EventSourceRecord:
    """Create or update an event source definition keyed by list_url."""

    result = await session.execute(
        select(EventSource).where(EventSource.list_url == list_url)
    )
    source = result.scalar_one_or_none()
    if source is None:
        source = EventSource(
            name=name,
            list_url=list_url,
            source_type=source_type,
            parser_key=parser_key,
            base_url=base_url,
            faculty=faculty,
            unit_name=unit_name,
            department=department,
            fetch_interval_minutes=fetch_interval_minutes,
            max_items_per_run=max_items_per_run,
            parser_options=parser_options,
            is_active=is_active,
        )
        session.add(source)
        await session.flush()
        return _source_to_record(source)

    source.name = name
    source.source_type = source_type
    source.parser_key = parser_key
    source.base_url = base_url
    source.faculty = faculty
    source.unit_name = unit_name
    source.department = department
    source.fetch_interval_minutes = fetch_interval_minutes
    source.max_items_per_run = max_items_per_run
    source.parser_options = parser_options
    source.is_active = is_active
    await session.flush()
    return _source_to_record(source)


async def create_event_sync_run(
    session: AsyncSession,
    *,
    source_id: int,
    started_at: datetime | None = None,
) -> EventSyncRun:
    """Create an event sync run record before fetch/parse begins."""

    run = EventSyncRun(
        source_id=source_id,
        started_at=started_at or datetime.now(UTC),
        status="started",
    )
    session.add(run)
    await session.flush()
    return run


async def finalize_event_sync_run(
    session: AsyncSession,
    *,
    run: EventSyncRun,
    status: str,
    stats: EventSyncStats,
    error_message: str | None = None,
    finished_at: datetime | None = None,
) -> None:
    """Persist final event sync counters and status."""

    run.status = status
    run.items_found = stats.items_found
    run.items_inserted = stats.items_inserted
    run.items_updated = stats.items_updated
    run.items_deactivated = stats.items_deactivated
    run.error_message = error_message
    run.finished_at = finished_at or datetime.now(UTC)
    await session.flush()


async def mark_event_source_sync_result(
    session: AsyncSession,
    *,
    source_id: int,
    success: bool,
    finished_at: datetime | None = None,
    error_message: str | None = None,
) -> None:
    """Store the last success/error state on an event source record."""

    source = await session.get(EventSource, source_id)
    if source is None:
        return
    if success:
        source.last_success_at = finished_at or datetime.now(UTC)
        source.last_error = None
    else:
        source.last_error = error_message
    await session.flush()


async def upsert_events_for_source(
    session: AsyncSession,
    *,
    source: EventSourceRecord,
    candidates: list[EventCandidate],
    seen_at: datetime | None = None,
    dry_run: bool = False,
    allow_deactivation: bool = True,
) -> EventSyncStats:
    """Insert/update normalized event candidates for a single source."""

    seen_at = seen_at or datetime.now(UTC)
    stats = EventSyncStats(items_found=len(candidates))
    if not candidates:
        return stats

    urls = [candidate.source_url for candidate in candidates if candidate.source_url]
    query = select(Event)
    if urls:
        query = query.where(
            or_(
                Event.source_id == source.id,
                Event.source_url.in_(urls),
            )
        )
    else:
        query = query.where(Event.source_id == source.id)

    existing_rows = list((await session.execute(query)).scalars().all())
    existing_by_url = {
        row.source_url: row
        for row in existing_rows
        if row.source_url
    }
    existing_by_hash = {
        row.content_hash: row
        for row in existing_rows
        if row.content_hash
    }
    seen_row_ids: set[int] = set()
    inserted = 0
    updated = 0

    for index, candidate in enumerate(candidates):
        candidate_seen_at = seen_at - timedelta(seconds=index)
        title = collapse_whitespace(candidate.title)
        original_text = collapse_whitespace(candidate.original_text)
        summary = collapse_whitespace(candidate.summary) or summarize_event_text(
            title=title,
            original_text=original_text,
            location=candidate.location,
        )
        content_hash = build_event_content_hash(
            title=title,
            source_url=candidate.source_url,
            original_text=original_text,
            starts_at=candidate.starts_at,
            location=candidate.location,
        )

        row = None
        if candidate.source_url:
            row = existing_by_url.get(candidate.source_url)
        if row is None:
            row = existing_by_hash.get(content_hash)

        department = candidate.department or source.department
        faculty = candidate.faculty or source.faculty
        unit_name = candidate.unit_name or source.unit_name

        if row is None:
            if dry_run:
                inserted += 1
                continue
            row = Event(
                source_id=source.id,
                title=title,
                original_text=original_text or None,
                summary=summary or None,
                display_summary=collapse_whitespace(candidate.display_summary) or summary or None,
                content_hash=content_hash,
                source_url=candidate.source_url,
                faculty=faculty,
                unit_name=unit_name,
                department=department,
                event_type=candidate.event_type,
                location=collapse_whitespace(candidate.location) or None,
                organizer=collapse_whitespace(candidate.organizer) or None,
                starts_at=candidate.starts_at,
                ends_at=candidate.ends_at,
                all_day=bool(candidate.all_day),
                last_seen_at=candidate_seen_at,
                fetched_at=seen_at,
                is_active=True,
                inactive_reason=None,
            )
            session.add(row)
            await session.flush()
            await _replace_event_links(
                session,
                event_id=int(row.id),
                links=candidate.links,
            )
            inserted += 1
            continue

        seen_row_ids.add(int(row.id))
        if dry_run:
            updated += 1
            continue

        row.source_id = source.id
        row.title = title
        row.original_text = original_text or None
        row.summary = summary or None
        row.display_summary = collapse_whitespace(candidate.display_summary) or summary or None
        row.content_hash = content_hash
        row.source_url = candidate.source_url
        row.faculty = faculty
        row.unit_name = unit_name
        row.department = department
        row.event_type = candidate.event_type
        row.location = collapse_whitespace(candidate.location) or None
        row.organizer = collapse_whitespace(candidate.organizer) or None
        row.starts_at = candidate.starts_at
        row.ends_at = candidate.ends_at
        row.all_day = bool(candidate.all_day)
        row.last_seen_at = candidate_seen_at
        row.fetched_at = seen_at
        row.is_active = True
        row.inactive_reason = None
        await _replace_event_links(
            session,
            event_id=int(row.id),
            links=candidate.links,
        )
        updated += 1

    deactivated = 0
    if allow_deactivation and not dry_run:
        grace_threshold = seen_at - timedelta(hours=_DEACTIVATION_GRACE_HOURS)
        source_rows = [
            row
            for row in existing_rows
            if row.source_id == source.id and row.id not in seen_row_ids
        ]
        for row in source_rows:
            if not row.is_active:
                continue
            if row.last_seen_at is not None and row.last_seen_at > grace_threshold:
                continue
            row.is_active = False
            row.inactive_reason = "missing_from_source"
            deactivated += 1

    return EventSyncStats(
        items_found=len(candidates),
        items_inserted=inserted,
        items_updated=updated,
        items_deactivated=deactivated,
    )


async def _replace_event_links(
    session: AsyncSession,
    *,
    event_id: int,
    links: tuple[EventLinkCandidate, ...],
) -> None:
    """Replace stored child links for an event with the latest parsed set."""

    await session.execute(
        delete(EventLink).where(EventLink.event_id == event_id)
    )
    for link in links:
        session.add(
            EventLink(
                event_id=event_id,
                label=collapse_whitespace(link.label) or collapse_whitespace(link.url),
                url=collapse_whitespace(link.url),
                link_type=collapse_whitespace(link.link_type) or "related",
                sort_order=int(link.sort_order),
            )
        )
