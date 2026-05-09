"""Capability executor for event database searches."""

from __future__ import annotations

from typing import Any

from src.capabilities.models import ExecutionResult
from src.db.events import EventRecord, fetch_relevant_events


async def search(params: dict[str, Any]) -> ExecutionResult:
    """Run a whitelisted event search using existing DB helpers."""
    query = str(params.get("query") or "").strip()
    if not query:
        return ExecutionResult(
            success=False,
            capability="event.search",
            params=params,
            error="missing_query",
            missing_params=["query"],
            fallback_allowed=False,
        )

    limit = _safe_int(params.get("limit"), default=5, minimum=1, maximum=10)
    records = await fetch_relevant_events(
        query,
        department=_optional_text(params.get("department")),
        faculty=_optional_text(params.get("faculty")),
        unit_name=_optional_text(params.get("unit_name")),
        limit=limit,
    )
    return ExecutionResult(
        success=True,
        capability="event.search",
        params=params,
        records=[_record_to_dict(item) for item in records],
        metadata={
            "query": query,
            "limit": limit,
            "record_count": len(records),
        },
        authoritative_no_records=True,
        fallback_allowed=False,
    )


def _record_to_dict(item: EventRecord) -> dict[str, Any]:
    return {
        "id": item.id,
        "title": item.title,
        "display_summary": item.display_summary,
        "summary": item.summary,
        "original_text": item.original_text,
        "source_url": item.source_url,
        "faculty": item.faculty,
        "unit_name": item.unit_name,
        "department": item.department,
        "event_type": item.event_type,
        "location": item.location,
        "organizer": item.organizer,
        "starts_at": item.starts_at.isoformat() if item.starts_at else None,
        "ends_at": item.ends_at.isoformat() if item.ends_at else None,
        "all_day": item.all_day,
        "links": [
            {"label": link.label, "url": link.url, "link_type": link.link_type}
            for link in item.links
        ],
    }


def _optional_text(value: Any) -> str | None:
    text = str(value).strip() if value is not None else ""
    return text or None


def _safe_int(value: Any, *, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(parsed, maximum))
