"""Smoke-test a running Docker A2A stack through public HTTP surfaces."""

from __future__ import annotations

import argparse
import asyncio
import os
from typing import Any
from uuid import uuid4

import httpx
from a2a.types import Role

from scripts.a2a_http_canary import print_json
from src.a2a import USER_QUERY_RESPONSE_SCHEMA, build_text_message
from src.a2a.service_identity import MAIN_ORCHESTRATOR_SERVICE_ID, build_a2a_auth_headers


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


async def _get_json(client: httpx.AsyncClient, url: str) -> dict[str, Any]:
    response = await client.get(url)
    response.raise_for_status()
    return response.json()


async def _post_json(
    client: httpx.AsyncClient,
    url: str,
    *,
    payload: dict[str, Any],
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    response = await client.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def _profile_payload(*, query: str, context_id: str) -> dict[str, Any]:
    return {
        "query": query,
        "context_id": context_id,
        "full_name": "A2A Smoke Ogrenci",
        "student_number": "22000001",
        "student_department": "Bilgisayar Muhendisligi",
        "student_faculty": "Muhendislik Fakultesi",
        "student_type": "Turk ogrenci",
        "llm_profile": "fast",
    }


def _find_structured_artifact(task_payload: dict[str, Any]) -> dict[str, Any] | None:
    for artifact in task_payload.get("artifacts") or []:
        metadata = artifact.get("metadata") or {}
        if metadata.get("schema") == USER_QUERY_RESPONSE_SCHEMA:
            return artifact
    return None


async def run_smoke(args: argparse.Namespace) -> dict[str, Any]:
    base_url = args.base_url.rstrip("/")
    context_id = args.context_id or f"a2a-docker-smoke-{uuid4().hex[:8]}"
    trace_id = args.trace_id or f"trace-{uuid4().hex}"
    signature_secret = args.request_signature_secret or args.internal_key

    async with httpx.AsyncClient(timeout=args.timeout) as client:
        health = await _get_json(client, f"{base_url}/health")
        topology = await _get_json(client, f"{base_url}/a2a/topology")
        active_count = int(topology.get("active_count") or 0)
        agent_ids = {
            str(agent.get("agent_id"))
            for agent in topology.get("agents") or []
            if agent.get("agent_id")
        }

        _require(active_count >= args.min_active, f"A2A active_count dusuk: {active_count}")
        if args.expect_protocol:
            _require(
                topology.get("a2a_transport_protocol") == args.expect_protocol,
                (
                    "A2A transport protocol beklenenden farkli: "
                    f"{topology.get('a2a_transport_protocol')!r}"
                ),
            )
        for expected_agent in args.expect_agent:
            _require(
                expected_agent in agent_ids,
                f"Beklenen A2A agent topology'de yok: {expected_agent}",
            )

        public_query = None
        if not args.skip_public_query:
            public_query = await _post_json(
                client,
                f"{base_url}/query",
                payload=_profile_payload(query=args.query, context_id=context_id),
            )
            _require(public_query.get("query_id") == context_id, "Public /query context_id korumadi.")
            _require(bool(public_query.get("answer")), "Public /query bos cevap dondu.")
            _require(
                bool(public_query.get("departments_involved")),
                "Public /query departman izi uretmedi.",
            )

        jsonrpc = None
        if not args.skip_jsonrpc:
            message = build_text_message(
                args.jsonrpc_query,
                context_id=f"{context_id}-jsonrpc",
                role=Role.user,
                metadata={
                    **_profile_payload(
                        query=args.jsonrpc_query,
                        context_id=f"{context_id}-jsonrpc",
                    ),
                    "trace_id": trace_id,
                    "span_id": "smoke-main-client",
                },
            )
            jsonrpc_payload = {
                "jsonrpc": "2.0",
                "id": f"{context_id}-rpc",
                "method": "message/send",
                "params": {
                    "message": message.model_dump(mode="json", exclude_none=True),
                },
            }
            headers = build_a2a_auth_headers(
                internal_api_key=args.internal_key,
                caller_id=args.caller_id,
                target_id=MAIN_ORCHESTRATOR_SERVICE_ID,
                body=jsonrpc_payload,
                signature_secret=signature_secret,
            )
            jsonrpc = await _post_json(
                client,
                f"{base_url}/a2a",
                payload=jsonrpc_payload,
                headers=headers,
            )
            result = jsonrpc.get("result") or {}
            _require(result.get("status", {}).get("state") == "completed", "JSON-RPC task tamamlanmadi.")
            _require(result.get("metadata", {}).get("trace_id") == trace_id, "JSON-RPC trace_id korunmadi.")
            state_transitions = result.get("metadata", {}).get("state_transitions") or []
            transition_states = [
                item.get("state")
                for item in state_transitions
                if isinstance(item, dict)
            ]
            _require(
                transition_states[-3:] == ["submitted", "working", "completed"],
                f"JSON-RPC state transition history beklenenden farkli: {transition_states!r}",
            )
            structured_artifact = _find_structured_artifact(result)
            _require(structured_artifact is not None, "JSON-RPC structured user response artifact yok.")

        diagnostics = None
        if not args.skip_diagnostics:
            diagnostics = await _get_json(client, f"{base_url}/a2a/diagnostics")
            _require(diagnostics.get("status") == "ok", "A2A diagnostics status ok degil.")
            overview = diagnostics.get("overview") or {}
            _require(
                int(overview.get("agent_task_count") or 0) >= 0,
                "A2A diagnostics agent_task_count gecersiz.",
            )

        return {
            "base_url": base_url,
            "health": health,
            "topology": {
                "status": topology.get("status"),
                "a2a_mode": topology.get("a2a_mode"),
                "a2a_transport_protocol": topology.get("a2a_transport_protocol"),
                "agent_count": topology.get("agent_count"),
                "active_count": topology.get("active_count"),
                "stale_count": topology.get("stale_count"),
                "agent_ids": sorted(agent_ids),
            },
            "public_query": public_query,
            "jsonrpc": jsonrpc,
            "diagnostics": diagnostics,
            "trace_id": trace_id,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Smoke-test an already running Docker A2A stack."
    )
    parser.add_argument("--base-url", default=os.getenv("A2A_SMOKE_BASE_URL", "http://127.0.0.1:8000"))
    parser.add_argument(
        "--internal-key",
        default=(
            os.getenv("SERVER_INTERNAL_API_KEY")
            or os.getenv("A2A_INTERNAL_API_KEY")
            or "local-a2a-secret"
        ),
    )
    parser.add_argument(
        "--request-signature-secret",
        default=os.getenv("A2A_REQUEST_SIGNATURE_SECRET"),
        help="A2A request-signature secret. Defaults to --internal-key when omitted.",
    )
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--min-active", type=int, default=5)
    parser.add_argument("--expect-protocol", choices=["rest", "jsonrpc"], default=None)
    parser.add_argument("--expect-agent", action="append", default=[])
    parser.add_argument("--context-id", default=None)
    parser.add_argument("--trace-id", default=None)
    parser.add_argument(
        "--caller-id",
        default=MAIN_ORCHESTRATOR_SERVICE_ID,
        help=(
            "A2A caller identity for JSON-RPC smoke. Defaults to main_orchestrator "
            "because Docker overlays allowlist internal service ids by default."
        ),
    )
    parser.add_argument("--query", default="ikinci donem dersleri ne")
    parser.add_argument("--jsonrpc-query", default="Bu hafta etkinlik var mi?")
    parser.add_argument("--skip-public-query", action="store_true")
    parser.add_argument("--skip-jsonrpc", action="store_true")
    parser.add_argument("--skip-diagnostics", action="store_true")
    return parser.parse_args()


def main() -> None:
    print_json(asyncio.run(run_smoke(parse_args())))


if __name__ == "__main__":
    main()
