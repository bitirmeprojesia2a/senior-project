"""QueryLog ve AgentTask kayit yardimcilari."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import logging
from typing import Any

from sqlalchemy import select

from src.core.constants import AgentRole, Department, TaskType
from src.db.connection import get_session
from src.db.support_models import AgentRegistry, AgentTask, QueryLog
from src.db.schemas import DepartmentResponse, RoutingResult
from src.orchestrators.response_utils import response_core_answer

logger = logging.getLogger(__name__)

_QUERY_PREVIEW_MAX_CHARS = 240
_RESPONSE_PREVIEW_MAX_CHARS = 500
_ANSWER_PREVIEW_MAX_CHARS = 220
_REASONING_PREVIEW_MAX_CHARS = 280
_ERROR_PREVIEW_MAX_CHARS = 220
_SOURCE_REF_PREVIEW_MAX_CHARS = 80
_MAX_SOURCE_REFS = 5


def _utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp for telemetry records."""
    return datetime.now(UTC)


def _compact_text(value: object, *, max_len: int) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    compacted = " ".join(text.split())
    if len(compacted) <= max_len:
        return compacted
    return compacted[: max_len - 3].rstrip() + "..."


def _compact_list(
    values: list[object] | tuple[object, ...] | None,
    *,
    max_items: int,
    item_max_len: int,
) -> list[str]:
    compacted: list[str] = []
    for value in values or []:
        item = _compact_text(value, max_len=item_max_len)
        if item:
            compacted.append(item)
    return compacted[:max_items]


def _prune_mapping(value: Any) -> Any:
    if isinstance(value, dict):
        pruned: dict[str, Any] = {}
        for key, item in value.items():
            cleaned = _prune_mapping(item)
            if cleaned is None:
                continue
            if isinstance(cleaned, (dict, list)) and not cleaned:
                continue
            pruned[str(key)] = cleaned
        return pruned
    if isinstance(value, list):
        pruned_items = [_prune_mapping(item) for item in value]
        return [
            item
            for item in pruned_items
            if item is not None and not (isinstance(item, (dict, list)) and not item)
        ]
    return value


def _sanitize_query_metadata(
    *,
    context_id: str,
    user_id: str | None,
    task_type: str | None,
    reasoning: str | None,
) -> dict[str, Any]:
    return _prune_mapping(
        {
            "context_id": context_id,
            "has_user_id": bool(user_id),
            "task_type": task_type,
            "reasoning_preview": _compact_text(
                reasoning,
                max_len=_REASONING_PREVIEW_MAX_CHARS,
            ),
        }
    )


def _sanitize_query_log_response(response_text: str | None) -> str | None:
    return _compact_text(response_text, max_len=_RESPONSE_PREVIEW_MAX_CHARS)


def _sanitize_agent_task_payload(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if not payload:
        return None

    sanitized = {
        "context_id": payload.get("context_id"),
        "task_type": payload.get("task_type"),
        "query_text": _compact_text(payload.get("query_text"), max_len=_QUERY_PREVIEW_MAX_CHARS),
        "original_query": _compact_text(
            payload.get("original_query"),
            max_len=_QUERY_PREVIEW_MAX_CHARS,
        ),
        "resolved_query": _compact_text(
            payload.get("resolved_query"),
            max_len=_QUERY_PREVIEW_MAX_CHARS,
        ),
        "routing_reason": _compact_text(
            payload.get("routing_reason"),
            max_len=_REASONING_PREVIEW_MAX_CHARS,
        ),
        "profile": {
            "is_authenticated": bool(payload.get("is_authenticated", False)),
            "has_student_id": payload.get("student_id") is not None,
            "has_student_number": bool(payload.get("student_number")),
            "student_department": _compact_text(
                payload.get("student_department"),
                max_len=80,
            ),
            "student_faculty": _compact_text(
                payload.get("student_faculty"),
                max_len=80,
            ),
            "student_type": _compact_text(
                payload.get("student_type"),
                max_len=40,
            ),
        },
        "conversation": {
            "is_follow_up": bool(payload.get("conversation_is_follow_up", False)),
            "topic": _compact_text(payload.get("conversation_topic"), max_len=120),
            "source_refs": _compact_list(
                payload.get("conversation_source_refs"),
                max_items=_MAX_SOURCE_REFS,
                item_max_len=_SOURCE_REF_PREVIEW_MAX_CHARS,
            ),
        },
        "execution": {
            "llm_profile": payload.get("llm_profile"),
            "priority": payload.get("priority"),
            "force_llm_synthesis": bool(payload.get("force_llm_synthesis", False)),
            "query_complexity": payload.get("query_complexity"),
            "is_personal_query": bool(payload.get("is_personal_query", False)),
        },
    }
    return _prune_mapping(sanitized)


def _sanitize_error_message(error_msg: str | None) -> str | None:
    return _compact_text(error_msg, max_len=_ERROR_PREVIEW_MAX_CHARS)


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

    @staticmethod
    def _log_best_effort_failure(operation: str, exc: Exception) -> None:
        """Telemetry yazimi ana urun akisini kirmamali; hatayi sadece kaydet."""
        logger.warning("%s_failed: %s", operation, exc)

    @staticmethod
    def _build_agent_task_result(
        response: DepartmentResponse | None,
        error_msg: str | None,
    ) -> tuple[dict[str, Any] | None, str, str | None]:
        """DepartmentResponse nesnesini telemetry sonucu icin normalize eder."""
        if response is None:
            return None, "failed" if error_msg else "completed", _sanitize_error_message(error_msg)

        result_payload = {
            "department": response.department.value,
            "success": response.success,
            "answer_preview": _compact_text(
                response_core_answer(response),
                max_len=_ANSWER_PREVIEW_MAX_CHARS,
            ),
            "source_count": len(response.sources),
        }
        if not response.success and response.error:
            return result_payload, "failed", _sanitize_error_message(response.error)
        return result_payload, "failed" if error_msg else "completed", _sanitize_error_message(error_msg)

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
                        last_heartbeat=_utcnow(),
                    )
                    session.add(agent)
                    await session.flush()
                else:
                    agent.name = identity.name
                    agent.department = identity.department
                    agent.role = identity.role
                    agent.description = identity.description
                    agent.last_heartbeat = _utcnow()
                    await session.flush()

                return int(agent.id)
        except Exception as exc:
            self._log_best_effort_failure("ensure_agent", exc)
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
                    query_text=_compact_text(query_text, max_len=_QUERY_PREVIEW_MAX_CHARS) or "",
                    departments=[department.value for department in routing.departments],
                    routing_strategy=routing.strategy.value,
                    confidence_score=routing.confidence,
                    status="processing",
                    query_metadata=_sanitize_query_metadata(
                        context_id=context_id,
                        user_id=user_id,
                        task_type=routing.task_type.value if routing.task_type else None,
                        reasoning=routing.reasoning,
                    ),
                )
                session.add(query_log)
                await session.flush()
                return int(query_log.id)
        except Exception as exc:
            self._log_best_effort_failure("create_query_log", exc)
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

                query_log.response_text = _sanitize_query_log_response(response_text)
                query_log.response_time_ms = int(response_time_ms) if response_time_ms is not None else None
                query_log.status = status
                query_log.error = _sanitize_error_message(error)
                if departments is not None:
                    query_log.departments = departments
                await session.flush()
        except Exception as exc:
            self._log_best_effort_failure("finalize_query_log", exc)

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

                result_payload, status, error_msg = self._build_agent_task_result(
                    response,
                    error_msg,
                )
                completed_at = _utcnow()

                if agent_task is None:
                    agent_task = AgentTask(
                        task_id=task_id,
                        query_log_id=query_log_id,
                        sender_agent_id=sender_id,
                        receiver_agent_id=receiver_id,
                        task_type=task_type.value if task_type else "unknown",
                        status=status,
                        payload=_sanitize_agent_task_payload(payload),
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
                    agent_task.payload = _sanitize_agent_task_payload(payload)
                    agent_task.result = result_payload
                    agent_task.error_msg = error_msg
                    agent_task.completed_at = completed_at

                await session.flush()
        except Exception as exc:
            self._log_best_effort_failure("record_agent_task", exc)


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
