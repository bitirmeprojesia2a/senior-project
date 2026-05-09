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
from src.capabilities.planner import plan_capability_action
from src.capabilities.registry import CAPABILITY_REGISTRY
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
from src.core.constants import ConfidenceLevel, Department, RoutingStrategy, TaskType
from src.core.text_normalization import normalize_text
from src.db.conversation_context import ConversationContextService, ConversationResolution
from src.db.schemas import DepartmentResponse, IntentAnalysis, RoutingResult, UserQueryResponse
from src.db.telemetry import (
    TelemetryService,
    build_department_orchestrator_identity,
    build_main_orchestrator_identity,
)
from src.llm.llm_service import LLMService, LLMServiceError
from src.llm.prompt_templates import MULTI_DEPARTMENT_SYNTHESIS_SYSTEM_PROMPT
from src.quality.judge import run_judge
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
    looks_like_contact_query,
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
    _clean_source_name,
    build_evidence_packet_fallback_answer,
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
    "tesekkur": "Rica ederim. Başka bir sorunuz olursa yazabilirsiniz.",
    "sagol": "Rica ederim. Başka bir sorunuz olursa yazabilirsiniz.",
    "evet": "Hazırım. Devam etmemi istediğiniz konuyu biraz daha açık yazabilirsiniz.",
    "tamam": "Hazırım. Devam etmemi istediğiniz konuyu biraz daha açık yazabilirsiniz.",
    "anladim": "Hazırım. Devam etmemi istediğiniz konuyu biraz daha açık yazabilirsiniz.",
    "smalltalk": "Merhaba. Size öğrenci işleri, akademik programlar, finans, duyuru veya etkinlik konularında yardımcı olabilirim.",
    "hayir": "Tamam. Farklı bir konuda yardım isterseniz yazabilirsiniz.",
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
        if normalized in {"selam", "merhaba", "mrb", "naber", "nasilsin", "ne haber"}:
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

                early_event_gate_decision: dict[str, object] | None = None
                if looks_like_event_query(query):
                    early_event_gate_decision = await self._evaluate_short_circuit_gate(
                        query=query,
                        capability="event",
                        llm_profile=llm_profile,
                        heuristic_reason="Erken etkinlik sinyali.",
                    )
                    if not bool(early_event_gate_decision["allow"]):
                        if profiler is not None:
                            profiler.set_attribute(
                                "event_short_circuit",
                                {
                                    "eligible": True,
                                    "status": "blocked_by_gate",
                                    "gate": early_event_gate_decision,
                                },
                            )
                    else:
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
                            routing_reason=str(early_event_gate_decision["routing_reason"]),
                            capability_params=self._capability_params_from_gate(
                                early_event_gate_decision
                            ),
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

                # Follow-up'ta student_type belli değilse, konuşma bağlamından çıkar
                if student_type is None and conversation_resolution.student_type_hint:
                    student_type = conversation_resolution.student_type_hint

                early_announcement_reason: str | None = None
                early_announcement_gate_decision: dict[str, object] | None = None
                if (
                    looks_like_announcement_query(effective_query)
                    and not should_block_announcement_primary_flow(effective_query)
                    and not self._looks_like_incomplete_capability_fragment(effective_query)
                ):
                    early_announcement_gate_decision = await self._evaluate_short_circuit_gate(
                        query=effective_query,
                        capability="announcement",
                        llm_profile=llm_profile,
                        heuristic_reason="Erken duyuru sinyali.",
                    )
                    if bool(early_announcement_gate_decision["allow"]):
                        early_announcement_reason = str(
                            early_announcement_gate_decision["routing_reason"]
                        )
                    elif profiler is not None:
                        profiler.set_attribute(
                            "announcement_short_circuit",
                            {
                                "eligible": True,
                                "status": "blocked_by_gate",
                                "gate": early_announcement_gate_decision,
                            },
                        )
                elif (
                    conversation_resolution.is_follow_up
                    and conversation_resolution.announcement_context
                    and should_keep_announcement_follow_up(effective_query)
                ):
                    early_announcement_reason = "Duyuru follow-up baglami korundu."

                if early_announcement_reason is not None:
                    if profiler is not None:
                        profiler.set_attribute(
                            "question_cache",
                            {
                                "eligible": False,
                                "status": "bypass",
                                "reason": "announcement_query",
                            },
                        )
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
                        routing_reasoning=early_announcement_reason,
                        capability_params=self._capability_params_from_gate(
                            early_announcement_gate_decision
                        ),
                        trace_metadata=trace,
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

                capability_planner_payload = None
                # Routing (normalization dahil) her zaman ana karar katmani olarak kalir.
                # Capability planner router'i atlamaz; yalnizca routing sonrasinda
                # whitelisted capability metadata'si uretmek icin kullanilir.
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
                        and not conversation_resolution.used_context
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
                        reasoning=routing.reasoning,
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

                # Duyuru/etkinlik capability akisi.
                # Marker sinyalleri tek basina karar vermez; LLM planner veya routing
                # intent capability secmis olmalidir. Duyuru follow-up'lari ise mevcut
                # kayitli duyuru baglami uzerinden ayrica korunur.
                event_short_circuit_reason: str | None = None
                event_short_circuit_params: dict[str, object] | None = None
                if query_normalization.target_capability == "event":
                    event_short_circuit_reason = (
                        query_normalization.reasoning
                        or "Routing LLM etkinlik capability'sini secti."
                    )
                elif looks_like_event_query(effective_query):
                    if (
                        early_event_gate_decision is not None
                        and normalize_text(effective_query) == normalize_text(query)
                    ):
                        gate_decision = early_event_gate_decision
                    else:
                        gate_decision = await self._evaluate_short_circuit_gate(
                            query=effective_query,
                            capability="event",
                            llm_profile=llm_profile,
                            heuristic_reason="Routing sonrasi etkinlik sinyali.",
                    )
                    if bool(gate_decision["allow"]):
                        event_short_circuit_reason = str(gate_decision["routing_reason"])
                        event_short_circuit_params = self._capability_params_from_gate(
                            gate_decision
                        )

                if event_short_circuit_reason is not None:
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
                        routing_reason=event_short_circuit_reason,
                        capability_params=event_short_circuit_params,
                        trace_metadata=trace,
                    )

                announcement_short_circuit_reason: str | None = None
                announcement_short_circuit_params: dict[str, object] | None = None
                if query_normalization.target_capability == "announcement":
                    announcement_short_circuit_reason = (
                        query_normalization.reasoning
                        or "Routing LLM duyuru capability'sini secti."
                    )
                elif looks_like_announcement_query(effective_query):
                    if early_announcement_gate_decision is not None:
                        gate_decision = early_announcement_gate_decision
                    else:
                        gate_decision = await self._evaluate_short_circuit_gate(
                            query=effective_query,
                            capability="announcement",
                            llm_profile=llm_profile,
                            heuristic_reason="Duyuru keyword sinyali.",
                    )
                    if bool(gate_decision["allow"]):
                        announcement_short_circuit_reason = str(
                            gate_decision["routing_reason"]
                        )
                        announcement_short_circuit_params = self._capability_params_from_gate(
                            gate_decision
                        )

                is_announcement_follow_up = (
                    conversation_resolution.is_follow_up
                    and conversation_resolution.announcement_context
                    and should_keep_announcement_follow_up(effective_query)
                )
                if announcement_short_circuit_reason is not None or is_announcement_follow_up:
                    if announcement_short_circuit_reason is None:
                        announcement_short_circuit_reason = (
                            "Duyuru follow-up baglami korundu."
                        )
                    announcement_scope = self._resolve_announcement_scope(
                        query=effective_query,
                        conversation_resolution=conversation_resolution,
                        student_department=student_department,
                        student_faculty=student_faculty,
                    )
                    planner_faculty = self._capability_param_text(
                        announcement_short_circuit_params,
                        "faculty",
                    )
                    planner_unit_name = self._capability_param_text(
                        announcement_short_circuit_params,
                        "unit_name",
                    )
                    planner_limit = self._capability_param_int(
                        announcement_short_circuit_params,
                        "limit",
                        default=None,
                        minimum=1,
                        maximum=10,
                    )
                    allow_latest_fallback = self._capability_param_bool(
                        announcement_short_circuit_params,
                        "allow_latest_fallback",
                        default=should_allow_announcement_latest_fallback(effective_query),
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
                            routing_reasoning=announcement_short_circuit_reason,
                            task_type=None,
                            faculty=planner_faculty or announcement_scope["faculty"],
                            unit_name=planner_unit_name or announcement_scope["unit_name"],
                            conversation_source_refs=conversation_resolution.source_hints,
                            allow_latest_fallback=allow_latest_fallback,
                            limit=planner_limit,
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
                        capability_params=None,
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
                            conversation_source_refs=conversation_resolution.source_hints,
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
                    query=effective_query,
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
                    clarification_response = self._build_clarification_response(
                        context_id=context_id,
                        start_time=start_time,
                        query_log_id=query_log_id,
                        routing_reasoning=(
                            "Akademik program sorusu icin bolum/program bilgisi gerekli."
                        ),
                        message=ACADEMIC_DEPARTMENT_CLARIFICATION_MESSAGE,
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
                        with profile_stage("main.conversation.record_academic_department_clarification"):
                            await self._record_conversation_turn(
                                context_id=context_id,
                                original_query=query,
                                resolved_query=effective_query,
                                memory_answer=build_memory_answer(
                                    answer=ACADEMIC_DEPARTMENT_CLARIFICATION_MESSAGE
                                ),
                                final_response=clarification_response,
                                routing_task_type=routing.task_type,
                                conversation_resolution=conversation_resolution,
                            )
                    return clarification_response

                intent = routing.intent
                selected_department_count = len(set(routing.departments or []))
                main_can_own_final_answer = (
                    selected_department_count >= 1
                    and not looks_like_contact_query(effective_query)
                    and not looks_like_personal_data_query(effective_query)
                    and not (intent.is_personal if intent else False)
                )
                final_answer_owner = (
                    "main_orchestrator"
                    if main_can_own_final_answer
                    else "department_orchestrator"
                )
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
                    "final_answer_owner": final_answer_owner,
                    "specialist_response_mode": (
                        "evidence_packet" if final_answer_owner == "main_orchestrator" else "answer"
                    ),
                    **trace,
                }
                if capability_planner_payload is None:
                    capability_planner_payload = await self._maybe_plan_capability(
                        query=effective_query,
                        routing=routing,
                        conversation_resolution=conversation_resolution,
                        student_department=student_department,
                        student_faculty=student_faculty,
                        student_type=student_type,
                        llm_profile=llm_profile,
                    )
                if capability_planner_payload is not None:
                    metadata["capability_planner"] = capability_planner_payload

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
                    clarification_response = self._build_clarification_response(
                        context_id=context_id,
                        start_time=start_time,
                        query_log_id=query_log_id,
                        routing_reasoning=(
                            "Uzman ajan bolum/program netlestirmesi istedi."
                        ),
                        message=department_responses[0].answer,
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
                        with profile_stage("main.conversation.record_department_context_clarification"):
                            await self._record_conversation_turn(
                                context_id=context_id,
                                original_query=query,
                                resolved_query=effective_query,
                                memory_answer=build_memory_answer(
                                    answer=department_responses[0].answer
                                ),
                                final_response=clarification_response,
                                routing_task_type=routing.task_type,
                                conversation_resolution=conversation_resolution,
                            )
                    return clarification_response

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
                            conversation_source_refs=conversation_resolution.source_hints,
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
                                conversation_source_refs=conversation_resolution.source_hints,
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

                # Post-synthesis judge quality gate
                # Only runs when LLM_MAIN_JUDGE_ENABLED is true AND
                # the answer used global synthesis or is multi-department risky.
                if settings.llm.main_judge_enabled and (
                    used_global_synthesis
                    or len({r.department for r in filtered_responses if r.answer.strip()}) >= 2
                ):
                    answer = await self._apply_main_judge_gate(
                        query=effective_query,
                        answer=answer,
                        responses=filtered_responses,
                        llm_profile=llm_profile,
                        used_global_synthesis=used_global_synthesis,
                    )

                memory_answer = build_memory_answer(answer=answer)
                
                agents_involved = []
                for r in filtered_responses:
                    agent_name = r.metadata.get("agent_id") or r.department.value
                    if agent_name not in agents_involved:
                        agents_involved.append(agent_name)
                if used_global_synthesis and "orchestrator" not in agents_involved:
                    agents_involved.append("orchestrator")

                final_response = self._build_user_query_response(
                    answer=answer,
                    responses=filtered_responses,
                    department_responses=filtered_departments,
                    context_id=context_id,
                    start_time=start_time,
                    student_full_name=student_full_name,
                    used_global_synthesis=used_global_synthesis,
                    routing_strategy=routing.strategy.value if routing else None,
                    agents_involved=agents_involved,
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

    def _routing_for_capability_owner(
        self,
        routing,
        planner_payload: dict | None,
    ):
        """Route an applied capability to departments selected by the planner.

        The department router remains the legacy fallback. This method does not
        infer an owner from the registry; the planner's single JSON decision
        must include departments when it wants to override legacy routing.
        """
        if not isinstance(planner_payload, dict) or not planner_payload.get("apply"):
            return None
        action = planner_payload.get("action")
        if not isinstance(action, dict):
            return None
        capability = str(action.get("capability") or "").strip().lower()
        if not capability or capability == "none":
            return None
        confidence = float(action.get("confidence") or 0.0)
        if confidence < settings.capability_planner.confidence_threshold:
            return None
        missing_params = action.get("missing_params") or []
        if missing_params:
            return None

        planner_departments: list[Department] = []
        for department_value in action.get("departments") or []:
            try:
                department = Department(str(department_value).strip().lower())
            except ValueError:
                return None
            if department not in planner_departments:
                planner_departments.append(department)
        if not planner_departments:
            return None

        current_departments = list(routing.departments or [])
        if current_departments == planner_departments:
            return None

        reasoning = (
            f"{routing.reasoning or ''} Capability planner selected "
            f"{capability}; dispatching to planner-selected department(s): "
            f"{', '.join(department.value for department in planner_departments)}."
        ).strip()
        return routing.model_copy(
            update={
                "departments": planner_departments,
                "strategy": (
                    RoutingStrategy.DIRECT
                    if len(planner_departments) == 1
                    else RoutingStrategy.PARALLEL
                ),
                "reasoning": reasoning,
            },
            deep=True,
        )

    async def _maybe_plan_capability_pre_route(
        self,
        *,
        query: str,
        conversation_resolution: ConversationResolution,
        student_department: str | None,
        student_faculty: str | None,
        student_type: str | None,
        llm_profile: str | None,
    ) -> dict | None:
        """Run the capability planner before department routing when safe.

        This is the first controlled router+planner merge: if the planner
        confidently selects a whitelisted capability with a Department owner,
        the legacy router LLM can be skipped. Low-confidence, missing-slot,
        non-Department, or invalid decisions fall back to normal routing.
        """
        planner_settings = settings.capability_planner
        if (
            not planner_settings.enabled
            or not planner_settings.should_apply
            or not planner_settings.pre_route_enabled
        ):
            return None
        scope = planner_settings.scope_set
        if not scope:
            return None

        context = {
            "original_query": conversation_resolution.original_query,
            "effective_query": conversation_resolution.effective_query,
            "standalone_query": conversation_resolution.standalone_query,
            "is_follow_up": conversation_resolution.is_follow_up,
            "active_topic": conversation_resolution.active_topic,
            "department_hints": [
                getattr(department, "value", str(department))
                for department in (conversation_resolution.department_hints or [])
            ],
            "task_type_hint": (
                getattr(conversation_resolution.task_type_hint, "value", None)
                or str(conversation_resolution.task_type_hint or "")
            ),
            "source_hints": list(conversation_resolution.source_hints or []),
            "student_department": student_department,
            "student_faculty": student_faculty,
            "student_type": student_type,
            "llm_profile": llm_profile,
            "pre_route": True,
        }
        if conversation_resolution.frame is not None:
            context["conversation_frame"] = conversation_resolution.frame.to_prompt_context()

        with profile_stage("main.capability_planner.pre_route", mode=planner_settings.mode):
            action = await plan_capability_action(
                query=query,
                departments=sorted(scope),
                llm_service=self.llm_service,
                context=context,
                timeout_seconds=planner_settings.timeout_seconds,
            )
        if action is not None:
            action = self._normalize_capability_action_params(action, query=query)

        payload = {
            "mode": planner_settings.mode,
            "apply": planner_settings.should_apply,
            "pre_route": True,
            "action": action.model_dump() if action is not None else None,
            "plan_decision": action.to_plan_decision().model_dump() if action is not None else None,
            "departments": [],
            "legacy_routing": None,
        }
        if action is not None:
            logger.info(
                "capability_planner_pre_route_decision mode=%s apply=%s capability=%s confidence=%.2f missing=%s fallback=%s",
                planner_settings.mode,
                planner_settings.should_apply,
                action.capability,
                action.confidence,
                action.missing_params,
                action.fallback,
            )
        else:
            logger.info(
                "capability_planner_pre_route_decision mode=%s apply=%s capability=none",
                planner_settings.mode,
                planner_settings.should_apply,
            )
        profiler = get_current_profiler()
        if profiler is not None:
            profiler.set_attribute("capability_planner_pre_route", payload)
        return payload

    @staticmethod
    def _routing_from_capability_payload(planner_payload: dict | None) -> RoutingResult | None:
        """Build routing from the LLM planner's departments field.

        This intentionally does not derive departments from the capability
        registry. The single planner call owns both decisions; the registry is
        only used elsewhere to validate that the capability itself is known.
        """
        if not isinstance(planner_payload, dict) or not planner_payload.get("apply"):
            return None
        if not planner_payload.get("pre_route"):
            return None
        action = planner_payload.get("action")
        if not isinstance(action, dict):
            return None
        capability = str(action.get("capability") or "").strip().lower()
        if not capability or capability == "none":
            return None
        confidence = float(action.get("confidence") or 0.0)
        threshold = max(
            float(settings.capability_planner.confidence_threshold),
            float(settings.capability_planner.pre_route_confidence_threshold),
        )
        if confidence < threshold:
            return None
        if action.get("missing_params") or action.get("fallback"):
            return None

        owner_departments: list[Department] = []
        for department_value in action.get("departments") or []:
            try:
                department = Department(str(department_value).strip().lower())
            except ValueError:
                return None
            if department not in owner_departments:
                owner_departments.append(department)
        if not owner_departments:
            return None

        target_capability = capability.split(".", 1)[0]
        if target_capability not in {"announcement", "event"}:
            target_capability = "none"

        return RoutingResult(
            departments=owner_departments,
            confidence=confidence,
            confidence_level=(
                ConfidenceLevel.HIGH if confidence >= 0.7 else ConfidenceLevel.MEDIUM
            ),
            strategy=(
                RoutingStrategy.DIRECT
                if len(owner_departments) == 1
                else RoutingStrategy.PARALLEL
            ),
            reasoning=(
                f"Capability planner pre-route selected {capability}; "
                "legacy router skipped for this confident whitelisted decision."
            ),
            task_type=None,
            intent=IntentAnalysis(
                complexity="simple",
                is_personal=False,
                force_llm_synthesis=False,
                query_type="procedural"
                if str(capability).endswith(".policy_lookup")
                else "factual",
                reasoning=str(action.get("reasoning") or ""),
                canonical_query=None,
                primary_intent=str(action.get("intent") or capability),
                target_capability=target_capability,
                required_slots=[],
                missing_slots=[],
            ),
        )

    async def _maybe_plan_capability(
        self,
        *,
        query: str,
        routing,
        conversation_resolution: ConversationResolution,
        student_department: str | None,
        student_faculty: str | None,
        student_type: str | None = None,
        llm_profile: str | None = None,
    ) -> dict | None:
        planner_settings = settings.capability_planner
        if not planner_settings.enabled:
            return None

        department_values = {
            getattr(department, "value", str(department))
            for department in (routing.departments or [])
        }
        scope = planner_settings.scope_set
        if planner_settings.mode in {"on", "shadow"}:
            # In global modes the planner should see every enabled capability
            # family, including non-Department executors such as announcement
            # and event search. Legacy routing remains available as fallback;
            # this only expands the LLM planner's allowed whitelist.
            scoped_department_values = set(scope)
            if not scoped_department_values:
                return None
            planner_departments = sorted(scoped_department_values)
        else:
            scoped_department_values = department_values.intersection(scope)
            if not scoped_department_values:
                return None
            planner_departments = [
                department
                for department in (routing.departments or [])
                if getattr(department, "value", str(department)) in scoped_department_values
            ]
        if planner_settings.mode == "pilot" and (
            len(department_values) != 1 or department_values != scoped_department_values
        ):
            logger.info(
                "capability_planner_skipped mode=%s reason=pilot_requires_single_scoped_department departments=%s scope=%s",
                planner_settings.mode,
                sorted(department_values),
                sorted(scope),
            )
            return {
                "mode": planner_settings.mode,
                "apply": False,
                "action": None,
                "plan_decision": None,
                "skipped": "pilot_requires_single_scoped_department",
                "departments": sorted(department_values),
                "legacy_routing": {
                    "departments": sorted(department_values),
                    "reasoning": getattr(routing, "reasoning", None),
                    "strategy": getattr(getattr(routing, "strategy", None), "value", None)
                    or str(getattr(routing, "strategy", "") or ""),
                },
            }

        context = {
            "original_query": conversation_resolution.original_query,
            "effective_query": conversation_resolution.effective_query,
            "standalone_query": conversation_resolution.standalone_query,
            "is_follow_up": conversation_resolution.is_follow_up,
            "active_topic": conversation_resolution.active_topic,
            "department_hints": [
                getattr(department, "value", str(department))
                for department in (conversation_resolution.department_hints or [])
            ],
            "task_type_hint": (
                getattr(conversation_resolution.task_type_hint, "value", None)
                or str(conversation_resolution.task_type_hint or "")
            ),
            "source_hints": list(conversation_resolution.source_hints or []),
            "student_department": student_department,
            "student_faculty": student_faculty,
            "student_type": student_type,
            "llm_profile": llm_profile,
        }
        if conversation_resolution.frame is not None:
            context["conversation_frame"] = conversation_resolution.frame.to_prompt_context()
        with profile_stage("main.capability_planner", mode=planner_settings.mode):
            action = await plan_capability_action(
                query=query,
                departments=planner_departments,
                llm_service=self.llm_service,
                context=context,
                timeout_seconds=planner_settings.timeout_seconds,
            )
        if action is not None:
            action = self._normalize_capability_action_params(action, query=query)

        payload = {
            "mode": planner_settings.mode,
            "apply": planner_settings.should_apply,
            "action": action.model_dump() if action is not None else None,
            "plan_decision": action.to_plan_decision().model_dump() if action is not None else None,
            "departments": sorted(department_values),
            "legacy_routing": {
                "departments": sorted(department_values),
                "reasoning": getattr(routing, "reasoning", None),
                "strategy": getattr(getattr(routing, "strategy", None), "value", None)
                or str(getattr(routing, "strategy", "") or ""),
            },
        }
        if action is not None:
            logger.info(
                "capability_planner_decision mode=%s apply=%s capability=%s confidence=%.2f missing=%s fallback=%s departments=%s",
                planner_settings.mode,
                planner_settings.should_apply,
                action.capability,
                action.confidence,
                action.missing_params,
                action.fallback,
                sorted(department_values),
            )
        else:
            logger.info(
                "capability_planner_decision mode=%s apply=%s capability=none departments=%s",
                planner_settings.mode,
                planner_settings.should_apply,
                sorted(department_values),
            )
        profiler = get_current_profiler()
        if profiler is not None:
            profiler.set_attribute("capability_planner", payload)
        return payload

    @staticmethod
    def _normalize_capability_action_params(action, *, query: str):
        """Preserve the user wording when a capability needs semantic date matching.

        The planner may express a calendar question as a broad label such as
        "akademik takvim". The deterministic calendar helper matches concrete
        row phrases ("derslerin bitimi", "final sinavlari", ...), so keep the
        original query whenever it carries those row-level signals.
        """
        if action.capability != "calendar.academic_date":
            return action

        params = dict(action.params or {})
        param_query = str(params.get("query") or "").strip()
        normalized_query = normalize_text(query)
        normalized_param_query = normalize_text(param_query)
        calendar_row_markers = (
            "derslerin bitimi",
            "ders bitimi",
            "ders bitis",
            "son ders tarihi",
            "derslerin baslamasi",
            "ders baslangic",
            "final",
            "yariyil sonu",
            "butunleme",
            "ara sinav",
            "not giris",
        )
        original_has_row_marker = any(
            marker in normalized_query for marker in calendar_row_markers
        )
        if original_has_row_marker:
            params["query"] = query
            return action.model_copy(update={"params": params})
        if not param_query:
            params["query"] = query
            return action.model_copy(update={"params": params})
        return action

    async def _evaluate_short_circuit_gate(
        self,
        *,
        query: str,
        capability: str,
        llm_profile: str | None,
        heuristic_reason: str,
    ) -> dict[str, object]:
        """Optionally gate heuristic event/announcement short-circuits with LLM reasoning.

        Marker-based event/announcement short-circuits require LLM confirmation.
        When the planner is disabled or out of scope, the heuristic path is
        blocked so the normal routing LLM can make the primary decision. In
        shadow mode the legacy short-circuit is still allowed for observation.
        """
        planner_settings = settings.capability_planner
        capability_key = capability.strip().lower()
        if not planner_settings.enabled or capability_key not in planner_settings.scope_set:
            return {
                "allow": False,
                "confirmed": False,
                "mode": planner_settings.mode,
                "capability": capability_key,
                "source": "llm_required_gate_disabled",
                "routing_reason": heuristic_reason,
                "reasoning": "short-circuit gate disabled; falling through to routing LLM",
                "confidence": 0.0,
                "target_capability": "none",
                "params": {},
            }

        with profile_stage("main.short_circuit_gate", capability=capability_key):
            action = await plan_capability_action(
                query=query,
                departments=[capability_key],
                llm_service=self.llm_service,
                context={
                    "short_circuit_candidate": capability_key,
                    "legacy_reason": heuristic_reason,
                },
                timeout_seconds=planner_settings.timeout_seconds,
            )

        expected_capability = f"{capability_key}.search"
        confirmed = (
            action is not None
            and action.capability == expected_capability
            and action.confidence >= planner_settings.confidence_threshold
            and not action.missing_params
        )
        allow = confirmed or planner_settings.mode == "shadow"
        routing_reason = (
            action.reasoning
            if confirmed and action is not None and action.reasoning
            else heuristic_reason
        )
        payload: dict[str, object] = {
            "allow": allow,
            "confirmed": confirmed,
            "mode": planner_settings.mode,
            "capability": capability_key,
            "source": "llm_gate",
            "routing_reason": routing_reason,
            "reasoning": action.reasoning if action is not None else None,
            "confidence": action.confidence if action is not None else 0.0,
            "target_capability": action.capability if action is not None else "none",
            "params": action.params if action is not None else {},
        }
        logger.info(
            "short_circuit_gate capability=%s mode=%s allow=%s confirmed=%s target=%s confidence=%.2f",
            capability_key,
            planner_settings.mode,
            allow,
            confirmed,
            payload["target_capability"],
            payload["confidence"],
        )
        profiler = get_current_profiler()
        if profiler is not None:
            profiler.set_attribute(f"{capability_key}_short_circuit_gate", payload)
        return payload

    @staticmethod
    def _looks_like_incomplete_capability_fragment(query: str) -> bool:
        """Let very short unfinished capability fragments go through LLM routing."""
        normalized = normalize_text(query).strip(" \t\r\n?.!,;:")
        tokens = normalized.split()
        if len(tokens) > 2:
            return False
        incomplete_markers = {"duyur", "haber", "ilan", "etkinlik"}
        return any(token in incomplete_markers for token in tokens)

    @staticmethod
    def _capability_params_from_gate(
        gate_decision: dict[str, object] | None,
    ) -> dict[str, object] | None:
        if not isinstance(gate_decision, dict):
            return None
        params = gate_decision.get("params")
        if not isinstance(params, dict) or not params:
            return None
        return dict(params)

    @staticmethod
    def _capability_param_text(
        params: dict[str, object] | None,
        name: str,
    ) -> str | None:
        if not isinstance(params, dict):
            return None
        value = params.get(name)
        text = str(value).strip() if value is not None else ""
        return text or None

    @staticmethod
    def _capability_param_int(
        params: dict[str, object] | None,
        name: str,
        *,
        default: int | None,
        minimum: int,
        maximum: int,
    ) -> int | None:
        if not isinstance(params, dict) or name not in params:
            return default
        try:
            parsed = int(params.get(name))
        except (TypeError, ValueError):
            return default
        return max(minimum, min(parsed, maximum))

    @staticmethod
    def _capability_param_bool(
        params: dict[str, object] | None,
        name: str,
        *,
        default: bool,
    ) -> bool:
        if not isinstance(params, dict) or name not in params:
            return default
        value = params.get(name)
        if isinstance(value, bool):
            return value
        text = str(value).strip().lower()
        if text in {"true", "1", "yes", "evet"}:
            return True
        if text in {"false", "0", "no", "hayir", "hayÄ±r"}:
            return False
        return default

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
        routing_reason: str | None = None,
        capability_params: dict[str, object] | None = None,
        trace_metadata: dict | None = None,
    ) -> UserQueryResponse:
        """Handle explicit event queries without waiting for generic routing."""
        event_scope = self._resolve_event_scope(
            query=query,
            student_department=student_department,
            student_faculty=student_faculty,
        )
        planner_faculty = self._capability_param_text(capability_params, "faculty")
        planner_unit_name = self._capability_param_text(capability_params, "unit_name")
        planner_limit = self._capability_param_int(
            capability_params,
            "limit",
            default=5,
            minimum=1,
            maximum=10,
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
                routing_reason=(
                    routing_reason
                    or "Etkinlik short-circuit: sorgu dogrudan etkinlik ajanina yonlendirildi."
                ),
                query_log_id=query_log_id,
                task_type=None,
                faculty=planner_faculty or event_scope["faculty"],
                unit_name=planner_unit_name or event_scope["unit_name"],
                limit=planner_limit or 5,
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
        capability_params: dict[str, object] | None = None,
        trace_metadata: dict | None = None,
    ) -> UserQueryResponse:
        """Handle explicit announcement queries without generic routing."""
        announcement_scope = self._resolve_announcement_scope(
            query=query,
            conversation_resolution=conversation_resolution,
            student_department=student_department,
            student_faculty=student_faculty,
        )
        planner_faculty = self._capability_param_text(capability_params, "faculty")
        planner_unit_name = self._capability_param_text(capability_params, "unit_name")
        planner_limit = self._capability_param_int(
            capability_params,
            "limit",
            default=None,
            minimum=1,
            maximum=10,
        )
        allow_latest_fallback = self._capability_param_bool(
            capability_params,
            "allow_latest_fallback",
            default=should_allow_announcement_latest_fallback(query),
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
                faculty=planner_faculty or announcement_scope["faculty"],
                unit_name=planner_unit_name or announcement_scope["unit_name"],
                conversation_source_refs=conversation_resolution.source_hints,
                allow_latest_fallback=allow_latest_fallback,
                limit=planner_limit,
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
        routing_strategy: str | None = None,
        agents_involved: list[str] | None = None,
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
            routing_strategy=routing_strategy,
            agents_involved=agents_involved,
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

        # Source-backed answers are refined here even for a single department.
        # If final refinement fails, the specialist answer remains the fallback.
        synthesized = await self._synthesize_department_answers(
            query=query,
            responses=responses,
            llm_profile=llm_profile,
        )
        if not synthesized:
            fallback = build_evidence_packet_fallback_answer(responses)
            if fallback:
                if responses_need_contact_suggestion(responses):
                    fallback += CONTACT_SUGGESTION
                return fallback, False
            return self._compose_answers(responses), False

        # Claim guard on global synthesis; use filtered_responses' sources
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
                        "source": _clean_source_name(s.metadata.get("source", s.metadata.get("filename", ""))),
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

    async def _apply_main_judge_gate(
        self,
        *,
        query: str,
        answer: str,
        responses: list[DepartmentResponse],
        llm_profile: str | None = None,
        used_global_synthesis: bool = False,
    ) -> str:
        """Run the LLM-as-a-Judge quality gate on the final composed answer.

        Only runs on risky answers. Maximum 1 repair loop.
        Returns the (possibly repaired) answer string.
        """
        from src.quality.answer_filter import check_answer_quality

        # Pre-check: foreign token suspicion
        quality = check_answer_quality(answer)
        has_foreign_suspicion = quality.needs_rewrite and bool(quality.bad_tokens)

        # Multi-department detection
        is_multi_department = len({r.department for r in responses if r.answer.strip()}) >= 2

        # Build structured evidence summary for judge
        # NOTE: RAGSource.metadata does NOT carry selected_sentences or
        # extracted_facts; those live on EvidenceItem objects which are not
        # available at this stage.  We use content + source name + score only.
        evidence_parts: list[str] = []
        for resp in responses:
            if not resp.sources:
                continue
            for s in resp.sources[:3]:
                source_name = _clean_source_name(s.metadata.get("source", s.metadata.get("filename", "")))
                score_str = f"skor={s.score:.2f}" if s.score else ""
                entry = f"[{resp.department.value}/{source_name}] {score_str}"
                entry += f"\n  \u0130\u00e7erik: {s.content[:500]}"
                evidence_parts.append(entry)
        evidence_summary = "\n\n".join(evidence_parts)[:2000]
        plan_decision: dict | None = None
        answer_contract: dict | None = None
        evidence_contract: dict | None = None
        for resp in responses:
            metadata = resp.metadata or {}
            packet = metadata.get("evidence_packet") if isinstance(metadata, dict) else None
            candidates = [metadata, packet] if isinstance(packet, dict) else [metadata]
            for candidate in candidates:
                if not isinstance(candidate, dict):
                    continue
                if plan_decision is None and isinstance(candidate.get("plan_decision"), dict):
                    plan_decision = candidate.get("plan_decision")
                if answer_contract is None and isinstance(candidate.get("answer_contract"), dict):
                    answer_contract = candidate.get("answer_contract")
                if evidence_contract is None and isinstance(candidate.get("evidence_contract"), dict):
                    evidence_contract = candidate.get("evidence_contract")
            if plan_decision or answer_contract or evidence_contract:
                break

        # Intent coverage check
        intent_coverage_is_low = False
        missing_intents: list[str] = []
        try:
            from src.quality.intent_coverage import compute_intent_coverage
            coverage = compute_intent_coverage(query, [r.answer for r in responses if r.answer.strip()])
            intent_coverage_is_low = coverage.is_low
            missing_intents = coverage.uncovered
        except Exception:
            pass

        judge_result = await run_judge(
            query=query,
            answer=answer,
            evidence_summary=evidence_summary,
            plan_decision=plan_decision,
            answer_contract=answer_contract,
            evidence_contract=evidence_contract,
            llm_service=self.llm_service,
            llm_profile=llm_profile,
            is_multi_department=is_multi_department,
            has_foreign_suspicion=has_foreign_suspicion,
            intent_coverage_is_low=intent_coverage_is_low,
            missing_intents=missing_intents if missing_intents else None,
        )

        if judge_result is None:
            # Not risky or judge failed; accept as-is
            return answer

        _profiler = get_current_profiler()
        judge_meta = {
            "approved": judge_result.approved,
            "action": judge_result.action,
            "failure_reason": judge_result.failure_reason,
            "plan_decision": plan_decision,
            "answer_contract": answer_contract,
            "evidence_contract": evidence_contract,
        }
        if _profiler is not None:
            _profiler.set_attribute("main_judge", judge_meta)

        logger.info(
            "main_judge_result approved=%s action=%s failure=%s",
            judge_result.approved,
            judge_result.action,
            judge_result.failure_reason,
        )

        if judge_result.approved or judge_result.action == "accept":
            return answer

        # Main-level judge does NOT use ask_clarification; that is a
        # specialist-agent concern.  Fall through to rewrite_only repair.
        # retrieve_again is also downgraded to rewrite_only at this level
        # because re-dispatching departments is too expensive post-synthesis.

        if judge_result.action in ("rewrite_only", "retrieve_again", "ask_clarification"):
            # Single repair attempt via LLM
            repair_context = evidence_summary
            if judge_result.suggested_query:
                repair_context += f"\n\nJudge \u00f6nerisi: {judge_result.suggested_query}"

            repair_prompt = (
                f"Kullan\u0131c\u0131 sorusu:\n{query}\n\n"
                f"\u00d6nceki cevap:\n{answer}\n\n"
                f"Judge sorunu:\n{judge_result.failure_reason or judge_result.action}\n\n"
                f"Kaynak ba\u011flam\u0131:\n{repair_context}\n\n"
                "Cevab\u0131 ayn\u0131 kaynaklara dayanarak yeniden yaz. "
                "Eksik alt niyetleri tamamla, yanl\u0131\u015f/desteklenmeyen iddialar\u0131 \u00e7\u0131kar, "
                "say\u0131/tarih/\u00fccret/AKTS/GANO bilgilerini kaynakta ge\u00e7en \u015fekliyle koru. "
                "Kaynakta yoksa uydurma. Do\u011fal T\u00fcrk\u00e7e d\u0131\u015f\u0131nda kelime kullanma."
            )
            try:
                with profile_stage("main.judge_repair"):
                    repaired = await asyncio.wait_for(
                        self.llm_service.generate(
                            prompt=repair_prompt,
                            system=MULTI_DEPARTMENT_SYNTHESIS_SYSTEM_PROMPT,
                            model_role="global_synthesis" if is_multi_department else "final_refinement",
                            llm_profile=llm_profile,
                        ),
                        timeout=_GLOBAL_SYNTHESIS_TIMEOUT_SECONDS,
                    )
                if repaired and repaired.strip():
                    logger.info("main_judge_repair_success original_len=%d repaired_len=%d", len(answer), len(repaired))
                    return repaired.strip()
            except (asyncio.TimeoutError, LLMServiceError) as exc:
                logger.warning("main_judge_repair_failed reason=%s", type(exc).__name__)

        # Fallback: return original answer
        return answer
