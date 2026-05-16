"""Uzman ajanlar icin ortak taban siniflar."""

from __future__ import annotations

import asyncio
import inspect
import json
import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Awaitable, Callable, Sequence

from a2a.types import AgentSkill, Task

from src.a2a import build_agent_card, build_agent_response_task
from src.core.constants import (
    AgentRole,
    Capability,
    Department,
    TaskType,
)
from src.core.config import settings
from src.core.contact_intent import looks_like_contact_intent
from src.core.policy_facets import align_policy_evidence, resolve_policy_facet
from src.core.profiling import profile_stage
from src.core.retrieval_execution_policy import (
    RetrievalExecutionPolicy,
    resolve_retrieval_execution_policy,
    strong_primary_evidence,
)
from src.core.source_owner_policy import apply_source_owner_policy
from src.core.text_normalization import normalize_text
from src.agents.academic.curriculum_utils import infer_department_from_query
from src.rag.multi_query_expander import expand_query as _expand_multi_queries
from src.rag.query_preprocessor import QueryPreprocessor
from src.quality.evidence import (
    build_evidence_context_chunks,
    build_evidence_diagnostics,
    extract_factual_claims,
    extract_evidence_items,
    select_evidence_sentences,
)
from src.quality.evidence_answer_validator import extract_value_labels, infer_source_family
from src.quality.evidence_selector import EvidenceSelectionDecision, select_evidence_with_llm
from src.db.office_contacts import OfficeContactRecord, fetch_office_contacts
from src.db.schemas import DepartmentResponse, RAGSource
from src.llm.prompt_templates import GENERAL_QA_SYSTEM_PROMPT

if TYPE_CHECKING:
    from src.llm.llm_service import LLMService
    from src.rag.retriever import HybridRetriever

logger = logging.getLogger(__name__)
OMU_SWITCHBOARD_PHONE = "0 (362) 312 19 19"
_EVIDENCE_QUERY_PREPROCESSOR = QueryPreprocessor()

_SHARED_RETRIEVER: HybridRetriever | None = None
_SHARED_LOCAL_FALLBACK_RETRIEVER: HybridRetriever | None = None
_LLM_SYNTHESIS_TIMEOUT_SECONDS = settings.llm.specialist_synthesis_timeout_seconds

_SPECIALIST_LLM_CONTEXT_MAX_LEN = 2000
_SPECIALIST_EVIDENCE_MAX_SENTENCES = 7
_SPECIALIST_EVIDENCE_MIN_SCORE = 0.45

_FAQ_QUESTION_RE = re.compile(r"^\s*(?:\d+[\.\)]\s*)?(.{10,120}\?)\s*$", re.MULTILINE)
_FAQ_SOURCE_PATTERNS = ("sik_sorulan", "sikca_sorulan", "sss", "faq")
# Backward-compat aliases — canonical definitions live in src.quality.evidence
from src.quality.evidence import EVIDENCE_SENTENCE_RE as _EVIDENCE_SENTENCE_RE  # noqa: E402
from src.quality.evidence import EVIDENCE_STOPWORDS as _EVIDENCE_STOPWORDS  # noqa: E402


# Genel/yaygın kelimeler — eşleşme skorunda düşük ağırlık
_FAQ_LOW_WEIGHT_WORDS = frozenset({
    "ne", "nasil", "nerede", "neden", "hangi", "kim", "kac",
    "mi", "mu", "mi", "mu", "icin", "ile", "ve", "bir",
    "var", "yok", "olur", "olmali", "gerekir", "yapmali",
    "kayit",  # çok genel — düşük ağırlık
    "ogrenci", "universite", "belge", "bilgi",
})


def _faq_word_weight(word: str) -> float:
    return 0.3 if word in _FAQ_LOW_WEIGHT_WORDS else 1.0


def _extract_relevant_faq_block(content: str, query: str, *, max_blocks: int = 2) -> str:
    """SSS iceriginden sorguya en yakin Q&A bloklarini cikar (varsayilan: top-2)."""
    questions = list(_FAQ_QUESTION_RE.finditer(content))
    if len(questions) < 2:
        return content

    query_lower = normalize_text(query)
    query_words = set(query_lower.split())

    scored_blocks: list[tuple[float, str]] = []
    for i, match in enumerate(questions):
        end = questions[i + 1].start() if i + 1 < len(questions) else len(content)
        block = content[match.start():end].strip()

        # Soru kısmını 2x ağırlıkla puanla
        question_text = match.group(1) if match.group(1) else block.split("\n")[0]
        q_text_words = set(normalize_text(question_text).split())
        q_overlap = sum(_faq_word_weight(w) for w in query_words & q_text_words) * 2.0

        # Blok genel overlap
        block_lower = normalize_text(block)
        block_words = set(block_lower.split())
        b_overlap = sum(_faq_word_weight(w) for w in query_words & block_words)

        total_score = q_overlap + b_overlap
        scored_blocks.append((total_score, block))

    scored_blocks.sort(key=lambda pair: pair[0], reverse=True)
    top_blocks = [block for score, block in scored_blocks[:max_blocks] if score > 0]
    if not top_blocks:
        return scored_blocks[0][1] if scored_blocks else content

    return "\n\n".join(top_blocks)


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
            if settings.retrieval_service.enabled:
                from src.rag.remote import RemoteHybridRetriever

                _SHARED_RETRIEVER = RemoteHybridRetriever()  # type: ignore[assignment]
            else:
                from src.rag.retriever import HybridRetriever

                _SHARED_RETRIEVER = HybridRetriever()
        return _SHARED_RETRIEVER

    @staticmethod
    def _build_shared_local_fallback_retriever() -> HybridRetriever:
        """Remote retrieval gecici olarak dusunce pahali local fallback'i tekrar kurma."""
        global _SHARED_LOCAL_FALLBACK_RETRIEVER
        if _SHARED_LOCAL_FALLBACK_RETRIEVER is None:
            from src.rag.retriever import HybridRetriever

            _SHARED_LOCAL_FALLBACK_RETRIEVER = HybridRetriever()
        return _SHARED_LOCAL_FALLBACK_RETRIEVER

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
        return build_agent_response_task(
            response,
            request_task=task,
            emitter_id=self.agent_id,
            emitter_name=self.definition.name,
            metadata=self._agent_response_metadata(),
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
            final_answer_owner = str(meta.get("final_answer_owner") or "").strip() or None
            specialist_response_mode = str(meta.get("specialist_response_mode") or "").strip() or None
            llm_profile = meta.get("llm_profile")
            student_department = meta.get("student_department")
            intent_force_llm = bool(meta.get("force_llm_synthesis", False))
            plan_context = self._build_plan_context_from_metadata(meta)
            source_owner_payload = (
                plan_context.get("source_owner")
                if isinstance(plan_context.get("source_owner"), dict)
                else {}
            )
            source_owner_primary = str(source_owner_payload.get("primary") or "").strip() or None
            retrieval_query = str(meta.get("retrieval_query") or "").strip() or query_text
            explicit_department_scope = (
                infer_department_from_query(retrieval_query)
                or infer_department_from_query(query_text)
            )
            retrieval_department_scope = explicit_department_scope or student_department
            retrieval_policy = resolve_retrieval_execution_policy(
                department=self.department,
                branch_role=str(meta.get("branch_role") or "").strip() or None,
                metadata=meta,
            )
            search_top_k = retrieval_policy.top_k or self._search_top_k(retrieval_query, meta)
            retrieval_stats: dict[str, object] = {
                "schema": "omu.retrieval_execution_stats.v1",
                "policy": retrieval_policy.to_metadata(),
                "search_calls": 0,
                "multi_query_variant_count": 0,
                "multi_query_added_results": 0,
                "early_stop_reason": None,
                "support_lite_applied": retrieval_policy.support_lite,
            }
            with profile_stage("agent.retriever.search", agent_id=self.agent_id, department=self.department.value):
                try:
                    retrieval_stats["search_calls"] = int(retrieval_stats["search_calls"]) + 1
                    results = retriever.search(
                        retrieval_query,
                        top_k=search_top_k,
                        department=self.department,
                        source_hints=source_hints,
                        topic_hint=topic_hint,
                        student_department=retrieval_department_scope,
                        source_owner=source_owner_primary,
                        reranker_candidate_limit=retrieval_policy.reranker_candidate_limit,
                    )
                except Exception:
                    if not settings.retrieval_service.enabled or not settings.retrieval_service.fallback_to_local:
                        raise
                    logger.warning(
                        "remote_retrieval_failed_falling_back_local agent=%s",
                        self.agent_id,
                        exc_info=True,
                    )
                    retriever = self._build_shared_local_fallback_retriever()
                    retrieval_stats["search_calls"] = int(retrieval_stats["search_calls"]) + 1
                    results = retriever.search(
                        retrieval_query,
                        top_k=search_top_k,
                        department=self.department,
                        source_hints=source_hints,
                        topic_hint=topic_hint,
                        student_department=retrieval_department_scope,
                        source_owner=source_owner_primary,
                        reranker_candidate_limit=retrieval_policy.reranker_candidate_limit,
                    )
            # ── Multi-Query Expansion: search variant queries and merge ──
            with profile_stage("agent.multi_query_expansion", agent_id=self.agent_id):
                strong_evidence, early_stop_reason = strong_primary_evidence(
                    list(results),
                    policy=retrieval_policy,
                )
                retrieval_stats["early_stop_reason"] = early_stop_reason
                results = self._apply_multi_query_expansion(
                    retrieval_query,
                    results,
                    retriever=retriever,
                    top_k=search_top_k,
                    department=self.department,
                    source_hints=source_hints,
                    topic_hint=topic_hint,
                    student_department=retrieval_department_scope,
                    source_owner=source_owner_primary,
                    policy=retrieval_policy,
                    skip=strong_evidence,
                    stats=retrieval_stats,
                )
            enrich_results = getattr(type(retriever), "enrich_results", None)
            if callable(enrich_results) and self._should_enrich_results(query_text, results):
                with profile_stage("agent.retriever.enrich_results", agent_id=self.agent_id, department=self.department.value):
                    try:
                        results = retriever.enrich_results(results, department=self.department)
                    except Exception:
                        if not settings.retrieval_service.enabled or not settings.retrieval_service.fallback_to_local:
                            raise
                        logger.warning(
                            "remote_retrieval_enrich_failed_falling_back_local agent=%s",
                            self.agent_id,
                            exc_info=True,
                        )
                        local_retriever = self._build_shared_local_fallback_retriever()
                        results = local_retriever.enrich_results(results, department=self.department)
            plan_context = dict(plan_context or {})
            plan_context["retrieval_execution_policy"] = retrieval_policy.to_metadata()
            plan_context["retrieval_execution_stats"] = retrieval_stats
            with profile_stage("agent.plan_evidence_bias", agent_id=self.agent_id, department=self.department.value):
                results = self._apply_plan_evidence_source_bias(results, plan_context)
            with profile_stage("agent.source_owner_policy", agent_id=self.agent_id, department=self.department.value):
                owner_policy = apply_source_owner_policy(
                    results,
                    plan_context.get("source_owner") if plan_context else None,
                    mode=settings.source_owner_policy.mode,
                    min_compatible_score=settings.source_owner_policy.min_compatible_score,
                )
                results = owner_policy.results
                if owner_policy.diagnostics.get("status") != "skipped":
                    plan_context = dict(plan_context or {})
                    plan_context["source_owner_policy"] = owner_policy.diagnostics
                if owner_policy.should_block:
                    return self._build_department_response(
                        answer=owner_policy.fallback_answer or "",
                        query_text=query_text,
                        results=results[:3],
                        generation_mode="kural",
                        include_contact_suggestion=True,
                        final_answer_owner=final_answer_owner,
                        specialist_response_mode=specialist_response_mode,
                        plan_context=plan_context,
                    )
            with profile_stage("agent.filter_results", agent_id=self.agent_id, department=self.department.value):
                results = self._filter_results_for_answer(query_text, results)
            with profile_stage("agent.generate_answer", agent_id=self.agent_id):
                if self._should_return_evidence_packet_only(
                    final_answer_owner=final_answer_owner,
                    specialist_response_mode=specialist_response_mode,
                    results=results,
                ):
                    answer = self._build_evidence_handoff_answer(query_text, results)
                    generation_mode = self._derive_non_llm_generation_mode(results)
                else:
                    answer, generation_mode = await self._generate_answer(
                        query_text,
                        results,
                        force_llm=intent_force_llm,
                        allow_llm=not disable_specialist_llm,
                        llm_profile=llm_profile,
                        plan_context=plan_context,
                    )
            return self._build_department_response(
                answer=answer,
                query_text=query_text,
                results=results,
                generation_mode=generation_mode,
                include_contact_suggestion=True,
                final_answer_owner=final_answer_owner,
                specialist_response_mode=specialist_response_mode,
                plan_context=plan_context,
            )

    def _agent_response_metadata(self) -> dict[str, str]:
        """A2A AgentResponse identity metadata for published artifacts."""
        if self.agent_id == "announcement_agent":
            return {
                "agent_role": AgentRole.CAPABILITY_AGENT.value,
                "capability": Capability.ANNOUNCEMENT.value,
            }
        if self.agent_id == "event_agent":
            return {
                "agent_role": AgentRole.CAPABILITY_AGENT.value,
                "capability": Capability.EVENT.value,
            }
        return {"agent_role": AgentRole.SPECIALIST_AGENT.value}

    async def handle_a2a_task(self, task: Task) -> Task:
        """Geriye donuk uyumluluk icin A2A response task dondurur."""
        return await self.handle_task(task)

    def _build_department_response(
        self,
        *,
        answer: str,
        query_text: str,
        results: Sequence[dict],
        generation_mode: str | None = None,
        include_contact_suggestion: bool = False,
        success: bool = True,
        final_answer_owner: str | None = None,
        specialist_response_mode: str | None = None,
        plan_context: dict | None = None,
    ) -> DepartmentResponse:
        """RAG sonuc listesiyle birlikte standart departman cevabi kurar."""
        response_metadata = {}
        if results:
            response_metadata["evidence_packet"] = self._build_evidence_packet(
                query_text=query_text,
                answer=answer,
                results=results,
                generation_mode=generation_mode,
                final_answer_owner=final_answer_owner,
                specialist_response_mode=specialist_response_mode,
                plan_context=plan_context,
            )
        if plan_context:
            for key in (
                "plan_decision",
                "answer_contract",
                "evidence_contract",
                "policy_facet",
                "source_owner",
                "source_owner_policy",
                "retrieval_execution_policy",
                "retrieval_execution_stats",
                "decision_contract",
                "resolved_decision",
                "runtime_authority",
            ):
                if key in plan_context:
                    response_metadata[key] = plan_context.get(key)
        if final_answer_owner:
            response_metadata["final_answer_owner"] = final_answer_owner
        if specialist_response_mode:
            response_metadata["specialist_response_mode"] = specialist_response_mode

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
            include_contact_suggestion=include_contact_suggestion,
            success=success,
            metadata=response_metadata,
        )

    @staticmethod
    def _should_return_evidence_packet_only(
        *,
        final_answer_owner: str | None,
        specialist_response_mode: str | None,
        results: Sequence[dict],
    ) -> bool:
        """Return whether the specialist should hand off evidence instead of writing the final answer."""
        return (
            final_answer_owner == "main_orchestrator"
            and specialist_response_mode == "evidence_packet"
            and bool(results)
        )

    def _build_evidence_handoff_answer(
        self,
        query_text: str,
        results: Sequence[dict],
    ) -> str:
        """Build a readable fallback summary while the main orchestrator owns final synthesis."""
        lines = ["Kaynak bilgisi final cevap için hazırlandı."]
        for item in list(results)[:3]:
            content = str(item.get("content") or "")
            if not content.strip():
                continue
            source = str(item.get("source") or (item.get("metadata") or {}).get("source") or "kaynak")
            snippet = select_evidence_sentences(
                query_text,
                content,
                max_sentences=2,
                min_score=0.25,
            )
            snippet = " ".join((snippet or content[:360]).split())
            if len(snippet) > 360:
                snippet = f"{snippet[:357].rstrip()}..."
            if snippet:
                lines.append(f"- {source}: {snippet}")
        return "\n".join(lines)

    def _build_evidence_packet(
        self,
        *,
        query_text: str,
        answer: str,
        results: Sequence[dict],
        generation_mode: str | None,
        final_answer_owner: str | None = None,
        specialist_response_mode: str | None = None,
        plan_context: dict | None = None,
    ) -> dict:
        """Build compact grounding material for final synthesis."""
        selected_sources: list[dict] = []
        facts: list[dict] = []
        source_families: list[str] = []
        seen_facts: set[tuple[str, str]] = set()
        plan_context = dict(plan_context or {})
        source_owner_payload = plan_context.get("source_owner") if isinstance(plan_context.get("source_owner"), dict) else {}
        source_owner = str(source_owner_payload.get("primary") or "").strip() or None
        specialist_selection = (
            plan_context.get("specialist_selection")
            if isinstance(plan_context.get("specialist_selection"), dict)
            else {}
        )
        specialist = str(
            specialist_selection.get("selected_agent_id")
            or specialist_selection.get("agent_id")
            or self.agent_id
        ).strip()
        registry = (
            specialist_selection.get("registry")
            if isinstance(specialist_selection.get("registry"), dict)
            else {}
        )
        contract_match_reason = str(
            registry.get("reason")
            or specialist_selection.get("reason")
            or ""
        ).strip()
        policy_facet = (
            plan_context.get("policy_facet")
            if isinstance(plan_context.get("policy_facet"), dict)
            else {}
        )

        for item in list(results)[:5]:
            content = str(item.get("content") or "")
            if not content.strip():
                continue
            metadata = self._build_source_metadata(item)
            source_name = str(
                metadata.get("source")
                or metadata.get("filename")
                or metadata.get("file_name")
                or item.get("source")
                or "kaynak"
            )
            try:
                score = round(float(item.get("score", 0.0)), 4)
            except (TypeError, ValueError):
                score = 0.0
            support = select_evidence_sentences(
                query_text,
                content,
                max_sentences=3,
                min_score=0.30,
            )
            support = support[:700].strip()
            family = infer_source_family(source=source_name, claim=support or content[:420])
            policy_alignment = metadata.get("policy_alignment")
            if not isinstance(policy_alignment, dict):
                policy_alignment = align_policy_evidence(
                    policy_facet,
                    content=content,
                    source_text=source_name,
                )
            source_diagnostics = self._build_selected_source_diagnostics(
                metadata=metadata,
                rank=len(selected_sources) + 1,
            )
            selected_sources.append(
                {
                    "source": source_name,
                    "score": score,
                    "snippet": support or content[:420].strip(),
                    "source_family": family,
                    "source_owner": source_owner,
                    "department": self.department.value,
                    "specialist": specialist,
                    "contract_match_reason": contract_match_reason,
                    "policy_alignment": policy_alignment,
                    "diagnostics": source_diagnostics,
                }
            )
            if family and family not in source_families:
                source_families.append(family)

            for claim in extract_factual_claims(content)[:5]:
                key = (claim, source_name)
                if key in seen_facts:
                    continue
                seen_facts.add(key)
                claim_policy_alignment = align_policy_evidence(
                    policy_facet,
                    content=claim,
                    source_text=source_name,
                ) if policy_facet else policy_alignment
                if (
                    isinstance(policy_alignment, dict)
                    and str(policy_alignment.get("status") or "") in {"conflict", "weak_conflict"}
                    and (
                        not isinstance(claim_policy_alignment, dict)
                        or str(claim_policy_alignment.get("status") or "") not in {"conflict", "weak_conflict"}
                    )
                ):
                    claim_policy_alignment = policy_alignment
                value_roles = self._build_fact_value_roles(
                    claim,
                    policy_alignment=claim_policy_alignment,
                )
                facts.append(
                    {
                        "claim": claim,
                        "source": source_name,
                        "score": score,
                        "support": support[:420],
                        "source_family": family,
                        "source_owner": source_owner,
                        "department": self.department.value,
                        "specialist": specialist,
                        "contract_match_reason": contract_match_reason,
                        "policy_alignment": claim_policy_alignment,
                        "value_roles": value_roles,
                    }
                )
                if len(facts) >= 12:
                    break
            if len(facts) >= 12:
                break

        top_score = max((float(source.get("score") or 0.0) for source in selected_sources), default=0.0)
        confidence = "high" if top_score >= 0.65 else "medium" if top_score >= 0.35 else "low"
        limits: list[str] = []
        if not facts and selected_sources:
            limits.append("Kaynaklarda sayi, tarih veya kosul biciminde ayiklanmis net olgu bulunmadi.")
        required_values: list[str] = []
        supporting_claims: list[str] = []
        value_arbitration = self._build_packet_value_arbitration(facts)
        for fact in facts[:8]:
            claim = str(fact.get("claim") or "").strip()
            if claim and claim not in supporting_claims:
                supporting_claims.append(claim)
            for value in extract_value_labels(claim):
                if value not in required_values:
                    required_values.append(value)
            if len(required_values) >= 10:
                break

        packet = {
            "version": 1,
            "department": self.department.value,
            "answer_role": "evidence_packet",
            "final_answer_owner": final_answer_owner,
            "specialist_response_mode": specialist_response_mode,
            "query_interpretation": query_text[:240],
            "confidence": confidence,
            "generation_mode": generation_mode,
            "answer_summary": answer[:500],
            "source_owner": source_owner,
            "specialist": specialist,
            "specialist_selection": specialist_selection,
            "contract_match_reason": contract_match_reason,
            "facts": facts,
            "required_values": required_values[:10],
            "value_arbitration": value_arbitration,
            "supporting_claims": supporting_claims[:8],
            "source_family": source_families[0] if source_families else None,
            "limits": limits,
            "selected_sources": selected_sources,
        }
        if plan_context:
            if "plan_decision" in plan_context:
                packet["plan_decision"] = plan_context.get("plan_decision") or {}
            if "answer_contract" in plan_context:
                packet["answer_contract"] = plan_context.get("answer_contract") or {}
            if "evidence_contract" in plan_context:
                packet["evidence_contract"] = plan_context.get("evidence_contract") or {}
            if "policy_facet" in plan_context:
                packet["policy_facet"] = plan_context.get("policy_facet") or {}
            if "source_owner" in plan_context:
                packet["source_owner"] = plan_context.get("source_owner") or {}
            if "specialist_selection" in plan_context:
                packet["specialist_selection"] = plan_context.get("specialist_selection") or {}
            if "source_owner_policy" in plan_context:
                packet["source_owner_policy"] = plan_context.get("source_owner_policy") or {}
            if "retrieval_execution_policy" in plan_context:
                packet["retrieval_execution_policy"] = plan_context.get("retrieval_execution_policy") or {}
            if "retrieval_execution_stats" in plan_context:
                packet["retrieval_execution_stats"] = plan_context.get("retrieval_execution_stats") or {}
            if "decision_contract" in plan_context:
                packet["decision_contract"] = plan_context.get("decision_contract") or {}
            if "resolved_decision" in plan_context:
                packet["resolved_decision"] = plan_context.get("resolved_decision") or {}
            if "runtime_authority" in plan_context:
                packet["runtime_authority"] = plan_context.get("runtime_authority") or {}
        return packet

    @staticmethod
    def _build_selected_source_diagnostics(*, metadata: dict, rank: int) -> dict:
        """Return compact chunk/retrieval diagnostics for replay triage."""
        chunk = {
            key: metadata.get(key)
            for key in (
                "chunk_index",
                "chunk_count",
                "madde_no",
                "sub_chunk",
                "parent_context_expanded",
                "merged_chunk_count",
                "merged_parent_id",
            )
            if metadata.get(key) not in (None, "")
        }
        retrieval = {
            key: metadata.get(key)
            for key in (
                "score_type",
                "retrieval_collection",
                "retrieval_collection_role",
                "source_constrained_recall",
                "department_scoped_recall",
                "department_scoped_recall_student_department",
                "source_owner_compatible",
                "source_owner_avoid_match",
                "policy_alignment_score",
            )
            if metadata.get(key) not in (None, "")
        }
        return {
            "rank": rank,
            "chunk": chunk,
            "retrieval": retrieval,
        }

    @staticmethod
    def _build_plan_context_from_metadata(meta: dict) -> dict:
        """Extract plan/contract metadata supplied by the capability planner."""
        planner_payload = meta.get("capability_planner")
        action_payload = {}
        if isinstance(planner_payload, dict) and isinstance(planner_payload.get("action"), dict):
            action_payload = dict(planner_payload.get("action") or {})
        plan_decision = meta.get("plan_decision")
        if not isinstance(plan_decision, dict) and action_payload:
            plan_decision = {
                "intent": action_payload.get("intent"),
                "capability": action_payload.get("capability"),
                "params": action_payload.get("params") or {},
                "missing_slots": action_payload.get("missing_params") or [],
                "answer_contract": action_payload.get("answer_contract") or {},
                "evidence_contract": action_payload.get("evidence_contract") or {},
                "fallback_route": action_payload.get("fallback_route") or action_payload.get("fallback"),
                "confidence": action_payload.get("confidence"),
                "reasoning": action_payload.get("reasoning"),
            }
        answer_contract = meta.get("answer_contract")
        if not isinstance(answer_contract, dict):
            answer_contract = action_payload.get("answer_contract") or {}
        evidence_contract = meta.get("evidence_contract")
        if not isinstance(evidence_contract, dict):
            evidence_contract = action_payload.get("evidence_contract") or {}
        context = {
            "plan_decision": plan_decision if isinstance(plan_decision, dict) else {},
            "answer_contract": answer_contract if isinstance(answer_contract, dict) else {},
            "evidence_contract": evidence_contract if isinstance(evidence_contract, dict) else {},
        }
        source_owner = meta.get("source_owner")
        if isinstance(source_owner, dict):
            context["source_owner"] = source_owner
        specialist_selection = meta.get("specialist_selection")
        if isinstance(specialist_selection, dict):
            context["specialist_selection"] = specialist_selection
        decision_contract = meta.get("decision_contract")
        if isinstance(decision_contract, dict):
            context["decision_contract"] = decision_contract
        resolved_decision = meta.get("resolved_decision")
        if isinstance(resolved_decision, dict):
            context["resolved_decision"] = resolved_decision
        runtime_authority = meta.get("runtime_authority")
        if isinstance(runtime_authority, dict):
            context["runtime_authority"] = runtime_authority
        policy_facet = meta.get("policy_facet")
        if not isinstance(policy_facet, dict):
            capability = str(
                plan_decision.get("capability")
                if isinstance(plan_decision, dict)
                else action_payload.get("capability")
                or ""
            ).strip()
            if capability == "student_affairs.policy_lookup":
                params = (
                    plan_decision.get("params")
                    if isinstance(plan_decision, dict) and isinstance(plan_decision.get("params"), dict)
                    else action_payload.get("params")
                    if isinstance(action_payload.get("params"), dict)
                    else {}
                )
                policy_facet = resolve_policy_facet(
                    query=str(params.get("query") or meta.get("query_text") or ""),
                    params=params,
                    answer_contract=answer_contract if isinstance(answer_contract, dict) else {},
                )
        if isinstance(policy_facet, dict):
            context["policy_facet"] = policy_facet
        return {key: value for key, value in context.items() if value}

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

    @staticmethod
    def _build_fact_value_roles(
        claim: str,
        *,
        policy_alignment: dict | None = None,
    ) -> list[dict[str, str]]:
        alignment_status = (
            str(policy_alignment.get("status") or "")
            if isinstance(policy_alignment, dict)
            else ""
        )
        normalized = normalize_text(claim)
        roles: list[dict[str, str]] = []
        for value in extract_value_labels(claim):
            value_norm = normalize_text(value)
            position = normalized.find(value_norm)
            if position < 0:
                position = normalized.find(value_norm.replace(",", "."))
            window_after = normalized[position: position + 55] if position >= 0 else normalized
            window = normalized[max(0, position - 55): position + 55] if position >= 0 else normalized
            role = "supporting_value"
            if alignment_status == "conflict":
                role = "conflicting_threshold"
            elif alignment_status == "weak_conflict":
                role = "secondary_program_threshold"
            elif value_norm.startswith("%") or value_norm.startswith("yuzde"):
                role = "related_condition"
            elif re.search(r"\b(?:uzerinden|puan\s+uzerinden)\b", window_after[:40]):
                role = "scale_value"
            elif any(marker in window for marker in ("en az", "en cok", "asgari", "azami", "minimum", "maksimum")):
                role = "answer_threshold"
            roles.append(
                {
                    "value": value,
                    "role": role,
                    "policy_alignment_status": alignment_status or "unknown",
                }
            )
        return roles

    @staticmethod
    def _build_packet_value_arbitration(facts: Sequence[dict]) -> dict[str, list[str]]:
        result = {
            "primary_values": [],
            "related_values": [],
            "secondary_values": [],
            "conflicting_values": [],
        }
        target_by_role = {
            "answer_threshold": "primary_values",
            "related_condition": "related_values",
            "secondary_program_threshold": "secondary_values",
            "conflicting_threshold": "conflicting_values",
        }
        for fact in facts:
            for item in fact.get("value_roles") or []:
                if not isinstance(item, dict):
                    continue
                target = target_by_role.get(str(item.get("role") or ""))
                value = str(item.get("value") or "").strip()
                if target and value and value not in result[target]:
                    result[target].append(value)
        return result

    @staticmethod
    def _apply_plan_evidence_source_bias(
        results: Sequence[dict],
        plan_context: dict | None,
    ) -> list[dict]:
        """Apply planner-provided source preferences without affecting legacy flows."""
        if not results or not plan_context:
            return list(results)
        evidence_contract = plan_context.get("evidence_contract")
        if not isinstance(evidence_contract, dict):
            evidence_contract = {}
        policy_facet = plan_context.get("policy_facet")
        if not isinstance(policy_facet, dict):
            policy_facet = {}

        preferred = BaseSpecialistAgent._normalized_contract_markers(
            evidence_contract.get("preferred_sources")
        )
        avoid = BaseSpecialistAgent._normalized_contract_markers(
            evidence_contract.get("avoid_sources")
        )
        has_policy_facet = bool(policy_facet)
        if not preferred and not avoid and not has_policy_facet:
            return list(results)

        adjusted: list[dict] = []
        changed = False
        for item in results:
            candidate = dict(item)
            metadata = candidate.get("metadata") or {}
            source_text = " ".join(
                normalize_text(str(value or ""))
                for value in (
                    candidate.get("source"),
                    metadata.get("source"),
                    metadata.get("file_name"),
                    metadata.get("title"),
                    metadata.get("relative_path"),
                    metadata.get("source_url"),
                    metadata.get("category"),
                    metadata.get("subcategory"),
                )
            )
            content_text = normalize_text(str(candidate.get("content") or "")[:900])
            haystack = f"{source_text} {content_text}"
            score = float(candidate.get("score", 0.0))
            updated_score = score
            if preferred and any(marker in haystack for marker in preferred):
                updated_score += 0.22
            if avoid and any(marker in haystack for marker in avoid):
                updated_score *= 0.30
            policy_alignment = align_policy_evidence(
                policy_facet,
                content=str(candidate.get("content") or ""),
                source_text=source_text,
            )
            updated_score = (
                (updated_score + float(policy_alignment.get("score_delta") or 0.0))
                * float(policy_alignment.get("score_multiplier") or 1.0)
            )
            if updated_score != score or has_policy_facet:
                candidate["score"] = round(updated_score, 6)
                candidate_metadata = dict(metadata)
                if has_policy_facet:
                    candidate_metadata["policy_facet"] = {
                        "facet": policy_facet.get("facet"),
                        "target_program": policy_facet.get("target_program"),
                        "reason": policy_facet.get("reason"),
                    }
                    candidate_metadata["policy_alignment"] = policy_alignment
                candidate["metadata"] = candidate_metadata
                if updated_score != score:
                    changed = True
            adjusted.append(candidate)

        if changed:
            adjusted.sort(key=lambda item: float(item.get("score", 0.0)), reverse=True)
        return adjusted

    @staticmethod
    def _normalized_contract_markers(value: object) -> tuple[str, ...]:
        if not isinstance(value, (list, tuple, set)):
            return ()
        markers = []
        for item in value:
            normalized = normalize_text(str(item or ""))
            if normalized:
                markers.append(normalized)
        return tuple(dict.fromkeys(markers))

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
        return looks_like_contact_intent(query_text)

    async def _fetch_contacts(
        self,
        *,
        department: Department,
        agent_id: str | None = None,
        include_generic: bool = True,
    ) -> list[OfficeContactRecord]:
        fetch_kwargs = {
            "department": department,
            "agent_id": agent_id,
        }
        if self._contact_fetcher_accepts_include_generic():
            fetch_kwargs["include_generic"] = include_generic
        return await self._contact_fetcher(**fetch_kwargs)

    def _contact_fetcher_accepts_include_generic(self) -> bool:
        try:
            signature = inspect.signature(self._contact_fetcher)
        except (TypeError, ValueError):
            return True
        parameters = signature.parameters
        if "include_generic" in parameters:
            return True
        return any(parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in parameters.values())

    async def _handle_contact_request(self) -> DepartmentResponse:
        """Ajanla iliskili ofis iletisim bilgilerini sunar."""
        contacts = await self._fetch_contacts(
            department=self.department,
            agent_id=self.agent_id,
            include_generic=False,
        )
        if not contacts:
            contacts = await self._fetch_contacts(department=self.department)
        if not contacts:
            return DepartmentResponse(
                department=self.department,
                answer=(
                    "Şu anda bu alan için kayıtlı iletişim bilgisi bulunamadı. "
                    "Öğrenci İşleri Daire Başkanlığı genel hattından yardım alabilirsiniz."
                ),
                generation_mode="kural",
                success=True,
            )

        lines = ["İlgili birim iletişim bilgileri:"]
        for contact in contacts:
            parts = [f"- {contact.unit_name}"]
            if contact.person_name:
                title_str = f" - {contact.title}" if contact.title else ""
                parts.append(f"  {contact.person_name}{title_str}")
            if contact.phone_ext:
                parts.append(f"  Telefon: {OMU_SWITCHBOARD_PHONE} / Dahili: {contact.phone_ext}")
            else:
                parts.append(f"  Santral: {OMU_SWITCHBOARD_PHONE}")
            if contact.email:
                parts.append(f"  E-Posta: {contact.email}")
            lines.append("\n".join(parts))

        return DepartmentResponse(
            department=self.department,
            answer="\n".join(lines),
            generation_mode="kural",
            success=True,
        )

    # ── Deterministik answer completeness check ──────────────────
    # Soru tipine gore cevapta zorunlu alan kontrolu.
    # Ekstra LLM cagrisi YOK — sadece regex/pattern bazli kontrol.

    _QUESTION_TYPE_PATTERNS: ClassVar[list[tuple[str, re.Pattern, tuple[str, ...]]]] = [
        # (tip, sorgu_paterni, cevapta_beklenen_kalip)
        ("ne_zaman", re.compile(r"\bne zaman\b|\bzamani\b|\btarihi\b|\btarih\b|\bne kadar sure\b", re.I),
         (r"\d{1,2}[\./-]\d{1,2}", r"\d{4}", r"\bhafta\b", r"\bgun\b", r"\bay\b",
          r"\bdonem\b", r"\bbaslangic\b", r"\bbitis\b", r"\bsure\b", r"\bdeadline\b",
          r"\bicerisinde\b", r"\bitibaren\b", r"\bkadar\b", r"\bonce\b", r"\bsonra\b")),
        ("kac_ne_kadar", re.compile(r"\bkac\b|\bne kadar\b|\bmiktari\b|\btutari\b|\bucreti\b", re.I),
         (r"\d+", r"\bAKTS\b", r"\bkredi\b", r"\bTL\b", r"\byuzde\b", r"\boran\b",
          r"\btutar\b", r"\bucret\b", r"\bsayi\b", r"\bnet tutar yok\b")),
        ("hangi_belge", re.compile(r"\bhangi belge\b|\bnereden al\b|\bform\b|\bdilekce\b|\bdekont\b", re.I),
         (r"\bform\b", r"\bdilekce\b", r"\bbelge\b", r"\bdekont\b", r"\bbasvuru\b",
          r"\bnereden\b", r"\bplatform\b", r"\bsistem\b", r"\bweb\b", r"\binternet\b")),
        ("kimler", re.compile(r"\bkimler\b|\bkimler katil\b|\bkatilabilir\b|\buygun\b|\bhangi ogrenci\b", re.I),
         (r"\bogrenci\b", r"\blisans\b", r"\bonlisans\b", r"\byuksek lisans\b",
          r"\bkosul\b", r"\bsart\b", r"\buygun\b", r"\bhak\b", r"\bkatil\b")),
    ]

    @classmethod
    def _check_answer_completeness(cls, query: str, answer: str) -> str | None:
        """Cevapta soru tipinin gerektirdigi bilgi var mi kontrol et.
        Eksikse uyari mesaji don, doluysa None don.
        """
        q_lower = normalize_text(query)
        answer_normalized = normalize_text(answer)
        for q_type, q_pattern, a_patterns in cls._QUESTION_TYPE_PATTERNS:
            if not q_pattern.search(q_lower):
                continue
            # Cevapta en az bir beklenen kalip var mi?
            if any(re.search(ap, answer_normalized, re.I) for ap in a_patterns):
                return None
            # Eksik — uyari don
            return (
                f"Bu konuda elimdeki kaynaklarda net {q_type.replace('_', ' ')} bilgisi bulunamadı. "
                "Soruyu daha detaylı sorabilir veya ilgili birimle iletişime geçebilirsin."
            )
        return None

    # ── Evidence boost — soru tipine gore ilgili evidence oncelendirme ──

    _EVIDENCE_BOOST_PATTERNS: ClassVar[list[tuple[re.Pattern, tuple[str, ...], float]]] = [
        # (sorgu_paterni, evidence_sinyal_kelimeleri, boost)
        (re.compile(r"\bmezun\w*.*\bakts\b|\bakts\b.*\bmezun\w*|\bmezuniyet\b.*\bkredi\b|\bkredi\b.*\bmezuniyet\b", re.I),
         ("mezun olabilmek", "240 akts", "300 akts", "360 akts", "120 akts",
          "dort yillik", "bes yillik", "alti yillik", "meslek yuksekokulu",
          "on lisans", "lisans", "yonetmelik"), 0.12),
        (re.compile(r"\bne zaman\b|\bzamani\b|\btarihi\b", re.I),
         ("tarih", "sure", "hafta", "gun", "ay", "donem", "baslangic", "bitis", "deadline",
          "itibaren", "kadar", "once", "sonra", "icerisinde"), 0.05),
        (re.compile(r"\bkac\b|\bne kadar\b|\bucreti\b|\btutari\b", re.I),
         ("akts", "kredi", "tl", "yuzde", "oran", "tutar", "ucret", "sayi", "adet"), 0.05),
        (re.compile(r"\bhangi belge\b|\bnereden al\b|\bform\b", re.I),
         ("form", "dilekce", "belge", "dekont", "platform", "web", "sistem", "basvuru"), 0.05),
        # AKTS/GANO ders kaydi sorularinda regulation/registration kaynaklari oncelikli
        (re.compile(r"\bakts hakki\b|\bakts siniri\b|\bkredi hakki\b|\bkredi siniri\b|\bders yuku\b|\bgano.*akts\b|\bakts.*gano\b|\bdonemlik akts\b|\bkac akts alabilirim\b", re.I),
         ("ders kaydi", "akts hakki", "kredi siniri", "gno", "donem yuku", "azami",
          "yonetmelik", "yonerge", "kayit", "basvuru"), 0.08),
        # Tek ders sinavi sorularinda devam sarti / almis olma kosulu kaynaklari oncelikli
        (re.compile(r"\btek ders\b|\btek derse\b|\btek ders sinavi\b", re.I),
         ("devam sarti", "devam sartini", "almis olmak", "almamis", "giremez",
          "basar", "basarisiz", "mezuniyet", "yonetmelik", "tek ders sinavi"), 0.10),
    ]

    # AKTS/GANO sorularinda ilgisiz kaynaklari demote et
    _EVIDENCE_DEMOTE_PATTERNS: ClassVar[list[tuple[re.Pattern, tuple[str, ...], float]]] = [
        # (sorgu_paterni, demote_sinyal_kelimeleri, penalty)
        (re.compile(r"\bmezun\w*.*\bakts\b|\bakts\b.*\bmezun\w*|\bmezuniyet\b.*\bkredi\b|\bkredi\b.*\bmezuniyet\b", re.I),
         ("pedagojik formasyon", "erasmus", "uluslararasi", "degisim", "ozel ogrenci",
          "staj", "yatay gecis", "harc", "odeme", "ucret", "dekont"), -0.12),
        (re.compile(r"\bakts\b|\bakts hakki\b|\bkredi siniri\b|\bders yuku\b|\bgano.*akts\b|\bakts.*gano\b", re.I),
         ("erasmus", "uluslararasi", "staj", "yatay gecis", "mup", "sanayi",
          "bitirme", "harc", "odeme", "ucret", "dekont"), -0.10),
    ]

    @classmethod
    def _apply_evidence_boost(cls, query: str, results: list[dict]) -> list[dict]:
        """Soru tipine gore ilgili icerik sinyali tasiyan evidence'lara kucuk boost ver."""
        q_lower = normalize_text(query)
        for q_pattern, signals, boost in cls._EVIDENCE_BOOST_PATTERNS:
            if not q_pattern.search(q_lower):
                continue
            for r in results:
                content = normalize_text(r.get("content") or "")
                if any(s in content for s in signals):
                    r["score"] = float(r.get("score", 0.0)) + boost
            break  # ilk eslesen kurali uygula, digerlerini atla
        # Demote: ilgisiz kaynaklari cezalandir
        for q_pattern, demote_signals, penalty in cls._EVIDENCE_DEMOTE_PATTERNS:
            if not q_pattern.search(q_lower):
                continue
            for r in results:
                content = normalize_text(r.get("content") or "")
                if any(s in content for s in demote_signals):
                    r["score"] = max(0.0, float(r.get("score", 0.0)) + penalty)
            break
        return results

    def _apply_multi_query_expansion(
        self,
        query: str,
        results: list[dict],
        *,
        retriever: HybridRetriever,
        top_k: int | None,
        department: Department | str | None,
        source_hints: list[str] | None = None,
        topic_hint: str | None = None,
        student_department: str | None = None,
        source_owner: str | None = None,
        policy: RetrievalExecutionPolicy | None = None,
        skip: bool = False,
        stats: dict[str, object] | None = None,
    ) -> list[dict]:
        """Search variant queries from MQE and merge into primary results.

        Each variant query is searched independently. Results are merged
        with deduplication (by content prefix) and re-sorted by score.
        The primary query results always take priority.
        """
        if skip:
            if stats is not None:
                stats["multi_query_skipped"] = True
                stats.setdefault("multi_query_skip_reason", "strong_primary_evidence")
            return results
        max_variants = policy.max_multi_query_variants if policy is not None else settings.rag.primary_multi_query_max_variants
        if max_variants <= 0:
            if stats is not None:
                stats["multi_query_skipped"] = True
                stats.setdefault("multi_query_skip_reason", "policy_disabled")
            return results
        expanded = _expand_multi_queries(query)
        if not expanded.variants:
            if stats is not None:
                stats["multi_query_skipped"] = True
                stats.setdefault("multi_query_skip_reason", "no_variants")
            return results

        seen_prefixes: set[str] = set()
        for item in results:
            prefix = normalize_text(str(item.get("content") or ""))[:120]
            seen_prefixes.add(prefix)

        merged_new: list[dict] = []
        for variant in expanded.variants[:max_variants]:
            try:
                if stats is not None:
                    stats["search_calls"] = int(stats.get("search_calls") or 0) + 1
                    stats["multi_query_variant_count"] = int(stats.get("multi_query_variant_count") or 0) + 1
                variant_results = retriever.search(
                    variant,
                    top_k=policy.variant_top_k if policy is not None else max(3, (top_k or 5) // 2),
                    department=department,
                    source_hints=source_hints,
                    topic_hint=topic_hint,
                    student_department=student_department,
                    source_owner=source_owner,
                    reranker_candidate_limit=(
                        policy.variant_reranker_candidate_limit if policy is not None else None
                    ),
                )
            except Exception:
                logger.debug(
                    "multi_query_variant_search_failed variant=%s",
                    variant,
                    exc_info=True,
                )
                continue

            for item in variant_results:
                prefix = normalize_text(str(item.get("content") or ""))[:120]
                if prefix in seen_prefixes:
                    continue
                seen_prefixes.add(prefix)
                # Mark the item as coming from MQE for diagnostics
                item_meta = dict(item.get("metadata") or {})
                item_meta["mqe_variant"] = variant
                item["metadata"] = item_meta
                merged_new.append(item)

        if stats is not None:
            stats["multi_query_added_results"] = int(stats.get("multi_query_added_results") or 0) + len(merged_new)
        if not merged_new:
            return results

        combined = list(results) + merged_new
        combined.sort(key=lambda item: float(item.get("score", 0.0)), reverse=True)
        # Cap to reasonable size
        max_results = max(len(results), (top_k or 5) + 4)
        logger.info(
            "multi_query_merge primary=%d added=%d total=%d profile=%s",
            len(results),
            len(merged_new),
            len(combined[:max_results]),
            expanded.profile,
        )
        return combined[:max_results]

    async def _generate_answer(
        self,
        query_text: str,
        results: Sequence[dict],
        *,
        db_context: str | None = None,
        force_llm: bool = False,
        allow_llm: bool = True,
        llm_profile: str | None = None,
        plan_context: dict | None = None,
    ) -> tuple[str, str]:
        """Tek yanit uretim noktasi. Tum ajanlar bu metodu kullanmali."""
        # Evidence boost — soru tipine gore ilgili evidence oncelendirme
        if results:
            results = self._apply_evidence_boost(query_text, list(results))

        if not results and not db_context:
            return (
                "Bu konuda elimde yeterli kaynak bulunamadı. "
                "Soruyu biraz daha detaylandırırsan veya ilgili birimle iletişime geçersen daha net yardımcı olabilirim."
            ), "kural"

        if results and not db_context:
            top_meta = results[0].get("metadata") or {}
            score_type_raw = str(top_meta.get("score_type", "")).lower()
            top_score = float(results[0].get("score", 0.0))
            top_source = results[0].get("source", "?")
            logger.info(
                (
                    "generate_answer_score_check agent=%s top_score=%.4f "
                    "score_type=%s top_source=%s result_count=%s"
                ),
                self.agent_id,
                top_score,
                score_type_raw,
                top_source,
                len(results),
            )
            if score_type_raw == "reranker" and top_score < 0.10:
                logger.info(
                    "low_rag_score_kept_for_llm agent=%s top_reranker_score=%.4f",
                    self.agent_id,
                    top_score,
                )

        if not allow_llm or not settings.llm.specialist_synthesis_enabled:
            if allow_llm and not settings.llm.specialist_synthesis_enabled:
                logger.info(
                    "specialist_llm_synthesis_disabled agent=%s",
                    self.agent_id,
                )
            with profile_stage("agent.source_only_answer", agent_id=self.agent_id):
                return (
                    self._build_source_only_answer(query_text, results, db_context=db_context),
                    self._derive_non_llm_generation_mode(results, db_context=db_context),
                )

        force_specialist_llm = force_llm or self._should_force_llm_synthesis(
            query_text,
            results,
            db_context=db_context,
        )
        # Legacy path: specialist LLM synthesis is kept behind
        # LLM_SPECIALIST_SYNTHESIS_ENABLED. The main orchestrator owns normal
        # final-answer synthesis; this path is only for explicit fallback modes.

        with profile_stage("agent.llm_synthesize", agent_id=self.agent_id):
            answer, gen_mode = await self._llm_synthesize(
                query_text,
                results,
                db_context=db_context,
                llm_profile=llm_profile,
                force_llm=force_specialist_llm,
                plan_context=plan_context,
            )

        # Claim guard — conservative check against evidence
        if gen_mode not in ("kural",):
            try:
                from src.quality.claim_guard import guard_answer as _guard_answer
                from src.core.profiling import get_current_profiler

                _profiler = get_current_profiler()
                # Recover evidence items from the extraction stage
                evidence_items_for_guard = getattr(self, "_last_evidence_items", None)
                if evidence_items_for_guard:
                    with profile_stage("agent.claim_guard", agent_id=self.agent_id):
                        guard_result = _guard_answer(answer, evidence_items_for_guard)
                        answer = guard_result.cleaned_answer
                        if _profiler is not None:
                            _profiler.set_attribute("claim_guard", {
                                "unsupported_claims": guard_result.unsupported_claims,
                                "modifications_made": guard_result.modifications_made,
                            })
            except Exception:
                logger.debug("claim_guard_skipped agent=%s", self.agent_id, exc_info=True)

        # Deterministik completeness check — soru tipine gore cevapta zorunlu alan kontrolu
        if gen_mode not in ("kural",):
            completeness_warning = self._check_answer_completeness(query_text, answer)
            if completeness_warning:
                logger.info(
                    "answer_completeness_warning agent=%s query_type_match",
                    self.agent_id,
                )
                answer = f"{answer}\n\n{completeness_warning}"

        return answer, gen_mode

    # Çok-parçalı soru kalıpları — tek RAG kaynaktan cevaplanamaz
    _MULTI_PART_QUERY_MARKERS = frozenset({
        "ve", "ayrica", "ayrıca", "bunun yaninda", "bunun yani sira",
        "hem", "hem de", "ile birlikte", "hangileri", "neler",
    })

    def _should_force_llm_synthesis(
        self,
        query_text: str,
        results: Sequence[dict],
        *,
        db_context: str | None = None,
    ) -> bool:
        """Belirli sorgulari dogrudan LLM sentezine zorlar."""
        # 1) Soru birden fazla alt-soru iceriyorsa LLM sentez sart
        lowered = normalize_text(query_text)
        marker_count = sum(1 for m in self._MULTI_PART_QUERY_MARKERS if m in lowered)
        if marker_count >= 2:
            return True

        # 2) Birden fazla guclu kaynak varsa (skor > 0.50 ve 2+ adet) → sentez gerekli
        strong_results = [
            r for r in results[:5]
            if float(r.get("score", 0.0)) >= 0.50
        ]
        if len(strong_results) >= 3:
            return True

        # 3) Prosedur/nasil sorulari → LLM sentez sart (kural modu yetersiz)
        _PROCEDURE_FORCE_MARKERS = (
            "nasil", "ne yap", "nereden", "nereye", "hangi birim",
            "yapabil", "yapamam", "yapabilir", "yapamaz",
            "girebil", "giremez", "alabil", "alamaz",
            "mi ", "mu ", "miyim", "muyum", "miyiz", "muyuz",
            "gerekiyor", "gerekir", "zorunlu",
            "ne zaman", "kimler", "katilabilir", "basvurusu",
            "basvuru", "kosullari", "sartlari", "nelere",
        )
        if any(m in lowered for m in _PROCEDURE_FORCE_MARKERS):
            return True

        return False

    def _should_use_llm_evidence_selection(
        self,
        query_text: str,
        evidence_items: Sequence,
        *,
        force_llm: bool,
        db_context: str | None = None,
    ) -> bool:
        """Allow agents to keep final synthesis while skipping the extra selector call."""
        _ = query_text, force_llm, db_context
        min_candidates = max(
            1,
            int(settings.rag.llm_evidence_selection_min_candidates),
        )
        return (
            settings.rag.llm_evidence_selection_enabled
            and len(evidence_items) >= min_candidates
        )

    def _build_source_only_answer(
        self,
        query_text: str,
        results: Sequence[dict],
        *,
        db_context: str | None = None,
    ) -> str:
        """LLM sentezi atlandiginda gosterilecek guvenli kaynak yaniti."""
        return self._build_llm_failure_fallback(
            results,
            db_context=db_context,
            query_text=query_text,
        )

    def _filter_results_for_answer(
        self,
        query_text: str,
        results: Sequence[dict],
    ) -> list[dict]:
        """Allow specialist agents to drop misleading retrieval results."""
        _ = query_text
        return list(results)

    def _should_enrich_results(self, query_text: str, results: Sequence[dict]) -> bool:
        """Allow agents to skip expensive neighbor expansion when compact evidence is better."""
        _ = query_text, results
        return True

    def _llm_synthesis_timeout_seconds(
        self,
        query_text: str,
        results: Sequence[dict],
        *,
        llm_profile: str | None = None,
    ) -> float:
        """Allow agents to cap slow external LLM calls for low-risk short answers."""
        _ = query_text, results, llm_profile
        return float(_LLM_SYNTHESIS_TIMEOUT_SECONDS)

    async def _apply_judge_quality_gate(
        self,
        *,
        query_text: str,
        answer: str,
        system: str,
        context_chunks: Sequence[str],
        evidence_items: Sequence,
        intent_coverage,
        llm_profile: str | None,
        synthesis_timeout: float,
        plan_context: dict | None = None,
    ) -> tuple[str, dict]:
        """Run the optional one-shot LLM judge and apply at most one repair.

        The judge is intentionally bounded: one evaluation and one corrective
        generation. This keeps latency predictable while catching risky
        numeric/regulation/no-info/foreign-token answers.
        """
        from src.core.profiling import get_current_profiler
        from src.quality.answer_filter import check_answer_quality, REWRITE_ONLY_SYSTEM_SUFFIX
        from src.quality.judge import run_judge

        quality = check_answer_quality(answer)
        evidence_summary = "\n\n".join(context_chunks[:5])
        judge_meta: dict = {
            "judge_enabled": False,
            "judge_action": "not_run",
            "retry_count": 0,
        }
        has_plan_contract = bool(
            (plan_context or {}).get("answer_contract")
            or (plan_context or {}).get("evidence_contract")
        )
        if not has_plan_contract and not settings.llm.specialist_judge_enabled:
            return answer, judge_meta

        judge_result = await run_judge(
            query=query_text,
            answer=answer,
            evidence_summary=evidence_summary,
            plan_decision=(plan_context or {}).get("plan_decision"),
            answer_contract=(plan_context or {}).get("answer_contract"),
            evidence_contract=(plan_context or {}).get("evidence_contract"),
            llm_service=self.llm_service,
            llm_profile=llm_profile,
            has_foreign_suspicion=quality.needs_rewrite,
            intent_coverage_is_low=bool(getattr(intent_coverage, "is_low", False)),
            missing_intents=list(getattr(intent_coverage, "missing_intents", []) or []),
        )
        if judge_result is None:
            return answer, judge_meta

        judge_meta.update(
            {
                "judge_enabled": True,
                "judge_action": judge_result.action,
                "approved": judge_result.approved,
                "failure_reason": judge_result.failure_reason,
                "missing_intents": judge_result.missing_intents,
                "unsupported_claims": judge_result.unsupported_claims,
                "bad_tokens": judge_result.bad_tokens,
                "suggested_query": judge_result.suggested_query,
            }
        )
        _profiler = get_current_profiler()
        if _profiler is not None:
            _profiler.set_attribute("answer_judge", judge_meta)

        if judge_result.approved or judge_result.action == "accept":
            return answer, judge_meta

        if judge_result.action == "ask_clarification":
            judge_meta["retry_count"] = 1
            clarification = (
                "Bu soruyu doğru cevaplayabilmem için eksik bir bilgi var. "
                "Bölüm/program, öğrenci türü veya hangi başvuru/işlem hakkında sorduğunuzu belirtir misiniz?"
            )
            return clarification, judge_meta

        repair_context = evidence_summary
        repair_query = query_text

        if judge_result.action == "retrieve_again" and judge_result.suggested_query:
            try:
                with profile_stage("agent.judge_retrieve_again", agent_id=self.agent_id):
                    retry_results = self._get_retriever().search(
                        judge_result.suggested_query,
                        top_k=8,
                        department=self.department,
                    )
                    retry_results = self._apply_evidence_boost(
                        judge_result.suggested_query,
                        list(retry_results),
                    )
                    retry_items = extract_evidence_items(
                        judge_result.suggested_query,
                        retry_results[:8],
                        self.department.value,
                        analysis_query=_EVIDENCE_QUERY_PREPROCESSOR.preprocess(
                            judge_result.suggested_query
                        ),
                    )
                    if retry_items:
                        repair_context = "\n\n".join(
                            build_evidence_context_chunks(
                                retry_items,
                                judge_result.suggested_query,
                                max_items=5,
                                max_content_len=_SPECIALIST_LLM_CONTEXT_MAX_LEN,
                            )
                        )
                        repair_query = judge_result.suggested_query
                        judge_meta["retrieve_again_results"] = len(retry_results)
            except Exception:
                logger.debug("judge_retrieve_again_failed agent=%s", self.agent_id, exc_info=True)

        try:
            with profile_stage("agent.judge_repair", agent_id=self.agent_id, action=judge_result.action):
                repair_prompt = (
                    f"Kullan\u0131c\u0131 sorusu:\n{repair_query}\n\n"
                    f"\u00d6nceki cevap:\n{answer}\n\n"
                    f"Judge sorunu:\n{judge_result.failure_reason or judge_result.action}\n\n"
                    f"Kaynak ba\u011flam\u0131:\n{repair_context}\n\n"
                    "Cevab\u0131 ayn\u0131 kaynaklara dayanarak yeniden yaz. "
                    "Eksik alt niyetleri tamamla, yanl\u0131\u015f/desteklenmeyen iddialar\u0131 \u00e7\u0131kar, "
                    "say\u0131/tarih/\u00fccret/AKTS/GANO bilgilerini kaynakta ge\u00e7en \u015fekliyle koru. "
                    "Kaynakta yoksa uydurma. Do\u011fal T\u00fcrk\u00e7e d\u0131\u015f\u0131nda kelime kullanma."
                )
                repaired = await asyncio.wait_for(
                    self.llm_service.generate(
                        prompt=repair_prompt,
                        system=system + REWRITE_ONLY_SYSTEM_SUFFIX,
                        model_role="specialist_synthesis",
                        llm_profile=llm_profile,
                    ),
                    timeout=synthesis_timeout,
                )
                if repaired and len(repaired.strip()) > 12:
                    judge_meta["retry_count"] = 1
                    return repaired, judge_meta
        except Exception as exc:
            logger.warning(
                "judge_repair_failed agent=%s action=%s reason=%s",
                self.agent_id,
                judge_result.action,
                type(exc).__name__,
            )

        return answer, judge_meta

    def _search_top_k(self, query_text: str, metadata: dict) -> int | None:
        """Allow specialist agents to request a wider retrieval result set."""
        _ = query_text, metadata
        return None

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

    async def _llm_synthesize(
        self,
        query_text: str,
        results: Sequence[dict],
        *,
        db_context: str | None = None,
        llm_profile: str | None = None,
        force_llm: bool = False,
        plan_context: dict | None = None,
    ) -> tuple[str, str]:
        """RAG kaynaklarini (ve varsa DB baglamini) LLM ile sentezler."""
        # LLM sentez esiginde threshold kontrolunu kaldirildi —
        # kaynak bulunduysa LLM'e birakilir, LLM kaynakta bilgi yoksa kendisi soyler.
        # Sadece tamamen ilgisiz (0.10 alti) skorlari zaten _generate_answer'da filtreleniyor.

        # ── Structured Evidence Pipeline ─────────────────────
        with profile_stage("agent.evidence_extraction", agent_id=self.agent_id):
            # Pre-filter: FAQ extraction on raw content
            preprocessed_results = []
            for item in results[:8]:
                item_copy = dict(item)
                source = item_copy.get("source", "bilinmiyor")
                if _is_faq_source(source) and query_text:
                    item_copy["content"] = _extract_relevant_faq_block(
                        item_copy.get("content", ""), query_text,
                    )
                preprocessed_results.append(item_copy)

            evidence_items = extract_evidence_items(
                query_text,
                preprocessed_results,
                self.department.value if hasattr(self, "department") else "",
                analysis_query=_EVIDENCE_QUERY_PREPROCESSOR.preprocess(query_text),
            )

            # Low-score keyword overlap filter (preserve existing behavior)
            # BUT: if reranker score >= 0.45, trust the reranker's semantic
            # understanding — semantic paraphrases (e.g. "bırakıp ayrılmak"
            # ↔ "ilişik kesme") have low term overlap but high reranker scores.
            if not force_llm:
                _kept_evidence: list = []
                for ev in evidence_items:
                    if ev.score < 0.55 and not ev.matched_query_terms:
                        # Reranker trusts this source — keep it despite low overlap
                        if ev.score >= 0.45 and ev.score_type == "reranker":
                            _kept_evidence.append(ev)
                            continue
                        _kw_overlap = self._compute_keyword_overlap(
                            query_text, ev.content_snippet,
                        )
                        if _kw_overlap < 0.10:
                            logger.info(
                                "llm_context_filtered source=%s score=%.3f keyword_overlap=%.3f",
                                ev.source_name, ev.score, _kw_overlap,
                            )
                            continue
                    _kept_evidence.append(ev)
                # Filtreleme sonrasi evidence sifir olursa, orijinal evidence'in
                # en az 1 tanesini koru — LLM kaynakta bilgi yoksa kendisi soyler.
                if not _kept_evidence and evidence_items:
                    _kept_evidence = [evidence_items[0]]
                    logger.info(
                        "evidence_filter_kept_top_fallback agent=%s score=%.3f",
                        self.agent_id, evidence_items[0].score,
                    )
                evidence_items = _kept_evidence

            # Evidence varsa LLM'e birak; LLM kaynakta bilgi yoksa kendisi soyler.
            # Sadece evidence hic yoksa (0 sonuc) Kural fallback zaten _generate_answer'da yapiliyor.

            evidence_max_items = 8 if force_llm else 5
            selector_max_items = min(
                evidence_max_items,
                max(1, int(settings.rag.llm_evidence_selection_max_selected)),
            )
            if self._should_use_llm_evidence_selection(
                query_text,
                evidence_items,
                force_llm=force_llm,
                db_context=db_context,
            ):
                with profile_stage("agent.evidence_selection", agent_id=self.agent_id):
                    evidence_items, selection_decision = await select_evidence_with_llm(
                        query_text,
                        evidence_items,
                        self.llm_service,
                        llm_profile=llm_profile,
                        max_selected=selector_max_items,
                    )
            else:
                original_candidate_count = len(evidence_items)
                evidence_items = list(evidence_items)[:selector_max_items]
                selection_decision = EvidenceSelectionDecision(
                    used_llm=False,
                    status="agent_skipped",
                    reason="selector not required for this agent/query",
                    candidate_count=original_candidate_count,
                )
            if not evidence_items and not db_context:
                # Evidence selection tum evidence'lari elemis olabilir —
                # orijinal results'tan en az 1 tanesini geri koy, LLM denesin.
                if preprocessed_results:
                    from src.quality.evidence import EvidenceItem, _stable_source_id, _source_identity, select_evidence_sentences
                    top = preprocessed_results[0]
                    top_content = top.get("content", "")
                    top_source = top.get("source", "bilinmiyor")
                    top_metadata = top.get("metadata") or {}
                    top_score = float(top.get("score", 0.0))
                    source_id = _stable_source_id(
                        _source_identity(top_metadata, top_source),
                        top_content,
                    )
                    evidence_items = [EvidenceItem(
                        content_snippet=top_content[:500],
                        source_name=top_source,
                        source_id=source_id,
                        department=self.department.value,
                        score=top_score,
                        score_type=str(top_metadata.get("score_type", "")),
                        selected_sentences=select_evidence_sentences(query_text, top_content),
                        matched_query_terms=[],
                        relevance_score=top_score,
                        extracted_facts=[],
                    )]
                    logger.info(
                        "evidence_selection_recovered_top agent=%s score=%.3f",
                        self.agent_id, evidence_items[0].score,
                    )
                else:
                    logger.info(
                        "llm_evidence_selection_insufficient agent=%s status=%s",
                        self.agent_id,
                        selection_decision.status,
                    )
                    return (
                        "Bu konuda elimdeki kaynaklarda yeterli bilgi bulunamad\u0131. "
                        "Soruyu daha detayl\u0131 sorabilir veya ilgili birimle ileti\u015fime ge\u00e7ebilirsin.",
                        "kural",
                    )
            context_chunks = build_evidence_context_chunks(
                evidence_items,
                query_text,
                max_items=evidence_max_items,
                max_content_len=_SPECIALIST_LLM_CONTEXT_MAX_LEN,
            )

            # Log evidence diagnostics
            from src.core.profiling import get_current_profiler
            _profiler = get_current_profiler()

            # Intent coverage: çok parçalı sorularda evidence kapsama kontrolü
            from src.quality.intent_coverage import compute_intent_coverage
            _intent_coverage = compute_intent_coverage(
                query_text,
                [ev.content_snippet for ev in evidence_items],
            )
            if _intent_coverage.is_low:
                logger.info(
                    "intent_coverage_low agent=%s sub_intents=%s missing=%s ratio=%.2f",
                    self.agent_id,
                    _intent_coverage.sub_intents,
                    _intent_coverage.missing_intents,
                    _intent_coverage.coverage_ratio,
                )

            if _profiler is not None:
                _profiler.set_attribute(
                    "evidence_summary",
                    build_evidence_diagnostics(evidence_items),
                )
                _profiler.set_attribute(
                    "evidence_selection",
                    selection_decision.to_diagnostics_dict(),
                )
                _profiler.set_attribute(
                    "intent_coverage",
                    {
                        "sub_intents": _intent_coverage.sub_intents,
                        "covered_intents": _intent_coverage.covered_intents,
                        "missing_intents": _intent_coverage.missing_intents,
                        "coverage_ratio": _intent_coverage.coverage_ratio,
                        "is_low": _intent_coverage.is_low,
                    },
                )

            # Store for claim guard and judge (used after LLM synthesis returns)
            self._last_evidence_items = evidence_items
            self._last_intent_coverage = _intent_coverage

        safe_prompt = f"Kullan\u0131c\u0131 sorusu:\n{query_text}\n\n"
        if db_context:
            safe_prompt += f"Veritabani Bilgisi:\n{db_context}\n\n"
        if context_chunks:
            safe_prompt += f"Belge Baglami:\n{chr(10).join(context_chunks)}\n\n"
        prompt_plan_context = {
            key: value
            for key, value in (plan_context or {}).items()
            if key != "decision_contract"
        }
        if prompt_plan_context:
            safe_prompt += (
                "Plan ve cevap sozlesmesi JSON:\n"
                f"{json.dumps(prompt_plan_context, ensure_ascii=False, default=str)[:1800]}\n\n"
            )
        safe_prompt += (
            "Yukaridaki verilerden kullaniciya dogrudan cevap yaz. "
            "Belge basliklarini, kaynak etiketlerini, ic baglam ifadelerini "
            "veya bu talimati cevapta tekrar etme."
        )
        prompt = safe_prompt

        answer_style_rules = """

CEVAP YAZIM KURALLARI:
- Once sorunun dogrudan yanitini ver; sonra gerekiyorsa kisa maddelerle kosul, adim veya istisnayi ekle.
- Selamlama yapma ve kullanicinin ne sordugunu yeniden anlatma. "Merhaba", "bilgi almak istiyorsunuz", "hakkinda bilgi ariyorsunuz" gibi girisler yazma.
- Kullaniciya ikinci sahisla hitap et: "siz", "ders kaydinizi", "basvurunuzu" gibi. Kaynakta gecen "ogrenci/ogrenciler" ifadelerini gerekirse kullaniciya uygun bicime cevir.
- Kendi adina veya kurum adina islem yapmis gibi yazma; "kaydimi yaptirdim", "kaydmizi", "sorumluyuz" gibi ozne kaymalarindan kacin.
- "Soru:", "Yanit:", "Benchmark", "Kaynak Bilgisi", "KAYNAK DOGRULAMA KURALLARI", "KURALLAR", "Belge Baglami", "Kanit" gibi ic basliklari cevapta kullanma.
- Cevabi dogal Turkce yaz (ASCII degil: "ogrenci" degil "\u00f6\u011frenci", "ucret" degil "\u00fccret", "basvuru" degil "ba\u015fvuru"); "certain", "about", "regarding", "information" gibi Ingilizce dolgu veya yer tutucu kelimeler kullanma.
- Kaynakta gecen sayi, tarih, yuzde, sure veya kosul esigi sorunun cevabi icin gerekliyse koru; kaynakta olmayan sayi, tarih, portal, menu, odeme kanali veya form adi uretme.
- Prosedur sorularinda kaynakta varsa su alanlari ozellikle koru: sure/deadline, basvuru belgesi veya form, yetkili kurul/komisyon/birim, platform/sistem adi, devam/devamsizlik kosulu, sayisal esik ve istisna.
- Resmi kisaltma veya ad kaynakta geciyorsa sadelestirip kaybetme; gerekirse birlikte yaz: "UBYS/ogrenci bilgi sistemi" gibi.
- Olumsuz ve istisna bildiren ifadeleri tersine cevirme: "sayilmaz", "dikkate alinmaz", "gerekmez", "zorunlu degildir", "giremez" gibi hukumleri ayni anlamda koru.
- Kaynak soruyla kismen ilgiliyse yalnizca dogrudan ilgili bilgiyi ver; ilgisiz metni ve kaynak yorumunu cevaba tasima.
- Cevap verdikten sonra ayrica "bilgi bulunamadi" gibi celisen bir not ekleme.
- Cevabi yarim cumleyle bitirme; kaynakta ayrintili esik/tutar yoksa o parcayi acmadan tamamlanmis cumleyle dur.
- OLUMSUZ KURAL ONCELIGI: Kaynakta "giremez", "alamaz", "yapilamaz", "kabul edilmez", "almamis olan ogrenciler giremez" gibi kisitlayici/yasaklayici bir ifade varsa ve kullanicinin sorusu "yapabilir miyim?", "girebilir miyim?" seklindeyse, cevabi dogrudan "Hayir" ile baslat ve kaynaktaki kisitlamayi aynen aktar. Kullanicinin beklentisine uyum saglamak icin olumsuz kurali olumluya cevirme. Kaynakta "giremez" diyorsa cevap "giremezsiniz" olmalidir.
- COK PARCALI SORU: Kullanici birden fazla seyi soruyorsa (ornegin "ne zaman + kimler + nasil + ucret + gerekli belge + sartlar") cevabi alt basiklara bol. Her alt parca icin kaynakta bilgi varsa ver; kaynak sadece bir alt parcayi destekliyorsa diger parcalar icin "Bu konuda kaynaklarda net bilgi bulunamadi" de. Tarih sorulmus ama kaynakta tarih yoksa tarih UYDURMA; "akademik takvim/duyuru ile ilan edilir" gibi temkinli ifadelendirme kullan.
"""
        system = (self.definition.system_prompt or GENERAL_QA_SYSTEM_PROMPT) + answer_style_rules
        synthesis_timeout = self._llm_synthesis_timeout_seconds(
            query_text,
            results,
            llm_profile=llm_profile,
        )
        selected_model = settings.resolve_llm_model(
            role="specialist_synthesis",
            profile=llm_profile,
        )
        logger.info(
            "specialist_llm_synthesis_start agent=%s timeout_s=%s prompt_chars=%s sources=%s model=%s profile=%s",
            self.agent_id,
            synthesis_timeout,
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
                    timeout=synthesis_timeout,
                )

            # Post-generation quality check: foreign/broken token detection
            from src.quality.answer_filter import check_answer_quality, REWRITE_ONLY_SYSTEM_SUFFIX
            quality = check_answer_quality(answer)
            if quality.needs_rewrite:
                logger.info(
                    "answer_quality_rewrite agent=%s issues=%s bad_tokens=%s",
                    self.agent_id,
                    quality.detected_issues,
                    quality.bad_tokens[:3],
                )
                try:
                    rewrite_system = system + REWRITE_ONLY_SYSTEM_SUFFIX
                    rewrite_prompt = (
                        f"Önceki cevapta yabancı kelime ve bozuk tokenlar vardı. "
                        f"Aynı anlamı koruyarak doğal Türkçe ile yeniden yaz:\n\n{answer}"
                    )
                    rewritten = await asyncio.wait_for(
                        self.llm_service.generate(
                            prompt=rewrite_prompt,
                            system=rewrite_system,
                            model_role="specialist_synthesis",
                            llm_profile=llm_profile,
                        ),
                        timeout=synthesis_timeout,
                    )
                    if rewritten and len(rewritten.strip()) > len(answer.strip()) * 0.4:
                        answer = rewritten
                        logger.info("answer_quality_rewrite_success agent=%s", self.agent_id)
                except (asyncio.TimeoutError, Exception) as retry_exc:
                    logger.warning(
                        "answer_quality_rewrite_failed agent=%s reason=%s",
                        self.agent_id, type(retry_exc).__name__,
                    )

            # Riskli cevaplarda LLM-as-a-Judge kalite kapisi. En fazla bir
            # rewrite/retrieve-again onarimi yapilir; tekrar judge calistirilmaz.
            answer, judge_meta = await self._apply_judge_quality_gate(
                query_text=query_text,
                answer=answer,
                system=system,
                context_chunks=context_chunks,
                evidence_items=evidence_items,
                intent_coverage=_intent_coverage,
                llm_profile=llm_profile,
                synthesis_timeout=synthesis_timeout,
                plan_context=plan_context,
            )
            if judge_meta.get("judge_enabled"):
                logger.info(
                    "answer_judge_applied agent=%s action=%s retry_count=%s approved=%s",
                    self.agent_id,
                    judge_meta.get("judge_action"),
                    judge_meta.get("retry_count"),
                    judge_meta.get("approved"),
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

    @classmethod
    def _extract_evidence_content(cls, query_text: str, content: str) -> str:
        """LLM baglamina soruyla en ilgili kanit cumlelerini tasir.

        Thin wrapper around ``select_evidence_sentences`` from
        ``src.quality.evidence``.  Kept for backward compatibility.
        """
        return select_evidence_sentences(
            query_text,
            content,
            max_sentences=_SPECIALIST_EVIDENCE_MAX_SENTENCES,
            min_score=_SPECIALIST_EVIDENCE_MIN_SCORE,
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
                + "Bu konuda ilgili kaynaklara ula\u015fmaya \u00e7al\u0131\u015ft\u0131m ancak \u015fu anda k\u0131sa bir \u00f6zet \u00fcretemedim. "
                "Soruyu daha spesifik sorman veya ilgili birimle ileti\u015fime ge\u00e7men faydal\u0131 olur."
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

    @staticmethod
    def _compute_keyword_overlap(query: str, content: str) -> float:
        """Sorgu ile icerik arasindaki keyword overlap oranini hesaplar (0.0-1.0)."""
        _stop = frozenset({
            "bir", "bu", "su", "o", "ve", "ile", "icin", "ne", "mi", "mu",
            "da", "de", "nasil", "nedir", "var", "yok", "hangi", "kac",
        })
        q_tokens = set(normalize_text(query).split()) - _stop
        c_tokens = set(normalize_text(content[:500]).split()) - _stop
        if not q_tokens:
            return 0.0
        return len(q_tokens & c_tokens) / len(q_tokens)
