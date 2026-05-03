"""Slack Bolt app wiring testleri."""

from src.core.config import settings
from src.slack.app import (
    _is_duplicate_event,
    _process_and_reply,
    _recent_event_keys,
    _should_ignore_event,
    create_slack_app,
)
from src.slack.service import SlackIncomingMessage


class _FakeSlackService:
    async def handle_message(self, message):
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
    assert _should_ignore_event({"text": "hello"}) is False


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

    async def chat_postMessage(self, **kwargs):
        self.messages.append(kwargs)


def test_process_and_reply_posts_generated_messages():
    import asyncio

    client = _FakeSlackClient()

    asyncio.run(
        _process_and_reply(
            service=_FakeSlackService(),
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
            "text": "ok: help",
            "thread_ts": "100.1",
            "unfurl_links": False,
            "unfurl_media": False,
        }
    ]
