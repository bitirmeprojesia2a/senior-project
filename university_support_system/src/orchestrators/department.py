"""Department orchestrator implementation."""

from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Iterable

from a2a.types import Task

from src.a2a import build_agent_response_task, extract_department_response
from src.a2a.tracing import child_trace_metadata, ensure_trace_metadata
from src.a2a.specialist_transport import SpecialistTransport, build_specialist_transport
from src.agents.base import BaseSpecialistAgent
from src.core.constants import Department, TaskType
from src.core.profiling import profile_stage
from src.core.text_normalization import normalize_text
from src.db.schemas import DepartmentResponse
from src.db.telemetry import (
    TelemetryService,
    build_department_orchestrator_identity,
    build_specialist_agent_identity,
)
from src.orchestrators.department_factories import (
    build_academic_programs_orchestrator,
    build_finance_orchestrator,
    build_student_affairs_orchestrator,
)

from src.orchestrators.department_task_utils import (
    build_request_task,
    build_specialist_task,
    extract_query_from_task,
)


@dataclass
class DepartmentOrchestrator:
    """Dispatches work to specialist agents within a department."""

    department: Department
    agents: dict[TaskType, BaseSpecialistAgent]
    fallback_agent: BaseSpecialistAgent
    keyword_routing: dict[str, str] = field(default_factory=dict)
    agents_by_id: dict[str, BaseSpecialistAgent] = field(default_factory=dict)
    telemetry_service: TelemetryService | None = None
    specialist_transport: SpecialistTransport = field(default_factory=build_specialist_transport)

    async def handle(
        self,
        *,
        query_text: str,
        context_id: str,
        task_type: TaskType | None = None,
        metadata: dict | None = None,
    ) -> DepartmentResponse:
        request_task = self._build_request_task(
            query_text=query_text,
            context_id=context_id,
            task_type=task_type,
            metadata=metadata,
        )
        response_task = await self.handle_task(
            request_task,
            task_type=task_type,
            metadata=metadata,
        )
        response = extract_department_response(response_task)
        if response is None:
            raise ValueError(
                f"{self.department.value} orchestrator gecerli department response dondurmedi."
            )
        return response

    async def handle_task(
        self,
        task: Task,
        *,
        task_type: TaskType | None = None,
        metadata: dict | None = None,
    ) -> Task:
        with profile_stage(
            "department.handle",
            department=self.department.value,
            task_type=task_type.value if task_type else None,
        ):
            merged_metadata = dict(task.metadata or {})
            if metadata:
                merged_metadata.update(metadata)
            merged_metadata = ensure_trace_metadata(merged_metadata)
            query_text = str(merged_metadata.get("query_text", "")).strip() or extract_query_from_task(task)
            with profile_stage("department.select_agent", department=self.department.value):
                agent = self._select_agent(task_type, query_text)
            specialist_metadata = child_trace_metadata(merged_metadata)
            payload, specialist_task = build_specialist_task(
                query_text=query_text,
                context_id=task.contextId,
                task_type=task_type,
                metadata=specialist_metadata,
            )
            agent_started: float | None = None
            agent_latency_ms: float | None = None
            try:
                with profile_stage(
                    "department.agent_handle_task",
                    department=self.department.value,
                    agent_id=agent.agent_id,
                ):
                    agent_started = perf_counter()
                    agent_response_task = await self.specialist_transport.dispatch(
                        agent=agent,
                        task=specialist_task,
                    )
                    agent_latency_ms = round((perf_counter() - agent_started) * 1000, 2)
                    response = extract_department_response(agent_response_task)
                    if response is None:
                        raise ValueError(
                            f"{agent.agent_id} gecerli department response metadata'si dondurmedi."
                        )
                    # Başarısız specialist yanıtı (A2A hatası) — fallback dene
                    if not response.success and response.error and _is_transport_error(response.error):
                        logger.warning(
                            "department_a2a_failed department=%s agent=%s error=%s, attempting RAG fallback",
                            self.department.value, agent.agent_id, response.error[:100],
                        )
                        fallback_meta = _extract_transport_diagnostics(response)
                        await self._record_agent_task(
                            agent=agent,
                            task_id=agent_response_task.id,
                            query_log_id=merged_metadata.get("query_log_id"),
                            task_type=task_type,
                            payload=payload.to_metadata(),
                            response=response,
                            latency_ms=agent_latency_ms,
                        )
                        fallback_response = await self._try_rag_fallback(
                            agent=agent,
                            query_text=query_text,
                            error_msg=response.error,
                            metadata=merged_metadata,
                        )
                        if fallback_response is not None:
                            fallback_meta["fallback_from_error"] = True
                            return build_agent_response_task(
                                fallback_response,
                                request_task=task,
                                emitter_id=f"{self.department.value}_orchestrator",
                                emitter_name=f"{self.department.value} Orchestrator",
                                metadata={"selected_agent_id": agent.agent_id, **fallback_meta},
                            )
                        # Fallback de başarısız — orijinal failed response'u dön
                await self._record_agent_task(
                    agent=agent,
                    task_id=agent_response_task.id,
                    query_log_id=merged_metadata.get("query_log_id"),
                    task_type=task_type,
                    payload=payload.to_metadata(),
                    response=response,
                    latency_ms=agent_latency_ms,
                )
                return build_agent_response_task(
                    response,
                    request_task=task,
                    emitter_id=f"{self.department.value}_orchestrator",
                    emitter_name=f"{self.department.value} Orchestrator",
                    metadata={"selected_agent_id": agent.agent_id},
                )
            except Exception as exc:
                if agent_latency_ms is None and agent_started is not None:
                    agent_latency_ms = round((perf_counter() - agent_started) * 1000, 2)
                await self._record_agent_task(
                    agent=agent,
                    task_id=str(specialist_task.id),
                    query_log_id=merged_metadata.get("query_log_id"),
                    task_type=task_type,
                    payload=payload.to_metadata(),
                    response=None,
                    error_msg=str(exc),
                    latency_ms=agent_latency_ms,
                )
                # Fallback: uzman ajan hatası durumunda kaynaklı RAG cevabı dene
                # Hassas sorgularda (kişisel veri, ödeme) fallback yapma
                fallback_response = await self._try_rag_fallback(
                    agent=agent,
                    query_text=query_text,
                    error_msg=str(exc),
                    metadata=merged_metadata,
                )
                if fallback_response is not None:
                    return build_agent_response_task(
                        fallback_response,
                        request_task=task,
                        emitter_id=f"{self.department.value}_orchestrator",
                        emitter_name=f"{self.department.value} Orchestrator",
                        metadata={
                            "selected_agent_id": agent.agent_id,
                            "fallback_from_error": True,
                            "original_error": str(exc)[:200],
                        },
                    )
                raise

    async def handle_a2a(
        self,
        *,
        query_text: str,
        context_id: str,
        task_type: TaskType | None = None,
        metadata: dict | None = None,
    ) -> Task:
        """Backward-compatible alias that returns an A2A response task."""
        request_task = self._build_request_task(
            query_text=query_text,
            context_id=context_id,
            task_type=task_type,
            metadata=metadata,
        )
        return await self.handle_task(request_task, task_type=task_type, metadata=metadata)

    @staticmethod
    def _build_request_task(
        *,
        query_text: str,
        context_id: str,
        task_type: TaskType | None,
        metadata: dict | None,
    ) -> Task:
        return build_request_task(
            query_text=query_text,
            context_id=context_id,
            task_type=task_type,
            metadata=metadata,
        )

    async def _record_agent_task(
        self,
        *,
        agent: BaseSpecialistAgent,
        task_id: str,
        query_log_id: int | None,
        task_type: TaskType | None,
        payload: dict,
        response: DepartmentResponse | None,
        error_msg: str | None = None,
        latency_ms: float | None = None,
    ) -> None:
        if self.telemetry_service is None:
            return

        stage_name = (
            "department.telemetry.record_success"
            if error_msg is None
            else "department.telemetry.record_error"
        )
        with profile_stage(stage_name, department=self.department.value):
            await self.telemetry_service.record_agent_task(
                task_id=task_id,
                query_log_id=query_log_id,
                sender=build_department_orchestrator_identity(self.department),
                receiver=build_specialist_agent_identity(agent),
                task_type=task_type,
                payload=payload,
                response=response,
                error_msg=error_msg,
                latency_ms=latency_ms,
            )

    def _select_agent(
        self,
        task_type: TaskType | None,
        query_text: str = "",
    ) -> BaseSpecialistAgent:
        if query_text and self.keyword_routing and self.agents_by_id:
            lowered = _normalize_text(query_text)
            for keyword, agent_id in _iter_keyword_routes(self.keyword_routing):
                normalized_keyword = _normalize_text(keyword)
                if normalized_keyword and normalized_keyword in lowered:
                    matched = self.agents_by_id.get(agent_id)
                    if matched is not None:
                        return matched

        if task_type is not None:
            agent = self.agents.get(task_type)
            if agent is not None:
                return agent

        return self.fallback_agent

    async def _try_rag_fallback(
        self,
        *,
        agent: BaseSpecialistAgent,
        query_text: str,
        error_msg: str,
        metadata: dict,
    ) -> DepartmentResponse | None:
        """Uzman ajan hatası durumunda kaynaklı RAG cevabı dene.

        Hassas sorgularda (kişisel veri, ödeme) fallback yapma.
        Sadece güvenli read-only/procedure/RAG sorgularında uygula.
        """
        # Hassas sorgu tiplerinde fallback yapma
        from src.routing.routing_policy import looks_like_personal_data_query, has_payment_markers
        normalized = normalize_text(query_text)
        if looks_like_personal_data_query(query_text) or has_payment_markers(normalized):
            logger.info(
                "rag_fallback_skipped_sensitive department=%s agent=%s",
                self.department.value, agent.agent_id,
            )
            return None

        # Sadece A2A transport/internal hatalarında fallback dene
        # Kullanıcı kaynaklı hatalarda (validation vb.) fallback gereksiz
        if not _is_transport_error(error_msg):
            return None

        try:
            retriever = agent._get_retriever()
            results = retriever.search(
                query_text,
                top_k=agent._search_top_k(query_text, metadata),
            )
            if not results:
                return None

            answer, gen_mode = await agent._generate_answer(
                query_text,
                results,
                allow_llm=False,  # source-only, LLM sentez yok
            )
            response = agent._build_department_response(
                answer=answer,
                results=results,
                generation_mode=f"rag_fallback:{gen_mode}",
                success=True,
            )
            # Fallback metadata ekle (sources korunmuş olur)
            response.metadata = dict(response.metadata or {})
            response.metadata["fallback"] = True
            response.metadata["original_error"] = error_msg[:200]
            return response
        except Exception as fallback_exc:
            logger.warning(
                "rag_fallback_failed department=%s agent=%s error=%s",
                self.department.value, agent.agent_id, fallback_exc,
            )
            return None


def _normalize_text(text: str) -> str:
    return normalize_text(text)


_TRANSPORT_ERROR_MARKERS = ("a2a_", "transport", "timeout", "connection", "EvidenceItem")


def _is_transport_error(error_msg: str) -> bool:
    """Hata mesajı A2A transport/internal kaynaklı mı?"""
    return any(marker in error_msg for marker in _TRANSPORT_ERROR_MARKERS)


def _extract_transport_diagnostics(response: DepartmentResponse) -> dict:
    """Başarısız response'tan transport diagnostic metadata çıkar."""
    meta = dict(response.metadata or {})
    diag: dict[str, str | int | None] = {
        "original_error": (response.error or "")[:200],
    }
    for key in ("detail", "endpoint", "attempt", "timeout_seconds", "http_status", "circuit_state", "error_code"):
        if key in meta:
            diag[f"transport_{key}"] = meta[key]
    return diag


def _iter_keyword_routes(keyword_routing: dict[str, str]) -> list[tuple[str, str]]:
    ranked_routes: list[tuple[int, int, int, str, str]] = []
    for index, (keyword, agent_id) in enumerate(keyword_routing.items()):
        normalized_keyword = _normalize_text(keyword)
        ranked_routes.append(
            (
                -len(normalized_keyword.split()),
                -len(normalized_keyword),
                index,
                keyword,
                agent_id,
            )
        )
    ranked_routes.sort()
    return [(keyword, agent_id) for _, _, _, keyword, agent_id in ranked_routes]


__all__ = [
    "DepartmentOrchestrator",
    "build_student_affairs_orchestrator",
    "build_academic_programs_orchestrator",
    "build_finance_orchestrator",
]
