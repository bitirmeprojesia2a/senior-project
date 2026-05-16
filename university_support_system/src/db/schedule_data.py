"""Structured course schedule queries for future hybrid timetable answers."""

from __future__ import annotations

from datetime import datetime
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
_WEEKDAY_DISPLAY = {
    "pazartesi": "Pazartesi",
    "sali": "Salı",
    "carsamba": "Çarşamba",
    "persembe": "Perşembe",
    "cuma": "Cuma",
    "cumartesi": "Cumartesi",
    "pazar": "Pazar",
}
_SCHEDULE_TEXT_REPLACEMENTS = {
    "Muhendisligi": "Mühendisliği",
    "Muh.": "Müh.",
    "Egitimi": "Eğitimi",
    "Sinif": "Sınıf",
    "sinif": "sınıf",
    "Ogretim Elemani": "Öğretim Elemanı",
}
_COURSE_NAME_TRANSLATIONS = {
    "Computer Programming (Lab)": "Bilgisayar Programlama (Lab)",
    "Computer Programming": "Bilgisayar Programlama",
    "Fundamentals of Electrical Engineering (Lab)": "Elektrik Mühendisliği Temelleri (Lab)",
    "Fundamentals of Electrical Engineering": "Elektrik Mühendisliği Temelleri",
    "Electronics II A (Lab)": "Elektronik II A (Lab)",
    "Electronics II B (Lab)": "Elektronik II B (Lab)",
    "Advanced Programming (Lab)": "İleri Programlama (Lab)",
    "Advanced Programming": "İleri Programlama",
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


def normalize_schedule_rows_for_answer(
    rows: list[dict[str, Any]],
    *,
    query_text: str | None = None,
    default_term_key: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Normalize schedule rows for deterministic user-facing answers.

    Generic program schedule answers should show the current undergraduate
    weekly schedule.  Graduate/blank "other" buckets are kept only when the
    user explicitly asks for them.
    """
    if not rows:
        return [], {
            "schema": "omu.schedule_filter.v1",
            "term_context": None,
            "excluded_rows": 0,
            "explicit_other_scope": False,
        }

    query = normalize_text(query_text or "")
    explicit_other_scope = _explicit_other_schedule_scope(query)
    term_key = _extract_schedule_term_key(query)
    if term_key is None and _has_multiple_schedule_terms(rows):
        term_key = default_term_key or _default_schedule_term_key()

    term_rows = rows
    if term_key:
        matching_rows = [
            row for row in rows
            if _schedule_term_key(row.get("term")) == term_key
        ]
        if matching_rows:
            term_rows = matching_rows

    normalized_rows = [_normalize_schedule_row(row) for row in term_rows]
    if not explicit_other_scope:
        undergrad_rows = [
            row for row in normalized_rows
            if _schedule_row_level(row) == "undergraduate"
        ]
        if undergrad_rows:
            normalized_rows = undergrad_rows
        else:
            normalized_rows = [
                row for row in normalized_rows
                if _schedule_row_level(row) != "graduate"
            ]

    normalized_rows.sort(key=schedule_row_sort_key)
    return normalized_rows, {
        "schema": "omu.schedule_filter.v1",
        "term_context": _schedule_term_context(normalized_rows),
        "requested_term": term_key,
        "excluded_rows": max(0, len(rows) - len(normalized_rows)),
        "explicit_other_scope": explicit_other_scope,
    }


def schedule_group_sort_key(group: str | None) -> tuple[int, str]:
    normalized = normalize_text(group or "")
    match = re.search(r"\b([1-4])\s*\.?\s*sinif\b", normalized)
    if match:
        return int(match.group(1)), normalized
    if "belirtilmeyen" in normalized:
        return 90, normalized
    return 80, normalized


def format_schedule_day(value: Any) -> str:
    """Return a Turkish display label for schedule weekday values."""
    raw = str(value or "").strip()
    return _WEEKDAY_DISPLAY.get(normalize_text(raw), raw)


def format_schedule_group(value: Any) -> str:
    """Return a Turkish display label for schedule class/group values."""
    text = str(value or "").strip()
    if not text:
        return ""
    normalized = normalize_text(text)
    match = re.search(r"\b([1-4])\s*\.?\s*sinif\b", normalized)
    if match:
        return f"{int(match.group(1))}. Sınıf"
    return format_schedule_label(text)


def format_schedule_label(value: Any) -> str:
    """Naturalize common ASCII schedule labels without changing DB identity."""
    text = str(value or "").strip()
    for broken, fixed in _SCHEDULE_TEXT_REPLACEMENTS.items():
        text = text.replace(broken, fixed)
    return text


def format_schedule_course_name(value: Any) -> str:
    """Clean and naturalize course names for user-facing schedule answers."""
    text = _clean_schedule_course_name(str(value or ""))
    return _COURSE_NAME_TRANSLATIONS.get(text, text)


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


def _normalize_schedule_row(row: dict[str, Any]) -> dict[str, Any]:
    cleaned = dict(row)
    derived_group = _derive_schedule_group(cleaned)
    if derived_group:
        cleaned["schedule_group"] = derived_group
    cleaned["course_name"] = _clean_schedule_course_name(
        str(cleaned.get("course_name") or cleaned.get("name") or "")
    )
    return cleaned


def _derive_schedule_group(row: dict[str, Any]) -> str | None:
    raw_group = str(row.get("schedule_group") or "").strip()
    if raw_group and normalize_text(raw_group) not in {"diger", "other"}:
        return raw_group
    section = normalize_text(row.get("section") or "")
    match = re.search(r"\b(?:fzk|fizik|sinif)?\s*([1-4])\b", section)
    if match:
        return f"{int(match.group(1))}. Sinif"
    code = normalize_text(row.get("course_code") or row.get("course_key") or "")
    code_match = re.search(r"\b[a-z]{2,6}\s*([1-4])\d{2}\b", code)
    if code_match:
        return f"{int(code_match.group(1))}. Sinif"
    return None


def _schedule_row_level(row: dict[str, Any]) -> str:
    haystack = normalize_text(
        " ".join(
            str(row.get(key) or "")
            for key in (
                "source_document",
                "department",
                "course_name",
                "course_code",
                "course_key",
                "schedule_group",
                "section",
            )
        )
    )
    if any(marker in haystack for marker in ("yuksek lisans", "lisansustu", "doktora", "uzmanlik alan dersi")):
        return "graduate"
    if schedule_group_sort_key(str(row.get("schedule_group") or ""))[0] in {1, 2, 3, 4}:
        return "undergraduate"
    if "lisans" in haystack and "lisansustu" not in haystack:
        return "undergraduate"
    return "unknown"


def _clean_schedule_course_name(value: str) -> str:
    text = " ".join(str(value or "").split())
    if text in _COURSE_NAME_TRANSLATIONS:
        return _COURSE_NAME_TRANSLATIONS[text]
    replacements = {
        "Öğretmen lik": "Öğretmenlik",
        "Ogretmen lik": "Ogretmenlik",
        "Uygula ması": "Uygulaması",
        "Uygula masi": "Uygulamasi",
        "Kaynaştır ma": "Kaynaştırma",
        "Kaynastir ma": "Kaynastirma",
        "Öğretimin de": "Öğretiminde",
        "Ogretimin de": "Ogretiminde",
    }
    for broken, fixed in replacements.items():
        text = text.replace(broken, fixed)
    return text


def _explicit_other_schedule_scope(normalized_query: str) -> bool:
    return any(
        marker in normalized_query
        for marker in (
            "lisansustu",
            "yuksek lisans",
            "doktora",
            "uzmanlik",
            "diger dersler",
            "tum dersler",
            "tum gruplar",
        )
    )


def _has_multiple_schedule_terms(rows: list[dict[str, Any]]) -> bool:
    terms = {
        (
            str(row.get("academic_year") or "").strip(),
            _schedule_term_key(row.get("term")),
        )
        for row in rows
        if row.get("term") or row.get("academic_year")
    }
    return len(terms) > 1


def _extract_schedule_term_key(normalized_query: str) -> str | None:
    semester_match = re.search(r"\b([1-8])\s*\.?\s*(?:yariyil|donem)\b", normalized_query)
    if semester_match is not None:
        semester = int(semester_match.group(1))
        return "guz" if semester % 2 == 1 else "bahar"
    if any(marker in normalized_query for marker in ("bahar", "ikinci donem", "2 donem", "ikinci yariyil", "2 yariyil")):
        return "bahar"
    if any(marker in normalized_query for marker in ("guz", "ilk donem", "birinci donem", "1 donem", "ilk yariyil", "birinci yariyil", "1 yariyil")):
        return "guz"
    return None


def _default_schedule_term_key() -> str:
    month = datetime.now().month
    if 2 <= month <= 7:
        return "bahar"
    return "guz"


def _schedule_term_key(raw_term: Any) -> str:
    normalized = normalize_text(raw_term or "")
    if "bahar" in normalized:
        return "bahar"
    if "guz" in normalized:
        return "guz"
    return normalized


def _schedule_term_context(rows: list[dict[str, Any]]) -> str | None:
    contexts: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for row in rows:
        academic_year = str(row.get("academic_year") or "").strip()
        term = str(row.get("term") or "").strip()
        if not academic_year and not term:
            continue
        key = (academic_year, term)
        if key in seen:
            continue
        seen.add(key)
        contexts.append(key)
    if len(contexts) != 1:
        return None
    academic_year, term = contexts[0]
    if academic_year and term:
        return f"{academic_year} {term}"
    return academic_year or term


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
