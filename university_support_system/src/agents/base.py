"""Uzman ajanlar icin ortak taban siniflar."""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Awaitable, Callable, Sequence

from a2a.types import AgentSkill, Task

from src.a2a import build_agent_card, build_department_response_task
from src.core.constants import (
    Department,
    RAG_DIRECT_MIN_CONTENT_LEN,
    RAG_DIRECT_SCORE_THRESHOLD,
    TaskType,
)
from src.core.config import settings
from src.core.messages import CONTACT_SUGGESTION
from src.core.profiling import profile_stage
from src.core.text_normalization import normalize_text
from src.db.office_contacts import OfficeContactRecord, fetch_office_contacts
from src.db.schemas import DepartmentResponse, RAGSource
from src.llm.prompt_templates import GENERAL_QA_SYSTEM_PROMPT

if TYPE_CHECKING:
    from src.llm.llm_service import LLMService
    from src.rag.retriever import HybridRetriever

logger = logging.getLogger(__name__)

_SHARED_RETRIEVER: HybridRetriever | None = None
_LLM_SYNTHESIS_TIMEOUT_SECONDS = settings.llm.specialist_synthesis_timeout_seconds

_CONTACT_REQUEST_KEYWORDS = (
    "iletisim", "iletisim bilgisi", "telefon", "dahili", "e-posta",
    "eposta", "email", "sekreter", "sekreterlik", "ofis", "telefon numarasi",
    "adres", "kime basvurayim", "kimle gorusmeliyim", "birim", "mudurluk",
)

_DIRECT_RAG_RERANKER_THRESHOLD = 0.605
_DIRECT_RAG_RETRIEVAL_THRESHOLD = 0.25
_SPECIALIST_LLM_CONTEXT_MAX_LEN = 1500

_LLM_SYNTHESIS_MIN_RERANKER_SCORE = 0.30
_LLM_SYNTHESIS_MIN_RETRIEVAL_SCORE = 0.18

_NO_USEFUL_RESULT_RERANKER_CEILING = 0.25

_DIRECT_RAG_SCORE_GAP_MIN = 0.01

_FAQ_QUESTION_RE = re.compile(r"^\s*(?:\d+[\.\)]\s*)?(.{10,120}\?)\s*$", re.MULTILINE)
_FAQ_SOURCE_PATTERNS = ("sik_sorulan", "sikca_sorulan", "sss", "faq")


def _extract_relevant_faq_block(content: str, query: str) -> str:
    """SSS iceriginden sorguya en yakin Q&A blogunu cikar."""
    questions = list(_FAQ_QUESTION_RE.finditer(content))
    if len(questions) < 2:
        return content

    query_lower = normalize_text(query)
    query_words = set(query_lower.split())

    best_block = content
    best_overlap = 0
    for i, match in enumerate(questions):
        end = questions[i + 1].start() if i + 1 < len(questions) else len(content)
        block = content[match.start():end].strip()
        block_lower = normalize_text(block)
        block_words = set(block_lower.split())
        overlap = len(query_words & block_words)
        if overlap > best_overlap:
            best_overlap = overlap
            best_block = block

    return best_block


def _is_faq_source(source: str) -> bool:
    lowered = normalize_text(source)
    return any(p in lowered for p in _FAQ_SOURCE_PATTERNS)
_GENERATION_MODE_ORDER = ("vt", "rag", "llm", "kural")


@dataclass(frozen=True)
class AgentDefinition:
    """Uzman ajan sabit tanimi."""

    agent_id: str
    name: str
    department: Department
    description: str
    task_types: tuple[TaskType, ...]
    examples: tuple[str, ...]
    tags: tuple[str, ...]
    system_prompt: str = ""


class BaseSpecialistAgent:
    """RAG + LLM tabanli temel uzman ajan."""

    def __init__(
        self,
        definition: AgentDefinition,
        *,
        llm_service: LLMService | None = None,
        retriever_factory: Callable[[], HybridRetriever] | None = None,
        contact_fetcher: Callable[..., Awaitable[list[OfficeContactRecord]]] | None = None,
    ) -> None:
        self.definition = definition
        if llm_service is None:
            from src.llm.llm_service import LLMService

            llm_service = LLMService()
        self.llm_service = llm_service
        self._retriever_factory = retriever_factory or self._build_shared_retriever
        self._retriever: HybridRetriever | None = None
        self._contact_fetcher = contact_fetcher or fetch_office_contacts

    @staticmethod
    def _build_shared_retriever() -> HybridRetriever:
        """Surec boyunca ortak kullanilacak retriever ornegini uretir."""
        global _SHARED_RETRIEVER
        if _SHARED_RETRIEVER is None:
            from src.rag.retriever import HybridRetriever

            _SHARED_RETRIEVER = HybridRetriever()
        return _SHARED_RETRIEVER

    def _get_retriever(self) -> HybridRetriever:
        """Ajan yasam dongusu boyunca ayni retriever ornegini kullanir."""
        if self._retriever is None:
            self._retriever = self._retriever_factory()
        return self._retriever

    @property
    def agent_id(self) -> str:
        return self.definition.agent_id

    @property
    def department(self) -> Department:
        return self.definition.department

    def build_card(self):
        """A2A AgentCard uretir."""
        skills = [
            AgentSkill(
                id=f"{self.agent_id}_skill",
                name=self.definition.name,
                description=self.definition.description,
                tags=list(self.definition.tags),
                examples=list(self.definition.examples),
                inputModes=["text"],
                outputModes=["text"],
            )
        ]
        return build_agent_card(
            agent_id=self.agent_id,
            name=self.definition.name,
            description=self.definition.description,
            url=f"https://omu.edu.tr/agents/{self.agent_id}",
            skills=skills,
        )

    async def handle_task(self, task: Task) -> Task:
        """A2A task'ini isleyip A2A response task'i uretir."""
        response = await self.handle_department_task(task)
        return build_department_response_task(
            response,
            request_task=task,
            emitter_id=self.agent_id,
            emitter_name=self.definition.name,
        )

    async def handle_department_task(self, task: Task) -> DepartmentResponse:
        """A2A task'ini isleyip departman yaniti uretir."""
        with profile_stage("agent.handle_task", agent_id=self.agent_id, department=self.department.value):
            query_text = str((task.metadata or {}).get("query_text", "")).strip()
            if not query_text:
                with profile_stage("agent.extract_query", agent_id=self.agent_id):
                    query_text = self._extract_query_from_task(task)

            if self._is_contact_request(query_text):
                with profile_stage("agent.contact_request", agent_id=self.agent_id):
                    return await self._handle_contact_request()

            meta = task.metadata or {}
            retriever = self._get_retriever()
            source_hints = meta.get("conversation_source_refs") or []
            topic_hint = meta.get("conversation_topic")
            disable_specialist_llm = bool(meta.get("disable_specialist_llm", False))
            llm_profile = meta.get("llm_profile")
            student_department = meta.get("student_department")
            intent_force_llm = bool(meta.get("force_llm_synthesis", False))
            with profile_stage("agent.retriever.search", agent_id=self.agent_id, department=self.department.value):
                results = retriever.search(
                    query_text,
                    department=self.department,
                    source_hints=source_hints,
                    topic_hint=topic_hint,
                    student_department=student_department,
                )
            enrich_results = getattr(type(retriever), "enrich_results", None)
            if callable(enrich_results):
                with profile_stage("agent.retriever.enrich_results", agent_id=self.agent_id, department=self.department.value):
                    results = retriever.enrich_results(results, department=self.department)
            with profile_stage("agent.generate_answer", agent_id=self.agent_id):
                answer, generation_mode = await self._generate_answer(
                    query_text,
                    results,
                    force_llm=intent_force_llm,
                    allow_llm=not disable_specialist_llm,
                    llm_profile=llm_profile,
                )
            return self._build_department_response(
                answer=f"{answer}{CONTACT_SUGGESTION}",
                results=results,
                generation_mode=generation_mode,
            )

    async def handle_a2a_task(self, task: Task) -> Task:
        """Geriye donuk uyumluluk icin A2A response task dondurur."""
        return await self.handle_task(task)

    def _build_department_response(
        self,
        *,
        answer: str,
        results: Sequence[dict],
        generation_mode: str | None = None,
        success: bool = True,
    ) -> DepartmentResponse:
        """RAG sonuc listesiyle birlikte standart departman cevabi kurar."""
        return DepartmentResponse(
            department=self.department,
            answer=answer,
            sources=[
                RAGSource(
                    content=item.get("content", ""),
                    score=float(item.get("score", 0.0)),
                    metadata=self._build_source_metadata(item),
                )
                for item in results
            ],
            generation_mode=generation_mode,
            success=success,
        )

    @staticmethod
    def _build_source_metadata(item: dict) -> dict:
        """Top-level retriever alanlarini kaynak metadata'sina tasir."""
        metadata = dict(item.get("metadata", {}) or {})
        source = item.get("source")
        if source and "source" not in metadata:
            metadata["source"] = source
        source_url = item.get("source_url")
        if source_url and "source_url" not in metadata:
            metadata["source_url"] = source_url
        return metadata

    def _extract_query_from_task(self, task: Task) -> str:
        """Task icindeki ilk text part'tan sorgu cikarir."""
        message = task.status.message
        if message is None:
            return ""
        for part in message.parts:
            text = getattr(part, "text", None)
            if text:
                return str(text)
            root = getattr(part, "root", None)
            text = getattr(root, "text", None)
            if text:
                return str(text)
        return ""

    @staticmethod
    def _is_contact_request(query_text: str) -> bool:
        lowered = normalize_text(query_text)
        return any(kw in lowered for kw in _CONTACT_REQUEST_KEYWORDS)

    async def _handle_contact_request(self) -> DepartmentResponse:
        """Ajanla iliskili ofis iletisim bilgilerini sunar."""
        contacts = await self._contact_fetcher(
            department=self.department,
            agent_id=self.agent_id,
        )
        if not contacts:
            contacts = await self._contact_fetcher(department=self.department)
        if not contacts:
            return DepartmentResponse(
                department=self.department,
                answer=(
                    "Su anda bu alan icin kayitli iletisim bilgisi bulunamadi. "
                    "Ogrenci Isleri Daire Baskanligi genel hattindan yardim alabilirsiniz."
                ),
                generation_mode="kural",
                success=True,
            )

        lines = ["Ilgili birim iletisim bilgileri:"]
        for contact in contacts:
            parts = [f"- {contact.unit_name}"]
            if contact.person_name:
                title_str = f" - {contact.title}" if contact.title else ""
                parts.append(f"  {contact.person_name}{title_str}")
            if contact.phone_ext:
                parts.append(f"  Dahili: {contact.phone_ext}")
            if contact.email:
                parts.append(f"  E-Posta: {contact.email}")
            lines.append("\n".join(parts))

        return DepartmentResponse(
            department=self.department,
            answer="\n".join(lines),
            generation_mode="kural",
            success=True,
        )

    async def _generate_answer(
        self,
        query_text: str,
        results: Sequence[dict],
        *,
        db_context: str | None = None,
        force_llm: bool = False,
        allow_llm: bool = True,
        llm_profile: str | None = None,
    ) -> tuple[str, str]:
        """Tek yanit uretim noktasi. Tum ajanlar bu metodu kullanmali."""
        if not results and not db_context:
            return (
                "Bu konuda elimde yeterli kaynak bulunamadi. "
                "Soruyu biraz daha detaylandirirsan veya ilgili birimle iletisime gecersen daha net yardimci olabilirim."
            ), "kural"

        if results and not db_context:
            top_meta = results[0].get("metadata") or {}
            score_type_raw = str(top_meta.get("score_type", "")).lower()
            top_score = float(results[0].get("score", 0.0))
            top_source = results[0].get("source", "?")
            logger.info(
                "generate_answer_score_check",
                agent_id=self.agent_id,
                top_score=round(top_score, 4),
                score_type=score_type_raw,
                top_source=top_source,
                result_count=len(results),
                ceiling=_NO_USEFUL_RESULT_RERANKER_CEILING,
                llm_min=_LLM_SYNTHESIS_MIN_RERANKER_SCORE,
            )
            if score_type_raw == "reranker":
                if top_score < _NO_USEFUL_RESULT_RERANKER_CEILING:
                    logger.info(
                        "no_useful_rag_results agent=%s top_reranker_score=%.4f ceiling=%.4f",
                        self.agent_id, top_score, _NO_USEFUL_RESULT_RERANKER_CEILING,
                    )
                    return (
                        "Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. "
                        "Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin."
                    ), "kural"

        force_llm = force_llm or self._should_force_llm_synthesis(
            query_text,
            results,
            db_context=db_context,
        )

        if not force_llm:
            with profile_stage("agent.direct_rag_check", agent_id=self.agent_id):
                direct = self._try_direct_rag_answer(results, query_text=query_text)
            if direct is not None:
                prefix = f"{db_context}\n\n" if db_context else ""
                logger.info("rag_direct_answer used=%s score=%.3f", self.agent_id, results[0].get("score", 0))
                return prefix + direct, self._derive_non_llm_generation_mode(
                    results,
                    db_context=db_context,
                )

            if not allow_llm:
                with profile_stage("agent.source_only_answer", agent_id=self.agent_id):
                    return (
                        self._build_source_only_answer(query_text, results, db_context=db_context),
                        self._derive_non_llm_generation_mode(results, db_context=db_context),
                    )

            if self._should_skip_llm_synthesis(query_text, results, db_context=db_context):
                with profile_stage("agent.source_only_answer", agent_id=self.agent_id):
                    return (
                        self._build_source_only_answer(query_text, results, db_context=db_context),
                        self._derive_non_llm_generation_mode(results, db_context=db_context),
                    )

        with profile_stage("agent.llm_synthesize", agent_id=self.agent_id):
            return await self._llm_synthesize(
                query_text,
                results,
                db_context=db_context,
                llm_profile=llm_profile,
            )

    def _should_skip_llm_synthesis(
        self,
        query_text: str,
        results: Sequence[dict],
        *,
        db_context: str | None = None,
    ) -> bool:
        """Alt ajanlarin LLM sentezini kisa devre etmesine izin verir."""
        return False

    def _should_force_llm_synthesis(
        self,
        query_text: str,
        results: Sequence[dict],
        *,
        db_context: str | None = None,
    ) -> bool:
        """Belirli sorgulari dogrudan LLM sentezine zorlar."""
        return False

    def _build_source_only_answer(
        self,
        query_text: str,
        results: Sequence[dict],
        *,
        db_context: str | None = None,
    ) -> str:
        """LLM sentezi atlandiginda gosterilecek guvenli kaynak yaniti."""
        return self._build_llm_failure_fallback(results, db_context=db_context)

    @classmethod
    def _compose_generation_mode(cls, *parts: str) -> str:
        normalized = {
            str(part).strip().lower()
            for part in parts
            if part and str(part).strip()
        }
        if not normalized:
            return "kural"
        ordered = [part for part in _GENERATION_MODE_ORDER if part in normalized]
        extras = sorted(normalized - set(_GENERATION_MODE_ORDER))
        return "+".join(ordered + extras)

    def _derive_non_llm_generation_mode(
        self,
        results: Sequence[dict],
        *,
        db_context: str | None = None,
    ) -> str:
        parts: list[str] = []
        if db_context:
            parts.append("vt")
        if results:
            parts.append("rag")
        if not parts:
            parts.append("kural")
        return self._compose_generation_mode(*parts)

    def _derive_llm_generation_mode(
        self,
        results: Sequence[dict],
        *,
        db_context: str | None = None,
    ) -> str:
        parts: list[str] = ["llm"]
        if db_context:
            parts.append("vt")
        if results:
            parts.append("rag")
        return self._compose_generation_mode(*parts)

    def _try_direct_rag_answer(self, results: Sequence[dict], query_text: str = "") -> str | None:
        """En yuksek skorlu RAG sonucu yeterince iyiyse LLM'e gitmeden dondurur."""
        if not results:
            return None

        top = results[0]
        score = float(top.get("score", 0.0))
        content = top.get("content", "").strip()
        source = top.get("source", "")
        metadata = dict(top.get("metadata", {}) or {})
        score_type = str(metadata.get("score_type", "semantic_similarity"))
        direct_threshold = self._resolve_direct_rag_threshold(score_type)

        if score < direct_threshold:
            return None
        if len(content) < RAG_DIRECT_MIN_CONTENT_LEN:
            return None

        if (
            score_type.strip().lower() == "reranker"
            and len(results) >= 2
            and score < direct_threshold + 0.07
        ):
            second_score = float(results[1].get("score", 0.0))
            if (score - second_score) < _DIRECT_RAG_SCORE_GAP_MIN:
                logger.info(
                    "direct_rag_skipped_small_gap agent=%s top=%.4f second=%.4f gap=%.4f",
                    self.agent_id, score, second_score, score - second_score,
                )
                return None

        if _is_faq_source(source) and query_text:
            content = _extract_relevant_faq_block(content, query_text)

        return f"{self._compact_source_content(content, max_len=None)}\n\n(Kaynak: {source})"

    @staticmethod
    def _resolve_direct_rag_threshold(score_type: str) -> float:
        """Map heterogeneous score types onto practical direct-answer thresholds."""
        normalized_type = (score_type or "").strip().lower()
        if normalized_type == "reranker":
            return _DIRECT_RAG_RERANKER_THRESHOLD
        if normalized_type == "retrieval":
            return _DIRECT_RAG_RETRIEVAL_THRESHOLD
        return RAG_DIRECT_SCORE_THRESHOLD

    async def _llm_synthesize(
        self,
        query_text: str,
        results: Sequence[dict],
        *,
        db_context: str | None = None,
        llm_profile: str | None = None,
    ) -> tuple[str, str]:
        """RAG kaynaklarini (ve varsa DB baglamini) LLM ile sentezler."""
        if results and not db_context:
            top_score = float(results[0].get("score", 0.0))
            top_metadata = results[0].get("metadata") or {}
            score_type = str(top_metadata.get("score_type", "semantic_similarity")).strip().lower()

            min_threshold = (
                _LLM_SYNTHESIS_MIN_RERANKER_SCORE
                if score_type == "reranker"
                else _LLM_SYNTHESIS_MIN_RETRIEVAL_SCORE
            )

            if top_score < min_threshold:
                logger.info(
                    "llm_synthesis_blocked_low_score agent=%s top_score=%.4f threshold=%.4f score_type=%s",
                    self.agent_id, top_score, min_threshold, score_type,
                )
                return (
                    "Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamadi. "
                    "Soruyu daha detayli sorabilir veya ilgili birimle iletisime gecebilirsin.",
                    "kural",
                )

        context_chunks = []
        for index, item in enumerate(results[:3], start=1):
            source = item.get("source", "bilinmiyor")
            raw_content = item.get("content", "")
            if _is_faq_source(source) and query_text:
                raw_content = _extract_relevant_faq_block(raw_content, query_text)
            content = self._compact_source_content(
                raw_content,
                max_len=_SPECIALIST_LLM_CONTEXT_MAX_LEN,
            )
            context_chunks.append(f"[Kaynak {index}: {source}]\n{content}")

        prompt = f"Soru:\n{query_text}\n\n"
        if db_context:
            prompt += f"Veritabani Bilgisi:\n{db_context}\n\n"
        if context_chunks:
            prompt += f"Belge Baglami:\n{chr(10).join(context_chunks)}\n\n"
        prompt += (
            "KURALLAR:\n"
            "1. Yalnizca verilen belge baglaminda ACIKCA gecen bilgileri kullan.\n"
            "2. Kaynaklar soruyu dogrudan yanitlamiyorsa 'Bu konuda elimdeki kaynaklarda net bilgi bulunamadi' de.\n"
            "3. ASLA tahmin yurutme, genel bilgiyle bosluk doldurma, kavram tanimi uydurma.\n"
            "4. Kaynaklarda yer almayan adim listeleri, buton isimleri, ekran adimlari veya kisaltma acimlari URETME.\n"
            "5. YALNIZCA Turkce yanit ver; Ingilizce veya baska dilden kelime KULLANMA (contribution, spring, register gibi).\n"
            "6. Universite adini kaynakta yazmiyorsa UYDURMA. Bu sistem Ondokuz Mayis Universitesi (OMU) icindir.\n"
            "7. 'Kisisel deneyimim' veya 'genel bilgi birikimim' gibi ifadeler KULLANMA — sadece belge kaynagi kullan."
        )

        system = self.definition.system_prompt or GENERAL_QA_SYSTEM_PROMPT
        selected_model = settings.resolve_llm_model(
            role="specialist_synthesis",
            profile=llm_profile,
        )
        logger.info(
            "specialist_llm_synthesis_start agent=%s timeout_s=%s prompt_chars=%s sources=%s model=%s profile=%s",
            self.agent_id,
            _LLM_SYNTHESIS_TIMEOUT_SECONDS,
            len(prompt) + len(system),
            len(context_chunks),
            selected_model,
            llm_profile or settings.normalize_llm_profile(settings.llm.profile),
        )
        from src.llm.llm_service import LLMServiceError

        try:
            with profile_stage("agent.llm_generate", agent_id=self.agent_id):
                answer = await asyncio.wait_for(
                    self.llm_service.generate(
                        prompt=prompt,
                        system=system,
                        model_role="specialist_synthesis",
                        llm_profile=llm_profile,
                    ),
                    timeout=_LLM_SYNTHESIS_TIMEOUT_SECONDS,
                )
                return answer, self._derive_llm_generation_mode(results, db_context=db_context)
        except (asyncio.TimeoutError, LLMServiceError) as exc:
            logger.warning(
                "llm_synthesis_fallback_used agent=%s reason=%s",
                self.agent_id,
                type(exc).__name__,
            )
            with profile_stage("agent.llm_failure_fallback", agent_id=self.agent_id, reason=type(exc).__name__):
                return (
                    self._build_llm_failure_fallback(results, db_context=db_context),
                    self._derive_non_llm_generation_mode(results, db_context=db_context),
                )

    def _build_llm_failure_fallback(
        self,
        results: Sequence[dict],
        *,
        db_context: str | None = None,
        query_text: str = "",
    ) -> str:
        """LLM sentezi basarisiz olursa en guvenli belge ozetine doner."""
        prefix = f"{db_context}\n\n" if db_context else ""
        if not results:
            return (
                prefix
                + "Bu konuda ilgili kaynaklara ulasmaya calistim ancak su anda kisa bir ozet uretemedim. "
                "Soruyu daha spesifik sorman veya ilgili birimle iletisime gecmen faydali olur."
            )

        top = results[0]
        content = top.get("content", "").strip()
        source = top.get("source", "bilinmiyor")
        if _is_faq_source(source) and query_text:
            content = _extract_relevant_faq_block(content, query_text)
        content = self._compact_source_content(content, max_len=None)
        return (
            prefix
            + f"Eldeki en ilgili kaynakta su bilgi yer aliyor:\n{content}\n\n(Kaynak: {source})"
        )

    @staticmethod
    def _compact_source_content(content: str, *, max_len: int | None = 320) -> str:
        collapsed = re.sub(r"\s+", " ", content).strip()
        if max_len is not None and len(collapsed) > max_len:
            return f"{collapsed[: max_len - 3].rstrip()}..."
        return collapsed
