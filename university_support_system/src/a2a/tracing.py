"""Lightweight trace metadata helpers for A2A task chains."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

TRACE_ID_KEY = "trace_id"
SPAN_ID_KEY = "span_id"
PARENT_SPAN_ID_KEY = "parent_span_id"
TRACE_METADATA_KEYS = (TRACE_ID_KEY, SPAN_ID_KEY, PARENT_SPAN_ID_KEY)


def new_trace_id() -> str:
    """Return an opaque correlation id shared by one user-visible query chain."""
    return uuid4().hex


def new_span_id() -> str:
    """Return a compact span id for one hop inside an A2A trace."""
    return uuid4().hex[:16]


def trace_metadata(metadata: dict[str, Any] | None) -> dict[str, str]:
    """Extract non-empty trace fields from arbitrary metadata."""
    if not metadata:
        return {}
    fields: dict[str, str] = {}
    for key in TRACE_METADATA_KEYS:
        value = metadata.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            fields[key] = text
    return fields


def ensure_trace_metadata(
    metadata: dict[str, Any] | None = None,
    *,
    trace_id: str | None = None,
    span_id: str | None = None,
    parent_span_id: str | None = None,
) -> dict[str, Any]:
    """Return metadata with trace/span ids, preserving existing values."""
    merged = dict(metadata or {})
    existing_trace = str(merged.get(TRACE_ID_KEY) or trace_id or "").strip()
    existing_span = str(merged.get(SPAN_ID_KEY) or span_id or "").strip()
    existing_parent = str(merged.get(PARENT_SPAN_ID_KEY) or parent_span_id or "").strip()

    merged[TRACE_ID_KEY] = existing_trace or new_trace_id()
    merged[SPAN_ID_KEY] = existing_span or new_span_id()
    if existing_parent:
        merged[PARENT_SPAN_ID_KEY] = existing_parent
    else:
        merged.pop(PARENT_SPAN_ID_KEY, None)
    return merged


def child_trace_metadata(metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return metadata for a child A2A hop in the same trace."""
    parent = ensure_trace_metadata(metadata)
    child = dict(parent)
    child[PARENT_SPAN_ID_KEY] = str(parent[SPAN_ID_KEY])
    child[SPAN_ID_KEY] = new_span_id()
    return child
