"""Policy helpers for rule-based department routing."""

from __future__ import annotations

import re

from src.core.constants import Department, TaskType
from src.core.query_markers import ACADEMIC_DEPARTMENT_CONTEXT_MARKERS
from src.core.text_normalization import normalize_text

CAP_OR_YAP_IN_QUERY = re.compile(r"\b(?:çap|cap|yandal|yan\s+dal)\b", re.IGNORECASE)
ROUTING_PAYMENT_MARKERS: tuple[str, ...] = (
    "ucret", "harc", "odeme", "taksit", "dekont",
    "katki payi", "borc", "borclu", "iade", "fazla ucret",
    "ogrenim ucreti", "banka", "havale", "tahsilat",
)
ROUTING_REGISTRATION_MARKERS: tuple[str, ...] = (
    "kayit", "kayd", "yenileme", "ders kaydi",
    "ders secimi", "ders ekleme", "ders birakma",
)
ROUTING_TIMING_MARKERS: tuple[str, ...] = (
    "basvuru", "ne zaman", "takvim", "tarih", "surec",
    "son gun", "son tarih", "acildi mi", "basladi mi",
)
ROUTING_ACADEMIC_CONTEXT_MARKERS: tuple[str, ...] = ACADEMIC_DEPARTMENT_CONTEXT_MARKERS
ROUTING_ACADEMIC_CALENDAR_MARKERS: tuple[str, ...] = (
    "akademik takvim",
    "kayit donemi",
    "ders kaydi takvimi",
    "ders kayit tarihi",
    "yariyil baslangici",
    "donem baslangici",
    "final donemi",
    "sinav takvimi",
)
ROUTING_FORMAL_RULE_MARKERS: tuple[str, ...] = (
    "azami",
    "azami sure",
    "azami ogrenim suresi",
    "butunleme",
    "devam zorunlulugu",
    "devam yuzdesi",
    "devamsizlik",
    "not sistemi",
    "degerlendirme sistemi",
    "bagil degerlendirme",
    "harf notu",
    "gecme notu",
    "basari notu",
    "sinif tekrari",
    "ders tekrari",
)
ROUTING_INTERNATIONAL_MARKERS: tuple[str, ...] = (
    "erasmus",
    "uluslararasi",
    "yabanci",
    "ikamet",
    "denklik",
    "tomer",
    "yos",
    "exchange",
    "mevlana",
    "farabi",
    "degisim programi",
    "yabanci ogrenci",
    "goc idaresi",
)
ROUTING_CAP_MARKERS: tuple[str, ...] = (
    "cap", "cift anadal", "cift ana dal", "yandal", "yan dal",
    "ikinci lisans",
)
ROUTING_STUDENT_DOCUMENT_MARKERS: tuple[str, ...] = (
    "transkript",
    "ogrenci belgesi",
    "transkript belgesi",
    "diploma eki",
    "not dokumu",
    "kayit belgesi",
    "ogrenci durum belgesi",
    "askerlik belgesi",
    "tecil belgesi",
)
ROUTING_STUDENT_DOCUMENT_REQUEST_MARKERS: tuple[str, ...] = (
    "belge nasil al",
    "belgemi nasil al",
    "belgeyi nasil al",
    "nereden alabilirim",
    "belge almak istiyorum",
    "belge basvurusu",
)
ROUTING_STUDENT_SERVICES_MARKERS: tuple[str, ...] = (
    "sifre",
    "parola",
    "ubys",
    "obs",
    "ilisik kesme",
    "kayit dondurma",
    "donem dondurma",
    "kayit sildirme",
    "sifre sifirlama",
    "giris yapamiyorum",
)
ROUTING_SCHOLARSHIP_MARKERS: tuple[str, ...] = (
    "burs",
    "scholarship",
    "yemek bursu",
    "kismi zamanli",
    "burs basvurusu",
    "basari bursu",
    "ihtiyac bursu",
)
ROUTING_INTERNSHIP_MARKERS: tuple[str, ...] = (
    "staj",
    "mup",
    "mesleki uygulama",
    "sanayi uygulamasi",
    "bitirme projesi",
    "zorunlu staj",
    "staj defteri",
    "staj sigorta",
)
ROUTING_GENERAL_AKTS_MARKERS: tuple[str, ...] = (
    "mezun olmak icin kac akts gerekir",
    "mezuniyet icin kac akts gerekir",
    "toplam akts",
    "akts gerekli",
    "kredi gerekli",
    "mezuniyet kredisi",
)
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
    "kaydim",
    "not ortalamam",
    "stajim",
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


def has_student_document_markers(normalized_text: str) -> bool:
    """Return whether query is clearly about transcript or student document retrieval."""
    if contains_any(normalized_text, ROUTING_STUDENT_DOCUMENT_MARKERS):
        return True
    return "belge" in normalized_text and any(
        marker in normalized_text for marker in ("ogrenci", "transkript", "diploma")
    )


def has_student_document_request_markers(normalized_text: str) -> bool:
    """Return whether query explicitly asks how/where to obtain a student document."""
    return contains_any(normalized_text, ROUTING_STUDENT_DOCUMENT_REQUEST_MARKERS)


def has_student_services_markers(normalized_text: str) -> bool:
    """Return whether query is clearly about password/reset/freeze/withdrawal student services."""
    return contains_any(normalized_text, ROUTING_STUDENT_SERVICES_MARKERS)


def has_scholarship_markers(normalized_text: str) -> bool:
    """Return whether query is about scholarship-like topics."""
    return contains_any(normalized_text, ROUTING_SCHOLARSHIP_MARKERS)


def has_internship_markers(normalized_text: str) -> bool:
    """Return whether query is clearly about internship-like procedures."""
    return contains_any(normalized_text, ROUTING_INTERNSHIP_MARKERS)


def has_general_akts_markers(normalized_text: str) -> bool:
    """Return whether query asks for a program-level AKTS graduation rule."""
    return ("akts" in normalized_text or "ects" in normalized_text) and contains_any(
        normalized_text,
        ROUTING_GENERAL_AKTS_MARKERS,
    )


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
        if has_internship_markers(normalized_query):
            return TaskType.PROCEDURE_QUERY
        if any(keyword in normalized_query for keyword in ("kayit", "kayd", "yatay", "dikey", "muafiyet", "intibak", "takvim")):
            return TaskType.REGISTRATION_QUERY
        if has_student_services_markers(normalized_query):
            return TaskType.REGISTRATION_QUERY
        if has_general_akts_markers(normalized_query):
            return TaskType.ACADEMIC_QUERY
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
