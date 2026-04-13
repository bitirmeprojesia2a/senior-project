"""Main query orchestrator."""

from __future__ import annotations

import asyncio
import logging
from time import perf_counter
from uuid import uuid4

from src.agents.announcement import AnnouncementAgent
from src.core.config import settings
from src.core.messages import CONTACT_SUGGESTION
from src.core.profiling import get_current_profiler, profile_stage
from src.core.text_normalization import normalize_text
from src.db.conversation_context import ConversationContextService, ConversationResolution
from src.db.schemas import DepartmentResponse, UserQueryResponse
from src.db.telemetry import TelemetryService, build_main_orchestrator_identity
from src.llm.llm_service import LLMService, LLMServiceError
from src.llm.prompt_templates import MULTI_DEPARTMENT_SYNTHESIS_SYSTEM_PROMPT
from src.orchestrators.announcement_utils import (
    build_announcement_response,
    request_announcement_response,
)
from src.orchestrators.defaults import build_default_orchestrators
from src.orchestrators.department_dispatch import dispatch_to_departments
from src.orchestrators.query_policy import (
    ACADEMIC_DEPARTMENT_CLARIFICATION_MESSAGE,
    CLARIFICATION_MESSAGE,
    looks_like_announcement_query,
    requires_academic_department_clarification,
    should_fetch_related_announcements,
    should_use_global_synthesis,
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

_GLOBAL_SYNTHESIS_TIMEOUT_SECONDS = settings.llm.global_synthesis_timeout_seconds

logger = logging.getLogger(__name__)

_ACK_ONLY_RESPONSES = {
    "tesekkur": "Rica ederim. Baska bir sorunuz olursa yazabilirsiniz.",
    "sagol": "Rica ederim. Baska bir sorunuz olursa yazabilirsiniz.",
    "evet": "Hazirim. Devam etmemi istediginiz konuyu biraz daha acik yazabilirsiniz.",
    "tamam": "Hazirim. Devam etmemi istediginiz konuyu biraz daha acik yazabilirsiniz.",
    "anladim": "Hazirim. Devam etmemi istediginiz konuyu biraz daha acik yazabilirsiniz.",
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
        telemetry_service: TelemetryService | None = None,
        llm_service: LLMService | None = None,
        conversation_service: ConversationContextService | None = None,
    ) -> None:
        self.router = router or DepartmentRouter()
        self.telemetry_service = telemetry_service or TelemetryService()
        self.department_orchestrators = department_orchestrators or build_default_orchestrators(
            self.telemetry_service
        )
        self.announcement_agent = announcement_agent or AnnouncementAgent()
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
    ) -> UserQueryResponse:
        start_time = perf_counter()
        context_id = context_id or str(uuid4())
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

        query_log_id = None
        try:
            with profile_stage("main.handle_query", context_id=context_id):
                if self.conversation_service is not None:
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

                acknowledgement_message = self._resolve_acknowledgement_message(query)
                if acknowledgement_message is not None and not conversation_resolution.is_follow_up:
                    response_time_ms = round((perf_counter() - start_time) * 1000, 2)
                    return build_clarification_user_response(
                        context_id=context_id,
                        message=acknowledgement_message,
                        response_time_ms=response_time_ms,
                        full_name=student_full_name,
                    )

                effective_query = conversation_resolution.effective_query
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
                        }
                    profiler.set_attribute("routing", routing_attrs)
                with profile_stage("main.telemetry.create_query_log"):
                    query_log_id = await self.telemetry_service.create_query_log(
                        query_text=query,
                        routing=routing,
                        orchestrator=build_main_orchestrator_identity(),
                        context_id=context_id,
                        user_id=user_id,
                        student_id=student_id,
                    )

                if routing.strategy.name == "CLARIFICATION" and not routing.departments:
                    if looks_like_announcement_query(effective_query):
                        with profile_stage("main.announcement_only_response"):
                            return await build_announcement_response(
                                announcement_agent=self.announcement_agent,
                                telemetry_service=self.telemetry_service,
                                query=effective_query,
                                context_id=context_id,
                                start_time=start_time,
                                query_log_id=query_log_id,
                                routing_reasoning=routing.reasoning,
                                task_type=routing.task_type,
                                faculty=student_faculty,
                            )
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
                }

                with profile_stage("main.dispatch_departments"):
                    department_responses = await dispatch_to_departments(
                        department_orchestrators=self.department_orchestrators,
                        query=effective_query,
                        context_id=context_id,
                        routing=routing,
                        metadata=metadata,
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
                    with profile_stage("main.fallback_announcement"):
                        fallback = await request_announcement_response(
                            announcement_agent=self.announcement_agent,
                            telemetry_service=self.telemetry_service,
                            query=effective_query,
                            context_id=context_id,
                            routing_reason=routing.reasoning,
                            query_log_id=query_log_id,
                            task_type=routing.task_type,
                            faculty=student_faculty,
                        )
                        responses.append(fallback)
                else:
                    announcement_response = None
                    if should_fetch_related_announcements(effective_query):
                        with profile_stage("main.related_announcements"):
                            announcement_response = await request_announcement_response(
                                announcement_agent=self.announcement_agent,
                                telemetry_service=self.telemetry_service,
                                query=effective_query,
                                context_id=context_id,
                                routing_reason=routing.reasoning,
                                query_log_id=query_log_id,
                                task_type=routing.task_type,
                                departments=[
                                    department.value for department in routing.departments
                                ],
                                faculty=student_faculty,
                                allow_latest_fallback=False,
                            )
                    if announcement_response is not None and announcement_response.sources:
                        responses.append(announcement_response)

                with profile_stage("main.filter_low_confidence"):
                    filtered_responses = filter_low_confidence_responses(responses)
                    filtered_departments = filter_low_confidence_responses(
                        list(department_responses)
                    )

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
                active_topic=conversation_resolution.active_topic,
            )
        except Exception as exc:
            logger.warning("conversation_turn_record_skipped reason=%s", type(exc).__name__)

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

        synthesized = await self._synthesize_department_answers(
            query=query,
            responses=responses,
            llm_profile=llm_profile,
        )
        if not synthesized:
            return self._compose_answers(responses), False

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

        selected_model = settings.resolve_llm_model(
            role="global_synthesis",
            profile=llm_profile,
        )
        logger.info(
            "global_llm_synthesis_start timeout_s=%s prompt_chars=%s departments=%s model=%s profile=%s",
            _GLOBAL_SYNTHESIS_TIMEOUT_SECONDS,
            len(prompt) + len(MULTI_DEPARTMENT_SYNTHESIS_SYSTEM_PROMPT),
            [response.department.value for response in meaningful],
            selected_model,
            llm_profile or settings.normalize_llm_profile(settings.llm.profile),
        )
        try:
            with profile_stage("main.global_llm_synthesis"):
                return await asyncio.wait_for(
                    self.llm_service.generate(
                        prompt=prompt,
                        system=MULTI_DEPARTMENT_SYNTHESIS_SYSTEM_PROMPT,
                        model_role="global_synthesis",
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
