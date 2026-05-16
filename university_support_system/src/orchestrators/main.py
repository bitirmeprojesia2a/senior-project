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
from src.core.answer_contracts import (
    answer_contract_policy_facet,
    contract_from_metadata,
    resolve_answer_contract,
    should_use_deterministic_final,
    validate_answer_against_contract,
)
from src.core.contract_answer_policy import build_contract_answer_plan, render_contract_answer_plan
from src.core.messages import CONTACT_SUGGESTION
from src.core.profiling import get_current_profiler, profile_stage
from src.core.constants import ConfidenceLevel, Department, RoutingStrategy, TaskType
from src.core.decision_authority import build_resolved_decision_metadata
from src.core.source_ownership import (
    OWNER_ACADEMIC_CALENDAR,
    OWNER_INTERNATIONAL_POLICY,
    OWNER_STUDENT_AFFAIRS_POLICY,
    resolve_source_ownership,
    source_ownership_to_metadata,
)
from src.core.text_normalization import normalize_text
from src.diagnostics import (
    build_decision_trace_record,
    build_shadow_decision_contract,
    decision_contract_to_metadata,
    write_decision_trace_record,
)
from src.db.conversation_context import ConversationContextService, ConversationResolution
from src.db.schemas import DepartmentResponse, IntentAnalysis, RoutingResult, UserQueryResponse
from src.agents.student.graduation_utils import (
    GRADUATION_AKTS_POLICY_FACET,
    is_graduation_akts_total_query,
)
from src.db.telemetry import (
    TelemetryService,
    build_department_orchestrator_identity,
    build_main_orchestrator_identity,
)
from src.llm.llm_service import LLMService, LLMServiceError
from src.llm.prompt_templates import MULTI_DEPARTMENT_SYNTHESIS_SYSTEM_PROMPT
from src.quality.evidence_answer_validator import (
    AnswerValidationResult,
    should_enforce_validation,
    validate_evidence_answer,
)
from src.quality.answer_coverage import validate_answer_coverage
from src.quality.answer_value_conflict import validate_answer_value_conflicts
from src.quality.judge import run_judge
from src.orchestrators.announcement_utils import (
    build_announcement_response,
    request_announcement_response,
)
from src.orchestrators.defaults import build_default_orchestrators, build_remote_department_targets
from src.orchestrators.department_dispatch import dispatch_to_departments
from src.orchestrators.event_utils import build_event_response, request_event_response
from src.orchestrators.final_quality import TEMPORARY_SYNTHESIS_FAILURE_ANSWER
from src.orchestrators.query_policy import (
    ACADEMIC_DEPARTMENT_CLARIFICATION_MESSAGE,
    CLARIFICATION_MESSAGE,
    build_supplemental_announcement_probe_query,
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
from src.orchestrators.response_utils import (
    build_response_filter_diagnostics,
    filter_low_confidence_responses,
    is_announcement_response,
    is_low_confidence_rag_response,
    is_no_info_response,
)
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


def _status_severity(status: str) -> int:
    return {"skipped": 0, "pass": 0, "check": 1, "fail": 2}.get(str(status or ""), 1)


def _preserved_required_values(result: AnswerValidationResult) -> set[str]:
    answer_values = set(result.answer_values)
    preserved: set[str] = set()
    for claim in result.required_claims:
        for value in claim.required_values:
            labels = {value.raw, *value.aliases}
            if labels & answer_values:
                preserved.add(value.raw)
    return preserved


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
                            is_authenticated=is_authenticated,
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
                        is_authenticated=is_authenticated,
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
                        self._maybe_record_decision_trace(
                            original_query=query,
                            effective_query=effective_query,
                            context_id=context_id,
                            query_log_id=query_log_id,
                            trace_metadata=trace,
                            is_authenticated=is_authenticated,
                            conversation_resolution=conversation_resolution,
                            responses=[],
                            final_response=final_response,
                            final_answer_owner="question_cache",
                            cache_lookup_policy=pre_route_cache_lookup.reason,
                            cache_store_policy="cache_hit",
                            deterministic_rules=["pre_route_question_cache_hit"],
                        )
                        return final_response

                capability_planner_payload = None
                # Routing (normalization dahil) her zaman ana karar katmani olarak kalir.
                # Capability planner router'i atlamaz; yalnizca routing sonrasinda
                # whitelisted capability metadata'si uretmek icin kullanilir.
                routing_department_hints = conversation_resolution.department_hints
                routing_task_type_hint = conversation_resolution.task_type_hint
                frame = conversation_resolution.frame
                if frame is not None:
                    safe_context_operations = {"same_topic", "answer_slot", "correction"}
                    if (
                        frame.operation not in safe_context_operations
                        or float(frame.confidence or 0.0) < 0.75
                    ):
                        routing_department_hints = []
                        routing_task_type_hint = None
                with profile_stage("main.router.route"):
                    routing = await self.router.route(
                        effective_query,
                        llm_profile=llm_profile,
                        preferred_departments=routing_department_hints,
                        preferred_task_type=routing_task_type_hint,
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
                        self._maybe_record_decision_trace(
                            original_query=query,
                            effective_query=effective_query,
                            context_id=context_id,
                            query_log_id=query_log_id,
                            trace_metadata=trace,
                            is_authenticated=is_authenticated,
                            routing=routing,
                            conversation_resolution=conversation_resolution,
                            responses=[],
                            final_response=final_response,
                            final_answer_owner="question_cache",
                            cache_lookup_policy=cache_lookup_decision.reason,
                            cache_store_policy="cache_hit",
                            deterministic_rules=["question_cache_hit"],
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
                        is_authenticated=is_authenticated,
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
                    source_owner_payload = source_ownership_to_metadata(
                        resolve_source_ownership(override="announcement_search")
                    )
                    source_owner_payload["final_answer_owner"] = "announcement_agent"
                    decision_contract_payload = self._build_runtime_decision_contract_metadata(
                        original_query=query,
                        effective_query=effective_query,
                        routing=routing,
                        conversation_resolution=conversation_resolution,
                        final_answer_owner="announcement_agent",
                        cache_lookup_policy=cache_lookup_decision.reason,
                        source_owner_override="announcement_search",
                        source_owner_payload=source_owner_payload,
                        deterministic_rules=["announcement_short_circuit"],
                        stage="announcement_short_circuit",
                    )
                    resolved_decision_payload = build_resolved_decision_metadata(
                        original_query=query,
                        effective_query=effective_query,
                        routing=routing,
                        conversation_resolution=conversation_resolution,
                        capability_planner_payload=capability_planner_payload,
                        source_owner_payload=source_owner_payload,
                        final_answer_owner="announcement_agent",
                        cache_lookup_policy=cache_lookup_decision.reason,
                        decision_contract_payload=decision_contract_payload,
                        stage="announcement_short_circuit",
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
                            decision_contract=decision_contract_payload,
                            resolved_decision=resolved_decision_payload,
                            trace_metadata=trace,
                        )
                    if announcement_user_response.answer == TEMPORARY_SYNTHESIS_FAILURE_ANSWER:
                        return announcement_user_response
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
                    self._maybe_record_decision_trace(
                        original_query=query,
                        effective_query=effective_query,
                        context_id=context_id,
                        query_log_id=query_log_id,
                        trace_metadata=trace,
                        is_authenticated=is_authenticated,
                        routing=routing,
                        conversation_resolution=conversation_resolution,
                        responses=[],
                        final_response=announcement_user_response,
                        final_answer_owner="announcement_agent",
                        cache_lookup_policy=cache_lookup_decision.reason,
                        source_owner_override="announcement_search",
                        source_owner_payload=source_owner_payload,
                        deterministic_rules=["announcement_short_circuit"],
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
                        is_authenticated=is_authenticated,
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
                    source_owner_payload = source_ownership_to_metadata(
                        resolve_source_ownership(override="announcement_search")
                    )
                    source_owner_payload["final_answer_owner"] = "announcement_agent"
                    decision_contract_payload = self._build_runtime_decision_contract_metadata(
                        original_query=query,
                        effective_query=effective_query,
                        routing=routing,
                        conversation_resolution=conversation_resolution,
                        final_answer_owner="announcement_agent",
                        cache_lookup_policy=cache_lookup_decision.reason,
                        source_owner_override="announcement_search",
                        source_owner_payload=source_owner_payload,
                        deterministic_rules=["announcement_short_circuit"],
                        stage="announcement_short_circuit",
                    )
                    resolved_decision_payload = build_resolved_decision_metadata(
                        original_query=query,
                        effective_query=effective_query,
                        routing=routing,
                        conversation_resolution=conversation_resolution,
                        capability_planner_payload=capability_planner_payload,
                        source_owner_payload=source_owner_payload,
                        final_answer_owner="announcement_agent",
                        cache_lookup_policy=cache_lookup_decision.reason,
                        decision_contract_payload=decision_contract_payload,
                        stage="announcement_short_circuit",
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
                            allow_latest_fallback=should_allow_announcement_latest_fallback(
                                effective_query
                            ),
                            decision_contract=decision_contract_payload,
                            resolved_decision=resolved_decision_payload,
                            trace_metadata=trace,
                        )
                    if announcement_user_response.answer == TEMPORARY_SYNTHESIS_FAILURE_ANSWER:
                        return announcement_user_response
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
                    self._maybe_record_decision_trace(
                        original_query=query,
                        effective_query=effective_query,
                        context_id=context_id,
                        query_log_id=query_log_id,
                        trace_metadata=trace,
                        is_authenticated=is_authenticated,
                        routing=routing,
                        conversation_resolution=conversation_resolution,
                        responses=[],
                        final_response=announcement_user_response,
                        final_answer_owner="announcement_agent",
                        cache_lookup_policy=cache_lookup_decision.reason,
                        source_owner_override="announcement_search",
                        source_owner_payload=source_owner_payload,
                        deterministic_rules=["announcement_short_circuit"],
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
                    self._maybe_record_decision_trace(
                        original_query=query,
                        effective_query=effective_query,
                        context_id=context_id,
                        query_log_id=query_log_id,
                        trace_metadata=trace,
                        is_authenticated=is_authenticated,
                        routing=routing,
                        conversation_resolution=conversation_resolution,
                        final_response=clarification_response,
                        final_answer_owner="clarification",
                        cache_lookup_policy=cache_lookup_decision.reason,
                        deterministic_rules=["missing_slot_clarification"],
                    )
                    return clarification_response

                if routing.strategy.name == "CLARIFICATION" and not routing.departments:
                    clarification_response = self._build_clarification_response(
                        context_id=context_id,
                        start_time=start_time,
                        query_log_id=query_log_id,
                        routing_reasoning=routing.reasoning,
                        full_name=student_full_name,
                    )
                    self._maybe_record_decision_trace(
                        original_query=query,
                        effective_query=effective_query,
                        context_id=context_id,
                        query_log_id=query_log_id,
                        trace_metadata=trace,
                        is_authenticated=is_authenticated,
                        routing=routing,
                        conversation_resolution=conversation_resolution,
                        final_response=clarification_response,
                        final_answer_owner="clarification",
                        cache_lookup_policy=cache_lookup_decision.reason,
                        deterministic_rules=["router_clarification"],
                    )
                    return clarification_response

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
                    self._maybe_record_decision_trace(
                        original_query=query,
                        effective_query=effective_query,
                        context_id=context_id,
                        query_log_id=query_log_id,
                        trace_metadata=trace,
                        is_authenticated=is_authenticated,
                        routing=routing,
                        conversation_resolution=conversation_resolution,
                        final_response=clarification_response,
                        final_answer_owner="clarification",
                        cache_lookup_policy=cache_lookup_decision.reason,
                        deterministic_rules=["academic_department_clarification"],
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
                frame_payload = None
                if conversation_resolution is not None and conversation_resolution.frame is not None:
                    try:
                        frame_payload = conversation_resolution.frame.to_prompt_context()
                    except Exception:
                        frame_payload = None
                answer_contract = resolve_answer_contract(
                    effective_query,
                    conversation_frame=frame_payload if isinstance(frame_payload, dict) else None,
                )
                if answer_contract is not None:
                    if should_use_deterministic_final(answer_contract):
                        final_answer_owner = "department_orchestrator"
                        metadata["final_answer_owner"] = final_answer_owner
                        metadata["specialist_response_mode"] = "answer"
                    metadata["answer_contract"] = answer_contract.to_metadata()
                policy_facet_payload = self._policy_facet_payload(
                    query=effective_query,
                    conversation_resolution=conversation_resolution,
                )
                if policy_facet_payload is not None:
                    metadata["policy_facet"] = policy_facet_payload
                elif answer_contract is not None:
                    metadata["policy_facet"] = answer_contract_policy_facet(answer_contract)
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
                capability_planner_payload = self._enforce_policy_facet_capability(
                    capability_planner_payload,
                    policy_facet_payload=policy_facet_payload,
                    query=effective_query,
                )
                capability_planner_payload = self._enforce_answer_contract_capability(
                    capability_planner_payload,
                    answer_contract_payload=metadata.get("answer_contract"),
                    query=effective_query,
                )
                if capability_planner_payload is not None:
                    metadata["capability_planner"] = capability_planner_payload
                source_owner_payload = self._resolve_source_owner_payload(
                    original_query=query,
                    effective_query=effective_query,
                    routing=routing,
                    capability_planner_payload=capability_planner_payload,
                    final_answer_owner=final_answer_owner,
                )
                if answer_contract is not None:
                    source_owner_payload["primary"] = answer_contract.source_owner
                    source_owner_payload["capability"] = answer_contract.capability
                    source_owner_payload["reasoning"] = (
                        f"answer_contract:{answer_contract.contract_id}"
                    )
                    source_owner_payload["confidence"] = 1.0
                    source_owner_payload["final_answer_owner"] = final_answer_owner
                metadata["source_owner"] = source_owner_payload
                if profiler is not None:
                    profiler.set_attribute("source_owner", source_owner_payload)
                decision_contract_payload = self._build_runtime_decision_contract_metadata(
                    original_query=query,
                    effective_query=effective_query,
                    routing=routing,
                    conversation_resolution=conversation_resolution,
                    capability_planner_payload=capability_planner_payload,
                    final_answer_owner=final_answer_owner,
                    cache_lookup_policy=cache_lookup_decision.reason,
                    source_owner_payload=source_owner_payload,
                    stage="department_dispatch",
                )
                if decision_contract_payload is not None:
                    metadata["decision_contract"] = decision_contract_payload
                    if profiler is not None:
                        profiler.set_attribute(
                            "decision_contract",
                            {
                                "mode": decision_contract_payload.get("mode"),
                                "stage": decision_contract_payload.get("stage"),
                                "schema": decision_contract_payload.get("schema"),
                                "source_owner": (
                                    decision_contract_payload.get("contract", {})
                                    .get("source_owner", {})
                                    .get("primary")
                                ),
                            },
                        )
                resolved_decision_payload = build_resolved_decision_metadata(
                    original_query=query,
                    effective_query=effective_query,
                    routing=routing,
                    conversation_resolution=conversation_resolution,
                    answer_contract=answer_contract,
                    capability_planner_payload=capability_planner_payload,
                    source_owner_payload=source_owner_payload,
                    final_answer_owner=final_answer_owner,
                    cache_lookup_policy=cache_lookup_decision.reason,
                    decision_contract_payload=decision_contract_payload,
                    stage="department_dispatch",
                )
                metadata["resolved_decision"] = resolved_decision_payload
                if profiler is not None:
                    profiler.set_attribute("resolved_decision", resolved_decision_payload)

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
                    self._maybe_record_decision_trace(
                        original_query=query,
                        effective_query=effective_query,
                        context_id=context_id,
                        query_log_id=query_log_id,
                        trace_metadata=trace,
                        is_authenticated=is_authenticated,
                        routing=routing,
                        conversation_resolution=conversation_resolution,
                        capability_planner_payload=capability_planner_payload,
                        responses=department_responses,
                        final_response=clarification_response,
                        final_answer_owner="clarification",
                        cache_lookup_policy=cache_lookup_decision.reason,
                        source_owner_payload=source_owner_payload,
                        deterministic_rules=["department_context_clarification"],
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
                            allow_latest_fallback=should_allow_announcement_latest_fallback(
                                effective_query
                            ),
                            decision_contract=decision_contract_payload,
                            resolved_decision=resolved_decision_payload,
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
                                decision_contract=decision_contract_payload,
                                resolved_decision=resolved_decision_payload,
                                trace_metadata=trace,
                            )
                    if announcement_response is not None and announcement_response.sources:
                        responses.append(announcement_response)
                    supplemental_probe_query = build_supplemental_announcement_probe_query(effective_query)
                    if supplemental_probe_query:
                        announcement_scope = self._resolve_announcement_scope(
                            query=effective_query,
                            conversation_resolution=conversation_resolution,
                            student_department=student_department,
                            student_faculty=student_faculty,
                        )
                        with profile_stage("main.supplemental_announcement_probe"):
                            supplemental_response = await request_announcement_response(
                                announcement_agent=self.announcement_agent,
                                telemetry_service=self.telemetry_service,
                                query=supplemental_probe_query,
                                context_id=context_id,
                                routing_reason=routing.reasoning,
                                query_log_id=query_log_id,
                                task_type=routing.task_type,
                                faculty=announcement_scope["faculty"],
                                unit_name=announcement_scope["unit_name"],
                                conversation_source_refs=conversation_resolution.source_hints,
                                allow_latest_fallback=False,
                                probe_mode="supplemental",
                                require_keyword_match=True,
                                minimum_match_score=10,
                                recent_days=240,
                                limit=3,
                                decision_contract=decision_contract_payload,
                                resolved_decision=resolved_decision_payload,
                                trace_metadata=trace,
                            )
                        if supplemental_response is not None:
                            supplemental_response.metadata = {
                                **(supplemental_response.metadata or {}),
                                "supplemental_probe": {
                                    "mode": "pilot",
                                    "query": supplemental_probe_query,
                                    "record_count": len(supplemental_response.sources),
                                    "status": (
                                        "ran_appended"
                                        if supplemental_response.sources
                                        else "ran_no_match"
                                    ),
                                },
                            }
                        if supplemental_response is not None and (
                            supplemental_response.sources
                            or (
                                answer_contract is not None
                                and answer_contract.contract_id
                                in {"cap_application_dates"}
                            )
                        ):
                            responses.append(supplemental_response)

                with profile_stage("main.filter_low_confidence"):
                    filter_source_owner = str(
                        (source_owner_payload or {}).get("primary") or ""
                    ).strip() or None
                    filtered_responses = filter_low_confidence_responses(
                        responses,
                        source_owner=filter_source_owner,
                    )
                    filter_diagnostics = build_response_filter_diagnostics(
                        original=responses,
                        filtered=filtered_responses,
                        source_owner=filter_source_owner,
                    )
                    profiler = get_current_profiler()
                    if profiler is not None:
                        profiler.set_attribute("response_filter", filter_diagnostics)
                    filtered_departments = list(department_responses)

                with profile_stage("main.compose_response"):
                    answer, used_global_synthesis = await self._compose_final_answer(
                        query=effective_query,
                        responses=filtered_responses,
                        llm_profile=llm_profile,
                        answer_contract=answer_contract,
                    )
                synthesis_failed_temporarily = (
                    answer == TEMPORARY_SYNTHESIS_FAILURE_ANSWER
                )

                if synthesis_failed_temporarily:
                    response_time_ms = round((perf_counter() - start_time) * 1000, 2)
                    final_response = build_clarification_user_response(
                        context_id=context_id,
                        message=answer,
                        response_time_ms=response_time_ms,
                        full_name=student_full_name,
                    )
                    await self.telemetry_service.finalize_query_log(
                        query_log_id=query_log_id,
                        response_text=answer,
                        response_time_ms=final_response.response_time_ms,
                        status="failed",
                        error="llm_synthesis_failed",
                        departments=[response.department.value for response in filtered_responses],
                    )
                    profiler = get_current_profiler()
                    if profiler is not None and final_response.diagnostics is not None:
                        final_response.diagnostics.local_profile = profiler.snapshot()
                    elif profiler is not None:
                        from src.db.schemas import QueryDiagnostics
                        final_response.diagnostics = QueryDiagnostics(local_profile=profiler.snapshot())
                    return final_response

                with profile_stage("main.evidence_answer_validator"):
                    answer_validation = validate_evidence_answer(
                        query=effective_query,
                        answer=answer,
                        responses=filtered_responses,
                        mode=settings.answer_validation.mode,
                    )
                    profiler = get_current_profiler()
                    if profiler is not None:
                        profiler.set_attribute(
                            "evidence_answer_validator",
                            answer_validation.to_dict(),
                        )
                with profile_stage("main.answer_coverage_shadow"):
                    answer_coverage = validate_answer_coverage(
                        query=effective_query,
                        answer=answer,
                        responses=filtered_responses,
                    )
                    profiler = get_current_profiler()
                    if profiler is not None:
                        profiler.set_attribute(
                            "answer_coverage_validator",
                            answer_coverage.to_dict(),
                        )
                with profile_stage("main.answer_value_conflict_shadow"):
                    answer_value_conflict = validate_answer_value_conflicts(
                        query=effective_query,
                        answer=answer,
                        responses=filtered_responses,
                    )
                    profiler = get_current_profiler()
                    if profiler is not None:
                        profiler.set_attribute(
                            "answer_value_conflict_validator",
                            answer_value_conflict.to_dict(),
                        )

                is_multi_department_answer = (
                    len({r.department for r in filtered_responses if r.answer.strip()}) >= 2
                )

                # Post-synthesis judge quality gate. The deterministic
                # validator does not decide the answer; it only escalates
                # suspicious evidence/answer mismatches to the existing judge.
                if settings.llm.main_judge_enabled and (
                    used_global_synthesis
                    or is_multi_department_answer
                    or should_enforce_validation(answer_validation)
                ):
                    answer = await self._apply_main_judge_gate(
                        query=effective_query,
                        answer=answer,
                        responses=filtered_responses,
                        llm_profile=llm_profile,
                        used_global_synthesis=used_global_synthesis,
                        answer_validation=answer_validation,
                    )

                answer = await self._apply_final_quality_gate(
                    query=effective_query,
                    answer=answer,
                    llm_profile=llm_profile,
                )
                if answer == TEMPORARY_SYNTHESIS_FAILURE_ANSWER:
                    response_time_ms = round((perf_counter() - start_time) * 1000, 2)
                    final_response = build_clarification_user_response(
                        context_id=context_id,
                        message=answer,
                        response_time_ms=response_time_ms,
                        full_name=student_full_name,
                    )
                    await self.telemetry_service.finalize_query_log(
                        query_log_id=query_log_id,
                        response_text=answer,
                        response_time_ms=final_response.response_time_ms,
                        status="failed",
                        error="final_quality_gate_failed",
                        departments=[response.department.value for response in filtered_responses],
                    )
                    profiler = get_current_profiler()
                    if profiler is not None and final_response.diagnostics is not None:
                        final_response.diagnostics.local_profile = profiler.snapshot()
                    elif profiler is not None:
                        from src.db.schemas import QueryDiagnostics
                        final_response.diagnostics = QueryDiagnostics(local_profile=profiler.snapshot())
                    return final_response

                contract_validation = validate_answer_against_contract(
                    query=effective_query,
                    answer=answer,
                    contract=answer_contract,
                )
                profiler = get_current_profiler()
                if profiler is not None:
                    profiler.set_attribute("answer_contract_validation", contract_validation)
                if contract_validation.get("status") == "fail":
                    original_contract_violations = list(contract_validation.get("violations") or [])
                    contract_fallback = self._contract_validation_fallback(
                        query=effective_query,
                        contract=answer_contract,
                    )
                    if contract_fallback:
                        fallback_validation = validate_answer_against_contract(
                            query=effective_query,
                            answer=contract_fallback,
                            contract=answer_contract,
                        )
                        fallback_answer = await self._apply_final_quality_gate(
                            query=effective_query,
                            answer=contract_fallback,
                            llm_profile=llm_profile,
                        )
                        if (
                            fallback_validation.get("status") != "fail"
                            and fallback_answer != TEMPORARY_SYNTHESIS_FAILURE_ANSWER
                        ):
                            logger.info(
                                "answer_contract_validation_recovered_with_fallback contract=%s violations=%s",
                                contract_validation.get("contract_id"),
                                contract_validation.get("violations"),
                            )
                            answer = fallback_answer
                            contract_validation = fallback_validation
                            if profiler is not None:
                                profiler.set_attribute(
                                    "answer_contract_validation",
                                    {
                                        **fallback_validation,
                                        "recovered_from": original_contract_violations,
                                        "fallback": "deterministic_contract_template",
                                    },
                                )
                        else:
                            contract_fallback = None
                    if contract_fallback:
                        pass
                    else:
                        logger.warning(
                            "answer_contract_validation_failed contract=%s violations=%s",
                            contract_validation.get("contract_id"),
                            contract_validation.get("violations"),
                        )
                        response_time_ms = round((perf_counter() - start_time) * 1000, 2)
                        final_response = build_clarification_user_response(
                            context_id=context_id,
                            message=TEMPORARY_SYNTHESIS_FAILURE_ANSWER,
                            response_time_ms=response_time_ms,
                            full_name=student_full_name,
                        )
                        await self.telemetry_service.finalize_query_log(
                            query_log_id=query_log_id,
                            response_text=TEMPORARY_SYNTHESIS_FAILURE_ANSWER,
                            response_time_ms=final_response.response_time_ms,
                            status="failed",
                            error="answer_contract_validation_failed",
                            departments=[response.department.value for response in filtered_responses],
                        )
                        if profiler is not None and final_response.diagnostics is not None:
                            final_response.diagnostics.local_profile = profiler.snapshot()
                        elif profiler is not None:
                            from src.db.schemas import QueryDiagnostics
                            final_response.diagnostics = QueryDiagnostics(local_profile=profiler.snapshot())
                        return final_response

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
                self._maybe_record_decision_trace(
                    original_query=query,
                    effective_query=effective_query,
                    context_id=context_id,
                    query_log_id=query_log_id,
                    trace_metadata=trace,
                    is_authenticated=is_authenticated,
                    routing=routing,
                    conversation_resolution=conversation_resolution,
                    capability_planner_payload=capability_planner_payload,
                    responses=filtered_responses,
                    final_response=final_response,
                    final_answer_owner=final_answer_owner,
                    used_global_synthesis=used_global_synthesis,
                    cache_lookup_policy=cache_lookup_decision.reason,
                    cache_store_policy=cache_store_decision.reason,
                    source_owner_payload=source_owner_payload,
                )
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

    @staticmethod
    def _channel_from_context_id(context_id: str | None) -> str:
        if context_id and context_id.startswith("slack:"):
            return "slack"
        return "api_or_a2a"

    @staticmethod
    def _selected_specialists_from_responses(responses: list[DepartmentResponse]) -> list[str]:
        specialists: list[str] = []
        for response in responses:
            metadata = dict(response.metadata or {})
            selection = metadata.get("specialist_selection")
            selection_agent_id = (
                selection.get("selected_agent_id")
                if isinstance(selection, dict)
                else None
            )
            agent_id = str(
                selection_agent_id
                or metadata.get("selected_agent_id")
                or metadata.get("agent_id")
                or response.department.value
            ).strip()
            if agent_id and agent_id not in specialists:
                specialists.append(agent_id)
        return specialists

    @staticmethod
    def _planner_action_payload(planner_payload: dict | None) -> dict | None:
        if not isinstance(planner_payload, dict):
            return None
        action = planner_payload.get("action")
        return action if isinstance(action, dict) else None

    @staticmethod
    def _policy_facet_payload(
        *,
        query: str,
        conversation_resolution: ConversationResolution | None,
    ) -> dict | None:
        frame_payload = None
        if conversation_resolution is not None and conversation_resolution.frame is not None:
            try:
                frame_payload = conversation_resolution.frame.to_prompt_context()
            except Exception:
                frame_payload = None
        frame_facet = ""
        if isinstance(frame_payload, dict):
            frame_facet = str(frame_payload.get("policy_facet") or frame_payload.get("facet") or "")
        if not is_graduation_akts_total_query(query, policy_facet=frame_facet):
            return None
        return {
            "schema": "omu.policy_facet.v1",
            "facet": GRADUATION_AKTS_POLICY_FACET,
            "question_type": "graduation_total_akts",
            "source_owner": OWNER_STUDENT_AFFAIRS_POLICY,
            "capability": "student_affairs.policy_lookup",
            "contract": "education_level_graduation_total",
        }

    @staticmethod
    def _enforce_policy_facet_capability(
        planner_payload: dict | None,
        *,
        policy_facet_payload: dict | None,
        query: str,
    ) -> dict | None:
        if not isinstance(policy_facet_payload, dict):
            return planner_payload
        if policy_facet_payload.get("facet") != GRADUATION_AKTS_POLICY_FACET:
            return planner_payload
        payload = dict(planner_payload or {})
        action = {
            "capability": "student_affairs.policy_lookup",
            "intent": "graduation_akts_total",
            "params": {
                "query": query,
                "topic": "mezuniyet",
                "policy_facet": GRADUATION_AKTS_POLICY_FACET,
                "question_type": "graduation_total_akts",
            },
            "missing_params": [],
            "answer_contract": {
                "must_answer": [
                    "mezuniyet icin toplam AKTS",
                    "on lisans/lisans seviye ayrimi",
                    "ders donemi AKTS yukunden ayirma",
                ],
            },
            "evidence_contract": {
                "preferred_sources": ["on_lisans_lisans_yonetmeligi", "mezuniyet_kosullari"],
                "avoid_sources": ["formasyon", "erasmus", "lisansustu", "staj", "donemlik_ders_yuku"],
            },
            "fallback_route": None,
            "confidence": 1.0,
            "fallback": None,
            "reasoning": "policy_facet_contract:graduation_akts_total",
        }
        payload.update(
            {
                "mode": payload.get("mode") or "contract",
                "apply": True,
                "action": action,
                "plan_decision": action,
                "policy_facet_enforced": True,
            }
        )
        return payload

    @staticmethod
    def _enforce_answer_contract_capability(
        planner_payload: dict | None,
        *,
        answer_contract_payload: dict | None,
        query: str,
    ) -> dict | None:
        if not isinstance(answer_contract_payload, dict):
            return planner_payload
        capability = str(answer_contract_payload.get("capability") or "").strip()
        if not capability:
            return planner_payload

        contract_id = str(answer_contract_payload.get("contract_id") or "").strip()
        facet = str(answer_contract_payload.get("facet") or contract_id).strip()
        existing_action = (
            planner_payload.get("action")
            if isinstance(planner_payload, dict) and isinstance(planner_payload.get("action"), dict)
            else {}
        )
        existing_params = (
            existing_action.get("params")
            if isinstance(existing_action, dict) and isinstance(existing_action.get("params"), dict)
            else {}
        )
        params: dict[str, object] = {
            **existing_params,
            "query": query,
            "policy_facet": facet,
            "answer_contract": answer_contract_payload,
        }
        if capability == "schedule.weekly_program":
            program = None
            frame_entities = answer_contract_payload.get("entities")
            if isinstance(frame_entities, dict):
                program = frame_entities.get("program")
            # The planner is still free to provide a better canonical program.
            # This fallback keeps the action valid when conversation context
            # already rewrote the query to include the program name.
            if params.get("program"):
                pass
            elif not program:
                for marker in ("icin", "ders programi"):
                    if marker in normalize_text(query):
                        break
                params["program"] = query
            else:
                params["program"] = str(program)
        action = {
            "capability": capability,
            "intent": contract_id or facet,
            "params": params,
            "missing_params": [],
            "answer_contract": answer_contract_payload,
            "evidence_contract": {
                "source_owner": answer_contract_payload.get("source_owner"),
                "forbidden_source_families": answer_contract_payload.get("forbidden_source_families", []),
            },
            "fallback_route": None,
            "confidence": 1.0,
            "fallback": None,
            "reasoning": f"answer_contract:{contract_id or facet}",
        }
        payload = dict(planner_payload or {})
        payload.update(
            {
                "mode": payload.get("mode") or "contract",
                "apply": True,
                "action": action,
                "plan_decision": action,
                "answer_contract_enforced": True,
            }
        )
        return payload

    def _resolve_source_owner_payload(
        self,
        *,
        original_query: str,
        effective_query: str,
        routing: RoutingResult | None,
        capability_planner_payload: dict | None,
        final_answer_owner: str | None,
    ) -> dict:
        """Build the runtime source-owner contract carried through A2A metadata."""
        intent = getattr(routing, "intent", None) if routing is not None else None
        departments = [
            getattr(department, "value", str(department))
            for department in (getattr(routing, "departments", None) or [])
        ]
        action = self._planner_action_payload(capability_planner_payload)
        capability = str(action.get("capability") or "").strip() if action else None
        policy_facet_payload = (
            action.get("params", {}).get("policy_facet")
            if isinstance(action, dict) and isinstance(action.get("params"), dict)
            else None
        )
        if policy_facet_payload == GRADUATION_AKTS_POLICY_FACET:
            capability = "student_affairs.policy_lookup"
        action_confidence = None
        if action is not None and action.get("confidence") is not None:
            try:
                action_confidence = float(action.get("confidence"))
            except (TypeError, ValueError):
                action_confidence = None
        resolution = resolve_source_ownership(
            original_query=original_query,
            effective_query=effective_query,
            capability=capability,
            primary_intent=getattr(intent, "primary_intent", None),
            target_capability=getattr(intent, "target_capability", None),
            task_type=getattr(routing, "task_type", None) if routing is not None else None,
            is_personal=bool(getattr(intent, "is_personal", False)),
            confidence=action_confidence
            if action_confidence is not None
            else getattr(routing, "confidence", None),
            final_departments=departments,
        )
        payload = source_ownership_to_metadata(resolution)
        payload["routing_departments"] = departments
        payload["final_answer_owner"] = final_answer_owner
        if capability:
            payload["capability"] = capability
        return payload

    @staticmethod
    def _build_runtime_decision_contract_metadata(
        *,
        original_query: str,
        effective_query: str,
        routing: RoutingResult | None = None,
        conversation_resolution: ConversationResolution | None = None,
        capability_planner_payload: dict | None = None,
        final_answer_owner: str | None = None,
        cache_lookup_policy: str | None = None,
        cache_store_policy: str | None = None,
        source_owner_payload: dict | None = None,
        source_owner_override: str | None = None,
        deterministic_rules: list[str] | None = None,
        stage: str = "runtime",
    ) -> dict | None:
        """Build read-only decision contract metadata; never affect behavior."""
        try:
            contract = build_shadow_decision_contract(
                original_query=original_query,
                effective_query=effective_query,
                routing=routing,
                conversation_resolution=conversation_resolution,
                capability_planner_payload=capability_planner_payload,
                final_answer_owner=final_answer_owner,
                cache_lookup_policy=cache_lookup_policy,
                cache_store_policy=cache_store_policy,
                source_owner_override=source_owner_override,
                source_owner_payload=source_owner_payload,
                deterministic_rules=deterministic_rules,
            )
            return decision_contract_to_metadata(
                contract,
                producer="main_orchestrator",
                stage=stage,
            )
        except Exception as exc:
            logger.warning(
                "runtime_decision_contract_skipped reason=%s",
                type(exc).__name__,
            )
            return None

    def _maybe_record_decision_trace(
        self,
        *,
        original_query: str,
        effective_query: str,
        context_id: str,
        query_log_id: int | None,
        trace_metadata: dict | None,
        is_authenticated: bool,
        routing: RoutingResult | None = None,
        conversation_resolution: ConversationResolution | None = None,
        capability_planner_payload: dict | None = None,
        responses: list[DepartmentResponse] | None = None,
        final_response: UserQueryResponse | None = None,
        final_answer_owner: str | None = None,
        used_global_synthesis: bool = False,
        cache_lookup_policy: str | None = None,
        cache_store_policy: str | None = None,
        source_owner_override: str | None = None,
        source_owner_payload: dict | None = None,
        deterministic_rules: list[str] | None = None,
    ) -> None:
        """Best-effort shadow contract trace writer; never affects answers."""
        if not settings.decision_trace.enabled:
            return
        try:
            responses = list(responses or [])
            profiler = get_current_profiler()
            profiler_snapshot = profiler.snapshot() if profiler is not None else None
            record = build_decision_trace_record(
                original_query=original_query,
                effective_query=effective_query,
                trace_metadata=trace_metadata,
                runtime_mode=settings.a2a.mode,
                channel=self._channel_from_context_id(context_id),
                context_id=context_id,
                query_log_id=query_log_id,
                is_authenticated=is_authenticated,
                routing=routing,
                conversation_resolution=conversation_resolution,
                capability_planner_payload=capability_planner_payload,
                responses=responses,
                final_response=final_response,
                final_answer_owner=final_answer_owner,
                used_global_synthesis=used_global_synthesis,
                cache_lookup_policy=cache_lookup_policy,
                cache_store_policy=cache_store_policy,
                selected_specialists=self._selected_specialists_from_responses(responses),
                profiler_snapshot=profiler_snapshot,
                include_answer_preview=settings.decision_trace.include_answer_preview,
                source_owner_override=source_owner_override,
                source_owner_payload=source_owner_payload,
                deterministic_rules=deterministic_rules,
            )
            with profile_stage("main.decision_trace.write"):
                output_path = write_decision_trace_record(record)
            if profiler is not None:
                profiler.set_attribute(
                    "decision_trace",
                    {
                        "enabled": True,
                        "written": True,
                        "path": str(output_path),
                        "trace_id": record.trace_id,
                    },
                )
        except Exception as exc:
            logger.warning("decision_trace_record_skipped reason=%s", type(exc).__name__)

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

    @staticmethod
    def _post_route_planner_scope(
        *,
        query: str,
        routing,
        scope: set[str],
    ) -> tuple[list[str], str]:
        """Limit planner choices to router-owned departments plus registry guards."""
        department_values = {
            getattr(department, "value", str(department))
            for department in (routing.departments or [])
        }
        planner_scope = set(department_values).intersection(scope)
        intent = getattr(routing, "intent", None)
        owner_hint = resolve_source_ownership(
            original_query=query,
            effective_query=query,
            primary_intent=getattr(intent, "primary_intent", None),
            target_capability=getattr(intent, "target_capability", None),
            task_type=getattr(routing, "task_type", None),
            is_personal=bool(getattr(intent, "is_personal", False)),
            confidence=getattr(routing, "confidence", None),
            final_departments=sorted(department_values),
        )
        owner_scope_expansions = {
            OWNER_ACADEMIC_CALENDAR: {Department.STUDENT_AFFAIRS.value},
            OWNER_INTERNATIONAL_POLICY: {Department.ACADEMIC_PROGRAMS.value},
        }
        planner_scope.update(owner_scope_expansions.get(owner_hint.primary, set()).intersection(scope))
        return sorted(planner_scope), "router_first_with_source_registry_expansions"

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
        planner_departments, planner_scope_policy = self._post_route_planner_scope(
            query=query,
            routing=routing,
            scope=scope,
        )
        scoped_department_values = set(planner_departments)
        if not scoped_department_values:
            return None
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
                "planner_scope": planner_departments,
                "planner_scope_policy": planner_scope_policy,
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
            "planner_scope_policy": planner_scope_policy,
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
            "planner_scope": planner_departments,
            "planner_scope_policy": planner_scope_policy,
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
        if text in {"false", "0", "no", "hayir", "hayır"}:
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
        is_authenticated: bool = False,
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
        source_owner_payload = source_ownership_to_metadata(
            resolve_source_ownership(override="event_search")
        )
        source_owner_payload["final_answer_owner"] = "event_agent"
        decision_contract_payload = self._build_runtime_decision_contract_metadata(
            original_query=original_query,
            effective_query=query,
            conversation_resolution=conversation_resolution,
            final_answer_owner="event_agent",
            source_owner_override="event_search",
            source_owner_payload=source_owner_payload,
            deterministic_rules=["event_short_circuit"],
            stage="event_short_circuit",
        )
        resolved_decision_payload = build_resolved_decision_metadata(
            original_query=original_query,
            effective_query=query,
            conversation_resolution=conversation_resolution,
            source_owner_payload=source_owner_payload,
            final_answer_owner="event_agent",
            decision_contract_payload=decision_contract_payload,
            stage="event_short_circuit",
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
                decision_contract=decision_contract_payload,
                resolved_decision=resolved_decision_payload,
                trace_metadata=trace_metadata,
            )
            event_user_response = await build_event_response(
                response=event_response,
                telemetry_service=self.telemetry_service,
                context_id=context_id,
                start_time=start_time,
                query_log_id=query_log_id,
            )
        if event_user_response.answer == TEMPORARY_SYNTHESIS_FAILURE_ANSWER:
            return event_user_response
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
        self._maybe_record_decision_trace(
            original_query=original_query,
            effective_query=query,
            context_id=context_id,
            query_log_id=query_log_id,
            trace_metadata=trace_metadata,
            is_authenticated=is_authenticated,
            conversation_resolution=conversation_resolution,
            responses=[],
            final_response=event_user_response,
            final_answer_owner="event_agent",
            source_owner_override="event_search",
            source_owner_payload=source_owner_payload,
            deterministic_rules=["event_short_circuit"],
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
        is_authenticated: bool = False,
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
        source_owner_payload = source_ownership_to_metadata(
            resolve_source_ownership(override="announcement_search")
        )
        source_owner_payload["final_answer_owner"] = "announcement_agent"
        decision_contract_payload = self._build_runtime_decision_contract_metadata(
            original_query=original_query,
            effective_query=query,
            conversation_resolution=conversation_resolution,
            final_answer_owner="announcement_agent",
            source_owner_override="announcement_search",
            source_owner_payload=source_owner_payload,
            deterministic_rules=["announcement_short_circuit"],
            stage="announcement_short_circuit",
        )
        resolved_decision_payload = build_resolved_decision_metadata(
            original_query=original_query,
            effective_query=query,
            conversation_resolution=conversation_resolution,
            source_owner_payload=source_owner_payload,
            final_answer_owner="announcement_agent",
            decision_contract_payload=decision_contract_payload,
            stage="announcement_short_circuit",
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
                decision_contract=decision_contract_payload,
                resolved_decision=resolved_decision_payload,
                trace_metadata=trace_metadata,
            )
        if announcement_user_response.answer == TEMPORARY_SYNTHESIS_FAILURE_ANSWER:
            return announcement_user_response
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
        self._maybe_record_decision_trace(
            original_query=original_query,
            effective_query=query,
            context_id=context_id,
            query_log_id=query_log_id,
            trace_metadata=trace_metadata,
            is_authenticated=is_authenticated,
            conversation_resolution=conversation_resolution,
            responses=[],
            final_response=announcement_user_response,
            final_answer_owner="announcement_agent",
            source_owner_override="announcement_search",
            source_owner_payload=source_owner_payload,
            deterministic_rules=["announcement_short_circuit"],
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
        answer_contract=None,
    ) -> tuple[str, bool]:
        if should_use_deterministic_final(answer_contract):
            deterministic_fallback = self._compose_deterministic_contract_fallback(responses)
            if deterministic_fallback:
                return deterministic_fallback, False
            return self._compose_answers(responses), False

        if not should_use_global_synthesis(query=query, responses=responses):
            return self._compose_answers(responses), False

        # Source-backed answers are refined here even for a single department.
        # If final refinement fails, the specialist answer remains the fallback.
        synthesized, synthesis_failed = await self._synthesize_department_answers(
            query=query,
            responses=responses,
            llm_profile=llm_profile,
        )
        if not synthesized:
            if synthesis_failed:
                deterministic_fallback = self._compose_deterministic_contract_fallback(responses)
                if deterministic_fallback:
                    return deterministic_fallback, False
                strong_fallback = self._compose_strong_non_llm_fallback(responses)
                if strong_fallback:
                    return strong_fallback, False
                contract_fallback = self._contract_validation_fallback(
                    query=query,
                    contract=answer_contract,
                )
                if contract_fallback:
                    return contract_fallback, False
                evidence_fallback = build_evidence_packet_fallback_answer(responses, query=query)
                if evidence_fallback:
                    if responses_need_contact_suggestion(responses):
                        evidence_fallback += CONTACT_SUGGESTION
                    return evidence_fallback, False
                announcement_no_match = self._compose_announcement_no_match_fallback(responses)
                if announcement_no_match:
                    return announcement_no_match, False
                return TEMPORARY_SYNTHESIS_FAILURE_ANSWER, False
            fallback = build_evidence_packet_fallback_answer(responses, query=query)
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

    def _compose_deterministic_contract_fallback(self, responses: list[DepartmentResponse]) -> str | None:
        deterministic_responses: list[DepartmentResponse] = []
        for response in responses:
            contract = contract_from_metadata(response.metadata)
            if contract is not None and contract.synthesis_policy == "deterministic":
                deterministic_responses.append(response)
        if not deterministic_responses:
            return None
        return self._compose_answers(deterministic_responses)

    def _compose_strong_non_llm_fallback(self, responses: list[DepartmentResponse]) -> str | None:
        """Keep a reliable branch answer when optional final synthesis fails."""
        strong_responses = [
            response
            for response in responses
            if not (
                isinstance(response.metadata, dict)
                and (
                    response.metadata.get("specialist_response_mode") == "evidence_packet"
                    or response.metadata.get("final_answer_owner") == "main_orchestrator"
                )
            )
            if (
                response.success
                and response.answer.strip()
                and not is_announcement_response(response)
                and not is_low_confidence_rag_response(response)
                and not is_no_info_response(response)
            )
        ]
        if not strong_responses:
            return None
        return self._compose_answers(strong_responses)

    def _compose_announcement_no_match_fallback(self, responses: list[DepartmentResponse]) -> str | None:
        """Surface scoped announcement no-match answers instead of a synthesis error."""
        no_match_responses = [
            response
            for response in responses
            if (
                response.success
                and "ilgili aktif duyuru bulunamadi" in normalize_text(response.answer)
            )
        ]
        if not no_match_responses:
            return None
        return self._compose_answers(no_match_responses)

    @staticmethod
    def _contract_validation_fallback(*, query: str, contract) -> str | None:
        """Return a conservative answer from the shared contract answer policy."""
        plan = build_contract_answer_plan(query=query, contract=contract)
        return render_contract_answer_plan(plan)

    async def _synthesize_department_answers(
        self,
        *,
        query: str,
        responses: list[DepartmentResponse],
        llm_profile: str | None = None,
    ) -> tuple[str | None, bool]:
        prompt, meaningful = build_global_synthesis_prompt(query, responses)
        if not prompt:
            return None, False

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
                answer = await asyncio.wait_for(
                    self.llm_service.generate(
                        prompt=prompt,
                        system=MULTI_DEPARTMENT_SYNTHESIS_SYSTEM_PROMPT,
                        model_role=synthesis_role,
                        llm_profile=llm_profile,
                    ),
                    timeout=_GLOBAL_SYNTHESIS_TIMEOUT_SECONDS,
                )
                return answer, False
        except (asyncio.TimeoutError, LLMServiceError) as exc:
            logger.warning(
                "global_llm_synthesis_failed_controlled_error reason=%s",
                type(exc).__name__,
            )
            return None, True

    async def _apply_main_judge_gate(
        self,
        *,
        query: str,
        answer: str,
        responses: list[DepartmentResponse],
        llm_profile: str | None = None,
        used_global_synthesis: bool = False,
        answer_validation: AnswerValidationResult | None = None,
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
        pre_validation = answer_validation or validate_evidence_answer(
            query=query,
            answer=answer,
            responses=responses,
            mode=settings.answer_validation.mode,
        )
        pre_coverage = validate_answer_coverage(
            query=query,
            answer=answer,
            responses=responses,
        )
        pre_value_conflict = validate_answer_value_conflicts(
            query=query,
            answer=answer,
            responses=responses,
        )

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
        validation_context = (
            pre_validation.to_judge_context()
            if pre_validation is not None
            else ""
        )
        if validation_context:
            evidence_summary = f"{validation_context}\n\n{evidence_summary}"[:2500]
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
            missing_intents = coverage.missing_intents
        except Exception as exc:
            logger.warning("intent_coverage_check_failed reason=%s", type(exc).__name__)

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
            force=bool(pre_validation and should_enforce_validation(pre_validation)),
            validator_result=pre_validation.to_dict() if pre_validation else None,
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
            "triggered_by_validator": bool(pre_validation and should_enforce_validation(pre_validation)),
            "answer_validation": pre_validation.to_dict() if pre_validation else {},
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
                    repaired_answer = repaired.strip()
                    post_validation = validate_evidence_answer(
                        query=query,
                        answer=repaired_answer,
                        responses=responses,
                        mode=pre_validation.mode if pre_validation else settings.answer_validation.mode,
                    )
                    post_coverage = validate_answer_coverage(
                        query=query,
                        answer=repaired_answer,
                        responses=responses,
                    )
                    post_value_conflict = validate_answer_value_conflicts(
                        query=query,
                        answer=repaired_answer,
                        responses=responses,
                    )
                    repair_decision = self._judge_repair_decision(
                        pre_validation=pre_validation,
                        post_validation=post_validation,
                        pre_coverage=pre_coverage.to_dict(),
                        post_coverage=post_coverage.to_dict(),
                        pre_value_conflict=pre_value_conflict.to_dict(),
                        post_value_conflict=post_value_conflict.to_dict(),
                    )
                    judge_meta["repair"] = {
                        "accepted": repair_decision["accepted"],
                        "outcome": repair_decision["outcome"],
                        "rejection_reason": repair_decision["reason"],
                        "pre_repair_validation": pre_validation.to_dict(),
                        "post_repair_validation": post_validation.to_dict(),
                        "pre_repair_coverage": pre_coverage.to_dict(),
                        "post_repair_coverage": post_coverage.to_dict(),
                        "pre_repair_value_conflict": pre_value_conflict.to_dict(),
                        "post_repair_value_conflict": post_value_conflict.to_dict(),
                    }
                    if _profiler is not None:
                        _profiler.set_attribute("main_judge", judge_meta)
                    if _profiler is not None and repair_decision["accepted"]:
                        post_validation_meta = post_validation.to_dict()
                        post_validation_meta["pre_judge"] = pre_validation.to_dict()
                        post_validation_meta["judge_escalated"] = True
                        if repair_decision["outcome"] == "accepted_improved":
                            post_validation_meta["repair_accepted"] = True
                        else:
                            post_validation_meta["repair_neutral"] = True
                        post_validation_meta["repair_outcome"] = repair_decision["outcome"]
                        _profiler.set_attribute(
                            "evidence_answer_validator",
                            post_validation_meta,
                        )
                        post_coverage_meta = post_coverage.to_dict()
                        post_coverage_meta["pre_judge"] = pre_coverage.to_dict()
                        post_coverage_meta["repair_outcome"] = repair_decision["outcome"]
                        _profiler.set_attribute("answer_coverage_validator", post_coverage_meta)
                        post_value_conflict_meta = post_value_conflict.to_dict()
                        post_value_conflict_meta["pre_judge"] = pre_value_conflict.to_dict()
                        post_value_conflict_meta["repair_outcome"] = repair_decision["outcome"]
                        _profiler.set_attribute(
                            "answer_value_conflict_validator",
                            post_value_conflict_meta,
                        )
                    if repair_decision["accepted"]:
                        logger.info(
                            "main_judge_repair_success original_len=%d repaired_len=%d",
                            len(answer),
                            len(repaired),
                        )
                        return repaired_answer
                    if _profiler is not None:
                        pre_validation_meta = pre_validation.to_dict()
                        pre_validation_meta["post_repair_validation"] = post_validation.to_dict()
                        pre_validation_meta["judge_escalated"] = True
                        pre_validation_meta["repair_rejected"] = True
                        pre_validation_meta["rejection_reason"] = repair_decision["reason"]
                        _profiler.set_attribute(
                            "evidence_answer_validator",
                            pre_validation_meta,
                        )
                        pre_coverage_meta = pre_coverage.to_dict()
                        pre_coverage_meta["post_repair_coverage"] = post_coverage.to_dict()
                        pre_coverage_meta["repair_rejected"] = True
                        pre_coverage_meta["rejection_reason"] = repair_decision["reason"]
                        _profiler.set_attribute("answer_coverage_validator", pre_coverage_meta)
                        pre_value_conflict_meta = pre_value_conflict.to_dict()
                        pre_value_conflict_meta["post_repair_value_conflict"] = post_value_conflict.to_dict()
                        pre_value_conflict_meta["repair_rejected"] = True
                        pre_value_conflict_meta["rejection_reason"] = repair_decision["reason"]
                        _profiler.set_attribute(
                            "answer_value_conflict_validator",
                            pre_value_conflict_meta,
                        )
                    logger.info(
                        "main_judge_repair_rejected reason=%s original_len=%d repaired_len=%d",
                        repair_decision["reason"],
                        len(answer),
                        len(repaired),
                    )
                    return answer
            except (asyncio.TimeoutError, LLMServiceError) as exc:
                logger.warning("main_judge_repair_failed reason=%s", type(exc).__name__)

        # Fallback: return original answer
        return answer

    async def _apply_final_quality_gate(
        self,
        *,
        query: str,
        answer: str,
        llm_profile: str | None = None,
    ) -> str:
        """Run the shared bad-token gate after all judge/repair steps."""
        from src.orchestrators.response_utils import clean_final_answer
        from src.quality.answer_filter import (
            REWRITE_ONLY_SYSTEM_SUFFIX,
            check_answer_quality,
            quality_issue_blocks_answer,
        )

        cleaned = clean_final_answer(answer)
        quality = check_answer_quality(cleaned)
        if not quality.needs_rewrite:
            return cleaned

        repair_prompt = (
            f"Kullanici sorusu:\n{query}\n\n"
            f"Cevap:\n{cleaned}\n\n"
            "Cevabi ayni bilgileri koruyarak dogal Turkce ile yeniden yaz. "
            "Sayi, tarih, ucret, AKTS ve kaynakta gecen kosullari degistirme."
        )
        try:
            with profile_stage("main.final_quality_repair"):
                repaired = await asyncio.wait_for(
                    self.llm_service.generate(
                        prompt=repair_prompt,
                        system=MULTI_DEPARTMENT_SYNTHESIS_SYSTEM_PROMPT + REWRITE_ONLY_SYSTEM_SUFFIX,
                        model_role="final_refinement",
                        llm_profile=llm_profile,
                    ),
                    timeout=_GLOBAL_SYNTHESIS_TIMEOUT_SECONDS,
                )
        except (asyncio.TimeoutError, LLMServiceError) as exc:
            logger.warning("final_quality_repair_failed reason=%s", type(exc).__name__)
            if not quality_issue_blocks_answer(quality):
                logger.warning(
                    "final_quality_gate_tolerated_minor_issue bad_tokens=%s issues=%s",
                    quality.bad_tokens,
                    quality.detected_issues,
                )
                return cleaned
            return TEMPORARY_SYNTHESIS_FAILURE_ANSWER

        repaired_answer = clean_final_answer(str(repaired or "").strip())
        repaired_quality = check_answer_quality(repaired_answer)
        if repaired_answer and not repaired_quality.needs_rewrite:
            return repaired_answer
        if repaired_answer and not quality_issue_blocks_answer(repaired_quality):
            logger.warning(
                "final_quality_gate_tolerated_repaired_minor_issue bad_tokens=%s issues=%s",
                repaired_quality.bad_tokens,
                repaired_quality.detected_issues,
            )
            return repaired_answer
        logger.warning(
            "final_quality_gate_rejected bad_tokens=%s repaired_bad_tokens=%s",
            quality.bad_tokens,
            repaired_quality.bad_tokens,
        )
        return TEMPORARY_SYNTHESIS_FAILURE_ANSWER

    @staticmethod
    def _judge_repair_decision(
        *,
        pre_validation: AnswerValidationResult,
        post_validation: AnswerValidationResult,
        pre_coverage: dict,
        post_coverage: dict,
        pre_value_conflict: dict,
        post_value_conflict: dict,
    ) -> dict[str, object]:
        """Accept a judge repair only when it does not degrade guardrail signals."""
        if _status_severity(post_validation.status) > _status_severity(pre_validation.status):
            return {
                "accepted": False,
                "outcome": "rejected_worse",
                "reason": "evidence_validation_worsened",
            }
        if _status_severity(str(post_coverage.get("status") or "skipped")) > _status_severity(
            str(pre_coverage.get("status") or "skipped")
        ):
            return {
                "accepted": False,
                "outcome": "rejected_worse",
                "reason": "answer_coverage_worsened",
            }
        if _status_severity(str(post_value_conflict.get("status") or "skipped")) > _status_severity(
            str(pre_value_conflict.get("status") or "skipped")
        ):
            return {
                "accepted": False,
                "outcome": "rejected_worse",
                "reason": "answer_value_conflict_worsened",
            }

        preserved_before = _preserved_required_values(pre_validation)
        missing_after = set(post_validation.missing_values)
        if preserved_before & missing_after:
            return {
                "accepted": False,
                "outcome": "rejected_worse",
                "reason": "repair_lost_previously_preserved_required_value",
            }

        if post_validation.status == "fail" and pre_validation.status != "fail":
            return {
                "accepted": False,
                "outcome": "rejected_worse",
                "reason": "repair_failed_validation",
            }

        improved = (
            _status_severity(post_validation.status) < _status_severity(pre_validation.status)
            or _status_severity(str(post_coverage.get("status") or "skipped"))
            < _status_severity(str(pre_coverage.get("status") or "skipped"))
            or _status_severity(str(post_value_conflict.get("status") or "skipped"))
            < _status_severity(str(pre_value_conflict.get("status") or "skipped"))
        )
        return {
            "accepted": True,
            "outcome": "accepted_improved" if improved else "accepted_neutral",
            "reason": "repair_improved" if improved else "repair_not_worse",
        }
