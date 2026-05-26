"""Smoke script coverage for local external A2A mock partner onboarding."""

from argparse import Namespace

import pytest

from scripts.a2a_external_mock_smoke import run_smoke


@pytest.mark.asyncio
async def test_external_mock_smoke_validates_partner_and_signature():
    result = await run_smoke(
        Namespace(
            agent_id="mock-external-agent-test",
            secret="mock-external-secret-test",
            expected_target_kind="capability",
            expected_target="mock_lookup",
            transport_protocol="jsonrpc",
        )
    )

    assert result["validation"]["trusted"] is True
    assert result["validation"]["reason"] == "trusted"
    assert result["inbound_authorization"]["ok"] is True
    assert result["mock_jsonrpc"]["status"] == "completed"
