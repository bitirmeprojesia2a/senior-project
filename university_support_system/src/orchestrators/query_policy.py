"""Query policy helpers for the main orchestrator."""

from __future__ import annotations

import re

from src.agents.academic.curriculum_utils import infer_department_from_query
from src.agents.finance.tuition_utils import extract_requested_unit
from src.core.constants import Department, TaskType
from src.core.query_markers import (
    ACADEMIC_DEPARTMENT_CONTEXT_MARKERS,
    CONTACT_QUERY_MARKERS,
    EVENT_QUERY_MARKERS,
    GLOBAL_SYNTHESIS_QUERY_MARKERS,
    RELATED_ANNOUNCEMENT_QUERY_MARKERS,
)
from src.core.text_normalization import contains_any_normalized, normalize_text
from src.db.schemas import DepartmentResponse
from src.db.schemas import IntentAnalysis
from src.orchestrators.response_utils import response_eligible_for_global_synthesis
from src.routing.query_concepts import (
    CAPABILITY_ANNOUNCEMENT,
    CONCEPT_ACADEMIC_CALENDAR,
    CONCEPT_ANNOUNCEMENT,
    CONCEPT_COURSE_SCHEDULE,
    CONCEPT_EXEMPTION,
    CONCEPT_HORIZONTAL_TRANSFER,
    extract_query_concepts,
)

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

AUTH_CLARIFICATION_MESSAGE = (
    "Kisisel sorunuza yanit verebilmem icin kimliginizi dogrulamam gerekiyor. "
    "Dogrulamayi ogrenci e-posta adresinize gonderecegim tek kullanimlik kod ile tamamlayabilirsiniz."
)

FEE_CONTEXT_CLARIFICATION_MESSAGE = (
    "Ogrenim ucreti ogrenci turune ve birime gore degisiyor. "
    "Dogru ucreti paylasabilmem icin Turk ogrenci misiniz, uluslararasi ogrenci misiniz? "
    "Mumkunse fakulte veya bolum bilginizi de ekleyin."
)

APPLICATION_TYPE_CLARIFICATION_MESSAGE = (
    "Hangi basvuru turu icin tarih sordugunuzu belirtir misiniz? "
    "Ornegin yatay gecis, CAP/YAP, Erasmus, staj, yaz okulu veya kayit basvurusu gibi yazabilirsiniz."
)

PROGRAM_CONTEXT_CLARIFICATION_MESSAGE = (
    "Bu soruyu dogru cevaplayabilmem icin fakulte, bolum veya program bilgisini belirtir misiniz?"
)

STUDENT_TYPE_CLARIFICATION_MESSAGE = (
    "Bu bilgi ogrenci turune gore degisiyor. Turk ogrenci misiniz, uluslararasi ogrenci misiniz?"
)

COURSE_CODE_PATTERN = re.compile(r"\b[A-ZÇĞİÖŞÜ]{2,6}\s?\d{3,4}\b", re.IGNORECASE)

_GENERAL_RULE_BYPASS: tuple[str, ...] = (
    "devam zorunlulugu",
    "devamsizlik",
    "basarisiz",
    "sinav",
    "degerlendirme",
    "not sistemi",
    "tekrar",
    "kural",
    "yonetmelik",
    "yonerge",
    "nasil degisir",
    "ne olur",
    "etkilenir mi",
    "sayilir mi",
    "muaf",
    "kosul",
    "sart",
    "nasil",
)

_ANNOUNCEMENT_DIRECT_LOOKUP_MARKERS: tuple[str, ...] = (
    "sinav programi",
    "ders programi",
    "final sinavi programi",
    "butunleme sinavi programi",
    "ara sinav programi",
    "tek ders sinavi",
    "tek ders",
    "ara sinav",
    "butunleme sinavi",
    "final sinavi",
    "mazeret sinavi",
)

_ANNOUNCEMENT_DIRECT_LOOKUP_INTENTS: tuple[str, ...] = (
    "var mi",
    "nereden takip",
    "nereden ogren",
    "linki olan",
    "duyurusu var mi",
)
_ANNOUNCEMENT_EXPLICIT_LOOKUP_INTENTS: tuple[str, ...] = (
    "duyuru",
    "duyurusu",
    "haber",
    "ilan",
    "link",
    "yayinlandi",
    "yayimlandi",
    "nereden takip",
    "nereden ogren",
)
_COURSE_SCHEDULE_ANNOUNCEMENT_INTENTS: tuple[str, ...] = tuple(
    marker for marker in _ANNOUNCEMENT_EXPLICIT_LOOKUP_INTENTS if marker != "var mi"
)
_EXAM_PROGRAM_LOOKUP_MARKERS: tuple[str, ...] = (
    "sinav programi",
    "final sinavi programi",
    "butunleme sinavi programi",
    "ara sinav programi",
    "mazeret sinavi programi",
)

_ACADEMIC_CALENDAR_DATE_MARKERS: tuple[str, ...] = (
    "final sinavlari",
    "final sinavlarinin",
    "butunleme sinavlari",
    "butunleme sinavlarinin",
    "ara sinavlari",
    "ara sinavlarinin",
    "sinavlari ne zaman",
    "sinavlar ne zaman",
    "sinav tarihleri",
    "not giris",
    "notlarin giril",
    "notlarin son",
    "girilmesinin son gunu",
    "girilmesinin son günü",
    "girilmesi son gun",
)

_RELATED_ANNOUNCEMENT_SUBJECT_MARKERS: tuple[str, ...] = (
    "duyuru",
    "haber",
    "ilan",
    "program",
    "takvim",
    "basvuru",
    "sinav",
    "tek ders",
)

_LATEST_ANNOUNCEMENT_FALLBACK_MARKERS: tuple[str, ...] = (
    "son duyuru",
    "son duyurular",
    "guncel duyuru",
    "guncel duyurular",
    "duyurular neler",
    "haberler neler",
)

_SUBJECT_SPECIFIC_ANNOUNCEMENT_MARKERS: tuple[str, ...] = (
    "sinav takvimi",
    "sinav programi",
    "final sinavi programi",
    "butunleme sinavi programi",
    "ara sinav programi",
    "ara sinav",
    "final sinavi",
    "butunleme sinavi",
    "ders programi",
    "tek ders",
)

_ANNOUNCEMENT_FOLLOW_UP_MARKERS: tuple[str, ...] = (
    "detay",
    "detayi",
    "link",
    "linki",
    "devami",
    "icerik",
    "tarih",
    "nerede",
    "hangisi",
    "ilk",
    "ikincisi",
    "ucuncusu",
)

_ANNOUNCEMENT_TOPIC_SHIFT_MARKERS: tuple[str, ...] = (
    "kayit",
    "kayit tarihi",
    "kayit tarihleri",
    "kayit donemi",
    "staj",
    "ders kaydi",
    "ders secimi",
    "mufredat",
    "dersleri",
    "dersi hangi",
    "sinifta",
    "yariyil",
    "donem ucreti",
    "harc",
    "ogrenim ucreti",
    "yemekhane",
    "not",
    "not giris",
    "final sinavlari",
    "sinav tarihleri",
    "mezuniyet",
    "diploma",
    "kayit dondurma",
    "ilisik kesme",
)

_PROCEDURAL_ANNOUNCEMENT_BLOCK_MARKERS: tuple[str, ...] = (
    "muafiyet",
    "muaf",
    "intibak",
    "ders saydir",
    "ders saydirma",
    "ders kaydi",
    "ders secimi",
    "kayit yenileme",
    "kayit dondurma",
    "ilisik kesme",
    "staj",
    "cap",
    "cift anadal",
    "yandal",
    "yaz okulu",
    "yatay gecis",
    "erasmus",
    "mezuniyet",
)

_PROCEDURAL_QUESTION_MARKERS: tuple[str, ...] = (
    "basvuru",
    "basvurusu",
    "basvurulur",
    "ne zaman",
    "zaman",
    "nasil",
    "ne yapmaliyim",
    "surec",
    "son gun",
    "son tarih",
    "hangi belgeler",
    "kimler katilabilir",
    "katilabilir",
)

_EXPLICIT_ANNOUNCEMENT_ALLOW_MARKERS: tuple[str, ...] = (
    "duyuru",
    "duyurusu",
    "haber",
    "ilan",
    "link",
    "yayinlandi",
    "yayimlandi",
    "son duyuru",
    "guncel duyuru",
    "nereden takip",
    "nereden ogren",
)


def augment_query_for_department(
    department: Department,
    query: str,
    metadata: dict,
) -> str:
    """Add lightweight context to the query only when strictly needed.

    ACADEMIC_PROGRAMS queries are no longer prefixed; department context is
    handled via metadata-based boosting in the retriever instead.
    Finance queries still receive a student-type hint for fee differentiation.
    """
    if department != Department.FINANCE:
        return query

    student_type = (metadata.get("student_type") or "").strip()
    student_faculty = (metadata.get("student_faculty") or "").strip()

    lowered_query = normalize_text(query)
    student_type_prefix = ""
    if student_type and normalize_text(student_type) not in lowered_query:
        suffix = " baglami icin: " if "ogrenci" in normalize_text(student_type) else " ogrenci baglami icin: "
        student_type_prefix = f"{student_type}{suffix}"

    faculty_prefix = ""
    fee_markers = ("ucret", "harc", "odeme", "katki payi")
    requested_unit = extract_requested_unit(query)
    if student_faculty and not requested_unit and any(marker in lowered_query for marker in fee_markers):
        if normalize_text(student_faculty) not in lowered_query:
            faculty_prefix = f"{student_faculty} icin: "

    return f"{student_type_prefix}{faculty_prefix}{query}".strip()


def build_missing_slot_clarification_message(
    *,
    intent: IntentAnalysis | None,
    metadata: dict | None = None,
) -> str | None:
    """Turn LLM-provided missing slot metadata into a safe clarification prompt.

    The LLM decides which semantic slots are missing; this function only maps
    known slot names to user-facing questions and ignores slots already present
    in authenticated/session metadata.
    """
    if intent is None or not intent.missing_slots:
        return None
    if intent.primary_intent == "academic_calendar":
        return None

    metadata = metadata or {}
    missing_slots = set(intent.missing_slots)

    if metadata.get("is_authenticated"):
        missing_slots.discard("auth")
    if metadata.get("student_type"):
        missing_slots.discard("student_type")
    if metadata.get("student_faculty") or metadata.get("student_department"):
        missing_slots.discard("faculty_or_program")
        missing_slots.discard("department_or_program")
        missing_slots.discard("program")
    if not missing_slots:
        return None

    if "auth" in missing_slots:
        return AUTH_CLARIFICATION_MESSAGE

    fee_slots = {"student_type", "faculty_or_program", "department_or_program", "program"}
    if "student_type" in missing_slots and missing_slots.intersection(fee_slots - {"student_type"}):
        return FEE_CONTEXT_CLARIFICATION_MESSAGE

    if "application_type" in missing_slots:
        return APPLICATION_TYPE_CLARIFICATION_MESSAGE

    if "student_type" in missing_slots:
        return STUDENT_TYPE_CLARIFICATION_MESSAGE

    if missing_slots.intersection({"faculty_or_program", "department_or_program", "program", "course_name"}):
        return PROGRAM_CONTEXT_CLARIFICATION_MESSAGE

    return None


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
    has_known_program_name = infer_department_from_query(query) is not None
    if has_explicit_program_signal or has_explicit_course_code or has_known_program_name:
        return False

    if any(signal in lowered for signal in _GENERAL_RULE_BYPASS):
        return False

    return contains_any_normalized(lowered, ACADEMIC_DEPARTMENT_CONTEXT_MARKERS)


def looks_like_announcement_query(query: str) -> bool:
    """Return whether the query primarily targets announcements."""
    normalized = normalize_text(query)
    concepts = extract_query_concepts(normalized)
    if CAPABILITY_ANNOUNCEMENT in concepts.blocked_primary_capabilities:
        return False
    if concepts.has(CONCEPT_ANNOUNCEMENT):
        return True
    if (
        (concepts.has(CONCEPT_ACADEMIC_CALENDAR) or contains_any_normalized(normalized, _ACADEMIC_CALENDAR_DATE_MARKERS))
        and not concepts.has(CONCEPT_ANNOUNCEMENT)
        and "programi" not in normalized
    ):
        return False
    if contains_any_normalized(normalized, _EXAM_PROGRAM_LOOKUP_MARKERS):
        return True
    if concepts.has(CONCEPT_COURSE_SCHEDULE) or "ders programi" in normalized:
        return contains_any_normalized(normalized, _COURSE_SCHEDULE_ANNOUNCEMENT_INTENTS)
    return (
        contains_any_normalized(normalized, _ANNOUNCEMENT_DIRECT_LOOKUP_INTENTS)
        and contains_any_normalized(normalized, _ANNOUNCEMENT_DIRECT_LOOKUP_MARKERS)
    )


def should_block_announcement_primary_flow(query: str) -> bool:
    """Return whether a procedural question must not become announcement-only.

    Some procedural questions contain timing words such as "basvuru" and
    "ne zaman". Those can be semantically close to announcements, but the user
    is asking for the rule/process unless they explicitly ask for a duyuru,
    ilan, haber or link.
    """
    normalized = normalize_text(query)
    concepts = extract_query_concepts(normalized)
    if CAPABILITY_ANNOUNCEMENT in concepts.explicit_capabilities:
        return False
    if CAPABILITY_ANNOUNCEMENT in concepts.blocked_primary_capabilities:
        return True
    if contains_any_normalized(normalized, _EXPLICIT_ANNOUNCEMENT_ALLOW_MARKERS):
        return False
    if "yatay gecis" in normalized and contains_any_normalized(
        normalized,
        ("muafiyet", "muaf", "intibak", "ders saydir"),
    ):
        return True
    return contains_any_normalized(
        normalized,
        _PROCEDURAL_ANNOUNCEMENT_BLOCK_MARKERS,
    ) and contains_any_normalized(normalized, _PROCEDURAL_QUESTION_MARKERS)


def looks_like_event_query(query: str) -> bool:
    """Return whether the query explicitly asks for events."""
    normalized = normalize_text(query)
    if looks_like_contact_query(normalized):
        return False
    return contains_any_normalized(normalized, EVENT_QUERY_MARKERS)


def looks_like_contact_query(query: str) -> bool:
    """Return whether the query primarily asks for contact information."""
    return contains_any_normalized(query, CONTACT_QUERY_MARKERS)


def should_fetch_related_announcements(query: str) -> bool:
    """Return whether a non-announcement query still benefits from related announcements."""
    normalized = normalize_text(query)
    concepts = extract_query_concepts(normalized)
    if should_block_announcement_primary_flow(normalized):
        if concepts.has(CONCEPT_HORIZONTAL_TRANSFER) and concepts.has(CONCEPT_EXEMPTION):
            return False
        if not (
            contains_any_normalized(normalized, RELATED_ANNOUNCEMENT_QUERY_MARKERS)
            and contains_any_normalized(normalized, _RELATED_ANNOUNCEMENT_SUBJECT_MARKERS)
        ):
            return False
    if looks_like_announcement_query(normalized):
        return True
    if contains_any_normalized(normalized, _ACADEMIC_CALENDAR_DATE_MARKERS):
        return False
    # Ilgili duyuru sinyali, contact marker'larindan once degerlendirilir.
    # Aksi halde "nerede" marker'i "nereden takip edilir" gibi sorgulari
    # yanlislikla contact sorusu sanip duyuru zenginlestirmesini kapatabilir.
    if contains_any_normalized(
        normalized,
        RELATED_ANNOUNCEMENT_QUERY_MARKERS,
    ) and contains_any_normalized(
        normalized,
        _RELATED_ANNOUNCEMENT_SUBJECT_MARKERS,
    ):
        return True
    if looks_like_contact_query(normalized):
        return False
    return False


def should_allow_announcement_latest_fallback(query: str) -> bool:
    """Return whether announcement lookup may fall back to generic latest records."""
    normalized = normalize_text(query)
    if contains_any_normalized(normalized, _LATEST_ANNOUNCEMENT_FALLBACK_MARKERS):
        return True
    if contains_any_normalized(normalized, _SUBJECT_SPECIFIC_ANNOUNCEMENT_MARKERS):
        return False
    return looks_like_announcement_query(normalized)


def should_keep_announcement_follow_up(query: str) -> bool:
    """Return whether a follow-up should remain in the announcement flow."""
    normalized = normalize_text(query).strip(" \t\r\n?.!,;:")
    if looks_like_announcement_query(normalized):
        return True
    if contains_any_normalized(normalized, _ANNOUNCEMENT_TOPIC_SHIFT_MARKERS):
        return False
    tokens = normalized.split()
    return len(tokens) <= 4 and contains_any_normalized(
        normalized,
        _ANNOUNCEMENT_FOLLOW_UP_MARKERS,
    )


def personalize_answer(answer: str, full_name: str | None) -> str:
    """Add a first-name prefix when a profile is available."""
    if not full_name or not answer:
        return answer
    first_name = (full_name.split() or [full_name])[0]
    return f"{first_name}, {answer}"


def query_prefers_global_synthesis(query: str) -> bool:
    """Return whether the query likely benefits from a combined LLM synthesis."""
    return contains_any_normalized(query, GLOBAL_SYNTHESIS_QUERY_MARKERS)


def should_use_global_synthesis(*, query: str, responses: list[DepartmentResponse]) -> bool:
    """Return whether final answer composition should use global synthesis."""
    if looks_like_contact_query(query):
        return False
    meaningful = [
        response
        for response in responses
        if response_eligible_for_global_synthesis(response)
    ]
    if not meaningful:
        return False
    if not any(response.sources or response.db_data for response in meaningful):
        return False
    if all(not response.sources for response in meaningful):
        return False
    # Tek veya cok departman farketmeksizin, anlamli kaynak varsa
    # her zaman LLM sentezi/refinement uygula.
    return True
