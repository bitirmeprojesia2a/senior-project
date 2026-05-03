"""Announcement source registry and synchronization persistence helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
import hashlib
from typing import Any

from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.text_normalization import collapse_whitespace, normalize_text
from src.db.connection import get_session
from src.db.support_models import (
    Announcement,
    AnnouncementLink,
    AnnouncementSource,
    AnnouncementSyncRun,
)

_DEACTIVATION_GRACE_HOURS = 48


@dataclass(frozen=True)
class AnnouncementSourceRecord:
    """Serializable view of a configured announcement source."""

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
class AnnouncementCandidate:
    """Normalized announcement payload ready to persist."""

    title: str
    source_url: str | None
    original_text: str | None
    summary: str | None = None
    display_summary: str | None = None
    published_at: datetime | None = None
    faculty: str | None = None
    unit_name: str | None = None
    department: str | None = None
    links: tuple["AnnouncementLinkCandidate", ...] = ()


@dataclass(frozen=True)
class AnnouncementLinkCandidate:
    """Link metadata extracted from an announcement detail page."""

    label: str
    url: str
    link_type: str = "attachment"
    sort_order: int = 0


@dataclass(frozen=True)
class AnnouncementSyncStats:
    """Counts collected during a sync run."""

    items_found: int = 0
    items_inserted: int = 0
    items_updated: int = 0
    items_deactivated: int = 0


def build_announcement_content_hash(
    *,
    title: str,
    source_url: str | None,
    original_text: str | None,
) -> str:
    """Build a stable content hash for duplicate detection."""

    payload = "||".join(
        [
            normalize_text(collapse_whitespace(title)),
            normalize_text(source_url or ""),
            normalize_text(collapse_whitespace(original_text or "")),
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def summarize_announcement_text(
    *,
    title: str,
    original_text: str | None,
    max_chars: int = 280,
) -> str:
    """Produce a lightweight summary without requiring LLM synthesis."""

    text = collapse_whitespace(original_text)
    if not text:
        return collapse_whitespace(title)
    if len(text) <= max_chars:
        return text

    for separator in (". ", "! ", "? "):
        first_sentence, found, _ = text.partition(separator)
        if found and len(first_sentence) >= 40:
            sentence = f"{first_sentence.strip()}{separator.strip()}"
            if len(sentence) <= max_chars:
                return sentence

    return f"{text[: max_chars - 3].rstrip()}..."


def _source_to_record(source: AnnouncementSource) -> AnnouncementSourceRecord:
    return AnnouncementSourceRecord(
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


async def fetch_active_announcement_sources(
    *,
    source_id: int | None = None,
) -> list[AnnouncementSourceRecord]:
    """Return active sources from the registry."""

    async with get_session() as session:
        query = select(AnnouncementSource).where(AnnouncementSource.is_active.is_(True))
        if source_id is not None:
            query = query.where(AnnouncementSource.id == source_id)
        query = query.order_by(AnnouncementSource.id.asc())
        rows = list((await session.execute(query)).scalars().all())
        return [_source_to_record(row) for row in rows]


async def get_or_create_announcement_source(
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
) -> AnnouncementSourceRecord:
    """Create or update a source definition keyed by list_url."""

    result = await session.execute(
        select(AnnouncementSource).where(AnnouncementSource.list_url == list_url)
    )
    source = result.scalar_one_or_none()
    if source is None:
        source = AnnouncementSource(
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


async def create_announcement_sync_run(
    session: AsyncSession,
    *,
    source_id: int,
    started_at: datetime | None = None,
) -> AnnouncementSyncRun:
    """Create a sync run record before fetch/parse begins."""

    run = AnnouncementSyncRun(
        source_id=source_id,
        started_at=started_at or datetime.now(UTC),
        status="started",
    )
    session.add(run)
    await session.flush()
    return run


async def finalize_announcement_sync_run(
    session: AsyncSession,
    *,
    run: AnnouncementSyncRun,
    status: str,
    stats: AnnouncementSyncStats,
    error_message: str | None = None,
    finished_at: datetime | None = None,
) -> None:
    """Persist final run counters and status."""

    run.status = status
    run.items_found = stats.items_found
    run.items_inserted = stats.items_inserted
    run.items_updated = stats.items_updated
    run.items_deactivated = stats.items_deactivated
    run.error_message = error_message
    run.finished_at = finished_at or datetime.now(UTC)
    await session.flush()


async def mark_announcement_source_sync_result(
    session: AsyncSession,
    *,
    source_id: int,
    success: bool,
    finished_at: datetime | None = None,
    error_message: str | None = None,
) -> None:
    """Store the last success/error state on a source record."""

    source = await session.get(AnnouncementSource, source_id)
    if source is None:
        return
    if success:
        source.last_success_at = finished_at or datetime.now(UTC)
        source.last_error = None
    else:
        source.last_error = error_message
    await session.flush()


async def upsert_announcements_for_source(
    session: AsyncSession,
    *,
    source: AnnouncementSourceRecord,
    candidates: list[AnnouncementCandidate],
    seen_at: datetime | None = None,
    dry_run: bool = False,
    allow_deactivation: bool = True,
) -> AnnouncementSyncStats:
    """Insert/update normalized announcement candidates for a single source."""

    seen_at = seen_at or datetime.now(UTC)
    stats = AnnouncementSyncStats(items_found=len(candidates))
    if not candidates:
        return stats

    urls = [candidate.source_url for candidate in candidates if candidate.source_url]
    query = select(Announcement)
    if urls:
        query = query.where(
            or_(
                Announcement.source_id == source.id,
                Announcement.source_url.in_(urls),
            )
        )
    else:
        query = query.where(Announcement.source_id == source.id)

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
        original_text = collapse_whitespace((candidate.original_text or "").replace("\x00", " "))
        summary = collapse_whitespace((candidate.summary or "").replace("\x00", " ")) or summarize_announcement_text(
            title=title,
            original_text=original_text,
        )
        display_summary = collapse_whitespace((candidate.display_summary or "").replace("\x00", " "))
        content_hash = build_announcement_content_hash(
            title=title,
            source_url=candidate.source_url,
            original_text=original_text,
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
            row = Announcement(
                source_id=source.id,
                title=title,
                original_text=original_text or None,
                summary=summary or None,
                display_summary=display_summary or summary or None,
                content_hash=content_hash,
                source_url=candidate.source_url,
                faculty=faculty,
                unit_name=unit_name,
                department=department,
                published_at=candidate.published_at,
                last_seen_at=candidate_seen_at,
                fetched_at=seen_at,
                is_active=True,
                inactive_reason=None,
            )
            session.add(row)
            await session.flush()
            await _replace_announcement_links(
                session,
                announcement_id=int(row.id),
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
        row.display_summary = display_summary or summary or None
        row.content_hash = content_hash
        row.source_url = candidate.source_url
        row.faculty = faculty
        row.unit_name = unit_name
        row.department = department
        row.published_at = candidate.published_at
        row.last_seen_at = candidate_seen_at
        row.fetched_at = seen_at
        row.is_active = True
        row.inactive_reason = None
        await _replace_announcement_links(
            session,
            announcement_id=int(row.id),
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

    return AnnouncementSyncStats(
        items_found=len(candidates),
        items_inserted=inserted,
        items_updated=updated,
        items_deactivated=deactivated,
    )


async def _replace_announcement_links(
    session: AsyncSession,
    *,
    announcement_id: int,
    links: tuple[AnnouncementLinkCandidate, ...],
) -> None:
    """Replace stored child links for an announcement with the latest parsed set."""

    await session.execute(
        delete(AnnouncementLink).where(AnnouncementLink.announcement_id == announcement_id)
    )
    for link in links:
        session.add(
            AnnouncementLink(
                announcement_id=announcement_id,
                label=collapse_whitespace(link.label) or collapse_whitespace(link.url),
                url=collapse_whitespace(link.url),
                link_type=collapse_whitespace(link.link_type) or "attachment",
                sort_order=int(link.sort_order),
            )
        )
