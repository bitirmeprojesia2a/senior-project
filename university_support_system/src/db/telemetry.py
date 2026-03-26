"""QueryLog ve AgentTask kayit yardimcilari."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import logging
from typing import Any

from sqlalchemy import select

from src.core.constants import AgentRole, Department, TaskType
from src.db.connection import get_session
from src.db.models import AgentRegistry, AgentTask, QueryLog
from src.db.schemas import DepartmentResponse, RoutingResult

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AgentIdentity:
    """Kayit icin gereken ajan kimligi."""

    agent_id: str
    name: str
    department: str
    role: str
    description: str | None = None


class TelemetryService:
    """QueryLog ve AgentTask kayitlarini en iyi caba ile yazar."""

    async def ensure_agent(self, identity: AgentIdentity) -> int | None:
        try:
            async with get_session() as session:
                stmt = select(AgentRegistry).where(AgentRegistry.agent_id == identity.agent_id)
                agent = (await session.execute(stmt)).scalar_one_or_none()

                if agent is None:
                    agent = AgentRegistry(
                        agent_id=identity.agent_id,
                        name=identity.name,
                        department=identity.department,
                        role=identity.role,
                        description=identity.description,
                        is_active=True,
                        last_heartbeat=datetime.now(UTC),
                    )
                    session.add(agent)
                    await session.flush()
                else:
                    agent.name = identity.name
                    agent.department = identity.department
                    agent.role = identity.role
                    agent.description = identity.description
                    agent.last_heartbeat = datetime.now(UTC)
                    await session.flush()

                return int(agent.id)
        except Exception as exc:
            logger.warning("ensure_agent_failed: %s", exc)
            return None

    async def create_query_log(
        self,
        *,
        query_text: str,
        routing: RoutingResult,
        orchestrator: AgentIdentity,
        context_id: str,
        user_id: str | None = None,
        student_id: int | None = None,
    ) -> int | None:
        try:
            agent_registry_id = await self.ensure_agent(orchestrator)
            async with get_session() as session:
                query_log = QueryLog(
                    student_id=student_id,
                    agent_id=agent_registry_id,
                    query_text=query_text,
                    departments=[department.value for department in routing.departments],
                    routing_strategy=routing.strategy.value,
                    confidence_score=routing.confidence,
                    status="processing",
                    query_metadata={
                        "context_id": context_id,
                        "user_id": user_id,
                        "task_type": routing.task_type.value if routing.task_type else None,
                        "reasoning": routing.reasoning,
                    },
                )
                session.add(query_log)
                await session.flush()
                return int(query_log.id)
        except Exception as exc:
            logger.warning("create_query_log_failed: %s", exc)
            return None

    async def finalize_query_log(
        self,
        *,
        query_log_id: int | None,
        response_text: str | None,
        response_time_ms: float | None,
        status: str,
        error: str | None = None,
        departments: list[str] | None = None,
    ) -> None:
        if query_log_id is None:
            return

        try:
            async with get_session() as session:
                query_log = await session.get(QueryLog, query_log_id)
                if query_log is None:
                    return

                query_log.response_text = response_text
                query_log.response_time_ms = int(response_time_ms) if response_time_ms is not None else None
                query_log.status = status
                query_log.error = error
                if departments is not None:
                    query_log.departments = departments
                await session.flush()
        except Exception as exc:
            logger.warning("finalize_query_log_failed: %s", exc)

    async def record_agent_task(
        self,
        *,
        task_id: str,
        sender: AgentIdentity,
        receiver: AgentIdentity,
        task_type: TaskType | None,
        payload: dict[str, Any] | None,
        response: DepartmentResponse | None,
        query_log_id: int | None = None,
        error_msg: str | None = None,
    ) -> None:
        try:
            sender_id = await self.ensure_agent(sender)
            receiver_id = await self.ensure_agent(receiver)
            if sender_id is None or receiver_id is None:
                return

            async with get_session() as session:
                stmt = select(AgentTask).where(AgentTask.task_id == task_id)
                agent_task = (await session.execute(stmt)).scalar_one_or_none()

                result_payload = None
                status = "failed" if error_msg else "completed"
                completed_at = datetime.now(UTC)

                if response is not None:
                    result_payload = {
                        "department": response.department.value,
                        "success": response.success,
                        "answer_preview": response.answer[:500],
                        "source_count": len(response.sources),
                    }
                    if not response.success and response.error:
                        error_msg = response.error
                        status = "failed"

                if agent_task is None:
                    agent_task = AgentTask(
                        task_id=task_id,
                        query_log_id=query_log_id,
                        sender_agent_id=sender_id,
                        receiver_agent_id=receiver_id,
                        task_type=task_type.value if task_type else "unknown",
                        status=status,
                        payload=payload,
                        result=result_payload,
                        error_msg=error_msg,
                        completed_at=completed_at,
                    )
                    session.add(agent_task)
                else:
                    agent_task.query_log_id = query_log_id
                    agent_task.sender_agent_id = sender_id
                    agent_task.receiver_agent_id = receiver_id
                    agent_task.task_type = task_type.value if task_type else "unknown"
                    agent_task.status = status
                    agent_task.payload = payload
                    agent_task.result = result_payload
                    agent_task.error_msg = error_msg
                    agent_task.completed_at = completed_at

                await session.flush()
        except Exception as exc:
            logger.warning("record_agent_task_failed: %s", exc)


def build_main_orchestrator_identity() -> AgentIdentity:
    return AgentIdentity(
        agent_id="main_orchestrator",
        name="Main Orchestrator",
        department="system",
        role=AgentRole.MAIN_ORCHESTRATOR.value,
        description="Ana sorgu yonlendirme ve birlestirme orkestratoru.",
    )


def build_department_orchestrator_identity(department: Department) -> AgentIdentity:
    return AgentIdentity(
        agent_id=f"{department.value}_orchestrator",
        name=f"{department.value} Orchestrator",
        department=department.value,
        role=AgentRole.DEPARTMENT_ORCHESTRATOR.value,
        description=f"{department.value} uzman ajanlarini yoneten departman orkestratoru.",
    )


def build_specialist_agent_identity(agent: Any) -> AgentIdentity:
    return AgentIdentity(
        agent_id=agent.agent_id,
        name=agent.definition.name,
        department=agent.department.value,
        role=AgentRole.SPECIALIST_AGENT.value,
        description=agent.definition.description,
    )
