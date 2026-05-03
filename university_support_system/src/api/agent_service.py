"""Standalone agent service entrypoint."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import logging
from time import perf_counter
from typing import Any

from a2a.types import (
    JSONRPCRequest,
    MessageSendParams,
    Task,
)
from fastapi import FastAPI, Header, HTTPException
from pydantic import ValidationError

from src.a2a import (
    AgentServiceTarget,
    SpecialistTarget,
    resolve_agent_service_target,
)
from src.a2a.agent_cards import build_agent_card_payload, build_standard_agent_card
from src.a2a.jsonrpc import jsonrpc_error, jsonrpc_success
from src.a2a.service_identity import (
    A2A_BODY_SHA256_HEADER,
    A2A_CALLER_ID_HEADER,
    A2A_NONCE_HEADER,
    A2A_SIGNATURE_HEADER,
    A2A_TARGET_ID_HEADER,
    A2A_TIMESTAMP_HEADER,
)
from src.agents.announcement import AnnouncementAgent
from src.agents.event import EventAgent
from src.api.a2a_dispatch import (
    A2ADispatchRequest,
    CapabilityDispatchRequest,
    SpecialistDispatchRequest,
    assert_a2a_jsonrpc_access,
    assert_internal_api_access,
)
from src.api.agent_service_execution import (
    capability_payload_from_message,
    department_payload_from_message,
    execute_capability_dispatch,
    execute_capability_message_send,
    execute_department_dispatch,
    execute_department_message_send,
    execute_specialist_dispatch,
    execute_specialist_message_send,
    message_metadata,
    message_text,
    specialist_payload_from_message,
)
from src.core.config import settings
from src.core.constants import Capability, Department
from src.db import AuthService, dispose_engine
from src.db.schemas import DepartmentResponse
from src.db.telemetry import (
    TelemetryService,
    build_capability_agent_identity,
    build_department_orchestrator_identity,
    build_specialist_agent_identity,
)
from src.orchestrators.defaults import build_department_orchestrator, build_specialist_agent
from src.startup.warmup import cancel_application_warmup, schedule_application_warmup, warm_application_resources

logger = logging.getLogger(__name__)
_PRESENCE_REFRESH_TIMEOUT_SECONDS = 1.0


def resolve_agent_target(value: str | None = None) -> AgentServiceTarget:
    """Resolve the configured service target for this standalone agent service."""
    return resolve_agent_service_target(
        raw_target=value or settings.agent.department,
        specialist_id=settings.agent.specialist_id,
    )


def resolve_agent_department(value: str | None = None) -> Department:
    """Backward-compatible department-only resolver."""
    target = resolve_agent_target(value)
    if isinstance(target, Department):
        return target
    raise RuntimeError(f"Beklenen departman, farkli hedef geldi: {target.value}")


@asynccontextmanager
async def _agent_lifespan(app: FastAPI):
    warmup_task = schedule_application_warmup(
        lambda: warm_application_resources(
            llm_service=getattr(getattr(app.state, "handler", None), "llm_service", None),
            target=getattr(app.state, "target", None),
        ),
        label=f"agent:{getattr(getattr(app.state, 'target', None), 'value', 'unknown')}",
    )
    try:
        register_presence = getattr(app.state, "register_presence", None)
        if register_presence is not None:
            try:
                await asyncio.wait_for(
                    register_presence(),
                    timeout=_PRESENCE_REFRESH_TIMEOUT_SECONDS,
                )
            except Exception as exc:
                logger.warning(
                    "agent_service_startup_presence_refresh_failed error=%s",
                    exc,
                )
        yield
    finally:
        await cancel_application_warmup(warmup_task)
        await dispose_engine()


def create_agent_service_app(
    *,
    target: AgentServiceTarget | None = None,
    department: Department | None = None,
    orchestrator: Any | None = None,
    service_handler: Any | None = None,
    auth_service: AuthService | None = None,
    telemetry_service: TelemetryService | None = None,
) -> FastAPI:
    """Create a FastAPI app that serves one department or capability agent."""
    resolved_target = target or department or resolve_agent_target()
    resolved_telemetry_service = telemetry_service or TelemetryService()

    if isinstance(resolved_target, Department):
        handler = orchestrator or build_department_orchestrator(
            resolved_target,
            resolved_telemetry_service,
        )
    elif resolved_target is Capability.ANNOUNCEMENT:
        handler = service_handler or AnnouncementAgent()
    elif resolved_target is Capability.EVENT:
        handler = service_handler or EventAgent()
    elif isinstance(resolved_target, SpecialistTarget):
        handler = service_handler or build_specialist_agent(
            resolved_target.department,
            resolved_target.agent_id,
        )
    else:
        raise RuntimeError(f"Desteklenmeyen agent target: {resolved_target!r}")

    resolved_auth_service = auth_service or AuthService()
    agent_card_payload = build_agent_card_payload(
        target=resolved_target,
        service_handler=handler,
    )
    standard_agent_card = build_standard_agent_card(
        target=resolved_target,
        service_handler=handler,
    )

    async def _register_presence() -> None:
        if isinstance(resolved_target, Department):
            identity = build_department_orchestrator_identity(
                resolved_target,
                endpoint=agent_card_payload["url"],
                capabilities=agent_card_payload["capabilities"],
            )
        else:
            if isinstance(resolved_target, Capability):
                identity = build_capability_agent_identity(
                    resolved_target,
                    endpoint=agent_card_payload["url"],
                    capabilities=agent_card_payload["capabilities"],
                )
            else:
                identity = build_specialist_agent_identity(
                    handler,
                    endpoint=agent_card_payload["url"],
                    capabilities=agent_card_payload["capabilities"],
                )
        await resolved_telemetry_service.ensure_agent(identity)

    app = FastAPI(
        title=f"OMU {resolved_target.display_name} Agent Service",
        version=settings.server.app_version,
        description="Standalone agent service for HTTP A2A dispatch.",
        lifespan=_agent_lifespan,
    )
    app.state.target = resolved_target
    app.state.handler = handler
    app.state.register_presence = _register_presence
    app.state.request_count = 0
    app.state.failure_count = 0
    app.state.total_response_time_ms = 0.0

    async def _refresh_presence_best_effort() -> None:
        try:
            await asyncio.wait_for(
                app.state.register_presence(),
                timeout=_PRESENCE_REFRESH_TIMEOUT_SECONDS,
            )
        except Exception as exc:
            logger.warning(
                "agent_service_presence_refresh_failed target=%s error=%s",
                resolved_target.value,
                exc,
            )

    @app.get("/health", tags=["system"])
    async def health() -> dict[str, Any]:
        await _refresh_presence_best_effort()
        body = {
            "status": "ok",
            "service": settings.agent.service_id,
            "a2a_mode": "agent_service",
            "a2a_transport_protocol": settings.a2a.transport_protocol,
            "build": settings.server.build_metadata(),
            "runtime": {
                "label": settings.server.runtime_label,
            },
        }
        if isinstance(resolved_target, Department):
            body["department"] = resolved_target.value
        elif isinstance(resolved_target, Capability):
            body["capability"] = resolved_target.value
        else:
            body["department"] = resolved_target.department.value
            body["specialist_id"] = resolved_target.agent_id
        return body

    @app.get("/agent-card", tags=["a2a"])
    async def agent_card() -> dict[str, Any]:
        await _refresh_presence_best_effort()
        return agent_card_payload

    @app.get("/.well-known/agent.json", tags=["a2a"])
    async def well_known_agent_json() -> dict[str, Any]:
        await _refresh_presence_best_effort()
        return standard_agent_card.model_dump(mode="json", exclude_none=True)

    @app.get("/.well-known/agent-card.json", tags=["a2a"])
    async def well_known_agent_card_json() -> dict[str, Any]:
        await _refresh_presence_best_effort()
        return standard_agent_card.model_dump(mode="json", exclude_none=True)

    @app.get("/metrics", tags=["system"])
    async def metrics() -> dict[str, Any]:
        count = app.state.request_count
        avg_ms = app.state.total_response_time_ms / count if count else 0.0
        if isinstance(resolved_target, Department):
            target_key = "department"
        elif isinstance(resolved_target, Capability):
            target_key = "capability"
        else:
            target_key = "specialist_id"
        return {
            target_key: resolved_target.value,
            "request_count": count,
            "failure_count": app.state.failure_count,
            "avg_response_time_ms": round(avg_ms, 2),
        }

    async def _handle_message_send(params: MessageSendParams) -> Task:
        message = params.message
        metadata = message_metadata(params)
        query_text = message_text(message)
        if not query_text:
            raise ValueError("message/send icin en az bir text part gerekir.")
        context_id = message.contextId or str(metadata.get("context_id") or "api-a2a-context")
        start = perf_counter()
        app.state.request_count += 1
        try:
            if isinstance(resolved_target, Department):
                payload = department_payload_from_message(
                    department=resolved_target,
                    message=message,
                    metadata=metadata,
                    query_text=query_text,
                    context_id=context_id,
                )
                response_task = await execute_department_message_send(
                    payload=payload,
                    message=message,
                    handler=handler,
                    auth_service=resolved_auth_service,
                    emitter_id=settings.agent.service_id,
                    emitter_name=standard_agent_card.name,
                )
            elif isinstance(resolved_target, Capability):
                payload = capability_payload_from_message(
                    capability=resolved_target,
                    metadata=metadata,
                    query_text=query_text,
                    context_id=context_id,
                )
                response_task = await execute_capability_message_send(
                    payload=payload,
                    handler=handler,
                )
            else:
                payload = specialist_payload_from_message(
                    target=resolved_target,
                    metadata=metadata,
                    query_text=query_text,
                    context_id=context_id,
                )
                response_task = await execute_specialist_message_send(
                    payload=payload,
                    message=message,
                    handler=handler,
                )
            app.state.total_response_time_ms += (perf_counter() - start) * 1000
            return response_task
        except Exception:
            app.state.failure_count += 1
            raise

    @app.post("/a2a", tags=["a2a"])
    async def jsonrpc_a2a(
        payload: dict[str, Any],
        x_internal_api_key: str | None = Header(default=None, alias="X-Internal-API-Key"),
        x_a2a_caller_id: str | None = Header(default=None, alias=A2A_CALLER_ID_HEADER),
        x_a2a_target_id: str | None = Header(default=None, alias=A2A_TARGET_ID_HEADER),
        x_a2a_timestamp: str | None = Header(default=None, alias=A2A_TIMESTAMP_HEADER),
        x_a2a_nonce: str | None = Header(default=None, alias=A2A_NONCE_HEADER),
        x_a2a_body_sha256: str | None = Header(default=None, alias=A2A_BODY_SHA256_HEADER),
        x_a2a_signature: str | None = Header(default=None, alias=A2A_SIGNATURE_HEADER),
    ) -> dict[str, Any]:
        assert_a2a_jsonrpc_access(
            x_internal_api_key,
            caller_id=x_a2a_caller_id,
            target_id=x_a2a_target_id,
            expected_target_id=settings.agent.service_id,
            request_body=payload,
            request_timestamp=x_a2a_timestamp,
            request_nonce=x_a2a_nonce,
            request_body_sha256=x_a2a_body_sha256,
            request_signature=x_a2a_signature,
        )
        try:
            request = JSONRPCRequest.model_validate(payload)
        except ValidationError as exc:
            return jsonrpc_error(
                None,
                code=-32600,
                message="Invalid JSON-RPC request.",
                data=exc.errors(),
            )
        if request.method != "message/send":
            return jsonrpc_error(
                request.id,
                code=-32601,
                message=f"Unsupported A2A method: {request.method}",
            )
        try:
            params = MessageSendParams.model_validate(request.params or {})
            response_task = await _handle_message_send(params)
        except (ValidationError, ValueError) as exc:
            return jsonrpc_error(
                request.id,
                code=-32602,
                message="Invalid message/send params.",
                data=str(exc),
            )
        except Exception as exc:
            logger.exception(
                "agent_service_jsonrpc_execution_failed target=%s",
                resolved_target.value,
            )
            return jsonrpc_error(
                request.id,
                code=-32000,
                message="A2A agent execution failed.",
                data=str(exc),
            )
        return jsonrpc_success(
            request,
            response_task.model_dump(mode="json", exclude_none=True),
        )

    if isinstance(resolved_target, Department):

        @app.post("/a2a/dispatch", response_model=DepartmentResponse, tags=["a2a"])
        async def dispatch_task(
            payload: A2ADispatchRequest,
            x_internal_api_key: str | None = Header(default=None, alias="X-Internal-API-Key"),
            x_a2a_caller_id: str | None = Header(default=None, alias=A2A_CALLER_ID_HEADER),
            x_a2a_target_id: str | None = Header(default=None, alias=A2A_TARGET_ID_HEADER),
            x_a2a_timestamp: str | None = Header(default=None, alias=A2A_TIMESTAMP_HEADER),
            x_a2a_nonce: str | None = Header(default=None, alias=A2A_NONCE_HEADER),
            x_a2a_body_sha256: str | None = Header(default=None, alias=A2A_BODY_SHA256_HEADER),
            x_a2a_signature: str | None = Header(default=None, alias=A2A_SIGNATURE_HEADER),
        ) -> DepartmentResponse:
            assert_internal_api_access(
                x_internal_api_key,
                caller_id=x_a2a_caller_id,
                target_id=x_a2a_target_id,
                expected_target_id=settings.agent.service_id,
                request_body=payload.model_dump(mode="json"),
                request_timestamp=x_a2a_timestamp,
                request_nonce=x_a2a_nonce,
                request_body_sha256=x_a2a_body_sha256,
                request_signature=x_a2a_signature,
            )
            await _refresh_presence_best_effort()
            if payload.department != resolved_target:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Bu servis {resolved_target.value} departmani icin calisiyor; "
                        f"{payload.department.value} kabul edilmedi."
                    ),
                )

            start = perf_counter()
            app.state.request_count += 1
            try:
                response, _, _ = await execute_department_dispatch(
                    payload=payload,
                    handler=handler,
                    auth_service=resolved_auth_service,
                )
                app.state.total_response_time_ms += (perf_counter() - start) * 1000
                return response
            except Exception:
                app.state.failure_count += 1
                raise

    elif isinstance(resolved_target, Capability):

        @app.post("/a2a/dispatch", response_model=DepartmentResponse, tags=["a2a"])
        async def dispatch_capability_task(
            payload: CapabilityDispatchRequest,
            x_internal_api_key: str | None = Header(default=None, alias="X-Internal-API-Key"),
            x_a2a_caller_id: str | None = Header(default=None, alias=A2A_CALLER_ID_HEADER),
            x_a2a_target_id: str | None = Header(default=None, alias=A2A_TARGET_ID_HEADER),
            x_a2a_timestamp: str | None = Header(default=None, alias=A2A_TIMESTAMP_HEADER),
            x_a2a_nonce: str | None = Header(default=None, alias=A2A_NONCE_HEADER),
            x_a2a_body_sha256: str | None = Header(default=None, alias=A2A_BODY_SHA256_HEADER),
            x_a2a_signature: str | None = Header(default=None, alias=A2A_SIGNATURE_HEADER),
        ) -> DepartmentResponse:
            assert_internal_api_access(
                x_internal_api_key,
                caller_id=x_a2a_caller_id,
                target_id=x_a2a_target_id,
                expected_target_id=settings.agent.service_id,
                request_body=payload.model_dump(mode="json"),
                request_timestamp=x_a2a_timestamp,
                request_nonce=x_a2a_nonce,
                request_body_sha256=x_a2a_body_sha256,
                request_signature=x_a2a_signature,
            )
            await _refresh_presence_best_effort()
            if payload.capability != resolved_target:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Bu servis {resolved_target.value} capability'si icin calisiyor; "
                        f"{payload.capability.value} kabul edilmedi."
                    ),
                )

            start = perf_counter()
            app.state.request_count += 1
            try:
                response = await execute_capability_dispatch(
                    payload=payload,
                    handler=handler,
                )
                app.state.total_response_time_ms += (perf_counter() - start) * 1000
                return response
            except Exception:
                app.state.failure_count += 1
                raise

    else:

        @app.post("/a2a/dispatch", response_model=DepartmentResponse, tags=["a2a"])
        async def dispatch_specialist_task(
            payload: SpecialistDispatchRequest,
            x_internal_api_key: str | None = Header(default=None, alias="X-Internal-API-Key"),
            x_a2a_caller_id: str | None = Header(default=None, alias=A2A_CALLER_ID_HEADER),
            x_a2a_target_id: str | None = Header(default=None, alias=A2A_TARGET_ID_HEADER),
            x_a2a_timestamp: str | None = Header(default=None, alias=A2A_TIMESTAMP_HEADER),
            x_a2a_nonce: str | None = Header(default=None, alias=A2A_NONCE_HEADER),
            x_a2a_body_sha256: str | None = Header(default=None, alias=A2A_BODY_SHA256_HEADER),
            x_a2a_signature: str | None = Header(default=None, alias=A2A_SIGNATURE_HEADER),
        ) -> DepartmentResponse:
            assert_internal_api_access(
                x_internal_api_key,
                caller_id=x_a2a_caller_id,
                target_id=x_a2a_target_id,
                expected_target_id=settings.agent.service_id,
                request_body=payload.model_dump(mode="json"),
                request_timestamp=x_a2a_timestamp,
                request_nonce=x_a2a_nonce,
                request_body_sha256=x_a2a_body_sha256,
                request_signature=x_a2a_signature,
            )
            await _refresh_presence_best_effort()
            if (
                payload.department != resolved_target.department
                or payload.agent_id != resolved_target.agent_id
            ):
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Bu servis {resolved_target.department.value}/{resolved_target.agent_id} "
                        f"uzman ajani icin calisiyor; "
                        f"{payload.department.value}/{payload.agent_id} kabul edilmedi."
                    ),
                )

            start = perf_counter()
            app.state.request_count += 1
            try:
                response = await execute_specialist_dispatch(
                    payload=payload,
                    handler=handler,
                )
                app.state.total_response_time_ms += (perf_counter() - start) * 1000
                return response
            except Exception:
                app.state.failure_count += 1
                raise

    return app
