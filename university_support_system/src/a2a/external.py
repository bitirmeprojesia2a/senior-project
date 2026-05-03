"""External A2A partner trust and AgentCard validation helpers."""

from __future__ import annotations

from typing import Any, Literal

import httpx
from pydantic import BaseModel, Field

from src.a2a.discovery import A2AAgentCardCheck
from src.a2a.service_identity import (
    default_a2a_replay_cache,
    verify_a2a_request_signature,
)
from src.core.config import settings


class ExternalAgentValidationRequest(BaseModel):
    """Admin request for validating an external A2A partner agent."""

    agent_id: str = Field(..., min_length=1, max_length=160)
    endpoint: str | None = Field(default=None, description="Partner service base URL or /a2a URL.")
    expected_target_kind: str | None = Field(default=None, max_length=80)
    expected_target: str | None = Field(default=None, max_length=160)
    transport_protocol: Literal["rest", "jsonrpc"] | None = None


class ExternalAgentValidationResult(BaseModel):
    """Result of external A2A partner trust validation."""

    trusted: bool
    reason: str
    agent_id: str
    endpoint: str | None = None
    card_url: str | None = None
    transport_protocol: Literal["rest", "jsonrpc"] | None = None
    card: dict[str, Any] | None = None


def clean_external_agent_id(value: str | None) -> str | None:
    """Normalize an external caller/agent id."""
    cleaned = (value or "").strip()
    return cleaned or None


def is_external_agent_allowed(agent_id: str | None) -> bool:
    """Return whether `agent_id` is explicitly trusted by configuration."""
    cleaned = clean_external_agent_id(agent_id)
    return bool(cleaned and cleaned in settings.a2a.external_allowed_agent_id_set())


def _normalize_url(value: str | None) -> str:
    return (value or "").strip().rstrip("/")


def _service_base_url(endpoint: str) -> str:
    base = _normalize_url(endpoint)
    if base.endswith("/a2a"):
        return base[:-4].rstrip("/")
    return base


def _message_url(endpoint: str) -> str:
    base = _normalize_url(endpoint)
    if base.endswith("/a2a"):
        return base
    return f"{base}/a2a"


def _candidate_card_urls(endpoint: str) -> list[str]:
    base = _service_base_url(endpoint)
    return [
        f"{base}/.well-known/agent.json",
        f"{base}/.well-known/agent-card.json",
        f"{base}/agent-card",
    ]


def _skill_tags(card: dict[str, Any]) -> set[str]:
    tags: set[str] = set()
    skills = card.get("skills") or []
    if not isinstance(skills, list):
        return tags
    for skill in skills:
        if not isinstance(skill, dict):
            continue
        for tag in skill.get("tags") or []:
            if isinstance(tag, str) and tag.strip():
                tags.add(tag.strip())
    return tags


def _card_capabilities(card: dict[str, Any]) -> dict[str, Any]:
    capabilities = card.get("capabilities") or {}
    return capabilities if isinstance(capabilities, dict) else {}


def _validate_external_agent_card(
    card: Any,
    *,
    agent_id: str,
    endpoint: str,
    expected_target_kind: str | None = None,
    expected_target: str | None = None,
    transport_protocol: Literal["rest", "jsonrpc"] | None = None,
) -> A2AAgentCardCheck:
    if not isinstance(card, dict):
        return A2AAgentCardCheck(False, "agent_card_not_object")

    capabilities = _card_capabilities(card)
    service_id = str(card.get("service_id") or "").strip()
    if service_id and service_id != agent_id:
        return A2AAgentCardCheck(
            False,
            f"service_id_mismatch expected={agent_id} actual={service_id}",
            card,
        )

    card_url = str(card.get("url") or "").strip()
    if card_url and _normalize_url(card_url) != _message_url(endpoint):
        return A2AAgentCardCheck(
            False,
            f"agent_url_mismatch expected={_message_url(endpoint)} actual={card_url}",
            card,
        )

    tags = _skill_tags(card)
    target_kind = str(capabilities.get("service_target_kind") or "").strip()
    if expected_target_kind:
        if target_kind:
            if target_kind != expected_target_kind:
                return A2AAgentCardCheck(
                    False,
                    f"target_kind_mismatch expected={expected_target_kind} actual={target_kind}",
                    card,
                )
        elif expected_target_kind not in tags:
            return A2AAgentCardCheck(False, f"target_kind_not_advertised expected={expected_target_kind}", card)

    target = str(capabilities.get("service_target") or "").strip()
    if expected_target:
        if target:
            if target != expected_target:
                return A2AAgentCardCheck(
                    False,
                    f"target_mismatch expected={expected_target} actual={target}",
                    card,
                )
        elif expected_target not in tags:
            return A2AAgentCardCheck(False, f"target_not_advertised expected={expected_target}", card)

    if transport_protocol:
        advertised_protocol = str(capabilities.get("a2a_transport_protocol") or "").strip()
        if advertised_protocol and advertised_protocol != transport_protocol:
            return A2AAgentCardCheck(
                False,
                f"transport_protocol_mismatch expected={transport_protocol} actual={advertised_protocol}",
                card,
            )
        if transport_protocol == "jsonrpc":
            jsonrpc_flag = capabilities.get("a2a_jsonrpc")
            if jsonrpc_flag is False:
                return A2AAgentCardCheck(False, "jsonrpc_explicitly_disabled", card)
            if not card_url and jsonrpc_flag is not True:
                return A2AAgentCardCheck(False, "jsonrpc_not_advertised", card)

    if card_url and not isinstance(card.get("skills"), list):
        return A2AAgentCardCheck(False, "standard_agent_card_skills_missing", card)

    return A2AAgentCardCheck(True, card=card)


async def validate_external_agent(
    request: ExternalAgentValidationRequest,
) -> ExternalAgentValidationResult:
    """Validate an external partner AgentCard against explicit trust config."""
    agent_id = clean_external_agent_id(request.agent_id)
    if not settings.a2a.external_trust_enabled:
        return ExternalAgentValidationResult(
            trusted=False,
            reason="external_trust_disabled",
            agent_id=agent_id or request.agent_id,
            endpoint=request.endpoint,
            transport_protocol=request.transport_protocol,
        )
    if not agent_id or not is_external_agent_allowed(agent_id):
        return ExternalAgentValidationResult(
            trusted=False,
            reason="external_agent_not_allowlisted",
            agent_id=agent_id or request.agent_id,
            endpoint=request.endpoint,
            transport_protocol=request.transport_protocol,
        )

    configured_endpoint = settings.a2a.external_agent_endpoint_map().get(agent_id)
    endpoint = _normalize_url(request.endpoint or configured_endpoint)
    if configured_endpoint and request.endpoint and _normalize_url(configured_endpoint) != endpoint:
        return ExternalAgentValidationResult(
            trusted=False,
            reason="external_agent_endpoint_mismatch",
            agent_id=agent_id,
            endpoint=endpoint,
            transport_protocol=request.transport_protocol,
        )
    if not endpoint:
        return ExternalAgentValidationResult(
            trusted=False,
            reason="external_agent_endpoint_required",
            agent_id=agent_id,
            endpoint=None,
            transport_protocol=request.transport_protocol,
        )

    last_error = "agent_card_fetch_failed"
    timeout = max(0.1, settings.a2a.external_agent_card_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        for card_url in _candidate_card_urls(endpoint):
            try:
                response = await client.get(card_url)
                response.raise_for_status()
                card = response.json()
            except Exception as exc:
                last_error = f"agent_card_fetch_failed: {type(exc).__name__}"
                continue

            check = _validate_external_agent_card(
                card,
                agent_id=agent_id,
                endpoint=endpoint,
                expected_target_kind=request.expected_target_kind,
                expected_target=request.expected_target,
                transport_protocol=request.transport_protocol or settings.a2a.transport_protocol,
            )
            return ExternalAgentValidationResult(
                trusted=check.compatible,
                reason=check.detail or "trusted",
                agent_id=agent_id,
                endpoint=endpoint,
                card_url=card_url,
                transport_protocol=request.transport_protocol or settings.a2a.transport_protocol,
                card=check.card,
            )

    return ExternalAgentValidationResult(
        trusted=False,
        reason=last_error,
        agent_id=agent_id,
        endpoint=endpoint,
        transport_protocol=request.transport_protocol or settings.a2a.transport_protocol,
    )


def authorize_external_a2a_request(
    *,
    caller_id: str | None,
    target_id: str | None,
    expected_target_id: str | None,
    request_body: object | None,
    request_timestamp: str | None,
    request_nonce: str | None,
    request_body_sha256: str | None,
    request_signature: str | None,
) -> tuple[bool, str]:
    """Validate an incoming external A2A JSON-RPC request."""
    if not settings.a2a.external_trust_enabled:
        return False, "external_trust_disabled"

    caller = clean_external_agent_id(caller_id)
    if not caller:
        return False, "external_caller_id_missing"
    if not is_external_agent_allowed(caller):
        return False, "external_caller_not_allowlisted"

    expected_target = clean_external_agent_id(expected_target_id)
    target = clean_external_agent_id(target_id)
    if expected_target and target != expected_target:
        return False, "external_target_id_mismatch"

    if not settings.a2a.external_require_request_signature:
        return True, "external_trusted_without_signature"

    secret = settings.a2a.external_signature_secret_for(caller)
    if not secret:
        return False, "external_signature_secret_missing"
    if request_body is None:
        return False, "external_request_body_missing"

    return verify_a2a_request_signature(
        body=request_body,
        secret=secret,
        caller_id=caller,
        target_id=target,
        timestamp=request_timestamp,
        nonce=request_nonce,
        body_sha256=request_body_sha256,
        signature=request_signature,
        ttl_seconds=settings.a2a.request_signature_ttl_seconds,
        replay_cache=default_a2a_replay_cache(),
    )


__all__ = [
    "ExternalAgentValidationRequest",
    "ExternalAgentValidationResult",
    "authorize_external_a2a_request",
    "clean_external_agent_id",
    "is_external_agent_allowed",
    "validate_external_agent",
]
