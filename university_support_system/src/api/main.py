"""FastAPI uygulama giris noktasi."""

from __future__ import annotations

from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.agents import AnnouncementAgent
from src.api.query_flow import (
    build_dispatch_metadata,
    resolve_dispatch_context,
    resolve_query_context,
)
from src.core.config import settings
from src.core.constants import Department, TaskType
from src.db import (
    AuthService,
    ConversationContextService,
    ProfileContextService,
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
    UserQueryResponse,
)
from src.llm.llm_service import LLMService
from src.notifications import EmailDeliveryError
from src.orchestrators.main import MainOrchestrator
from src.rag.warmup import warm_retrieval_resources


class A2ADispatchRequest(BaseModel):
    """Uygulama ici A2A gorev gonderim semasi."""

    department: Department = Field(..., description="Hedef departman")
    query: str = Field(..., min_length=1, max_length=500, description="Kullanici sorgusu")
    context_id: str | None = Field(default=None, description="Konusma baglam kimligi")
    user_id: str | None = Field(default=None, description="Kullanici kimligi")
    full_name: str | None = Field(default=None, description="Kullanicinin ad soyad bilgisi")
    student_number: str | None = Field(default=None, description="Kullanicinin ogrenci numarasi")
    student_id: int | None = Field(default=None, description="Dogrulanmis ogrenci veritabani kimligi")
    student_department: str | None = Field(default=None, description="Ogrencinin bolum veya program bilgisi")
    student_faculty: str | None = Field(default=None, description="Ogrencinin fakulte bilgisi")
    student_type: str | None = Field(default=None, description="Ogrenci tipi veya uyruk bilgisi")
    llm_profile: str | None = Field(default=None, description="LLM profil tercihi: fast, balanced veya quality")
    is_authenticated: bool = Field(default=False, description="Kimlik dogrulama durumu")
    session_token: str | None = Field(default=None, description="Dogrulama oturum anahtari")
    slack_user_id: str | None = Field(default=None, description="Slack kullanici kimligi")
    task_type: TaskType | None = Field(default=None, description="Zorlanmis gorev tipi")


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
def get_agent_card_summaries() -> list[AgentCardSummary]:
    orchestrators = get_main_orchestrator().department_orchestrators
    agents = [
        *orchestrators[Department.STUDENT_AFFAIRS].agents.values(),
        orchestrators[Department.STUDENT_AFFAIRS].fallback_agent,
        *orchestrators[Department.ACADEMIC_PROGRAMS].agents.values(),
        orchestrators[Department.ACADEMIC_PROGRAMS].fallback_agent,
        *orchestrators[Department.FINANCE].agents.values(),
        orchestrators[Department.FINANCE].fallback_agent,
        AnnouncementAgent(),
    ]

    unique: dict[str, AgentCardSummary] = {}
    for agent in agents:
        unique[agent.agent_id] = AgentCardSummary(
            agent_id=agent.agent_id,
            name=agent.definition.name,
            department=agent.department.value,
            description=agent.definition.description,
            task_types=[task_type.value for task_type in agent.definition.task_types],
        )
    return list(unique.values())


@asynccontextmanager
async def _app_lifespan(app: FastAPI):
    _ = app
    if settings.server.warmup_enabled:
        get_main_orchestrator()
        get_llm_service()
        warm_retrieval_resources()
    try:
        yield
    finally:
        await dispose_engine()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Universite Kurumsal Destek Sistemi",
        version="1.0.0",
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
                "active_departments": [department.value for department in Department],
                "a2a_mode": "internal",
                "auth_mode": "otp_session",
            },
            llm=llm_health,
        )

    @app.get("/agents", response_model=list[AgentCardSummary], tags=["agents"])
    async def list_agents(cards: list[AgentCardSummary] = Depends(get_agent_card_summaries)) -> list[AgentCardSummary]:
        return cards

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
        if otp_result is None:
            raise HTTPException(status_code=404, detail="Ogrenci numarasi bulunamadi.")
        if not otp_result.get("success", True):
            raise HTTPException(status_code=400, detail=otp_result["message"])

        return OTPRequestResponse(
            success=True,
            message="Dogrulama kodu ogrenci e-posta adresinize gonderildi.",
            student_number=otp_result["student_number"],
            masked_email=otp_result["masked_email"],
            expires_at=otp_result["expires_at"].isoformat(),
            delivery_channel=otp_result["delivery_channel"],
            otp_preview_code=otp_result["otp_preview_code"],
        )

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
        if result is None:
            raise HTTPException(status_code=404, detail="Ogrenci numarasi bulunamadi.")
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

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
    ) -> AuthResolveResponse:
        if not payload.session_token and not payload.slack_user_id:
            raise HTTPException(status_code=400, detail="session_token veya slack_user_id gereklidir.")

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
        )

    @app.post("/a2a/dispatch", response_model=DepartmentResponse, tags=["a2a"])
    async def dispatch_task(
        payload: A2ADispatchRequest,
        orchestrator: MainOrchestrator = Depends(get_main_orchestrator),
        auth_service: AuthService = Depends(get_auth_service),
    ) -> DepartmentResponse:
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
