"""QueryLog ve AgentTask kayit yardimcilari."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import aliased

from src.a2a.tracing import trace_metadata
from src.core.config import settings
from src.core.constants import AgentRole, Capability, Department, TaskType
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
    extra_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    trace = trace_metadata(extra_metadata)
    payload = _prune_mapping(
        {
            "context_id": context_id,
            "has_user_id": bool(user_id),
            "task_type": task_type,
            "trace": trace,
            "reasoning_preview": _compact_text(
                reasoning,
                max_len=_REASONING_PREVIEW_MAX_CHARS,
            ),
        }
    )
    if extra_metadata:
        merged = dict(payload or {})
        merged.update(_prune_mapping(extra_metadata) or {})
        return _prune_mapping(merged)
    return payload


def _sanitize_query_log_response(response_text: str | None) -> str | None:
    return _compact_text(response_text, max_len=_RESPONSE_PREVIEW_MAX_CHARS)


def _sanitize_agent_task_payload(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if not payload:
        return None

    sanitized = {
        "context_id": payload.get("context_id"),
        "task_type": payload.get("task_type"),
        "trace": trace_metadata(payload),
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
    endpoint: str | None = None
    capabilities: dict[str, Any] | None = None


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
        latency_ms: float | None = None,
    ) -> tuple[dict[str, Any] | None, str, str | None]:
        """DepartmentResponse nesnesini telemetry sonucu icin normalize eder."""
        if response is None:
            if latency_ms is None:
                return None, "failed" if error_msg else "completed", _sanitize_error_message(error_msg)
            return (
                {"latency_ms": round(float(latency_ms), 2)},
                "failed" if error_msg else "completed",
                _sanitize_error_message(error_msg),
            )

        result_payload = {
            "department": response.department.value,
            "success": response.success,
            "answer_preview": _compact_text(
                response_core_answer(response),
                max_len=_ANSWER_PREVIEW_MAX_CHARS,
            ),
            "source_count": len(response.sources),
        }
        if latency_ms is not None:
            result_payload["latency_ms"] = round(float(latency_ms), 2)
        if not response.success and response.error:
            return result_payload, "failed", _sanitize_error_message(response.error)
        return result_payload, "failed" if error_msg else "completed", _sanitize_error_message(error_msg)

    async def ensure_agent(self, identity: AgentIdentity) -> int | None:
        try:
            async with get_session() as session:
                stmt = select(AgentRegistry).where(AgentRegistry.agent_id == identity.agent_id)
                agent = (await session.execute(stmt)).scalar_one_or_none()

                normalized_endpoint = (
                    identity.endpoint.rstrip("/") if identity.endpoint else None
                )
                normalized_capabilities = (
                    _prune_mapping(identity.capabilities)
                    if identity.capabilities is not None
                    else None
                )

                if agent is None:
                    agent = AgentRegistry(
                        agent_id=identity.agent_id,
                        name=identity.name,
                        department=identity.department,
                        role=identity.role,
                        description=identity.description,
                        endpoint=normalized_endpoint,
                        capabilities=normalized_capabilities,
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
                    if normalized_endpoint is not None:
                        agent.endpoint = normalized_endpoint
                    if normalized_capabilities is not None:
                        agent.capabilities = normalized_capabilities
                    agent.is_active = True
                    agent.last_heartbeat = _utcnow()
                    await session.flush()

                return int(agent.id)
        except Exception as exc:
            self._log_best_effort_failure("ensure_agent", exc)
            return None

    async def resolve_department_endpoint(self, department: Department | str) -> str | None:
        """Resolve the freshest active department orchestrator endpoint from registry."""
        department_value = department.value if isinstance(department, Department) else str(department)
        return await self.resolve_service_endpoint(
            department_value,
            role=AgentRole.DEPARTMENT_ORCHESTRATOR.value,
        )

    async def resolve_agent_endpoint(
        self,
        agent_id: str,
        *,
        role: str | None = None,
    ) -> str | None:
        """Resolve the freshest active endpoint for a concrete agent id."""
        ttl_seconds = max(0.0, settings.a2a.discovery_ttl_seconds)
        heartbeat_cutoff = _utcnow() - timedelta(seconds=ttl_seconds)
        try:
            async with get_session() as session:
                conditions = [
                    AgentRegistry.agent_id == agent_id,
                    AgentRegistry.is_active.is_(True),
                    AgentRegistry.endpoint.is_not(None),
                ]
                if role is not None:
                    conditions.append(AgentRegistry.role == role)
                stmt = (
                    select(AgentRegistry.endpoint, AgentRegistry.last_heartbeat)
                    .where(*conditions)
                    .order_by(
                        AgentRegistry.last_heartbeat.desc(),
                        AgentRegistry.updated_at.desc(),
                    )
                    .limit(1)
                )
                row = (await session.execute(stmt)).one_or_none()
                if row is None:
                    return None
                endpoint, last_heartbeat = row
                if not endpoint:
                    return None
                if (
                    ttl_seconds > 0
                    and last_heartbeat is not None
                    and last_heartbeat < heartbeat_cutoff
                ):
                    logger.info(
                        "resolve_agent_endpoint_stale agent_id=%s endpoint=%s last_heartbeat=%s ttl_seconds=%s",
                        agent_id,
                        endpoint,
                        last_heartbeat.isoformat(),
                        ttl_seconds,
                    )
                    return None
                return str(endpoint).rstrip("/")
        except Exception as exc:
            self._log_best_effort_failure("resolve_agent_endpoint", exc)
            return None

    async def resolve_service_endpoint(
        self,
        service_name: str,
        *,
        role: str | None = None,
    ) -> str | None:
        """Resolve the freshest active service endpoint from registry."""
        ttl_seconds = max(0.0, settings.a2a.discovery_ttl_seconds)
        heartbeat_cutoff = _utcnow() - timedelta(seconds=ttl_seconds)
        try:
            async with get_session() as session:
                conditions = [
                    AgentRegistry.department == service_name,
                    AgentRegistry.is_active.is_(True),
                    AgentRegistry.endpoint.is_not(None),
                ]
                if role is not None:
                    conditions.append(AgentRegistry.role == role)
                stmt = (
                    select(AgentRegistry.endpoint, AgentRegistry.last_heartbeat)
                    .where(*conditions)
                    .order_by(
                        AgentRegistry.last_heartbeat.desc(),
                        AgentRegistry.updated_at.desc(),
                    )
                    .limit(1)
                )
                row = (await session.execute(stmt)).one_or_none()
                if row is None:
                    return None
                endpoint, last_heartbeat = row
                if not endpoint:
                    return None
                if (
                    ttl_seconds > 0
                    and last_heartbeat is not None
                    and last_heartbeat < heartbeat_cutoff
                ):
                    logger.info(
                        "resolve_service_endpoint_stale service=%s endpoint=%s last_heartbeat=%s ttl_seconds=%s",
                        service_name,
                        endpoint,
                        last_heartbeat.isoformat(),
                        ttl_seconds,
                    )
                    return None
                return str(endpoint).rstrip("/")
        except Exception as exc:
            self._log_best_effort_failure("resolve_service_endpoint", exc)
            return None

    async def list_registered_agents(
        self,
        *,
        include_internal: bool = False,
    ) -> list[dict[str, Any]]:
        """Return registry entries with freshness interpretation for ops visibility."""
        ttl_seconds = max(0.0, settings.a2a.discovery_ttl_seconds)
        heartbeat_cutoff = _utcnow() - timedelta(seconds=ttl_seconds)
        try:
            async with get_session() as session:
                stmt = (
                    select(AgentRegistry)
                    .order_by(
                        AgentRegistry.department.asc(),
                        AgentRegistry.role.asc(),
                        AgentRegistry.name.asc(),
                    )
                )
                rows = (await session.execute(stmt)).scalars().all()

            agents: list[dict[str, Any]] = []
            for row in rows:
                is_published_service = bool(row.endpoint) and row.role in {
                    AgentRole.DEPARTMENT_ORCHESTRATOR.value,
                    AgentRole.CAPABILITY_AGENT.value,
                    AgentRole.SPECIALIST_AGENT.value,
                }
                if not include_internal and not is_published_service:
                    continue
                last_heartbeat = row.last_heartbeat
                stale = bool(
                    ttl_seconds > 0
                    and last_heartbeat is not None
                    and last_heartbeat < heartbeat_cutoff
                )
                capabilities = row.capabilities or {}
                agents.append(
                    {
                        "agent_id": row.agent_id,
                        "name": row.name,
                        "department": row.department,
                        "role": row.role,
                        "description": row.description,
                        "endpoint": row.endpoint.rstrip("/") if row.endpoint else None,
                        "is_active": bool(row.is_active),
                        "last_heartbeat": (
                            last_heartbeat.isoformat() if last_heartbeat is not None else None
                        ),
                        "is_stale": stale,
                        "capabilities": capabilities,
                        "service_build": capabilities.get("service_build"),
                        "service_runtime_label": capabilities.get("service_runtime_label"),
                        "is_published_service": is_published_service,
                    }
                )
            return agents
        except Exception as exc:
            self._log_best_effort_failure("list_registered_agents", exc)
            return []

    async def get_a2a_diagnostics(
        self,
        *,
        window_minutes: int = 60,
        recent_limit: int = 10,
    ) -> dict[str, Any]:
        """Return recent A2A query/task health summary for operations views."""
        safe_window_minutes = max(1, min(int(window_minutes), 24 * 60))
        safe_recent_limit = max(0, min(int(recent_limit), 50))
        generated_at = _utcnow()
        window_started_at = generated_at - timedelta(minutes=safe_window_minutes)

        try:
            sender = aliased(AgentRegistry)
            receiver = aliased(AgentRegistry)
            async with get_session() as session:
                query_rows = (
                    await session.execute(
                        select(QueryLog)
                        .where(QueryLog.created_at >= window_started_at)
                        .order_by(QueryLog.created_at.desc())
                    )
                ).scalars().all()
                task_rows = (
                    await session.execute(
                        select(AgentTask, sender, receiver)
                        .join(sender, AgentTask.sender_agent_id == sender.id)
                        .join(receiver, AgentTask.receiver_agent_id == receiver.id)
                        .where(AgentTask.created_at >= window_started_at)
                        .order_by(AgentTask.created_at.desc())
                    )
                ).all()
        except Exception as exc:
            self._log_best_effort_failure("get_a2a_diagnostics", exc)
            return {
                "status": "error",
                "overview": {
                    "generated_at": generated_at.isoformat(),
                    "window_minutes": safe_window_minutes,
                    "window_started_at": window_started_at.isoformat(),
                    "query_count": 0,
                    "query_failure_count": 0,
                    "agent_task_count": 0,
                    "agent_task_failure_count": 0,
                    "avg_response_time_ms": None,
                    "max_response_time_ms": None,
                },
                "agents": [],
                "recent_failures": [],
                "error": _sanitize_error_message(str(exc)),
            }

        response_times = [
            int(row.response_time_ms)
            for row in query_rows
            if row.response_time_ms is not None
        ]
        query_failure_count = sum(1 for row in query_rows if row.status != "completed")

        agent_stats: dict[str, dict[str, Any]] = {}
        recent_failures: list[dict[str, Any]] = []
        agent_task_failure_count = 0

        for agent_task, sender_row, receiver_row in task_rows:
            receiver_id = receiver_row.agent_id
            stats = agent_stats.setdefault(
                receiver_id,
                {
                    "agent_id": receiver_id,
                    "name": receiver_row.name,
                    "department": receiver_row.department,
                    "role": receiver_row.role,
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "failed_tasks": 0,
                    "_latencies": [],
                    "latency_sample_count": 0,
                    "avg_latency_ms": None,
                    "max_latency_ms": None,
                    "last_error": None,
                    "last_completed_at": None,
                },
            )
            stats["total_tasks"] += 1
            if agent_task.status == "completed":
                stats["completed_tasks"] += 1
            else:
                stats["failed_tasks"] += 1
                agent_task_failure_count += 1

            result = agent_task.result or {}
            latency_ms = result.get("latency_ms") if isinstance(result, dict) else None
            if isinstance(latency_ms, (int, float)):
                stats["_latencies"].append(float(latency_ms))
            if agent_task.completed_at is not None and stats["last_completed_at"] is None:
                stats["last_completed_at"] = agent_task.completed_at.isoformat()
            if agent_task.error_msg and stats["last_error"] is None:
                stats["last_error"] = agent_task.error_msg

            if agent_task.status != "completed" and len(recent_failures) < safe_recent_limit:
                payload = agent_task.payload or {}
                trace = payload.get("trace") if isinstance(payload, dict) else {}
                recent_failures.append(
                    {
                        "task_id": agent_task.task_id,
                        "sender_agent_id": sender_row.agent_id,
                        "receiver_agent_id": receiver_row.agent_id,
                        "status": agent_task.status,
                        "error": agent_task.error_msg,
                        "completed_at": (
                            agent_task.completed_at.isoformat()
                            if agent_task.completed_at is not None
                            else None
                        ),
                        "trace_id": trace.get("trace_id") if isinstance(trace, dict) else None,
                        "query_preview": (
                            payload.get("query_text") if isinstance(payload, dict) else None
                        ),
                    }
                )

        agents: list[dict[str, Any]] = []
        for stats in agent_stats.values():
            latencies = stats.pop("_latencies")
            if latencies:
                stats["latency_sample_count"] = len(latencies)
                stats["avg_latency_ms"] = round(sum(latencies) / len(latencies), 2)
                stats["max_latency_ms"] = round(max(latencies), 2)
            total_tasks = int(stats["total_tasks"])
            stats["failure_rate"] = (
                round(float(stats["failed_tasks"]) / total_tasks, 4)
                if total_tasks
                else 0.0
            )
            agents.append(stats)
        agents.sort(key=lambda item: (-int(item["failed_tasks"]), item["agent_id"]))

        return {
            "status": "ok",
            "overview": {
                "generated_at": generated_at.isoformat(),
                "window_minutes": safe_window_minutes,
                "window_started_at": window_started_at.isoformat(),
                "query_count": len(query_rows),
                "query_failure_count": query_failure_count,
                "agent_task_count": len(task_rows),
                "agent_task_failure_count": agent_task_failure_count,
                "avg_response_time_ms": (
                    round(sum(response_times) / len(response_times), 2)
                    if response_times
                    else None
                ),
                "max_response_time_ms": max(response_times) if response_times else None,
            },
            "agents": agents,
            "recent_failures": recent_failures,
        }

    async def create_query_log(
        self,
        *,
        query_text: str,
        routing: RoutingResult | None,
        orchestrator: AgentIdentity,
        context_id: str,
        user_id: str | None = None,
        student_id: int | None = None,
        metadata_extra: dict[str, Any] | None = None,
    ) -> int | None:
        try:
            agent_registry_id = await self.ensure_agent(orchestrator)
            async with get_session() as session:
                query_log = QueryLog(
                    student_id=student_id,
                    agent_id=agent_registry_id,
                    query_text=_compact_text(query_text, max_len=_QUERY_PREVIEW_MAX_CHARS) or "",
                    departments=[department.value for department in routing.departments] if routing else [],
                    routing_strategy=routing.strategy.value if routing else None,
                    confidence_score=routing.confidence if routing else None,
                    status="processing",
                    query_metadata=_sanitize_query_metadata(
                        context_id=context_id,
                        user_id=user_id,
                        task_type=routing.task_type.value if routing and routing.task_type else None,
                        reasoning=routing.reasoning if routing else "announcement_short_circuit",
                        extra_metadata=metadata_extra,
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
        latency_ms: float | None = None,
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
                    latency_ms,
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


def build_department_orchestrator_identity(
    department: Department,
    *,
    endpoint: str | None = None,
    capabilities: dict[str, Any] | None = None,
) -> AgentIdentity:
    return AgentIdentity(
        agent_id=f"{department.value}_orchestrator",
        name=f"{department.value} Orchestrator",
        department=department.value,
        role=AgentRole.DEPARTMENT_ORCHESTRATOR.value,
        description=f"{department.value} uzman ajanlarini yoneten departman orkestratoru.",
        endpoint=endpoint,
        capabilities=capabilities,
    )


def build_specialist_agent_identity(
    agent: Any,
    *,
    endpoint: str | None = None,
    capabilities: dict[str, Any] | None = None,
) -> AgentIdentity:
    return AgentIdentity(
        agent_id=agent.agent_id,
        name=agent.definition.name,
        department=agent.department.value,
        role=AgentRole.SPECIALIST_AGENT.value,
        description=agent.definition.description,
        endpoint=endpoint,
        capabilities=capabilities,
    )


def build_capability_agent_identity(
    capability: Capability,
    *,
    endpoint: str | None = None,
    capabilities: dict[str, Any] | None = None,
) -> AgentIdentity:
    return AgentIdentity(
        agent_id=f"{capability.value}_agent",
        name=f"{capability.display_name} Agent",
        department=capability.value,
        role=AgentRole.CAPABILITY_AGENT.value,
        description=f"{capability.display_name} icin ayrik capability agent servisi.",
        endpoint=endpoint,
        capabilities=capabilities,
    )
