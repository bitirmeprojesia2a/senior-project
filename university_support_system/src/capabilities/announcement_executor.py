"""Capability executor for announcement database searches."""

from __future__ import annotations

from typing import Any

from src.capabilities.models import ExecutionResult
from src.db.announcements import (
    AnnouncementRecord,
    _detect_faculty_scope,
    _detect_unit_scope,
    fetch_relevant_announcements,
)


async def search(params: dict[str, Any]) -> ExecutionResult:
    """Run a whitelisted announcement search using existing DB helpers."""
    query = str(params.get("query") or "").strip()
    if not query:
        return ExecutionResult(
            success=False,
            capability="announcement.search",
            params=params,
            error="missing_query",
            missing_params=["query"],
            fallback_allowed=False,
        )

    limit = _safe_int(params.get("limit"), default=5, minimum=1, maximum=10)
    allow_latest_fallback = _safe_bool(
        params.get("allow_latest_fallback"),
        default=_default_allow_latest_fallback(query, params),
    )
    records = await fetch_relevant_announcements(
        query,
        department=_optional_text(params.get("department")),
        faculty=_optional_text(params.get("faculty")),
        unit_name=_optional_text(params.get("unit_name")),
        limit=limit,
        allow_latest_fallback=allow_latest_fallback,
        probe_mode=_optional_text(params.get("probe_mode")),
        require_keyword_match=_safe_bool(params.get("require_keyword_match"), default=False),
        minimum_match_score=_safe_optional_int(params.get("minimum_match_score")),
        recent_days=_safe_optional_int(params.get("recent_days")) or 30,
    )
    return ExecutionResult(
        success=True,
        capability="announcement.search",
        params=params,
        records=[_record_to_dict(item) for item in records],
        metadata={
            "query": query,
            "limit": limit,
            "allow_latest_fallback": allow_latest_fallback,
            "probe_mode": _optional_text(params.get("probe_mode")),
            "require_keyword_match": _safe_bool(params.get("require_keyword_match"), default=False),
            "record_count": len(records),
        },
        authoritative_no_records=True,
        fallback_allowed=False,
    )


def _record_to_dict(item: AnnouncementRecord) -> dict[str, Any]:
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
        "published_at": item.published_at.isoformat() if item.published_at else None,
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


def _safe_optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_bool(value: Any, *, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "evet"}:
        return True
    if text in {"false", "0", "no", "hayir", "hayır"}:
        return False
    return default


def _default_allow_latest_fallback(query: str, params: dict[str, Any]) -> bool:
    if _optional_text(params.get("faculty")) or _optional_text(params.get("unit_name")):
        return False
    if _detect_faculty_scope(query) or _detect_unit_scope(query):
        return False
    return True
