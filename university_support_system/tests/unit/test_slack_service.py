"""Slack adapter servis testleri."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.db.auth import AuthContext
from src.db.schemas import UserQueryResponse
from src.slack.service import (
    SlackBotService,
    SlackCommandKind,
    SlackIncomingMessage,
    build_slack_context_id,
    parse_slack_command,
)


def test_parse_slack_command_recognizes_login_verify_logout_and_query():
    assert parse_slack_command("login 20210001").kind == SlackCommandKind.LOGIN
    verify = parse_slack_command("verify 20210001 123456")
    assert verify.kind == SlackCommandKind.VERIFY
    assert verify.student_number == "20210001"
    assert verify.otp_code == "123456"
    assert parse_slack_command("logout").kind == SlackCommandKind.LOGOUT
    query = parse_slack_command("<@U999> EEM214 on kosulu nedir?")
    assert query.kind == SlackCommandKind.QUERY
    assert query.query == "EEM214 on kosulu nedir?"


def test_build_slack_context_id_prefers_thread_ts():
    message = SlackIncomingMessage(
        text="soru",
        user_id="U1",
        channel_id="C1",
        ts="100.1",
        thread_ts="99.9",
    )

    assert build_slack_context_id(message) == "slack:C1:99.9"


def test_build_slack_context_id_uses_stable_dm_context():
    first = SlackIncomingMessage(
        text="Diş hekimliği dönem ücreti ne kadar?",
        user_id="U1",
        channel_id="D1",
        ts="100.1",
    )
    second = SlackIncomingMessage(
        text="Türk öğrenciyim",
        user_id="U1",
        channel_id="D1",
        ts="101.1",
    )

    assert build_slack_context_id(first) == "slack:D1:U1"
    assert build_slack_context_id(second) == "slack:D1:U1"


@dataclass
class _FakeAuthService:
    auth_context: AuthContext | None = None
    requested: tuple[str, str] | None = None
    verified: tuple[str, str, str] | None = None
    invalidated: str | None = None
    invalidated_slack_user_id: str | None = None

    async def request_otp(self, *, student_number: str, slack_user_id: str | None = None):
        self.requested = (student_number, slack_user_id or "")
        return {
            "success": True,
            "student_number": student_number,
            "masked_email": "20******@stu.omu.edu.tr",
        }

    async def verify_otp(self, *, student_number: str, otp_code: str, slack_user_id: str | None = None):
        self.verified = (student_number, otp_code, slack_user_id or "")
        return {
            "success": True,
            "full_name": "Ahmet Yilmaz",
            "student_department": "Bilgisayar Muhendisligi",
        }

    async def resolve_auth_context(self, *, session_token: str | None = None, slack_user_id: str | None = None):
        return self.auth_context

    async def invalidate_session(self, session_token: str):
        self.invalidated = session_token
        return True

    async def invalidate_slack_sessions(self, slack_user_id: str):
        self.invalidated_slack_user_id = slack_user_id
        return True


class _FakeOrchestrator:
    def __init__(self):
        self.last_call = None

    async def handle_query(self, query: str, **kwargs):
        self.last_call = {"query": query, **kwargs}
        return UserQueryResponse(
            answer=f"yanit: {query}",
            departments_involved=["academic_programs"],
            generation_modes=["VT"],
            sources=[],
            response_time_ms=12.0,
            query_id=kwargs.get("context_id") or "ctx",
        )


@pytest.mark.asyncio
async def test_slack_service_login_and_verify_use_slack_identity():
    auth_service = _FakeAuthService()
    service = SlackBotService(orchestrator=_FakeOrchestrator(), auth_service=auth_service)

    login_reply = await service.handle_message(
        SlackIncomingMessage(text="login 20210001", user_id="U123", channel_id="D1")
    )
    verify_reply = await service.handle_message(
        SlackIncomingMessage(text="verify 20210001 123456", user_id="U123", channel_id="D1")
    )

    assert auth_service.requested == ("20210001", "U123")
    assert auth_service.verified == ("20210001", "123456", "U123")
    assert "Dogrulama kodu" in login_reply[0]
    assert "Giris tamamlandi" in verify_reply[0]


@pytest.mark.asyncio
async def test_slack_service_query_passes_auth_context_to_orchestrator():
    auth_context = AuthContext(
        student_db_id=42,
        student_number="20210001",
        full_name="Ahmet Yilmaz",
        student_department="Bilgisayar Muhendisligi",
        student_faculty="Muhendislik Fakultesi",
        student_type="domestic",
        slack_user_id="U123",
        session_token="session-1",
        expires_at=None,
    )
    auth_service = _FakeAuthService(auth_context=auth_context)
    orchestrator = _FakeOrchestrator()
    service = SlackBotService(orchestrator=orchestrator, auth_service=auth_service)

    replies = await service.handle_message(
        SlackIncomingMessage(
            text="EEM214 on kosulu nedir?",
            user_id="U123",
            channel_id="D1",
            ts="100.1",
        )
    )

    assert replies == ["yanit: EEM214 on kosulu nedir?"]
    assert orchestrator.last_call["context_id"] == "slack:D1:U123"
    assert orchestrator.last_call["student_id"] == 42
    assert orchestrator.last_call["student_department"] == "Bilgisayar Muhendisligi"
    assert orchestrator.last_call["student_type"] == "domestic"
    assert orchestrator.last_call["is_authenticated"] is True


@pytest.mark.asyncio
async def test_slack_service_logout_invalidates_all_slack_sessions():
    auth_context = AuthContext(
        student_db_id=42,
        student_number="20210001",
        full_name="Ahmet Yilmaz",
        student_department="Bilgisayar Muhendisligi",
        student_faculty="Muhendislik Fakultesi",
        slack_user_id="U123",
        session_token="session-1",
        expires_at=None,
    )
    auth_service = _FakeAuthService(auth_context=auth_context)
    service = SlackBotService(orchestrator=_FakeOrchestrator(), auth_service=auth_service)

    replies = await service.handle_message(
        SlackIncomingMessage(text="logout", user_id="U123", channel_id="D1")
    )

    assert auth_service.invalidated is None
    assert auth_service.invalidated_slack_user_id == "U123"
    assert replies == ["Slack oturumunuz kapatildi."]
