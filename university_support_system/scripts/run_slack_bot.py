"""Slack Socket Mode botunu baslatir."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Slack Socket Mode botunu baslatir.")
    parser.add_argument(
        "--runtime",
        choices=("inprocess", "a2a"),
        default=os.environ.get("SLACK_RUNTIME", "inprocess"),
        help="Slack botunun kullanacagi orchestrator runtime'i.",
    )
    parser.add_argument(
        "--a2a-endpoint-profile",
        choices=("local", "docker"),
        default=os.environ.get("SLACK_A2A_ENDPOINT_PROFILE", "local"),
        help="A2A runtime icin varsayilan endpoint adresleri.",
    )
    parser.add_argument(
        "--transport-protocol",
        choices=("rest", "jsonrpc"),
        default=os.environ.get("A2A_TRANSPORT_PROTOCOL", "jsonrpc"),
        help="A2A HTTP transport protokolu.",
    )
    parser.add_argument(
        "--slack-env-prefix",
        default=os.environ.get("SLACK_ENV_PREFIX"),
        help=(
            "Ikinci Slack app/token seti icin prefix. Ornek: SLACK_A2A verilirse "
            "SLACK_A2A_BOT_TOKEN, SLACK_A2A_SIGNING_SECRET, SLACK_A2A_APP_TOKEN kullanilir."
        ),
    )
    return parser.parse_args()


def _copy_prefixed_slack_env(prefix: str | None) -> None:
    if not prefix:
        return
    normalized = prefix.rstrip("_")
    mapping = {
        f"{normalized}_BOT_TOKEN": "SLACK_BOT_TOKEN",
        f"{normalized}_SIGNING_SECRET": "SLACK_SIGNING_SECRET",
        f"{normalized}_APP_TOKEN": "SLACK_APP_TOKEN",
    }
    for source, target in mapping.items():
        value = os.environ.get(source)
        if value:
            os.environ[target] = value


def _configure_runtime_env(args: argparse.Namespace) -> None:
    _copy_prefixed_slack_env(args.slack_env_prefix)

    if args.runtime == "inprocess":
        os.environ.setdefault("A2A_MODE", "inprocess")
        os.environ.setdefault("A2A_SPECIALIST_MODE", "inprocess")
        return

    os.environ["A2A_MODE"] = "http"
    os.environ.setdefault("A2A_SPECIALIST_MODE", "http")
    os.environ["A2A_TRANSPORT_PROTOCOL"] = args.transport_protocol
    os.environ.setdefault("A2A_DEPARTMENT_TIMEOUT_SECONDS", "75")
    os.environ.setdefault("A2A_TIMEOUT_SECONDS", "30")

    if args.a2a_endpoint_profile == "docker":
        defaults = {
            "A2A_STUDENT_AFFAIRS_URL": "http://agent-student-affairs:8101",
            "A2A_ACADEMIC_PROGRAMS_URL": "http://agent-academic:8102",
            "A2A_FINANCE_URL": "http://agent-finance:8103",
            "A2A_ANNOUNCEMENT_URL": "http://agent-announcement:8104",
            "A2A_EVENT_URL": "http://agent-event:8105",
        }
    else:
        defaults = {
            "A2A_STUDENT_AFFAIRS_URL": "http://localhost:8101",
            "A2A_ACADEMIC_PROGRAMS_URL": "http://localhost:8102",
            "A2A_FINANCE_URL": "http://localhost:8103",
            "A2A_ANNOUNCEMENT_URL": "http://localhost:8104",
            "A2A_EVENT_URL": "http://localhost:8105",
        }
    for key, value in defaults.items():
        os.environ.setdefault(key, value)


async def main() -> None:
    """Slack bot giris noktasi."""

    args = _parse_args()
    _configure_runtime_env(args)

    from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

    from src.core.config import settings
    from src.db.connection import dispose_engine, init_engine
    from src.slack.app import create_slack_app

    logging.basicConfig(level=getattr(logging, settings.server.log_level.upper(), logging.INFO))
    if not settings.slack.socket_mode_configured:
        raise RuntimeError(
            "Socket Mode icin SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET ve SLACK_APP_TOKEN ayarlanmali."
        )

    init_engine()
    app = create_slack_app()
    try:
        handler = AsyncSocketModeHandler(
            app,
            settings.slack.app_token,
            web_client=app.client,
        )
        await handler.start_async()
    finally:
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())
