"""Standardized Docker rollout helper for A2A services."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence
from urllib.error import URLError
from urllib.request import urlopen


ROOT_DIR = Path(__file__).resolve().parent.parent
LEGACY_IMAGE_REFS = (
    "university_support_system-api:latest",
    "university_support_system-agent-finance:latest",
    "university_support_system-agent-student-affairs:latest",
    "university_support_system-agent-academic:latest",
)


def _default_build_timestamp() -> str:
    return datetime.now().astimezone().isoformat()


def _default_git_sha() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            check=True,
        )
        value = result.stdout.strip()
        return value or "local"
    except Exception:
        return "local"


def _run_command(command: Sequence[str], *, env: dict[str, str]) -> None:
    printable = " ".join(command)
    print(f"\n> {printable}\n")
    subprocess.run(command, cwd=ROOT_DIR, env=env, check=True)


def _capture_command(command: Sequence[str]) -> str:
    result = subprocess.run(
        command,
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def _compose_files(
    existing_infra: bool,
    include_student: bool,
    include_academic: bool,
    include_announcement: bool,
    include_event: bool,
    include_finance_specialists: bool,
    include_student_specialists: bool = False,
    include_academic_specialists: bool = False,
    include_slack: bool = False,
    use_gpu: bool = False,
    gpu_scope: str = "targeted",
) -> list[str]:
    files = [
        "docker-compose.a2a-existing-infra.yml"
        if existing_infra
        else "docker-compose.a2a.yml"
    ]
    if include_student:
        files.append("docker-compose.a2a-existing-infra-student.yml")
    if include_academic:
        files.append("docker-compose.a2a-existing-infra-academic.yml")
    if existing_infra and (include_announcement or include_event):
        files.append("docker-compose.a2a-existing-infra-capabilities.yml")
    if existing_infra and include_finance_specialists:
        files.append("docker-compose.a2a-existing-infra-finance-specialists.yml")
    if existing_infra and include_student_specialists:
        files.append("docker-compose.a2a-existing-infra-student-specialists.yml")
    if existing_infra and include_academic_specialists:
        files.append("docker-compose.a2a-existing-infra-academic-specialists.yml")
    if use_gpu:
        files.append(
            "docker-compose.a2a-app-gpu-all.yml"
            if gpu_scope == "all"
            else "docker-compose.a2a-app-gpu.yml"
        )
    if include_slack:
        files.append("docker-compose.slack.yml")
    return files


def _service_names(
    include_student: bool,
    include_academic: bool,
    include_announcement: bool,
    include_event: bool,
    include_finance_specialists: bool,
    include_student_specialists: bool = False,
    include_academic_specialists: bool = False,
    include_slack: bool = False,
    slack_service: str = "slack-bot-a2a",
) -> list[str]:
    services = ["retrieval-service", "api", "agent-finance"]
    if include_finance_specialists:
        services.extend(["agent-finance-tuition", "agent-finance-scholarship"])
    if include_student:
        services.append("agent-student-affairs")
    if include_student_specialists:
        services.extend(
            [
                "agent-student-registration",
                "agent-student-graduation",
                "agent-student-internship",
                "agent-student-life",
            ]
        )
    if include_academic:
        services.append("agent-academic")
    if include_academic_specialists:
        services.extend(
            [
                "agent-academic-curriculum",
                "agent-academic-regulation",
                "agent-academic-international",
            ]
        )
    if include_announcement:
        services.append("agent-announcement")
    if include_event:
        services.append("agent-event")
    if include_slack:
        services.append(slack_service)
    return services


def _compose_base_args(files: Sequence[str]) -> list[str]:
    args = ["docker", "compose"]
    for file_name in files:
        args.extend(["-f", file_name])
    return args


def _compose_up_args(compose_args: Sequence[str], services: Sequence[str]) -> list[str]:
    """Return a deterministic recreate command for rollout-managed services."""
    return [
        *compose_args,
        "up",
        "--no-build",
        "--force-recreate",
        "-d",
        *services,
    ]


def _health_targets(
    include_student: bool,
    include_academic: bool,
    include_announcement: bool,
    include_event: bool,
    include_finance_specialists: bool,
    include_student_specialists: bool = False,
    include_academic_specialists: bool = False,
) -> list[tuple[str, str]]:
    targets = [
        ("retrieval-service", "http://localhost:8140/health"),
        ("api", "http://localhost:8000/health"),
        ("agent-finance", "http://localhost:8103/health"),
    ]
    if include_student:
        targets.append(("agent-student-affairs", "http://localhost:8101/health"))
    if include_student_specialists:
        targets.extend(
            [
                ("agent-student-registration", "http://localhost:8120/health"),
                ("agent-student-graduation", "http://localhost:8121/health"),
                ("agent-student-internship", "http://localhost:8122/health"),
                ("agent-student-life", "http://localhost:8123/health"),
            ]
        )
    if include_academic:
        targets.append(("agent-academic", "http://localhost:8102/health"))
    if include_academic_specialists:
        targets.extend(
            [
                ("agent-academic-curriculum", "http://localhost:8130/health"),
                ("agent-academic-regulation", "http://localhost:8131/health"),
                ("agent-academic-international", "http://localhost:8132/health"),
            ]
        )
    if include_announcement:
        targets.append(("agent-announcement", "http://localhost:8104/health"))
    if include_event:
        targets.append(("agent-event", "http://localhost:8105/health"))
    if include_finance_specialists:
        targets.append(("agent-finance-tuition", "http://localhost:8110/health"))
        targets.append(("agent-finance-scholarship", "http://localhost:8111/health"))
    return targets


def _load_health_payload(url: str, *, timeout_seconds: float) -> dict[str, Any]:
    with urlopen(url, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def _health_build_id(payload: dict[str, Any]) -> str | None:
    app_build = payload.get("app", {}).get("build")
    if isinstance(app_build, dict):
        build_id = app_build.get("build_id")
        if build_id:
            return str(build_id)
    agent_build = payload.get("build")
    if isinstance(agent_build, dict):
        build_id = agent_build.get("build_id")
        if build_id:
            return str(build_id)
    return None


def _health_matches_build(payload: dict[str, Any], *, expected_build_id: str) -> bool:
    if payload.get("status") not in {"ok", "healthy", "warming"}:
        return False
    return _health_build_id(payload) == expected_build_id


def _wait_for_health_targets(
    targets: Sequence[tuple[str, str]],
    *,
    expected_build_id: str,
    startup_timeout_seconds: float,
    request_timeout_seconds: float,
    poll_interval_seconds: float,
) -> None:
    deadline = time.monotonic() + startup_timeout_seconds
    pending = {name: url for name, url in targets}
    last_seen: dict[str, dict[str, Any]] = {}

    while pending and time.monotonic() < deadline:
        resolved: list[str] = []
        for name, url in pending.items():
            try:
                payload = _load_health_payload(url, timeout_seconds=request_timeout_seconds)
            except (URLError, TimeoutError, OSError, json.JSONDecodeError):
                continue

            last_seen[name] = {
                "status": payload.get("status"),
                "build_id": _health_build_id(payload),
            }
            if _health_matches_build(payload, expected_build_id=expected_build_id):
                resolved.append(name)

        for name in resolved:
            url = pending.pop(name)
            print(f"Health OK: {name} -> {url} (build_id={expected_build_id})")

        if pending:
            time.sleep(poll_interval_seconds)

    if pending:
        formatted = ", ".join(
            (
                f"{name}={url}"
                f" last_status={last_seen.get(name, {}).get('status', '-')}"
                f" last_build_id={last_seen.get(name, {}).get('build_id', '-')}"
            )
            for name, url in pending.items()
        )
        raise RuntimeError(
            "Expected build metadata did not appear on all health endpoints within "
            f"{startup_timeout_seconds:.0f}s: {formatted}"
        )


def _slack_container_name(service_name: str) -> str:
    return {
        "slack-bot-a2a": "uni_slack_bot_a2a",
        "slack-bot-inprocess": "uni_slack_bot_inprocess",
    }.get(service_name, service_name)


def _opposite_slack_service_name(service_name: str) -> str:
    return {
        "slack-bot-a2a": "slack-bot-inprocess",
        "slack-bot-inprocess": "slack-bot-a2a",
    }.get(service_name, "")


def _wait_for_container_running(
    container_name: str,
    *,
    env: dict[str, str],
    startup_timeout_seconds: float,
    poll_interval_seconds: float,
) -> None:
    deadline = time.monotonic() + startup_timeout_seconds
    last_status = ""
    while time.monotonic() < deadline:
        result = subprocess.run(
            [
                "docker",
                "inspect",
                "-f",
                "{{.State.Running}} {{.State.Status}}",
                container_name,
            ],
            cwd=ROOT_DIR,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        last_status = result.stdout.strip() or result.stderr.strip()
        if result.returncode == 0 and result.stdout.strip().startswith("true "):
            print(f"Container OK: {container_name} is running")
            return
        time.sleep(poll_interval_seconds)

    raise RuntimeError(
        f"Slack container did not reach running state within "
        f"{startup_timeout_seconds:.0f}s: {container_name} "
        f"last_status={last_status or '-'}"
    )


def _select_legacy_image_refs(image_refs: Sequence[str]) -> list[str]:
    known = set(LEGACY_IMAGE_REFS)
    return [image_ref for image_ref in image_refs if image_ref in known]


def _list_local_image_refs() -> list[str]:
    output = _capture_command(
        [
            "docker",
            "image",
            "ls",
            "--format",
            "{{.Repository}}:{{.Tag}}",
        ]
    )
    image_refs = [line.strip() for line in output.splitlines() if line.strip()]
    return _select_legacy_image_refs(image_refs)


def _report_legacy_images() -> list[str]:
    legacy_refs = _list_local_image_refs()
    if legacy_refs:
        print("Legacy image candidates detected:")
        for image_ref in legacy_refs:
            print(f"- {image_ref}")
    else:
        print("No legacy image candidates detected.")
    return legacy_refs


def _remove_legacy_images(image_refs: Sequence[str], *, env: dict[str, str]) -> None:
    if not image_refs:
        print("No legacy images to remove.")
        return
    _run_command(["docker", "image", "rm", *image_refs], env=env)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build the shared A2A Docker image once and recreate selected services "
            "with deterministic build metadata."
        )
    )
    parser.add_argument(
        "--base-infra",
        action="store_true",
        help=(
            "Use docker-compose.a2a.yml instead of the existing-infra overlay. "
            "Student/academic extra overlays remain existing-infra only."
        ),
    )
    parser.add_argument(
        "--include-student",
        action="store_true",
        help="Include the student affairs agent service in the rollout.",
    )
    parser.add_argument(
        "--include-academic",
        action="store_true",
        help="Include the academic programs agent service in the rollout.",
    )
    parser.add_argument(
        "--include-announcement",
        action="store_true",
        help="Include the announcement capability agent service in the rollout.",
    )
    parser.add_argument(
        "--include-event",
        action="store_true",
        help="Include the event capability agent service in the rollout.",
    )
    parser.add_argument(
        "--include-finance-specialists",
        action="store_true",
        help="Include finance specialist agent services behind the finance orchestrator.",
    )
    parser.add_argument(
        "--include-student-specialists",
        action="store_true",
        help="Include student affairs specialist agent services behind the student affairs orchestrator.",
    )
    parser.add_argument(
        "--include-academic-specialists",
        action="store_true",
        help="Include academic programs specialist agent services behind the academic programs orchestrator.",
    )
    parser.add_argument(
        "--include-all-specialists",
        action="store_true",
        help="Include all available specialist agent services behind their department orchestrators.",
    )
    parser.add_argument(
        "--no-slack",
        action="store_true",
        help="Do not recreate the Slack bot service as part of the rollout.",
    )
    parser.add_argument(
        "--slack-service",
        choices=("slack-bot-a2a", "slack-bot-inprocess"),
        default="slack-bot-a2a",
        help="Slack bot service to include in the rollout unless --no-slack is set.",
    )
    parser.add_argument(
        "--transport-protocol",
        choices=("rest", "jsonrpc"),
        default="jsonrpc",
        help="HTTP wire protocol used by A2A transports.",
    )
    parser.add_argument(
        "--build-id",
        default=f"codex-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        help="Build identifier exposed in /health responses.",
    )
    parser.add_argument(
        "--build-timestamp",
        default=_default_build_timestamp(),
        help="ISO-8601 build timestamp exposed in /health responses.",
    )
    parser.add_argument(
        "--git-sha",
        default=_default_git_sha(),
        help="Git SHA exposed in /health responses.",
    )
    parser.add_argument(
        "--image-ref",
        default="university_support_system-app:latest",
        help="Image reference exposed in /health responses.",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip the image build step and only recreate services.",
    )
    parser.add_argument(
        "--install-build-tools",
        action="store_true",
        help=(
            "Install optional apt build tools in the image. "
            "Leave disabled for normal wheel-based builds."
        ),
    )
    parser.add_argument(
        "--gpu",
        action="store_true",
        help=(
            "Build a GPU-capable image and apply the GPU runtime overlay for "
            "embedding/reranker-heavy services."
        ),
    )
    parser.add_argument(
        "--gpu-base-image",
        default="pytorch/pytorch:2.6.0-cuda12.4-cudnn9-runtime",
        help=(
            "Base image to use for GPU rollouts. Ignored unless --gpu is set."
        ),
    )
    parser.add_argument(
        "--gpu-scope",
        choices=("targeted", "all"),
        default="targeted",
        help=(
            "GPU runtime scope. 'targeted' only enables CUDA for the heaviest "
            "retrieval agents, 'all' applies the overlay to every A2A app service."
        ),
    )
    parser.add_argument(
        "--build-only",
        action="store_true",
        help="Only build the shared image; do not recreate services.",
    )
    parser.add_argument(
        "--skip-health-check",
        action="store_true",
        help="Skip post-rollout health verification.",
    )
    parser.add_argument(
        "--health-timeout-seconds",
        type=float,
        default=120.0,
        help="How long to wait for the new build ID to appear on health endpoints.",
    )
    parser.add_argument(
        "--health-request-timeout-seconds",
        type=float,
        default=5.0,
        help="Per-request timeout for health checks.",
    )
    parser.add_argument(
        "--health-poll-interval-seconds",
        type=float,
        default=3.0,
        help="Polling interval between health checks.",
    )
    parser.add_argument(
        "--cleanup-legacy-images",
        action="store_true",
        help=(
            "Remove legacy image tags after a successful rollout. "
            "Without this flag the script only reports cleanup candidates."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    include_finance_specialists = (
        args.include_finance_specialists or args.include_all_specialists
    )
    include_student_specialists = (
        args.include_student_specialists or args.include_all_specialists
    )
    include_academic_specialists = (
        args.include_academic_specialists or args.include_all_specialists
    )
    include_student = args.include_student or include_student_specialists
    include_academic = args.include_academic or include_academic_specialists
    include_slack = not args.no_slack

    if args.base_infra and (
        include_student
        or include_academic
        or args.include_announcement
        or args.include_event
        or include_finance_specialists
        or include_student_specialists
        or include_academic_specialists
        or include_slack
    ):
        print(
            "Extra overlays only support the existing-infra rollout path.",
            file=sys.stderr,
        )
        return 2

    compose_files = _compose_files(
        existing_infra=not args.base_infra,
        include_student=include_student,
        include_academic=include_academic,
        include_announcement=args.include_announcement,
        include_event=args.include_event,
        include_finance_specialists=include_finance_specialists,
        include_student_specialists=include_student_specialists,
        include_academic_specialists=include_academic_specialists,
        include_slack=include_slack,
        use_gpu=args.gpu,
        gpu_scope=args.gpu_scope,
    )
    services = _service_names(
        include_student=include_student,
        include_academic=include_academic,
        include_announcement=args.include_announcement,
        include_event=args.include_event,
        include_finance_specialists=include_finance_specialists,
        include_student_specialists=include_student_specialists,
        include_academic_specialists=include_academic_specialists,
        include_slack=include_slack,
        slack_service=args.slack_service,
    )

    env = os.environ.copy()
    env["A2A_BUILD_ID"] = args.build_id
    env["A2A_BUILD_TIMESTAMP"] = args.build_timestamp
    env["A2A_GIT_SHA"] = args.git_sha
    env["A2A_IMAGE_REF"] = args.image_ref
    env["A2A_TRANSPORT_PROTOCOL"] = args.transport_protocol
    env["A2A_INSTALL_BUILD_TOOLS"] = "true" if args.install_build_tools else "false"
    env["A2A_TORCH_VARIANT"] = "gpu" if args.gpu else "cpu"
    env["A2A_BASE_IMAGE"] = (
        args.gpu_base_image if args.gpu else "python:3.11-slim"
    )

    compose_args = _compose_base_args(compose_files)

    print("A2A rollout plan")
    print(f"- Compose files: {', '.join(compose_files)}")
    print(f"- Services: {', '.join(services)}")
    print(f"- Transport protocol: {args.transport_protocol}")
    print(f"- Build ID: {args.build_id}")
    print(f"- Build timestamp: {args.build_timestamp}")
    print(f"- Git SHA: {args.git_sha}")
    print(f"- Image ref: {args.image_ref}")
    print(f"- Slack rollout: {include_slack}")
    if include_slack:
        print(f"- Slack service: {args.slack_service}")
    print(f"- Install build tools: {args.install_build_tools}")
    print(f"- GPU mode: {args.gpu}")
    if args.gpu:
        print(f"- GPU base image: {args.gpu_base_image}")
        print(f"- GPU scope: {args.gpu_scope}")

    if not args.skip_build:
        _run_command([*compose_args, "build", "api"], env=env)

    if args.build_only:
        return 0

    if include_slack:
        opposite_slack_service = _opposite_slack_service_name(args.slack_service)
        if opposite_slack_service:
            _run_command([*compose_args, "stop", opposite_slack_service], env=env)

    _run_command(_compose_up_args(compose_args, services), env=env)
    if not args.skip_health_check:
        _wait_for_health_targets(
            _health_targets(
                include_student=include_student,
                include_academic=include_academic,
                include_announcement=args.include_announcement,
                include_event=args.include_event,
                include_finance_specialists=include_finance_specialists,
                include_student_specialists=include_student_specialists,
                include_academic_specialists=include_academic_specialists,
            ),
            expected_build_id=args.build_id,
            startup_timeout_seconds=args.health_timeout_seconds,
            request_timeout_seconds=args.health_request_timeout_seconds,
            poll_interval_seconds=args.health_poll_interval_seconds,
        )
        if include_slack:
            _wait_for_container_running(
                _slack_container_name(args.slack_service),
                env=env,
                startup_timeout_seconds=min(30.0, args.health_timeout_seconds),
                poll_interval_seconds=args.health_poll_interval_seconds,
            )

    legacy_refs = _report_legacy_images()
    if args.cleanup_legacy_images:
        _remove_legacy_images(legacy_refs, env=env)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
