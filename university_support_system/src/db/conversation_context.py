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

_COURSE_CODE_PATTERN = re.compile(r"\b[A-ZÇĞİÖŞÜ]{2,6}\s?\d{3,4}\b", re.IGNORECASE)
_FOLLOW_UP_PREFIXES = (
    "peki",
    "bir de",
    "bu durumda",
    "bu ders",
    "bunun",
    "bunlar",
    "bunlar icin",
    "onun",
    "onlar",
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
)
_FOLLOW_UP_PRONOUNS = {
    "bu", "bunu", "buna", "bunda", "bunun", "bundan",
    "bunlar", "bunlarin", "bunlara",
    "su", "sunu", "sunun",
    "o", "onu", "ona", "onun", "ondan", "onlar", "onlarin",
    "orada", "burada", "oraya", "buraya",
    "aynisi", "kendisi",
}
_TURBO_WORDS = {
    "evet", "hayir", "tamam", "tesekkurler", "ok", "sagol",
    "baska", "anladim", "tamamdir", "sagolun", "tesekkur",
    "iyi", "guzel", "oldu", "peki",
}
_MIN_CONTENT_WORD_OVERLAP = 0.35


def _rewrite_preserves_intent(original: str, rewritten: str) -> bool:
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
    orig_tokens = set(normalize_text(original).split()) - stop_words
    rew_tokens = set(normalize_text(rewritten).split()) - stop_words
    if not orig_tokens:
        return True

    # Birebir eslesen tokenlar
    overlap = len(orig_tokens & rew_tokens)

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
    return ratio >= _MIN_CONTENT_WORD_OVERLAP


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
            )

        rewrite_method = "heuristic"
        llm_resolution = None
        if settings.conversation.rewrite_with_llm and llm_service is not None:
            llm_resolution = await self._rewrite_with_llm(
                query=query,
                state=state,
                llm_service=llm_service,
                llm_profile=llm_profile,
                student_department=student_department,
                student_faculty=student_faculty,
                student_type=student_type,
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
                user_query=user_query,
                resolved_query=resolved_query,
                assistant_answer=assistant_answer,
                answer_summary=answer_summary,
                active_topic=topic,
                task_type=task_type.value if task_type else None,
                is_follow_up=is_follow_up,
                departments=list(dict.fromkeys(departments)),
                source_refs=source_refs,
                turn_metadata={
                    "source_count": len(sources),
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
            state.last_user_query = user_query
            state.last_resolved_query = resolved_query
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
                last_user_query=user_query,
                last_resolved_query=resolved_query,
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
        query_tokens = [token for token in normalized_query.split() if token]

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

        is_follow_up = bool(
            state.turn_count > 0
            and (starts_with_follow_up or has_strong_marker or has_weak_marker or pronoun_like)
        )

        # Konu degisimi kontrolu: Yeni sorguda farkli bir konu tespit edilirse
        # follow-up olarak degil, bagimsiz soru olarak degerlendir.
        # Ornek: state.topic="CAP" ama sorgu="Erasmus basvurusu nasil yapilir?"
        if is_follow_up:
            new_topic = self._infer_topic(query)
            if (
                new_topic is not None
                and state.active_topic is not None
                and normalize_text(new_topic) != normalize_text(state.active_topic)
            ):
                is_follow_up = False

        return {
            "is_follow_up": is_follow_up,
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

        if not is_follow_up:
            standalone_query = query

        if is_follow_up and standalone_query != query:
            if not _rewrite_preserves_intent(query, standalone_query):
                logger.warning(
                    "conversation_rewrite_rejected original=%r rewritten=%r",
                    query,
                    standalone_query,
                )
                standalone_query = query
                is_follow_up = False

        carry_over_departments = self._parse_departments(payload.get("carry_over_departments") or [])
        clarification_message = payload.get("clarification_message")
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
                str(clarification_message).strip()
                if payload.get("needs_clarification") and clarification_message
                else None
            ),
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
        normalized_topic = normalize_text(state.active_topic)
        if normalized_topic and normalized_topic in lowered:
            return query
        return f"{state.active_topic} hakkinda: {query}"

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

        for topic, markers in _TOPIC_PATTERNS:
            if any(marker in normalized_query for marker in markers):
                return topic
        return None

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
