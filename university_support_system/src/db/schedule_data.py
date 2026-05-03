"""Structured course schedule queries for future hybrid timetable answers."""

from __future__ import annotations

import re
from typing import Any

from sqlalchemy import select

from src.core.text_normalization import normalize_text
from src.db.connection import get_session
from src.db.student_models import CourseScheduleSlot

_DEPARTMENT_SUFFIXES = (
    "bolumu",
    "bolum",
    "programi",
    "program",
    "anabilim dali",
    "abd",
    "lisans",
    "onlisans",
)
_WEEKDAY_ORDER = {
    "pazartesi": 1,
    "sali": 2,
    "carsamba": 3,
    "persembe": 4,
    "cuma": 5,
    "cumartesi": 6,
    "pazar": 7,
}


def _department_match_key(value: str | None) -> str:
    """Normalize department names for schedule matching."""
    normalized = normalize_text(value or "")
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    for suffix in _DEPARTMENT_SUFFIXES:
        normalized = re.sub(rf"\b{re.escape(suffix)}\b", " ", normalized)
    return " ".join(normalized.split())


def _schedule_sort_key(slot: CourseScheduleSlot) -> tuple[int, str, str, str, str]:
    """Sort schedule rows by actual weekday order, then time/group/course."""
    return (
        _weekday_sort_value(slot.day_of_week),
        str(slot.start_time or ""),
        slot.schedule_group or "",
        slot.course_key or "",
        slot.section or "",
    )


def _weekday_sort_value(day_of_week: str | None) -> int:
    return _WEEKDAY_ORDER.get(normalize_text(day_of_week or ""), 99)


def schedule_row_sort_key(row: dict[str, Any]) -> tuple[int, str, str, str, str]:
    """Sort serialized schedule rows consistently with DB model rows."""
    return (
        _weekday_sort_value(str(row.get("day_of_week") or "")),
        str(row.get("start_time") or ""),
        str(row.get("schedule_group") or ""),
        str(row.get("course_key") or ""),
        str(row.get("section") or ""),
    )


def _slot_to_dict(slot: CourseScheduleSlot) -> dict[str, Any]:
    return {
        "academic_year": slot.academic_year,
        "term": slot.term,
        "department": slot.department,
        "course_code": slot.course_code,
        "course_key": slot.course_key,
        "course_name": slot.course_name,
        "schedule_group": slot.schedule_group or None,
        "section": slot.section or None,
        "day_of_week": slot.day_of_week,
        "start_time": slot.start_time.isoformat() if slot.start_time else None,
        "end_time": slot.end_time.isoformat() if slot.end_time else None,
        "classroom": slot.classroom,
        "instructor": slot.instructor,
        "source_document": slot.source_document,
        "source_url": slot.source_url,
        "is_active": slot.is_active,
    }


async def fetch_schedule_slots_by_department(
    department: str,
    *,
    academic_year: str | None = None,
    term: str | None = None,
) -> list[dict[str, Any]]:
    """Return structured schedule rows for a department."""
    normalized_department = _department_match_key(department)
    if not normalized_department:
        return []

    async with get_session() as session:
        stmt = select(CourseScheduleSlot).where(CourseScheduleSlot.is_active.is_(True))
        if academic_year:
            stmt = stmt.where(CourseScheduleSlot.academic_year == academic_year)
        if term:
            stmt = stmt.where(CourseScheduleSlot.term == term)

        rows = (await session.execute(stmt)).scalars().all()
        matches = [
            slot for slot in rows
            if _department_match_key(slot.department) == normalized_department
        ]
        matches.sort(key=_schedule_sort_key)
        return [_slot_to_dict(slot) for slot in matches]


async def fetch_schedule_slots_for_course(
    course_code: str,
    *,
    department: str | None = None,
    academic_year: str | None = None,
    term: str | None = None,
) -> list[dict[str, Any]]:
    """Return structured schedule rows for a course code."""
    normalized_query = normalize_text(course_code).replace(" ", "")
    if not normalized_query:
        return []

    async with get_session() as session:
        stmt = select(CourseScheduleSlot).where(CourseScheduleSlot.is_active.is_(True))
        if academic_year:
            stmt = stmt.where(CourseScheduleSlot.academic_year == academic_year)
        if term:
            stmt = stmt.where(CourseScheduleSlot.term == term)

        rows = (await session.execute(stmt)).scalars().all()
        matches = [
            slot for slot in rows
            if (
                normalize_text(slot.course_code).replace(" ", "") == normalized_query
                or normalize_text(slot.course_key).replace(" ", "") == normalized_query
            )
        ]

        if department:
            normalized_department = _department_match_key(department)
            matches = [
                slot for slot in matches
                if _department_match_key(slot.department) == normalized_department
            ]

        matches.sort(
            key=lambda slot: (
                _schedule_sort_key(slot)[0],
                str(slot.start_time or ""),
                slot.schedule_group or "",
                slot.section or "",
                slot.department,
            )
        )
        return [_slot_to_dict(slot) for slot in matches]
