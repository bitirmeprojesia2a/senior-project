"""Helpers for event-only orchestration flows."""

from __future__ import annotations

from datetime import UTC, timedelta, timezone
from time import perf_counter

from src.a2a import extract_department_response
from src.a2a.tracing import child_trace_metadata
from src.a2a.capability_transport import HttpA2ACapabilityTransport
from src.api.a2a_dispatch import CapabilityDispatchRequest
from src.core.config import settings
from src.core.constants import Capability
from src.db.events import EventRecord
from src.db.schemas import DepartmentResponse, RAGSource
from src.db.telemetry import (
    build_capability_agent_identity,
    build_main_orchestrator_identity,
    build_specialist_agent_identity,
)
from src.orchestrators.task_builders import build_event_request_task
from src.orchestrators.response_utils import EVENT_SURFACE_DEPARTMENT
from src.orchestrators.user_response_builders import build_event_user_response

_ISTANBUL = timezone(timedelta(hours=3))


def _format_event_datetime(value) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    localized = value.astimezone(_ISTANBUL)
    if localized.hour == 0 and localized.minute == 0:
        return localized.strftime("%d.%m.%Y")
    return localized.strftime("%d.%m.%Y %H:%M")


def _format_event_range(event: EventRecord) -> str | None:
    start = _format_event_datetime(event.starts_at)
    end = _format_event_datetime(event.ends_at)
    if start and end and start != end:
        return f"{start} - {end}"
    return start or end


def build_event_sources(events: list[EventRecord]) -> list[RAGSource]:
    sources: list[RAGSource] = []
    for event in events:
        summary = event.display_summary or event.summary or event.title
        if event.source_url:
            sources.append(
                RAGSource(
                    content=summary,
                    score=1.0,
                    metadata={
                        "record_type": "event",
                        "title": event.title,
                        "source_url": event.source_url,
                        "faculty": event.faculty,
                        "unit_name": event.unit_name,
                        "event_type": event.event_type,
                        "location": event.location,
                        "organizer": event.organizer,
                    },
                )
            )
        for link in event.links:
            sources.append(
                RAGSource(
                    content=link.label,
                    score=1.0,
                    metadata={
                        "record_type": "event",
                        "title": event.title,
                        "label": link.label,
                        "url": link.url,
                        "link_type": link.link_type,
                    },
                )
            )
    return sources


def format_event_answer(
    *,
    query: str,
    events: list[EventRecord],
) -> str:
    if not events:
        return (
            "Bu sorguya uygun guncel veya yakin tarihli etkinlik bulamadim. "
            "Isterseniz fakulte, bolum ya da etkinlik turu belirterek tekrar sorabilirsiniz."
        )

    lines = ["Buldugum ilgili etkinlikler:"]
    for index, event in enumerate(events, start=1):
        lines.append(f"{index}. {event.title}")
        when = _format_event_range(event)
        if when:
            lines.append(f"   Tarih: {when}")
        if event.location:
            lines.append(f"   Yer: {event.location}")
        if event.organizer:
            lines.append(f"   Duzenleyen: {event.organizer}")
        if event.event_type:
            lines.append(f"   Tur: {event.event_type}")
        summary = event.display_summary or event.summary
        if summary:
            lines.append(f"   Ozet: {summary}")
    return "\n".join(lines)


async def build_event_response(
    *,
    response: DepartmentResponse,
    telemetry_service,
    context_id: str,
    start_time: float,
    query_log_id: int | None,
):
    """Build a full user-facing response for event-only requests."""
    response_time_ms = round((perf_counter() - start_time) * 1000, 2)
    await telemetry_service.finalize_query_log(
        query_log_id=query_log_id,
        response_text=response.answer,
        response_time_ms=response_time_ms,
        status="completed",
        departments=[EVENT_SURFACE_DEPARTMENT],
    )
    return build_event_user_response(
        context_id=context_id,
        answer=response.answer,
        sources=response.sources,
        response_time_ms=response_time_ms,
    )


async def request_event_response(
    *,
    event_agent,
    telemetry_service,
    query: str,
    context_id: str,
    routing_reason: str | None,
    query_log_id: int | None,
    task_type,
    faculty: str | None = None,
    unit_name: str | None = None,
    limit: int = 5,
    trace_metadata: dict | None = None,
):
    """Call the event agent through local or HTTP capability transport."""
    event_trace = child_trace_metadata(trace_metadata)
    event_task = build_event_request_task(
        query=query,
        context_id=context_id,
        routing_reason=routing_reason,
        faculty=faculty,
        unit_name=unit_name,
        limit=limit,
        trace_id=event_trace.get("trace_id"),
        span_id=event_trace.get("span_id"),
        parent_span_id=event_trace.get("parent_span_id"),
    )

    agent_started = perf_counter()
    if settings.a2a.mode == "http":
        response_task = None
        response = await HttpA2ACapabilityTransport(
            endpoint_resolver=telemetry_service
        ).dispatch(
            capability=Capability.EVENT,
            payload=CapabilityDispatchRequest(
                capability=Capability.EVENT,
                query=query,
                context_id=context_id,
                routing_reason=routing_reason,
                faculty=faculty,
                unit_name=unit_name,
                limit=limit,
                trace_id=event_trace.get("trace_id"),
                span_id=event_trace.get("span_id"),
                parent_span_id=event_trace.get("parent_span_id"),
            ),
        )
    else:
        response_task = await event_agent.handle_task(event_task)
        response = extract_department_response(response_task)
        if response is None:
            raise ValueError("event_agent gecerli department response dondurmedi.")
    agent_latency_ms = round((perf_counter() - agent_started) * 1000, 2)

    await telemetry_service.record_agent_task(
        task_id=response_task.id if response_task is not None else f"{context_id}:event",
        query_log_id=query_log_id,
        sender=build_main_orchestrator_identity(),
        receiver=(
            build_specialist_agent_identity(event_agent)
            if response_task is not None
            else build_capability_agent_identity(Capability.EVENT)
        ),
        task_type=task_type,
        payload=event_task.metadata or {},
        response=response,
        latency_ms=agent_latency_ms,
    )
    return response
