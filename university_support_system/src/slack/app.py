"""Slack Bolt uygulaması."""

from __future__ import annotations

import logging
import asyncio
import time

from slack_bolt.async_app import AsyncApp
from slack_sdk.web.async_client import AsyncWebClient

from src.core.config import settings
from src.db import AuthService, ConversationContextService
from src.orchestrators.main import MainOrchestrator
from src.slack.service import SlackBotService, SlackIncomingMessage

logger = logging.getLogger(__name__)

_SLACK_ACCEPT_ENCODING = "gzip, deflate"
_RECENT_EVENT_TTL_SECONDS = 120.0
_RECENT_EVENT_MAX_SIZE = 512
_recent_event_keys: dict[str, float] = {}


def build_default_slack_service() -> SlackBotService:
    """Prod çalışma için varsayılan Slack servislerini kurar."""

    return SlackBotService(
        orchestrator=MainOrchestrator(conversation_service=ConversationContextService()),
        auth_service=AuthService(),
    )


def create_slack_app(*, service: SlackBotService | None = None) -> AsyncApp:
    """Slack Bolt AsyncApp oluşturur ve event handler'larını bağlar."""

    if not settings.slack.bot_token:
        raise RuntimeError("SLACK_BOT_TOKEN ayarlanmamış.")
    if not settings.slack.signing_secret:
        raise RuntimeError("SLACK_SIGNING_SECRET ayarlanmamış.")

    active_service = service or build_default_slack_service()
    slack_client = AsyncWebClient(
        token=settings.slack.bot_token,
        headers={"Accept-Encoding": _SLACK_ACCEPT_ENCODING},
    )
    app = AsyncApp(
        client=slack_client,
        signing_secret=settings.slack.signing_secret,
    )

    async def _reply(event: dict, say) -> None:
        if _should_ignore_event(event):
            return
        if _is_duplicate_event(event):
            return

        slack_message = SlackIncomingMessage(
            text=str(event.get("text") or ""),
            user_id=str(event.get("user") or ""),
            channel_id=str(event.get("channel") or ""),
            ts=event.get("ts"),
            thread_ts=event.get("thread_ts"),
        )
        if not slack_message.text or not slack_message.user_id or not slack_message.channel_id:
            return

        reply_thread_ts = slack_message.thread_ts or slack_message.ts
        asyncio.create_task(
            _process_and_reply(
                service=active_service,
                message=slack_message,
                client=app.client,
                thread_ts=reply_thread_ts,
            )
        )

    @app.event("app_mention")
    async def handle_app_mention(event, say):
        await _reply(event, say)

    @app.event("message")
    async def handle_direct_message(event, say):
        if event.get("channel_type") != "im":
            return
        await _reply(event, say)

    return app


def _should_ignore_event(event: dict) -> bool:
    """Bot/self generated Slack eventlerini atlar."""

    if event.get("bot_id") or event.get("bot_profile"):
        return True
    subtype = event.get("subtype")
    return subtype not in {None, "file_share"}


def _is_duplicate_event(event: dict) -> bool:
    """Aynı Slack event'i kısa süre içinde tekrar gelirse tekrar cevaplama."""

    now = time.monotonic()
    expired = [
        key for key, seen_at in _recent_event_keys.items()
        if now - seen_at > _RECENT_EVENT_TTL_SECONDS
    ]
    for key in expired:
        _recent_event_keys.pop(key, None)

    event_key = (
        str(event.get("client_msg_id") or "").strip()
        or str(event.get("event_id") or "").strip()
        or "|".join(
            str(event.get(field) or "").strip()
            for field in ("channel", "user", "ts", "text")
        )
    )
    if not event_key.strip("|"):
        return False
    if event_key in _recent_event_keys:
        return True
    if len(_recent_event_keys) >= _RECENT_EVENT_MAX_SIZE:
        oldest_key = min(_recent_event_keys, key=_recent_event_keys.get)
        _recent_event_keys.pop(oldest_key, None)
    _recent_event_keys[event_key] = now
    return False


async def _process_and_reply(
    *,
    service: SlackBotService,
    message: SlackIncomingMessage,
    client,
    thread_ts: str | None,
) -> None:
    """Slack event ack'ini bekletmeden cevabı arka planda üretir."""

    # Immediately post a short placeholder so the user knows the bot is working.
    thinking_text = "Cevabınız hazırlanıyor, lütfen bekleyin..."
    try:
        thinking_msg = await client.chat_postMessage(
            channel=message.channel_id,
            text=thinking_text,
            thread_ts=thread_ts,
            unfurl_links=False,
            unfurl_media=False,
        )
        thinking_ts = thinking_msg.get("message", {}).get("ts") or thinking_msg.get("ts")
    except Exception:
        thinking_ts = None

    try:
        replies = await service.handle_message(message)
    except Exception:
        logger.exception("slack_message_failed")
        replies = [
            "Slack isteği işlenirken hata oluştu. Sistem ayaktaysa birazdan tekrar deneyebilirsiniz."
        ]

    # Update the thinking placeholder with the first reply chunk
    if thinking_ts and replies:
        try:
            await client.chat_update(
                channel=message.channel_id,
                ts=thinking_ts,
                text=replies[0],
            )
            replies = replies[1:]
        except Exception:
            logger.debug("slack_thinking_update_failed", exc_info=True)

    for reply in replies:
        await client.chat_postMessage(
            channel=message.channel_id,
            text=reply,
            thread_ts=thread_ts,
            unfurl_links=False,
            unfurl_media=False,
        )
