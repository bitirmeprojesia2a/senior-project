"""A2A discovery and AgentCard preflight tests."""

import pytest

import src.a2a.discovery as discovery_module
from src.a2a.discovery import A2AServiceDiscoveryClient, A2AServiceExpectation
from src.core.config import settings


@pytest.mark.asyncio
async def test_agent_card_check_accepts_expected_service(monkeypatch):
    monkeypatch.setattr(settings.a2a, "discovery_agent_card_enabled", True)
    A2AServiceDiscoveryClient.reset_runtime_state()

    class _FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "service_id": "agent-finance",
                "capabilities": {
                    "a2a_jsonrpc": True,
                    "a2a_transport_protocol": "jsonrpc",
                    "service_target_kind": "department",
                    "service_target": "finance",
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
            assert url == "http://agent-finance:8103/agent-card"
            return _FakeResponse()

    monkeypatch.setattr(discovery_module.httpx, "AsyncClient", _FakeAsyncClient)

    check = await A2AServiceDiscoveryClient().verify_agent_card(
        "http://agent-finance:8103",
        expectation=A2AServiceExpectation(
            service_id="agent-finance",
            target_kind="department",
            target="finance",
            transport_protocol="jsonrpc",
        ),
    )

    assert check.compatible is True


@pytest.mark.asyncio
async def test_agent_card_check_rejects_target_mismatch(monkeypatch):
    monkeypatch.setattr(settings.a2a, "discovery_agent_card_enabled", True)
    A2AServiceDiscoveryClient.reset_runtime_state()

    class _FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "service_id": "agent-academic",
                "capabilities": {
                    "a2a_jsonrpc": True,
                    "a2a_transport_protocol": "jsonrpc",
                    "service_target_kind": "department",
                    "service_target": "academic_programs",
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

    monkeypatch.setattr(discovery_module.httpx, "AsyncClient", _FakeAsyncClient)

    check = await A2AServiceDiscoveryClient().verify_agent_card(
        "http://agent-academic:8102",
        expectation=A2AServiceExpectation(
            service_id="agent-finance",
            target_kind="department",
            target="finance",
            transport_protocol="jsonrpc",
        ),
    )

    assert check.compatible is False
    assert "service_id_mismatch" in str(check.detail)


@pytest.mark.asyncio
async def test_agent_card_check_is_noop_when_disabled(monkeypatch):
    monkeypatch.setattr(settings.a2a, "discovery_agent_card_enabled", False)
    A2AServiceDiscoveryClient.reset_runtime_state()

    class _FailingAsyncClient:
        def __init__(self, *, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            raise AssertionError("AgentCard fetch should not run when disabled")

        async def __aexit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(discovery_module.httpx, "AsyncClient", _FailingAsyncClient)

    check = await A2AServiceDiscoveryClient().verify_agent_card(
        "http://agent-finance:8103",
        expectation=A2AServiceExpectation(service_id="agent-finance"),
    )

    assert check.compatible is True
