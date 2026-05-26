"""Smoke-test MainOrchestrator -> HTTP A2A -> standalone agent service."""

from __future__ import annotations

import argparse
import asyncio
from typing import Any

from scripts.a2a_http_canary import print_json
from scripts.a2a_two_process_smoke import (
    _DEFAULT_PORTS,
    _start_agent_service,
    _stop_process,
    _wait_until_healthy,
)
from src.core.config import settings
from src.core.constants import ConfidenceLevel, Department, RoutingStrategy, TaskType
from src.db.schemas import IntentAnalysis, RoutingResult
from src.orchestrators.main import MainOrchestrator


class _FixedFinanceRouter:
    async def route(self, *_args, **_kwargs) -> RoutingResult:
        return RoutingResult(
            departments=[Department.FINANCE],
            confidence=0.99,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.DIRECT,
            reasoning="A2A main HTTP smoke: finance route forced.",
            task_type=TaskType.TUITION_QUERY,
            intent=IntentAnalysis(
                complexity="simple",
                is_personal=True,
                force_llm_synthesis=False,
                query_type="factual",
            ),
        )


class _NoopTelemetry:
    async def create_query_log(self, **_kwargs) -> int:
        return 0

    async def finalize_query_log(self, **_kwargs) -> None:
        return None

    async def record_agent_task(self, **_kwargs) -> None:
        return None


class _UnusedAnnouncementAgent:
    async def handle_task(self, *_args, **_kwargs):  # pragma: no cover - defensive guard
        raise AssertionError("Announcement agent should not be used in A2A main HTTP smoke.")


class _UnusedLLMService:
    async def generate(self, *_args, **_kwargs):  # pragma: no cover - defensive guard
        raise AssertionError("LLM should not be used in A2A main HTTP smoke.")


def _configure_parent_a2a(
    *,
    base_url: str,
    internal_key: str,
    request_timeout: float,
) -> dict[str, Any]:
    previous = {
        "mode": settings.a2a.mode,
        "finance_url": settings.a2a.finance_url,
        "timeout_seconds": settings.a2a.timeout_seconds,
        "server_internal_api_key": settings.server.internal_api_key,
    }
    settings.a2a.mode = "http"
    settings.a2a.finance_url = base_url
    settings.a2a.timeout_seconds = request_timeout
    settings.server.internal_api_key = internal_key
    return previous


def _restore_parent_a2a(previous: dict[str, Any]) -> None:
    settings.a2a.mode = previous["mode"]
    settings.a2a.finance_url = previous["finance_url"]
    settings.a2a.timeout_seconds = previous["timeout_seconds"]
    settings.server.internal_api_key = previous["server_internal_api_key"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Start finance agent service and smoke-test MainOrchestrator HTTP A2A."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=_DEFAULT_PORTS[Department.FINANCE])
    parser.add_argument("--internal-key", default="local-a2a-secret")
    parser.add_argument("--startup-timeout", type=float, default=60.0)
    parser.add_argument("--request-timeout", type=float, default=30.0)
    parser.add_argument("--query", default="Harc borcum ne kadar?")
    parser.add_argument("--log-file", default=None)
    return parser.parse_args()


async def async_main() -> None:
    args = parse_args()
    base_url = f"http://{args.host}:{args.port}"
    log_path = None
    if args.log_file:
        from pathlib import Path

        log_path = Path(args.log_file)
    else:
        import tempfile
        from pathlib import Path

        log_path = Path(tempfile.gettempdir()) / f"omu_a2a_main_finance_{args.port}.log"

    process = _start_agent_service(
        department=Department.FINANCE,
        host=args.host,
        port=args.port,
        internal_key=args.internal_key,
        log_path=log_path,
    )
    previous = _configure_parent_a2a(
        base_url=base_url,
        internal_key=args.internal_key,
        request_timeout=args.request_timeout,
    )
    try:
        health = await _wait_until_healthy(
            base_url=base_url,
            timeout_seconds=args.startup_timeout,
        )
        orchestrator = MainOrchestrator(
            router=_FixedFinanceRouter(),
            announcement_agent=_UnusedAnnouncementAgent(),
            telemetry_service=_NoopTelemetry(),
            llm_service=_UnusedLLMService(),
        )
        response = await orchestrator.handle_query(
            args.query,
            context_id="a2a-main-http-smoke",
            student_department="Bilgisayar Muhendisligi",
            student_faculty="Muhendislik Fakultesi",
        )
        if "kimliginizi dogrulamam" not in response.answer:
            raise RuntimeError("Main HTTP smoke beklenen auth-guard cevabini alamadi.")
        if "finance" not in response.departments_involved:
            raise RuntimeError("Main HTTP smoke finance departman izini alamadi.")
        print_json(
            {
                "main_a2a_mode": settings.a2a.mode,
                "service_health": health,
                "response": response.model_dump(mode="json"),
                "started_process": {
                    "pid": process.pid,
                    "base_url": base_url,
                    "log_file": str(log_path),
                },
            }
        )
    finally:
        _restore_parent_a2a(previous)
        _stop_process(process)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
