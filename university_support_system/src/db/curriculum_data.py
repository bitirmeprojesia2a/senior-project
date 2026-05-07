"""Mufredat ve ders katalogu odakli veri sorgulari."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, ProgrammingError

from src.core.text_normalization import normalize_text
from src.db.connection import get_session
from src.db.student_models import Course, CoursePrerequisite

logger = logging.getLogger(__name__)

COURSE_CODE_ALIASES: dict[str, str] = {
    "TBMAT101": "TBMAT111",
    "TBMAT102": "TBMAT112",
    "TBFIZ115": "TBFIZ121",
    "BIL205": "BIL215",
    "BIL307": "BIL313",
    "BIL461": "BIL409",
}
_SHARED_CURRICULUM_DEPARTMENT_MARKERS = (
    "temel bilimler",
    "yabanci diller",
    "ataturk ilkeleri",
    "turk dili",
    "is sagligi",
    "muhendislik fakultesi ortak",
    "sosyal secmeli",
)
_ELECTIVE_COURSE_TYPES = {
    "teknik_secmeli",
    "lab_secmeli",
    "secmeli_grup",
    "sosyal_secmeli",
    "universite_secmeli",
}
_PROGRAM_TOTAL_EXCLUDED_TYPES = {"staj", "mup", "sanayi"}
_COURSE_TITLE_STOPWORDS = {
    "ders",
    "dersi",
    "dersin",
    "dersinin",
    "hangi",
    "kacinci",
    "kac",
    "sinif",
    "sinifta",
    "yariyil",
    "donem",
    "mi",
    "ne",
    "neler",
    "nelerdir",
    "var",
    "vardir",
    "bulunur",
    "bulunuyor",
    "mufredat",
    "mufredatta",
    "mufredatinda",
    "bolum",
    "bolumu",
    "program",
    "programi",
    "onkosul",
    "onkosulu",
    "kosul",
    "kosulu",
    "akts",
    "kredi",
    "ve",
    "ile",
    "icin",
}
_COURSE_CODE_NORMALIZE_MAP = str.maketrans(
    {
        "Ç": "C",
        "Ğ": "G",
        "İ": "I",
        "Ö": "O",
        "Ş": "S",
        "Ü": "U",
        "ç": "C",
        "ğ": "G",
        "ı": "I",
        "i": "I",
        "ö": "O",
        "ş": "S",
        "ü": "U",
    }
)


def _is_missing_column_error(exc: Exception) -> bool:
    """Veritabani semasi koddan geride kaldiginda gelen kolon hatasini tanir."""
    message = str(exc).lower()
    return "does not exist" in message or "undefinedcolumnerror" in message


def _normalize_text(value: str | None) -> str:
    return normalize_text(value)


def _title_tokens(value: str | None) -> set[str]:
    normalized = _normalize_text(value)
    return {
        token.strip(" \t\r\n?.!,;:()[]{}\"'")
        for token in normalized.split()
        if len(token.strip(" \t\r\n?.!,;:()[]{}\"'")) >= 3
        and token.strip(" \t\r\n?.!,;:()[]{}\"'") not in _COURSE_TITLE_STOPWORDS
    }


def _should_include_course_for_department(
    course: dict[str, Any],
    normalized_department: str,
) -> bool:
    if not normalized_department:
        return True

    course_department = _normalize_text(course.get("department"))
    if normalized_department in course_department:
        return True
    if any(marker in course_department for marker in _SHARED_CURRICULUM_DEPARTMENT_MARKERS):
        return True

    return False


def _legacy_course_select():
    """Eski sema ile de calisan minimal ders secimi."""
    return select(
        Course.id.label("id"),
        Course.course_code.label("course_code"),
        Course.course_name.label("course_name"),
        Course.credits.label("credits"),
        Course.department.label("department"),
        Course.semester.label("semester"),
        Course.instructor.label("instructor"),
    )


def _legacy_course_mapping_to_dict(course_row: Any) -> dict[str, Any]:
    """Eksik curriculum kolonlari icin guvenli varsayimlarla ders sozlugu uretir."""
    credits = int(course_row["credits"])
    return {
        "course_code": course_row["course_code"],
        "course_name": course_row["course_name"],
        "credits": credits,
        "akts": credits,
        "theory_hours": 0,
        "practice_hours": 0,
        "lab_hours": 0,
        "department": course_row["department"],
        "curriculum_semester": None,
        "course_type": "bilinmiyor",
        "elective_group": None,
        "instructor": course_row["instructor"],
    }


def _course_to_dict(course: Course) -> dict[str, Any]:
    return {
        "course_code": course.course_code,
        "course_name": course.course_name,
        "credits": course.credits,
        "akts": course.akts,
        "theory_hours": course.theory_hours,
        "practice_hours": course.practice_hours,
        "lab_hours": course.lab_hours,
        "department": course.department,
        "curriculum_semester": course.curriculum_semester,
        "course_type": course.course_type,
        "elective_group": course.elective_group,
        "instructor": course.instructor,
    }


def _course_counts_for_program_total(course: dict[str, Any]) -> bool:
    """Mezuniyet AKTS toplami icin baz mufredat derslerini sec."""
    course_type = _normalize_text(course.get("course_type"))
    course_name = _normalize_text(course.get("course_name"))
    elective_group = str(course.get("elective_group") or "").strip()

    if course_type in _PROGRAM_TOTAL_EXCLUDED_TYPES:
        return False

    if course_type in {"teknik_secmeli", "lab_secmeli"} and elective_group:
        return False

    if course_type in {"sosyal_secmeli", "universite_secmeli"}:
        return "grup" in course_name or not elective_group

    return True


def resolve_course_code(code: str) -> tuple[str, str | None]:
    """Ders kodunu cozumler. Alias varsa (guncel_kod, eski_kod) doner."""
    upper = _normalize_course_code_key(code)
    if upper in COURSE_CODE_ALIASES:
        return COURSE_CODE_ALIASES[upper], upper
    return upper, None


def _normalize_course_code_key(code: str | None) -> str:
    """Ders kodlarini Turkce harf/encoding farklarindan bagimsiz karsilastir."""
    if not code:
        return ""
    normalized = str(code).translate(_COURSE_CODE_NORMALIZE_MAP)
    normalized = normalize_text(normalized).upper().replace(" ", "")
    return "".join(ch for ch in normalized if ch.isalnum() or ch == "-")


async def _fetch_course_by_code(session: Any, course_code: str) -> Course | None:
    """Exact lookup yetmezse FIZ/FİZ gibi kod varyantlarini normalizasyonla bul."""
    stmt = select(Course).where(Course.course_code == course_code)
    course = (await session.execute(stmt)).scalar_one_or_none()
    if course is not None:
        return course

    normalized_target = _normalize_course_code_key(course_code)
    if not normalized_target:
        return None

    candidates = (await session.execute(select(Course))).scalars().all()
    for candidate in candidates:
        if _normalize_course_code_key(candidate.course_code) == normalized_target:
            return candidate
    return None


async def fetch_courses_by_semester(
    semester: str,
    department: str | None = None,
) -> list[dict[str, Any]]:
    """Belirli doneme ait aktif dersleri getirir."""
    async with get_session() as session:
        normalized_department = _normalize_text(department)
        try:
            stmt = select(Course).where(Course.semester == semester)
            stmt = stmt.order_by(Course.course_code.asc())
            courses = (await session.execute(stmt)).scalars().all()
            payload = [_course_to_dict(course) for course in courses]
            if normalized_department:
                payload = [
                    course
                    for course in payload
                    if _should_include_course_for_department(course, normalized_department)
                ]
            return payload
        except (ProgrammingError, DBAPIError) as exc:
            if not _is_missing_column_error(exc):
                raise
            await session.rollback()
            logger.warning(
                "legacy_course_schema_fallback",
                extra={"query_type": "semester", "semester": semester},
            )
            legacy_stmt = _legacy_course_select().where(Course.semester == semester)
            legacy_stmt = legacy_stmt.order_by(Course.course_code.asc())
            rows = (await session.execute(legacy_stmt)).mappings().all()
            payload = [_legacy_course_mapping_to_dict(row) for row in rows]
            if normalized_department:
                payload = [
                    course
                    for course in payload
                    if _should_include_course_for_department(course, normalized_department)
                ]
            return payload


async def fetch_courses_by_curriculum_semester(
    semester_num: int,
    department: str | None = None,
) -> list[dict[str, Any]]:
    """Mufredat yariyil numarasina (1-8) gore dersleri getirir."""
    async with get_session() as session:
        normalized_department = _normalize_text(department)
        try:
            stmt = (
                select(Course)
                .where(Course.curriculum_semester == semester_num)
                .order_by(Course.course_code.asc())
            )
            courses = (await session.execute(stmt)).scalars().all()
            payload = [_course_to_dict(course) for course in courses]
            if normalized_department:
                payload = [
                    course
                    for course in payload
                    if _should_include_course_for_department(course, normalized_department)
                ]
            return payload
        except (ProgrammingError, DBAPIError) as exc:
            if not _is_missing_column_error(exc):
                raise
            await session.rollback()
            logger.warning(
                "curriculum_semester_unavailable_in_legacy_schema",
                extra={"semester_num": semester_num},
            )
            return []


async def fetch_courses_by_title(
    query_text: str,
    department: str | None = None,
    *,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Find catalog courses whose title is explicitly mentioned in a query."""
    query_tokens = _title_tokens(query_text)
    if not query_tokens:
        return []

    async with get_session() as session:
        normalized_department = _normalize_text(department)
        try:
            courses = (await session.execute(select(Course))).scalars().all()
            payload = [_course_to_dict(course) for course in courses]
        except (ProgrammingError, DBAPIError) as exc:
            if not _is_missing_column_error(exc):
                raise
            await session.rollback()
            logger.warning("legacy_course_title_lookup")
            rows = (await session.execute(_legacy_course_select())).mappings().all()
            payload = [_legacy_course_mapping_to_dict(row) for row in rows]

    if normalized_department:
        payload = [
            course
            for course in payload
            if _should_include_course_for_department(course, normalized_department)
        ]

    ranked: list[tuple[float, dict[str, Any]]] = []
    for course in payload:
        title_tokens = _title_tokens(course.get("course_name"))
        if not title_tokens:
            continue
        overlap = query_tokens & title_tokens
        coverage = len(overlap) / max(1, len(title_tokens))
        precision = len(overlap) / max(1, len(query_tokens))
        score = (coverage * 0.7) + (precision * 0.3)
        if coverage >= 0.66 and len(overlap) >= min(2, len(title_tokens)):
            ranked.append((score, course))

    ranked.sort(
        key=lambda item: (
            -item[0],
            str(item[1].get("department") or ""),
            int(item[1].get("curriculum_semester") or 99),
            str(item[1].get("course_code") or ""),
        )
    )
    return [course for _, course in ranked[:limit]]


async def fetch_courses_by_elective_group(group_code: str) -> list[dict[str, Any]]:
    """Belirli bir secmeli grup koduna ait dersleri getirir."""
    async with get_session() as session:
        try:
            stmt = (
                select(Course)
                .where(
                    Course.elective_group == group_code,
                    Course.course_type != "secmeli_grup",
                )
                .order_by(Course.course_code.asc())
            )
            courses = (await session.execute(stmt)).scalars().all()
            return [_course_to_dict(course) for course in courses]
        except (ProgrammingError, DBAPIError) as exc:
            if not _is_missing_column_error(exc):
                raise
            await session.rollback()
            logger.warning(
                "elective_group_unavailable_in_legacy_schema",
                extra={"group_code": group_code},
            )
            return []


async def fetch_course_prerequisites(course_code: str) -> dict[str, Any] | None:
    """Ders onkosullarini getirir. Eski/alternatif kod verilirse guncel koda yonlendirir."""
    resolved_code, alias_from = resolve_course_code(course_code)

    async with get_session() as session:
        try:
            course = await _fetch_course_by_code(session, resolved_code)
            if course is None:
                return None

            prereq_stmt = (
                select(CoursePrerequisite, Course)
                .join(Course, CoursePrerequisite.prerequisite_id == Course.id)
                .where(CoursePrerequisite.course_id == course.id)
                .order_by(CoursePrerequisite.prerequisite_group)
            )
            prereq_rows = (await session.execute(prereq_stmt)).all()

            groups: dict[int, list[dict[str, Any]]] = {}
            flat_list: list[dict[str, Any]] = []
            for prereq_rel, prereq_course in prereq_rows:
                entry = {
                    "course_code": prereq_course.course_code,
                    "course_name": prereq_course.course_name,
                    "group": prereq_rel.prerequisite_group,
                }
                flat_list.append(entry)
                groups.setdefault(prereq_rel.prerequisite_group, []).append(entry)

            return {
                "course_code": course.course_code,
                "course_name": course.course_name,
                "credits": course.credits,
                "akts": course.akts,
                "prerequisites": flat_list,
                "prerequisite_groups": groups,
                "redirected_from": alias_from,
            }
        except (ProgrammingError, DBAPIError) as exc:
            if not _is_missing_column_error(exc):
                raise
            await session.rollback()
            logger.warning(
                "legacy_prerequisite_schema_fallback",
                extra={"course_code": resolved_code},
            )

            course_stmt = _legacy_course_select().where(Course.course_code == resolved_code)
            course_row = (await session.execute(course_stmt)).mappings().first()
            if course_row is None:
                normalized_target = _normalize_course_code_key(resolved_code)
                legacy_rows = (await session.execute(_legacy_course_select())).mappings().all()
                course_row = next(
                    (
                        row
                        for row in legacy_rows
                        if _normalize_course_code_key(row["course_code"]) == normalized_target
                    ),
                    None,
                )
            if course_row is None:
                return None

            prereq_stmt = (
                select(
                    Course.course_code.label("course_code"),
                    Course.course_name.label("course_name"),
                )
                .select_from(CoursePrerequisite)
                .join(Course, CoursePrerequisite.prerequisite_id == Course.id)
                .where(CoursePrerequisite.course_id == course_row["id"])
                .order_by(Course.course_code.asc())
            )
            prereq_rows = (await session.execute(prereq_stmt)).mappings().all()

            groups: dict[int, list[dict[str, Any]]] = {}
            flat_list: list[dict[str, Any]] = []
            for prereq_row in prereq_rows:
                entry = {
                    "course_code": prereq_row["course_code"],
                    "course_name": prereq_row["course_name"],
                    "group": 1,
                }
                flat_list.append(entry)
                groups.setdefault(1, []).append(entry)

            return {
                "course_code": course_row["course_code"],
                "course_name": course_row["course_name"],
                "credits": course_row["credits"],
                "akts": course_row["credits"],
                "prerequisites": flat_list,
                "prerequisite_groups": groups,
                "redirected_from": alias_from,
            }


async def fetch_program_akts_summary(department: str) -> dict[str, Any] | None:
    """Bolum/program icin baz mezuniyet AKTS ozetini getir."""
    normalized_department = _normalize_text(department)
    if not normalized_department:
        return None

    async with get_session() as session:
        try:
            stmt = (
                select(Course)
                .where(Course.curriculum_semester.is_not(None))
                .order_by(Course.curriculum_semester.asc(), Course.course_code.asc())
            )
            courses = (await session.execute(stmt)).scalars().all()
            payload = [_course_to_dict(course) for course in courses]
        except (ProgrammingError, DBAPIError) as exc:
            if not _is_missing_column_error(exc):
                raise
            await session.rollback()
            logger.warning(
                "program_akts_unavailable_in_legacy_schema",
                extra={"department": department},
            )
            return None

    filtered_courses = [
        course
        for course in payload
        if _should_include_course_for_department(course, normalized_department)
    ]
    counted_courses = [
        course for course in filtered_courses if _course_counts_for_program_total(course)
    ]
    if not counted_courses:
        return None

    semester_totals: dict[int, int] = {}
    total_akts = 0
    for course in counted_courses:
        semester = course.get("curriculum_semester")
        akts = int(course.get("akts") or course.get("credits") or 0)
        if semester is None or akts <= 0:
            continue
        semester_totals[semester] = semester_totals.get(semester, 0) + akts
        total_akts += akts

    if not semester_totals:
        return None

    return {
        "department": department,
        "normalized_department": normalized_department,
        "total_akts": total_akts,
        "semester_totals": dict(sorted(semester_totals.items())),
        "excluded_course_types": sorted(_PROGRAM_TOTAL_EXCLUDED_TYPES),
        "counted_course_count": len(counted_courses),
    }
