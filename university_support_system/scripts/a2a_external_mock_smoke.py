"""Smoke test for external A2A partner onboarding with a local mock agent."""

from __future__ import annotations

import argparse
import asyncio
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import Any

import httpx

from src.a2a.external import ExternalAgentValidationRequest, authorize_external_a2a_request
from src.a2a.external import validate_external_agent
from src.a2a.service_identity import (
    A2A_BODY_SHA256_HEADER,
    A2A_CALLER_ID_HEADER,
    A2A_NONCE_HEADER,
    A2A_SIGNATURE_HEADER,
    A2A_TARGET_ID_HEADER,
    A2A_TIMESTAMP_HEADER,
    MAIN_ORCHESTRATOR_SERVICE_ID,
    sign_a2a_request,
)
from src.core.config import settings


class _MockExternalAgentServer:
    """Tiny HTTP server that behaves like an external A2A partner."""

    def __init__(
        self,
        *,
        agent_id: str,
        target_kind: str,
        target: str,
        transport_protocol: str,
    ) -> None:
        self.agent_id = agent_id
        self.target_kind = target_kind
        self.target = target
        self.transport_protocol = transport_protocol
        self._server: ThreadingHTTPServer | None = None
        self._thread: Thread | None = None

    @property
    def base_url(self) -> str:
        if self._server is None:
            raise RuntimeError("Mock server baslatilmadi.")
        host, port = self._server.server_address
        return f"http://{host}:{port}"

    def __enter__(self) -> "_MockExternalAgentServer":
        parent = self

        class Handler(BaseHTTPRequestHandler):
            def _write_json(self, payload: dict[str, Any], *, status: int = 200) -> None:
                body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
                if self.path not in {
                    "/.well-known/agent.json",
                    "/.well-known/agent-card.json",
                    "/agent-card",
                }:
                    self._write_json({"error": "not_found"}, status=404)
                    return

                self._write_json(
                    {
                        "service_id": parent.agent_id,
                        "name": "Mock External A2A Partner",
                        "url": f"{parent.base_url}/a2a",
                        "version": "1.0.0",
                        "capabilities": {
                            "streaming": False,
                            "pushNotifications": False,
                            "stateTransitionHistory": True,
                            "a2a_jsonrpc": True,
                            "a2a_transport_protocol": parent.transport_protocol,
                            "service_target_kind": parent.target_kind,
                            "service_target": parent.target,
                        },
                        "defaultInputModes": ["text/plain"],
                        "defaultOutputModes": ["application/json"],
                        "skills": [
                            {
                                "id": parent.target,
                                "name": "Mock Lookup",
                                "description": "Local mock partner skill for external A2A onboarding smoke.",
                                "tags": [parent.target_kind, parent.target],
                            }
                        ],
                    }
                )

            def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
                if self.path != "/a2a":
                    self._write_json({"error": "not_found"}, status=404)
                    return
                length = int(self.headers.get("Content-Length", "0") or "0")
                raw_body = self.rfile.read(length) if length > 0 else b"{}"
                try:
                    body = json.loads(raw_body.decode("utf-8"))
                except json.JSONDecodeError:
                    self._write_json({"error": "invalid_json"}, status=400)
                    return

                self._write_json(
                    {
                        "jsonrpc": "2.0",
                        "id": body.get("id"),
                        "result": {
                            "id": "mock-external-task",
                            "kind": "task",
                            "contextId": "mock-external-context",
                            "status": {"state": "completed"},
                            "metadata": {
                                "emitter_id": parent.agent_id,
                                "response_schema": "mock.external_response.v1",
                            },
                            "artifacts": [],
                        },
                    }
                )

            def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
                return

        self._server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._thread = Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=2)


def _patch_external_settings(
    *,
    agent_id: str,
    endpoint: str,
    secret: str,
    transport_protocol: str,
) -> dict[str, Any]:
    previous = {
        "external_trust_enabled": settings.a2a.external_trust_enabled,
        "external_allowed_agent_ids": settings.a2a.external_allowed_agent_ids,
        "external_agent_endpoints": settings.a2a.external_agent_endpoints,
        "external_agent_signature_secrets": settings.a2a.external_agent_signature_secrets,
        "external_require_request_signature": settings.a2a.external_require_request_signature,
        "transport_protocol": settings.a2a.transport_protocol,
    }
    settings.a2a.external_trust_enabled = True
    settings.a2a.external_allowed_agent_ids = agent_id
    settings.a2a.external_agent_endpoints = f"{agent_id}={endpoint}"
    settings.a2a.external_agent_signature_secrets = f"{agent_id}={secret}"
    settings.a2a.external_require_request_signature = True
    settings.a2a.transport_protocol = transport_protocol
    return previous


def _restore_external_settings(previous: dict[str, Any]) -> None:
    for key, value in previous.items():
        setattr(settings.a2a, key, value)


async def _post_to_mock_agent(*, endpoint: str, agent_id: str, secret: str) -> dict[str, Any]:
    body = {
        "jsonrpc": "2.0",
        "id": "external-mock-smoke",
        "method": "message/send",
        "params": {
            "message": {
                "kind": "message",
                "role": "user",
                "messageId": "external-mock-message",
                "parts": [{"kind": "text", "text": "ping"}],
            }
        },
    }
    signature_headers = sign_a2a_request(
        body=body,
        secret=secret,
        caller_id=MAIN_ORCHESTRATOR_SERVICE_ID,
        target_id=agent_id,
    )
    headers = {
        A2A_CALLER_ID_HEADER: MAIN_ORCHESTRATOR_SERVICE_ID,
        A2A_TARGET_ID_HEADER: agent_id,
        **signature_headers,
    }
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(f"{endpoint}/a2a", json=body, headers=headers)
        response.raise_for_status()
        return response.json()


async def run_smoke(args: argparse.Namespace) -> dict[str, Any]:
    with _MockExternalAgentServer(
        agent_id=args.agent_id,
        target_kind=args.expected_target_kind,
        target=args.expected_target,
        transport_protocol=args.transport_protocol,
    ) as mock_server:
        previous = _patch_external_settings(
            agent_id=args.agent_id,
            endpoint=mock_server.base_url,
            secret=args.secret,
            transport_protocol=args.transport_protocol,
        )
        try:
            validation = await validate_external_agent(
                ExternalAgentValidationRequest(
                    agent_id=args.agent_id,
                    expected_target_kind=args.expected_target_kind,
                    expected_target=args.expected_target,
                    transport_protocol=args.transport_protocol,
                )
            )

            inbound_body = {
                "jsonrpc": "2.0",
                "id": "external-inbound-smoke",
                "method": "message/send",
                "params": {"message": {"parts": [{"kind": "text", "text": "hello"}]}},
            }
            inbound_headers = sign_a2a_request(
                body=inbound_body,
                secret=args.secret,
                caller_id=args.agent_id,
                target_id=MAIN_ORCHESTRATOR_SERVICE_ID,
            )
            auth_ok, auth_detail = authorize_external_a2a_request(
                caller_id=args.agent_id,
                target_id=MAIN_ORCHESTRATOR_SERVICE_ID,
                expected_target_id=MAIN_ORCHESTRATOR_SERVICE_ID,
                request_body=inbound_body,
                request_timestamp=inbound_headers[A2A_TIMESTAMP_HEADER],
                request_nonce=inbound_headers[A2A_NONCE_HEADER],
                request_body_sha256=inbound_headers[A2A_BODY_SHA256_HEADER],
                request_signature=inbound_headers[A2A_SIGNATURE_HEADER],
            )

            mock_rpc = await _post_to_mock_agent(
                endpoint=mock_server.base_url,
                agent_id=args.agent_id,
                secret=args.secret,
            )
        finally:
            _restore_external_settings(previous)

    return {
        "mock_agent_id": args.agent_id,
        "mock_endpoint": mock_server.base_url,
        "validation": validation.model_dump(mode="json"),
        "inbound_authorization": {
            "ok": auth_ok,
            "detail": auth_detail,
        },
        "mock_jsonrpc": {
            "status": mock_rpc.get("result", {}).get("status", {}).get("state"),
            "response_schema": mock_rpc.get("result", {}).get("metadata", {}).get("response_schema"),
        },
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local external A2A partner smoke test")
    parser.add_argument("--agent-id", default="mock-external-agent")
    parser.add_argument("--secret", default="mock-external-secret")
    parser.add_argument("--expected-target-kind", default="capability")
    parser.add_argument("--expected-target", default="mock_lookup")
    parser.add_argument("--transport-protocol", choices=["rest", "jsonrpc"], default="jsonrpc")
    return parser.parse_args()


async def main() -> None:
    args = _parse_args()
    result = await run_smoke(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    validation = result["validation"]
    inbound = result["inbound_authorization"]
    if not validation.get("trusted") or not inbound.get("ok"):
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
