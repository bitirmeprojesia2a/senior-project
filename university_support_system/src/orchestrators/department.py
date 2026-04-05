"""Department orchestrator implementation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from a2a.types import Task

from src.a2a import build_department_response_task, extract_department_response
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
            query_text = str(merged_metadata.get("query_text", "")).strip() or extract_query_from_task(task)
            with profile_stage("department.select_agent", department=self.department.value):
                agent = self._select_agent(task_type, query_text)
            payload, specialist_task = build_specialist_task(
                query_text=query_text,
                context_id=task.contextId,
                task_type=task_type,
                metadata=merged_metadata,
            )
            try:
                with profile_stage(
                    "department.agent_handle_task",
                    department=self.department.value,
                    agent_id=agent.agent_id,
                ):
                    agent_response_task = await agent.handle_task(specialist_task)
                    response = extract_department_response(agent_response_task)
                    if response is None:
                        raise ValueError(
                            f"{agent.agent_id} gecerli department response metadata'si dondurmedi."
                        )
                await self._record_agent_task(
                    agent=agent,
                    task_id=agent_response_task.id,
                    query_log_id=merged_metadata.get("query_log_id"),
                    task_type=task_type,
                    payload=payload.to_metadata(),
                    response=response,
                )
                return build_department_response_task(
                    response,
                    request_task=task,
                    emitter_id=f"{self.department.value}_orchestrator",
                    emitter_name=f"{self.department.value} Orchestrator",
                    metadata={"selected_agent_id": agent.agent_id},
                )
            except Exception as exc:
                await self._record_agent_task(
                    agent=agent,
                    task_id=str(specialist_task.id),
                    query_log_id=merged_metadata.get("query_log_id"),
                    task_type=task_type,
                    payload=payload.to_metadata(),
                    response=None,
                    error_msg=str(exc),
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
            )

    def _select_agent(
        self,
        task_type: TaskType | None,
        query_text: str = "",
    ) -> BaseSpecialistAgent:
        if query_text and self.keyword_routing and self.agents_by_id:
            lowered = _normalize_text(query_text)
            for keyword, agent_id in self.keyword_routing.items():
                if _normalize_text(keyword) in lowered:
                    matched = self.agents_by_id.get(agent_id)
                    if matched is not None:
                        return matched

        if task_type is not None:
            agent = self.agents.get(task_type)
            if agent is not None:
                return agent

        return self.fallback_agent


def _normalize_text(text: str) -> str:
    return normalize_text(text)


__all__ = [
    "DepartmentOrchestrator",
    "build_student_affairs_orchestrator",
    "build_academic_programs_orchestrator",
    "build_finance_orchestrator",
]
