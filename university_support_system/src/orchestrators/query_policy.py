"""Query policy helpers for the main orchestrator."""

from __future__ import annotations

import re

from src.core.constants import Department, TaskType
from src.core.query_markers import (
    ACADEMIC_DEPARTMENT_CONTEXT_MARKERS,
    ANNOUNCEMENT_QUERY_MARKERS,
    GLOBAL_SYNTHESIS_QUERY_MARKERS,
)
from src.core.text_normalization import contains_any_normalized, normalize_text
from src.db.schemas import DepartmentResponse

CLARIFICATION_MESSAGE = (
    "Sorunuzun hangi alana ait oldugunu net olarak belirleyemedim. "
    "Asagidaki seceneklerden birini belirterek tekrar sorabilirsiniz:\n"
    "- Ogrenci Isleri (kayit, not, staj, mezuniyet)\n"
    "- Akademik Programlar (mufredat, yonetmelik, Erasmus)\n"
    "- Finans (harc, burs, odeme)"
)

ACADEMIC_DEPARTMENT_CLARIFICATION_MESSAGE = (
    "Bu soruyu dogru cevaplayabilmem icin once bolum veya program bilgisini bilmem gerekiyor. "
    "Ornegin soyle sorabilirsiniz:\n"
    '- "Bilgisayar Muhendisligi icin 1. yariyil dersleri nelerdir?"\n'
    '- "Kimya bolumu teknik secmeli dersleri hangileri?"\n'
    "Kisisel ders/AKTS ilerlemesi ogrenmek istiyorsan OTP ile giris yapabilirsin; "
    "boylece bolum bilgin oturumdan otomatik kullanilir."
)

COURSE_CODE_PATTERN = re.compile(r"\b[A-ZÇĞİÖŞÜ]{2,6}\s?\d{3,4}\b", re.IGNORECASE)


def augment_query_for_department(
    department: Department,
    query: str,
    metadata: dict,
) -> str:
    """Inject department-specific context into the query when needed."""
    student_department = (metadata.get("student_department") or "").strip()
    student_faculty = (metadata.get("student_faculty") or "").strip()
    student_type = (metadata.get("student_type") or "").strip()
    if department != Department.ACADEMIC_PROGRAMS or not student_department:
        augmented = query
    else:
        lowered_query = normalize_text(query)
        lowered_department = normalize_text(student_department)
        if lowered_department in lowered_query:
            augmented = query
        else:
            faculty_prefix = f"{student_faculty} / " if student_faculty else ""
            augmented = f"{faculty_prefix}{student_department} bolumu/programi icin: {query}"

    if department != Department.FINANCE:
        return augmented

    lowered_augmented = normalize_text(augmented)
    student_type_prefix = ""
    if student_type and normalize_text(student_type) not in lowered_augmented:
        suffix = " baglami icin: " if "ogrenci" in normalize_text(student_type) else " ogrenci baglami icin: "
        student_type_prefix = f"{student_type}{suffix}"

    faculty_prefix = ""
    fee_markers = ("ucret", "harc", "odeme", "katki payi")
    if student_faculty and any(marker in lowered_augmented for marker in fee_markers):
        if normalize_text(student_faculty) not in lowered_augmented:
            faculty_prefix = f"{student_faculty} icin: "

    return f"{student_type_prefix}{faculty_prefix}{augmented}".strip()


def requires_academic_department_clarification(
    *,
    query: str,
    departments: list[Department],
    task_type: TaskType | None,
    student_department: str | None,
) -> bool:
    """Return whether academic department information must be clarified."""
    if student_department:
        return False
    if Department.ACADEMIC_PROGRAMS not in departments:
        return False
    if task_type not in {TaskType.COURSE_QUERY, None}:
        return False

    lowered = normalize_text(query)
    has_explicit_program_signal = any(keyword in lowered for keyword in ("bolumu", "anabilim dali"))
    has_explicit_course_code = COURSE_CODE_PATTERN.search(query) is not None
    if has_explicit_program_signal or has_explicit_course_code:
        return False

    return contains_any_normalized(lowered, ACADEMIC_DEPARTMENT_CONTEXT_MARKERS)


def looks_like_announcement_query(query: str) -> bool:
    """Return whether the query primarily targets announcements."""
    return contains_any_normalized(query, ANNOUNCEMENT_QUERY_MARKERS)


def personalize_answer(answer: str, full_name: str | None) -> str:
    """Add a first-name prefix when a profile is available."""
    if not full_name or not answer:
        return answer
    first_name = (full_name.split() or [full_name])[0]
    return f"{first_name}, {answer}"


def query_prefers_global_synthesis(query: str) -> bool:
    """Return whether the query likely benefits from a combined LLM synthesis."""
    return contains_any_normalized(query, GLOBAL_SYNTHESIS_QUERY_MARKERS)


def should_disable_specialist_llm(
    *,
    query: str,
    orchestrator_count: int,
) -> bool:
    """Disable per-specialist synthesis when a later global synthesis is preferred."""
    return orchestrator_count > 1 and query_prefers_global_synthesis(query)


def should_use_global_synthesis(*, query: str, responses: list[DepartmentResponse]) -> bool:
    """Return whether final answer composition should use global synthesis."""
    meaningful = [response for response in responses if response.answer.strip() and response.success]
    departments = {response.department for response in meaningful}
    if len(departments) < 2:
        return False
    if not any(response.sources or response.db_data for response in meaningful):
        return False
    return query_prefers_global_synthesis(query)
