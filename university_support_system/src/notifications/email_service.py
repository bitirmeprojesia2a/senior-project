"""SMTP tabanli e-posta gonderim servisi."""

from __future__ import annotations

import asyncio
import smtplib
from email.message import EmailMessage
from typing import Optional

from src.core.config import settings


class EmailDeliveryError(RuntimeError):
    """E-posta gonderimi basarisiz oldugunda firlatilir."""


class EmailService:
    """Gercek SMTP baglantisi ile e-posta gonderir."""

    def __init__(self) -> None:
        self._settings = settings.email

    @property
    def is_configured(self) -> bool:
        return self._settings.is_configured

    async def send_otp_email(
        self,
        *,
        to_email: str,
        full_name: str,
        otp_code: str,
        expires_in_minutes: int,
    ) -> None:
        if not self.is_configured:
            raise EmailDeliveryError(
                "SMTP ayarlari eksik. EMAIL_FROM_EMAIL ve baglanti ayarlari tanimli olmali."
            )

        display_name = self._display_name()
        subject = f"{display_name} Dogrulama Kodu"
        body = (
            f"Merhaba {full_name},\n\n"
            "Kisisel ogrenci bilgilerine dayali sorunuza yanit verebilmek icin kimlik dogrulamasi gerekiyor.\n"
            f"Tek kullanimlik dogrulama kodunuz: {otp_code}\n"
            f"Bu kod {expires_in_minutes} dakika boyunca gecerlidir.\n\n"
            "Bu islemi siz baslatmadiysaniz bu e-postayi dikkate almayabilirsiniz.\n\n"
            f"{display_name}"
        )
        await asyncio.to_thread(
            self._send_email_sync,
            to_email=to_email,
            subject=subject,
            body=body,
        )

    def _send_email_sync(self, *, to_email: str, subject: str, body: str) -> None:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self._format_from_header()
        message["To"] = to_email
        message.set_content(body)

        try:
            with smtplib.SMTP(
                host=self._settings.host,
                port=self._settings.port,
                timeout=self._settings.timeout_seconds,
            ) as smtp:
                if self._settings.use_tls:
                    smtp.starttls()
                if self._settings.username:
                    smtp.login(self._settings.username, self._settings.password or "")
                smtp.send_message(message)
        except (smtplib.SMTPException, OSError) as exc:  # pragma: no cover - network/runtime dependent
            raise EmailDeliveryError(f"E-posta gonderimi basarisiz oldu: {exc}") from exc

    def _format_from_header(self) -> str:
        from_email = self._settings.from_email
        if from_email is None:
            raise EmailDeliveryError("EMAIL_FROM_EMAIL ayari eksik.")

        from_name: Optional[str] = self._display_name()
        if from_name:
            return f"{from_name} <{from_email}>"
        return from_email

    def _display_name(self) -> str:
        configured = (self._settings.from_name or "").strip()
        if configured and configured not in {"OMU Destek Sistemi", "OMÜ Destek Sistemi"}:
            return configured
        return settings.institution.support_bot_name
