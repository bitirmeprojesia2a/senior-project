"""Slack runtime helper for local and Docker modes."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence


ROOT_DIR = Path(__file__).resolve().parent.parent

A2A_COMPOSE_FILES = [
    "docker-compose.a2a-existing-infra.yml",
    "docker-compose.a2a-existing-infra-student.yml",
    "docker-compose.a2a-existing-infra-academic.yml",
    "docker-compose.a2a-existing-infra-capabilities.yml",
    "docker-compose.a2a-existing-infra-finance-specialists.yml",
    "docker-compose.a2a-existing-infra-student-specialists.yml",
    "docker-compose.a2a-existing-infra-academic-specialists.yml",
    "docker-compose.a2a-app-gpu.yml",
    "docker-compose.slack.yml",
]

SLACK_ONLY_COMPOSE_FILES = ["docker-compose.slack.yml"]

DEFAULT_A2A_GPU_BASE_IMAGE = "pytorch/pytorch:2.6.0-cuda12.4-cudnn9-runtime"


def _compose_args(files: Sequence[str]) -> list[str]:
    args = ["docker", "compose"]
    for file_name in files:
        args.extend(["-f", file_name])
    return args


def _run(command: Sequence[str]) -> int:
    print("> " + " ".join(command))
    completed = subprocess.run(command, cwd=ROOT_DIR, check=False)
    return completed.returncode


def _service_name(runtime: str) -> str:
    return "slack-bot-a2a" if runtime == "a2a" else "slack-bot-inprocess"


def _opposite_service_name(runtime: str) -> str:
    return "slack-bot-inprocess" if runtime == "a2a" else "slack-bot-a2a"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Slack bot runtime'ini kisa komutlarla ac/kapat.",
    )
    parser.add_argument(
        "action",
        choices=("up", "stop", "restart", "logs", "status"),
        help="Yapilacak islem.",
    )
    parser.add_argument(
        "--runtime",
        choices=("a2a", "inprocess"),
        default="a2a",
        help="Slack bot runtime'i. Varsayilan: a2a.",
    )
    parser.add_argument(
        "--no-a2a-stack",
        action="store_true",
        help="A2A compose dosyalarini ekleme; sadece docker-compose.slack.yml kullan.",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help=(
            "Deprecated: Slack runtime shared image build etmez. "
            "A2A image rollout icin scripts.a2a_rollout kullan."
        ),
    )
    parser.add_argument(
        "--tail",
        default="100",
        help="logs icin satir sayisi.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.build:
        print(
            "--build artik slack_runtime icinde desteklenmiyor. "
            "Shared A2A image build/recreate icin `python -m scripts.a2a_rollout` "
            "kullanin; slack_runtime sadece mevcut image ile Slack servisini "
            "acip kapatir.",
            file=sys.stderr,
        )
        return 2

    service = _service_name(args.runtime)
    compose_files = (
        SLACK_ONLY_COMPOSE_FILES
        if args.no_a2a_stack or args.runtime == "inprocess"
        else A2A_COMPOSE_FILES
    )
    if args.runtime == "a2a" and not args.no_a2a_stack:
        os.environ.setdefault("A2A_TORCH_VARIANT", "gpu")
        os.environ.setdefault("A2A_BASE_IMAGE", DEFAULT_A2A_GPU_BASE_IMAGE)
        os.environ.setdefault("A2A_TRANSPORT_PROTOCOL", "jsonrpc")
    compose = _compose_args(compose_files)

    if args.action == "up":
        stop_other_code = _run([*compose, "stop", _opposite_service_name(args.runtime)])
        if stop_other_code != 0:
            return stop_other_code
        command = [*compose, "up", "-d"]
        if args.build:
            command.append("--build")
        else:
            command.append("--no-build")
        command.append(service)
        return _run(command)

    if args.action == "stop":
        return _run([*compose, "stop", service])

    if args.action == "restart":
        stop_other_code = _run([*compose, "stop", _opposite_service_name(args.runtime)])
        if stop_other_code != 0:
            return stop_other_code
        stop_code = _run([*compose, "stop", service])
        if stop_code != 0:
            return stop_code
        command = [*compose, "up", "-d"]
        if args.build:
            command.append("--build")
        else:
            command.append("--no-build")
        command.append(service)
        return _run(command)

    if args.action == "logs":
        return _run([*compose, "logs", "-f", "--tail", str(args.tail), service])

    if args.action == "status":
        return _run([*compose, "ps", service])

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
