"""Slack Bolt app wiring testleri."""

import asyncio
import logging

from src.core.config import settings
from src.slack.app import (
    _extract_file_attachments,
    _is_duplicate_event,
    _log_background_task_result,
    _process_and_reply,
    _recent_event_keys,
    _should_ignore_event,
    create_slack_app,
)
from src.slack.service import SlackIncomingMessage


class _FakeSlackService:
    def __init__(self):
        self.last_slack_client = None

    async def handle_message(self, message, *, slack_client=None):
        self.last_slack_client = slack_client
        return [f"ok: {message.text}"]


def test_create_slack_app_registers_with_configured_tokens():
    previous_bot_token = settings.slack.bot_token
    previous_signing_secret = settings.slack.signing_secret
    try:
        settings.slack.bot_token = "xoxb-test-token"
        settings.slack.signing_secret = "test-signing-secret"

        app = create_slack_app(service=_FakeSlackService())

        assert app is not None
        assert app.client.headers["Accept-Encoding"] == "gzip, deflate"
    finally:
        settings.slack.bot_token = previous_bot_token
        settings.slack.signing_secret = previous_signing_secret


def test_should_ignore_bot_events():
    assert _should_ignore_event({"bot_id": "B123"}) is True
    assert _should_ignore_event({"subtype": "message_changed"}) is True
    assert _should_ignore_event({"subtype": "file_share"}) is False
    assert _should_ignore_event({"text": "hello"}) is False


def test_extract_file_attachments_from_file_share_event():
    attachments = _extract_file_attachments(
        {
            "files": [
                {
                    "id": "F1",
                    "name": "transkript.pdf",
                    "mimetype": "application/pdf",
                    "size": "123",
                    "url_private_download": "https://files.slack.test/F1",
                }
            ]
        }
    )

    assert len(attachments) == 1
    assert attachments[0].id == "F1"
    assert attachments[0].name == "transkript.pdf"
    assert attachments[0].size == 123


def test_duplicate_slack_event_is_ignored_once_seen():
    _recent_event_keys.clear()
    event = {
        "client_msg_id": "client-1",
        "channel": "D123",
        "user": "U123",
        "ts": "100.1",
        "text": "Diş hekimliği dönem ücreti ne kadar?",
    }

    assert _is_duplicate_event(event) is False
    assert _is_duplicate_event(event) is True


class _FakeSlackClient:
    def __init__(self):
        self.messages = []
        self.updates = []

    async def chat_postMessage(self, **kwargs):
        self.messages.append(kwargs)
        return {"message": {"ts": f"msg-{len(self.messages)}"}}

    async def chat_update(self, **kwargs):
        self.updates.append(kwargs)
        return {"ok": True}


def test_process_and_reply_posts_generated_messages():
    client = _FakeSlackClient()
    service = _FakeSlackService()

    asyncio.run(
        _process_and_reply(
            service=service,
            message=SlackIncomingMessage(
                text="help",
                user_id="U123",
                channel_id="D123",
                ts="100.1",
            ),
            client=client,
            thread_ts="100.1",
        )
    )

    assert client.messages == [
        {
            "channel": "D123",
            "text": "Cevabınız hazırlanıyor, lütfen bekleyin...",
            "thread_ts": "100.1",
            "unfurl_links": False,
            "unfurl_media": False,
        }
    ]
    assert client.updates == [
        {
            "channel": "D123",
            "ts": "msg-1",
            "text": "ok: help",
        }
    ]
    assert service.last_slack_client is client


def test_background_task_result_logs_exceptions(caplog):
    async def _raise_error():
        raise RuntimeError("background failed")

    async def _run():
        task = asyncio.create_task(_raise_error())
        await asyncio.sleep(0)
        with caplog.at_level(logging.ERROR):
            _log_background_task_result(task)

    asyncio.run(_run())

    assert "slack_background_task_failed" in caplog.text
