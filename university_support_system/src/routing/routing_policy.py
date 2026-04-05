"""Policy helpers for rule-based department routing."""

from __future__ import annotations

import re

from src.core.constants import Department, TaskType
from src.core.query_markers import ACADEMIC_DEPARTMENT_CONTEXT_MARKERS
from src.core.text_normalization import normalize_text

CAP_OR_YAP_IN_QUERY = re.compile(r"\b(?:çap|cap|yandal|yan\s+dal)\b", re.IGNORECASE)
ROUTING_PAYMENT_MARKERS: tuple[str, ...] = ("ucret", "harc", "odeme", "taksit", "dekont")
ROUTING_REGISTRATION_MARKERS: tuple[str, ...] = ("kayit", "kayd", "yenileme", "ders kaydi")
ROUTING_TIMING_MARKERS: tuple[str, ...] = ("basvuru", "ne zaman", "takvim", "tarih", "surec")
ROUTING_ACADEMIC_CONTEXT_MARKERS: tuple[str, ...] = ACADEMIC_DEPARTMENT_CONTEXT_MARKERS
ROUTING_ACADEMIC_CALENDAR_MARKERS: tuple[str, ...] = (
    "akademik takvim",
    "kayit donemi",
    "ders kaydi takvimi",
)
ROUTING_FORMAL_RULE_MARKERS: tuple[str, ...] = (
    "azami",
    "butunleme",
    "devam zorunlulugu",
    "not sistemi",
    "degerlendirme sistemi",
)
ROUTING_INTERNATIONAL_MARKERS: tuple[str, ...] = (
    "erasmus",
    "uluslararasi",
    "yabanci",
    "ikamet",
    "denklik",
    "tomer",
    "yos",
)
ROUTING_CAP_MARKERS: tuple[str, ...] = ("cap", "cift anadal", "cift ana dal", "yandal", "yan dal")
ROUTING_PERSONAL_MARKERS: tuple[str, ...] = (
    "ortalamam",
    "notlarim",
    "gno",
    "transkript",
    "borcum",
    "borcun",
    "harcim",
    "odemem",
    "bursum",
    "aliyor muyum",
    "durumum",
    "mezuniyetime",
    "dersim",
    "derslerim",
    "kredim",
    "kaldi",
    "tamamladim",
)
NORMALIZED_COURSE_CODE_IN_QUERY = re.compile(r"\b[a-z]{2,}\s?\d{3,4}\b", re.IGNORECASE)


def normalize_routing_text(text: str) -> str:
    """Normalize text for router keyword checks."""
    return normalize_text(text)


def contains_any(normalized_text: str, markers: tuple[str, ...]) -> bool:
    """Return whether normalized text includes any marker."""
    return any(marker in normalized_text for marker in markers)


def looks_like_personal_data_query(query: str) -> bool:
    """Return whether query likely asks for personal/private student data."""
    lowered = normalize_routing_text(query)
    return contains_any(lowered, ROUTING_PERSONAL_MARKERS)


def has_payment_registration_timing_overlap(normalized_text: str) -> bool:
    """Return whether query mixes payment and registration timing signals."""
    return (
        contains_any(normalized_text, ROUTING_PAYMENT_MARKERS)
        and contains_any(normalized_text, ROUTING_REGISTRATION_MARKERS)
        and contains_any(normalized_text, ROUTING_TIMING_MARKERS)
    )


def has_academic_calendar_markers(normalized_text: str) -> bool:
    """Return whether query is clearly about registration or academic calendar dates."""
    return contains_any(normalized_text, ROUTING_ACADEMIC_CALENDAR_MARKERS)


def has_cap_markers(normalized_text: str) -> bool:
    """Return whether query mentions CAP/YAP style programs."""
    return bool(CAP_OR_YAP_IN_QUERY.search(normalized_text)) or contains_any(
        normalized_text, ROUTING_CAP_MARKERS
    )


def has_formal_rule_markers(normalized_text: str) -> bool:
    """Return whether query looks like a formal academic rule/policy question."""
    return contains_any(normalized_text, ROUTING_FORMAL_RULE_MARKERS)


def has_international_markers(normalized_text: str) -> bool:
    """Return whether query is about international or Erasmus processes."""
    return contains_any(normalized_text, ROUTING_INTERNATIONAL_MARKERS)


def looks_like_personal_credit_progress_query(normalized_text: str) -> bool:
    """Return whether query asks about a student's own AKTS/kredi progress."""
    return "tamamladim" in normalized_text and (
        "akts" in normalized_text
        or "kredim" in normalized_text
        or "kredilerim" in normalized_text
    )


def should_skip_llm_for_academic_context_query(
    query: str,
    departments: list[Department],
) -> bool:
    """Return whether the query is already clearly academic-context bound."""
    if Department.ACADEMIC_PROGRAMS not in departments:
        return False
    if NORMALIZED_COURSE_CODE_IN_QUERY.search(normalize_routing_text(query)):
        return False
    lowered = normalize_routing_text(query)
    return contains_any(lowered, ROUTING_ACADEMIC_CONTEXT_MARKERS)


def detect_task_type(query: str, departments: list[Department]) -> TaskType | None:
    """Infer a coarse task type from the query and routed departments."""
    normalized_query = normalize_routing_text(query)

    if Department.FINANCE in departments:
        if "burs" in normalized_query:
            return TaskType.SCHOLARSHIP_QUERY
        if any(keyword in normalized_query for keyword in ("odeme", "harc", "dekont", "taksit", "ucret")):
            return TaskType.TUITION_QUERY
        return TaskType.PAYMENT_QUERY

    if (CAP_OR_YAP_IN_QUERY.search(normalized_query) or contains_any(normalized_query, ROUTING_CAP_MARKERS)) and Department.STUDENT_AFFAIRS in departments:
        if contains_any(normalized_query, ROUTING_TIMING_MARKERS):
            return TaskType.PROCEDURE_QUERY
        return TaskType.COURSE_QUERY

    if Department.STUDENT_AFFAIRS in departments:
        if any(keyword in normalized_query for keyword in ("kayit", "kayd", "yatay", "dikey", "muafiyet", "intibak", "takvim")):
            return TaskType.REGISTRATION_QUERY
        if any(
            keyword in normalized_query
            for keyword in (
                "not",
                "gno",
                "transkript",
                "mezuniyet",
                "diploma",
                "bagil",
                "yaz okulu",
                "akts",
                "kredi",
                "kredim",
                "kredilerim",
                "tamamladim",
            )
        ):
            return TaskType.ACADEMIC_QUERY
        return TaskType.COURSE_QUERY

    if Department.ACADEMIC_PROGRAMS in departments:
        if any(
            keyword in normalized_query
            for keyword in (
                "yonerge",
                "yonetmelik",
                "politika",
                "prosedur",
                "genelge",
                "azami",
                "butunleme",
                "devam zorunlulugu",
                "not sistemi",
                "erasmus",
                "uluslararasi",
                "ikamet",
                "denklik",
                "tomer",
                "yos",
            )
        ):
            return TaskType.PROCEDURE_QUERY
        return TaskType.COURSE_QUERY

    return None
