"""Departman orkestratörleri."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.a2a import A2AQueryPayload, build_query_task
from src.agents.base import BaseSpecialistAgent
from src.core.constants import Department, TaskType
from src.db.telemetry import (
    TelemetryService,
    build_department_orchestrator_identity,
    build_specialist_agent_identity,
)
from src.db.schemas import DepartmentResponse


@dataclass
class DepartmentOrchestrator:
    """Bir departman içindeki uzman ajanlara görev dağıtır."""

    department: Department
    agents: dict[TaskType, BaseSpecialistAgent]
    fallback_agent: BaseSpecialistAgent
    telemetry_service: TelemetryService | None = None

    async def handle(
        self,
        *,
        query_text: str,
        context_id: str,
        task_type: TaskType | None = None,
        metadata: dict | None = None,
    ) -> DepartmentResponse:
        agent = self._select_agent(task_type)
        payload = A2AQueryPayload(
            query_text=query_text,
            context_id=context_id,
            task_type=task_type.value if task_type else None,
            routing_reason=(metadata or {}).get("routing_reason"),
            is_authenticated=bool((metadata or {}).get("is_authenticated", False)),
            student_id=(metadata or {}).get("student_id"),
        )
        task = build_query_task(payload)
        try:
            response = await agent.handle_task(task)
            if self.telemetry_service is not None:
                await self.telemetry_service.record_agent_task(
                    task_id=task.id,
                    query_log_id=(metadata or {}).get("query_log_id"),
                    sender=build_department_orchestrator_identity(self.department),
                    receiver=build_specialist_agent_identity(agent),
                    task_type=task_type,
                    payload=payload.to_metadata(),
                    response=response,
                )
            return response
        except Exception as exc:
            if self.telemetry_service is not None:
                await self.telemetry_service.record_agent_task(
                    task_id=task.id,
                    query_log_id=(metadata or {}).get("query_log_id"),
                    sender=build_department_orchestrator_identity(self.department),
                    receiver=build_specialist_agent_identity(agent),
                    task_type=task_type,
                    payload=payload.to_metadata(),
                    response=None,
                    error_msg=str(exc),
                )
            raise

    def _select_agent(self, task_type: TaskType | None) -> BaseSpecialistAgent:
        if task_type is None:
            return self.fallback_agent
        return self.agents.get(task_type, self.fallback_agent)


def build_student_affairs_orchestrator(
    agents: Iterable[BaseSpecialistAgent],
    telemetry_service: TelemetryService | None = None,
) -> DepartmentOrchestrator:
    agents_by_id = {agent.agent_id: agent for agent in agents}
    return DepartmentOrchestrator(
        department=Department.STUDENT_AFFAIRS,
        agents={
            TaskType.REGISTRATION_QUERY: agents_by_id["registration_agent"],
            TaskType.ACADEMIC_QUERY: agents_by_id["graduation_agent"],
            TaskType.COURSE_QUERY: agents_by_id["graduation_agent"],
            TaskType.PROCEDURE_QUERY: agents_by_id["internship_agent"],
        },
        fallback_agent=agents_by_id["student_life_agent"],
        telemetry_service=telemetry_service,
    )


def build_academic_programs_orchestrator(
    agents: Iterable[BaseSpecialistAgent],
    telemetry_service: TelemetryService | None = None,
) -> DepartmentOrchestrator:
    agents_by_id = {agent.agent_id: agent for agent in agents}
    return DepartmentOrchestrator(
        department=Department.ACADEMIC_PROGRAMS,
        agents={
            TaskType.COURSE_QUERY: agents_by_id["curriculum_agent"],
            TaskType.PROCEDURE_QUERY: agents_by_id["regulation_agent"],
        },
        fallback_agent=agents_by_id["international_agent"],
        telemetry_service=telemetry_service,
    )


def build_finance_orchestrator(
    agents: Iterable[BaseSpecialistAgent],
    telemetry_service: TelemetryService | None = None,
) -> DepartmentOrchestrator:
    agents_by_id = {agent.agent_id: agent for agent in agents}
    return DepartmentOrchestrator(
        department=Department.FINANCE,
        agents={
            TaskType.TUITION_QUERY: agents_by_id["tuition_agent"],
            TaskType.PAYMENT_QUERY: agents_by_id["tuition_agent"],
            TaskType.SCHOLARSHIP_QUERY: agents_by_id["scholarship_agent"],
        },
        fallback_agent=agents_by_id["tuition_agent"],
        telemetry_service=telemetry_service,
    )
