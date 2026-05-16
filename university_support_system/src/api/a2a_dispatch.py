"""Shared request schema and access control for internal A2A dispatch."""

from __future__ import annotations

from hmac import compare_digest
from typing import Any

from fastapi import HTTPException
from pydantic import BaseModel, Field

from src.a2a.external import authorize_external_a2a_request
from src.a2a.service_identity import (
    default_a2a_replay_cache,
    verify_a2a_request_signature,
)
from src.core.config import settings
from src.core.constants import Capability, Department, TaskType


class A2ADispatchRequest(BaseModel):
    """Internal A2A department dispatch request."""

    department: Department = Field(..., description="Hedef departman")
    query: str = Field(..., min_length=1, max_length=1000, description="Kullanici sorgusu")
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
    original_query: str | None = Field(default=None, description="Kullanicinin ham sorgusu")
    resolved_query: str | None = Field(default=None, description="Konusma baglami ile cozulmus sorgu")
    conversation_is_follow_up: bool = Field(default=False, description="Takip sorusu mu")
    conversation_topic: str | None = Field(default=None, description="Aktif konusma konusu")
    conversation_source_refs: list[str] = Field(default_factory=list, description="Konusma kaynak referanslari")
    force_llm_synthesis: bool = Field(default=False, description="LLM sentezini zorla")
    query_complexity: str | None = Field(default=None, description="Routing niyet karmasikligi")
    is_personal_query: bool = Field(default=False, description="Kisisel veri sorgusu mu")
    final_answer_owner: str | None = Field(default=None, description="Nihai cevap yazimi sahibi")
    specialist_response_mode: str | None = Field(default=None, description="Uzman ajan cevap modu")
    capability_planner: dict[str, Any] | None = Field(default=None, description="Capability planner payload")
    source_owner: dict[str, Any] | None = Field(default=None, description="Source ownership registry payload")
    policy_facet: dict[str, Any] | None = Field(default=None, description="Policy facet contract payload")
    decision_contract: dict[str, Any] | None = Field(default=None, description="Read-only runtime decision contract")
    resolved_decision: dict[str, Any] | None = Field(default=None, description="Resolved runtime decision authority payload")
    runtime_authority: dict[str, Any] | None = Field(default=None, description="Active runtime authority payload")
    branch_dispatch_gate: dict[str, Any] | None = Field(default=None, description="Branch dispatch gate diagnostics")
    branch_role: str | None = Field(default=None, description="Retrieval execution branch role")
    retrieval_execution_policy: dict[str, Any] | None = Field(default=None, description="Retrieval execution budget policy")
    disable_specialist_llm: bool = Field(default=False, description="Uzman LLM sentezini devre disi birak")
    trace_id: str | None = Field(default=None, description="A2A izleme korelasyon kimligi")
    span_id: str | None = Field(default=None, description="A2A hop/span kimligi")
    parent_span_id: str | None = Field(default=None, description="Ust A2A hop/span kimligi")


class CapabilityDispatchRequest(BaseModel):
    """Internal A2A capability dispatch request."""

    capability: Capability = Field(..., description="Hedef capability agent")
    query: str = Field(..., min_length=1, max_length=1000, description="Kullanici sorgusu")
    context_id: str | None = Field(default=None, description="Konusma baglam kimligi")
    routing_reason: str | None = Field(default=None, description="Yonlendirme gerekcesi")
    departments: list[str] = Field(default_factory=list, description="Announcement filtre departmanlari")
    faculty: str | None = Field(default=None, description="Fakulte filtresi")
    unit_name: str | None = Field(default=None, description="Birim filtresi")
    conversation_source_refs: list[str] = Field(default_factory=list, description="Konusma kaynak referanslari")
    allow_latest_fallback: bool = Field(default=True, description="Announcement latest fallback izni")
    probe_mode: str | None = Field(default=None, description="Announcement probe modu")
    require_keyword_match: bool = Field(default=False, description="Keyword eslesmesi zorunlu mu")
    minimum_match_score: int | None = Field(default=None, ge=0, description="Minimum keyword skor esigi")
    recent_days: int | None = Field(default=None, ge=1, le=730, description="Duyuru gunellik penceresi")
    limit: int = Field(default=5, ge=1, le=20, description="Maksimum sonuc sayisi")
    decision_contract: dict[str, Any] | None = Field(default=None, description="Read-only runtime decision contract")
    resolved_decision: dict[str, Any] | None = Field(default=None, description="Resolved runtime decision authority payload")
    runtime_authority: dict[str, Any] | None = Field(default=None, description="Active runtime authority payload")
    trace_id: str | None = Field(default=None, description="A2A izleme korelasyon kimligi")
    span_id: str | None = Field(default=None, description="A2A hop/span kimligi")
    parent_span_id: str | None = Field(default=None, description="Ust A2A hop/span kimligi")


class SpecialistDispatchRequest(BaseModel):
    """Internal A2A specialist-agent dispatch request."""

    department: Department = Field(..., description="Uzman ajanin departmani")
    agent_id: str = Field(..., min_length=1, max_length=120, description="Hedef uzman ajan kimligi")
    query: str = Field(..., min_length=1, max_length=1000, description="Kullanici sorgusu")
    context_id: str | None = Field(default=None, description="Konusma baglam kimligi")
    task_type: TaskType | None = Field(default=None, description="Zorlanmis gorev tipi")
    student_id: int | None = Field(default=None, description="Dogrulanmis ogrenci veritabani kimligi")
    student_department: str | None = Field(default=None, description="Ogrencinin bolum veya program bilgisi")
    student_faculty: str | None = Field(default=None, description="Ogrencinin fakulte bilgisi")
    student_type: str | None = Field(default=None, description="Ogrenci tipi veya uyruk bilgisi")
    llm_profile: str | None = Field(default=None, description="LLM profil tercihi")
    is_authenticated: bool = Field(default=False, description="Kimlik dogrulama durumu")
    original_query: str | None = Field(default=None, description="Kullanicinin ham sorgusu")
    resolved_query: str | None = Field(default=None, description="Konusma baglami ile cozulmus sorgu")
    conversation_is_follow_up: bool = Field(default=False, description="Takip sorusu mu")
    conversation_topic: str | None = Field(default=None, description="Aktif konusma konusu")
    conversation_source_refs: list[str] = Field(default_factory=list, description="Konusma kaynak referanslari")
    force_llm_synthesis: bool = Field(default=False, description="LLM sentezini zorla")
    query_complexity: str | None = Field(default=None, description="Routing niyet karmasikligi")
    is_personal_query: bool = Field(default=False, description="Kisisel veri sorgusu mu")
    final_answer_owner: str | None = Field(default=None, description="Nihai cevap yazimi sahibi")
    specialist_response_mode: str | None = Field(default=None, description="Uzman ajan cevap modu")
    capability_planner: dict[str, Any] | None = Field(default=None, description="Capability planner payload")
    source_owner: dict[str, Any] | None = Field(default=None, description="Source ownership registry payload")
    policy_facet: dict[str, Any] | None = Field(default=None, description="Policy facet contract payload")
    decision_contract: dict[str, Any] | None = Field(default=None, description="Read-only runtime decision contract")
    resolved_decision: dict[str, Any] | None = Field(default=None, description="Resolved runtime decision authority payload")
    runtime_authority: dict[str, Any] | None = Field(default=None, description="Active runtime authority payload")
    specialist_selection: dict[str, Any] | None = Field(default=None, description="Specialist selector decision diagnostics")
    branch_dispatch_gate: dict[str, Any] | None = Field(default=None, description="Branch dispatch gate diagnostics")
    branch_role: str | None = Field(default=None, description="Retrieval execution branch role")
    retrieval_execution_policy: dict[str, Any] | None = Field(default=None, description="Retrieval execution budget policy")
    disable_specialist_llm: bool = Field(default=False, description="Uzman LLM sentezini devre disi birak")
    trace_id: str | None = Field(default=None, description="A2A izleme korelasyon kimligi")
    span_id: str | None = Field(default=None, description="A2A hop/span kimligi")
    parent_span_id: str | None = Field(default=None, description="Ust A2A hop/span kimligi")


def _clean_service_id(value: str | None) -> str | None:
    cleaned = (value or "").strip()
    return cleaned or None


def assert_internal_api_access(
    api_key: str | None,
    *,
    caller_id: str | None = None,
    target_id: str | None = None,
    expected_target_id: str | None = None,
    request_body: object | None = None,
    request_timestamp: str | None = None,
    request_nonce: str | None = None,
    request_body_sha256: str | None = None,
    request_signature: str | None = None,
) -> None:
    """Validate access for internal-only endpoints.

    A2A endpoints pass `expected_target_id`, which enables optional service
    identity policy in addition to the shared internal secret.
    """
    configured_key = settings.server.internal_api_key or settings.a2a.internal_api_key
    if not configured_key:
        raise HTTPException(
            status_code=503,
            detail="Internal API erisimi bu ortamda etkinlestirilmemis.",
        )
    if not api_key or not compare_digest(api_key, configured_key):
        raise HTTPException(status_code=403, detail="Internal API erisimi reddedildi.")

    expected_target = _clean_service_id(expected_target_id)
    if expected_target is None:
        return

    caller = _clean_service_id(caller_id)
    target = _clean_service_id(target_id)
    allowed_callers = settings.a2a.allowed_caller_id_set()

    if settings.a2a.require_service_identity and caller is None:
        raise HTTPException(status_code=403, detail="A2A caller identity eksik.")
    if allowed_callers and (caller is None or caller not in allowed_callers):
        raise HTTPException(status_code=403, detail="A2A caller identity izinli degil.")
    if target is not None and target != expected_target:
        raise HTTPException(status_code=403, detail="A2A target identity eslesmedi.")

    if not settings.a2a.require_request_signature:
        return

    signature_secret = settings.a2a.resolved_request_signature_secret(configured_key)
    if not signature_secret:
        raise HTTPException(
            status_code=503,
            detail="A2A request signature secret bu ortamda etkinlestirilmemis.",
        )
    if request_body is None:
        raise HTTPException(status_code=403, detail="A2A request body imzasi dogrulanamadi.")

    ok, detail = verify_a2a_request_signature(
        body=request_body,
        secret=signature_secret,
        caller_id=caller,
        target_id=target,
        timestamp=request_timestamp,
        nonce=request_nonce,
        body_sha256=request_body_sha256,
        signature=request_signature,
        ttl_seconds=settings.a2a.request_signature_ttl_seconds,
        replay_cache=default_a2a_replay_cache(),
    )
    if not ok:
        raise HTTPException(status_code=403, detail=detail)


def assert_a2a_jsonrpc_access(
    api_key: str | None,
    *,
    caller_id: str | None = None,
    target_id: str | None = None,
    expected_target_id: str | None = None,
    request_body: object | None = None,
    request_timestamp: str | None = None,
    request_nonce: str | None = None,
    request_body_sha256: str | None = None,
    request_signature: str | None = None,
) -> None:
    """Validate access for standard JSON-RPC A2A endpoints.

    Internal callers continue to use the existing internal API key policy.
    External partner agents must use explicit A2A external trust configuration
    and signed caller identity headers; legacy `/a2a/dispatch` remains internal-only.
    """
    if api_key:
        assert_internal_api_access(
            api_key,
            caller_id=caller_id,
            target_id=target_id,
            expected_target_id=expected_target_id,
            request_body=request_body,
            request_timestamp=request_timestamp,
            request_nonce=request_nonce,
            request_body_sha256=request_body_sha256,
            request_signature=request_signature,
        )
        return

    ok, detail = authorize_external_a2a_request(
        caller_id=caller_id,
        target_id=target_id,
        expected_target_id=expected_target_id,
        request_body=request_body,
        request_timestamp=request_timestamp,
        request_nonce=request_nonce,
        request_body_sha256=request_body_sha256,
        request_signature=request_signature,
    )
    if ok:
        return

    if detail == "external_trust_disabled":
        assert_internal_api_access(
            api_key,
            caller_id=caller_id,
            target_id=target_id,
            expected_target_id=expected_target_id,
            request_body=request_body,
            request_timestamp=request_timestamp,
            request_nonce=request_nonce,
            request_body_sha256=request_body_sha256,
            request_signature=request_signature,
        )
    raise HTTPException(status_code=403, detail=f"External A2A erisimi reddedildi: {detail}")
