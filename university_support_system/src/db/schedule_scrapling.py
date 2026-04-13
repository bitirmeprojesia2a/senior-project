"""Optional Scrapling adapter for HTML-based schedule sources.

This module is intentionally optional: the current local timetable corpus is
PDF-first, so the main ingest path remains in ``schedule_ingest.py``.
When a department publishes weekly schedules as HTML tables, the same
``parse_schedule_table`` pipeline can be reused through Scrapling.
"""

from __future__ import annotations

from datetime import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from src.core.text_normalization import collapse_whitespace
from src.db.schedule_ingest import infer_schedule_context, parse_schedule_table

try:  # pragma: no cover - optional dependency
    from scrapling.fetchers import Fetcher
except ImportError:  # pragma: no cover - optional dependency
    Fetcher = None


def scrapling_is_available() -> bool:
    return Fetcher is not None


def _selector_text(node: Any) -> str:
    texts: list[str] = []
    css = getattr(node, "css", None)
    if callable(css):
        try:
            text_selector = css("::text")
            getall = getattr(text_selector, "getall", None)
            if callable(getall):
                texts = [collapse_whitespace(str(value)) for value in getall() if collapse_whitespace(str(value))]
        except Exception:
            texts = []

    if texts:
        return collapse_whitespace(" ".join(texts))

    raw_text = getattr(node, "text", None)
    if callable(raw_text):
        raw_text = raw_text()
    if raw_text is None:
        raw_text = getattr(node, "get", lambda: "")()
    return collapse_whitespace(str(raw_text))


def _extract_table_grid(table_node: Any) -> list[list[str]]:
    rows: list[list[str]] = []
    for row_node in table_node.css("tr"):
        row_values = [_selector_text(cell) for cell in row_node.css("th, td")]
        if any(row_values):
            rows.append(row_values)
    return rows


def _dedupe_slots(parsed_slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: dict[
        tuple[str, str, str, str, str | None, str | None, str, time, str | None],
        dict[str, Any],
    ] = {}
    for slot in parsed_slots:
        key = (
            slot["academic_year"],
            slot["term"],
            slot["department"],
            slot["course_key"],
            slot["schedule_group"],
            slot["section"],
            slot["day_of_week"],
            slot["start_time"],
            slot["classroom"],
        )
        deduped[key] = slot
    return list(deduped.values())


def collect_schedule_slots_from_scrapling_response(
    response: Any,
    *,
    source_name: str,
    source_url: str | None = None,
    academic_year: str | None = None,
    term: str | None = None,
    department: str | None = None,
) -> list[dict[str, Any]]:
    preview_text = _selector_text(response)
    context = infer_schedule_context(
        Path(source_name),
        preview_text,
        academic_year=academic_year,
        term=term,
        department=department,
    )

    parsed_slots: list[dict[str, Any]] = []
    for table_node in response.css("table"):
        table_grid = _extract_table_grid(table_node)
        if not table_grid:
            continue
        parsed_slots.extend(
            parse_schedule_table(
                table_grid,
                context,
                source_document=source_name,
                source_url=source_url,
            )
        )

    return _dedupe_slots(parsed_slots)


def collect_schedule_slots_from_scrapling_url(
    url: str,
    *,
    source_name: str | None = None,
    academic_year: str | None = None,
    term: str | None = None,
    department: str | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    if Fetcher is None:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "Scrapling yüklü değil. HTML schedule ingest için `pip install scrapling` ile kurulum yapın."
        )

    resolved_source_name = source_name or Path(urlparse(url).path).name or "schedule.html"
    response = Fetcher.fetch(url, follow_redirects=True, timeout=30)
    rows = collect_schedule_slots_from_scrapling_response(
        response,
        source_name=resolved_source_name,
        source_url=url,
        academic_year=academic_year,
        term=term,
        department=department,
    )
    return resolved_source_name, rows
