import asyncio

from src.core.config import settings
from src.notifications.email_service import EmailService


def test_email_service_uses_institution_name_for_legacy_default(monkeypatch):
    monkeypatch.setattr(settings.email, "host", "smtp.example.test")
    monkeypatch.setattr(settings.email, "from_email", "bot@example.test")
    monkeypatch.setattr(settings.email, "from_name", "OMU Destek Sistemi")
    monkeypatch.setattr(settings.institution, "support_bot_name", "ABC Destek Botu")

    service = EmailService()
    sent: dict[str, str] = {}

    def fake_send_email_sync(*, to_email: str, subject: str, body: str) -> None:
        sent["to_email"] = to_email
        sent["subject"] = subject
        sent["body"] = body

    monkeypatch.setattr(service, "_send_email_sync", fake_send_email_sync)

    asyncio.run(
        service.send_otp_email(
            to_email="student@example.test",
            full_name="Test Öğrenci",
            otp_code="123456",
            expires_in_minutes=5,
        )
    )

    assert sent["subject"] == "ABC Destek Botu Dogrulama Kodu"
    assert sent["body"].rstrip().endswith("ABC Destek Botu")
    assert service._format_from_header() == "ABC Destek Botu <bot@example.test>"


def test_email_service_keeps_explicit_from_name(monkeypatch):
    monkeypatch.setattr(settings.email, "host", "smtp.example.test")
    monkeypatch.setattr(settings.email, "from_email", "bot@example.test")
    monkeypatch.setattr(settings.email, "from_name", "Ozel Destek")
    monkeypatch.setattr(settings.institution, "support_bot_name", "ABC Destek Botu")

    service = EmailService()

    assert service._format_from_header() == "Ozel Destek <bot@example.test>"
