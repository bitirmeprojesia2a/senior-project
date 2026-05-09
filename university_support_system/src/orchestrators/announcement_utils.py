"""Helpers for announcement-agent orchestration flows."""

from __future__ import annotations

from time import perf_counter

from src.a2a.tracing import child_trace_metadata
from src.a2a.capability_transport import HttpA2ACapabilityTransport
from src.a2a import extract_department_response
from src.api.a2a_dispatch import CapabilityDispatchRequest
from src.core.config import settings
from src.core.constants import Capability
from src.db.telemetry import (
    build_capability_agent_identity,
    build_main_orchestrator_identity,
    build_specialist_agent_identity,
)
from src.orchestrators.response_utils import ANNOUNCEMENT_SURFACE_DEPARTMENT
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
    faculty: str | None = None,
    unit_name: str | None = None,
    conversation_source_refs: list[str] | None = None,
    allow_latest_fallback: bool = True,
    limit: int | None = None,
    trace_metadata: dict | None = None,
):
    """Call the announcement agent and record telemetry for the exchange."""
    announcement_trace = child_trace_metadata(trace_metadata)
    announcement_task = build_announcement_request_task(
        query=query,
        context_id=context_id,
        routing_reason=routing_reason,
        departments=departments,
        faculty=faculty,
        unit_name=unit_name,
        conversation_source_refs=conversation_source_refs,
        trace_id=announcement_trace.get("trace_id"),
        span_id=announcement_trace.get("span_id"),
        parent_span_id=announcement_trace.get("parent_span_id"),
    )
    announcement_task.metadata["allow_latest_fallback"] = allow_latest_fallback
    if limit is not None:
        announcement_task.metadata["limit"] = limit

    agent_started = perf_counter()
    if settings.a2a.mode == "http":
        response_task = None
        response = await HttpA2ACapabilityTransport(
            endpoint_resolver=telemetry_service
        ).dispatch(
            capability=Capability.ANNOUNCEMENT,
            payload=CapabilityDispatchRequest(
                capability=Capability.ANNOUNCEMENT,
                query=query,
                context_id=context_id,
                routing_reason=routing_reason,
                departments=list(departments or []),
                faculty=faculty,
                unit_name=unit_name,
                conversation_source_refs=list(conversation_source_refs or []),
                allow_latest_fallback=allow_latest_fallback,
                limit=limit or 5,
                trace_id=announcement_trace.get("trace_id"),
                span_id=announcement_trace.get("span_id"),
                parent_span_id=announcement_trace.get("parent_span_id"),
            ),
        )
    else:
        response_task = await announcement_agent.handle_task(announcement_task)
        response = extract_department_response(response_task)
        if response is None:
            raise ValueError("announcement_agent gecerli department response dondurmedi.")
    agent_latency_ms = round((perf_counter() - agent_started) * 1000, 2)

    await telemetry_service.record_agent_task(
        task_id=response_task.id if response_task is not None else f"{context_id}:announcement",
        query_log_id=query_log_id,
        sender=build_main_orchestrator_identity(),
        receiver=(
            build_specialist_agent_identity(announcement_agent)
            if response_task is not None
            else build_capability_agent_identity(Capability.ANNOUNCEMENT)
        ),
        task_type=task_type,
        payload=announcement_task.metadata or {},
        response=response,
        latency_ms=agent_latency_ms,
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
    faculty: str | None = None,
    unit_name: str | None = None,
    conversation_source_refs: list[str] | None = None,
    allow_latest_fallback: bool = True,
    limit: int | None = None,
    trace_metadata: dict | None = None,
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
        faculty=faculty,
        unit_name=unit_name,
        conversation_source_refs=conversation_source_refs,
        allow_latest_fallback=allow_latest_fallback,
        limit=limit,
        trace_metadata=trace_metadata,
    )
    response_time_ms = round((perf_counter() - start_time) * 1000, 2)
    await telemetry_service.finalize_query_log(
        query_log_id=query_log_id,
        response_text=response.answer,
        response_time_ms=response_time_ms,
        status="completed",
        departments=[ANNOUNCEMENT_SURFACE_DEPARTMENT],
    )
    return build_announcement_user_response(
        context_id=context_id,
        answer=response.answer,
        sources=response.sources,
        response_time_ms=response_time_ms,
    )
