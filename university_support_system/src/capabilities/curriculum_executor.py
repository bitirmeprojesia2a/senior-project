"""Deterministic executors for academic-program capabilities."""

from __future__ import annotations

from typing import Any

from src.agents.academic.curriculum_utils import (
    COURSE_CODE_PATTERN,
    infer_department_from_query,
)
from src.capabilities.models import ExecutionResult
from src.db.curriculum_data import (
    fetch_course_prerequisites,
    fetch_courses_by_curriculum_semester,
    fetch_courses_by_title,
)
from src.db.schedule_data import (
    fetch_schedule_slots_by_department,
    fetch_schedule_slots_for_course,
    schedule_row_sort_key,
)
from src.core.text_normalization import normalize_text


MAX_RECORDS = 120


async def course_exists_in_program(params: dict[str, Any]) -> ExecutionResult:
    program = _resolve_program(params.get("program"))
    course = _clean(params.get("course") or params.get("course_code"))
    if not program or not course:
        return _missing("course.exists_in_program", params, ["program", "course"])

    records = await fetch_courses_by_title(course, department=program, limit=20)
    return ExecutionResult(
        success=True,
        capability="course.exists_in_program",
        params={"program": program, "course": course},
        records=_limit(records),
        metadata={"program": program, "course": course, "exists": bool(records)},
        message=None if records else "course_not_found_in_program",
        authoritative_no_records=True,
        fallback_allowed=False,
    )


async def course_detail(params: dict[str, Any]) -> ExecutionResult:
    program = _resolve_program(params.get("program"))
    course_code = _extract_course_code(params.get("course_code") or params.get("course"))
    course = _clean(params.get("course"))

    if course_code:
        record = await fetch_course_prerequisites(course_code)
        records = [record] if record else []
        return ExecutionResult(
            success=True,
            capability="course.detail",
            params={"program": program, "course_code": course_code},
            records=records,
            metadata={"program": program, "course_code": course_code},
            message=None if records else "course_not_found",
            authoritative_no_records=True,
            fallback_allowed=False,
        )

    if not course:
        return _missing("course.detail", params, ["course_code|course"])

    records = await fetch_courses_by_title(course, department=program, limit=20)
    return ExecutionResult(
        success=True,
        capability="course.detail",
        params={"program": program, "course": course},
        records=_limit(records),
        metadata={"program": program, "course": course},
        message=None if records else "course_not_found",
        authoritative_no_records=True,
        fallback_allowed=False,
    )


async def course_prerequisites(params: dict[str, Any]) -> ExecutionResult:
    program = _resolve_program(params.get("program"))
    course_code = _extract_course_code(params.get("course_code") or params.get("course"))
    course = _clean(params.get("course"))

    if not course_code and course:
        matches = await fetch_courses_by_title(course, department=program, limit=5)
        if len(matches) == 1:
            course_code = _extract_course_code(matches[0].get("course_code"))
        elif matches:
            return ExecutionResult(
                success=True,
                capability="course.prerequisites",
                params={"program": program, "course": course},
                records=_limit(matches),
                metadata={"program": program, "course": course, "ambiguous": True},
                message="multiple_course_matches",
                authoritative_no_records=False,
                fallback_allowed=False,
            )

    if not course_code:
        return _missing("course.prerequisites", params, ["course_code|course"])

    record = await fetch_course_prerequisites(course_code)
    return ExecutionResult(
        success=True,
        capability="course.prerequisites",
        params={"program": program, "course_code": course_code},
        records=[record] if record else [],
        metadata={"program": program, "course_code": course_code},
        message=None if record else "course_not_found",
        authoritative_no_records=True,
        fallback_allowed=False,
    )


async def semester_courses(params: dict[str, Any]) -> ExecutionResult:
    program = _resolve_program(params.get("program"))
    semester = _as_int(params.get("semester"))
    if not program or semester is None:
        return _missing("curriculum.semester_courses", params, ["program", "semester"])

    records = await fetch_courses_by_curriculum_semester(semester, department=program)
    return ExecutionResult(
        success=True,
        capability="curriculum.semester_courses",
        params={"program": program, "semester": semester},
        records=_limit(records),
        metadata={
            "program": program,
            "semester": semester,
            "class_year": params.get("class_year") or _class_year_from_semester(semester),
            "term": params.get("term") or _term_from_semester(semester),
        },
        message=None if records else "semester_courses_not_found",
        authoritative_no_records=True,
        fallback_allowed=False,
    )


async def weekly_program(params: dict[str, Any]) -> ExecutionResult:
    program = _resolve_program(params.get("program"))
    if not program:
        return _missing("schedule.weekly_program", params, ["program"])

    course_code = _extract_course_code(params.get("course_code") or params.get("course"))
    semester = _as_int(params.get("semester"))
    class_year = _as_int(params.get("class_year")) or _class_year_from_semester(semester)
    term = _normalize_term(params.get("term")) or _term_from_semester(semester)

    if course_code:
        rows = await fetch_schedule_slots_for_course(course_code, department=program)
    else:
        rows = await fetch_schedule_slots_by_department(program)

    filtered = _filter_schedule_rows(rows, term=term, class_year=class_year)
    filtered.sort(key=schedule_row_sort_key)
    return ExecutionResult(
        success=True,
        capability="schedule.weekly_program",
        params={
            "program": program,
            "course_code": course_code,
            "semester": semester,
            "class_year": class_year,
            "term": term,
        },
        records=_limit(filtered),
        metadata={
            "program": program,
            "course_code": course_code,
            "semester": semester,
            "class_year": class_year,
            "term": term,
            "raw_count": len(rows),
        },
        message=None if filtered else "schedule_not_found",
        authoritative_no_records=True,
        fallback_allowed=False,
    )


def _missing(capability: str, params: dict[str, Any], names: list[str]) -> ExecutionResult:
    return ExecutionResult(
        success=False,
        capability=capability,
        params=params,
        error="missing_params",
        missing_params=names,
        fallback_allowed=False,
    )


def _resolve_program(value: Any) -> str | None:
    cleaned = _clean(value)
    if not cleaned:
        return None
    return infer_department_from_query(cleaned) or cleaned


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _as_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _extract_course_code(value: Any) -> str | None:
    text = _clean(value)
    if not text:
        return None
    match = COURSE_CODE_PATTERN.search(text)
    if not match:
        return None
    return match.group(0).upper().replace(" ", "")


def _class_year_from_semester(semester: int | None) -> int | None:
    if semester is None:
        return None
    return (semester + 1) // 2


def _term_from_semester(semester: int | None) -> str | None:
    if semester is None:
        return None
    return "guz" if semester % 2 == 1 else "bahar"


def _normalize_term(value: Any) -> str | None:
    text = normalize_text(str(value or ""))
    if not text:
        return None
    if any(marker in text for marker in ("guz", "fall", "ilk donem", "1 donem")):
        return "guz"
    if any(marker in text for marker in ("bahar", "spring", "ikinci donem", "2 donem")):
        return "bahar"
    return None


def _filter_schedule_rows(
    rows: list[dict[str, Any]],
    *,
    term: str | None,
    class_year: int | None,
) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    for row in rows:
        if term:
            row_term = _normalize_term(row.get("term")) or normalize_text(str(row.get("term") or ""))
            if term not in row_term:
                continue
        if class_year:
            if not _schedule_group_matches_class_year(row.get("schedule_group"), class_year):
                continue
        filtered.append(row)
    return filtered


def _schedule_group_matches_class_year(value: Any, class_year: int) -> bool:
    group = normalize_text(str(value or "")).replace(".", " ")
    parts = " ".join(group.split())
    return f"{class_year} sinif" in parts


def _limit(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return records[:MAX_RECORDS]
