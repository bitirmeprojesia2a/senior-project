"""Helpers for exporting curriculum and prerequisite data from UBYS pages."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from html import unescape
import json
import time
import re
from typing import Any
from urllib.parse import parse_qs, urlparse

import httpx


UBYS_BASE_URL = "https://ubys.omu.edu.tr"

TOKEN_RE = re.compile(
    r'<form id="__AjaxAntiForgeryForm"[^>]*>.*?<input name="__RequestVerificationToken" type="hidden" value="([^"]+)"',
    re.DOTALL,
)
TAG_RE = re.compile(r"<[^>]+>")
COURSE_CODE_RE = re.compile(r"\b[A-Z]{2,}[A-Z0-9-]*\s?\d{3,}\b")
PRECONDITION_LABEL_RE = re.compile(r"(Ön\s*Koşullar|On\s*Kosullar|Preconditions)", re.IGNORECASE)
PRECONDITION_PANEL_RE = re.compile(r"(Ön\s*/\s*Yan\s*Koşullar|On\s*/\s*Yan\s*Kosullar)", re.IGNORECASE)

COURSE_TYPE_REQUIRED = "zorunlu"
COURSE_TYPE_ELECTIVE = "secmeli"
COURSE_TYPE_UNIVERSITY_ELECTIVE = "sosyal_secmeli"
COURSE_TYPE_INTEGRATED = "entegre"

POOL_TYPE_DEPARTMENT_ELECTIVE = 15901
POOL_TYPE_UNIVERSITY_ELECTIVE = 15902
INTEGRATED_COURSE_TYPE = 12308


@dataclass(slots=True)
class UbysProgramRecord:
    academic_program_id: int
    curriculum_id: int
    encrypted_academic_program_id: str
    encrypted_curriculum_id: str
    full_program_name: str
    education_qualification_degree: int | None


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def strip_tags(value: str) -> str:
    return normalize_whitespace(unescape(TAG_RE.sub(" ", value)))


def normalize_course_code_key(value: str | None) -> str:
    """Normalize course-code filters across Turkish casing and mojibake variants."""
    if not value:
        return ""
    normalized = normalize_whitespace(str(value)).replace(" ", "").upper()
    try:
        normalized = normalized.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    normalized = normalized.replace("İ", "I").replace("İ", "I")
    return re.sub(r"[^A-Z0-9-]", "", normalized)


def extract_token(page_html: str) -> str:
    match = TOKEN_RE.search(page_html)
    if not match:
        raise ValueError("UBYS anti-forgery token could not be found on the page.")
    return match.group(1)


def extract_encrypted_program_id(page_url: str) -> str:
    parsed = urlparse(page_url)
    query = parse_qs(parsed.query)
    program_id = (query.get("id") or query.get("apIdStr") or [None])[0]
    if not program_id:
        raise ValueError("UBYS URL must include an 'id' or 'apIdStr' query parameter.")
    return program_id


def infer_department_name(full_program_name: str) -> str:
    normalized = normalize_whitespace(full_program_name)
    if " / " in normalized:
        return normalized.rsplit(" / ", 1)[-1]
    if " - " in normalized:
        return normalized.rsplit(" - ", 1)[-1]
    return normalized


def _department_slot_prefix(department_name: str) -> str:
    normalized = normalize_whitespace(department_name)
    words = re.findall(r"[A-Za-z0-9]+", normalized)
    if len(words) >= 2:
        prefix = "".join(word[0] for word in words[:4]).upper()
    elif words:
        prefix = words[0][:6].upper()
    else:
        prefix = "DEPT"
    return prefix[:6] or "DEPT"


def _build_program_slot_record(
    *,
    department: str,
    semester_no: int | None,
    slot_name: str,
    elective_group: str | None,
    credits: int,
    akts: int,
) -> dict[str, Any]:
    semester_token = str(semester_no or 0)
    slot_code = f"{_department_slot_prefix(department)}-SS-{semester_token}"
    if elective_group:
        suffix = re.sub(r"[^A-Za-z0-9]", "", elective_group.upper())[:6]
        if suffix:
            slot_code = f"{slot_code[:13]}-{suffix}"[:20]

    return {
        "slot_code": slot_code,
        "slot_name": slot_name,
        "department": department,
        "credits": credits,
        "akts": akts,
        "curriculum_semester": semester_no,
        "course_type": "secmeli_grup",
        "elective_group": elective_group,
    }


def find_program_record(
    records: list[dict[str, Any]],
    encrypted_program_id: str,
) -> UbysProgramRecord:
    for row in records:
        if row.get("EncryptedAcademicProgramId") != encrypted_program_id:
            continue
        curriculum_id = row.get("CurriculumId")
        encrypted_curriculum_id = row.get("EncryptedCurriculumId")
        academic_program_id = row.get("AcademicProgramId") or row.get("Id")
        if not curriculum_id or not encrypted_curriculum_id or not academic_program_id:
            raise ValueError("UBYS program record is missing curriculum identifiers.")
        return UbysProgramRecord(
            academic_program_id=int(academic_program_id),
            curriculum_id=int(curriculum_id),
            encrypted_academic_program_id=str(row["EncryptedAcademicProgramId"]),
            encrypted_curriculum_id=str(encrypted_curriculum_id),
            full_program_name=str(
                row.get("FullAcademicProgramName") or row.get("Name") or encrypted_program_id
            ),
            education_qualification_degree=(
                int(row["EducationQualificatinDegree"])
                if row.get("EducationQualificatinDegree") is not None
                else None
            ),
        )
    raise ValueError(f"UBYS program tree does not contain program id '{encrypted_program_id}'.")


def _is_meaningful_course(course: dict[str, Any] | None) -> bool:
    return bool(course and course.get("Code") and course.get("Name") and course.get("EncryptedId"))


def _map_pool_course_type(pool_type: int | None) -> str:
    if pool_type == POOL_TYPE_UNIVERSITY_ELECTIVE:
        return COURSE_TYPE_UNIVERSITY_ELECTIVE
    return COURSE_TYPE_ELECTIVE


def _safe_int(value: Any) -> int:
    if value in (None, ""):
        return 0
    return int(float(value))


def _build_course_record(
    *,
    course: dict[str, Any],
    department: str,
    semester_no: int | None,
    course_type: str,
    elective_group: str | None,
) -> dict[str, Any]:
    return {
        "course_code": str(course["Code"]).strip().upper(),
        "course_name": normalize_whitespace(str(course["Name"])),
        "department": department,
        "theory_hours": _safe_int(course.get("TheoreticalCredit")),
        "practice_hours": _safe_int(course.get("PractiseCredit")),
        "lab_hours": _safe_int(course.get("LaboratoryCredit")),
        "credits": _safe_int(course.get("Credit")),
        "akts": _safe_int(course.get("Ects")),
        "curriculum_semester": int(semester_no) if semester_no is not None else None,
        "course_type": course_type,
        "elective_group": elective_group,
    }


def build_curriculum_payload(
    curriculum_response: dict[str, Any],
    *,
    department_name: str,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    curriculum_details = curriculum_response.get("CurriculumDetails") or []
    if not curriculum_details:
        raise ValueError("UBYS curriculum response does not contain any curriculum details.")

    curriculum = curriculum_details[0]
    courses_by_code: dict[str, dict[str, Any]] = {}
    course_lookup: dict[str, dict[str, Any]] = {}
    program_slots: list[dict[str, Any]] = []
    seen_program_slots: set[str] = set()

    for row in curriculum.get("CurriculumCources") or []:
        semester_no = row.get("SemesterNo")
        course = row.get("Course")
        if _is_meaningful_course(course):
            course_type = COURSE_TYPE_REQUIRED
            if int(course.get("CourseType") or 0) == INTEGRATED_COURSE_TYPE:
                course_type = COURSE_TYPE_INTEGRATED
            record = _build_course_record(
                course=course,
                department=department_name,
                semester_no=semester_no,
                course_type=course_type,
                elective_group=None,
            )
            courses_by_code[record["course_code"]] = record
            course_lookup[record["course_code"]] = {
                "course_id": str(course["EncryptedId"]),
                "is_elective": False,
                "is_integrated": int(course.get("CourseType") or 0) == INTEGRATED_COURSE_TYPE,
            }

        pool = row.get("ElectivePool")
        if not pool:
            continue

        pool_code = normalize_whitespace(str(pool.get("Code") or pool.get("Name") or "")).strip() or None
        pool_type = _map_pool_course_type(pool.get("ElectivePoolType"))
        if pool_type == COURSE_TYPE_UNIVERSITY_ELECTIVE:
            slot = _build_program_slot_record(
                department=department_name,
                semester_no=semester_no,
                slot_name=normalize_whitespace(str(pool.get("Name") or "Sosyal Secmeli Ders (Grup)")),
                elective_group=pool_code,
                credits=_safe_int(pool.get("Credit")) or 2,
                akts=_safe_int(pool.get("Ects")) or 2,
            )
            slot_key = str(slot["slot_code"])
            if slot_key not in seen_program_slots:
                seen_program_slots.add(slot_key)
                program_slots.append(slot)
        for pool_course in pool.get("ElectivePoolCourses") or []:
            if not _is_meaningful_course(pool_course):
                continue
            record = _build_course_record(
                course=pool_course,
                department=department_name,
                semester_no=semester_no,
                course_type=pool_type,
                elective_group=pool_code,
            )
            code = record["course_code"]
            courses_by_code.setdefault(code, record)
            course_lookup.setdefault(
                code,
                {
                    "course_id": str(pool_course["EncryptedId"]),
                    "is_elective": True,
                    "is_integrated": False,
                },
            )

    payload = {
        "department": department_name,
        "courses": sorted(
            courses_by_code.values(),
            key=lambda item: (
                item.get("curriculum_semester") or 999,
                item["course_code"],
            ),
        ),
        "program_slots": sorted(
            program_slots,
            key=lambda item: (
                item.get("curriculum_semester") or 999,
                item["slot_code"],
            ),
        ),
        "prerequisites": [],
    }
    return payload, course_lookup


def _find_summary_prerequisite_text(detail_html: str) -> str:
    normalized_html = detail_html.replace("\r", "")
    row_match = re.search(
        r"<th[^>]*class=\"td-baslik\"[^>]*>\s*(?:Ön\s*Koşullar|On\s*Kosullar|Preconditions)\s*</th>\s*"
        r"<td[^>]*>.*?</td>\s*<td[^>]*>(.*?)</td>",
        normalized_html,
        re.DOTALL | re.IGNORECASE,
    )
    if not row_match:
        return ""
    return strip_tags(row_match.group(1))


def _extract_panel_rows(detail_html: str) -> list[list[str]]:
    panel_match = re.search(
        r"<div class=\"col-md-6\">(?:Ön\s*/\s*Yan\s*Koşullar|On\s*/\s*Yan\s*Kosullar)</div>.*?<tbody>(.*?)</tbody>",
        detail_html.replace("\r", ""),
        re.DOTALL | re.IGNORECASE,
    )
    if not panel_match:
        return []

    rows: list[list[str]] = []
    for row_html in re.findall(r"<tr>(.*?)</tr>", panel_match.group(1), re.DOTALL | re.IGNORECASE):
        columns = [strip_tags(col) for col in re.findall(r"<td[^>]*>(.*?)</td>", row_html, re.DOTALL | re.IGNORECASE)]
        if columns:
            rows.append(columns)
    return rows


def parse_prerequisites_from_course_detail(detail_html: str) -> list[dict[str, Any]]:
    prerequisite_entries: list[dict[str, Any]] = []

    for row in _extract_panel_rows(detail_html):
        if len(row) < 3:
            continue
        code = normalize_whitespace(row[0]).replace(" ", "")
        course_name = normalize_whitespace(row[1]) if len(row) >= 2 else ""
        condition = normalize_whitespace(row[2]).casefold()
        if not code:
            continue
        if "yan" in condition or "co" in condition:
            continue
        if "ön" in condition or "on" in condition or "pre" in condition or "kosul" in condition:
            prerequisite_entries.append(
                {
                    "course_code": code.upper(),
                    "course_name": course_name or None,
                    "group": 1,
                }
            )

    if not prerequisite_entries:
        summary = _find_summary_prerequisite_text(detail_html)
        if summary and summary.casefold() not in {"yok", "-", "none"}:
            prerequisite_entries.extend(
                {
                    "course_code": code.upper().replace(" ", ""),
                    "course_name": None,
                    "group": 1,
                }
                for code in COURSE_CODE_RE.findall(summary)
            )

    seen: set[str] = set()
    unique_entries: list[dict[str, Any]] = []
    for entry in prerequisite_entries:
        code = entry["course_code"]
        if code in seen:
            continue
        seen.add(code)
        unique_entries.append(entry)

    return unique_entries


class UbysCurriculumClient:
    """Small UBYS client for curriculum export flows."""

    def __init__(self, *, timeout: float = 30.0) -> None:
        self._client = httpx.Client(base_url=UBYS_BASE_URL, follow_redirects=True, timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "UbysCurriculumClient":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def fetch_program_page(self, page_url: str) -> tuple[str, str]:
        response = self._client.get(page_url)
        response.raise_for_status()
        return response.text, extract_token(response.text)

    def fetch_program_tree(self, token: str) -> list[dict[str, Any]]:
        response = self._client.post(
            "/AIS/Common/Helper/GetUnitProgramDataSource",
            headers={"x-RequestVerificationToken": token},
            json={
                "criter": {
                    "DontUsePrivilage": True,
                    "GetOnlyActiveForBologna": True,
                    "ShowOnlyUnitSingleProgram": True,
                }
            },
        )
        response.raise_for_status()
        return response.json()

    def fetch_curriculum_detail(self, token: str, program: UbysProgramRecord) -> dict[str, Any]:
        response = self._client.post(
            "/AIS/OutcomeBasedLearning/Home/SearchCurriculumDetail",
            headers={"x-RequestVerificationToken": token},
            json={
                "apid": program.academic_program_id,
                "apIdStr": program.encrypted_academic_program_id,
                "curId": program.curriculum_id,
                "curIdStr": program.encrypted_curriculum_id,
            },
        )
        response.raise_for_status()
        return response.json()

    def fetch_course_detail(
        self,
        *,
        program: UbysProgramRecord,
        course_id: str,
        is_elective: bool,
        is_integrated: bool,
    ) -> str:
        response = httpx.get(
            f"{UBYS_BASE_URL}/AIS/OutcomeBasedLearning/Home/CourseDetail",
            params={
                "isElectiveCourse": "true" if is_elective else "false",
                "isIntegratedCourse": "true" if is_integrated else "false",
                "courseId": course_id,
                "curriculumId": program.encrypted_curriculum_id,
                "apid": program.encrypted_academic_program_id,
                "eqd": program.education_qualification_degree,
                "progName": program.full_program_name,
            },
            follow_redirects=True,
            timeout=self._client.timeout,
        )
        response.raise_for_status()
        return response.text


def _fetch_course_prerequisites(
    *,
    program: UbysProgramRecord,
    course_code: str,
    course_id: str,
    is_elective: bool,
    is_integrated: bool,
    timeout: float,
) -> tuple[str, list[dict[str, Any]]]:
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            response = httpx.get(
                f"{UBYS_BASE_URL}/AIS/OutcomeBasedLearning/Home/CourseDetail",
                params={
                    "isElectiveCourse": "true" if is_elective else "false",
                    "isIntegratedCourse": "true" if is_integrated else "false",
                    "courseId": course_id,
                    "curriculumId": program.encrypted_curriculum_id,
                    "apid": program.encrypted_academic_program_id,
                    "eqd": program.education_qualification_degree,
                    "progName": program.full_program_name,
                },
                follow_redirects=True,
                timeout=timeout,
            )
            response.raise_for_status()
            return course_code, parse_prerequisites_from_course_detail(response.text)
        except Exception as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(0.5 * (attempt + 1))
    assert last_error is not None
    raise last_error



def export_curriculum_from_ubys(
    page_url: str,
    *,
    department_name: str | None = None,
    include_prerequisites: bool = True,
    prerequisite_course_codes: set[str] | None = None,
    max_prerequisite_courses: int | None = None,
) -> dict[str, Any]:
    encrypted_program_id = extract_encrypted_program_id(page_url)
    with UbysCurriculumClient() as client:
        program_page_html, token = client.fetch_program_page(page_url)
        program_tree = client.fetch_program_tree(token)
        program = find_program_record(program_tree, encrypted_program_id)
        curriculum_response = client.fetch_curriculum_detail(token, program)

        payload, course_lookup = build_curriculum_payload(
            curriculum_response,
            department_name=department_name or infer_department_name(program.full_program_name),
        )

        if include_prerequisites:
            prerequisite_rows: list[dict[str, Any]] = []
            attempted_codes: list[str] = []
            failed_codes: list[str] = []
            tasks: list[dict[str, Any]] = []
            filter_codes = (
                {
                    normalize_course_code_key(code)
                    for code in prerequisite_course_codes or set()
                    if normalize_course_code_key(code)
                }
                or None
            )
            for course in payload["courses"]:
                lookup = course_lookup.get(course["course_code"])
                if lookup:
                    if filter_codes and normalize_course_code_key(course["course_code"]) not in filter_codes:
                        continue
                    tasks.append(
                        {
                            "course_code": course["course_code"],
                            "course_id": lookup["course_id"],
                            "is_elective": bool(lookup["is_elective"]),
                            "is_integrated": bool(lookup["is_integrated"]),
                        }
                    )
            if max_prerequisite_courses is not None and max_prerequisite_courses > 0:
                tasks = tasks[:max_prerequisite_courses]

            max_workers = min(6, max(1, len(tasks)))
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_task = {
                    executor.submit(
                        _fetch_course_prerequisites,
                        program=program,
                        course_code=task["course_code"],
                        course_id=task["course_id"],
                        is_elective=task["is_elective"],
                        is_integrated=task["is_integrated"],
                        timeout=12.0,
                    ): task
                    for task in tasks
                }
                for future in as_completed(future_to_task):
                    try:
                        course_code, prerequisites = future.result()
                    except Exception:
                        failed_codes.append(future_to_task[future]["course_code"])
                        continue
                    attempted_codes.append(course_code)
                    if prerequisites:
                        prerequisite_rows.append(
                            {
                                "course_code": course_code,
                                "prerequisites": prerequisites,
                            }
                        )

            prerequisite_rows.sort(key=lambda item: item["course_code"])
            payload["prerequisites"] = prerequisite_rows
            payload["prerequisite_attempted_courses"] = sorted(set(attempted_codes))
            payload["prerequisite_failed_courses"] = sorted(set(failed_codes))

        # program_page_html is intentionally fetched to preserve the same cookie/token flow.
        _ = program_page_html
        return payload


def dump_payload(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)
