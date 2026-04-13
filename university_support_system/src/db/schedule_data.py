"""Structured course schedule queries for future hybrid timetable answers."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select

from src.core.text_normalization import normalize_text
from src.db.connection import get_session
from src.db.student_models import CourseScheduleSlot


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
    normalized_department = normalize_text(department)
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
            if normalize_text(slot.department) == normalized_department
        ]
        matches.sort(
            key=lambda slot: (
                slot.day_of_week,
                slot.start_time,
                slot.schedule_group or "",
                slot.course_key,
                slot.section or "",
            )
        )
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
            normalized_department = normalize_text(department)
            matches = [
                slot for slot in matches
                if normalize_text(slot.department) == normalized_department
            ]

        matches.sort(
            key=lambda slot: (
                slot.day_of_week,
                slot.start_time,
                slot.schedule_group or "",
                slot.section or "",
                slot.department,
            )
        )
        return [_slot_to_dict(slot) for slot in matches]
