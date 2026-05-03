"""Start a standalone A2A agent service process and smoke-test it."""

from __future__ import annotations

import argparse
import asyncio
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import httpx

from scripts.a2a_http_canary import _default_query_for_department, print_json, run_canary
from src.core.config import settings
from src.core.constants import Department, TaskType


_DEFAULT_PORTS = {
    Department.STUDENT_AFFAIRS: 8101,
    Department.ACADEMIC_PROGRAMS: 8102,
    Department.FINANCE: 8103,
}


def _service_id_for(department: Department) -> str:
    return f"agent-{department.value.replace('_', '-')}"


async def _wait_until_healthy(
    *,
    base_url: str,
    timeout_seconds: float,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last_error: str | None = None
    async with httpx.AsyncClient(timeout=2.0) as client:
        while time.monotonic() < deadline:
            try:
                response = await client.get(f"{base_url}/health")
                response.raise_for_status()
                return response.json()
            except Exception as exc:  # pragma: no cover - exercised by smoke usage
                last_error = str(exc)
                await asyncio.sleep(0.5)
    raise TimeoutError(f"Agent service saglik kontrolu zaman asimina ugradi: {last_error}")


def _build_child_env(
    *,
    department: Department,
    host: str,
    port: int,
    internal_key: str,
    base_url: str,
) -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "AGENT_DEPARTMENT": department.value,
            "AGENT_SERVICE_ID": _service_id_for(department),
            "AGENT_PUBLIC_URL": base_url,
            "SERVER_HOST": host,
            "SERVER_PORT": str(port),
            "SERVER_INTERNAL_API_KEY": internal_key,
        }
    )
    return env


def _tail_log(path: Path, max_chars: int = 6000) -> str:
    if not path.exists():
        return ""
    content = path.read_text(encoding="utf-8", errors="replace")
    return content[-max_chars:]


def _start_agent_service(
    *,
    department: Department,
    host: str,
    port: int,
    internal_key: str,
    log_path: Path,
) -> subprocess.Popen:
    base_url = f"http://{host}:{port}"
    with log_path.open("w", encoding="utf-8") as log_file:
        return subprocess.Popen(
            [sys.executable, "-m", "scripts.run_agent_service"],
            cwd=str(settings.base_dir),
            env=_build_child_env(
                department=department,
                host=host,
                port=port,
                internal_key=internal_key,
                base_url=base_url,
            ),
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
        )


def _stop_process(process: subprocess.Popen, timeout_seconds: float = 10.0) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:  # pragma: no cover - defensive cleanup
        process.kill()
        process.wait(timeout=timeout_seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Start a standalone A2A agent service process and run a smoke test."
    )
    parser.add_argument(
        "--department",
        choices=[department.value for department in Department],
        default=os.getenv("AGENT_DEPARTMENT") or Department.FINANCE.value,
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument(
        "--internal-key",
        default=(
            os.getenv("SERVER_INTERNAL_API_KEY")
            or os.getenv("A2A_INTERNAL_API_KEY")
            or "local-a2a-secret"
        ),
    )
    parser.add_argument("--query", default=None)
    parser.add_argument("--health-only", action="store_true")
    parser.add_argument("--startup-timeout", type=float, default=30.0)
    parser.add_argument(
        "--request-timeout",
        type=float,
        default=120.0,
        help="HTTP request timeout for canary calls. Higher default covers model cold-start.",
    )
    parser.add_argument(
        "--log-file",
        default=None,
        help="Child service log path. Defaults to a temporary file.",
    )
    return parser.parse_args()


async def async_main() -> None:
    args = parse_args()
    department = Department(args.department)
    port = args.port or _DEFAULT_PORTS[department]
    base_url = f"http://{args.host}:{port}"
    query, task_type = _default_query_for_department(department)
    log_path = Path(args.log_file) if args.log_file else Path(
        tempfile.gettempdir()
    ) / f"omu_a2a_{department.value}_{port}.log"

    process = _start_agent_service(
        department=department,
        host=args.host,
        port=port,
        internal_key=args.internal_key,
        log_path=log_path,
    )
    try:
        health = await _wait_until_healthy(
            base_url=base_url,
            timeout_seconds=args.startup_timeout,
        )
        result = await run_canary(
            department=department,
            base_url=base_url,
            internal_key=args.internal_key,
            query=args.query or query,
            task_type=task_type if isinstance(task_type, TaskType) else None,
            dispatch=not args.health_only,
            timeout_seconds=args.request_timeout,
        )
        result["started_process"] = {
            "pid": process.pid,
            "health": health,
            "log_file": str(log_path),
        }
        print_json(result)
    except Exception as exc:
        log_tail = _tail_log(log_path)
        if log_tail:
            print(log_tail, file=sys.stderr)
        raise RuntimeError(f"A2A two-process smoke failed: {exc}") from exc
    finally:
        _stop_process(process)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
