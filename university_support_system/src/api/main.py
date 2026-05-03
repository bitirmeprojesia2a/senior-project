"""FastAPI uygulama giris noktasi."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import timedelta
from functools import lru_cache
from typing import Any

from a2a.types import (
    JSONRPCRequest,
    MessageSendParams,
    Task,
)
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field, ValidationError

from src.a2a.service_identity import (
    A2A_BODY_SHA256_HEADER,
    A2A_CALLER_ID_HEADER,
    A2A_NONCE_HEADER,
    A2A_SIGNATURE_HEADER,
    A2A_TARGET_ID_HEADER,
    A2A_TIMESTAMP_HEADER,
    MAIN_ORCHESTRATOR_SERVICE_ID,
)
from src.a2a.external import (
    ExternalAgentValidationRequest,
    ExternalAgentValidationResult,
    validate_external_agent,
)
from src.a2a.jsonrpc import jsonrpc_error, jsonrpc_success
from src.a2a.tracing import ensure_trace_metadata
from src.agents import AnnouncementAgent
from src.api.a2a_dispatch import (
    A2ADispatchRequest,
    assert_a2a_jsonrpc_access,
    assert_internal_api_access,
)
from src.api.main_a2a import (
    build_main_agent_card as _build_main_agent_card,
    build_main_agent_card_payload as _build_main_agent_card_payload,
    build_main_agent_status_payload,
    build_user_query_response_task as _build_user_query_response_task,
    message_metadata as _message_metadata,
    message_text as _message_text,
)
from src.api.query_flow import (
    build_dispatch_metadata,
    resolve_dispatch_context,
    resolve_query_context,
)
from src.core.config import settings
from src.core.constants import Department
from src.core.profiling import QueryProfiler, activate_profiler, profile_stage
from src.db import (
    AuthService,
    ConversationContextService,
    ProfileContextService,
    TelemetryService,
    dispose_engine,
)
from src.db.schemas import (
    AuthResolvePayload,
    AuthResolveResponse,
    AuthenticatedUserQueryRequest,
    DepartmentResponse,
    LogoutPayload,
    LogoutResponse,
    OTPRequestPayload,
    OTPRequestResponse,
    OTPVerifyPayload,
    OTPVerifyResponse,
    QueryDiagnostics,
    UserQueryResponse,
)
from src.llm.llm_service import LLMService
from src.notifications import EmailDeliveryError
from src.orchestrators.main import MainOrchestrator
from src.startup.warmup import cancel_application_warmup, schedule_application_warmup, warm_application_resources
from src.db.auth_utils import utcnow


class AgentCardSummary(BaseModel):
    """Ajan karti ozeti."""

    agent_id: str
    name: str
    department: str
    description: str
    task_types: list[str]


class SystemHealthPayload(BaseModel):
    """Sistem saglik yaniti."""

    status: str
    app: dict[str, Any]
    llm: dict[str, Any]


class A2AAgentStatus(BaseModel):
    """A2A agent/service registry status payload."""

    agent_id: str
    name: str
    department: str
    role: str
    description: str | None = None
    endpoint: str | None = None
    is_active: bool
    last_heartbeat: str | None = None
    is_stale: bool
    capabilities: dict[str, Any] = Field(default_factory=dict)
    service_build: dict[str, Any] | None = None
    service_runtime_label: str | None = None
    is_published_service: bool = False


class A2ATopologyPayload(BaseModel):
    """A2A topology/admin visibility payload."""

    status: str
    a2a_mode: str
    a2a_transport_protocol: str
    discovery_ttl_seconds: float
    include_internal: bool
    agent_count: int
    active_count: int
    stale_count: int
    agents: list[A2AAgentStatus]


class A2ADiagnosticsOverview(BaseModel):
    """Recent A2A query/task health counters."""

    generated_at: str
    window_minutes: int
    window_started_at: str
    query_count: int
    query_failure_count: int
    agent_task_count: int
    agent_task_failure_count: int
    avg_response_time_ms: float | None = None
    max_response_time_ms: int | None = None


class A2AAgentDiagnostics(BaseModel):
    """Per-agent recent task health summary."""

    agent_id: str
    name: str
    department: str
    role: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    failure_rate: float
    latency_sample_count: int = 0
    avg_latency_ms: float | None = None
    max_latency_ms: float | None = None
    last_error: str | None = None
    last_completed_at: str | None = None


class A2ARecentFailure(BaseModel):
    """Recent failed A2A task sample."""

    task_id: str
    sender_agent_id: str
    receiver_agent_id: str
    status: str
    error: str | None = None
    completed_at: str | None = None
    trace_id: str | None = None
    query_preview: str | None = None


class A2ADiagnosticsPayload(BaseModel):
    """A2A diagnostics/admin visibility payload."""

    status: str
    overview: A2ADiagnosticsOverview
    agents: list[A2AAgentDiagnostics]
    recent_failures: list[A2ARecentFailure]
    error: str | None = None


def _sanitize_llm_health_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Health endpoint icin provider detaylarini minimum seviyeye indirir."""
    primary = payload.get("primary") or {}
    fallback = payload.get("fallback") or {}
    return {
        "status": payload.get("status", "unknown"),
        "primary": {
            "name": primary.get("name"),
            "status": primary.get("status"),
            "model_loaded": primary.get("model_loaded"),
        },
        "fallback": {
            "name": fallback.get("name"),
            "status": fallback.get("status"),
            "available": fallback.get("available", True),
            "model_loaded": fallback.get("model_loaded"),
        },
    }


async def _handle_user_query_payload(
    *,
    payload: AuthenticatedUserQueryRequest,
    orchestrator: MainOrchestrator,
    auth_service: AuthService,
    profile_service: ProfileContextService,
) -> UserQueryResponse:
    resolution = await resolve_query_context(
        payload=payload,
        auth_service=auth_service,
        profile_service=profile_service,
    )
    if resolution.immediate_response is not None:
        return resolution.immediate_response

    return await orchestrator.handle_query(
        payload.query,
        context_id=resolution.context_id,
        user_id=payload.user_id or resolution.resolved["slack_user_id"],
        student_id=resolution.resolved["student_id"],
        student_number=resolution.resolved["student_number"],
        student_full_name=resolution.resolved["full_name"],
        student_department=resolution.resolved["student_department"],
        student_faculty=resolution.resolved["student_faculty"],
        student_type=resolution.resolved["student_type"],
        llm_profile=payload.llm_profile,
        is_authenticated=resolution.resolved["is_authenticated"],
        trace_id=payload.trace_id,
        span_id=payload.span_id,
        parent_span_id=payload.parent_span_id,
        disable_cache=payload.disable_cache,
    )


def _attach_local_query_profile(
    response: UserQueryResponse,
    profiler: QueryProfiler,
) -> UserQueryResponse:
    """Attach API-process profiler data after the full query path completes."""
    diagnostics = response.diagnostics or QueryDiagnostics()
    diagnostics.local_profile = profiler.snapshot()
    response.diagnostics = diagnostics
    return response


async def _handle_main_message_send(
    *,
    params: MessageSendParams,
    orchestrator: MainOrchestrator,
    auth_service: AuthService,
    profile_service: ProfileContextService,
) -> Task:
    message = params.message
    metadata = _message_metadata(params)
    trace = ensure_trace_metadata(metadata)
    query_text = _message_text(message)
    if not query_text:
        raise ValueError("A2A message/send icin text part zorunludur.")
    context_id = message.contextId or str(metadata.get("context_id") or message.messageId)
    payload = AuthenticatedUserQueryRequest(
        query=query_text,
        user_id=metadata.get("user_id"),
        context_id=context_id,
        student_id=metadata.get("student_id"),
        full_name=metadata.get("full_name") or metadata.get("student_full_name"),
        student_number=metadata.get("student_number"),
        student_department=metadata.get("student_department"),
        student_faculty=metadata.get("student_faculty"),
        student_type=metadata.get("student_type"),
        llm_profile=metadata.get("llm_profile"),
        is_authenticated=bool(metadata.get("is_authenticated", False)),
        session_token=metadata.get("session_token"),
        slack_user_id=metadata.get("slack_user_id"),
        trace_id=trace.get("trace_id"),
        span_id=trace.get("span_id"),
        parent_span_id=trace.get("parent_span_id"),
    )
    response = await _handle_user_query_payload(
        payload=payload,
        orchestrator=orchestrator,
        auth_service=auth_service,
        profile_service=profile_service,
    )
    return _build_user_query_response_task(response, request_message=message, trace=trace)


def _build_generic_otp_request_response() -> OTPRequestResponse:
    """Enumeration riskini azaltmak icin standart OTP yaniti."""
    expires_at = (utcnow() + timedelta(minutes=settings.auth.otp_ttl_minutes)).isoformat()
    return OTPRequestResponse(
        success=True,
        message=(
            "Bilgileriniz dogruysa dogrulama kodu ogrenci e-posta adresinize gonderilecektir. "
            "Lutfen e-posta kutunuzu kontrol edin."
        ),
        expires_at=expires_at,
        delivery_channel="email_smtp",
    )


@lru_cache
def get_main_orchestrator() -> MainOrchestrator:
    return MainOrchestrator(
        conversation_service=ConversationContextService(),
    )


@lru_cache
def get_llm_service() -> LLMService:
    return LLMService()


@lru_cache
def get_auth_service() -> AuthService:
    return AuthService()


@lru_cache
def get_profile_context_service() -> ProfileContextService:
    return ProfileContextService()


@lru_cache
def get_telemetry_service() -> TelemetryService:
    return TelemetryService()


@lru_cache
def get_agent_card_summaries() -> list[AgentCardSummary]:
    orchestrators = get_main_orchestrator().department_orchestrators
    unique: dict[str, AgentCardSummary] = {}
    for department, orchestrator in orchestrators.items():
        if not hasattr(orchestrator, "agents"):
            unique[f"{department.value}_remote_service"] = AgentCardSummary(
                agent_id=f"{department.value}_remote_service",
                name=f"{department.display_name} Remote A2A Service",
                department=department.value,
                description="HTTP A2A transport ile cagrilan ayrik departman servisi.",
                task_types=[],
            )
            continue
        agents = [
            *orchestrator.agents.values(),
            orchestrator.fallback_agent,
        ]
        for agent in agents:
            unique[agent.agent_id] = AgentCardSummary(
                agent_id=agent.agent_id,
                name=agent.definition.name,
                department=agent.department.value,
                description=agent.definition.description,
                task_types=[task_type.value for task_type in agent.definition.task_types],
            )
    announcement_agent = AnnouncementAgent()
    unique[announcement_agent.agent_id] = AgentCardSummary(
        agent_id=announcement_agent.agent_id,
        name=announcement_agent.definition.name,
        department=announcement_agent.department.value,
        description=announcement_agent.definition.description,
        task_types=[task_type.value for task_type in announcement_agent.definition.task_types],
    )
    return list(unique.values())


@asynccontextmanager
async def _app_lifespan(app: FastAPI):
    _ = app
    warmup_task = None
    if settings.server.warmup_enabled:
        get_main_orchestrator()
        warmup_task = schedule_application_warmup(
            lambda: warm_application_resources(llm_service=get_llm_service()),
            label="api",
        )
    try:
        yield
    finally:
        await cancel_application_warmup(warmup_task)
        await dispose_engine()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Universite Kurumsal Destek Sistemi",
        version=settings.server.app_version,
        description=(
            "RAG, LLM, auth, router ve uygulama ici A2A orkestrasyonu uzerinden "
            "universite destek sorgularini cevaplayan API."
        ),
        lifespan=_app_lifespan,
    )

    @app.get("/", tags=["system"])
    async def root() -> dict[str, Any]:
        return {
            "name": "university-support-system",
            "status": "ok",
            "version": settings.server.app_version,
            "build": settings.server.build_metadata(),
            "features": [
                "rag",
                "llm",
                "department-router",
                "internal-a2a",
                "otp-auth",
            ],
        }

    @app.get("/health", response_model=SystemHealthPayload, tags=["system"])
    async def health(llm_service: LLMService = Depends(get_llm_service)) -> SystemHealthPayload:
        llm_health = await llm_service.get_health()
        overall_status = llm_health.get("status", "unknown")
        return SystemHealthPayload(
            status=overall_status,
            app={
                "api": "healthy",
                "build": settings.server.build_metadata(),
                "runtime": {
                    "label": settings.server.runtime_label,
                    "llm_profile": settings.normalize_llm_profile(settings.llm.profile),
                },
                "active_departments": [department.value for department in Department],
                "a2a_mode": settings.a2a.mode,
                "a2a_transport_protocol": settings.a2a.transport_protocol,
                "auth_mode": "otp_session",
            },
            llm=_sanitize_llm_health_payload(llm_health),
        )

    @app.get("/agents", response_model=list[AgentCardSummary], tags=["agents"])
    async def list_agents(cards: list[AgentCardSummary] = Depends(get_agent_card_summaries)) -> list[AgentCardSummary]:
        return cards

    @app.get("/agent-card", tags=["a2a"])
    async def main_agent_card() -> dict[str, Any]:
        return _build_main_agent_card_payload()

    @app.get("/.well-known/agent.json", tags=["a2a"])
    async def well_known_main_agent_json() -> dict[str, Any]:
        return _build_main_agent_card().model_dump(mode="json", exclude_none=True)

    @app.get("/.well-known/agent-card.json", tags=["a2a"])
    async def well_known_main_agent_card_json() -> dict[str, Any]:
        return _build_main_agent_card().model_dump(mode="json", exclude_none=True)

    @app.get("/a2a/topology", response_model=A2ATopologyPayload, tags=["a2a"])
    async def a2a_topology(
        include_internal: bool = Query(
            default=False,
            description=(
                "True ise local/internal specialist registry kayitlari da listelenir. "
                "False iken yalniz endpoint'i olan A2A servisleri dondurulur."
            ),
        ),
        telemetry_service: TelemetryService = Depends(get_telemetry_service),
    ) -> A2ATopologyPayload:
        registry_agents = [
            A2AAgentStatus(**row)
            for row in await telemetry_service.list_registered_agents(
                include_internal=include_internal,
            )
        ]
        agents = [
            A2AAgentStatus(**build_main_agent_status_payload()),
            *[
                agent
                for agent in registry_agents
                if agent.agent_id != "main_orchestrator"
            ],
        ]
        active_count = sum(1 for agent in agents if agent.is_active)
        stale_count = sum(1 for agent in agents if agent.is_stale)
        return A2ATopologyPayload(
            status="ok",
            a2a_mode=settings.a2a.mode,
            a2a_transport_protocol=settings.a2a.transport_protocol,
            discovery_ttl_seconds=settings.a2a.discovery_ttl_seconds,
            include_internal=include_internal,
            agent_count=len(agents),
            active_count=active_count,
            stale_count=stale_count,
            agents=agents,
        )

    @app.get("/a2a/diagnostics", response_model=A2ADiagnosticsPayload, tags=["a2a"])
    async def a2a_diagnostics(
        window_minutes: int = Query(
            default=60,
            ge=1,
            le=24 * 60,
            description="Recent diagnostics window in minutes.",
        ),
        recent_limit: int = Query(
            default=10,
            ge=0,
            le=50,
            description="Maximum recent failed A2A task samples.",
        ),
        telemetry_service: TelemetryService = Depends(get_telemetry_service),
    ) -> A2ADiagnosticsPayload:
        return A2ADiagnosticsPayload(
            **await telemetry_service.get_a2a_diagnostics(
                window_minutes=window_minutes,
                recent_limit=recent_limit,
            )
        )

    @app.post("/auth/request-otp", response_model=OTPRequestResponse, tags=["auth"])
    async def request_otp(
        payload: OTPRequestPayload,
        auth_service: AuthService = Depends(get_auth_service),
    ) -> OTPRequestResponse:
        try:
            otp_result = await auth_service.request_otp(
                student_number=payload.student_number,
                slack_user_id=payload.slack_user_id,
            )
        except EmailDeliveryError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        if otp_result is None or not otp_result.get("success", True):
            return _build_generic_otp_request_response()

        return _build_generic_otp_request_response()

    @app.post("/auth/verify-otp", response_model=OTPVerifyResponse, tags=["auth"])
    async def verify_otp(
        payload: OTPVerifyPayload,
        auth_service: AuthService = Depends(get_auth_service),
    ) -> OTPVerifyResponse:
        result = await auth_service.verify_otp(
            student_number=payload.student_number,
            otp_code=payload.otp_code,
            slack_user_id=payload.slack_user_id,
        )
        if result is None or not result["success"]:
            raise HTTPException(
                status_code=400,
                detail="Ogrenci numarasi veya dogrulama kodu gecersiz.",
            )

        return OTPVerifyResponse(
            success=True,
            message="OTP dogrulandi.",
            student_id=result["student_db_id"],
            student_number=result["student_number"],
            full_name=result["full_name"],
            student_department=result["student_department"],
            student_faculty=result["student_faculty"],
            is_authenticated=True,
            session_token=result["session_token"],
            expires_at=result["expires_at"].isoformat(),
        )

    @app.post("/auth/resolve", response_model=AuthResolveResponse, tags=["auth"])
    async def resolve_auth(
        payload: AuthResolvePayload,
        auth_service: AuthService = Depends(get_auth_service),
        x_internal_api_key: str | None = Header(default=None, alias="X-Internal-API-Key"),
    ) -> AuthResolveResponse:
        if not payload.session_token and not payload.slack_user_id:
            raise HTTPException(status_code=400, detail="session_token veya slack_user_id gereklidir.")
        if payload.slack_user_id and not payload.session_token:
            assert_internal_api_access(x_internal_api_key)

        resolved = await auth_service.resolve_auth_context(
            session_token=payload.session_token,
            slack_user_id=payload.slack_user_id,
        )
        if resolved is None:
            raise HTTPException(status_code=404, detail="Aktif dogrulama baglami bulunamadi.")

        return AuthResolveResponse(
            is_authenticated=True,
            student_id=resolved.student_db_id,
            student_number=resolved.student_number,
            full_name=resolved.full_name,
            student_department=resolved.student_department,
            student_faculty=resolved.student_faculty,
            slack_user_id=resolved.slack_user_id,
            session_token=resolved.session_token,
            expires_at=resolved.expires_at.isoformat() if resolved.expires_at else None,
        )

    @app.post("/auth/logout", response_model=LogoutResponse, tags=["auth"])
    async def logout(
        payload: LogoutPayload,
        auth_service: AuthService = Depends(get_auth_service),
    ) -> LogoutResponse:
        invalidated = await auth_service.invalidate_session(payload.session_token)
        if not invalidated:
            raise HTTPException(status_code=404, detail="Oturum bulunamadi.")
        return LogoutResponse(success=True, message="Oturum kapatildi.")

    @app.post("/query", response_model=UserQueryResponse, tags=["query"])
    async def query(
        payload: AuthenticatedUserQueryRequest,
        orchestrator: MainOrchestrator = Depends(get_main_orchestrator),
        auth_service: AuthService = Depends(get_auth_service),
        profile_service: ProfileContextService = Depends(get_profile_context_service),
    ) -> UserQueryResponse:
        profiler = QueryProfiler(label=f"api.query:{payload.context_id or 'anonymous'}")
        with activate_profiler(profiler):
            with profile_stage("api.query"):
                response = await _handle_user_query_payload(
                    payload=payload,
                    orchestrator=orchestrator,
                    auth_service=auth_service,
                    profile_service=profile_service,
                )
        return _attach_local_query_profile(response, profiler)

    @app.post("/a2a", tags=["a2a"])
    async def jsonrpc_main_a2a(
        payload: dict[str, Any],
        orchestrator: MainOrchestrator = Depends(get_main_orchestrator),
        auth_service: AuthService = Depends(get_auth_service),
        profile_service: ProfileContextService = Depends(get_profile_context_service),
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
            expected_target_id=MAIN_ORCHESTRATOR_SERVICE_ID,
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
            response_task = await _handle_main_message_send(
                params=params,
                orchestrator=orchestrator,
                auth_service=auth_service,
                profile_service=profile_service,
            )
        except (ValidationError, ValueError) as exc:
            return jsonrpc_error(
                request.id,
                code=-32602,
                message="Invalid message/send params.",
                data=str(exc),
            )
        except Exception as exc:
            return jsonrpc_error(
                request.id,
                code=-32000,
                message="A2A main orchestrator execution failed.",
                data=str(exc),
            )
        return jsonrpc_success(
            request,
            response_task.model_dump(mode="json", exclude_none=True),
        )

    @app.post(
        "/a2a/external/validate",
        response_model=ExternalAgentValidationResult,
        tags=["a2a"],
    )
    async def validate_external_a2a_agent(
        payload: ExternalAgentValidationRequest,
        x_internal_api_key: str | None = Header(default=None, alias="X-Internal-API-Key"),
    ) -> ExternalAgentValidationResult:
        assert_internal_api_access(x_internal_api_key)
        return await validate_external_agent(payload)

    @app.post("/a2a/dispatch", response_model=DepartmentResponse, tags=["a2a"])
    async def dispatch_task(
        payload: A2ADispatchRequest,
        orchestrator: MainOrchestrator = Depends(get_main_orchestrator),
        auth_service: AuthService = Depends(get_auth_service),
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
            expected_target_id=MAIN_ORCHESTRATOR_SERVICE_ID,
            request_body=payload.model_dump(mode="json"),
            request_timestamp=x_a2a_timestamp,
            request_nonce=x_a2a_nonce,
            request_body_sha256=x_a2a_body_sha256,
            request_signature=x_a2a_signature,
        )
        department_orchestrator = orchestrator.department_orchestrators.get(payload.department)
        if department_orchestrator is None:
            raise HTTPException(
                status_code=404,
                detail=f"{payload.department.value} icin aktif departman orkestratoru bulunamadi.",
            )

        context_id, resolved = await resolve_dispatch_context(
            payload=payload,
            auth_service=auth_service,
        )

        return await department_orchestrator.handle(
            query_text=payload.query,
            context_id=context_id,
            task_type=payload.task_type,
            metadata=build_dispatch_metadata(payload=payload, resolved=resolved),
        )

    return app


app = create_app()
