"""Helpers for seeding curriculum and prerequisite data safely."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from src.core.text_normalization import normalize_text
from src.db.curriculum_data import resolve_course_code
from src.db.student_models import Course, CoursePrerequisite

SHARED_SOCIAL_ELECTIVE_DEPARTMENT = "Sosyal Secmeli"
_SHARED_SOCIAL_ELECTIVE_TYPES = {"sosyal_secmeli", "universite_secmeli"}
PROGRAM_SLOT_COURSE_TYPE = "secmeli_grup"


@dataclass(slots=True)
class CurriculumSeedResult:
    deleted_prerequisites: int
    processed_courses: int
    inserted_prerequisites: int
    missing_courses: list[str]
    missing_prerequisites: list[str]


def _normalize_course_type(value: Any) -> str:
    course_type = str(value or "zorunlu").strip().lower()
    return course_type or "zorunlu"


def normalize_curriculum_course_row(
    row: dict[str, Any],
    *,
    default_department: str,
) -> dict[str, Any]:
    """Canonicalize curriculum rows before they touch the database."""

    course_type = _normalize_course_type(row.get("course_type"))
    department = str(row.get("department") or default_department).strip()
    elective_group = row.get("elective_group")
    if elective_group is not None:
        elective_group = str(elective_group).strip() or None

    curriculum_semester = row.get("curriculum_semester")
    if curriculum_semester in ("", None):
        curriculum_semester = None
    elif curriculum_semester is not None:
        curriculum_semester = int(curriculum_semester)

    if course_type in _SHARED_SOCIAL_ELECTIVE_TYPES:
        course_type = "sosyal_secmeli"
        department = SHARED_SOCIAL_ELECTIVE_DEPARTMENT
        curriculum_semester = None
        elective_group = None

    course_code, _alias_from = resolve_course_code(str(row["course_code"]))

    return {
        "course_code": course_code,
        "course_name": str(row["course_name"]).strip(),
        "department": department,
        "theory_hours": int(row.get("theory_hours", 0)),
        "practice_hours": int(row.get("practice_hours", 0)),
        "lab_hours": int(row.get("lab_hours", 0)),
        "credits": int(row.get("credits", 0)),
        "akts": int(row.get("akts", row.get("credits", 0))),
        "curriculum_semester": curriculum_semester,
        "course_type": course_type,
        "elective_group": elective_group,
    }


def normalize_program_slot_row(
    row: dict[str, Any],
    *,
    default_department: str,
) -> dict[str, Any]:
    """Normalize department-specific curriculum slot rows."""

    slot_code = str(row.get("course_code") or row.get("slot_code") or "").strip().upper()
    slot_name = str(row.get("course_name") or row.get("slot_name") or "").strip()
    if not slot_code or not slot_name:
        raise ValueError("Program slot rows must define slot_code/course_code and slot_name/course_name.")

    curriculum_semester = row.get("curriculum_semester")
    if curriculum_semester in ("", None):
        curriculum_semester = None
    elif curriculum_semester is not None:
        curriculum_semester = int(curriculum_semester)

    elective_group = row.get("elective_group")
    if elective_group is not None:
        elective_group = str(elective_group).strip() or None

    course_type = _normalize_course_type(row.get("course_type", PROGRAM_SLOT_COURSE_TYPE))
    if course_type != PROGRAM_SLOT_COURSE_TYPE:
        course_type = PROGRAM_SLOT_COURSE_TYPE

    return {
        "course_code": slot_code,
        "course_name": slot_name,
        "department": str(row.get("department") or default_department).strip() or default_department,
        "theory_hours": int(row.get("theory_hours", row.get("credits", 0))),
        "practice_hours": int(row.get("practice_hours", 0)),
        "lab_hours": int(row.get("lab_hours", 0)),
        "credits": int(row.get("credits", 0)),
        "akts": int(row.get("akts", row.get("credits", 0))),
        "curriculum_semester": curriculum_semester,
        "course_type": course_type,
        "elective_group": elective_group,
    }


def _upsert_course(session: Session, **kwargs: Any) -> Course:
    code = str(kwargs["course_code"]).strip().upper()
    existing = session.scalar(select(Course).where(Course.course_code == code))
    if existing:
        for key, value in kwargs.items():
            if value is not None:
                setattr(existing, key, value)
        return existing

    course = Course(**kwargs)
    session.add(course)
    session.flush()
    return course


def _clean_prerequisites_for_courses(session: Session, course_codes: Iterable[str]) -> int:
    normalized_codes = sorted({str(code).strip().upper() for code in course_codes if str(code).strip()})
    if not normalized_codes:
        return 0

    course_ids = list(
        session.scalars(
            select(Course.id).where(Course.course_code.in_(normalized_codes))
        ).all()
    )
    if not course_ids:
        return 0

    result = session.execute(
        delete(CoursePrerequisite).where(CoursePrerequisite.course_id.in_(course_ids))
    )
    session.flush()
    return int(result.rowcount or 0)


def _resolve_prerequisite_course(
    session: Session,
    *,
    code_to_obj: dict[str, Course],
    prereq_code: str,
    prereq_name: str | None,
) -> Course | None:
    candidate_codes = [prereq_code]
    resolved_code, alias_from = resolve_course_code(prereq_code)
    if resolved_code not in candidate_codes:
        candidate_codes.append(resolved_code)
    if alias_from and alias_from not in candidate_codes:
        candidate_codes.append(alias_from)

    for candidate_code in candidate_codes:
        course = code_to_obj.get(candidate_code)
        if course is None:
            course = session.scalar(select(Course).where(Course.course_code == candidate_code))
        if course is not None:
            return course

    normalized_prereq_name = normalize_text(prereq_name)
    if normalized_prereq_name:
        for course in code_to_obj.values():
            if normalize_text(course.course_name) == normalized_prereq_name:
                return course
        return session.scalar(
            select(Course).where(Course.course_name == prereq_name)
        ) or next(
            (
                course
                for course in session.scalars(select(Course)).all()
                if normalize_text(course.course_name) == normalized_prereq_name
            ),
            None,
        )

    return None


def seed_curriculum_records(
    session: Session,
    *,
    courses: Sequence[dict[str, Any]],
    prerequisites: Sequence[dict[str, Any]],
    managed_prerequisite_course_codes: Sequence[str] | None = None,
) -> CurriculumSeedResult:
    """Insert/update curriculum courses and reset prerequisites only for managed courses."""

    normalized_courses: list[dict[str, Any]] = []
    for row in courses:
        default_department = str(row.get("department", "")).strip()
        if "slot_code" in row or "slot_name" in row:
            normalized_courses.append(
                normalize_program_slot_row(row, default_department=default_department)
            )
        else:
            normalized_courses.append(
                normalize_curriculum_course_row(row, default_department=default_department)
            )
    managed_codes = [course["course_code"] for course in normalized_courses]
    prerequisite_scope = (
        managed_codes
        if managed_prerequisite_course_codes is None
        else [str(code).strip().upper() for code in managed_prerequisite_course_codes]
    )
    deleted = _clean_prerequisites_for_courses(session, prerequisite_scope)

    code_to_obj: dict[str, Course] = {}
    for row in normalized_courses:
        code = row["course_code"]
        course = _upsert_course(
            session,
            course_code=code,
            course_name=row["course_name"],
            department=row["department"],
            theory_hours=row["theory_hours"],
            practice_hours=row["practice_hours"],
            lab_hours=row["lab_hours"],
            credits=row["credits"],
            akts=row["akts"],
            curriculum_semester=row.get("curriculum_semester"),
            course_type=row["course_type"],
            elective_group=row.get("elective_group"),
        )
        code_to_obj[code] = course

    session.flush()

    inserted_prereqs = 0
    missing_courses: list[str] = []
    missing_prereqs: list[str] = []

    for row in prerequisites:
        course_code = str(row["course_code"]).strip().upper()
        course = code_to_obj.get(course_code)
        if course is None:
            missing_courses.append(course_code)
            continue

        for prereq in row.get("prerequisites", []):
            prereq_code = str(prereq["course_code"]).strip().upper()
            prereq_course = _resolve_prerequisite_course(
                session,
                code_to_obj=code_to_obj,
                prereq_code=prereq_code,
                prereq_name=str(prereq.get("course_name") or "").strip() or None,
            )
            if prereq_course is None:
                missing_prereqs.append(f"{course_code}->{prereq_code}")
                continue

            session.add(
                CoursePrerequisite(
                    course_id=course.id,
                    prerequisite_id=prereq_course.id,
                    prerequisite_group=int(prereq.get("group", 1)),
                )
            )
            inserted_prereqs += 1

    session.flush()
    return CurriculumSeedResult(
        deleted_prerequisites=deleted,
        processed_courses=len(code_to_obj),
        inserted_prerequisites=inserted_prereqs,
        missing_courses=sorted(set(missing_courses)),
        missing_prerequisites=sorted(set(missing_prereqs)),
    )


def load_curriculum_payload(path: str | Path) -> dict[str, Any]:
    """Load and normalize curriculum seed payload from JSON."""

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    department = str(payload.get("department", "")).strip()
    if not department:
        raise ValueError("Curriculum payload must define 'department'.")

    raw_courses = payload.get("courses")
    if not isinstance(raw_courses, list) or not raw_courses:
        raise ValueError("Curriculum payload must include a non-empty 'courses' list.")

    normalized_courses: list[dict[str, Any]] = []
    for index, row in enumerate(raw_courses, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"Course row #{index} must be an object.")

        course_code = str(row.get("course_code", "")).strip().upper()
        course_name = str(row.get("course_name", "")).strip()
        if not course_code or not course_name:
            raise ValueError(f"Course row #{index} is missing course_code/course_name.")

        normalized_courses.append(
            normalize_curriculum_course_row(
                {
                    "course_code": course_code,
                    "course_name": course_name,
                    "department": row.get("department"),
                    "theory_hours": row.get("theory_hours", 0),
                    "practice_hours": row.get("practice_hours", 0),
                    "lab_hours": row.get("lab_hours", 0),
                    "credits": row.get("credits", 0),
                    "akts": row.get("akts", row.get("credits", 0)),
                    "curriculum_semester": row.get("curriculum_semester"),
                    "course_type": row.get("course_type", "zorunlu"),
                    "elective_group": row.get("elective_group"),
                },
                default_department=department,
            )
        )

    raw_prereqs = payload.get("prerequisites", [])
    if not isinstance(raw_prereqs, list):
        raise ValueError("'prerequisites' must be a list when provided.")

    normalized_prereqs: list[dict[str, Any]] = []
    for index, row in enumerate(raw_prereqs, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"Prerequisite row #{index} must be an object.")

        course_code = str(row.get("course_code", "")).strip().upper()
        prereq_items = row.get("prerequisites", [])
        if not course_code:
            raise ValueError(f"Prerequisite row #{index} is missing course_code.")
        if not isinstance(prereq_items, list):
            raise ValueError(f"Prerequisite row #{index} must contain a prerequisites list.")

        normalized_items: list[dict[str, Any]] = []
        for prereq in prereq_items:
            if not isinstance(prereq, dict):
                raise ValueError(
                    f"Prerequisite row #{index} contains a non-object prerequisite entry."
                )
            prereq_code = str(prereq.get("course_code", "")).strip().upper()
            if not prereq_code:
                raise ValueError(
                    f"Prerequisite row #{index} contains an entry without course_code."
                )
            normalized_items.append(
                {
                    "course_code": prereq_code,
                    "group": int(prereq.get("group", 1)),
                    "course_name": str(prereq.get("course_name", "")).strip() or None,
                }
            )

        normalized_prereqs.append(
            {"course_code": course_code, "prerequisites": normalized_items}
        )

    raw_program_slots = payload.get("program_slots", [])
    if not isinstance(raw_program_slots, list):
        raise ValueError("'program_slots' must be a list when provided.")

    normalized_program_slots: list[dict[str, Any]] = []
    for index, row in enumerate(raw_program_slots, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"Program slot row #{index} must be an object.")
        normalized_program_slots.append(
            normalize_program_slot_row(row, default_department=department)
        )

    payload["department"] = department
    payload["courses"] = normalized_courses + normalized_program_slots
    payload["prerequisites"] = normalized_prereqs
    return payload
