"""Main query orchestrator."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import replace
from time import perf_counter
from uuid import uuid4

from src.a2a.tracing import ensure_trace_metadata
from src.agents.announcement import AnnouncementAgent
from src.agents.event import EventAgent
from src.db.announcements import _detect_faculty_scope, _detect_unit_scope
from src.cache import (
    build_question_cache_key,
    evaluate_question_cache_lookup,
    evaluate_question_cache_storage,
    question_cache,
)
from src.core.config import settings
from src.core.messages import CONTACT_SUGGESTION
from src.core.profiling import get_current_profiler, profile_stage
from src.core.constants import TaskType
from src.core.text_normalization import normalize_text
from src.db.conversation_context import ConversationContextService, ConversationResolution
from src.db.schemas import DepartmentResponse, UserQueryResponse
from src.db.telemetry import (
    TelemetryService,
    build_department_orchestrator_identity,
    build_main_orchestrator_identity,
)
from src.llm.llm_service import LLMService, LLMServiceError
from src.llm.prompt_templates import MULTI_DEPARTMENT_SYNTHESIS_SYSTEM_PROMPT
from src.orchestrators.announcement_utils import (
    build_announcement_response,
    request_announcement_response,
)
from src.orchestrators.defaults import build_default_orchestrators, build_remote_department_targets
from src.orchestrators.department_dispatch import dispatch_to_departments
from src.orchestrators.event_utils import build_event_response, request_event_response
from src.orchestrators.query_policy import (
    ACADEMIC_DEPARTMENT_CLARIFICATION_MESSAGE,
    CLARIFICATION_MESSAGE,
    build_missing_slot_clarification_message,
    looks_like_announcement_query,
    looks_like_event_query,
    requires_academic_department_clarification,
    should_allow_announcement_latest_fallback,
    should_block_announcement_primary_flow,
    should_fetch_related_announcements,
    should_keep_announcement_follow_up,
    should_use_global_synthesis,
)
from src.orchestrators.query_normalization import (
    QueryNormalizationResult,
    rewrite_is_safe,
    unchanged_query,
)
from src.orchestrators.response_utils import compose_department_answers
from src.orchestrators.response_utils import filter_low_confidence_responses
from src.orchestrators.synthesis_utils import (
    build_global_synthesis_prompt,
    responses_need_contact_suggestion,
)
from src.orchestrators.user_response_builders import (
    build_clarification_user_response,
    build_final_user_response,
    build_memory_answer,
)
from src.routing import DepartmentRouter
from src.routing.routing_policy import looks_like_personal_data_query

_GLOBAL_SYNTHESIS_TIMEOUT_SECONDS = settings.llm.global_synthesis_timeout_seconds

logger = logging.getLogger(__name__)

_ACK_ONLY_RESPONSES = {
    "tesekkur": "Rica ederim. Baska bir sorunuz olursa yazabilirsiniz.",
    "sagol": "Rica ederim. Baska bir sorunuz olursa yazabilirsiniz.",
    "evet": "Hazirim. Devam etmemi istediginiz konuyu biraz daha acik yazabilirsiniz.",
    "tamam": "Hazirim. Devam etmemi istediginiz konuyu biraz daha acik yazabilirsiniz.",
    "anladim": "Hazirim. Devam etmemi istediginiz konuyu biraz daha acik yazabilirsiniz.",
    "smalltalk": "Iyiyim, tesekkur ederim. Size ogrenci isleri, akademik programlar, finans, duyuru veya etkinlik konularinda yardimci olabilirim.",
    "hayir": "Tamam. Farkli bir konuda yardim isterseniz yazabilirsiniz.",
}


class MainOrchestrator:
    """Routes a user query through department orchestrators and synthesis."""

    def __init__(
        self,
        *,
        router: DepartmentRouter | None = None,
        department_orchestrators: dict | None = None,
        announcement_agent: AnnouncementAgent | None = None,
        event_agent: EventAgent | None = None,
        telemetry_service: TelemetryService | None = None,
        llm_service: LLMService | None = None,
        conversation_service: ConversationContextService | None = None,
    ) -> None:
        self.router = router or DepartmentRouter()
        self.telemetry_service = telemetry_service or TelemetryService()
        if department_orchestrators is not None:
            self.department_orchestrators = department_orchestrators
        elif settings.a2a.mode == "http":
            self.department_orchestrators = build_remote_department_targets()
        else:
            self.department_orchestrators = build_default_orchestrators(
                self.telemetry_service
            )
        self.announcement_agent = announcement_agent or AnnouncementAgent()
        self.event_agent = event_agent or EventAgent()
        self.llm_service = llm_service or LLMService()
        self.conversation_service = conversation_service

    @staticmethod
    def _resolve_acknowledgement_message(query: str) -> str | None:
        normalized = normalize_text(query).strip(" \t\r\n.,!?;:")
        if not normalized:
            return None
        if normalized in {"tesekkurler", "tesekkur ederim", "tesekkur ederiz"}:
            return _ACK_ONLY_RESPONSES["tesekkur"]
        if normalized in {"sagol", "sag olun", "sagolun"}:
            return _ACK_ONLY_RESPONSES["sagol"]
        if normalized in {"evet", "tamam", "tamamdir", "ok", "anladim"}:
            return _ACK_ONLY_RESPONSES["tamam" if normalized != "evet" else "evet"]
        if normalized in {"naber", "nasilsin", "ne haber"}:
            return _ACK_ONLY_RESPONSES["smalltalk"]
        if normalized == "hayir":
            return _ACK_ONLY_RESPONSES["hayir"]
        return None

    async def handle_query(
        self,
        query: str,
        *,
        context_id: str | None = None,
        user_id: str | None = None,
        student_id: int | None = None,
        student_number: str | None = None,
        student_full_name: str | None = None,
        student_department: str | None = None,
        student_faculty: str | None = None,
        student_type: str | None = None,
        llm_profile: str | None = None,
        is_authenticated: bool = False,
        trace_id: str | None = None,
        span_id: str | None = None,
        parent_span_id: str | None = None,
        disable_cache: bool = False,
    ) -> UserQueryResponse:
        start_time = perf_counter()
        context_id = context_id or str(uuid4())
        trace = ensure_trace_metadata(
            {
                "trace_id": trace_id,
                "span_id": span_id,
                "parent_span_id": parent_span_id,
            }
        )
        profiler = get_current_profiler()
        conversation_resolution = ConversationResolution(
            original_query=query,
            effective_query=query,
            is_follow_up=False,
            used_context=False,
            active_topic=None,
            department_hints=[],
            source_hints=[],
        )
        if profiler is not None:
            profiler.set_attribute("context_id", context_id)
            profiler.set_attribute("query", query)
            profiler.set_attribute("a2a_trace", trace)

        query_log_id = None
        try:
            with profile_stage("main.handle_query", context_id=context_id):
                acknowledgement_message = self._resolve_acknowledgement_message(query)
                if acknowledgement_message is not None:
                    response_time_ms = round((perf_counter() - start_time) * 1000, 2)
                    return build_clarification_user_response(
                        context_id=context_id,
                        message=acknowledgement_message,
                        response_time_ms=response_time_ms,
                        full_name=student_full_name,
                    )

                if looks_like_event_query(query):
                    if profiler is not None:
                        profiler.set_attribute(
                            "question_cache",
                            {
                                "eligible": False,
                                "status": "bypass",
                                "reason": "event_query",
                            },
                        )
                    return await self._handle_event_short_circuit(
                        query=query,
                        original_query=query,
                        context_id=context_id,
                        start_time=start_time,
                        user_id=user_id,
                        student_id=student_id,
                        student_department=student_department,
                        student_faculty=student_faculty,
                        conversation_resolution=conversation_resolution,
                        trace_metadata=trace,
                    )

                skip_conversation_resolution = looks_like_personal_data_query(query)
                if self.conversation_service is not None and not skip_conversation_resolution:
                    with profile_stage("main.conversation.resolve"):
                        conversation_resolution = await self.conversation_service.resolve_query(
                            context_id=context_id,
                            query=query,
                            llm_service=self.llm_service,
                            llm_profile=llm_profile,
                            student_department=student_department,
                            student_faculty=student_faculty,
                            student_type=student_type,
                        )
                    if profiler is not None:
                        profiler.set_attribute(
                            "conversation_resolution",
                            {
                                "effective_query": conversation_resolution.effective_query,
                                "is_follow_up": conversation_resolution.is_follow_up,
                                "used_context": conversation_resolution.used_context,
                                "active_topic": conversation_resolution.active_topic,
                                "department_hints": [
                                    department.value
                                    for department in conversation_resolution.department_hints
                                ],
                                "rewrite_method": conversation_resolution.rewrite_method,
                                "standalone_query": conversation_resolution.standalone_query,
                            },
                        )
                    if conversation_resolution.clarification_message:
                        return self._build_clarification_response(
                            context_id=context_id,
                            start_time=start_time,
                            query_log_id=query_log_id,
                            routing_reasoning="Konusma baglami netlestirme istedi.",
                            message=conversation_resolution.clarification_message,
                            full_name=student_full_name,
                        )

                effective_query = conversation_resolution.effective_query
                query_normalization = unchanged_query(effective_query)

                if looks_like_announcement_query(effective_query):
                    return await self._handle_announcement_short_circuit(
                        query=effective_query,
                        original_query=query,
                        context_id=context_id,
                        start_time=start_time,
                        user_id=user_id,
                        student_id=student_id,
                        student_department=student_department,
                        student_faculty=student_faculty,
                        conversation_resolution=conversation_resolution,
                        trace_metadata=trace,
                        routing_reasoning=(
                            "Duyuru short-circuit: sorgu duyuru odakli, "
                            "router beklenmeden duyuru akisina yonlendirildi."
                        ),
                    )

                pre_route_cache_lookup = evaluate_question_cache_lookup(
                    query=effective_query,
                    conversation_resolution=conversation_resolution,
                    is_authenticated=is_authenticated,
                    disable_cache=disable_cache,
                )
                if pre_route_cache_lookup.allowed:
                    pre_route_cache_key = build_question_cache_key(
                        query=effective_query,
                        llm_profile=llm_profile,
                        student_department=student_department,
                        student_faculty=student_faculty,
                        student_type=student_type,
                        is_authenticated=is_authenticated,
                    )
                    with profile_stage("main.question_cache.pre_route_get"):
                        cached_response = question_cache.get(pre_route_cache_key)
                    if cached_response is not None:
                        if profiler is not None:
                            profiler.set_attribute(
                                "question_cache",
                                {
                                    "eligible": True,
                                    "status": "hit",
                                    "reason": pre_route_cache_lookup.reason,
                                    "stage": "pre_route",
                                },
                            )
                        with profile_stage("main.telemetry.create_query_log"):
                            query_log_id = await self.telemetry_service.create_query_log(
                                query_text=query,
                                routing=None,
                                orchestrator=build_main_orchestrator_identity(),
                                context_id=context_id,
                                user_id=user_id,
                                student_id=student_id,
                                metadata_extra={
                                    **trace,
                                    "cache": {
                                        "question_cache": "hit",
                                    }
                                },
                            )
                        final_response = self._build_cached_user_query_response(
                            cached_response=cached_response,
                            context_id=context_id,
                            start_time=start_time,
                        )
                        with profile_stage("main.telemetry.finalize_success"):
                            await self.telemetry_service.finalize_query_log(
                                query_log_id=query_log_id,
                                response_text=build_memory_answer(answer=final_response.answer),
                                response_time_ms=final_response.response_time_ms,
                                status="completed",
                                departments=final_response.departments_involved,
                            )
                        if self.conversation_service is not None:
                            with profile_stage("main.conversation.record_cache_hit"):
                                await self._record_conversation_turn(
                                    context_id=context_id,
                                    original_query=query,
                                    resolved_query=effective_query,
                                    memory_answer=build_memory_answer(
                                        answer=final_response.answer
                                    ),
                                    final_response=final_response,
                                    routing_task_type=None,
                                    conversation_resolution=conversation_resolution,
                                )
                        return final_response

                # ── Routing (normalization dahil) ──
                # Routing LLM hem departman bilgilendirmesi hem canonical_query,
                # primary_intent ve target_capability uretir — ayri normalization cagrisina gerek yok.
                with profile_stage("main.router.route"):
                    routing = await self.router.route(
                        effective_query,
                        llm_profile=llm_profile,
                        preferred_departments=conversation_resolution.department_hints,
                        preferred_task_type=conversation_resolution.task_type_hint,
                    )
                if routing.task_type is None and conversation_resolution.task_type_hint is not None:
                    routing = routing.model_copy(
                        update={"task_type": conversation_resolution.task_type_hint}
                    )

                # Routing sonucundan normalization bilgisi turet
                if routing.intent is not None:
                    canonical_from_routing = routing.intent.canonical_query or effective_query
                    is_rewritten = (
                        canonical_from_routing != effective_query
                        and normalize_text(canonical_from_routing) != normalize_text(effective_query)
                        and rewrite_is_safe(effective_query, canonical_from_routing)
                    )
                    if is_rewritten:
                        effective_query = canonical_from_routing
                        conversation_resolution = replace(
                            conversation_resolution,
                            effective_query=effective_query,
                            used_context=True,
                        )
                    query_normalization = QueryNormalizationResult(
                        original_query=conversation_resolution.effective_query,
                        canonical_query=effective_query,
                        is_rewritten=is_rewritten,
                        is_personal=routing.intent.is_personal,
                        primary_intent=routing.intent.primary_intent or "unknown",
                        target_capability=routing.intent.target_capability or "none",
                        confidence=routing.confidence,
                        reasoning=None,
                    )

                if profiler is not None:
                    profiler.set_attribute(
                        "query_normalization",
                        {
                            "enabled": True,
                            "pre_normalization_used": False,
                            "merged_with_routing": True,
                            "canonical_query": query_normalization.canonical_query,
                            "is_rewritten": query_normalization.is_rewritten,
                            "primary_intent": query_normalization.primary_intent,
                            "target_capability": query_normalization.target_capability,
                            "confidence": query_normalization.confidence,
                        },
                    )
                question_cache_key = None
                cache_lookup_decision = evaluate_question_cache_lookup(
                    query=effective_query,
                    conversation_resolution=conversation_resolution,
                    is_authenticated=is_authenticated,
                    disable_cache=disable_cache,
                )
                if cache_lookup_decision.allowed:
                    question_cache_key = build_question_cache_key(
                        query=effective_query,
                        llm_profile=llm_profile,
                        student_department=student_department,
                        student_faculty=student_faculty,
                        student_type=student_type,
                        is_authenticated=is_authenticated,
                    )
                    with profile_stage("main.question_cache.get"):
                        cached_response = question_cache.get(question_cache_key)
                    if cached_response is not None:
                        if profiler is not None:
                            profiler.set_attribute(
                                "question_cache",
                                {
                                    "eligible": True,
                                    "status": "hit",
                                    "reason": cache_lookup_decision.reason,
                                },
                            )
                        with profile_stage("main.telemetry.create_query_log"):
                            query_log_id = await self.telemetry_service.create_query_log(
                                query_text=query,
                                routing=None,
                                orchestrator=build_main_orchestrator_identity(),
                                context_id=context_id,
                                user_id=user_id,
                                student_id=student_id,
                                metadata_extra={
                                    **trace,
                                    "cache": {
                                        "question_cache": "hit",
                                    }
                                },
                            )
                        final_response = self._build_cached_user_query_response(
                            cached_response=cached_response,
                            context_id=context_id,
                            start_time=start_time,
                        )
                        with profile_stage("main.telemetry.finalize_success"):
                            await self.telemetry_service.finalize_query_log(
                                query_log_id=query_log_id,
                                response_text=build_memory_answer(answer=final_response.answer),
                                response_time_ms=final_response.response_time_ms,
                                status="completed",
                                departments=final_response.departments_involved,
                            )
                        if self.conversation_service is not None:
                            with profile_stage("main.conversation.record_cache_hit"):
                                await self._record_conversation_turn(
                                    context_id=context_id,
                                    original_query=query,
                                    resolved_query=effective_query,
                                    memory_answer=build_memory_answer(
                                        answer=final_response.answer
                                    ),
                                    final_response=final_response,
                                    routing_task_type=None,
                                    conversation_resolution=conversation_resolution,
                                )
                        return final_response
                    if profiler is not None:
                        profiler.set_attribute(
                            "question_cache",
                            {
                                "eligible": True,
                                "status": "miss",
                                "reason": cache_lookup_decision.reason,
                            },
                        )
                elif profiler is not None:
                    profiler.set_attribute(
                        "question_cache",
                        {
                            "eligible": False,
                            "status": "bypass",
                            "reason": cache_lookup_decision.reason,
                        },
                    )

                # ── Duyuru short-circuit ──
                # Duyuru sorgulari router'a gitmeden dogrudan announcement-only akisa yonlendirilir.
                # Ayrica onceki tur duyuru akisindan geldiginde (announcement_context=True)
                # follow-up sorular da duyuru akisinda kalir.
                if (
                    query_normalization.target_capability == "event"
                    or looks_like_event_query(effective_query)
                ):
                    return await self._handle_event_short_circuit(
                        query=effective_query,
                        original_query=query,
                        context_id=context_id,
                        start_time=start_time,
                        user_id=user_id,
                        student_id=student_id,
                        student_department=student_department,
                        student_faculty=student_faculty,
                        conversation_resolution=conversation_resolution,
                        trace_metadata=trace,
                    )

                is_announcement_query = (
                    (
                        query_normalization.target_capability == "announcement"
                        and not should_block_announcement_primary_flow(effective_query)
                    )
                    or looks_like_announcement_query(effective_query)
                )
                is_announcement_follow_up = (
                    conversation_resolution.is_follow_up
                    and conversation_resolution.announcement_context
                    and should_keep_announcement_follow_up(effective_query)
                )
                if is_announcement_query or is_announcement_follow_up:
                    announcement_scope = self._resolve_announcement_scope(
                        query=effective_query,
                        conversation_resolution=conversation_resolution,
                        student_department=student_department,
                        student_faculty=student_faculty,
                    )
                    with profile_stage("main.announcement_short_circuit"):
                        with profile_stage("main.telemetry.create_query_log"):
                            query_log_id = await self.telemetry_service.create_query_log(
                                query_text=query,
                                routing=None,
                                orchestrator=build_main_orchestrator_identity(),
                                context_id=context_id,
                                user_id=user_id,
                                student_id=student_id,
                                metadata_extra=trace,
                            )
                        announcement_user_response = await build_announcement_response(
                            announcement_agent=self.announcement_agent,
                            telemetry_service=self.telemetry_service,
                            query=effective_query,
                            context_id=context_id,
                            start_time=start_time,
                            query_log_id=query_log_id,
                            routing_reasoning="Duyuru short-circuit: sorgu duyuru odakli, dogrudan duyuru akisina yonlendirildi.",
                            task_type=None,
                            faculty=announcement_scope["faculty"],
                            unit_name=announcement_scope["unit_name"],
                            allow_latest_fallback=should_allow_announcement_latest_fallback(
                                effective_query
                            ),
                            trace_metadata=trace,
                        )
                    if self.conversation_service is not None:
                        with profile_stage("main.conversation.record_announcement"):
                            await self._record_conversation_turn(
                                context_id=context_id,
                                original_query=query,
                                resolved_query=effective_query,
                                memory_answer=build_memory_answer(
                                    answer=announcement_user_response.answer
                                ),
                                final_response=announcement_user_response,
                                routing_task_type=None,
                                conversation_resolution=conversation_resolution,
                            )
                    return announcement_user_response

                # Routing zaten yukarida yapildi; sadece profil bilgisi ekle
                if profiler is not None:
                    routing_attrs: dict = {
                        "departments": [
                            department.value for department in routing.departments
                        ],
                        "strategy": routing.strategy.value,
                        "task_type": (
                            routing.task_type.value if routing.task_type else None
                        ),
                        "confidence": routing.confidence,
                    }
                    if routing.intent is not None:
                        routing_attrs["intent"] = {
                            "complexity": routing.intent.complexity,
                            "is_personal": routing.intent.is_personal,
                            "force_llm_synthesis": routing.intent.force_llm_synthesis,
                            "query_type": routing.intent.query_type,
                            "canonical_query": routing.intent.canonical_query,
                            "primary_intent": routing.intent.primary_intent,
                            "target_capability": routing.intent.target_capability,
                            "required_slots": routing.intent.required_slots,
                            "missing_slots": routing.intent.missing_slots,
                        }
                    profiler.set_attribute("routing", routing_attrs)
                if routing.intent is not None and routing.intent.target_capability == "event":
                    return await self._handle_event_short_circuit(
                        query=effective_query,
                        original_query=query,
                        context_id=context_id,
                        start_time=start_time,
                        user_id=user_id,
                        student_id=student_id,
                        student_department=student_department,
                        student_faculty=student_faculty,
                        conversation_resolution=conversation_resolution,
                        trace_metadata=trace,
                    )
                with profile_stage("main.telemetry.create_query_log"):
                    query_log_id = await self.telemetry_service.create_query_log(
                        query_text=query,
                        routing=routing,
                        orchestrator=build_main_orchestrator_identity(),
                        context_id=context_id,
                        user_id=user_id,
                        student_id=student_id,
                        metadata_extra={
                            **trace,
                            "cache": {
                                "question_cache": (
                                    "miss" if question_cache_key is not None else "bypass"
                                ),
                            }
                        },
                    )
                if (
                    routing.intent is not None
                    and routing.intent.target_capability == "announcement"
                    and not should_block_announcement_primary_flow(effective_query)
                ):
                    announcement_scope = self._resolve_announcement_scope(
                        query=effective_query,
                        conversation_resolution=conversation_resolution,
                        student_department=student_department,
                        student_faculty=student_faculty,
                    )
                    with profile_stage("main.announcement_short_circuit"):
                        announcement_user_response = await build_announcement_response(
                            announcement_agent=self.announcement_agent,
                            telemetry_service=self.telemetry_service,
                            query=effective_query,
                            context_id=context_id,
                            start_time=start_time,
                            query_log_id=query_log_id,
                            routing_reasoning=(
                                routing.reasoning
                                or "Routing LLM capability olarak duyuru akisini secti."
                            ),
                            task_type=routing.task_type,
                            faculty=announcement_scope["faculty"],
                            unit_name=announcement_scope["unit_name"],
                            trace_metadata=trace,
                        )
                    if self.conversation_service is not None:
                        with profile_stage("main.conversation.record_announcement"):
                            await self._record_conversation_turn(
                                context_id=context_id,
                                original_query=query,
                                resolved_query=effective_query,
                                memory_answer=build_memory_answer(
                                    answer=announcement_user_response.answer
                                ),
                                final_response=announcement_user_response,
                                routing_task_type=routing.task_type,
                                conversation_resolution=conversation_resolution,
                    )
                    return announcement_user_response

                metadata_for_slot_check = {
                    "is_authenticated": is_authenticated,
                    "student_type": student_type,
                    "student_faculty": student_faculty,
                    "student_department": student_department,
                }
                missing_slot_message = build_missing_slot_clarification_message(
                    intent=routing.intent,
                    metadata=metadata_for_slot_check,
                )
                if missing_slot_message:
                    clarification_response = self._build_clarification_response(
                        context_id=context_id,
                        start_time=start_time,
                        query_log_id=query_log_id,
                        routing_reasoning=(
                            "Routing LLM eksik slot netlestirmesi istedi."
                        ),
                        message=missing_slot_message,
                        full_name=student_full_name,
                    )
                    clarification_response = clarification_response.model_copy(
                        update={
                            "departments_involved": [
                                department.value for department in routing.departments
                            ],
                            "generation_modes": ["kural"],
                        },
                        deep=True,
                    )
                    if self.conversation_service is not None:
                        with profile_stage("main.conversation.record_slot_clarification"):
                            await self._record_conversation_turn(
                                context_id=context_id,
                                original_query=query,
                                resolved_query=effective_query,
                                memory_answer=build_memory_answer(
                                    answer=missing_slot_message
                                ),
                                final_response=clarification_response,
                                routing_task_type=routing.task_type,
                                conversation_resolution=conversation_resolution,
                            )
                    return clarification_response

                if routing.strategy.name == "CLARIFICATION" and not routing.departments:
                    return self._build_clarification_response(
                        context_id=context_id,
                        start_time=start_time,
                        query_log_id=query_log_id,
                        routing_reasoning=routing.reasoning,
                        full_name=student_full_name,
                    )

                if requires_academic_department_clarification(
                    query=effective_query,
                    departments=routing.departments,
                    task_type=routing.task_type,
                    student_department=student_department,
                ):
                    return self._build_clarification_response(
                        context_id=context_id,
                        start_time=start_time,
                        query_log_id=query_log_id,
                        routing_reasoning=(
                            "Akademik program sorusu icin bolum/program bilgisi gerekli."
                        ),
                        message=ACADEMIC_DEPARTMENT_CLARIFICATION_MESSAGE,
                        full_name=student_full_name,
                    )

                intent = routing.intent
                metadata = {
                    "original_query": query,
                    "resolved_query": effective_query,
                    "routing_reason": routing.reasoning,
                    "user_id": user_id,
                    "student_id": student_id,
                    "student_number": student_number,
                    "student_full_name": student_full_name,
                    "student_department": student_department,
                    "student_faculty": student_faculty,
                    "student_type": student_type,
                    "llm_profile": llm_profile,
                    "is_authenticated": is_authenticated,
                    "query_log_id": query_log_id,
                    "conversation_is_follow_up": conversation_resolution.is_follow_up,
                    "conversation_topic": conversation_resolution.active_topic,
                    "conversation_source_refs": conversation_resolution.source_hints,
                    "force_llm_synthesis": intent.force_llm_synthesis if intent else False,
                    "query_complexity": intent.complexity if intent else None,
                    "is_personal_query": intent.is_personal if intent else False,
                    **trace,
                }

                with profile_stage("main.dispatch_departments"):
                    department_responses = await dispatch_to_departments(
                        department_orchestrators=self.department_orchestrators,
                        query=effective_query,
                        context_id=context_id,
                        routing=routing,
                        metadata=metadata,
                    )
                await self._record_department_transport_failures(
                    responses=department_responses,
                    context_id=context_id,
                    query=effective_query,
                    query_log_id=query_log_id,
                    task_type=routing.task_type,
                    trace_metadata=trace,
                )

                if department_responses and all(
                    response.error == "department_context_required"
                    for response in department_responses
                ):
                    return self._build_clarification_response(
                        context_id=context_id,
                        start_time=start_time,
                        query_log_id=query_log_id,
                        routing_reasoning=(
                            "Uzman ajan bolum/program netlestirmesi istedi."
                        ),
                        message=department_responses[0].answer,
                        full_name=student_full_name,
                    )

                responses: list[DepartmentResponse] = list(department_responses)

                if not responses:
                    announcement_scope = self._resolve_announcement_scope(
                        query=effective_query,
                        conversation_resolution=conversation_resolution,
                        student_department=student_department,
                        student_faculty=student_faculty,
                    )
                    with profile_stage("main.fallback_announcement"):
                        fallback = await request_announcement_response(
                            announcement_agent=self.announcement_agent,
                            telemetry_service=self.telemetry_service,
                            query=effective_query,
                            context_id=context_id,
                            routing_reason=routing.reasoning,
                            query_log_id=query_log_id,
                            task_type=routing.task_type,
                            faculty=announcement_scope["faculty"],
                            unit_name=announcement_scope["unit_name"],
                            trace_metadata=trace,
                        )
                        responses.append(fallback)
                else:
                    announcement_response = None
                    if should_fetch_related_announcements(effective_query):
                        announcement_scope = self._resolve_announcement_scope(
                            query=effective_query,
                            conversation_resolution=conversation_resolution,
                            student_department=student_department,
                            student_faculty=student_faculty,
                        )
                        with profile_stage("main.related_announcements"):
                            announcement_response = await request_announcement_response(
                                announcement_agent=self.announcement_agent,
                                telemetry_service=self.telemetry_service,
                                query=effective_query,
                                context_id=context_id,
                                routing_reason=routing.reasoning,
                                query_log_id=query_log_id,
                                task_type=routing.task_type,
                                faculty=announcement_scope["faculty"],
                                unit_name=announcement_scope["unit_name"],
                                allow_latest_fallback=should_allow_announcement_latest_fallback(
                                    effective_query
                                ),
                                trace_metadata=trace,
                            )
                    if announcement_response is not None and announcement_response.sources:
                        responses.append(announcement_response)

                with profile_stage("main.filter_low_confidence"):
                    filtered_responses = filter_low_confidence_responses(responses)
                    filtered_departments = list(department_responses)

                with profile_stage("main.compose_response"):
                    answer, used_global_synthesis = await self._compose_final_answer(
                        query=effective_query,
                        responses=filtered_responses,
                        llm_profile=llm_profile,
                    )
                    memory_answer = build_memory_answer(answer=answer)
                    final_response = self._build_user_query_response(
                        answer=answer,
                        responses=filtered_responses,
                        department_responses=filtered_departments,
                        context_id=context_id,
                        start_time=start_time,
                        student_full_name=student_full_name,
                        used_global_synthesis=used_global_synthesis,
                    )
                with profile_stage("main.telemetry.finalize_success"):
                    await self.telemetry_service.finalize_query_log(
                        query_log_id=query_log_id,
                        response_text=memory_answer,
                        response_time_ms=final_response.response_time_ms,
                        status="completed",
                        departments=final_response.departments_involved,
                    )
                if self.conversation_service is not None:
                    with profile_stage("main.conversation.record"):
                        await self._record_conversation_turn(
                            context_id=context_id,
                            original_query=query,
                            resolved_query=effective_query,
                            memory_answer=memory_answer,
                            final_response=final_response,
                            routing_task_type=routing.task_type,
                            conversation_resolution=conversation_resolution,
                        )
                cache_store_decision = evaluate_question_cache_storage(
                    question_cache_key=question_cache_key,
                    routing=routing,
                    final_response=final_response,
                    used_global_synthesis=used_global_synthesis,
                )
                if cache_store_decision.allowed:
                    with profile_stage("main.question_cache.put"):
                        question_cache.put(question_cache_key, final_response)
                # Stage surelerini diagnostics'e ekle
                profiler = get_current_profiler()
                if profiler is not None and final_response.diagnostics is not None:
                    final_response.diagnostics.local_profile = profiler.snapshot()
                elif profiler is not None:
                    from src.db.schemas import QueryDiagnostics
                    final_response.diagnostics = QueryDiagnostics(local_profile=profiler.snapshot())
                return final_response
        except Exception as exc:
            with profile_stage("main.telemetry.finalize_error"):
                await self.telemetry_service.finalize_query_log(
                    query_log_id=query_log_id,
                    response_text=None,
                    response_time_ms=round((perf_counter() - start_time) * 1000, 2),
                    status="failed",
                    error=str(exc),
                )
            raise

    async def _record_conversation_turn(
        self,
        *,
        context_id: str,
        original_query: str,
        resolved_query: str,
        memory_answer: str,
        final_response: UserQueryResponse,
        routing_task_type,
        conversation_resolution: ConversationResolution,
    ) -> None:
        """Persist follow-up state without affecting user-visible flow."""
        if self.conversation_service is None:
            return
        try:
            await self.conversation_service.record_turn(
                context_id=context_id,
                user_query=original_query,
                resolved_query=resolved_query,
                assistant_answer=memory_answer,
                departments=final_response.departments_involved,
                sources=final_response.sources,
                is_follow_up=conversation_resolution.is_follow_up,
                task_type=routing_task_type,
                active_topic=self._derive_conversation_topic(
                    final_response=final_response,
                    conversation_resolution=conversation_resolution,
                ),
            )
        except Exception as exc:
            logger.warning("conversation_turn_record_skipped reason=%s", type(exc).__name__)

    async def _record_department_transport_failures(
        self,
        *,
        responses: list[DepartmentResponse],
        context_id: str,
        query: str,
        query_log_id: int | None,
        task_type,
        trace_metadata: dict,
    ) -> None:
        """Expose failed remote department branches in A2A diagnostics."""
        if self.telemetry_service is None:
            return

        for response in responses:
            error_code = str(response.error or "")
            if response.success or not error_code.startswith("a2a_"):
                continue

            with profile_stage(
                "main.telemetry.record_department_transport_failure",
                department=response.department.value,
            ):
                await self.telemetry_service.record_agent_task(
                    task_id=f"{context_id}:department:{response.department.value}",
                    query_log_id=query_log_id,
                    sender=build_main_orchestrator_identity(),
                    receiver=build_department_orchestrator_identity(response.department),
                    task_type=task_type,
                    payload={
                        "query_text": query,
                        "context_id": context_id,
                        "trace": dict(trace_metadata or {}),
                    },
                    response=response,
                    error_msg=error_code,
                )

    async def _handle_event_short_circuit(
        self,
        *,
        query: str,
        original_query: str,
        context_id: str,
        start_time: float,
        user_id: str | None,
        student_id: int | None,
        student_department: str | None,
        student_faculty: str | None,
        conversation_resolution: ConversationResolution,
        trace_metadata: dict | None = None,
    ) -> UserQueryResponse:
        """Handle explicit event queries without waiting for generic routing."""
        event_scope = self._resolve_event_scope(
            query=query,
            student_department=student_department,
            student_faculty=student_faculty,
        )
        with profile_stage("main.event_short_circuit"):
            with profile_stage("main.telemetry.create_query_log"):
                query_log_id = await self.telemetry_service.create_query_log(
                    query_text=original_query,
                    routing=None,
                    orchestrator=build_main_orchestrator_identity(),
                    context_id=context_id,
                    user_id=user_id,
                    student_id=student_id,
                    metadata_extra=trace_metadata,
                )
            event_response = await request_event_response(
                event_agent=self.event_agent,
                telemetry_service=self.telemetry_service,
                query=query,
                context_id=context_id,
                routing_reason="Etkinlik short-circuit: sorgu dogrudan etkinlik ajanina yonlendirildi.",
                query_log_id=query_log_id,
                task_type=None,
                faculty=event_scope["faculty"],
                unit_name=event_scope["unit_name"],
                limit=5,
                trace_metadata=trace_metadata,
            )
            event_user_response = await build_event_response(
                response=event_response,
                telemetry_service=self.telemetry_service,
                context_id=context_id,
                start_time=start_time,
                query_log_id=query_log_id,
            )
        if self.conversation_service is not None:
            with profile_stage("main.conversation.record_event"):
                await self._record_conversation_turn(
                    context_id=context_id,
                    original_query=original_query,
                    resolved_query=query,
                    memory_answer=build_memory_answer(answer=event_user_response.answer),
                    final_response=event_user_response,
                    routing_task_type=None,
                    conversation_resolution=conversation_resolution,
                )
        return event_user_response

    async def _handle_announcement_short_circuit(
        self,
        *,
        query: str,
        original_query: str,
        context_id: str,
        start_time: float,
        user_id: str | None,
        student_id: int | None,
        student_department: str | None,
        student_faculty: str | None,
        conversation_resolution: ConversationResolution,
        routing_reasoning: str,
        task_type: TaskType | None = None,
        query_log_id: int | None = None,
        trace_metadata: dict | None = None,
    ) -> UserQueryResponse:
        """Handle explicit announcement queries without generic routing."""
        announcement_scope = self._resolve_announcement_scope(
            query=query,
            conversation_resolution=conversation_resolution,
            student_department=student_department,
            student_faculty=student_faculty,
        )
        with profile_stage("main.announcement_short_circuit"):
            if query_log_id is None:
                with profile_stage("main.telemetry.create_query_log"):
                    query_log_id = await self.telemetry_service.create_query_log(
                        query_text=original_query,
                        routing=None,
                        orchestrator=build_main_orchestrator_identity(),
                        context_id=context_id,
                        user_id=user_id,
                        student_id=student_id,
                        metadata_extra=trace_metadata,
                    )
            announcement_user_response = await build_announcement_response(
                announcement_agent=self.announcement_agent,
                telemetry_service=self.telemetry_service,
                query=query,
                context_id=context_id,
                start_time=start_time,
                query_log_id=query_log_id,
                routing_reasoning=routing_reasoning,
                task_type=task_type,
                faculty=announcement_scope["faculty"],
                unit_name=announcement_scope["unit_name"],
                allow_latest_fallback=should_allow_announcement_latest_fallback(query),
                trace_metadata=trace_metadata,
            )
        if self.conversation_service is not None:
            with profile_stage("main.conversation.record_announcement"):
                await self._record_conversation_turn(
                    context_id=context_id,
                    original_query=original_query,
                    resolved_query=query,
                    memory_answer=build_memory_answer(answer=announcement_user_response.answer),
                    final_response=announcement_user_response,
                    routing_task_type=task_type,
                    conversation_resolution=conversation_resolution,
                )
        return announcement_user_response

    @staticmethod
    def _derive_conversation_topic(
        *,
        final_response: UserQueryResponse,
        conversation_resolution: ConversationResolution,
    ) -> str | None:
        if conversation_resolution.active_topic:
            return conversation_resolution.active_topic
        if "announcement" not in (final_response.departments_involved or []):
            return None
        for source in final_response.sources:
            metadata = source.metadata or {}
            unit_name = str(metadata.get("unit_name") or "").strip()
            if unit_name:
                return unit_name
        for source in final_response.sources:
            metadata = source.metadata or {}
            faculty = str(metadata.get("faculty") or "").strip()
            if faculty:
                return faculty
        return None

    def _build_clarification_response(
        self,
        *,
        context_id: str,
        start_time: float,
        query_log_id: int | None,
        routing_reasoning: str | None,
        message: str = CLARIFICATION_MESSAGE,
        full_name: str | None = None,
    ) -> UserQueryResponse:
        """Build a user-facing clarification response."""
        response_time_ms = round((perf_counter() - start_time) * 1000, 2)
        self._schedule_query_log_finalization(
            query_log_id=query_log_id,
            response_text=message,
            response_time_ms=response_time_ms,
            status="clarification",
        )
        return build_clarification_user_response(
            context_id=context_id,
            message=message,
            response_time_ms=response_time_ms,
            full_name=full_name,
        )

    @staticmethod
    def _resolve_announcement_scope(
        *,
        query: str,
        conversation_resolution: ConversationResolution,
        student_department: str | None,
        student_faculty: str | None,
    ) -> dict[str, str | None]:
        normalized_query = normalize_text(query)
        active_topic = normalize_text(conversation_resolution.active_topic)
        normalized_department = normalize_text(student_department)
        normalized_faculty = normalize_text(student_faculty)

        unit_name = _detect_unit_scope(query)
        faculty = _detect_faculty_scope(query)
        explicit_unit_name = unit_name is not None
        explicit_faculty = faculty is not None

        if student_department and (
            (normalized_department and normalized_department in normalized_query)
            or (normalized_department and normalized_department == active_topic)
        ):
            unit_name = student_department

        if student_faculty and (
            (normalized_faculty and normalized_faculty in normalized_query)
            or (normalized_faculty and normalized_faculty == active_topic)
        ):
            faculty = student_faculty

        scoped_academic_markers = (
            "sinav takvimi",
            "sinav programi",
            "ara sinav",
            "final sinavi",
            "butunleme sinavi",
            "ders programi",
        )
        if any(marker in normalized_query for marker in scoped_academic_markers):
            unit_name = unit_name or student_department
            # Do not combine an explicitly requested unit with the student's
            # profile faculty. That can turn "Fizik ders programi" into a
            # "Muhendislik Fakultesi" announcement search.
            if not explicit_unit_name or explicit_faculty:
                faculty = faculty or student_faculty

        return {
            "faculty": faculty,
            "unit_name": unit_name,
        }

    @staticmethod
    def _resolve_event_scope(
        *,
        query: str,
        student_department: str | None,
        student_faculty: str | None,
    ) -> dict[str, str | None]:
        normalized_query = normalize_text(query)
        normalized_department = normalize_text(student_department)
        normalized_faculty = normalize_text(student_faculty)

        unit_name = None
        if student_department and normalized_department and normalized_department in normalized_query:
            unit_name = student_department

        faculty = None
        if student_faculty and normalized_faculty and normalized_faculty in normalized_query:
            faculty = student_faculty

        return {
            "faculty": faculty,
            "unit_name": unit_name,
        }

    @staticmethod
    def _build_cached_user_query_response(
        *,
        cached_response: UserQueryResponse,
        context_id: str,
        start_time: float,
    ) -> UserQueryResponse:
        return cached_response.model_copy(
            update={
                "query_id": context_id,
                "response_time_ms": round((perf_counter() - start_time) * 1000, 2),
                "diagnostics": None,
            },
            deep=True,
        )

    def _build_user_query_response(
        self,
        *,
        answer: str,
        responses: list[DepartmentResponse],
        department_responses: list[DepartmentResponse],
        context_id: str,
        start_time: float,
        student_full_name: str | None,
        used_global_synthesis: bool = False,
    ) -> UserQueryResponse:
        """Build the final user-facing response payload."""
        response_time_ms = round((perf_counter() - start_time) * 1000, 2)
        return build_final_user_response(
            answer=answer,
            responses=responses,
            department_responses=department_responses,
            context_id=context_id,
            response_time_ms=response_time_ms,
            student_full_name=student_full_name,
            used_global_synthesis=used_global_synthesis,
        )

    def _schedule_query_log_finalization(
        self,
        *,
        query_log_id: int | None,
        response_text: str | None,
        response_time_ms: float | None,
        status: str,
    ) -> None:
        """Queue best-effort telemetry finalization without blocking the loop."""
        if query_log_id is None:
            return
        asyncio.create_task(
            self.telemetry_service.finalize_query_log(
                query_log_id=query_log_id,
                response_text=response_text,
                response_time_ms=response_time_ms,
                status=status,
            )
        )

    @staticmethod
    def _compose_answers(responses: list[DepartmentResponse]) -> str:
        return compose_department_answers(responses)

    async def _compose_final_answer(
        self,
        *,
        query: str,
        responses: list[DepartmentResponse],
        llm_profile: str | None = None,
    ) -> tuple[str, bool]:
        if not should_use_global_synthesis(query=query, responses=responses):
            return self._compose_answers(responses), False

        # Tek departman, specialist LLM zaten basarili cevap verdiyse
        # gereksiz ikinci LLM cagrisindan kacin.
        from src.orchestrators.response_utils import is_no_info_response
        meaningful_responses = [r for r in responses if r.answer.strip()]
        departments = {r.department for r in meaningful_responses}
        if len(departments) < 2:
            # Specialist zaten iyi bir cevap urduyse (no-info degilse) sentez atla
            has_no_info = any(is_no_info_response(r) for r in meaningful_responses)
            has_sources = any(r.sources for r in meaningful_responses)
            if not has_no_info:
                # Specialist LLM basarili — final refinement gereksiz
                return self._compose_answers(responses), False
            if not has_sources:
                # Kaynak yok, sentez de bir sey yapamazdi
                return self._compose_answers(responses), False
            # No-info + kaynak var → final refinement ile LLM'e gonder

        synthesized = await self._synthesize_department_answers(
            query=query,
            responses=responses,
            llm_profile=llm_profile,
        )
        if not synthesized:
            return self._compose_answers(responses), False

        # Claim guard on global synthesis — use filtered_responses' sources
        try:
            from src.quality.claim_guard import guard_answer as _guard_answer
            from src.quality.evidence import extract_evidence_items, EvidenceItem
            from src.rag.query_preprocessor import QueryPreprocessor

            all_evidence: list[EvidenceItem] = []
            analysis_query = QueryPreprocessor().preprocess(query)
            for resp in responses:
                if not resp.sources:
                    continue
                raw_results = [
                    {
                        "content": s.content,
                        "source": s.metadata.get("source", s.metadata.get("filename", "")),
                        "score": s.score,
                        "metadata": s.metadata or {},
                    }
                    for s in resp.sources[:3]
                ]
                all_evidence.extend(
                    extract_evidence_items(
                        query,
                        raw_results,
                        resp.department.value,
                        analysis_query=analysis_query,
                    )
                )
            if all_evidence:
                with profile_stage("main.global_claim_guard"):
                    guard_result = _guard_answer(synthesized, all_evidence)
                    synthesized = guard_result.cleaned_answer
                    from src.core.profiling import get_current_profiler
                    _profiler = get_current_profiler()
                    if _profiler is not None:
                        _profiler.set_attribute("global_claim_guard", {
                            "unsupported_claims": guard_result.unsupported_claims,
                            "modifications_made": guard_result.modifications_made,
                        })
        except Exception:
            logger.debug("global_claim_guard_skipped", exc_info=True)

        if responses_need_contact_suggestion(responses):
            synthesized += CONTACT_SUGGESTION
        return synthesized, True

    async def _synthesize_department_answers(
        self,
        *,
        query: str,
        responses: list[DepartmentResponse],
        llm_profile: str | None = None,
    ) -> str | None:
        prompt, meaningful = build_global_synthesis_prompt(query, responses)
        if not prompt:
            return None

        synthesis_role = (
            "global_synthesis"
            if len({response.department for response in meaningful}) >= 2
            else "final_refinement"
        )
        selected_model = settings.resolve_llm_model(
            role=synthesis_role,
            profile=llm_profile,
        )
        logger.info(
            "final_llm_synthesis_start timeout_s=%s prompt_chars=%s departments=%s model=%s profile=%s role=%s",
            _GLOBAL_SYNTHESIS_TIMEOUT_SECONDS,
            len(prompt) + len(MULTI_DEPARTMENT_SYNTHESIS_SYSTEM_PROMPT),
            [response.department.value for response in meaningful],
            selected_model,
            llm_profile or settings.normalize_llm_profile(settings.llm.profile),
            synthesis_role,
        )
        try:
            with profile_stage("main.final_llm_synthesis"):
                return await asyncio.wait_for(
                    self.llm_service.generate(
                        prompt=prompt,
                        system=MULTI_DEPARTMENT_SYNTHESIS_SYSTEM_PROMPT,
                        model_role=synthesis_role,
                        llm_profile=llm_profile,
                    ),
                    timeout=_GLOBAL_SYNTHESIS_TIMEOUT_SECONDS,
                )
        except (asyncio.TimeoutError, LLMServiceError) as exc:
            logger.warning(
                "global_llm_synthesis_fallback_used reason=%s",
                type(exc).__name__,
            )
            return None
