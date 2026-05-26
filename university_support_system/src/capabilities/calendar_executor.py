"""Deterministic executors for academic-calendar capabilities."""

from __future__ import annotations

from typing import Any

from src.capabilities.models import ExecutionResult


async def academic_date(params: dict[str, Any]) -> ExecutionResult:
    from src.agents.student.registration_utils import build_general_exam_calendar_answer

    query = _build_calendar_query(params)
    if not query:
        return ExecutionResult(
            success=False,
            capability="calendar.academic_date",
            params=params,
            error="missing_params",
            missing_params=["query|label"],
            fallback_allowed=False,
        )

    result = build_general_exam_calendar_answer(query)
    if result is None:
        return ExecutionResult(
            success=True,
            capability="calendar.academic_date",
            params={"query": query, "term": params.get("term")},
            records=[],
            metadata={"query": query, "term": params.get("term")},
            message="academic_calendar_date_not_found",
            authoritative_no_records=False,
            fallback_allowed=True,
        )

    answer, calendar_data = result
    record = dict(calendar_data)
    record["answer"] = answer
    return ExecutionResult(
        success=True,
        capability="calendar.academic_date",
        params={"query": query, "term": params.get("term")},
        records=[record],
        metadata={**calendar_data, "answer": answer},
        authoritative_no_records=True,
        fallback_allowed=False,
    )


def _build_calendar_query(params: dict[str, Any]) -> str | None:
    query = _clean(params.get("query"))
    if query:
        return query

    label = _clean(params.get("label"))
    if not label:
        return None

    term = _clean(params.get("term"))
    return " ".join(part for part in (term, label, "ne zaman") if part)


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
