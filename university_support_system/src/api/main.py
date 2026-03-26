"""FastAPI uygulama giris noktasi."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.agents import AnnouncementAgent
from src.core.constants import Department, TaskType
from src.db import AuthService
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
from src.orchestrators.main import MainOrchestrator


class A2ADispatchRequest(BaseModel):
    """Uygulama ici A2A gorev gonderim semasi."""

    department: Department = Field(..., description="Hedef departman")
    query: str = Field(..., min_length=1, max_length=500, description="Kullanici sorgusu")
    context_id: str | None = Field(default=None, description="Konusma baglam kimligi")
    user_id: str | None = Field(default=None, description="Kullanici kimligi")
    student_id: int | None = Field(default=None, description="Dogrulanmis ogrenci veritabani kimligi")
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
    return MainOrchestrator()


@lru_cache
def get_llm_service() -> LLMService:
    return LLMService()


@lru_cache
def get_auth_service() -> AuthService:
    return AuthService()


@lru_cache
def get_agent_card_summaries() -> list[AgentCardSummary]:
    orchestrators = MainOrchestrator()._build_default_orchestrators()
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


async def _resolve_auth_inputs(
    *,
    student_id: int | None,
    is_authenticated: bool,
    session_token: str | None,
    slack_user_id: str | None,
    auth_service: AuthService,
) -> tuple[int | None, bool, str | None]:
    """Gelen API istegi icin auth baglamini cozumler."""

    if student_id is not None and is_authenticated:
        return student_id, True, slack_user_id

    if session_token:
        resolved = await auth_service.resolve_auth_context(session_token=session_token)
        if resolved is None:
            raise HTTPException(status_code=401, detail="Gecersiz veya suresi dolmus oturum.")
        return resolved.student_db_id, True, resolved.slack_user_id or slack_user_id

    if slack_user_id:
        resolved = await auth_service.resolve_auth_context(slack_user_id=slack_user_id)
        if resolved is not None:
            return resolved.student_db_id, True, resolved.slack_user_id

    return student_id, is_authenticated, slack_user_id


def create_app() -> FastAPI:
    app = FastAPI(
        title="Universite Kurumsal Destek Sistemi",
        version="1.0.0",
        description=(
            "RAG, LLM, auth, router ve uygulama ici A2A orkestrasyonu uzerinden "
            "universite destek sorgularini cevaplayan API."
        ),
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
        otp_result = await auth_service.request_otp(
            student_number=payload.student_number,
            slack_user_id=payload.slack_user_id,
        )
        if otp_result is None:
            raise HTTPException(status_code=404, detail="Ogrenci numarasi bulunamadi.")

        return OTPRequestResponse(
            success=True,
            message="OTP kodu olusturuldu. E-posta gonderimi su an stub modunda.",
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
    ) -> UserQueryResponse:
        resolved_student_id, resolved_auth, resolved_slack_user_id = await _resolve_auth_inputs(
            student_id=payload.student_id,
            is_authenticated=payload.is_authenticated,
            session_token=payload.session_token,
            slack_user_id=payload.slack_user_id,
            auth_service=auth_service,
        )
        return await orchestrator.handle_query(
            payload.query,
            context_id=payload.context_id,
            user_id=payload.user_id or resolved_slack_user_id,
            student_id=resolved_student_id,
            is_authenticated=resolved_auth,
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

        resolved_student_id, resolved_auth, resolved_slack_user_id = await _resolve_auth_inputs(
            student_id=payload.student_id,
            is_authenticated=payload.is_authenticated,
            session_token=payload.session_token,
            slack_user_id=payload.slack_user_id,
            auth_service=auth_service,
        )

        return await department_orchestrator.handle(
            query_text=payload.query,
            context_id=payload.context_id or "api-a2a-context",
            task_type=payload.task_type,
            metadata={
                "user_id": payload.user_id or resolved_slack_user_id,
                "student_id": resolved_student_id,
                "is_authenticated": resolved_auth,
                "routing_reason": "api_a2a_dispatch",
            },
        )

    return app


app = create_app()
