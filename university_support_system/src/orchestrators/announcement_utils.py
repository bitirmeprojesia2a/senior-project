"""Helpers for announcement-agent orchestration flows."""

from __future__ import annotations

from time import perf_counter

from src.a2a import extract_department_response
from src.db.telemetry import (
    build_main_orchestrator_identity,
    build_specialist_agent_identity,
)
from src.orchestrators.task_builders import build_announcement_request_task
from src.orchestrators.user_response_builders import build_announcement_user_response


async def request_announcement_response(
    *,
    announcement_agent,
    telemetry_service,
    query: str,
    context_id: str,
    routing_reason: str | None,
    query_log_id: int | None,
    task_type,
    departments: list[str] | None = None,
):
    """Call the announcement agent and record telemetry for the exchange."""
    announcement_task = build_announcement_request_task(
        query=query,
        context_id=context_id,
        routing_reason=routing_reason,
        departments=departments,
    )

    response_task = await announcement_agent.handle_task(announcement_task)
    response = extract_department_response(response_task)
    if response is None:
        raise ValueError("announcement_agent gecerli department response dondurmedi.")

    await telemetry_service.record_agent_task(
        task_id=response_task.id,
        query_log_id=query_log_id,
        sender=build_main_orchestrator_identity(),
        receiver=build_specialist_agent_identity(announcement_agent),
        task_type=task_type,
        payload=announcement_task.metadata or {},
        response=response,
    )
    return response


async def build_announcement_response(
    *,
    announcement_agent,
    telemetry_service,
    query: str,
    context_id: str,
    start_time: float,
    query_log_id: int | None,
    routing_reasoning: str | None,
    task_type,
):
    """Build a full user-facing response for announcement-only requests."""
    response = await request_announcement_response(
        announcement_agent=announcement_agent,
        telemetry_service=telemetry_service,
        query=query,
        context_id=context_id,
        routing_reason=routing_reasoning,
        query_log_id=query_log_id,
        task_type=task_type,
    )
    response_time_ms = round((perf_counter() - start_time) * 1000, 2)
    await telemetry_service.finalize_query_log(
        query_log_id=query_log_id,
        response_text=response.answer,
        response_time_ms=response_time_ms,
        status="completed",
        departments=["announcement"] if response.sources else [],
    )
    return build_announcement_user_response(
        context_id=context_id,
        answer=response.answer,
        sources=response.sources,
        response_time_ms=response_time_ms,
    )
