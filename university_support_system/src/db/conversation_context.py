"""Conversation state service for multi-turn query resolution."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Callable, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.constants import Department, TaskType
from src.core.text_normalization import normalize_text
from src.db.connection import get_session
from src.cache.conversation_cache import get_cached_state, set_cached_state
from src.db.conversation_models import ConversationState, ConversationTurn
from src.db.schemas import RAGSource
from src.llm.prompt_templates import CONVERSATION_FOLLOWUP_SYSTEM_PROMPT

if TYPE_CHECKING:
    from src.llm.llm_service import LLMService

logger = logging.getLogger(__name__)

_STATE_QUERY_PREVIEW_MAX_CHARS = 180
_TURN_QUERY_PREVIEW_MAX_CHARS = 240
_TURN_ANSWER_PREVIEW_MAX_CHARS = 420

_COURSE_CODE_PATTERN = re.compile(r"\b[A-ZÇĞİÖŞÜ]{2,6}\s?\d{3,4}\b", re.IGNORECASE)
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
}
_CONFUSION_OR_RESET_MARKERS = (
    "isler karisti",
    "kafam karisti",
    "karisti",
    "anlamadim",
    "emin degilim",
    "bilmiyorum",
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
)
_EXACT_FOLLOW_UP_ANSWER_MARKERS = {
    "turk",
    "yerli",
    "uluslararasi",
    "yabanci",
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


def _normalized_tokens(text: str) -> list[str]:
    return _WORD_TOKEN_PATTERN.findall(normalize_text(text))


def _content_tokens(text: str) -> set[str]:
    return set(_normalized_tokens(text)) - _INTENT_STOP_WORDS


def _count_token_overlap(base_tokens: set[str], candidate_tokens: set[str]) -> int:
    return len(base_tokens & candidate_tokens)


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
    return _count_token_overlap(context_tokens, rewritten_tokens) > 0


_QUESTION_TYPE_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("ne_zaman", ("ne zaman", "hangi tarihte", "son tarihi", "son tarih")),
    ("ne_kadar", ("ne kadar", "kac tl", "kac para")),
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


def _build_answer_fragment_query(query: str, *, state: "ConversationStateData") -> str | None:
    """Merge short answer fragments with the last concrete question."""
    if not _is_answer_fragment_follow_up(query):
        return None
    previous_query = (state.last_resolved_query or state.last_user_query or "").strip()
    if not previous_query:
        return None
    normalized_current = normalize_text(query)
    if normalized_current and normalized_current in normalize_text(previous_query):
        return previous_query
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
    tuition_context = (
        state.last_task_type == TaskType.TUITION_QUERY.value
        or any(
            marker in previous_context
            for marker in ("harc", "ucret", "ogrenim ucreti", "katki payi")
        )
    )
    if tuition_context:
        return f"{previous_query.rstrip('?.!,;:')} {query}".strip()
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
    ("CAP / Cift Anadal", ("cap", "cift anadal", "cift ana dal", "ikinci lisans")),
    ("Yandal", ("yandal", "yan dal")),
    ("Erasmus ve Uluslararasi Surecler", ("erasmus", "ikamet", "yos", "tomer", "denklik", "mevlana", "farabi", "degisim programi")),
    ("Harc ve Ogrenim Ucretleri", ("harc", "katki payi", "ucret", "odeme", "taksit", "ogrenim ucreti")),
    ("Burs ve Destekler", ("burs", "yemek bursu", "kismi zamanli", "basari bursu", "ihtiyac bursu")),
    ("Kayit ve Akademik Takvim", ("kayit", "ders kaydi", "akademik takvim", "muafiyet", "kayit donemi", "ders secimi")),
    ("Kayit Dondurma ve Silme", ("kayit dondurma", "donem dondurma", "kayit sildirme", "ilisik kesme")),
    ("Mezuniyet ve Akademik Durum", ("mezuniyet", "gno", "transkript", "diploma", "not ortalamasi", "azami sure")),
    ("Staj ve Uygulamali Egitim", ("staj", "mup", "sanayi uygulamasi", "bitirme projesi", "zorunlu staj", "mesleki uygulama")),
    ("Sinav ve Degerlendirme", ("sinav", "butunleme", "final", "vize", "mazeret", "bagil degerlendirme", "harf notu")),
    ("Yatay ve Dikey Gecis", ("yatay gecis", "dikey gecis", "kurum ici", "kurumlar arasi")),
    ("Mufredat ve Ders Yapisi", ("mufredat", "onkosul", "ders programi", "akts", "secmeli", "zorunlu ders")),
    ("Mevzuat ve Yonergeler", ("yonerge", "yonetmelik", "madde", "prosedur", "genelge")),
    ("Belgeler", ("ogrenci belgesi", "transkript belgesi", "diploma eki", "tecil", "askerlik belgesi")),
    ("Yaz Okulu", ("yaz okulu", "yaz donemi")),
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
    "Devamsizlik": "devamsizlik",
}


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
    clarification_message: str | None = None
    announcement_context: bool = False
    rewrite_method: str = "none"  # none | heuristic | llm | answer_fragment
    standalone_query: str | None = None  # explicit standalone form for telemetry


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

        heuristic = self._classify_follow_up(query=query, state=state)
        if not heuristic["is_follow_up"]:
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
            )

        rewrite_method = "heuristic"
        llm_resolution = None
        deterministic_answer_fragment_query = _build_answer_fragment_query(
            query,
            state=state,
        )
        if deterministic_answer_fragment_query:
            logger.info(
                "conversation_resolution context_id=%s is_follow_up=true "
                "rewrite_method=answer_fragment original=%r effective=%r topic=%s",
                context_id,
                query,
                deterministic_answer_fragment_query,
                state.active_topic,
            )
            return ConversationResolution(
                original_query=query,
                effective_query=deterministic_answer_fragment_query,
                is_follow_up=True,
                used_context=deterministic_answer_fragment_query != query,
                active_topic=state.active_topic,
                department_hints=self._parse_departments(state.last_departments),
                source_hints=list(state.last_source_refs),
                task_type_hint=self._parse_task_type(state.last_task_type),
                announcement_context=self._has_announcement_department_hint(state.last_departments),
                rewrite_method="answer_fragment",
                standalone_query=deterministic_answer_fragment_query,
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
        return ConversationResolution(
            original_query=query,
            effective_query=effective_query,
            is_follow_up=True,
            used_context=effective_query != query,
            active_topic=state.active_topic,
            department_hints=self._parse_departments(state.last_departments),
            source_hints=list(state.last_source_refs),
            task_type_hint=self._parse_task_type(state.last_task_type),
            announcement_context=self._has_announcement_department_hint(state.last_departments),
            rewrite_method=rewrite_method,
            standalone_query=effective_query if effective_query != query else None,
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
        )

    def _is_state_stale(self, state: ConversationStateData) -> bool:
        max_age = timedelta(minutes=settings.conversation.ttl_minutes)
        return self._now_provider() - state.updated_at > max_age

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

        if any(marker in normalized_query for marker in _CONFUSION_OR_RESET_MARKERS):
            return {
                "is_follow_up": False,
                "topic": state.active_topic,
            }

        if any(marker in normalized_query for marker in _INDEPENDENT_SHORT_QUERY_MARKERS):
            return {
                "is_follow_up": False,
                "topic": self._infer_topic(query),
            }

        if _is_standalone_academic_calendar_query(query):
            return {
                "is_follow_up": False,
                "topic": self._infer_topic(query),
            }

        # Kısa / yanıt niteliğinde ifadeler follow-up olarak değerlendirilmez
        if len(query_tokens) <= 2 and any(t in _TURBO_WORDS for t in query_tokens):
            return {
                "is_follow_up": False,
                "topic": state.active_topic,
            }

        starts_with_follow_up = self._starts_with_any(normalized_query, _FOLLOW_UP_PREFIXES)

        # Guclu marker'lar: her zaman follow-up sinyali
        has_strong_marker = any(
            marker in normalized_query
            for marker in _STRONG_FOLLOW_UP_MARKERS
        )

        # Zayif marker'lar: yalnizca kisa sorgularda (<=5 kelime) follow-up sinyali
        # 'Erasmus basvurusu nasil yapilir?' gibi uzun bagimsiz sorulari korur
        has_weak_marker = (
            len(query_tokens) <= 5
            and any(
                marker in normalized_query
                for marker in _WEAK_FOLLOW_UP_MARKERS
            )
        )

        # Zamir kontrolu: ilk 4 token'da zamir/referans kelime var mi
        pronoun_like = any(
            token in _FOLLOW_UP_PRONOUNS
            for token in query_tokens[:4]
        )
        answer_fragment = (
            state.turn_count > 0
            and state.last_departments
            and _is_answer_fragment_follow_up(query)
        )

        signal_based = (
            starts_with_follow_up
            or has_strong_marker
            or has_weak_marker
            or pronoun_like
            or answer_fragment
        )
        short_context_follow_up = (
            state.turn_count > 0
            and not signal_based
            and 1 < len(query_tokens) <= 4
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

        if marker_only_follow_up and len(query_tokens) > 3:
            new_topic = self._infer_topic(query)
            if (
                new_topic is not None
                and state.active_topic is not None
                and normalize_text(new_topic) != normalize_text(state.active_topic)
            ):
                is_follow_up = False

        return {
            "is_follow_up": is_follow_up,
            "allow_llm_downgrade": (
                short_context_follow_up or answer_fragment or has_weak_marker
            ),
            "topic": state.active_topic if is_follow_up else self._infer_topic(query),
        }

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
        prompt = self._build_follow_up_prompt(
            query=query,
            state=state,
            student_department=student_department,
            student_faculty=student_faculty,
            student_type=student_type,
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

        if not is_follow_up and not allow_follow_up_downgrade:
            is_follow_up = True
            standalone_query = query
        elif not is_follow_up:
            standalone_query = query

        if is_follow_up:
            context_texts = [state.active_topic] if state.active_topic else []
            if _is_answer_fragment_follow_up(query):
                context_texts.extend(
                    text
                    for text in (state.last_resolved_query, state.last_user_query)
                    if text
                )
            heuristic_query = self._rewrite_with_heuristics(query=query, state=state)
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
                    "conversation_rewrite_missing_context original=%r rewritten=%r â†’ heuristic_fallback",
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
            active_topic=str(payload.get("active_topic") or state.active_topic or "").strip() or None,
            department_hints=(carry_over_departments or self._parse_departments(state.last_departments)) if is_follow_up else [],
            source_hints=list(state.last_source_refs) if is_follow_up else [],
            task_type_hint=self._parse_task_type(state.last_task_type) if is_follow_up else None,
            clarification_message=(
                clarification_message if payload.get("needs_clarification") and clarification_message else None
            ),
            announcement_context=self._has_announcement_department_hint(state.last_departments) if is_follow_up else False,
            rewrite_method="llm",
            standalone_query=standalone_query if standalone_query != query else None,
        )

    @staticmethod
    def _rewrite_with_heuristics(
        *,
        query: str,
        state: ConversationStateData,
    ) -> str:
        if not state.active_topic:
            return query
        lowered = normalize_text(query)
        topic_seed = _topic_rewrite_seed(state.active_topic)
        normalized_topic = normalize_text(state.active_topic)
        normalized_seed = normalize_text(topic_seed)
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
    ) -> str:
        payload = {
            "current_query": query,
            "previous_turn": {
                "user_question": state.last_user_query,
                "resolved_question": state.last_resolved_query,
                "answer_summary": state.last_assistant_answer,
            },
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
                "standalone_query": "string",
                "active_topic": "string|null",
                "carry_over_departments": ["student_affairs"],
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
        course_code_match = _COURSE_CODE_PATTERN.search(query)
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
        merged.extend(match.group(0).replace(" ", "") for match in _COURSE_CODE_PATTERN.finditer(query))
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


def _compact_text(text: str | None, *, max_len: int) -> str:
    value = (text or "").strip()
    if len(value) <= max_len:
        return value
    return value[: max_len - 3].rstrip() + "..."
