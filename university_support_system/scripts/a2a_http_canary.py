"""Smoke test a running standalone A2A agent service."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from typing import Any

import httpx

from src.a2a.service_identity import (
    MAIN_ORCHESTRATOR_SERVICE_ID,
    build_a2a_auth_headers,
    department_service_id,
)
from src.core.config import settings
from src.core.constants import Department, TaskType


def print_json(data: dict[str, Any]) -> None:
    """Print JSON safely on Windows consoles with non-UTF-8 code pages."""
    output = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write(output.encode("utf-8"))
        return
    encoding = sys.stdout.encoding or "utf-8"
    print(output.encode(encoding, errors="replace").decode(encoding))


def _default_url_for_department(department: Department) -> str:
    configured = settings.a2a.endpoint_for(department.value)
    if configured:
        return configured
    fallback_ports = {
        Department.STUDENT_AFFAIRS: 8101,
        Department.ACADEMIC_PROGRAMS: 8102,
        Department.FINANCE: 8103,
    }
    return f"http://localhost:{fallback_ports[department]}"


def _default_query_for_department(department: Department) -> tuple[str, TaskType | None]:
    if department == Department.FINANCE:
        return "Harc borcum ne kadar?", TaskType.TUITION_QUERY
    if department == Department.STUDENT_AFFAIRS:
        return "Ders kaydi nasil yapilir?", TaskType.REGISTRATION_QUERY
    return "Erasmus basvurusu nasil yapilir?", TaskType.PROCEDURE_QUERY


async def _get_json(client: httpx.AsyncClient, url: str) -> dict[str, Any]:
    response = await client.get(url)
    response.raise_for_status()
    return response.json()


async def run_canary(
    *,
    department: Department,
    base_url: str,
    internal_key: str,
    query: str,
    task_type: TaskType | None,
    dispatch: bool,
    timeout_seconds: float | None = None,
    request_signature_secret: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {"department": department.value, "base_url": base_url}
    async with httpx.AsyncClient(timeout=timeout_seconds or settings.a2a.timeout_seconds) as client:
        result["health"] = await _get_json(client, f"{base_url}/health")
        result["agent_card"] = await _get_json(client, f"{base_url}/agent-card")
        result["metrics_before"] = await _get_json(client, f"{base_url}/metrics")
        if dispatch:
            payload = {
                "department": department.value,
                "query": query,
                "context_id": "a2a-canary",
                "task_type": task_type.value if task_type else None,
                "student_department": "Bilgisayar Muhendisligi",
                "student_faculty": "Muhendislik Fakultesi",
                "llm_profile": settings.normalize_llm_profile(settings.llm.profile),
            }
            if department == Department.FINANCE and query == "Harc borcum ne kadar?":
                payload["is_personal_query"] = True
            headers = build_a2a_auth_headers(
                internal_api_key=internal_key,
                caller_id=MAIN_ORCHESTRATOR_SERVICE_ID,
                target_id=department_service_id(department),
                body=payload,
                signature_secret=request_signature_secret or internal_key,
            )
            response = await client.post(
                f"{base_url}/a2a/dispatch",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            result["dispatch"] = response.json()
            result["metrics_after"] = await _get_json(client, f"{base_url}/metrics")
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test a running A2A agent service.")
    parser.add_argument(
        "--department",
        choices=[department.value for department in Department],
        default=os.getenv("AGENT_DEPARTMENT") or Department.FINANCE.value,
    )
    parser.add_argument("--url", default=None, help="Agent service base URL.")
    parser.add_argument(
        "--internal-key",
        default=settings.server.internal_api_key or settings.a2a.internal_api_key,
        help="Internal API key for /a2a/dispatch.",
    )
    parser.add_argument("--query", default=None, help="Override canary query.")
    parser.add_argument("--health-only", action="store_true", help="Skip /a2a/dispatch.")
    parser.add_argument(
        "--request-timeout",
        type=float,
        default=None,
        help="HTTP request timeout in seconds. Defaults to A2A_TIMEOUT_SECONDS.",
    )
    parser.add_argument(
        "--request-signature-secret",
        default=os.getenv("A2A_REQUEST_SIGNATURE_SECRET"),
        help="A2A request-signature secret. Defaults to --internal-key when omitted.",
    )
    return parser.parse_args()


async def async_main() -> None:
    args = parse_args()
    department = Department(args.department)
    default_query, task_type = _default_query_for_department(department)
    internal_key = args.internal_key
    if not args.health_only and not internal_key:
        raise RuntimeError("Dispatch testi icin SERVER_INTERNAL_API_KEY veya A2A_INTERNAL_API_KEY gerekli.")

    result = await run_canary(
        department=department,
        base_url=(args.url or _default_url_for_department(department)).rstrip("/"),
        internal_key=internal_key or "",
        query=args.query or default_query,
        task_type=task_type,
        dispatch=not args.health_only,
        timeout_seconds=args.request_timeout,
        request_signature_secret=args.request_signature_secret,
    )
    print_json(result)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
