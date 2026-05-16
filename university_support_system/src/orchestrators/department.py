"""Department orchestrator implementation."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any

from a2a.types import Task

from src.a2a import build_agent_response_task, extract_department_response
from src.a2a.tracing import child_trace_metadata, ensure_trace_metadata
from src.a2a.specialist_transport import SpecialistTransport, build_specialist_transport
from src.agents.base import BaseSpecialistAgent
from src.core.constants import Department, TaskType
from src.core.profiling import get_current_profiler, profile_stage
from src.core.retrieval_execution_policy import resolve_retrieval_execution_policy
from src.core.source_ownership import (
    OWNER_STUDENT_AFFAIRS_POLICY,
)
from src.core.specialist_ownership import (
    SpecialistOwnershipDecision,
    resolve_specialist_owner,
)
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

logger = logging.getLogger(__name__)

SPECIALIST_SELECTION_SCHEMA = "omu.specialist_selection.v1"

_SEMANTIC_SKIP_KEYS = frozenset(
    {
        "query",
        "original_query",
        "resolved_query",
        "original",
        "effective",
        "normalized",
    }
)
_SELECTOR_DECISION_SKIP_KEYS = _SEMANTIC_SKIP_KEYS | frozenset(
    {
        "avoid_sources",
        "collections_fallback",
        "collections_primary",
        "evidence",
        "evidence_contract",
        "fallback_route",
        "file_name",
        "legacy_routing",
        "producer_trace",
        "reasoning",
        "source",
        "source_hints",
        "source_owner",
        "source_refs",
        "source_url",
        "sources",
        "title",
        "top_sources",
        "preferred_sources",
    }
)
_SELECTOR_DECISION_KEYS = frozenset(
    {
        "active_topic",
        "answer_contract",
        "capabilities",
        "capability",
        "frame",
        "intent",
        "missing",
        "missing_params",
        "missing_slots",
        "must_answer",
        "params",
        "primary",
        "primary_intent",
        "question_type",
        "required",
        "required_slots",
        "secondary",
        "selected",
        "slots",
        "standalone_query",
        "task_type_hint",
        "task_type",
        "topic",
    }
)

@dataclass(frozen=True)
class _AgentSelectionCandidate:
    agent: BaseSpecialistAgent
    selected_by: str
    reason: str
    registry_decision: SpecialistOwnershipDecision | None = None


@dataclass(frozen=True)
class _AgentSelectionDecision:
    department: Department
    agent: BaseSpecialistAgent
    selected_by: str
    reason: str
    signals: dict[str, Any] = field(default_factory=dict)
    contract_agent_id: str | None = None
    contract_reason: str | None = None
    task_type_agent_id: str | None = None
    task_type_reason: str | None = None
    legacy_agent_id: str | None = None
    legacy_reason: str | None = None
    fallback_agent_id: str | None = None
    registry_decision: SpecialistOwnershipDecision | None = None

    def to_metadata(self) -> dict[str, Any]:
        legacy_match = None
        if self.legacy_agent_id is not None:
            legacy_match = self.legacy_agent_id == self.agent.agent_id
        return {
            "schema": SPECIALIST_SELECTION_SCHEMA,
            "mode": "contract_registry_keyword_fallback",
            "department": self.department.value,
            "selected_agent_id": self.agent.agent_id,
            "selected_by": self.selected_by,
            "reason": self.reason,
            "signals": {
                key: value
                for key, value in self.signals.items()
                if value not in (None, "", [])
            },
            "contract": {
                "agent_id": self.contract_agent_id,
                "reason": self.contract_reason,
            },
            "registry": (
                self.registry_decision.to_dict()
                if self.registry_decision is not None
                else None
            ),
            "task_type": {
                "agent_id": self.task_type_agent_id,
                "reason": self.task_type_reason,
            },
            "legacy_keyword": {
                "agent_id": self.legacy_agent_id,
                "reason": self.legacy_reason,
                "matches_selected": legacy_match,
                "used_as_fallback": self.selected_by == "legacy_keyword_fallback",
            },
            "fallback_agent_id": self.fallback_agent_id,
        }


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
                selection = self._select_agent_decision(
                    task_type,
                    query_text,
                    metadata=merged_metadata,
                )
                selection_metadata = selection.to_metadata()
                profiler = get_current_profiler()
                if profiler is not None:
                    profiler.append_attribute_list("specialist_selection", selection_metadata)
                agent = selection.agent
            specialist_metadata = child_trace_metadata(merged_metadata)
            specialist_metadata["specialist_selection"] = selection_metadata
            payload, specialist_task = build_specialist_task(
                query_text=query_text,
                context_id=task.contextId,
                task_type=task_type,
                metadata=specialist_metadata,
            )
            telemetry_payload = payload.to_metadata()
            telemetry_payload["specialist_selection"] = selection_metadata
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
                        if _is_transport_timeout_error(response.error):
                            logger.warning(
                                "department_a2a_timeout_no_rag_fallback department=%s agent=%s error=%s",
                                self.department.value,
                                agent.agent_id,
                                response.error[:100],
                            )
                            response.metadata = dict(response.metadata or {})
                            response.metadata["fallback_skipped_reason"] = "transport_timeout"
                            response.metadata["branch_timeout"] = True
                            await self._record_agent_task(
                                agent=agent,
                                task_id=agent_response_task.id,
                                query_log_id=merged_metadata.get("query_log_id"),
                                task_type=task_type,
                                payload=telemetry_payload,
                                response=response,
                                latency_ms=agent_latency_ms,
                            )
                            return build_agent_response_task(
                                response,
                                request_task=task,
                                emitter_id=f"{self.department.value}_orchestrator",
                                emitter_name=f"{self.department.value} Orchestrator",
                                metadata={
                                    "selected_agent_id": agent.agent_id,
                                    "specialist_selection": selection_metadata,
                                    "fallback_skipped_reason": "transport_timeout",
                                    "branch_timeout": True,
                                },
                            )
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
                            payload=telemetry_payload,
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
                                metadata={
                                    "selected_agent_id": agent.agent_id,
                                    "specialist_selection": selection_metadata,
                                    **fallback_meta,
                                },
                            )
                        # Fallback de başarısız — orijinal failed response'u dön
                await self._record_agent_task(
                    agent=agent,
                    task_id=agent_response_task.id,
                    query_log_id=merged_metadata.get("query_log_id"),
                    task_type=task_type,
                    payload=telemetry_payload,
                    response=response,
                    latency_ms=agent_latency_ms,
                )
                return build_agent_response_task(
                    response,
                    request_task=task,
                    emitter_id=f"{self.department.value}_orchestrator",
                    emitter_name=f"{self.department.value} Orchestrator",
                    metadata={
                        "selected_agent_id": agent.agent_id,
                        "specialist_selection": selection_metadata,
                    },
                )
            except Exception as exc:
                if agent_latency_ms is None and agent_started is not None:
                    agent_latency_ms = round((perf_counter() - agent_started) * 1000, 2)
                await self._record_agent_task(
                    agent=agent,
                    task_id=str(specialist_task.id),
                    query_log_id=merged_metadata.get("query_log_id"),
                    task_type=task_type,
                    payload=telemetry_payload,
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
                            "specialist_selection": selection_metadata,
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
        metadata: dict | None = None,
    ) -> BaseSpecialistAgent:
        return self._select_agent_decision(
            task_type,
            query_text,
            metadata=metadata,
        ).agent

    def _select_agent_decision(
        self,
        task_type: TaskType | None,
        query_text: str = "",
        metadata: dict | None = None,
    ) -> _AgentSelectionDecision:
        metadata = metadata or {}
        contract_candidate = self._select_contract_agent(metadata=metadata)
        task_type_candidate = self._select_task_type_agent(task_type)
        legacy_candidate = self._select_legacy_keyword_agent(query_text)

        if contract_candidate is not None:
            selected = contract_candidate
        elif task_type_candidate is not None:
            selected = _AgentSelectionCandidate(
                agent=task_type_candidate.agent,
                selected_by="task_type",
                reason=task_type_candidate.reason,
            )
        elif legacy_candidate is not None:
            selected = _AgentSelectionCandidate(
                agent=legacy_candidate.agent,
                selected_by="legacy_keyword_fallback",
                reason=legacy_candidate.reason,
            )
        else:
            selected = _AgentSelectionCandidate(
                agent=self.fallback_agent,
                selected_by="fallback",
                reason="no_contract_task_type_or_keyword_candidate",
            )

        return _AgentSelectionDecision(
            department=self.department,
            agent=selected.agent,
            selected_by=selected.selected_by,
            reason=selected.reason,
            signals={
                "capability": _extract_contract_capability(metadata),
                "source_owner": _extract_contract_source_owner(metadata),
                "task_type": task_type.value if task_type else None,
            },
            contract_agent_id=(
                contract_candidate.agent.agent_id if contract_candidate is not None else None
            ),
            contract_reason=contract_candidate.reason if contract_candidate is not None else None,
            task_type_agent_id=(
                task_type_candidate.agent.agent_id if task_type_candidate is not None else None
            ),
            task_type_reason=task_type_candidate.reason if task_type_candidate is not None else None,
            legacy_agent_id=legacy_candidate.agent.agent_id if legacy_candidate is not None else None,
            legacy_reason=legacy_candidate.reason if legacy_candidate is not None else None,
            fallback_agent_id=self.fallback_agent.agent_id,
            registry_decision=(
                contract_candidate.registry_decision if contract_candidate is not None else None
            ),
        )

    def _select_contract_agent(
        self,
        *,
        metadata: dict,
    ) -> _AgentSelectionCandidate | None:
        capability = _extract_contract_capability(metadata)
        source_owner = _extract_contract_source_owner(metadata)
        semantic_text = _contract_semantic_text(metadata)
        candidate = self._contract_candidate_from_registry(
            capability=capability,
            source_owner=source_owner,
            semantic_text=semantic_text,
        )
        if candidate is not None:
            return candidate

        candidate = self._contract_candidate_from_source_owner(
            source_owner=source_owner,
            semantic_text=semantic_text,
        )
        if candidate is not None:
            return candidate
        return None

    def _contract_candidate_from_registry(
        self,
        *,
        capability: str | None,
        source_owner: str | None,
        semantic_text: str,
    ) -> _AgentSelectionCandidate | None:
        decision = resolve_specialist_owner(
            department=self.department,
            capability=capability,
            source_owner=source_owner,
            semantic_text=semantic_text,
        )
        if decision is None:
            return None
        return self._candidate_from_agent_id(
            decision.agent_id,
            selected_by="contract",
            reason=decision.reason,
            registry_decision=decision,
        )

    def _contract_candidate_from_source_owner(
        self,
        *,
        source_owner: str | None,
        semantic_text: str,
    ) -> _AgentSelectionCandidate | None:
        owner_key = _selector_value(source_owner)
        if not owner_key:
            return None

        agent_id: str | None = None
        reason = f"source_owner:{owner_key}"
        if self.department is Department.STUDENT_AFFAIRS and owner_key == OWNER_STUDENT_AFFAIRS_POLICY:
            agent_id = "registration_agent"

        return self._candidate_from_agent_id(
            agent_id,
            selected_by="contract",
            reason=reason,
        )

    def _select_task_type_agent(
        self,
        task_type: TaskType | None,
    ) -> _AgentSelectionCandidate | None:
        if task_type is None:
            return None
        agent = self.agents.get(task_type)
        if agent is None:
            return None
        return _AgentSelectionCandidate(
            agent=agent,
            selected_by="task_type",
            reason=f"task_type:{task_type.value}",
        )

    def _select_legacy_keyword_agent(self, query_text: str) -> _AgentSelectionCandidate | None:
        if query_text and self.keyword_routing and self.agents_by_id:
            lowered = _normalize_text(query_text)
            for keyword, agent_id in _iter_keyword_routes(self.keyword_routing):
                normalized_keyword = _normalize_text(keyword)
                if normalized_keyword and normalized_keyword in lowered:
                    matched = self.agents_by_id.get(agent_id)
                    if matched is not None:
                        return _AgentSelectionCandidate(
                            agent=matched,
                            selected_by="legacy_keyword",
                            reason=f"keyword:{keyword}",
                        )
        return None

    def _candidate_from_agent_id(
        self,
        agent_id: str | None,
        *,
        selected_by: str,
        reason: str,
        registry_decision: SpecialistOwnershipDecision | None = None,
    ) -> _AgentSelectionCandidate | None:
        if not agent_id:
            return None
        agent = self.agents_by_id.get(agent_id)
        if agent is None:
            return None
        return _AgentSelectionCandidate(
            agent=agent,
            selected_by=selected_by,
            reason=reason,
            registry_decision=registry_decision,
        )

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
        if _is_transport_timeout_error(error_msg):
            logger.info(
                "rag_fallback_skipped_timeout department=%s agent=%s",
                self.department.value,
                agent.agent_id,
            )
            return None

        try:
            retriever = agent._get_retriever()
            retrieval_policy = resolve_retrieval_execution_policy(
                department=self.department,
                branch_role=str(metadata.get("branch_role") or "").strip() or None,
                metadata=metadata,
            )
            results = retriever.search(
                query_text,
                top_k=retrieval_policy.top_k or agent._search_top_k(query_text, metadata),
                department=self.department,
                source_owner=_extract_contract_source_owner(metadata),
                reranker_candidate_limit=retrieval_policy.reranker_candidate_limit,
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


def _selector_value(value: Any) -> str | None:
    text = str(value or "").strip().lower()
    return text or None


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _extract_contract_capability(metadata: dict[str, Any] | None) -> str | None:
    metadata = metadata or {}
    planner = _as_dict(metadata.get("capability_planner"))
    action = _as_dict(planner.get("action"))
    capability = action.get("capability") or planner.get("capability")
    if capability:
        return _selector_value(capability)

    resolved = _as_dict(metadata.get("resolved_decision"))
    if resolved.get("capability"):
        return _selector_value(resolved.get("capability"))

    contract = _decision_contract_body(metadata)
    capabilities = _as_dict(contract.get("capabilities"))
    capability = capabilities.get("selected")
    return _selector_value(capability)


def _extract_contract_source_owner(metadata: dict[str, Any] | None) -> str | None:
    metadata = metadata or {}
    source_owner = _as_dict(metadata.get("source_owner"))
    owner = source_owner.get("primary")
    if owner:
        return _selector_value(owner)

    resolved = _as_dict(metadata.get("resolved_decision"))
    if resolved.get("source_owner"):
        return _selector_value(resolved.get("source_owner"))

    contract = _decision_contract_body(metadata)
    contract_owner = _as_dict(contract.get("source_owner"))
    return _selector_value(contract_owner.get("primary"))


def _decision_contract_body(metadata: dict[str, Any]) -> dict[str, Any]:
    decision_contract = _as_dict(metadata.get("decision_contract"))
    return _as_dict(decision_contract.get("contract"))


def _contract_semantic_text(metadata: dict[str, Any] | None) -> str:
    metadata = metadata or {}
    parts: list[str] = []

    planner = _as_dict(metadata.get("capability_planner"))
    action = _as_dict(planner.get("action"))
    _collect_selector_decision_values(action.get("intent"), parts)
    _collect_selector_decision_values(action.get("params"), parts)
    _collect_selector_decision_values(action.get("answer_contract"), parts)
    _collect_selector_decision_values(planner.get("plan_decision"), parts)

    resolved = _as_dict(metadata.get("resolved_decision"))
    if resolved:
        _collect_selector_decision_values(resolved.get("contract"), parts)
        _collect_selector_decision_values(resolved.get("capability"), parts)
        _collect_selector_decision_values(resolved.get("source_owner"), parts)
    else:
        contract = _decision_contract_body(metadata)
        contract_query = _as_dict(contract.get("query"))
        _collect_semantic_values(contract_query.get("effective"), parts)
        _collect_semantic_values(contract_query.get("standalone_query"), parts)
        _collect_selector_decision_values(contract.get("conversation"), parts)
        _collect_selector_decision_values(contract.get("intent"), parts)
        _collect_selector_decision_values(contract.get("capabilities"), parts)
        _collect_selector_decision_values(contract.get("slots"), parts)
        retrieval = _as_dict(contract.get("retrieval"))
        _collect_selector_decision_values({"must_answer": retrieval.get("must_answer")}, parts)
    return _normalize_text(" ".join(parts))


def _collect_selector_decision_values(value: Any, parts: list[str]) -> None:
    """Collect only routing/intent signals used for specialist selection."""
    if value is None:
        return
    if isinstance(value, dict):
        for key, nested in value.items():
            normalized_key = str(key).strip().lower()
            if normalized_key in _SELECTOR_DECISION_SKIP_KEYS:
                continue
            if normalized_key not in _SELECTOR_DECISION_KEYS:
                continue
            parts.append(str(key))
            _collect_selector_decision_values(nested, parts)
        return
    if isinstance(value, (list, tuple, set)):
        for item in value:
            _collect_selector_decision_values(item, parts)
        return
    if isinstance(value, bool):
        return
    text = str(value).strip()
    if text:
        parts.append(text)


def _collect_semantic_values(value: Any, parts: list[str]) -> None:
    if value is None:
        return
    if isinstance(value, dict):
        for key, nested in value.items():
            normalized_key = str(key).strip().lower()
            if normalized_key in _SEMANTIC_SKIP_KEYS:
                continue
            parts.append(str(key))
            _collect_semantic_values(nested, parts)
        return
    if isinstance(value, (list, tuple, set)):
        for item in value:
            _collect_semantic_values(item, parts)
        return
    if isinstance(value, bool):
        return
    text = str(value).strip()
    if text:
        parts.append(text)


_TRANSPORT_ERROR_MARKERS = ("a2a_", "transport", "timeout", "connection", "EvidenceItem")
_TRANSPORT_TIMEOUT_MARKERS = (
    "a2a_transport_timeout",
    "a2a_specialist_transport_timeout",
    "readtimeout",
    "timeout",
    "timed out",
)


def _is_transport_error(error_msg: str) -> bool:
    """Hata mesajı A2A transport/internal kaynaklı mı?"""
    return any(marker in error_msg for marker in _TRANSPORT_ERROR_MARKERS)


def _is_transport_timeout_error(error_msg: str) -> bool:
    """Transport hatası uzak branch'in hala çalışıyor olabileceğini gösteren timeout mu?"""
    normalized = str(error_msg or "").strip().lower()
    return any(marker in normalized for marker in _TRANSPORT_TIMEOUT_MARKERS)


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
