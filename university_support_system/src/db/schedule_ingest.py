"""Helpers for ingesting structured course schedule rows from document sources.

Current primary source types are local PDF timetable documents parsed with
``pdfplumber`` and XLSX workbooks parsed through the standard OOXML structure.
HTML/table sources can be added later with a separate adapter without changing
the database contract defined here.
"""

from __future__ import annotations

from datetime import datetime, time, timedelta
from functools import lru_cache
import json
from pathlib import Path
import re
from typing import Any, Iterable
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import pdfplumber
from sqlalchemy import delete
from sqlalchemy.orm import Session

from src.core.text_normalization import (
    collapse_whitespace,
    iter_alias_matches_longest_first,
    normalize_text,
)
from src.db.models import CourseScheduleSlot

_ACADEMIC_YEAR_RE = re.compile(r"(20\d{2})\s*[-_/]\s*(20\d{2})")
_COURSE_CODE_RE = re.compile(r"\b([A-ZÇĞİÖŞÜ]{2,6}\s*\d{3}[A-Z]?)\b", re.IGNORECASE)
_DEPARTMENT_RE = re.compile(
    r"([A-ZÇĞİÖŞÜa-zçğıöşü0-9/&.,'\- ]+?)\s+"
    r"(B[OÖ]L[UÜ]M[UÜ]|ANAB[İI]L[İI]M DALI|ABD)\b",
    re.IGNORECASE,
)
_TIME_RANGE_RE = re.compile(r"([0-9:.]{3,5})\s*[-–]\s*([0-9:.]{3,5})")
_DAY_NAMES = {
    "pazartesi": "Pazartesi",
    "pa": "Pazartesi",
    "pztsi": "Pazartesi",
    "sali": "Sali",
    "sa": "Sali",
    "carsamba": "Carsamba",
    "ca": "Carsamba",
    "car": "Carsamba",
    "persembe": "Persembe",
    "pe": "Persembe",
    "cuma": "Cuma",
    "cu": "Cuma",
    "cumartesi": "Cumartesi",
    "pazar": "Pazar",
}
_TERM_MARKERS = {
    "bahar": "bahar",
    "guz": "guz",
    "fall": "guz",
    "spring": "bahar",
}
_ROMAN_NUMERALS = {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii"}
_INSTRUCTOR_TOKEN_RE = re.compile(r"^[A-ZÇĞİÖŞÜ]{1,6}(?:/[A-ZÇĞİÖŞÜ]{1,6})*$")
_INSTRUCTOR_TITLE_RE = re.compile(r"\b(?:Prof\.?|Doç\.?|Dr\.?)\b", re.IGNORECASE)
_CLASSROOM_TOKEN_RE = re.compile(
    r"^(?:[A-ZÇĞİÖŞÜ]{0,5}\d{1,4}[A-Z]?|[A-ZÇĞİÖŞÜ]{1,6}-\d{1,4}[A-Z]?|[A-ZÇĞİÖŞÜ]+-L\d+|[A-ZÇĞİÖŞÜ.]+L|L\d+|D\d+|F\d+|MBG-L\d+|ORG\.KIM\.L)$",
    re.IGNORECASE,
)
_PROGRAM_SECTION_RE = re.compile(
    r"^(?:[A-ZÇĞİÖŞÜ]{1,5}\d{0,2})(?:/(?:[A-ZÇĞİÖŞÜ]{1,5}\d{0,2}))*$",
    re.IGNORECASE,
)

_MAX_SCHEDULE_TEXT_LENGTH = 180
_WEEKLY_SCHEDULE_MARKERS = (
    "haftalik ders programi",
    "haftalik program",
    "ders programi",
)
_NON_WEEKLY_PROGRAM_MARKERS = (
    "lisans programi",
    "yuksek lisans programi",
    "yüksek lisans programi",
    "doktora programi",
    "programi course type",
    "type of course",
    "dersin kodu",
    "course type of course name",
)
_XLSX_NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
_SCHEDULE_SOURCE_OVERRIDES_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "metadata" / "schedule_source_overrides.json"
)
_COURSE_NAME_MARKERS = (
    "akademik",
    "arastirma",
    "armoni",
    "asa",
    "baski",
    "bilisim",
    "bati",
    "desen",
    "ders",
    "egitim",
    "felsefe",
    "fotograf",
    "grafik",
    "heykel",
    "koro",
    "muz",
    "muzik",
    "muze",
    "okul",
    "ork",
    "ogret",
    "perspektif",
    "resim",
    "sanat",
    "sec",
    "seramik",
    "sinif",
    "tas",
    "tasarim",
    "teori",
    "temel",
    "thm",
    "tarih",
    "tsm",
    "turk",
    "uyg",
    "yabanci",
    "yonet",
)
_INVALID_DEPARTMENT_MARKERS = (
    "ders program",
    "xlsx",
    "pdf",
    "docx",
    "guncel",
    "gununcel",
    "derstir",
    "bu ders",
    "bilinmiyor",
)
_FILENAME_DEPARTMENT_STOPWORDS = {
    "2022", "2023", "2024", "2025", "2026", "20", "21", "22", "23", "24", "25", "26",
    "bahar", "guz", "donemi", "yariyili", "egitim", "ogretim", "yili",
    "ders", "program", "programi", "haftalik", "lisans", "lisansustu",
    "guncel", "yeni", "son", "r0", "docx", "xlsx", "pdf", "abd",
}
_FILENAME_DEPARTMENT_ALIASES = {
    "okl": "Okul Oncesi Ogretmenligi",
    "sinif egt": "Sinif Ogretmenligi",
    "sinif egitimi": "Sinif Ogretmenligi",
    "ilkmat": "Matematik Ogretmenligi",
    "mat": "Matematik Ogretmenligi",
    "fizik": "Fizik",
    "biyoloji": "Biyoloji Egitimi",
    "fen": "Fen Bilgisi Ogretmenligi",
}


@lru_cache(maxsize=1)
def _load_schedule_source_overrides() -> dict[str, dict[str, Any]]:
    if not _SCHEDULE_SOURCE_OVERRIDES_PATH.exists():
        return {}

    with _SCHEDULE_SOURCE_OVERRIDES_PATH.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)

    sources = raw.get("sources", raw) if isinstance(raw, dict) else {}
    if not isinstance(sources, dict):
        return {}

    overrides: dict[str, dict[str, Any]] = {}
    for source_name, value in sources.items():
        if isinstance(source_name, str) and isinstance(value, dict):
            overrides[source_name] = value
    return overrides


def _source_override_for(path: Path) -> dict[str, Any]:
    overrides = _load_schedule_source_overrides()
    return overrides.get(path.name) or overrides.get(path.stem) or {}


def _merge_source_override(
    path: Path,
    *,
    academic_year: str | None,
    term: str | None,
    department: str | None,
    source_url: str | None,
) -> tuple[str | None, str | None, str | None, str | None, bool]:
    override = _source_override_for(path)
    skip = bool(override.get("skip"))
    return (
        academic_year if academic_year is not None else override.get("academic_year"),
        term if term is not None else override.get("term"),
        department if department is not None else override.get("department"),
        source_url if source_url is not None else override.get("source_url"),
        skip,
    )


def _clean_cell(value: object | None) -> str:
    if value is None:
        return ""
    lines = [collapse_whitespace(line) for line in str(value).splitlines()]
    cleaned_lines: list[str] = []
    for line in lines:
        if not line:
            continue
        if cleaned_lines and cleaned_lines[-1] == line:
            continue
        cleaned_lines.append(line)
    return collapse_whitespace(" ".join(cleaned_lines))


def _cell_lines(value: object | None) -> list[str]:
    if value is None:
        return []
    raw_lines = [collapse_whitespace(line) for line in str(value).splitlines()]
    lines: list[str] = []
    for line in raw_lines:
        if not line:
            continue
        if lines and lines[-1] == line:
            continue
        lines.append(line)
    return lines


def _normalize_day_label(value: object | None) -> str | None:
    text = _clean_cell(value)
    if not text:
        return None

    normalized = normalize_text(text)
    compact = re.sub(r"[^a-z]", "", normalized)
    if compact in _DAY_NAMES:
        return _DAY_NAMES[compact]

    reversed_compact = compact[::-1]
    if reversed_compact in _DAY_NAMES:
        return _DAY_NAMES[reversed_compact]

    return None


def _is_day_only_text(value: object | None) -> bool:
    text = _clean_cell(value)
    if not text:
        return False
    normalized = normalize_text(text)
    compact = re.sub(r"[^a-z]", "", normalized)
    return compact in _DAY_NAMES or compact[::-1] in _DAY_NAMES


def _parse_time_component(value: str) -> time | None:
    cleaned = collapse_whitespace(value).replace(".", ":")
    if not cleaned:
        return None

    if ":" in cleaned:
        parts = cleaned.split(":")
        if len(parts) != 2 or not all(part.isdigit() for part in parts):
            return None
        hour = int(parts[0])
        minute = int(parts[1])
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return time(hour=hour, minute=minute)
        return None

    digits = re.sub(r"\D", "", cleaned)
    if len(digits) == 3:
        hour = int(digits[0])
        minute = int(digits[1:])
    elif len(digits) == 4:
        hour = int(digits[:2])
        minute = int(digits[2:])
    else:
        return None

    if 0 <= hour <= 23 and 0 <= minute <= 59:
        return time(hour=hour, minute=minute)
    return None


def _parse_time_range(value: object | None) -> tuple[time, time] | None:
    text = _clean_cell(value)
    if not text:
        return None

    match = _TIME_RANGE_RE.search(text)
    if not match:
        return None

    start = _parse_time_component(match.group(1))
    end = _parse_time_component(match.group(2))
    if start is None or end is None:
        return None
    return start, end


def _default_end_time(start: time) -> time:
    anchor = datetime(2000, 1, 1, start.hour, start.minute) + timedelta(minutes=45)
    return anchor.time()


def _parse_time_cell_with_optional_next(
    current_value: object | None,
    next_value: object | None = None,
) -> tuple[time, time] | None:
    parsed_range = _parse_time_range(current_value)
    if parsed_range is not None:
        return parsed_range

    start_text = _clean_cell(current_value)
    start_time = _parse_time_component(start_text)
    if start_time is None:
        return None

    next_range = _parse_time_range(next_value)
    if next_range is not None:
        return start_time, next_range[0]

    next_text = _clean_cell(next_value)
    next_start = _parse_time_component(next_text)
    if next_start is not None:
        return start_time, next_start

    return start_time, _default_end_time(start_time)


def _looks_like_instructor(token: str) -> bool:
    normalized = normalize_text(token)
    if len(normalized) > 12:
        return False
    if normalized in _ROMAN_NUMERALS:
        return False
    return bool(_INSTRUCTOR_TOKEN_RE.match(token))


def _looks_like_classroom(token: str) -> bool:
    return bool(_CLASSROOM_TOKEN_RE.match(token))


def _looks_like_program_section(token: str) -> bool:
    return bool(_PROGRAM_SECTION_RE.match(token))


def _canonical_course_key(course_code: str | None, course_name: str | None) -> str | None:
    basis = collapse_whitespace(course_code or course_name)
    normalized = normalize_text(basis)
    return normalized or None


def _looks_like_composite_schedule_text(value: str) -> bool:
    normalized = normalize_text(value)
    if not normalized:
        return False

    if normalized.count("ofis") >= 2:
        return True

    classroom_hits = sum(1 for token in value.split() if _looks_like_classroom(token))
    if classroom_hits >= 3:
        return True

    return False


def _extract_course_fields(
    course_text: object | None,
    *,
    classroom: object | None = None,
    instructor: object | None = None,
) -> dict[str, str | None] | None:
    text = _clean_cell(course_text)
    if not text:
        return None

    normalized = normalize_text(text)
    if "ogle arasi" in normalized or "oglearasi" in normalized:
        return None

    classroom_text = _clean_cell(classroom) or None
    instructor_text = _clean_cell(instructor) or None

    if instructor_text is None and " / " in text:
        prefix, suffix = text.rsplit(" / ", 1)
        if any(marker in normalize_text(suffix) for marker in ("prof", "doc", "dr", "ogrt", "ogr")):
            text = collapse_whitespace(prefix)
            instructor_text = collapse_whitespace(suffix)
    if instructor_text is None:
        title_match = _INSTRUCTOR_TITLE_RE.search(text)
        if title_match and title_match.start() > 0:
            prefix = collapse_whitespace(text[: title_match.start()])
            suffix = collapse_whitespace(text[title_match.start() :])
            if prefix and suffix:
                text = prefix
                instructor_text = suffix

    tokens = text.split()
    if classroom_text is None and tokens and _looks_like_classroom(tokens[-1]):
        classroom_text = tokens.pop()
    if instructor_text is None and tokens and _looks_like_instructor(tokens[-1]):
        instructor_text = tokens.pop()
    text = collapse_whitespace(" ".join(tokens))

    course_code: str | None = None
    code_match = _COURSE_CODE_RE.search(text)
    if code_match:
        course_code = collapse_whitespace(code_match.group(1)).replace(" ", "")
        text = collapse_whitespace(text.replace(code_match.group(0), " "))

    course_name = text or None
    if course_name is None and course_code:
        course_name = course_code

    course_key = _canonical_course_key(course_code, course_name)
    if course_key is None:
        return None
    if course_name and (
        len(course_name) > _MAX_SCHEDULE_TEXT_LENGTH
        or _looks_like_composite_schedule_text(course_name)
    ):
        return None
    if len(course_key) > _MAX_SCHEDULE_TEXT_LENGTH:
        return None

    return {
        "course_code": course_code,
        "course_key": course_key,
        "course_name": course_name,
        "classroom": classroom_text,
        "instructor": instructor_text,
    }


def _extract_course_fields_from_multiline_cell(
    value: object | None,
) -> tuple[dict[str, str | None] | None, str | None]:
    lines = _cell_lines(value)
    if not lines:
        return None, None
    if len(lines) == 1 and _is_day_only_text(lines[0]):
        return None, None

    section_text: str | None = None
    if _looks_like_program_section(lines[0]):
        section_text = lines.pop(0)

    classroom_text: str | None = None
    instructor_text: str | None = None

    if lines:
        tail_tokens = lines[-1].split()
        if tail_tokens:
            leading_token = tail_tokens[0]
            looks_like_course_code = bool(_COURSE_CODE_RE.fullmatch(leading_token))
            if _looks_like_classroom(leading_token) and not looks_like_course_code:
                classroom_text = tail_tokens[0]
                trailing = collapse_whitespace(" ".join(tail_tokens[1:]))
                instructor_text = trailing or None
                lines.pop()
            elif _INSTRUCTOR_TITLE_RE.search(lines[-1]):
                instructor_text = lines.pop()

    course_text = "\n".join(lines)
    return (
        _extract_course_fields(
            course_text,
            classroom=classroom_text,
            instructor=instructor_text,
        ),
        section_text,
    )


def _extract_course_fields_from_loose_matrix_cell(
    value: object | None,
) -> dict[str, str | None] | None:
    text = _clean_cell(value).strip()
    if not text or text in {'"', "'", "-"}:
        return None
    if len(text) <= 2:
        return None

    fields = _extract_course_fields(text)
    if fields is None:
        return None
    if fields["course_code"]:
        return fields

    normalized = normalize_text(fields["course_name"] or text)
    if any(marker in normalized for marker in _COURSE_NAME_MARKERS):
        return fields
    return None


def _trim_department_candidate(candidate: str) -> str:
    cleaned = collapse_whitespace(candidate).strip(" -_/")
    split_pattern = re.compile(
        r"universitesi|üniversitesi|fakultesi|fakültesi|enstitusu|enstitüsü|"
        r"yuksekokulu|yüksekokulu|meslek yuksekokulu|meslek yüksekokulu",
        re.IGNORECASE,
    )
    while True:
        parts = split_pattern.split(cleaned, maxsplit=1)
        if len(parts) == 1:
            break
        cleaned = parts[-1].strip(" -_/")
    return cleaned


def _looks_like_plausible_department(value: str | None) -> bool:
    """Reject filename fragments and explanatory sentences as department names."""
    cleaned = collapse_whitespace(value)
    if not cleaned or len(cleaned) < 3 or len(cleaned) > 120:
        return False

    normalized = normalize_text(cleaned)
    if any(marker in normalized for marker in _INVALID_DEPARTMENT_MARKERS):
        return False
    if "_" in cleaned or "\\" in cleaned or "/" in cleaned:
        return False
    if "." in cleaned and not any(marker in normalized for marker in ("ogretmenligi", "muhendisligi")):
        return False

    alpha_count = sum(1 for char in normalized if char.isalpha())
    digit_count = sum(1 for char in normalized if char.isdigit())
    if alpha_count < 3:
        return False
    if digit_count and digit_count >= alpha_count:
        return False
    if re.search(r"\d{3,}", normalized):
        return False

    return True


def _infer_department_from_filename(path: Path) -> str | None:
    """Extract a plausible department phrase from descriptive schedule filenames."""
    normalized = normalize_text(path.stem)
    normalized = re.sub(r"[_\-.]+", " ", normalized)
    normalized = re.sub(r"\b20\d{2}\b", " ", normalized)
    normalized = re.sub(r"\b\d{2}\d{2}\b", " ", normalized)
    normalized = re.sub(r"\b\d{2}_?\d{2}\b", " ", normalized)
    tokens = [
        token
        for token in normalized.split()
        if token and token not in _FILENAME_DEPARTMENT_STOPWORDS and not token.isdigit()
    ]
    if not tokens:
        return None

    phrase = " ".join(tokens)
    alias_groups = (
        (replacement, (marker,))
        for marker, replacement in _FILENAME_DEPARTMENT_ALIASES.items()
    )
    for replacement, marker in iter_alias_matches_longest_first(alias_groups):
        marker_tokens = marker.split()
        if marker_tokens == tokens[: len(marker_tokens)] or marker in phrase and len(tokens) > 1:
            return replacement
    if len(tokens) == 1 and not any(
        suffix in tokens[0] for suffix in ("muhendisligi", "ogretmenligi")
    ):
        return None

    if any(marker in phrase for marker in ("muhendisligi", "ogretmenligi", "istatistik", "fizik", "kimya")):
        return " ".join(token.capitalize() for token in tokens)
    return None


def infer_schedule_context(
    pdf_path: Path,
    preview_text: str,
    *,
    academic_year: str | None = None,
    term: str | None = None,
    department: str | None = None,
) -> dict[str, str]:
    base_text = f"{pdf_path.stem} {preview_text}"

    resolved_academic_year = academic_year
    if resolved_academic_year is None:
        match = _ACADEMIC_YEAR_RE.search(base_text)
        if match:
            resolved_academic_year = f"{match.group(1)}-{match.group(2)}"
        else:
            resolved_academic_year = "bilinmiyor"

    resolved_term = term
    if resolved_term is None:
        normalized_base = normalize_text(base_text)
        term_alias_groups = (
            (term_name, (marker,))
            for marker, term_name in _TERM_MARKERS.items()
        )
        resolved_term = next(
            (
                term_name
                for term_name, marker in iter_alias_matches_longest_first(term_alias_groups)
                if marker in normalized_base
            ),
            "bilinmiyor",
        )

    resolved_department = department
    department_was_explicit = department is not None
    if resolved_department is None:
        match = _DEPARTMENT_RE.search(preview_text)
        if match:
            resolved_department = _trim_department_candidate(match.group(1))
        else:
            title_match = re.search(
                r"(.+?)\s+(?:haftalik|haftalık)\s+ders\s+programi",
                preview_text,
                re.IGNORECASE,
            )
            if title_match:
                resolved_department = _trim_department_candidate(title_match.group(1))
            else:
                resolved_department = _infer_department_from_filename(pdf_path) or collapse_whitespace(pdf_path.stem)
    if not department_was_explicit and not _looks_like_plausible_department(resolved_department):
        resolved_department = "bilinmiyor"

    return {
        "academic_year": collapse_whitespace(resolved_academic_year),
        "term": collapse_whitespace(resolved_term),
        "department": collapse_whitespace(resolved_department),
    }


def classify_schedule_document(source_name: str, preview_text: str) -> str:
    """Classify a schedule-corpus document for ingest/index decisions.

    Returns one of:
    - ``weekly_schedule``: looks like a real weekly timetable
    - ``non_weekly_program``: looks like catalog/curriculum/program listing
    - ``unknown``
    """
    normalized = normalize_text(f"{source_name} {preview_text}")
    has_day_signal = any(day in normalized for day in ("pazartesi", "sali", "carsamba", "persembe", "cuma"))
    has_time_signal = bool(_TIME_RANGE_RE.search(preview_text)) or bool(
        re.search(r"\b(?:8|9|10|11|12|13|14|15|16|17)[.:]\d{2}\b", preview_text)
    )
    if any(marker in normalized for marker in _NON_WEEKLY_PROGRAM_MARKERS) and not (has_day_signal and has_time_signal):
        return "non_weekly_program"
    if any(marker in normalized for marker in _WEEKLY_SCHEDULE_MARKERS) and (has_day_signal or has_time_signal):
        return "weekly_schedule"
    if has_day_signal and has_time_signal:
        return "weekly_schedule"
    return "unknown"


def _build_slot(
    context: dict[str, str],
    course_fields: dict[str, str | None],
    *,
    day_of_week: str,
    start_time: time,
    end_time: time,
    source_document: str,
    source_url: str | None,
    schedule_group: str | None = None,
    section: str | None = None,
) -> dict[str, Any]:
    return {
        "academic_year": context["academic_year"],
        "term": context["term"],
        "department": context["department"],
        "course_code": course_fields["course_code"],
        "course_key": course_fields["course_key"],
        "course_name": course_fields["course_name"],
        "schedule_group": collapse_whitespace(schedule_group),
        "section": collapse_whitespace(section),
        "day_of_week": day_of_week,
        "start_time": start_time,
        "end_time": end_time,
        "classroom": course_fields["classroom"],
        "instructor": course_fields["instructor"],
        "source_document": source_document,
        "source_url": source_url,
        "is_active": True,
    }


def _first_row_with_time(table: list[list[object | None]], time_col: int) -> int | None:
    for index, row in enumerate(table):
        if time_col < len(row) and _parse_time_range(row[time_col]):
            return index
    return None


def _parse_explicit_schedule_table(
    table: list[list[object | None]],
    context: dict[str, str],
    source_document: str,
    source_url: str | None,
) -> list[dict[str, Any]]:
    header_index: int | None = None
    header_map: dict[str, int] = {}
    for index, row in enumerate(table[:4]):
        normalized_cells = [normalize_text(cell) for cell in row]
        for cell_index, cell in enumerate(normalized_cells):
            if cell == "gun":
                header_map["day"] = cell_index
            elif cell == "saat":
                header_map["time"] = cell_index
            elif "ders kodu" in cell:
                header_map["course_code"] = cell_index
            elif "ders adi" in cell or cell == "ders":
                header_map["course_name"] = cell_index
            elif "ogretim uyesi" in cell:
                header_map["instructor"] = cell_index
        if "day" in header_map and "time" in header_map:
            header_index = index
            break

    if header_index is None:
        return []

    slots: list[dict[str, Any]] = []
    current_instructor: str | None = None
    for row in table[header_index + 1 :]:
        if not row:
            continue
        day = _normalize_day_label(row[header_map["day"]]) if header_map["day"] < len(row) else None
        times = _parse_time_range(row[header_map["time"]]) if header_map["time"] < len(row) else None
        if day is None or times is None:
            continue

        instructor_value = row[header_map["instructor"]] if "instructor" in header_map and header_map["instructor"] < len(row) else None
        instructor_text = _clean_cell(instructor_value)
        if instructor_text:
            current_instructor = instructor_text

        course_fields = _extract_course_fields(
            row[header_map["course_name"]] if "course_name" in header_map and header_map["course_name"] < len(row) else None,
            classroom=None,
            instructor=current_instructor,
        )
        if course_fields is None and "course_code" in header_map and header_map["course_code"] < len(row):
            code_value = _clean_cell(row[header_map["course_code"]])
            if code_value:
                course_fields = _extract_course_fields(code_value, instructor=current_instructor)

        if course_fields is None:
            continue

        if "course_code" in header_map and not course_fields["course_code"] and header_map["course_code"] < len(row):
            code_text = _clean_cell(row[header_map["course_code"]])
            if code_text:
                course_fields["course_code"] = code_text.replace(" ", "")
                course_fields["course_key"] = _canonical_course_key(course_fields["course_code"], course_fields["course_name"])

        slots.append(
            _build_slot(
                context,
                course_fields,
                day_of_week=day,
                start_time=times[0],
                end_time=times[1],
                source_document=source_document,
                source_url=source_url,
            )
        )

    return slots


def _parse_grouped_weekly_table(
    table: list[list[object | None]],
    context: dict[str, str],
    source_document: str,
    source_url: str | None,
) -> list[dict[str, Any]]:
    if len(table) < 3 or len(table[0]) < 9:
        return []

    header_text = " ".join(_clean_cell(cell) for cell in table[0][:4])
    if "saat" not in normalize_text(header_text):
        return []

    row_width = len(table[0])
    if row_width < 9 or (row_width - 3) % 3 != 0:
        return []

    group_columns: list[tuple[int, str | None]] = []
    for start in range(3, row_width, 3):
        group_columns.append((start, _clean_cell(table[0][start]) or None))

    first_data_row = _first_row_with_time(table, 2)
    if first_data_row is None:
        return []

    slots: list[dict[str, Any]] = []
    current_day: str | None = None
    for row in table[first_data_row:]:
        if len(row) < 3:
            continue
        day = _normalize_day_label(row[0])
        if day:
            current_day = day
        times = _parse_time_range(row[2])
        if current_day is None or times is None:
            continue

        for start_index, group_label in group_columns:
            course_fields = _extract_course_fields(
                row[start_index] if start_index < len(row) else None,
                classroom=row[start_index + 1] if start_index + 1 < len(row) else None,
                instructor=row[start_index + 2] if start_index + 2 < len(row) else None,
            )
            if course_fields is None:
                continue

            slots.append(
                _build_slot(
                    context,
                    course_fields,
                    day_of_week=current_day,
                    start_time=times[0],
                    end_time=times[1],
                    source_document=source_document,
                    source_url=source_url,
                    schedule_group=group_label,
                )
            )

    return slots


def _parse_single_column_grouped_weekly_table(
    table: list[list[object | None]],
    context: dict[str, str],
    source_document: str,
    source_url: str | None,
) -> list[dict[str, Any]]:
    if len(table) < 3 or len(table[0]) < 6 or len(table[0]) > 10:
        return []

    data_start = None
    for index, row in enumerate(table):
        if len(row) > 1 and _parse_time_cell_with_optional_next(row[1]):
            data_start = index
            break
    if data_start is None:
        return []

    group_labels = ["1.SINIF", "2.SINIF", "3.SINIF", "4.SINIF"]
    slots: list[dict[str, Any]] = []
    current_day: str | None = None
    for row_index in range(data_start, len(table)):
        row = table[row_index]
        if len(row) < 6:
            continue
        day = _normalize_day_label(row[0])
        if day:
            current_day = day
        times = _parse_time_cell_with_optional_next(
            row[1],
            table[row_index + 1][1] if row_index + 1 < len(table) and len(table[row_index + 1]) > 1 else None,
        )
        if current_day is None or times is None:
            continue

        for cell_index, group_label in zip(range(2, 6), group_labels, strict=False):
            course_fields, section_text = _extract_course_fields_from_multiline_cell(
                row[cell_index] if cell_index < len(row) else None
            )
            if course_fields is None:
                continue
            slots.append(
                _build_slot(
                    context,
                    course_fields,
                    day_of_week=current_day,
                    start_time=times[0],
                    end_time=times[1],
                    source_document=source_document,
                    source_url=source_url,
                    schedule_group=group_label,
                    section=section_text,
                )
            )

    return slots


def _parse_two_column_grouped_weekly_table(
    table: list[list[object | None]],
    context: dict[str, str],
    source_document: str,
    source_url: str | None,
) -> list[dict[str, Any]]:
    if len(table) < 3 or len(table[0]) < 8:
        return []

    header_row_index: int | None = None
    for index, row in enumerate(table[:4]):
        sinif_hits = sum(1 for cell in row if "sinif" in normalize_text(cell))
        if sinif_hits >= 2:
            header_row_index = index
            break

    if header_row_index is None:
        return []

    first_data_row = _first_row_with_time(table, 1)
    if first_data_row is None:
        return []

    header_row = table[header_row_index]
    group_columns: list[tuple[int, str | None]] = []
    for start in range(2, len(header_row), 2):
        group_label = _clean_cell(header_row[start]) if start < len(header_row) else None
        group_columns.append((start, group_label or None))

    slots: list[dict[str, Any]] = []
    current_day: str | None = None
    start_row_index = max(first_data_row, header_row_index + 1)
    for row_index in range(start_row_index, len(table)):
        row = table[row_index]
        if len(row) < 2:
            continue
        day = _normalize_day_label(row[0])
        if day:
            current_day = day
        times = _parse_time_cell_with_optional_next(
            row[1],
            table[row_index + 1][1] if row_index + 1 < len(table) and len(table[row_index + 1]) > 1 else None,
        )
        if current_day is None or times is None:
            continue

        for start_index, group_label in group_columns:
            course_fields = _extract_course_fields(
                row[start_index] if start_index < len(row) else None,
                classroom=row[start_index + 1] if start_index + 1 < len(row) else None,
            )
            if course_fields is None:
                continue

            slots.append(
                _build_slot(
                    context,
                    course_fields,
                    day_of_week=current_day,
                    start_time=times[0],
                    end_time=times[1],
                    source_document=source_document,
                    source_url=source_url,
                    schedule_group=group_label,
                )
            )

    return slots


def _parse_row_day_time_matrix_table(
    table: list[list[object | None]],
    context: dict[str, str],
    source_document: str,
    source_url: str | None,
) -> list[dict[str, Any]]:
    if len(table) < 2 or len(table[0]) < 3:
        return []
    if len(table[0]) > 1 and "sinif" in normalize_text(table[0][1]):
        return []

    header_times: dict[int, tuple[time, time]] = {}
    for index in range(1, len(table[0])):
        parsed = _parse_time_range(table[0][index])
        if parsed is not None:
            header_times[index] = parsed
    if len(header_times) < 2:
        return []

    slots: list[dict[str, Any]] = []
    for row in table[1:]:
        if not row:
            continue
        day = _normalize_day_label(row[0])
        if day is None:
            continue
        for cell_index, times in header_times.items():
            if cell_index >= len(row):
                continue
            course_fields, section_text = _extract_course_fields_from_multiline_cell(row[cell_index])
            if course_fields is None:
                continue
            slots.append(
                _build_slot(
                    context,
                    course_fields,
                    day_of_week=day,
                    start_time=times[0],
                    end_time=times[1],
                    source_document=source_document,
                    source_url=source_url,
                    section=section_text,
                )
            )

    return slots


def _parse_row_day_matrix_table(
    table: list[list[object | None]],
    context: dict[str, str],
    source_document: str,
    source_url: str | None,
) -> list[dict[str, Any]]:
    if not table or len(table[0]) < 4:
        return []

    header_row = table[0]
    if normalize_text(header_row[0]) != "gun":
        return []

    has_group_column = "sinif" in normalize_text(header_row[1]) if len(header_row) > 1 else False
    time_start_index = 2 if has_group_column else 1
    header_times: dict[int, tuple[time, time]] = {}
    for index in range(time_start_index, len(header_row)):
        parsed = _parse_time_range(header_row[index])
        if parsed is not None:
            header_times[index] = parsed

    if len(header_times) < 2:
        return []

    slots: list[dict[str, Any]] = []
    current_day: str | None = None
    for row in table[1:]:
        if not row:
            continue
        day = _normalize_day_label(row[0])
        if day:
            current_day = day
        if current_day is None:
            continue

        group_label = _clean_cell(row[1]) if has_group_column and len(row) > 1 else None
        for cell_index, times in header_times.items():
            if cell_index >= len(row):
                continue
            course_fields, section_text = _extract_course_fields_from_multiline_cell(row[cell_index])
            if course_fields is None:
                continue
            slots.append(
                _build_slot(
                    context,
                    course_fields,
                    day_of_week=current_day,
                    start_time=times[0],
                    end_time=times[1],
                    source_document=source_document,
                    source_url=source_url,
                    schedule_group=group_label,
                    section=section_text,
                )
            )

    return slots


def _parse_wide_day_time_matrix_table(
    table: list[list[object | None]],
    context: dict[str, str],
    source_document: str,
    source_url: str | None,
) -> list[dict[str, Any]]:
    if len(table) < 3 or len(table[0]) < 6:
        return []

    header_row_index: int | None = None
    for index, row in enumerate(table[:4]):
        first_cell = normalize_text(row[0]) if row else ""
        compact_header = re.sub(
            r"[^a-z]",
            "",
            normalize_text(" ".join(_clean_cell(cell) for cell in row)),
        )
        if first_cell.startswith("gunler") or first_cell.startswith("gun ") or "sinif" in compact_header:
            header_row_index = index
            break
    if header_row_index is None:
        return []

    first_data_row = _first_row_with_time(table, 1)
    if first_data_row is None:
        return []

    group_by_column: dict[int, str | None] = {}
    current_group: str | None = None
    for cell_index, cell in enumerate(table[header_row_index]):
        label = _clean_cell(cell)
        compact_label = re.sub(r"[^a-z]", "", normalize_text(label))
        if "sinif" in compact_label:
            current_group = label
        if cell_index >= 2:
            group_by_column[cell_index] = current_group

    slots: list[dict[str, Any]] = []
    current_day: str | None = None
    for row in table[max(first_data_row, header_row_index + 1) :]:
        if len(row) < 2:
            continue
        day = _normalize_day_label(row[0])
        if day:
            current_day = day
        times = _parse_time_cell_with_optional_next(row[1])
        if current_day is None or times is None:
            continue

        for cell_index in range(2, len(row)):
            course_fields = _extract_course_fields_from_loose_matrix_cell(row[cell_index])
            if course_fields is None:
                continue
            slots.append(
                _build_slot(
                    context,
                    course_fields,
                    day_of_week=current_day,
                    start_time=times[0],
                    end_time=times[1],
                    source_document=source_document,
                    source_url=source_url,
                    schedule_group=group_by_column.get(cell_index),
                )
            )

    return slots


def _parse_column_day_matrix_table(
    table: list[list[object | None]],
    context: dict[str, str],
    source_document: str,
    source_url: str | None,
) -> list[dict[str, Any]]:
    if not table or len(table[0]) < 4:
        return []

    header_days: dict[int, str] = {}
    for index in range(1, len(table[0])):
        day = _normalize_day_label(table[0][index])
        if day:
            header_days[index] = day

    if len(header_days) < 2:
        return []

    slots: list[dict[str, Any]] = []
    current_time: tuple[time, time] | None = None
    for row_index in range(1, len(table)):
        row = table[row_index]
        if not row:
            continue
        parsed_time = _parse_time_cell_with_optional_next(
            row[0] if row else None,
            table[row_index + 1][0] if row_index + 1 < len(table) and table[row_index + 1] else None,
        )
        if parsed_time is not None:
            current_time = parsed_time
        if current_time is None:
            continue

        for cell_index, day in header_days.items():
            if cell_index >= len(row):
                continue
            course_fields, section_text = _extract_course_fields_from_multiline_cell(row[cell_index])
            if course_fields is None:
                continue
            slots.append(
                _build_slot(
                    context,
                    course_fields,
                    day_of_week=day,
                    start_time=current_time[0],
                    end_time=current_time[1],
                    source_document=source_document,
                    source_url=source_url,
                    section=section_text,
                )
            )

    return slots


def parse_schedule_table(
    table: list[list[object | None]],
    context: dict[str, str],
    *,
    source_document: str,
    source_url: str | None = None,
) -> list[dict[str, Any]]:
    for parser in (
        _parse_explicit_schedule_table,
        _parse_grouped_weekly_table,
        _parse_two_column_grouped_weekly_table,
        _parse_single_column_grouped_weekly_table,
        _parse_wide_day_time_matrix_table,
        _parse_row_day_time_matrix_table,
        _parse_row_day_matrix_table,
        _parse_column_day_matrix_table,
    ):
        slots = parser(table, context, source_document, source_url)
        if slots:
            return slots
    return []


def parse_schedule_slots_from_pdf(
    pdf_path: Path,
    *,
    academic_year: str | None = None,
    term: str | None = None,
    department: str | None = None,
    source_url: str | None = None,
) -> list[dict[str, Any]]:
    with pdfplumber.open(pdf_path) as pdf:
        preview_pages = pdf.pages[:2]
        preview_text = "\n".join(page.extract_text() or "" for page in preview_pages)
        context = infer_schedule_context(
            pdf_path,
            preview_text,
            academic_year=academic_year,
            term=term,
            department=department,
        )
        if context["department"] == "bilinmiyor":
            return []

        parsed_slots: list[dict[str, Any]] = []
        for page in pdf.pages:
            for table in page.extract_tables() or []:
                parsed_slots.extend(
                    parse_schedule_table(
                        table,
                        context,
                        source_document=pdf_path.name,
                        source_url=source_url,
                    )
                )

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


def _xlsx_column_index(cell_ref: str) -> int:
    match = re.match(r"([A-Z]+)", cell_ref)
    if match is None:
        return 0
    index = 0
    for char in match.group(1):
        index = index * 26 + ord(char) - ord("A") + 1
    return index - 1


def _read_xlsx_shared_strings(workbook: ZipFile) -> list[str]:
    try:
        shared_xml = workbook.read("xl/sharedStrings.xml")
    except KeyError:
        return []

    root = ET.fromstring(shared_xml)
    strings: list[str] = []
    for item in root.findall("x:si", _XLSX_NS):
        strings.append("".join(text.text or "" for text in item.findall(".//x:t", _XLSX_NS)))
    return strings


def _xlsx_cell_value(cell: ET.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    value = cell.find("x:v", _XLSX_NS)
    if value is None:
        inline = cell.find("x:is", _XLSX_NS)
        if inline is None:
            return ""
        return "".join(text.text or "" for text in inline.findall(".//x:t", _XLSX_NS))

    raw_value = value.text or ""
    if cell_type == "s":
        try:
            return shared_strings[int(raw_value)]
        except (ValueError, IndexError):
            return raw_value
    return raw_value


def _read_xlsx_tables(xlsx_path: Path) -> list[list[list[object | None]]]:
    tables: list[list[list[object | None]]] = []
    with ZipFile(xlsx_path) as workbook:
        shared_strings = _read_xlsx_shared_strings(workbook)
        sheet_names = sorted(
            name
            for name in workbook.namelist()
            if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")
        )

        for sheet_name in sheet_names:
            root = ET.fromstring(workbook.read(sheet_name))
            rows: list[list[object | None]] = []
            for row in root.findall(".//x:sheetData/x:row", _XLSX_NS):
                row_values: dict[int, str] = {}
                for cell in row.findall("x:c", _XLSX_NS):
                    cell_ref = cell.attrib.get("r", "")
                    row_values[_xlsx_column_index(cell_ref)] = _xlsx_cell_value(cell, shared_strings)
                if not row_values:
                    continue
                width = max(row_values) + 1
                rows.append([row_values.get(index, "") for index in range(width)])
            if rows:
                max_width = max(len(row) for row in rows)
                tables.append([row + [""] * (max_width - len(row)) for row in rows])
    return tables


def parse_schedule_slots_from_xlsx(
    xlsx_path: Path,
    *,
    academic_year: str | None = None,
    term: str | None = None,
    department: str | None = None,
    source_url: str | None = None,
) -> list[dict[str, Any]]:
    tables = _read_xlsx_tables(xlsx_path)
    preview_text = "\n".join(
        " ".join(_clean_cell(cell) for cell in row if _clean_cell(cell))
        for table in tables[:2]
        for row in table[:8]
    )
    context = infer_schedule_context(
        xlsx_path,
        preview_text,
        academic_year=academic_year,
        term=term,
        department=department,
    )
    if context["department"] == "bilinmiyor":
        return []

    parsed_slots: list[dict[str, Any]] = []
    for table in tables:
        parsed_slots.extend(
            parse_schedule_table(
                table,
                context,
                source_document=xlsx_path.name,
                source_url=source_url,
            )
        )

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


def collect_schedule_slots_from_path(
    source: Path,
    *,
    academic_year: str | None = None,
    term: str | None = None,
    department: str | None = None,
    source_url: str | None = None,
) -> dict[Path, list[dict[str, Any]]]:
    if source.is_file():
        files = [source]
    else:
        files = sorted([*source.glob("*.pdf"), *source.glob("*.xlsx")])
    collected: dict[Path, list[dict[str, Any]]] = {}
    for path in files:
        resolved_academic_year, resolved_term, resolved_department, resolved_source_url, skip = (
            _merge_source_override(
                path,
                academic_year=academic_year,
                term=term,
                department=department,
                source_url=source_url,
            )
        )
        if skip:
            collected[path] = []
            continue

        if path.suffix.lower() == ".xlsx":
            slots = parse_schedule_slots_from_xlsx(
                path,
                academic_year=resolved_academic_year,
                term=resolved_term,
                department=resolved_department,
                source_url=resolved_source_url,
            )
        else:
            slots = parse_schedule_slots_from_pdf(
                path,
                academic_year=resolved_academic_year,
                term=resolved_term,
                department=resolved_department,
                source_url=resolved_source_url,
            )
        collected[path] = slots
    return collected


def replace_schedule_slots_for_sources(
    session: Session,
    slots_by_source: dict[Path, list[dict[str, Any]]],
) -> dict[str, int]:
    inserted = 0
    for source_path, slots in slots_by_source.items():
        session.execute(
            delete(CourseScheduleSlot).where(
                CourseScheduleSlot.source_document == source_path.name
            )
        )
        for slot in slots:
            session.add(CourseScheduleSlot(**slot))
        inserted += len(slots)
    return {
        "sources": len(slots_by_source),
        "rows": inserted,
    }


def summarize_schedule_slots(slots_by_source: dict[Path, list[dict[str, Any]]]) -> dict[str, Any]:
    return {
        "sources": len(slots_by_source),
        "rows": sum(len(rows) for rows in slots_by_source.values()),
        "non_empty_sources": sum(1 for rows in slots_by_source.values() if rows),
        "empty_sources": [path.name for path, rows in slots_by_source.items() if not rows],
    }
