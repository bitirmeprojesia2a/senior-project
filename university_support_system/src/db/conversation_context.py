"""Conversation state service for multi-turn query resolution."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Callable, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.capabilities.conversation_frame import ConversationFrame
from src.core.config import settings
from src.core.constants import Department, TaskType
from src.core.source_ownership import source_owner_from_capability
from src.core.text_normalization import normalize_text
from src.db.connection import get_session
from src.cache.conversation_cache import get_cached_state, set_cached_state
from src.db.conversation_models import ConversationState, ConversationTurn
from src.db.schemas import RAGSource
from src.core.query_intent_guards import looks_like_fee_catalog_amount_query
from src.llm.prompt_templates import CONVERSATION_FOLLOWUP_SYSTEM_PROMPT

if TYPE_CHECKING:
    from src.llm.llm_service import LLMService

logger = logging.getLogger(__name__)

_STATE_QUERY_PREVIEW_MAX_CHARS = 280
_TURN_QUERY_PREVIEW_MAX_CHARS = 240
_TURN_ANSWER_PREVIEW_MAX_CHARS = 560
_TOPIC_TRANSITION_THRESHOLD = 0.55


def _parse_build_timestamp(value: str | None) -> datetime | None:
    if not value or value == "unknown":
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)

_COURSE_CODE_PATTERN = re.compile(r"\b[A-ZÇĞİÖŞÜ]{2,6}\s?\d{3,4}\b", re.IGNORECASE)
_KNOWN_COURSE_PREFIXES = {
    "bil", "eem", "end", "mak", "ins", "muh", "mat", "fiz", "kim",
    "bio", "ist", "ikt", "huk", "tip", "dis", "ecz", "ssd", "ydl",
    "tur", "ata", "ing", "alm", "frn", "egf",
}
_INVALID_COURSE_PREFIXES = {
    "icin", "mayis", "eylul", "ekim", "kasim", "aralik", "ocak",
    "subat", "mart", "nisan", "haziran", "temmuz", "agustos",
}
_FOLLOW_UP_PREFIXES = (
    "peki",
    "bir de",
    "bu durumda",
    "bu ders",
    "bunun",
    "bunun icin",
    "bunlar",
    "bunlar icin",
    "onun",
    "onun icin",
    "onlar",
    "onlar icin",
    "o zaman",
    "ya da",
    "ya peki",
    "ayrica",
    "ek olarak",
    "bununla birlikte",
    "buna ek olarak",
    "oyle ise",
    "oylemi",
    "bunu",
    "onu",
    "aynisi",
    "boylece",
    "sonra",
    "son olarak",
    "birde",
    "yani",
)
# Guclu marker'lar: Tek baslarina follow-up sinyali olarak yeterli
_STRONG_FOLLOW_UP_MARKERS = (
    "ucreti ne kadar",
    "ucretleri ne kadar",
    "ne kadar",
    "ne olmali",
    "suresi ne",
    "son tarihi",
    "gecerli mi",
    "zorunlu mu",
    "olur mu",
    "sart mi",
    "gerekli mi",
    "kosullari",
    "sartlari",
)
# Zayif marker'lar: Sadece kisa sorgularda (<=5 kelime) follow-up sinyali
_WEAK_FOLLOW_UP_MARKERS = (
    "ne zaman",
    "nasil",
    "neler",
    "hangileri",
    "nedir",
    "ne demek",
    "ne oluyor",
    "nereden",
    "nereye",
    "derslikte",
    "sinifta",
)
_FOLLOW_UP_PRONOUNS = {
    "bu", "bunu", "buna", "bunda", "bunun", "bundan",
    "bunlar", "bunlarin", "bunlara",
    "su", "sunu", "sunun",
    "o", "onu", "ona", "onun", "ondan", "onlar", "onlarin",
    "orada", "burada", "oraya", "buraya",
    "aynisi", "kendisi",
}
_PRONOUN_LED_PREFIXES = (
    "bunun",
    "bunun icin",
    "bunlar",
    "bunlar icin",
    "onun",
    "onun icin",
    "onlar",
    "onlar icin",
    "bunu",
    "onu",
)
_TURBO_WORDS = {
    "evet", "hayir", "tamam", "tesekkurler", "ok", "sagol",
    "baska", "anladim", "tamamdir", "sagolun", "tesekkur",
    "iyi", "guzel", "oldu", "peki",
    "sagolasin", "sagolasiniz", "eyvallah", "rica",
    "ricaderim", "ederim", "tesekkurler", "tesekkurederim",
    "sagolun", "sagolasin", "tesekur", "tşk",
}
_CONFUSION_OR_RESET_MARKERS = (
    "isler karisti",
    "kafam karisti",
    "karisti",
    "emin degilim",
    "bilmiyorum",
)
_EXPLANATION_FOLLOW_UP_MARKERS = (
    "anlamadim",
    "tam anlamadim",
    "daha acik",
    "daha anlasilir",
    "aciklar misin",
    "aciklar misiniz",
    "detayli aciklar",
    "daha detayli",
)
_INDEPENDENT_SHORT_QUERY_MARKERS = (
    "ogrencilik hak",
    "ogrenci hak",
    "haklarim",
)
_INDEPENDENT_ACADEMIC_CALENDAR_MARKERS = (
    "final sinav",
    "yariyil sonu sinav",
    "donem sonu sinav",
    "butunleme sinav",
    "ara sinav",
)
_INDEPENDENT_TOPIC_CHANGE_MARKERS = (
    "tek ders sinav",
    "tek ders",
    "erasmus basvuru",
    "erasmus programi",
    "staj",
    "staj basvuru",
    "zorunlu staj",
    "yatay gecis",
    "dikey gecis",
    "kayit dondurma",
    "kayit sildirme",
    "donem dondurma",
    "burs basvuru",
    "yaz okulu",
    "capa",
    "capa basvuru",
    "cap basvuru",
    "cift anadal",
    "yandal basvuru",
    "yan dal",
    "mezuniyet basvuru",
    "diploma",
    "transkript",
    "bu sinav",
    "butunleme sinav",
    "mazeret sinav",
    "ders tekrar",
    "mufredat",
    "ders programi",
    "ogrenci belge",
    "duyuru",
    "duyurular",
    "ilan",
    "haber",
    "sinav takvimi",
    "kimlik kart",
    "harc ucreti",
    "ogrenim ucreti",
    "katki payi",
    "devamsizlik",
    "saglik raporu",
    "yurt basvuru",
)
_INDEPENDENT_ACADEMIC_CALENDAR_TIME_MARKERS = (
    "ne zaman",
    "hangi tarihte",
    "tarih",
    "takvim",
    "son gun",
    "son tarih",
    "giril",
    "not giris",
)
_FOLLOW_UP_ANSWER_MARKERS = (
    "turk ogrenciyim",
    "turk ogrenci",
    "yerli ogrenciyim",
    "yerli ogrenci",
    "uluslararasi ogrenciyim",
    "uluslararasi ogrenci",
    "yabanci ogrenciyim",
    "yabanci ogrenci",
    "lisans ogrencisiyim",
    "lisans ogrenci",
    "onlisans ogrencisiyim",
    "onlisans ogrenci",
    "yuksek lisans ogrencisiyim",
    "yuksek lisans ogrenci",
    "doktora ogrencisiyim",
    "doktora ogrenci",
    "birinci sinifim",
    "ikinci sinifim",
    "ucuncu sinifim",
    "dorduncu sinifim",
    "son sinifim",
    "normal ogretim",
    "ikinci ogretim",
)
_EXACT_FOLLOW_UP_ANSWER_MARKERS = {
    "turk",
    "yerli",
    "uluslararasi",
    "yabanci",
    "lisans",
    "onlisans",
    "doktora",
}
_DOMESTIC_STATE_MARKERS = ("turk ogrenci", "yerli ogrenci", "turk ogrenciyim", "yerli ogrenciyim")
_INTERNATIONAL_STATE_MARKERS = ("uluslararasi ogrenci", "yabanci ogrenci", "uluslararasi ogrenciyim", "yabanci ogrenciyim")


def _infer_student_type_from_state(state: ConversationStateData) -> str | None:
    """Infer student type from conversation state (previous user/assistant turns)."""
    combined = normalize_text(
        f"{state.last_user_query or ''} {state.last_assistant_answer or ''}"
    )
    if any(marker in combined for marker in _INTERNATIONAL_STATE_MARKERS):
        return "international"
    if any(marker in combined for marker in _DOMESTIC_STATE_MARKERS):
        return "domestic"
    return None


_PROGRAM_SLOT_QUESTION_MARKERS = (
    "bolum veya program",
    "fakulte bolum veya program",
    "once bolum",
    "program bilgisini",
    "bolum bilgisini",
    "hangi program",
    "hangi bolum",
    "her donem kac akts",
    "kac akts",
    "akts hakki",
    "dersleri nelerdir",
    "dersleri hakkinda",
    "dersler neler",
    "hangi sinifta",
    "hangi donemde",
)
_COURSE_SLOT_REQUEST_MARKERS = (
    "ders adini ya da ders kodunu",
    "ders adi ya da ders kodu",
    "ders kodunu",
    "ders adini",
    "on kosul veya akts",
    "onkosul veya akts",
)
_SHORT_SLOT_FOLLOW_UP_MARKERS = (
    "ders programi",
    "haftalik program",
    "yariyil programi",
    "donem programi",
    "sinif programi",
    "mufredat",
    "ucret",
    "ucreti",
    "ogrenim ucreti",
    "ne kadar",
    "kac",
)
_STUDENT_TYPE_FRAGMENT_REWRITES: tuple[tuple[str, str], ...] = (
    ("turk ogrenciyim", "turk ogrenci"),
    ("turk ogrenci", "turk ogrenci"),
    ("uluslararasi ogrenciyim", "uluslararasi ogrenci"),
    ("uluslararasi ogrenci", "uluslararasi ogrenci"),
    ("yabanci ogrenciyim", "uluslararasi ogrenci"),
    ("yabanci ogrenci", "uluslararasi ogrenci"),
    ("onlisans ogrencisiyim", "onlisans ogrencisi"),
    ("onlisans ogrenci", "onlisans ogrencisi"),
    ("lisans ogrencisiyim", "lisans ogrencisi"),
    ("lisans ogrenci", "lisans ogrencisi"),
    ("yuksek lisans ogrencisiyim", "yuksek lisans ogrencisi"),
    ("yuksek lisans ogrenci", "yuksek lisans ogrencisi"),
    ("doktora ogrencisiyim", "doktora ogrencisi"),
    ("doktora ogrenci", "doktora ogrencisi"),
    ("birinci sinifim", "birinci sinif ogrencisi"),
    ("ikinci sinifim", "ikinci sinif ogrencisi"),
    ("ucuncu sinifim", "ucuncu sinif ogrencisi"),
    ("dorduncu sinifim", "dorduncu sinif ogrencisi"),
    ("son sinifim", "son sinif ogrencisi"),
)
_FEE_STUDENT_TYPE_FRAGMENT_REWRITES: dict[str, str] = {
    "turk": "Turk ogrenci",
    "yerli": "Turk ogrenci",
    "uluslararasi": "uluslararasi ogrenci",
    "yabanci": "uluslararasi ogrenci",
}
_MIN_CONTENT_WORD_OVERLAP = 0.35
_WORD_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
_INTENT_STOP_WORDS = {
    "bir", "bu", "su", "o", "ve", "ile", "icin", "ne", "nasil",
    "nedir", "mi", "mu", "da", "de", "den", "dan",
    "ya", "veya", "ama", "fakat", "gibi", "kadar", "en", "cok",
    "az", "hangi", "kim", "nere", "nerede", "zaman", "ise",
    "bunun", "bunu", "buna", "bundan", "bunlar", "bunlari", "bunlarin",
    "onun", "onu", "ona", "ondan", "onlar", "onlari", "onlarin",
    "peki", "hakkinda",
}
_VAGUE_FOLLOW_UP_TOKENS = {
    "sey",
    "basvuru",
    "basvurusu",
    "tarih",
    "tarihi",
    "zaman",
}
_CONDITIONAL_FOLLOW_UP_MARKERS = (
    "olsaydi",
    "olsaydim",
    "olursa",
    "olursam",
    "diyelim ki",
    "varsayalim",
    "farz edelim",
)
_CORRECTION_FOLLOW_UP_MARKERS = (
    "sordum",
    "sormustum",
    "soruyorum",
    "demedim",
    "degil",
    "kastettim",
    "bahsettim",
)


def _normalize_course_prefix(text: str) -> str:
    table = str.maketrans({
        "Ç": "c", "Ğ": "g", "İ": "i", "I": "i", "Ö": "o", "Ş": "s", "Ü": "u",
        "ç": "c", "ğ": "g", "ı": "i", "i": "i", "ö": "o", "ş": "s", "ü": "u",
    })
    return text.translate(table).lower()


def _is_valid_course_code_match(match: re.Match[str]) -> bool:
    raw = match.group(0).replace(" ", "")
    prefix = re.sub(r"\d+", "", raw)
    normalized_prefix = _normalize_course_prefix(prefix)
    if normalized_prefix in _INVALID_COURSE_PREFIXES:
        return False
    if normalized_prefix in _KNOWN_COURSE_PREFIXES:
        return True
    return prefix == prefix.upper() and len(prefix) <= 5


def _first_valid_course_code_match(text: str | None) -> re.Match[str] | None:
    if not text:
        return None
    for match in _COURSE_CODE_PATTERN.finditer(text):
        if _is_valid_course_code_match(match):
            return match
    return None
_SCHEDULE_CONTEXT_MARKERS = (
    "ders programi",
    "haftalik program",
    "programi satirlari",
)
_ACTION_FOLLOW_UP_MARKERS = (
    "basvur",
    "yapabilir",
    "girebilir",
    "alabilir",
    "edebilir",
    "olabilir miydim",
    "olabilir miydi",
)
_GENERIC_OVERLAP_WORDS = {
    "basvuru", "basvurusu", "basvurabilir", "basvurabilirim",
    "basvurmak", "basvurma", "nasil", "yapilir", "yapabilir",
    "yapabilirim", "nedir", "nelerdir", "ne", "kadar", "zaman",
    "kosul", "kosullari", "sartlari", "sart", "belge", "belgeler",
    "belgesi", "surec", "sureci", "tarih", "tarihi", "tarihleri",
    "ucret", "ucreti", "ucretleri", "hak", "hakki", "haklari",
    "sonuc", "sonuclari", "durum", "durumu", "islem", "islemi",
    "islemleri",
}
_VALUE_REFERENCE_TOKENS = {
    "deger",
    "sayi",
    "oran",
    "sart",
    "kosul",
    "miktar",
    "tutar",
}
_METRIC_TARGET_TOKENS = {
    "lisans",
    "onlisans",
    "doktora",
    "program",
    "bolum",
    "sinif",
}
_VALUE_REFERENCE_CONTEXT_TOKENS = {
    "akts",
    "kredi",
    "mezun",
    "mezuniyet",
    "ucret",
    "harc",
    "gun",
    "sure",
    "oran",
    "not",
    "gano",
    "sinif",
    "kapasite",
}
_TRANSIENT_FINANCE_FACET_MARKERS = (
    "harc",
    "borc",
    "borcum",
    "borcu",
    "borclu",
    "ucret",
    "odeme",
    "odemek",
    "odenir",
    "katki payi",
    "taksit",
    "dekont",
)
_PRIMARY_TOPIC_CARRY_MARKERS = (
    "basvuru tarihi",
    "basvuru tarihleri",
    "basvuru ne zaman",
    "basvuru zamani",
    "basvuru sureci",
    "tarihleri",
    "tarihi",
    "ne zaman",
    "hangi tarihte",
    "son gun",
    "son tarih",
    "belge",
    "belgeler",
    "kosul",
    "kosullari",
    "sart",
    "sartlari",
    "kontenjan",
)
_APPLICATION_TOPIC_NAMES = {
    "CAP / Cift Anadal",
    "Yandal",
    "Erasmus ve Uluslararasi Surecler",
    "Staj ve Uygulamali Egitim",
    "Yatay ve Dikey Gecis",
    "Yaz Okulu",
    "Kayit Dondurma ve Silme",
}


@dataclass(frozen=True)
class _CourseReference:
    code: str
    title: str | None = None
    department: str | None = None


def _normalized_tokens(text: str) -> list[str]:
    return _WORD_TOKEN_PATTERN.findall(normalize_text(text))


def _content_tokens(text: str) -> set[str]:
    return set(_normalized_tokens(text)) - _INTENT_STOP_WORDS


def _query_requests_finance_facet(query: str) -> bool:
    normalized_query = normalize_text(query)
    return any(marker in normalized_query for marker in _TRANSIENT_FINANCE_FACET_MARKERS)


def _is_application_topic(topic: str | None) -> bool:
    if not topic:
        return False
    return topic in _APPLICATION_TOPIC_NAMES or "basvuru" in normalize_text(_topic_rewrite_seed(topic))


def _query_requests_primary_topic_only(query: str, state: "ConversationStateData") -> bool:
    if not _is_application_topic(state.active_topic):
        return False
    if _query_requests_finance_facet(query):
        return False
    normalized_query = normalize_text(query)
    if any(marker in normalized_query for marker in _PRIMARY_TOPIC_CARRY_MARKERS):
        return True
    stripped_query = _strip_follow_up_prefixes(query)
    stripped_tokens = _content_tokens(stripped_query)
    return bool(stripped_tokens and stripped_tokens <= {"basvuru", "tarih", "tarihi", "tarihleri", "zaman"})


def _rewrite_carries_unrequested_finance_facet(
    *,
    query: str,
    rewritten: str,
    state: "ConversationStateData",
) -> bool:
    return (
        _query_requests_primary_topic_only(query, state)
        and _query_requests_finance_facet(rewritten)
        and not _query_requests_finance_facet(query)
    )


def _filter_transient_departments_for_query(
    *,
    query: str,
    state: "ConversationStateData",
    departments: Sequence[Department],
) -> list[Department]:
    parsed = list(dict.fromkeys(departments))
    if not _query_requests_primary_topic_only(query, state):
        return parsed
    if not _is_application_topic(state.active_topic):
        return parsed
    return [department for department in parsed if department != Department.FINANCE]


def _count_token_overlap(base_tokens: set[str], candidate_tokens: set[str]) -> int:
    return len(base_tokens & candidate_tokens)


def _count_stem_overlap(base_tokens: set[str], candidate_tokens: set[str]) -> float:
    """Approximate Turkish suffix overlap without introducing a stemmer."""
    overlap = float(_count_token_overlap(base_tokens, candidate_tokens))
    for base_token in base_tokens - candidate_tokens:
        for candidate_token in candidate_tokens - base_tokens:
            shorter = min(base_token, candidate_token, key=len)
            longer = max(base_token, candidate_token, key=len)
            if len(shorter) >= 4 and longer.startswith(shorter):
                overlap += 0.5
                break
    return overlap


def _topic_transition_score(query: str, state: "ConversationStateData") -> float:
    """Return 0.0 for same-topic queries and 1.0 for likely topic changes."""
    query_tokens = _content_tokens(query) - _GENERIC_OVERLAP_WORDS
    state_tokens = _content_tokens(
        " ".join(
            text
            for text in (
                state.active_topic,
                state.last_user_query,
                state.last_resolved_query,
            )
            if text
        )
    ) - _GENERIC_OVERLAP_WORDS
    if not query_tokens or not state_tokens:
        return 0.5
    overlap = _count_stem_overlap(query_tokens, state_tokens)
    return max(0.0, 1.0 - (overlap / max(len(query_tokens), len(state_tokens))))


def _looks_like_conditional_action_follow_up(query: str) -> bool:
    normalized_query = normalize_text(query)
    return (
        any(marker in normalized_query for marker in _CONDITIONAL_FOLLOW_UP_MARKERS)
        and any(marker in normalized_query for marker in _ACTION_FOLLOW_UP_MARKERS)
    )


def _looks_like_correction_follow_up(query: str) -> bool:
    normalized_query = normalize_text(query)
    return any(marker in normalized_query for marker in _CORRECTION_FOLLOW_UP_MARKERS)


def _infer_corrected_topic_from_correction(query: str) -> str | None:
    normalized_query = normalize_text(query)
    if "degil" in normalized_query:
        tail = normalized_query.split("degil", 1)[1].strip(" \t\r\n?.!,;:")
        topic = ConversationContextService._infer_topic(tail)
        if topic:
            return topic
    topic = ConversationContextService._infer_topic(query)
    if topic:
        return topic
    return None


def _extract_schedule_term_correction(query: str) -> str | None:
    normalized_query = normalize_text(query)
    if any(marker in normalized_query for marker in ("guz", "ilk donem", "ilk yariyil")):
        return "guz donemi"
    if any(marker in normalized_query for marker in ("bahar", "ikinci donem", "ikinci yariyil")):
        return "bahar donemi"
    return None


def _has_schedule_context(state: "ConversationStateData") -> bool:
    context = normalize_text(
        " ".join(
            item
            for item in (
                state.active_topic,
                state.last_user_query,
                state.last_resolved_query,
                state.last_assistant_answer,
            )
            if item
        )
    )
    return any(marker in context for marker in _SCHEDULE_CONTEXT_MARKERS)


def _append_schedule_term_to_query(query: str, term_text: str) -> str:
    stripped = query.rstrip(" \t\r\n?.!,;:")
    normalized = normalize_text(stripped)
    if "guz" in normalized or "bahar" in normalized:
        return stripped
    return f"{stripped} {term_text}"


def _looks_like_value_reference_follow_up(query: str) -> bool:
    normalized_query = normalize_text(query)
    query_tokens = set(_normalized_tokens(query))
    has_reference_token = bool(query_tokens & _VALUE_REFERENCE_TOKENS)
    has_metric_target = bool(query_tokens & _METRIC_TARGET_TOKENS)
    has_deictic_reference = bool(query_tokens & _FOLLOW_UP_PRONOUNS) or any(
        normalized_query.startswith(prefix) for prefix in _FOLLOW_UP_PREFIXES
    )
    has_question_shape = (
        "kac" in query_tokens
        or "nedir" in query_tokens
        or "ne" in query_tokens
        or "hangi" in query_tokens
        or "mi" in query_tokens
        or "mu" in query_tokens
        or "midir" in normalized_query
    )
    has_short_metric_fragment = (
        has_metric_target
        and has_question_shape
        and len(_content_tokens(query)) <= 3
    )
    return (
        has_reference_token
        and has_deictic_reference
        and has_question_shape
    ) or has_short_metric_fragment


def _query_depends_on_context(query: str, *, context_texts: Sequence[str] = ()) -> bool:
    normalized_query = normalize_text(query)
    query_tokens = _normalized_tokens(query)
    query_content_tokens = _content_tokens(query)
    context_tokens = {
        token
        for text in context_texts
        for token in _content_tokens(text)
    }

    mentions_context = bool(
        context_tokens
        and _count_token_overlap(query_content_tokens, context_tokens) > 0
    )
    if mentions_context:
        return False

    has_follow_up_style = (
        any(normalized_query.startswith(prefix) for prefix in _FOLLOW_UP_PREFIXES)
        or any(token in _FOLLOW_UP_PRONOUNS for token in query_tokens[:4])
        or any(marker in normalized_query for marker in _STRONG_FOLLOW_UP_MARKERS)
        or any(marker in normalized_query for marker in _WEAK_FOLLOW_UP_MARKERS)
    )
    return has_follow_up_style or len(query_content_tokens) <= 4


def _is_answer_fragment_follow_up(query: str) -> bool:
    normalized_query = normalize_text(query)
    stripped = normalized_query.strip(" \t\r\n?.!,;:")
    if stripped in _EXACT_FOLLOW_UP_ANSWER_MARKERS:
        return True
    return any(marker in normalized_query for marker in _FOLLOW_UP_ANSWER_MARKERS)


def _infer_program_fragment(query: str) -> str | None:
    try:
        from src.agents.academic.curriculum_utils import infer_department_from_query
    except Exception:
        return None
    return infer_department_from_query(query)


def _infer_graduation_program_fragment(query: str) -> str | None:
    program = _infer_program_fragment(query)
    if program:
        return program
    normalized = normalize_text(query)
    if "dis hekimligi" in normalized or "dis hekimliginden" in normalized:
        return "Dis Hekimligi"
    if "tip" in normalized or "tip fakultesi" in normalized:
        return "Tip"
    if "eczacilik" in normalized:
        return "Eczacilik"
    special_programs = (
        ("Diş Hekimliği", ("dis hekimligi", "dis hekimliginden")),
        ("Tıp", ("tip", "tip fakultesi")),
        ("Eczacılık", ("eczacilik",)),
        ("Veteriner", ("veteriner", "veterinerlik")),
    )
    for label, markers in special_programs:
        if any(marker in normalized for marker in markers):
            return label
    return None


def _replace_program_fragment_in_query(previous_query: str, new_program: str) -> str | None:
    previous_program = _infer_program_fragment(previous_query)
    if not previous_program:
        return None

    normalized_previous = normalize_text(previous_query).strip()
    normalized_old_program = normalize_text(previous_program).strip()
    normalized_new_program = normalize_text(new_program).strip()
    if not normalized_previous or not normalized_old_program or not normalized_new_program:
        return None
    if normalized_old_program == normalized_new_program:
        return previous_query.rstrip(" \t\r\n?.!,;:") + "?"
    if normalized_old_program not in normalized_previous:
        return None

    replaced = normalized_previous.replace(normalized_old_program, normalized_new_program, 1)
    return replaced.rstrip(" \t\r\n?.!,;:") + "?"


def _has_explicit_program_context(state: "ConversationStateData") -> bool:
    return any(
        _infer_program_fragment(text) is not None
        for text in (state.last_resolved_query, state.last_user_query, state.last_assistant_answer)
        if text
    )


def _looks_like_short_slot_follow_up(query: str, state: "ConversationStateData") -> bool:
    if state.turn_count <= 0:
        return False
    if len(_content_tokens(query)) > 4:
        return False
    normalized = normalize_text(query)
    if not any(marker in normalized for marker in _SHORT_SLOT_FOLLOW_UP_MARKERS):
        return False
    return _has_explicit_program_context(state)


def _looks_like_program_slot_question(text: str) -> bool:
    normalized = normalize_text(text)
    return any(marker in normalized for marker in _PROGRAM_SLOT_QUESTION_MARKERS)


def _last_answer_explicitly_requests_program_slot(answer: str | None) -> bool:
    normalized = normalize_text(answer or "")
    if not normalized:
        return False
    return (
        "belirtir misiniz" in normalized
        and any(
            marker in normalized
            for marker in (
                "fakulte",
                "bolum",
                "program",
                "birim",
            )
        )
    ) or any(marker in normalized for marker in _PROGRAM_SLOT_QUESTION_MARKERS)


def _last_answer_explicitly_requests_application_type(answer: str | None) -> bool:
    normalized = normalize_text(answer or "")
    return "hangi basvuru turu" in normalized


def _last_answer_explicitly_requests_course_slot(answer: str | None) -> bool:
    normalized = normalize_text(answer or "")
    return any(marker in normalized for marker in _COURSE_SLOT_REQUEST_MARKERS)


def _looks_like_prerequisite_property_query(query: str) -> bool:
    normalized = normalize_text(query)
    return "onkosul" in normalized or "on kosul" in normalized


def _looks_like_course_akts_property_query(query: str) -> bool:
    tokens = set(_normalized_tokens(query))
    normalized = normalize_text(query)
    return "akts" in tokens and (
        "kac" in tokens
        or "ne" in tokens
        or "nedir" in tokens
        or normalized.endswith("akts")
    )


def _looks_like_course_semester_property_query(query: str) -> bool:
    normalized = normalize_text(query)
    return any(
        marker in normalized
        for marker in (
            "hangi yariyil",
            "kacinci yariyil",
            "hangi donem",
            "kacinci donem",
            "hangi sinif",
            "kacinci sinif",
        )
    )


def _looks_like_course_property_query(query: str) -> bool:
    return (
        _looks_like_prerequisite_property_query(query)
        or _looks_like_course_akts_property_query(query)
        or _looks_like_course_semester_property_query(query)
    )


def _extract_course_reference(text: str | None) -> _CourseReference | None:
    if not text:
        return None
    match = _first_valid_course_code_match(text)
    if match is None:
        return None

    code = match.group(0).upper().replace(" ", "")
    after_code = text[match.end(): match.end() + 100]
    title_text = re.split(
        r"\s+(?:dersi|dersinin|dersinde|dersine)\b|[()\n\r|.,;:]",
        after_code,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0].strip(" \t-")
    title_tokens = [
        token
        for token in re.findall(r"[A-Za-z0-9Ã‡ÄÄ°Ã–ÅÃœÃ§ÄŸÄ±iÃ¶ÅŸÃ¼]+", title_text)
        if normalize_text(token) not in {
            "ders",
            "dersi",
            "dersinin",
            "onkosul",
            "onkosulu",
            "akts",
            "kredi",
            "var",
            "mi",
            "ne",
            "kac",
        }
    ]
    title = " ".join(title_tokens[:6]).strip() or None
    department = _infer_program_fragment(text)
    return _CourseReference(code=code, title=title, department=department)


def _extract_recent_course_reference(state: "ConversationStateData") -> _CourseReference | None:
    for text in (
        state.last_assistant_answer,
        state.last_resolved_query,
        state.last_user_query,
        state.rolling_summary,
    ):
        reference = _extract_course_reference(text)
        if reference is not None:
            return reference
    return None


def _build_query_for_course_property(query: str, reference: _CourseReference) -> str | None:
    if _looks_like_prerequisite_property_query(query):
        return f"{reference.code} dersinin onkosulu var mi?"
    if _looks_like_course_akts_property_query(query):
        return f"{reference.code} dersi kac AKTS?"
    if _looks_like_course_semester_property_query(query):
        return f"{reference.code} dersi hangi yariyilda?"
    return None


def _build_course_reference_query(query: str, *, state: "ConversationStateData") -> str | None:
    if not _looks_like_course_property_query(query):
        return None
    # Current-turn course codes are authoritative.  If the user asks
    # "BIL104 on kosulu var mi?" right after a BIL203 answer, do not rewrite it
    # back to the previous course reference.
    if _extract_course_reference(query) is not None:
        return None
    reference = _extract_recent_course_reference(state)
    if reference is None:
        return None
    return _build_query_for_course_property(query, reference)


def _build_course_slot_fragment_query(query: str, *, state: "ConversationStateData") -> str | None:
    if not _last_answer_explicitly_requests_course_slot(state.last_assistant_answer):
        return None
    if _extract_course_reference(query) is None:
        return None

    previous_query = (state.last_resolved_query or state.last_user_query or "").strip()
    if not previous_query:
        return None

    stripped_query = query.rstrip(" \t\r\n?.!,;:")
    if _looks_like_prerequisite_property_query(previous_query):
        return f"{stripped_query} dersinin onkosulu var mi?"
    if _looks_like_course_akts_property_query(previous_query):
        return f"{stripped_query} dersi kac AKTS?"
    if _looks_like_course_semester_property_query(previous_query):
        return f"{stripped_query} dersi hangi yariyilda?"
    return None


def _course_reference_departments(state: "ConversationStateData") -> list[Department]:
    departments = list(
        dict.fromkeys(
            [
                *ConversationContextService._parse_departments(state.last_departments),
                Department.ACADEMIC_PROGRAMS,
            ]
        )
    )
    return departments


def _infer_application_topic_fragment(query: str) -> str | None:
    if len(_content_tokens(query)) > 3:
        return None
    topic = ConversationContextService._infer_topic(query)
    if topic and _is_application_topic(topic):
        return topic
    return None


def _rewrite_student_type_fragment(query: str) -> str:
    normalized_query = normalize_text(query)
    stripped = normalized_query.strip(" \t\r\n?.!,;:")
    for marker, replacement in _STUDENT_TYPE_FRAGMENT_REWRITES:
        if marker in stripped:
            return replacement
    return stripped


def _rewrite_fee_student_type_fragment(query: str) -> str:
    stripped = normalize_text(query).strip(" \t\r\n?.!,;:")
    return _FEE_STUDENT_TYPE_FRAGMENT_REWRITES.get(stripped) or _rewrite_student_type_fragment(query)


def _last_answer_explicitly_requests_fee_slot(answer: str | None) -> bool:
    normalized = normalize_text(answer or "")
    if not normalized:
        return False
    return (
        "turk ogrenci misiniz" in normalized
        and "uluslararasi ogrenci misiniz" in normalized
        and (
            "dogru ucreti" in normalized
            or "ogrenci turune gore degisiyor" in normalized
            or "ogrenim ucreti" in normalized
        )
    )


def _expects_fee_student_type_fragment(state: "ConversationStateData") -> bool:
    previous_query = (state.last_resolved_query or state.last_user_query or "").strip()
    return (
        _last_answer_explicitly_requests_fee_slot(state.last_assistant_answer)
        or (
            state.last_task_type == TaskType.TUITION_QUERY.value
            and looks_like_fee_catalog_amount_query(previous_query)
        )
    )


def _expects_participation_student_type_fragment(previous_context: str) -> bool:
    return "katil" in previous_context or "kimler" in previous_context


def _is_standalone_academic_calendar_query(query: str) -> bool:
    normalized_query = normalize_text(query)
    if "program" in normalized_query:
        return False
    return any(
        marker in normalized_query for marker in _INDEPENDENT_ACADEMIC_CALENDAR_MARKERS
    ) and any(
        marker in normalized_query
        for marker in _INDEPENDENT_ACADEMIC_CALENDAR_TIME_MARKERS
    )


def _rewrite_preserves_intent(
    original: str,
    rewritten: str,
    *,
    context_texts: Sequence[str] = (),
) -> bool:
    """Check that the LLM rewrite did not completely change the query topic.

    Returns True when the rewritten query shares enough content words with
    the original, preventing the conversation resolver from replacing
    a standalone question with a totally different one.
    """
    stop_words = {
        "bir", "bu", "su", "o", "ve", "ile", "icin", "ne", "nasil",
        "nedir", "mi", "mu", "da", "de", "den", "dan",
        "ya", "veya", "ama", "fakat", "gibi", "kadar", "en", "cok",
        "az", "hangi", "kim", "nere", "nerede", "zaman", "ise",
        # Zamirler ve hal ekleri — follow-up sorgularda siklikla bulunurlar
        "bunun", "bunu", "buna", "bundan", "bunlar", "bunlari", "bunlarin",
        "onun", "onu", "ona", "ondan", "onlar", "onlari", "onlarin",
        "peki", "hakkinda",
    }
    orig_tokens = _content_tokens(original)
    rew_tokens = _content_tokens(rewritten)
    if not orig_tokens:
        return True

    # Birebir eslesen tokenlar
    overlap = _count_token_overlap(orig_tokens, rew_tokens)

    # Turkcede cogul/hal eki farkliliklari icin kok benzerligi:
    # 'belge'≈'belgeler', 'staj'≈'staji' gibi durumlari yakala
    for orig_tok in orig_tokens - rew_tokens:
        for rew_tok in rew_tokens - orig_tokens:
            shorter = min(orig_tok, rew_tok, key=len)
            longer = max(orig_tok, rew_tok, key=len)
            if len(shorter) >= 3 and longer.startswith(shorter):
                overlap += 1
                break

    ratio = overlap / len(orig_tokens)
    if ratio >= _MIN_CONTENT_WORD_OVERLAP:
        return True

    context_tokens = {
        token
        for text in context_texts
        for token in _content_tokens(text)
    }
    if not context_tokens:
        return False

    if not _query_depends_on_context(original, context_texts=context_texts):
        return False

    return _count_token_overlap(context_tokens, rew_tokens) > 0


def _rewrite_supplies_needed_context(
    original: str,
    rewritten: str,
    *,
    context_texts: Sequence[str] = (),
) -> bool:
    if not context_texts:
        return True

    if not _query_depends_on_context(original, context_texts=context_texts):
        return True

    context_tokens = {
        token
        for text in context_texts
        for token in _content_tokens(text)
    }
    if not context_tokens:
        return True

    rewritten_tokens = _content_tokens(rewritten)
    if _count_token_overlap(context_tokens, rewritten_tokens) > 0:
        return True

    if _looks_like_value_reference_follow_up(original):
        context_value_tokens = context_tokens & _VALUE_REFERENCE_CONTEXT_TOKENS
        rewritten_value_tokens = rewritten_tokens & _VALUE_REFERENCE_CONTEXT_TOKENS
        if context_value_tokens and rewritten_value_tokens:
            return True
        return _count_stem_overlap(context_tokens, rewritten_tokens) > 0

    return False


_QUESTION_TYPE_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("ne_zaman", ("ne zaman", "hangi tarihte", "son tarihi", "son tarih")),
    ("ne_kadar", ("ne kadar", "kac tl", "kac para")),
    ("kac_sayi", ("kac",)),
    ("var_mi", ("var mi", "gerekli mi", "zorunlu mu", "olur mu", "odenir mi", "odeyebilir miyim")),
    ("nedir", ("nedir", "ne demek", "ne oluyor")),
    ("nasil", ("nasil", "nasil yapilir", "nasil basvurulur")),
    ("nereden", ("nereden", "nereye", "kimden")),
)


def _extract_question_signatures(text: str) -> list[str]:
    normalized_text = normalize_text(text)
    signatures: list[str] = []
    for signature, patterns in _QUESTION_TYPE_PATTERNS:
        if any(pattern in normalized_text for pattern in patterns):
            signatures.append(signature)
    return signatures


def _rewrite_preserves_question_type(original: str, rewritten: str) -> bool:
    original_signatures = _extract_question_signatures(original)
    if not original_signatures:
        return True

    rewritten_signatures = _extract_question_signatures(rewritten)
    if not rewritten_signatures:
        return False

    if any(signature not in rewritten_signatures for signature in original_signatures):
        return False

    extra_signatures = [
        signature for signature in rewritten_signatures
        if signature not in original_signatures
    ]
    return not extra_signatures


def _topic_rewrite_seed(topic: str | None) -> str:
    if not topic:
        return ""
    return _TOPIC_REWRITE_SEEDS.get(topic, normalize_text(topic))


def _strip_follow_up_prefixes(query: str) -> str:
    normalized_query = normalize_text(query).strip(" \t\r\n?.!,;:")
    prefixes = sorted(
        (normalize_text(prefix) for prefix in _FOLLOW_UP_PREFIXES),
        key=len,
        reverse=True,
    )
    for prefix in prefixes:
        if normalized_query == prefix:
            return ""
        if normalized_query.startswith(f"{prefix} "):
            normalized_query = normalized_query[len(prefix):].strip()
            break
    return re.sub(r"\s+", " ", normalized_query).strip()


def _build_heuristic_follow_up_query(query: str, *, topic: str | None) -> str:
    topic_seed = _topic_rewrite_seed(topic)
    if not topic_seed:
        return query

    original_query = normalize_text(query).strip()
    stripped_query = _strip_follow_up_prefixes(query)
    if not stripped_query:
        return f"{topic_seed} hakkinda"

    if normalize_text(topic_seed) in stripped_query:
        return stripped_query

    signatures = set(_extract_question_signatures(stripped_query))

    if "basvuru" in stripped_query and "tarih" in stripped_query:
        return f"{topic_seed} tarihleri ne zaman?"
    if original_query.startswith("bu durumda"):
        return f"{topic_seed} durumunda {stripped_query}"
    if original_query.startswith(("bunun icin", "onun icin", "bunlar icin")):
        return f"{topic_seed} icin {stripped_query}"

    if "ne_zaman" in signatures and "tarih" in stripped_query:
        return f"{topic_seed} tarihleri ne zaman?"
    if "ne_zaman" in signatures and "yapilir" in stripped_query:
        return f"{topic_seed} ne zaman yapilir?"
    if "ne_kadar" in signatures and "sure" in stripped_query:
        return f"{topic_seed} suresi ne kadar?"
    if "ne_kadar" in signatures and "oden" in stripped_query:
        return f"{topic_seed} icin ne kadar odenir?"
    if "var_mi" in signatures:
        return f"{topic_seed} icin {stripped_query}"
    if "nedir" in signatures:
        return f"{topic_seed} icin {stripped_query}"
    if "nereden" in signatures:
        return f"{topic_seed} ile ilgili {stripped_query}"
    if "nasil" in signatures and "yapilir" in stripped_query:
        return f"{topic_seed} nasil yapilir?"

    if _query_depends_on_context(query, context_texts=[topic]):
        return f"{topic_seed} icin {stripped_query}"

    return f"{topic_seed} hakkinda: {stripped_query}"


def _build_graduation_akts_follow_up_query(query: str, *, state: "ConversationStateData") -> str | None:
    if not _has_graduation_akts_context(state):
        return None

    normalized = normalize_text(query).strip(" \t\r\n?.!,;:*")
    if not normalized:
        return None

    program_name = _infer_graduation_program_fragment(query)
    if program_name and any(marker in normalized for marker in ("kac", "icin kac", "toplam")):
        return (
            f"{program_name} programindan mezun olmak icin "
            "toplam kac AKTS tamamlamaliyim?"
        )

    if (
        re.fullmatch(r"(120|240|300|360)\s*(akts)?\s*(mi|degil mi|degilmi)?", normalized)
        or (
            any(value in normalized for value in ("120", "240", "300", "360"))
            and any(marker in normalized for marker in ("degil mi", "mi"))
        )
    ):
        previous = state.last_resolved_query or state.last_user_query or ""
        previous_program = _infer_graduation_program_fragment(previous)
        asked_value_match = re.search(r"\b(120|240|300|360)\b", normalized)
        asked_value = asked_value_match.group(1) if asked_value_match else "240"
        if previous_program:
            return (
                f"{previous_program} programindan mezun olmak icin toplam "
                f"AKTS {asked_value} mi?"
            )
        previous_normalized = normalize_text(previous)
        if "onlisans" in previous_normalized or "on lisans" in previous_normalized:
            return f"On lisans programindan mezun olmak icin toplam AKTS {asked_value} mi?"
        if "lisans" in previous_normalized:
            return f"Normal lisans programindan mezun olmak icin toplam AKTS {asked_value} mi?"

    if any(marker in normalized for marker in ("donem icin sormadim", "donem icin demedim", "toplam sordum", "toplamini sordum")):
        previous = state.last_resolved_query or state.last_user_query or ""
        previous_program = _infer_graduation_program_fragment(previous)
        if previous_program:
            return (
                f"{previous_program} programindan mezun olmak icin "
                "toplam kac AKTS tamamlamaliyim?"
            )
        return "Normal lisans programindan mezun olmak icin toplam kac AKTS tamamlamaliyim?"

    if any(marker in normalized for marker in ("lisans icin kac", "lisans icin kac peki", "lisans kac", "lisans icin")):
        if "onlisans" not in normalized and "on lisans" not in normalized:
            return "Normal lisans programindan mezun olmak icin toplam kac AKTS tamamlamaliyim?"

    if any(marker in normalized for marker in ("onlisans icin kac", "on lisans icin kac", "onlisans kac")):
        return "On lisans programindan mezun olmak icin toplam kac AKTS tamamlamaliyim?"

    if normalized in {"kac", "kac peki", "peki kac", "toplam kac"}:
        previous = normalize_text(state.last_resolved_query or state.last_user_query or "")
        if "onlisans" in previous or "on lisans" in previous:
            return "Normal lisans programindan mezun olmak icin toplam kac AKTS tamamlamaliyim?"
        if "lisans" in previous:
            return "Normal lisans programindan mezun olmak icin toplam kac AKTS tamamlamaliyim?"

    return None


def _has_graduation_akts_context(state: "ConversationStateData") -> bool:
    context = normalize_text(
        " ".join(
            item
            for item in (
                state.last_resolved_query,
                state.last_user_query,
                state.last_assistant_answer,
                state.active_topic,
            )
            if item
        )
    )
    if any(marker in context for marker in ("cap", "cift anadal", "yandal")):
        return False
    if "akts" not in context and "kredi" not in context:
        return False
    return any(marker in context for marker in ("mezun", "mezuniyet", "tamamlam", "lisans programindan"))


def _build_answer_fragment_query(query: str, *, state: "ConversationStateData") -> str | None:
    """Merge short answer fragments with the last concrete question."""
    previous_query = (state.last_resolved_query or state.last_user_query or "").strip()
    if not previous_query:
        return None
    normalized_current = normalize_text(query)
    if normalized_current and normalized_current in normalize_text(previous_query):
        return previous_query

    program_name = _infer_program_fragment(query)
    if program_name and (
        _looks_like_program_slot_question(previous_query)
        or _last_answer_explicitly_requests_program_slot(state.last_assistant_answer)
    ):
        replaced_query = _replace_program_fragment_in_query(previous_query, program_name)
        if replaced_query:
            return replaced_query
        return f"{program_name} icin {previous_query.rstrip('?.!,;:')}?".strip()

    application_topic = _infer_application_topic_fragment(query)
    if application_topic and _last_answer_explicitly_requests_application_type(
        state.last_assistant_answer
    ):
        topic_seed = _topic_rewrite_seed(application_topic)
        previous_normalized = normalize_text(previous_query)
        if any(marker in previous_normalized for marker in ("tarih", "takvim", "ne zaman")):
            return f"{topic_seed} tarihleri ne zaman?"
        return f"{topic_seed} icin {previous_query.rstrip('?.!,;:')}?".strip()

    if not _is_answer_fragment_follow_up(query):
        return None

    previous_context = normalize_text(
        " ".join(
            item
            for item in (
                previous_query,
                state.active_topic,
                state.last_assistant_answer,
            )
            if item
        )
    )
    fragment = _rewrite_student_type_fragment(query)
    if fragment and _expects_fee_student_type_fragment(state):
        fee_fragment = _rewrite_fee_student_type_fragment(query)
        return f"{previous_query.rstrip('?.!,;:')} {fee_fragment}".strip()
    if fragment and _expects_participation_student_type_fragment(previous_context):
        return f"{previous_query.rstrip('?.!,;:')} {fragment} icin".strip()
    return None


def _query_is_pronoun_led_follow_up(query: str) -> bool:
    normalized_query = normalize_text(query).strip()
    return any(
        normalized_query == prefix or normalized_query.startswith(f"{prefix} ")
        for prefix in _PRONOUN_LED_PREFIXES
    )


def _query_is_short_object_sensitive_follow_up(query: str) -> bool:
    content_tokens = _content_tokens(query)
    if not content_tokens or len(content_tokens) > 3:
        return False
    signatures = set(_extract_question_signatures(query))
    return bool(signatures & {"ne_kadar", "ne_zaman", "nedir", "nereden", "var_mi"})


def _token_is_scoped(token: str, allowed_tokens: set[str]) -> bool:
    if token in allowed_tokens:
        return True
    for allowed in allowed_tokens:
        shorter = min(token, allowed, key=len)
        longer = max(token, allowed, key=len)
        if len(shorter) >= 4 and longer.startswith(shorter):
            return True
    return False


def _rewrite_adds_unscoped_detail_tokens(
    *,
    query: str,
    rewritten: str,
    heuristic_query: str,
    topic: str | None,
) -> bool:
    if not (
        _query_is_pronoun_led_follow_up(query)
        or _query_is_short_object_sensitive_follow_up(query)
    ):
        return False
    if normalize_text(heuristic_query) == normalize_text(query):
        return False

    allowed_tokens = _content_tokens(heuristic_query)
    if topic:
        allowed_tokens.update(_content_tokens(topic))
    if not allowed_tokens:
        return False

    rewritten_tokens = _content_tokens(rewritten)
    injected_tokens = {
        token
        for token in rewritten_tokens
        if not _token_is_scoped(token, allowed_tokens)
    }
    return bool(injected_tokens)


def _should_accept_llm_clarification(
    *,
    query: str,
    state: "ConversationStateData",
    is_follow_up: bool,
    clarification_message: str | None,
) -> bool:
    if not clarification_message:
        return False
    if not is_follow_up:
        return True

    heuristic_query = _build_heuristic_follow_up_query(query, topic=state.active_topic)
    if normalize_text(heuristic_query) != normalize_text(query):
        return False
    return True


_TOPIC_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("CAP / Cift Anadal", ("cap", "capa", "cift anadal", "cift ana dal", "ikinci lisans")),
    ("Yandal", ("yandal", "yan dal")),
    ("Erasmus ve Uluslararasi Surecler", ("erasmus", "ikamet", "yos", "tomer", "denklik", "mevlana", "farabi", "degisim programi")),
    ("Harc ve Ogrenim Ucretleri", ("harc", "katki payi", "ucret", "odeme", "taksit", "ogrenim ucreti")),
    ("Burs ve Destekler", ("burs", "yemek bursu", "kismi zamanli", "basari bursu", "ihtiyac bursu")),
    ("Kayit ve Akademik Takvim", ("kayit", "ders kaydi", "akademik takvim", "muafiyet", "kayit donemi", "ders secimi")),
    ("Kayit Dondurma ve Silme", ("kayit dondurma", "donem dondurma", "kayit sildirme", "ilisik kesme")),
    ("Mezuniyet ve Akademik Durum", ("mezuniyet", "gno", "transkript", "diploma", "not ortalamasi", "azami sure")),
    ("Staj ve Uygulamali Egitim", ("staj", "mup", "sanayi uygulamasi", "bitirme projesi", "zorunlu staj", "mesleki uygulama")),
    ("Sinav ve Degerlendirme", ("tek ders", "tek ders sinav", "sinav", "butunleme", "final", "vize", "mazeret", "bagil degerlendirme", "harf notu")),
    ("Yatay ve Dikey Gecis", ("yatay gecis", "dikey gecis", "kurum ici", "kurumlar arasi")),
    ("Mufredat ve Ders Yapisi", ("mufredat", "onkosul", "ders programi", "akts", "secmeli", "zorunlu ders")),
    ("Mevzuat ve Yonergeler", ("yonerge", "yonetmelik", "madde", "prosedur", "genelge")),
    ("Belgeler", ("ogrenci belgesi", "transkript belgesi", "diploma eki", "tecil", "askerlik belgesi")),
    ("Duyurular", ("duyurular", "duyuru", "ilan", "haber")),
    ("Yaz Okulu", ("yaz okulu", "yaz donemi")),
    (
        "Ders Tekrari ve Devam",
        (
            "ders tekrari",
            "tekrar dersi",
            "devam kosulu",
            "devam sarti",
            "okulum uzuyor",
            "okul uzuyor",
            "dersimden kaldim",
            "basarisiz oldugum",
            "hic almadigim",
            "alt donem ders",
        ),
    ),
    ("Ogrenci Kimligi", ("kimlik karti", "ogrenci karti", "ogrenci kimligi", "kimligimi kaybettim")),
    ("Saglik ve Sigorta", ("saglik raporu", "sigorta", "is kazasi", "rapor aldim")),
    ("Yurt ve Barinma", ("yurt", "barinma", "konaklama")),
    ("Devamsizlik", ("devamsizlik", "devam zorunlulugu", "yoklama")),
)

_TOPIC_REWRITE_SEEDS: dict[str, str] = {
    "CAP / Cift Anadal": "cap basvurusu",
    "Yandal": "yandal basvurusu",
    "Erasmus ve Uluslararasi Surecler": "erasmus basvurusu",
    "Harc ve Ogrenim Ucretleri": "harc ucreti",
    "Burs ve Destekler": "burs",
    "Kayit ve Akademik Takvim": "kayit islemi",
    "Kayit Dondurma ve Silme": "kayit dondurma",
    "Mezuniyet ve Akademik Durum": "mezuniyet",
    "Staj ve Uygulamali Egitim": "staj",
    "Sinav ve Degerlendirme": "sinav",
    "Yatay ve Dikey Gecis": "yatay gecis",
    "Mufredat ve Ders Yapisi": "mufredat",
    "Mevzuat ve Yonergeler": "yonetmelik",
    "Belgeler": "belge",
    "Yaz Okulu": "yaz okulu",
    "Ders Tekrari ve Devam": "ders tekrari",
    "Ogrenci Kimligi": "ogrenci kimligi",
    "Saglik ve Sigorta": "saglik ve sigorta",
    "Yurt ve Barinma": "yurt ve barinma",
    "Devamsizlik": "devamsizlik",
}


_TOPIC_DEPARTMENT_HINTS: dict[str, tuple[Department, ...]] = {
    "CAP / Cift Anadal": (Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS),
    "Yandal": (Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS),
    "Erasmus ve Uluslararasi Surecler": (Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS),
    "Harc ve Ogrenim Ucretleri": (Department.FINANCE,),
    "Burs ve Destekler": (Department.FINANCE,),
    "Mufredat ve Ders Yapisi": (Department.ACADEMIC_PROGRAMS,),
    "Ders Programi": (Department.ACADEMIC_PROGRAMS,),
}


_SOURCE_HINT_TOPIC_RULES: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "CAP / Cift Anadal": (
        ("cap", "cift anadal", "cift ana dal", "anadal", "ana dal", "ikinci lisans", "yandal", "yan dal"),
        ("staj", "mup", "sanayi", "yatay gecis", "dikey gecis", "mezun", "diploma", "transkript"),
    ),
    "Yandal": (
        ("yandal", "yan dal", "cift anadal", "cift ana dal", "anadal"),
        ("staj", "mup", "sanayi", "yatay gecis", "dikey gecis", "mezun", "diploma", "transkript"),
    ),
    "Erasmus ve Uluslararasi Surecler": (
        ("erasmus", "uluslararasi", "yabanci", "ikamet", "yos", "tomer", "denklik", "mevlana", "farabi"),
        ("staj", "cift anadal", "cap", "yatay gecis", "dikey gecis", "harc"),
    ),
    "Harc ve Ogrenim Ucretleri": (
        ("harc", "katki payi", "ucret", "odeme", "taksit", "ogrenim ucreti", "tuition"),
        ("staj", "cift anadal", "cap", "yatay gecis", "mufredat"),
    ),
    "Burs ve Destekler": (
        ("burs", "yemek bursu", "kismi zamanli", "destek", "scholarship"),
        ("staj", "cift anadal", "cap", "yatay gecis", "mufredat"),
    ),
    "Kayit ve Akademik Takvim": (
        ("kayit", "takvim", "akademik takvim", "muafiyet", "intibak", "ders kaydi"),
        ("staj", "cift anadal", "cap", "yatay gecis", "mezun", "diploma"),
    ),
    "Kayit Dondurma ve Silme": (
        ("kayit dondurma", "dondurma", "kayit sildirme", "ilisik", "silme"),
        ("staj", "cift anadal", "cap", "yatay gecis", "mufredat"),
    ),
    "Mezuniyet ve Akademik Durum": (
        ("mezun", "diploma", "transkript", "not ortalamasi", "gno", "gano", "azami"),
        ("staj", "cift anadal", "cap", "yatay gecis"),
    ),
    "Staj ve Uygulamali Egitim": (
        ("staj", "mup", "sanayi", "mesleki uygulama", "uygulama", "bitirme"),
        ("cift anadal", "cap", "yatay gecis", "diploma", "mezun"),
    ),
    "Sinav ve Degerlendirme": (
        ("sinav", "final", "vize", "butunleme", "mazeret", "tek ders", "bagil", "takvim"),
        ("staj", "cift anadal", "cap", "yatay gecis", "mufredat"),
    ),
    "Yatay ve Dikey Gecis": (
        ("yatay gecis", "dikey gecis", "kurum ici", "kurumlar arasi", "gecis"),
        ("staj", "cift anadal", "cap", "yandal", "mezun", "diploma"),
    ),
    "Mufredat ve Ders Yapisi": (
        ("mufredat", "ders", "akts", "onkosul", "program", "curriculum", "course"),
        ("staj", "cift anadal", "cap", "yatay gecis", "harc"),
    ),
    "Yaz Okulu": (
        ("yaz okulu", "yaz donemi"),
        ("staj", "cift anadal", "cap", "yatay gecis", "mufredat"),
    ),
    "Ders Tekrari ve Devam": (
        ("ders tekrari", "tekrar", "devam", "devamsizlik", "hic almadigim", "alt donem"),
        ("staj", "cift anadal", "cap", "yatay gecis", "harc"),
    ),
}


def _departments_for_topic(topic: str | None) -> list[Department]:
    if not topic:
        return []
    return list(_TOPIC_DEPARTMENT_HINTS.get(topic, ()))


def _source_ref_text(value: str) -> str:
    normalized = normalize_text(value)
    spaced = re.sub(r"[_\-.]+", " ", normalized)
    return f"{normalized} {spaced}"


def _topic_source_hint_rules(
    topic: str | None,
    query: str | None = None,
) -> tuple[tuple[str, ...], tuple[str, ...]] | None:
    topic_key = topic or ConversationContextService._infer_topic(query or "")
    if not topic_key:
        return None
    return _SOURCE_HINT_TOPIC_RULES.get(topic_key)


def _filter_source_refs_for_topic(
    source_refs: Sequence[str],
    *,
    topic: str | None,
    query: str | None = None,
) -> list[str]:
    """Return source hints safe to reuse as hard boosts for a follow-up."""
    deduped = [ref for ref in dict.fromkeys(str(ref).strip() for ref in source_refs) if ref]
    if not deduped:
        return []

    rules = _topic_source_hint_rules(topic, query=query)
    if rules is None:
        return deduped[: settings.conversation.max_source_refs]

    allowed_markers, rejected_markers = rules
    allowed = tuple(normalize_text(marker) for marker in allowed_markers if marker)
    rejected = tuple(normalize_text(marker) for marker in rejected_markers if marker)
    filtered: list[str] = []
    for ref in deduped:
        normalized_ref = _source_ref_text(ref)
        has_allowed = bool(allowed) and any(marker in normalized_ref for marker in allowed)
        if not has_allowed:
            continue
        has_rejected = bool(rejected) and any(marker in normalized_ref for marker in rejected)
        if has_rejected:
            continue
        filtered.append(ref)
    return filtered[: settings.conversation.max_source_refs]


def _source_hints_for_follow_up(
    state: "ConversationStateData",
    *,
    topic: str | None,
    query: str | None = None,
) -> list[str]:
    raw_hints = list(state.last_source_refs or [])
    filtered = _filter_source_refs_for_topic(raw_hints, topic=topic, query=query)
    if len(filtered) != len([hint for hint in raw_hints if str(hint).strip()]):
        logger.info(
            "conversation_source_hints_filtered topic=%s kept=%s original=%s",
            topic or state.active_topic,
            filtered,
            raw_hints,
        )
    return filtered


def _topic_id_for(topic: str | None) -> str | None:
    if not topic:
        return None
    normalized = normalize_text(topic)
    return re.sub(r"[^a-z0-9]+", "_", normalized).strip("_") or None


def _infer_question_type(query: str) -> str | None:
    normalized = normalize_text(query)
    tokens = set(_normalized_tokens(query))
    if any(marker in normalized for marker in ("duyuru", "duyurular", "ilan", "haber")):
        return "announcement"
    if any(marker in normalized for marker in ("ders programi", "haftalik program", "sinav takvimi")):
        return "schedule"
    if any(marker in normalized for marker in ("ne zaman", "hangi tarihte", "tarih", "takvim", "son gun", "son tarih")):
        return "date"
    if any(marker in normalized for marker in ("ne kadar", "kac tl", "kac lira", "ucret", "harc", "katki payi")):
        return "amount"
    if any(marker in normalized for marker in ("basvurabilir", "yapabilir", "girebilir", "alabilir", "olur mu", "miyim", "miydim")):
        return "eligibility"
    if any(marker in normalized for marker in ("sart", "sartlari", "kosul", "kosullari", "gerekli")):
        return "conditions"
    if any(marker in normalized for marker in ("acilacak", "acilan ders", "hangi dersler")):
        return "offerings"
    if any(marker in normalized for marker in ("belge", "belgeler", "evrak")):
        return "documents"
    if any(marker in normalized for marker in ("detay", "acikla", "anlamadim")):
        return "explanation"
    if "akts" in tokens and any(marker in normalized for marker in ("mezun", "mezuniyet", "tamamlam")):
        return "graduation_akts"
    return None


def _infer_fee_scope(query: str) -> str | None:
    normalized = normalize_text(query)
    if any(marker in normalized for marker in ("fazla odeme", "iade", "harc iadesi", "ucret iadesi")):
        return "refund_policy"
    if any(marker in normalized for marker in ("borc", "borcum", "borcu", "borclu")):
        return "payment_debt_eligibility"
    if any(marker in normalized for marker in ("yaz okulu", "yaz donemi", "yaz ogretimi")):
        return "summer_school_fee"
    if any(marker in normalized for marker in ("cap", "capa", "cift anadal", "cift ana dal", "yandal", "yan dal")):
        return "cap_extra_fee"
    if any(marker in normalized for marker in ("erasmus", "degisim programi")):
        return "erasmus_fee"
    if any(marker in normalized for marker in ("ogrenim ucreti", "katki payi", "harc", "donemlik", "yillik")):
        return "regular_tuition_fee"
    return None


def _infer_policy_facet(query: str, topic: str | None = None) -> str | None:
    normalized = normalize_text(" ".join(item for item in (query, topic) if item))
    fee_scope = _infer_fee_scope(query)
    if fee_scope:
        return fee_scope
    if any(marker in normalized for marker in ("duyuru", "duyurular", "ilan", "haber")):
        return "announcement"
    if any(marker in normalized for marker in ("yaz okulu", "yaz donemi", "yaz ogretimi")):
        return "summer_school"
    if any(marker in normalized for marker in ("cap", "capa", "cift anadal", "cift ana dal")):
        return "cap"
    if any(marker in normalized for marker in ("staj", "mesleki uygulama", "mup")):
        return "internship"
    if "akts" in normalized and any(marker in normalized for marker in ("mezun", "mezuniyet", "tamamlam")):
        return "graduation_akts"
    if any(marker in normalized for marker in ("formasyon", "pedagojik")):
        return "pedagogical_formation"
    if any(marker in normalized for marker in ("takvim", "tarih", "ne zaman")):
        return "calendar"
    if any(marker in normalized for marker in ("ders programi", "mufredat", "onkosul", "on kosul")):
        return "curriculum"
    return _topic_id_for(topic)


def _infer_conversation_capability(
    query: str,
    *,
    question_type: str | None,
    policy_facet: str | None,
) -> str | None:
    normalized = normalize_text(query)
    fee_scope = _infer_fee_scope(query)
    if question_type == "announcement":
        return "announcement.search"
    if question_type == "schedule" and "sinav takvimi" in normalized:
        return "calendar.academic_date"
    if question_type == "date" and any(marker in normalized for marker in ("final", "butunleme", "derslerin", "akademik takvim")):
        return "calendar.academic_date"
    if fee_scope == "regular_tuition_fee" and question_type == "amount":
        return "finance.tuition_fee"
    if _first_valid_course_code_match(query) and _looks_like_prerequisite_property_query(query):
        return "course.prerequisites"
    if _first_valid_course_code_match(query) and _looks_like_course_property_query(query):
        return "course.detail"
    if any(marker in normalized for marker in ("ders programi", "haftalik program")):
        return "schedule.weekly_program"
    if any(marker in normalized for marker in ("yariyil ders", "donem ders", "kacinci donem", "hangi yariyil")):
        return "curriculum.semester_courses"
    if policy_facet in {"summer_school", "cap", "internship", "graduation_akts", "refund_policy", "payment_debt_eligibility", "summer_school_fee", "cap_extra_fee", "erasmus_fee"}:
        return "student_affairs.policy_lookup"
    return None


def _infer_source_owner_from_capability(capability: str | None, *, policy_facet: str | None) -> str | None:
    return source_owner_from_capability(capability)


def _build_conversation_entities(
    query: str,
    *,
    existing: dict | None,
    student_type_hint: str | None,
) -> dict:
    entities = dict(existing or {})
    reference = _extract_course_reference(query)
    if reference is not None:
        entities["course_code"] = reference.code
    program = _infer_program_fragment(query)
    if program:
        entities["program"] = program
    student_type = student_type_hint or _rewrite_fee_student_type_fragment(query)
    if normalize_text(student_type) in {"turk ogrenci", "uluslararasi ogrenci"}:
        entities["student_type"] = "international" if "uluslararasi" in normalize_text(student_type) else "domestic"
    fee_scope = _infer_fee_scope(query)
    if fee_scope:
        entities["fee_scope"] = fee_scope
    normalized = normalize_text(query)
    if "onlisans" in normalized or "on lisans" in normalized:
        entities["education_level"] = "associate"
    elif "lisans" in normalized:
        entities["education_level"] = "bachelor"
    return entities


def _infer_temporal_scope(query: str, *, existing: dict | None = None) -> dict:
    temporal = dict(existing or {})
    normalized = normalize_text(query)
    if any(marker in normalized for marker in ("guncel", "son", "bu yil", "2025 2026", "2025-2026")):
        temporal.setdefault("scope", "current")
    if any(marker in normalized for marker in ("ne zaman", "tarih", "takvim", "son gun", "son tarih")):
        temporal.setdefault("scope", "current")
    year_match = re.search(r"\b(20\d{2})\b", query)
    if year_match:
        temporal["year"] = year_match.group(1)
    return temporal


@dataclass(frozen=True)
class ConversationTurnData:
    """Stored turn data used by follow-up resolution."""

    id: int
    context_id: str
    turn_index: int
    user_query: str
    resolved_query: str
    assistant_answer: str
    answer_summary: str | None
    active_topic: str | None
    task_type: str | None
    is_follow_up: bool
    departments: list[str]
    source_refs: list[str]
    created_at: datetime


@dataclass(frozen=True)
class ConversationStateData:
    """Rolling conversation state optimized for quick lookups."""

    context_id: str
    active_topic: str | None
    rolling_summary: str | None
    active_entities: list[str]
    last_departments: list[str]
    last_source_refs: list[str]
    last_task_type: str | None
    last_turn_id: int | None
    last_user_query: str | None
    last_resolved_query: str | None
    last_assistant_answer: str | None
    turn_count: int
    updated_at: datetime


@dataclass(frozen=True)
class ConversationResolution:
    """Resolved standalone query and reusable context hints."""

    original_query: str
    effective_query: str
    is_follow_up: bool
    used_context: bool
    active_topic: str | None
    department_hints: list[Department]
    source_hints: list[str]
    task_type_hint: TaskType | None = None
    student_type_hint: str | None = None
    clarification_message: str | None = None
    announcement_context: bool = False
    rewrite_method: str = "none"  # none | heuristic | llm | answer_fragment
    standalone_query: str | None = None  # explicit standalone form for telemetry
    frame: ConversationFrame | None = None
    operation: str = "new_topic"
    topic_id: str | None = None
    source_owner: str | None = None
    capability: str | None = None
    policy_facet: str | None = None
    question_type: str | None = None
    entities: dict | None = None
    temporal_scope: dict | None = None
    base_turn_index: int | None = None
    confidence: float | None = None
    expires_after_turns: int | None = None

    def __post_init__(self) -> None:
        if self.frame is not None:
            return
        query_for_contract = self.standalone_query or self.effective_query or self.original_query
        question_type = self.question_type or _infer_question_type(query_for_contract)
        policy_facet = self.policy_facet or _infer_policy_facet(query_for_contract, self.active_topic)
        capability = self.capability or _infer_conversation_capability(
            query_for_contract,
            question_type=question_type,
            policy_facet=policy_facet,
        )
        source_owner = self.source_owner or _infer_source_owner_from_capability(
            capability,
            policy_facet=policy_facet,
        )
        entities = _build_conversation_entities(
            query_for_contract,
            existing=self.entities,
            student_type_hint=self.student_type_hint,
        )
        temporal_scope = _infer_temporal_scope(query_for_contract, existing=self.temporal_scope)
        object.__setattr__(self, "question_type", question_type)
        object.__setattr__(self, "policy_facet", policy_facet)
        object.__setattr__(self, "capability", capability)
        object.__setattr__(self, "source_owner", source_owner)
        object.__setattr__(self, "entities", entities)
        object.__setattr__(self, "temporal_scope", temporal_scope)
        object.__setattr__(
            self,
            "frame",
            ConversationFrame.from_resolution_parts(
                original_query=self.original_query,
                effective_query=self.effective_query,
                standalone_query=self.standalone_query,
                is_follow_up=self.is_follow_up,
                used_context=self.used_context,
                active_topic=self.active_topic,
                department_hints=self.department_hints,
                source_hints=self.source_hints,
                task_type_hint=self.task_type_hint,
                announcement_context=self.announcement_context,
                rewrite_method=self.rewrite_method,
                operation=self.operation,
                topic_id=self.topic_id or _topic_id_for(self.active_topic),
                source_owner=source_owner,
                capability=capability,
                policy_facet=policy_facet,
                question_type=question_type,
                entities=entities,
                temporal_scope=temporal_scope,
                base_turn_index=self.base_turn_index,
                confidence=self.confidence,
                expires_after_turns=self.expires_after_turns,
            ),
        )


class ConversationContextService:
    """Persists turns and resolves follow-up questions."""

    def __init__(
        self,
        *,
        session_provider: Callable[[], AbstractAsyncContextManager[AsyncSession]] = get_session,
        now_provider: Callable[[], datetime] | None = None,
    ) -> None:
        self._session_provider = session_provider
        self._now_provider = now_provider or (lambda: datetime.now(timezone.utc))

    async def get_state(self, *, context_id: str) -> ConversationStateData | None:
        # Redis read-through cache
        cached = await get_cached_state(context_id)
        if cached is not None:
            return cached

        async with self._session_provider() as session:
            result = await session.execute(
                select(ConversationState).where(ConversationState.context_id == context_id)
            )
            row = result.scalar_one_or_none()
            if row is None:
                return None
            state_data = self._to_state_data(row)

            # Populate cache for subsequent reads
            await set_cached_state(state_data)
            return state_data

    async def resolve_query(
        self,
        *,
        context_id: str,
        query: str,
        llm_service: LLMService | None = None,
        llm_profile: str | None = None,
        student_department: str | None = None,
        student_faculty: str | None = None,
        student_type: str | None = None,
    ) -> ConversationResolution:
        """Resolve a query into a standalone form when it depends on prior turns."""
        if not settings.conversation.enabled or not context_id or not query.strip():
            return self._direct_resolution(query)

        state = await self.get_state(context_id=context_id)
        if state is None or self._is_state_stale(state):
            logger.info(
                "conversation_resolution context_id=%s state=%s result=direct_no_state",
                context_id,
                "stale" if state is not None else "missing",
            )
            return self._direct_resolution(query)

        correction_fallback = self._build_correction_resolution(query=query, state=state)
        if correction_fallback is not None:
            logger.info(
                "conversation_resolution context_id=%s is_follow_up=true "
                "rewrite_method=correction_preferred original=%r effective=%r topic=%s",
                context_id,
                query,
                correction_fallback.effective_query,
                correction_fallback.active_topic,
            )
            return correction_fallback

        graduation_akts_follow_up_query = _build_graduation_akts_follow_up_query(
            query,
            state=state,
        )
        if graduation_akts_follow_up_query:
            logger.info(
                "conversation_resolution context_id=%s is_follow_up=true "
                "rewrite_method=graduation_akts_follow_up original=%r effective=%r topic=%s",
                context_id,
                query,
                graduation_akts_follow_up_query,
                state.active_topic,
            )
            return ConversationResolution(
                original_query=query,
                effective_query=graduation_akts_follow_up_query,
                is_follow_up=True,
                used_context=graduation_akts_follow_up_query != query,
                active_topic=state.active_topic or "Mezuniyet ve Akademik Durum",
                department_hints=[Department.STUDENT_AFFAIRS],
                source_hints=_source_hints_for_follow_up(
                    state,
                    topic=state.active_topic,
                    query=graduation_akts_follow_up_query,
                ),
                task_type_hint=TaskType.PROCEDURE_QUERY,
                announcement_context=False,
                rewrite_method="heuristic",
                standalone_query=graduation_akts_follow_up_query,
                operation="same_topic",
                policy_facet="graduation_akts",
                question_type="graduation_akts",
                confidence=0.9,
            )

        course_slot_fragment_query = _build_course_slot_fragment_query(query, state=state)
        if course_slot_fragment_query:
            topic = state.active_topic or "Mufredat ve Ders Yapisi"
            logger.info(
                "conversation_resolution context_id=%s is_follow_up=true "
                "rewrite_method=course_slot_fragment original=%r effective=%r topic=%s",
                context_id,
                query,
                course_slot_fragment_query,
                topic,
            )
            return ConversationResolution(
                original_query=query,
                effective_query=course_slot_fragment_query,
                is_follow_up=True,
                used_context=True,
                active_topic=topic,
                department_hints=_course_reference_departments(state),
                source_hints=_source_hints_for_follow_up(
                    state,
                    topic=topic,
                    query=course_slot_fragment_query,
                ),
                task_type_hint=TaskType.COURSE_QUERY,
                announcement_context=False,
                rewrite_method="answer_fragment",
                standalone_query=course_slot_fragment_query,
                operation="answer_slot",
                confidence=0.9,
            )

        course_reference_query = _build_course_reference_query(query, state=state)
        if course_reference_query:
            topic = state.active_topic or "Mufredat ve Ders Yapisi"
            logger.info(
                "conversation_resolution context_id=%s is_follow_up=true "
                "rewrite_method=course_reference original=%r effective=%r topic=%s",
                context_id,
                query,
                course_reference_query,
                topic,
            )
            return ConversationResolution(
                original_query=query,
                effective_query=course_reference_query,
                is_follow_up=True,
                used_context=True,
                active_topic=topic,
                department_hints=_course_reference_departments(state),
                source_hints=_source_hints_for_follow_up(
                    state,
                    topic=topic,
                    query=course_reference_query,
                ),
                task_type_hint=TaskType.COURSE_QUERY,
                announcement_context=False,
                rewrite_method="heuristic",
                standalone_query=course_reference_query,
                operation="same_topic",
                confidence=0.85,
            )

        deterministic_answer_fragment_query = _build_answer_fragment_query(
            query,
            state=state,
        )
        if deterministic_answer_fragment_query:
            fragment_inferred_topic = self._infer_topic(deterministic_answer_fragment_query)
            if _last_answer_explicitly_requests_application_type(state.last_assistant_answer):
                fragment_topic = (
                    fragment_inferred_topic
                    or state.active_topic
                    or self._infer_topic(state.last_resolved_query)
                    or self._infer_topic(state.last_user_query)
                )
            else:
                fragment_topic = (
                    state.active_topic
                    or self._infer_topic(state.last_resolved_query)
                    or self._infer_topic(state.last_user_query)
                    or fragment_inferred_topic
                )
            fragment_departments = list(
                dict.fromkeys(
                    [
                        *self._parse_departments(state.last_departments),
                        *_departments_for_topic(fragment_topic),
                    ]
                )
            )
            logger.info(
                "conversation_resolution context_id=%s is_follow_up=true "
                "rewrite_method=answer_fragment original=%r effective=%r topic=%s",
                context_id,
                query,
                deterministic_answer_fragment_query,
                fragment_topic,
            )
            return ConversationResolution(
                original_query=query,
                effective_query=deterministic_answer_fragment_query,
                is_follow_up=True,
                used_context=deterministic_answer_fragment_query != query,
                active_topic=fragment_topic,
                department_hints=fragment_departments,
                source_hints=_source_hints_for_follow_up(
                    state,
                    topic=fragment_topic,
                    query=deterministic_answer_fragment_query,
                ),
                task_type_hint=self._parse_task_type(state.last_task_type),
                announcement_context=self._has_announcement_department_hint(state.last_departments),
                rewrite_method="answer_fragment",
                standalone_query=deterministic_answer_fragment_query,
                operation="answer_slot",
                confidence=0.85,
            )

        heuristic = self._classify_follow_up(query=query, state=state)
        if not heuristic["is_follow_up"]:
            if (
                heuristic.get("needs_llm_decision")
                and settings.conversation.rewrite_with_llm
                and llm_service is not None
            ):
                llm_resolution = await self._rewrite_with_llm(
                    query=query,
                    state=state,
                    llm_service=llm_service,
                    llm_profile=llm_profile,
                    student_department=student_department,
                    student_faculty=student_faculty,
                    student_type=student_type,
                    allow_follow_up_downgrade=True,
                )
                if llm_resolution is not None:
                    logger.info(
                        "conversation_resolution context_id=%s ambiguous_llm_decision=%s "
                        "original=%r effective=%r topic=%s",
                        context_id,
                        llm_resolution.is_follow_up,
                        query,
                        llm_resolution.effective_query,
                        llm_resolution.active_topic,
                    )
                    return llm_resolution

            logger.info(
                "conversation_resolution context_id=%s is_follow_up=false "
                "topic=%s original=%r",
                context_id,
                heuristic["topic"],
                query,
            )
            return ConversationResolution(
                original_query=query,
                effective_query=query,
                is_follow_up=False,
                used_context=False,
                active_topic=heuristic["topic"],
                department_hints=[],
                source_hints=[],
                rewrite_method="none",
                standalone_query=query,
                operation="new_topic",
                confidence=0.9,
            )

        rewrite_method = "heuristic"
        llm_resolution = None
        if heuristic.get("operation") == "clarify":
            effective_query = (
                state.last_resolved_query
                or state.last_user_query
                or _build_heuristic_follow_up_query(query, topic=state.active_topic)
            )
            department_hints = list(
                dict.fromkeys(
                    [
                        *self._parse_departments(state.last_departments),
                        *_departments_for_topic(state.active_topic),
                    ]
                )
            )
            return ConversationResolution(
                original_query=query,
                effective_query=effective_query,
                is_follow_up=True,
                used_context=True,
                active_topic=state.active_topic,
                department_hints=department_hints,
                source_hints=_source_hints_for_follow_up(
                    state,
                    topic=state.active_topic,
                    query=effective_query,
                ),
                task_type_hint=self._parse_task_type(state.last_task_type),
                student_type_hint=_infer_student_type_from_state(state),
                announcement_context=self._has_announcement_department_hint(state.last_departments),
                rewrite_method="clarify",
                standalone_query=effective_query,
                operation="clarify",
                question_type="explanation",
                confidence=0.9,
            )
        if settings.conversation.rewrite_with_llm and llm_service is not None:
            llm_resolution = await self._rewrite_with_llm(
                query=query,
                state=state,
                llm_service=llm_service,
                llm_profile=llm_profile,
                student_department=student_department,
                student_faculty=student_faculty,
                student_type=student_type,
                allow_follow_up_downgrade=bool(heuristic.get("allow_llm_downgrade")),
            )
            if llm_resolution is not None:
                rewrite_method = "llm"

        if llm_resolution is not None:
            logger.info(
                "conversation_resolution context_id=%s is_follow_up=%s "
                "rewrite_method=%s original=%r effective=%r topic=%s",
                context_id,
                llm_resolution.is_follow_up,
                rewrite_method,
                query,
                llm_resolution.effective_query,
                llm_resolution.active_topic,
            )
            return llm_resolution

        if correction_fallback is not None:
            logger.info(
                "conversation_resolution context_id=%s is_follow_up=true "
                "rewrite_method=correction_fallback original=%r effective=%r topic=%s",
                context_id,
                query,
                correction_fallback.effective_query,
                correction_fallback.active_topic,
            )
            return correction_fallback

        effective_query = self._rewrite_with_heuristics(query=query, state=state)
        logger.info(
            "conversation_resolution context_id=%s is_follow_up=true "
            "rewrite_method=%s original=%r effective=%r topic=%s",
            context_id,
            rewrite_method,
            query,
            effective_query,
            state.active_topic,
        )
        department_hints = list(
            dict.fromkeys(
                [
                    *self._parse_departments(state.last_departments),
                    *_departments_for_topic(state.active_topic),
                ]
            )
        )
        department_hints = _filter_transient_departments_for_query(
            query=query,
            state=state,
            departments=department_hints,
        )
        return ConversationResolution(
            original_query=query,
            effective_query=effective_query,
            is_follow_up=True,
            used_context=effective_query != query,
            active_topic=state.active_topic,
            department_hints=department_hints,
            source_hints=_source_hints_for_follow_up(
                state,
                topic=state.active_topic,
                query=effective_query,
            ),
            task_type_hint=(
                TaskType.PROCEDURE_QUERY
                if _query_requests_primary_topic_only(query, state)
                else self._parse_task_type(state.last_task_type)
            ),
            student_type_hint=_infer_student_type_from_state(state),
            announcement_context=self._has_announcement_department_hint(state.last_departments),
            rewrite_method=rewrite_method,
            standalone_query=effective_query if effective_query != query else None,
            operation="same_topic",
            confidence=0.75,
        )

    async def record_turn(
        self,
        *,
        context_id: str,
        user_query: str,
        resolved_query: str,
        assistant_answer: str,
        departments: Sequence[str],
        sources: Sequence[RAGSource],
        is_follow_up: bool,
        task_type: TaskType | None,
        active_topic: str | None = None,
    ) -> None:
        """Persist the final turn and refresh rolling state."""
        if not settings.conversation.enabled or not context_id or not user_query.strip():
            return

        compact_user_query = _compact_text(
            user_query,
            max_len=_STATE_QUERY_PREVIEW_MAX_CHARS,
        )
        compact_resolved_query = _compact_text(
            resolved_query,
            max_len=_STATE_QUERY_PREVIEW_MAX_CHARS,
        )
        stored_user_query = _compact_text(
            user_query,
            max_len=_TURN_QUERY_PREVIEW_MAX_CHARS,
        )
        stored_resolved_query = _compact_text(
            resolved_query,
            max_len=_TURN_QUERY_PREVIEW_MAX_CHARS,
        )
        stored_assistant_answer = _compact_text(
            assistant_answer,
            max_len=_TURN_ANSWER_PREVIEW_MAX_CHARS,
        )
        answer_summary = _compact_text(
            assistant_answer,
            max_len=settings.conversation.max_answer_summary_chars,
        )
        source_refs = self._extract_source_refs(sources)
        topic = active_topic or self._infer_topic(resolved_query)
        async with self._session_provider() as session:
            turn_index = await self._next_turn_index(session=session, context_id=context_id)
            turn = ConversationTurn(
                context_id=context_id,
                turn_index=turn_index,
                user_query=stored_user_query,
                resolved_query=stored_resolved_query,
                assistant_answer=stored_assistant_answer,
                answer_summary=answer_summary,
                active_topic=topic,
                task_type=task_type.value if task_type else None,
                is_follow_up=is_follow_up,
                departments=list(dict.fromkeys(departments)),
                source_refs=source_refs,
                turn_metadata={
                    "source_count": len(sources),
                    "user_query_length": len((user_query or "").strip()),
                    "resolved_query_length": len((resolved_query or "").strip()),
                    "assistant_answer_length": len((assistant_answer or "").strip()),
                    "recorded_at": self._now_provider().isoformat(),
                },
            )
            session.add(turn)
            await session.flush()

            state = await self._load_or_create_state(session=session, context_id=context_id)
            state.active_topic = topic
            state.rolling_summary = self._build_rolling_summary(
                existing_summary=state.rolling_summary,
                user_query=resolved_query,
                answer_summary=answer_summary,
            )
            state.active_entities = self._merge_entities(
                existing=state.active_entities,
                topic=topic,
                query=resolved_query,
            )
            state.last_departments = list(dict.fromkeys(departments))
            state.last_source_refs = source_refs
            state.last_task_type = task_type.value if task_type else None
            state.last_turn_id = turn.id
            state.last_user_query = compact_user_query
            state.last_resolved_query = compact_resolved_query
            state.last_assistant_answer = answer_summary
            state.turn_count = turn_index
            await session.flush()

        # Write-through: update Redis cache with fresh state
        await set_cached_state(
            ConversationStateData(
                context_id=context_id,
                active_topic=topic,
                rolling_summary=state.rolling_summary,
                active_entities=list(state.active_entities or []),
                last_departments=list(dict.fromkeys(departments)),
                last_source_refs=source_refs,
                last_task_type=task_type.value if task_type else None,
                last_turn_id=turn.id,
                last_user_query=compact_user_query,
                last_resolved_query=compact_resolved_query,
                last_assistant_answer=answer_summary,
                turn_count=turn_index,
                updated_at=self._now_provider(),
            )
        )

    @staticmethod
    def _direct_resolution(query: str) -> ConversationResolution:
        return ConversationResolution(
            original_query=query,
            effective_query=query,
            is_follow_up=False,
            used_context=False,
            active_topic=None,
            department_hints=[],
            source_hints=[],
            rewrite_method="none",
            standalone_query=query,
            operation="new_topic",
            confidence=0.9,
        )

    def _build_correction_resolution(
        self,
        *,
        query: str,
        state: ConversationStateData,
    ) -> ConversationResolution | None:
        normalized_query = normalize_text(query)
        if not any(marker in normalized_query for marker in _CORRECTION_FOLLOW_UP_MARKERS):
            return None

        schedule_term = _extract_schedule_term_correction(query)
        if schedule_term and _has_schedule_context(state):
            previous_question = (state.last_resolved_query or state.last_user_query or "").strip()
            if previous_question:
                effective_query = _append_schedule_term_to_query(previous_question, schedule_term)
                return ConversationResolution(
                    original_query=query,
                    effective_query=effective_query,
                    is_follow_up=True,
                    used_context=True,
                    active_topic=state.active_topic,
                    department_hints=[Department.ACADEMIC_PROGRAMS],
                    source_hints=_source_hints_for_follow_up(
                        state,
                        topic=state.active_topic,
                        query=effective_query,
                    ),
                    task_type_hint=TaskType.COURSE_QUERY,
                    announcement_context=False,
                    rewrite_method="correction",
                    standalone_query=effective_query,
                    operation="correction",
                    confidence=0.9,
                )

        corrected_topic = _infer_corrected_topic_from_correction(query)
        if not corrected_topic:
            return None

        previous_question = (state.last_user_query or state.last_resolved_query or "").strip()
        if not previous_question:
            return None

        effective_query = self._rewrite_previous_question_for_corrected_topic(
            previous_question=previous_question,
            corrected_topic=corrected_topic,
        )
        if normalize_text(effective_query) == normalize_text(query):
            return None

        department_hints = _departments_for_topic(corrected_topic)
        if not department_hints:
            department_hints = self._parse_departments(state.last_departments)

        return ConversationResolution(
            original_query=query,
            effective_query=effective_query,
            is_follow_up=True,
            used_context=True,
            active_topic=corrected_topic,
            department_hints=department_hints,
            source_hints=[],
            task_type_hint=TaskType.PROCEDURE_QUERY if _is_application_topic(corrected_topic) else None,
            announcement_context=False,
            rewrite_method="correction",
            standalone_query=effective_query,
            operation="correction",
            confidence=0.9,
        )

    @staticmethod
    def _rewrite_previous_question_for_corrected_topic(
        *,
        previous_question: str,
        corrected_topic: str,
    ) -> str:
        topic_seed = _topic_rewrite_seed(corrected_topic)
        normalized_previous = normalize_text(previous_question)
        if not topic_seed:
            return previous_question

        if "basvuru" in normalized_previous and any(
            marker in normalized_previous
            for marker in ("tarih", "tarihleri", "ne zaman", "zaman", "son gun", "son tarih")
        ):
            return f"{topic_seed} tarihleri ne zaman?"
        if "basvuru" in normalized_previous and any(
            marker in normalized_previous
            for marker in ("belge", "belgeler", "evrak")
        ):
            return f"{topic_seed} icin hangi belgeler gerekli?"
        if any(marker in normalized_previous for marker in ("kosul", "kosullari", "sart", "sartlari")):
            return f"{topic_seed} kosullari neler?"
        if any(marker in normalized_previous for marker in ("borc", "borcum", "borcu", "harc")) and any(
            marker in normalized_previous
            for marker in ("basvurabilir", "basvurabilir miyim", "basvurabilir miydim", "engel", "olur mu")
        ):
            return f"{topic_seed} icin harc borcu basvuruya engel mi?"
        if any(marker in normalized_previous for marker in ("ucret", "harc", "katki payi", "odeme", "ne kadar")):
            return f"{topic_seed} ucreti veya harci var mi?"
        if any(
            marker in normalized_previous
            for marker in ("basvurabilir", "basvurabilir miyim", "basvurabilir miydim", "yapabilir miyim", "olur mu")
        ):
            return f"{topic_seed} icin basvurabilir miyim?"
        if "ne zaman" in normalized_previous or "tarih" in normalized_previous:
            return f"{topic_seed} ne zaman?"
        return _build_heuristic_follow_up_query(previous_question, topic=corrected_topic)

    def _is_state_stale(self, state: ConversationStateData) -> bool:
        max_age = timedelta(minutes=settings.conversation.ttl_minutes)
        updated_at = state.updated_at
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
        updated_at = updated_at.astimezone(timezone.utc)
        if self._now_provider() - updated_at > max_age:
            return True
        if settings.conversation.reset_on_build:
            build_timestamp = _parse_build_timestamp(settings.server.build_timestamp)
            if build_timestamp is not None and updated_at < build_timestamp:
                return True
        return False

    @staticmethod
    def _starts_with_any(text: str, prefixes: Sequence[str]) -> bool:
        return any(text.startswith(prefix) for prefix in prefixes)

    def _classify_follow_up(
        self,
        *,
        query: str,
        state: ConversationStateData,
    ) -> dict[str, str | bool | None]:
        normalized_query = normalize_text(query)
        query_tokens = _normalized_tokens(query)

        if (
            state.turn_count > 0
            and any(marker in normalized_query for marker in _EXPLANATION_FOLLOW_UP_MARKERS)
        ):
            return {
                "is_follow_up": True,
                "needs_llm_decision": False,
                "allow_llm_downgrade": False,
                "operation": "clarify",
                "topic": state.active_topic,
            }

        if any(marker in normalized_query for marker in _CONFUSION_OR_RESET_MARKERS):
            return {
                "is_follow_up": False,
                "needs_llm_decision": False,
                "topic": state.active_topic,
            }

        if any(marker in normalized_query for marker in _INDEPENDENT_SHORT_QUERY_MARKERS):
            return {
                "is_follow_up": False,
                "needs_llm_decision": False,
                "topic": self._infer_topic(query),
            }

        if _is_standalone_academic_calendar_query(query):
            return {
                "is_follow_up": False,
                "needs_llm_decision": False,
                "topic": self._infer_topic(query),
            }

        # Kısa / yanıt niteliğinde ifadeler follow-up olarak değerlendirilmez
        query_content_tokens = _content_tokens(query)
        short_slot_follow_up = _looks_like_short_slot_follow_up(query, state)
        if (
            "sey" in query_tokens
            and query_content_tokens
            and query_content_tokens <= _VAGUE_FOLLOW_UP_TOKENS
        ):
            return {
                "is_follow_up": False,
                "needs_llm_decision": False,
                "topic": self._infer_topic(query),
            }

        query_inferred_topic = self._infer_topic(query)
        correction_follow_up = (
            state.turn_count > 0
            and query_inferred_topic is not None
            and _looks_like_correction_follow_up(query)
        )
        if correction_follow_up:
            return {
                "is_follow_up": True,
                "needs_llm_decision": True,
                "allow_llm_downgrade": False,
                "topic": query_inferred_topic,
            }

        starts_with_follow_up = self._starts_with_any(normalized_query, _FOLLOW_UP_PREFIXES)
        pronoun_like = any(
            token in _FOLLOW_UP_PRONOUNS
            for token in query_tokens[:4]
        )
        explicit_topic_change_marker = any(
            marker in normalized_query
            for marker in _INDEPENDENT_TOPIC_CHANGE_MARKERS
        )
        if (
            state.turn_count > 0
            and state.active_topic is None
            and query_inferred_topic is not None
            and not short_slot_follow_up
            and not starts_with_follow_up
            and not pronoun_like
            and not _build_answer_fragment_query(query, state=state)
        ):
            return {
                "is_follow_up": False,
                "needs_llm_decision": False,
                "topic": query_inferred_topic,
            }

        if (
            state.active_topic is not None
            and query_inferred_topic is not None
            and normalize_text(query_inferred_topic) != normalize_text(state.active_topic)
            and explicit_topic_change_marker
            and not short_slot_follow_up
            and not starts_with_follow_up
            and (
                not pronoun_like
                or _topic_transition_score(query, state) >= _TOPIC_TRANSITION_THRESHOLD
            )
        ):
            return {
                "is_follow_up": False,
                "needs_llm_decision": False,
                "topic": query_inferred_topic,
            }

        if len(query_tokens) <= 2 and any(t in _TURBO_WORDS for t in query_tokens):
            return {
                "is_follow_up": False,
                "needs_llm_decision": False,
                "topic": state.active_topic,
            }

        # Guclu marker'lar: her zaman follow-up sinyali
        has_strong_marker = any(
            marker in normalized_query
            for marker in _STRONG_FOLLOW_UP_MARKERS
        )

        # Zayif marker'lar: yalnizca kisa sorgularda (<=5 kelime) follow-up sinyali
        # 'Erasmus basvurusu nasil yapilir?' gibi uzun bagimsiz sorulari korur
        has_weak_marker = (
            len(query_tokens) <= 3
            and any(
                marker in normalized_query
                for marker in _WEAK_FOLLOW_UP_MARKERS
            )
        )

        # Zamir kontrolu: ilk 4 token'da zamir/referans kelime var mi
        answer_fragment = (
            state.turn_count > 0
            and state.last_departments
            and _build_answer_fragment_query(query, state=state) is not None
        )
        unresolved_answer_fragment = _is_answer_fragment_follow_up(query) and not answer_fragment
        conditional_action_follow_up = (
            state.turn_count > 0
            and state.active_topic is not None
            and _looks_like_conditional_action_follow_up(query)
        )

        signal_based = (
            starts_with_follow_up
            or has_strong_marker
            or has_weak_marker
            or pronoun_like
            or answer_fragment
            or conditional_action_follow_up
        )
        short_context_follow_up = (
            state.turn_count > 0
            and not signal_based
            and not unresolved_answer_fragment
            and (1 < len(query_tokens) <= 4 or short_slot_follow_up)
        )
        if short_context_follow_up:
            new_topic = self._infer_topic(query)
            if (
                len(query_tokens) <= 2
                and
                new_topic is not None
                and state.active_topic is not None
                and normalize_text(new_topic) != normalize_text(state.active_topic)
            ):
                short_context_follow_up = False

        is_follow_up = bool(
            state.turn_count > 0
            and (signal_based or short_context_follow_up)
        )

        # Kisa sorgularda (<=4 kelime) state varsa ve hic sinyal yoksa
        # yine follow-up olarak degerlendir — LLM karar versin.
        # "Taksitle odeyebilir miyim?" gibi semantik follow-up'lari yakalar.
        # Konu degisimi kontrolu: SADECE sinyal-tabanli, marker-only follow-up'larda uygula.
        # Prefix ve zamir durumlarinda konu kontrolu ATLANIR.
        # Konu degisimi kontrolu: sadece marker tabanli follow-up'larda uygulanir.
        marker_only_follow_up = (
            is_follow_up
            and signal_based
            and not starts_with_follow_up
            and not pronoun_like
            and not conditional_action_follow_up
        )
        if marker_only_follow_up and "sey" in query_tokens:
            query_content_tokens = _content_tokens(query)
            state_context_tokens = _content_tokens(
                " ".join(
                    text
                    for text in (
                        state.active_topic,
                        state.last_user_query,
                        state.last_resolved_query,
                    )
                    if text
                )
            )
            if (
                query_content_tokens
                and query_content_tokens <= _VAGUE_FOLLOW_UP_TOKENS
                and _count_token_overlap(query_content_tokens, state_context_tokens) == 0
            ):
                is_follow_up = False

        if marker_only_follow_up:
            new_topic = self._infer_topic(query)
            if (
                new_topic is not None
                and state.active_topic is not None
                and normalize_text(new_topic) != normalize_text(state.active_topic)
                and _topic_transition_score(query, state) >= _TOPIC_TRANSITION_THRESHOLD
            ):
                is_follow_up = False

        needs_llm_decision = False
        if not is_follow_up:
            needs_llm_decision = self._should_ask_llm_for_ambiguous_follow_up(
                query=query,
                state=state,
                query_tokens=query_tokens,
                signal_based=signal_based,
            )

        return {
            "is_follow_up": is_follow_up,
            "needs_llm_decision": needs_llm_decision,
            "allow_llm_downgrade": (
                short_context_follow_up
                or answer_fragment
                or conditional_action_follow_up
                or has_weak_marker
                or needs_llm_decision
            ),
            "topic": state.active_topic if is_follow_up else self._infer_topic(query),
        }

    @staticmethod
    def _should_ask_llm_for_ambiguous_follow_up(
        *,
        query: str,
        state: ConversationStateData,
        query_tokens: Sequence[str],
        signal_based: bool,
    ) -> bool:
        """Return True when rules should defer a borderline context decision to LLM."""
        if state.turn_count <= 0 or not state.active_topic:
            return False
        if not query_tokens:
            return False

        query_content_tokens = _content_tokens(query)
        if not query_content_tokens:
            return False

        state_context = " ".join(
            text
            for text in (
                state.active_topic,
                state.last_user_query,
                state.last_resolved_query,
                state.last_assistant_answer,
            )
            if text
        )
        state_context_tokens = _content_tokens(state_context)
        overlap = _count_stem_overlap(query_content_tokens, state_context_tokens)
        transition_score = _topic_transition_score(query, state)
        inferred_topic = ConversationContextService._infer_topic(query)

        if _looks_like_conditional_action_follow_up(query):
            return True

        if (
            inferred_topic is not None
            and normalize_text(inferred_topic) != normalize_text(state.active_topic)
            and not signal_based
        ):
            return False

        if signal_based and transition_score < 0.85:
            return True
        if len(query_tokens) <= 8 and transition_score < 0.75:
            return True
        if overlap >= 1.0 and len(query_tokens) <= 12:
            return True
        return False

    async def _get_recent_turns(
        self,
        *,
        context_id: str,
        n: int = 3,
    ) -> list[ConversationTurnData]:
        """Fetch the last *n* persisted turns for richer LLM context."""
        try:
            async with self._session_provider() as session:
                result = await session.execute(
                    select(ConversationTurn)
                    .where(ConversationTurn.context_id == context_id)
                    .order_by(ConversationTurn.turn_index.desc())
                    .limit(n)
                )
                rows = result.scalars().all()
                return [self._to_turn_data(r) for r in reversed(rows)]
        except Exception:
            logger.debug("get_recent_turns_failed context_id=%s", context_id, exc_info=True)
            return []

    async def _rewrite_with_llm(
        self,
        *,
        query: str,
        state: ConversationStateData,
        llm_service: LLMService,
        llm_profile: str | None,
        student_department: str | None,
        student_faculty: str | None,
        student_type: str | None,
        allow_follow_up_downgrade: bool,
    ) -> ConversationResolution | None:
        max_recent_turns = max(0, int(settings.conversation.max_recent_turns))
        recent_turns = (
            await self._get_recent_turns(context_id=state.context_id, n=max_recent_turns)
            if max_recent_turns
            else []
        )
        prompt = self._build_follow_up_prompt(
            query=query,
            state=state,
            student_department=student_department,
            student_faculty=student_faculty,
            student_type=student_type,
            recent_turns=recent_turns,
        )
        try:
            raw = await asyncio.wait_for(
                llm_service.generate(
                    prompt=prompt,
                    system=CONVERSATION_FOLLOWUP_SYSTEM_PROMPT,
                    json_mode=True,
                    model_role="conversation",
                    llm_profile=llm_profile,
                ),
                timeout=settings.conversation.rewrite_timeout_seconds,
            )
        except Exception as exc:
            logger.warning("conversation_followup_llm_fallback reason=%s", type(exc).__name__)
            return None

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("conversation_followup_invalid_json")
            return None

        standalone_query = str(payload.get("standalone_query") or query).strip() or query
        is_follow_up = bool(payload.get("is_follow_up", True))
        operation = str(payload.get("operation") or "").strip().lower()
        correction_like_query = (
            _looks_like_correction_follow_up(query)
            and self._infer_topic(query) is not None
        )

        if correction_like_query and operation != "correct_previous_question":
            logger.warning(
                "conversation_correction_operation_missing original=%r operation=%r rewritten=%r -> fallback",
                query,
                operation,
                standalone_query,
            )
            return None

        if operation == "correct_previous_question" and not is_follow_up:
            logger.warning(
                "conversation_correction_operation_not_followup original=%r rewritten=%r -> fallback",
                query,
                standalone_query,
            )
            return None

        if not is_follow_up and not allow_follow_up_downgrade:
            is_follow_up = True
            standalone_query = query
        elif not is_follow_up:
            standalone_query = query

        if is_follow_up and operation == "correct_previous_question":
            return self._build_llm_correction_resolution(
                query=query,
                state=state,
                payload=payload,
                standalone_query=standalone_query,
            )

        if is_follow_up:
            context_texts = [
                text
                for text in (
                    state.last_resolved_query,
                    state.last_user_query,
                    state.active_topic,
                )
                if text
            ]
            if _looks_like_value_reference_follow_up(query):
                context_texts.extend(
                    text
                    for text in (
                        state.last_resolved_query,
                        state.last_user_query,
                        state.last_assistant_answer,
                        state.rolling_summary,
                    )
                    if text
                )
            heuristic_query = self._rewrite_with_heuristics(query=query, state=state)
            conditional_action_follow_up = _looks_like_conditional_action_follow_up(query)
            if conditional_action_follow_up and state.active_topic:
                topic_seed = _topic_rewrite_seed(state.active_topic)
                if topic_seed and normalize_text(topic_seed) not in normalize_text(standalone_query):
                    logger.warning(
                        "conversation_rewrite_missing_conditional_topic original=%r rewritten=%r topic=%s -> heuristic_fallback",
                        query,
                        standalone_query,
                        state.active_topic,
                    )
                    return None
            if _rewrite_carries_unrequested_finance_facet(
                query=query,
                rewritten=standalone_query,
                state=state,
            ):
                logger.warning(
                    "conversation_rewrite_carried_transient_finance_facet original=%r rewritten=%r topic=%s -> heuristic_fallback",
                    query,
                    standalone_query,
                    state.active_topic,
                )
                return None
            if not _rewrite_preserves_question_type(query, standalone_query):
                logger.warning(
                    "conversation_rewrite_changed_question_type original=%r rewritten=%r -> heuristic_fallback",
                    query,
                    standalone_query,
                )
                return None
            if not _rewrite_preserves_intent(
                query,
                standalone_query,
                context_texts=context_texts,
            ):
                logger.warning(
                    "conversation_rewrite_rejected original=%r rewritten=%r → heuristic_fallback",
                    query,
                    standalone_query,
                )
                # LLM rewrite'i reddedildi ama sorgu follow-up olabilir.
                # None dondurup heuristik fallback'e dusur.
                return None

            if not _rewrite_supplies_needed_context(
                query,
                standalone_query,
                context_texts=context_texts,
            ):
                logger.warning(
                    "conversation_rewrite_missing_context original=%r rewritten=%r → heuristic_fallback",
                    query,
                    standalone_query,
                )
                return None
            if _rewrite_adds_unscoped_detail_tokens(
                query=query,
                rewritten=standalone_query,
                heuristic_query=heuristic_query,
                topic=state.active_topic,
            ):
                logger.warning(
                    "conversation_rewrite_added_unscoped_details original=%r rewritten=%r -> heuristic_fallback",
                    query,
                    standalone_query,
                )
                return None

        carry_over_departments = self._parse_departments(payload.get("carry_over_departments") or [])
        clarification_message = str(payload.get("clarification_message") or "").strip() or None
        resolved_active_topic = str(payload.get("active_topic") or state.active_topic or "").strip() or None
        previous_departments = self._parse_departments(state.last_departments)
        if is_follow_up and _looks_like_conditional_action_follow_up(query) and state.active_topic:
            resolved_active_topic = state.active_topic
            carry_over_departments = list(
                dict.fromkeys(
                    [
                        *previous_departments,
                        *_departments_for_topic(state.active_topic),
                        *carry_over_departments,
                    ]
                )
            )
        if is_follow_up:
            carry_over_departments = _filter_transient_departments_for_query(
                query=query,
                state=state,
                departments=(carry_over_departments or previous_departments),
            )
        if payload.get("needs_clarification") and not _should_accept_llm_clarification(
            query=query,
            state=state,
            is_follow_up=is_follow_up,
            clarification_message=clarification_message,
        ):
            clarification_message = None
        return ConversationResolution(
            original_query=query,
            effective_query=standalone_query,
            is_follow_up=is_follow_up,
            used_context=standalone_query != query,
            active_topic=resolved_active_topic,
            department_hints=carry_over_departments if is_follow_up else [],
            source_hints=(
                _source_hints_for_follow_up(
                    state,
                    topic=resolved_active_topic,
                    query=standalone_query,
                )
                if is_follow_up
                else []
            ),
            task_type_hint=(
                (
                    TaskType.PROCEDURE_QUERY
                    if _query_requests_primary_topic_only(query, state)
                    else self._parse_task_type(state.last_task_type)
                )
                if is_follow_up
                else None
            ),
            clarification_message=(
                clarification_message if payload.get("needs_clarification") and clarification_message else None
            ),
            announcement_context=self._has_announcement_department_hint(state.last_departments) if is_follow_up else False,
            rewrite_method="llm",
            standalone_query=standalone_query if standalone_query != query else None,
            operation=(
                "same_topic"
                if is_follow_up
                else "new_topic"
            ),
            confidence=0.8 if is_follow_up else 0.9,
        )

    def _build_llm_correction_resolution(
        self,
        *,
        query: str,
        state: ConversationStateData,
        payload: dict,
        standalone_query: str,
    ) -> ConversationResolution | None:
        corrected_topic = (
            _infer_corrected_topic_from_correction(query)
            or (
                str(payload.get("active_topic") or "").strip()
                if not _looks_like_correction_follow_up(query)
                else ""
            )
            or self._infer_topic(query)
            or state.active_topic
        )
        if not corrected_topic:
            return None

        previous_question = (state.last_user_query or state.last_resolved_query or "").strip()
        if not previous_question:
            return None

        normalized_query = normalize_text(query)
        normalized_standalone = normalize_text(standalone_query)
        if not standalone_query or normalized_standalone == normalized_query:
            return None

        topic_seed = _topic_rewrite_seed(corrected_topic)
        topic_tokens = _content_tokens(corrected_topic) | _content_tokens(topic_seed)
        standalone_tokens = _content_tokens(standalone_query)
        if topic_tokens and _count_stem_overlap(topic_tokens, standalone_tokens) <= 0:
            logger.warning(
                "conversation_correction_missing_topic original=%r rewritten=%r topic=%s -> fallback",
                query,
                standalone_query,
                corrected_topic,
            )
            return None

        if not _rewrite_preserves_question_type(previous_question, standalone_query):
            logger.warning(
                "conversation_correction_changed_previous_question_type previous=%r rewritten=%r -> fallback",
                previous_question,
                standalone_query,
            )
            return None

        carry_over_departments = self._parse_departments(payload.get("carry_over_departments") or [])
        department_hints = list(
            dict.fromkeys(
                [
                    *(carry_over_departments or []),
                    *_departments_for_topic(corrected_topic),
                ]
            )
        )
        if not department_hints:
            department_hints = self._parse_departments(state.last_departments)
        department_hints = _filter_transient_departments_for_query(
            query=standalone_query,
            state=state,
            departments=department_hints,
        )

        return ConversationResolution(
            original_query=query,
            effective_query=standalone_query,
            is_follow_up=True,
            used_context=True,
            active_topic=corrected_topic,
            department_hints=department_hints,
            source_hints=[],
            task_type_hint=TaskType.PROCEDURE_QUERY if _is_application_topic(corrected_topic) else None,
            announcement_context=False,
            rewrite_method="llm",
            standalone_query=standalone_query,
            operation="correction",
            confidence=0.85,
        )

    @staticmethod
    def _rewrite_with_heuristics(
        *,
        query: str,
        state: ConversationStateData,
    ) -> str:
        previous_program = next(
            (
                program
                for program in (
                    _infer_program_fragment(state.last_resolved_query or ""),
                    _infer_program_fragment(state.last_user_query or ""),
                    _infer_program_fragment(state.last_assistant_answer or ""),
                )
                if program
            ),
            None,
        )
        normalized_query = normalize_text(query)
        if (
            previous_program
            and "yariyil" in normalized_query
            and any(marker in normalized_query for marker in ("ders", "mufredat", "program"))
        ):
            stripped_query = _strip_follow_up_prefixes(query)
            if stripped_query:
                return f"{previous_program} {stripped_query}".strip()

        if _looks_like_short_slot_follow_up(query, state):
            if previous_program:
                stripped_query = _strip_follow_up_prefixes(query)
                if stripped_query:
                    return f"{previous_program} {stripped_query}".strip()

        if not state.active_topic:
            return query
        lowered = normalize_text(query)
        topic_seed = _topic_rewrite_seed(state.active_topic)
        normalized_topic = normalize_text(state.active_topic)
        normalized_seed = normalize_text(topic_seed)
        if _looks_like_conditional_action_follow_up(query):
            stripped_query = _strip_follow_up_prefixes(query)
            if stripped_query and normalized_seed not in normalize_text(stripped_query):
                return f"{topic_seed} icin {stripped_query}".strip()
        if (normalized_topic and normalized_topic in lowered) or (
            normalized_seed and normalized_seed in lowered
        ):
            return query
        return _build_heuristic_follow_up_query(query, topic=state.active_topic)

    def _build_follow_up_prompt(
        self,
        *,
        query: str,
        state: ConversationStateData,
        student_department: str | None,
        student_faculty: str | None,
        student_type: str | None,
        recent_turns: list[ConversationTurnData] | None = None,
    ) -> str:
        payload = {
            "current_query": query,
            "previous_turn": {
                "user_question": state.last_user_query,
                "resolved_question": state.last_resolved_query,
                "answer_summary": state.last_assistant_answer,
            },
            "recent_turns": [
                {
                    "turn_index": t.turn_index,
                    "user_question": t.user_query,
                    "resolved_question": t.resolved_query,
                    "answer_summary": t.answer_summary,
                    "active_topic": t.active_topic,
                }
                for t in (recent_turns or [])
            ],
            "conversation_state": {
                "active_topic": state.active_topic,
                "rolling_summary": state.rolling_summary,
                "last_departments": state.last_departments,
                "last_source_refs": state.last_source_refs,
                "last_task_type": state.last_task_type,
                "active_entities": state.active_entities,
            },
            "profile_context": {
                "student_department": student_department,
                "student_faculty": student_faculty,
                "student_type": student_type,
            },
            "output_schema": {
                "is_follow_up": True,
                "operation": "new_topic|follow_primary_topic|follow_last_facet|answer_fragment|correct_previous_question|clarify",
                "standalone_query": "string",
                "active_topic": "string|null",
                "carry_over_departments": ["student_affairs"],
                "base_turn_index": "integer|null",
                "preserve_question_type": "date|amount|eligibility|procedure|document|location|definition|unknown|null",
                "dropped_facets": ["finance"],
                "needs_clarification": False,
                "clarification_message": "string|null",
            },
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)

    async def _next_turn_index(self, *, session: AsyncSession, context_id: str) -> int:
        result = await session.execute(
            select(func.max(ConversationTurn.turn_index)).where(
                ConversationTurn.context_id == context_id
            )
        )
        current_max = result.scalar_one()
        return int(current_max or 0) + 1

    async def _load_or_create_state(
        self,
        *,
        session: AsyncSession,
        context_id: str,
    ) -> ConversationState:
        result = await session.execute(
            select(ConversationState).where(ConversationState.context_id == context_id)
        )
        row = result.scalar_one_or_none()
        if row is not None:
            return row

        row = ConversationState(context_id=context_id)
        session.add(row)
        await session.flush()
        return row

    _ANNOUNCEMENT_DEPT_HINT = "announcement"

    @staticmethod
    def _parse_departments(raw_departments: Sequence[str]) -> list[Department]:
        parsed: list[Department] = []
        for item in raw_departments:
            try:
                parsed.append(Department(str(item)))
            except ValueError:
                continue
        return list(dict.fromkeys(parsed))

    @staticmethod
    def _has_announcement_department_hint(raw_departments: Sequence[str]) -> bool:
        return "announcement" in raw_departments

    @staticmethod
    def _parse_task_type(raw_task_type: str | None) -> TaskType | None:
        if not raw_task_type:
            return None
        try:
            return TaskType(raw_task_type)
        except ValueError:
            return None

    @staticmethod
    def _infer_topic(query: str) -> str | None:
        normalized_query = normalize_text(query)
        course_code_match = _first_valid_course_code_match(query)
        if course_code_match:
            return f"{course_code_match.group(0).replace(' ', '')} dersi"

        # En uzun/spesifik marker eslesmesini onceliklendir.
        # "kayit dondurma" > "kayit" gibi generic eslesmelerin spesifik olanlari yutmasini onle.
        best_topic: str | None = None
        best_marker_len = 0
        for topic, markers in _TOPIC_PATTERNS:
            for marker in markers:
                if marker in normalized_query and len(marker) > best_marker_len:
                    best_topic = topic
                    best_marker_len = len(marker)
        return best_topic

    @staticmethod
    def _extract_source_refs(sources: Sequence[RAGSource]) -> list[str]:
        refs: list[str] = []
        for source in sources:
            metadata = source.metadata or {}
            ref = (
                metadata.get("title")
                or metadata.get("file_name")
                or metadata.get("source")
                or metadata.get("source_url")
            )
            if ref:
                refs.append(str(ref).strip())
        deduped = [ref for ref in dict.fromkeys(refs) if ref]
        return deduped[: settings.conversation.max_source_refs]

    @staticmethod
    def _merge_entities(
        *,
        existing: Sequence[str] | None,
        topic: str | None,
        query: str,
    ) -> list[str]:
        merged = list(existing or [])
        if topic:
            merged.append(topic)
        merged.extend(
            match.group(0).replace(" ", "")
            for match in _COURSE_CODE_PATTERN.finditer(query)
            if _is_valid_course_code_match(match)
        )
        return list(dict.fromkeys(entity for entity in merged if entity))

    @staticmethod
    def _build_rolling_summary(
        *,
        existing_summary: str | None,
        user_query: str,
        answer_summary: str | None,
    ) -> str:
        current_piece = f"Soru: {_compact_text(user_query, max_len=180)} | Yanit: {answer_summary or ''}".strip()
        previous_pieces = [
            piece.strip()
            for piece in (existing_summary or "").split(" || ")
            if piece.strip()
        ]
        keep_count = max(settings.conversation.max_turns_in_summary - 1, 0)
        pieces = [*previous_pieces[-keep_count:], current_piece]
        merged = " || ".join(pieces)
        return _compact_text(merged, max_len=settings.conversation.max_rolling_summary_chars)

    @staticmethod
    def _to_state_data(row: ConversationState) -> ConversationStateData:
        return ConversationStateData(
            context_id=row.context_id,
            active_topic=row.active_topic,
            rolling_summary=row.rolling_summary,
            active_entities=list(row.active_entities or []),
            last_departments=list(row.last_departments or []),
            last_source_refs=list(row.last_source_refs or []),
            last_task_type=row.last_task_type,
            last_turn_id=row.last_turn_id,
            last_user_query=row.last_user_query,
            last_resolved_query=row.last_resolved_query,
            last_assistant_answer=row.last_assistant_answer,
            turn_count=row.turn_count,
            updated_at=row.updated_at,
        )

    @staticmethod
    def _to_turn_data(row: ConversationTurn) -> ConversationTurnData:
        return ConversationTurnData(
            id=row.id,
            context_id=row.context_id,
            turn_index=row.turn_index,
            user_query=row.user_query,
            resolved_query=row.resolved_query,
            assistant_answer=row.assistant_answer,
            answer_summary=row.answer_summary,
            active_topic=row.active_topic,
            task_type=row.task_type,
            is_follow_up=row.is_follow_up,
            departments=list(row.departments or []),
            source_refs=list(row.source_refs or []),
            created_at=row.created_at,
        )


def _compact_text(text: str | None, *, max_len: int) -> str:
    value = (text or "").strip()
    if len(value) <= max_len:
        return value
    return value[: max_len - 3].rstrip() + "..."
