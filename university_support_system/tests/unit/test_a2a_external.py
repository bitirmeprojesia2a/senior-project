"""External A2A trust and onboarding tests."""

import pytest

import src.a2a.external as external_module
from src.a2a.external import (
    ExternalAgentValidationRequest,
    authorize_external_a2a_request,
    validate_external_agent,
)
from src.a2a.service_identity import (
    A2A_BODY_SHA256_HEADER,
    A2A_NONCE_HEADER,
    A2A_SIGNATURE_HEADER,
    A2A_TIMESTAMP_HEADER,
    sign_a2a_request,
)
from src.core.config import settings


@pytest.mark.asyncio
async def test_external_validation_rejects_when_trust_disabled(monkeypatch):
    monkeypatch.setattr(settings.a2a, "external_trust_enabled", False)
    monkeypatch.setattr(settings.a2a, "external_allowed_agent_ids", "partner-agent")

    result = await validate_external_agent(
        ExternalAgentValidationRequest(
            agent_id="partner-agent",
            endpoint="https://partner.example",
            transport_protocol="jsonrpc",
        )
    )

    assert result.trusted is False
    assert result.reason == "external_trust_disabled"


@pytest.mark.asyncio
async def test_external_validation_accepts_allowlisted_standard_agent_card(monkeypatch):
    monkeypatch.setattr(settings.a2a, "external_trust_enabled", True)
    monkeypatch.setattr(settings.a2a, "external_allowed_agent_ids", "partner-agent")
    monkeypatch.setattr(settings.a2a, "external_agent_endpoints", "partner-agent=https://partner.example")

    class _FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "name": "Partner Agent",
                "url": "https://partner.example/a2a",
                "version": "1.0.0",
                "capabilities": {
                    "streaming": False,
                    "pushNotifications": False,
                    "stateTransitionHistory": True,
                },
                "defaultInputModes": ["text/plain"],
                "defaultOutputModes": ["application/json"],
                "skills": [
                    {
                        "id": "partner_lookup",
                        "name": "Partner Lookup",
                        "description": "Partner data lookup.",
                        "tags": ["capability", "partner_lookup"],
                    }
                ],
            }

    class _FakeAsyncClient:
        def __init__(self, *, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url):
            assert url == "https://partner.example/.well-known/agent.json"
            return _FakeResponse()

    monkeypatch.setattr(external_module.httpx, "AsyncClient", _FakeAsyncClient)

    result = await validate_external_agent(
        ExternalAgentValidationRequest(
            agent_id="partner-agent",
            expected_target_kind="capability",
            expected_target="partner_lookup",
            transport_protocol="jsonrpc",
        )
    )

    assert result.trusted is True
    assert result.reason == "trusted"
    assert result.card_url == "https://partner.example/.well-known/agent.json"


@pytest.mark.asyncio
async def test_external_validation_rejects_internal_card_service_id_mismatch(monkeypatch):
    monkeypatch.setattr(settings.a2a, "external_trust_enabled", True)
    monkeypatch.setattr(settings.a2a, "external_allowed_agent_ids", "partner-agent")

    class _FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "service_id": "different-agent",
                "capabilities": {
                    "a2a_jsonrpc": True,
                    "a2a_transport_protocol": "jsonrpc",
                },
            }

    class _FakeAsyncClient:
        def __init__(self, *, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url):
            return _FakeResponse()

    monkeypatch.setattr(external_module.httpx, "AsyncClient", _FakeAsyncClient)

    result = await validate_external_agent(
        ExternalAgentValidationRequest(
            agent_id="partner-agent",
            endpoint="https://partner.example",
            transport_protocol="jsonrpc",
        )
    )

    assert result.trusted is False
    assert "service_id_mismatch" in result.reason


def test_external_a2a_request_authorization_accepts_signed_allowlisted_partner(monkeypatch):
    monkeypatch.setattr(settings.a2a, "external_trust_enabled", True)
    monkeypatch.setattr(settings.a2a, "external_allowed_agent_ids", "partner-agent")
    monkeypatch.setattr(settings.a2a, "external_agent_signature_secrets", "partner-agent=partner-secret")

    body = {"jsonrpc": "2.0", "id": "1", "method": "message/send", "params": {}}
    headers = sign_a2a_request(
        body=body,
        secret="partner-secret",
        caller_id="partner-agent",
        target_id="main_orchestrator",
        nonce="nonce-1",
    )

    ok, detail = authorize_external_a2a_request(
        caller_id="partner-agent",
        target_id="main_orchestrator",
        expected_target_id="main_orchestrator",
        request_body=body,
        request_timestamp=headers[A2A_TIMESTAMP_HEADER],
        request_nonce=headers[A2A_NONCE_HEADER],
        request_body_sha256=headers[A2A_BODY_SHA256_HEADER],
        request_signature=headers[A2A_SIGNATURE_HEADER],
    )

    assert ok is True
    assert detail == "ok"


def test_external_a2a_request_authorization_rejects_target_mismatch(monkeypatch):
    monkeypatch.setattr(settings.a2a, "external_trust_enabled", True)
    monkeypatch.setattr(settings.a2a, "external_allowed_agent_ids", "partner-agent")
    monkeypatch.setattr(settings.a2a, "external_agent_signature_secrets", "partner-agent=partner-secret")

    ok, detail = authorize_external_a2a_request(
        caller_id="partner-agent",
        target_id="agent-finance",
        expected_target_id="main_orchestrator",
        request_body={},
        request_timestamp="1800000000",
        request_nonce="nonce-1",
        request_body_sha256="invalid",
        request_signature="invalid",
    )

    assert ok is False
    assert detail == "external_target_id_mismatch"
