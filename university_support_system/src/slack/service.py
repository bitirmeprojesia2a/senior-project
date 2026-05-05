"""Slack adapter servis katmani."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.core.text_normalization import normalize_text
from src.db.auth import AuthContext, AuthService
from src.notifications import EmailDeliveryError
from src.orchestrators.main import MainOrchestrator
from src.slack.formatting import normalize_slack_text, split_slack_message


class SlackCommandKind(str, Enum):
    """Slack mesajindan cozumlenen komut tipi."""

    HELP = "help"
    LOGIN = "login"
    VERIFY = "verify"
    LOGOUT = "logout"
    QUERY = "query"


@dataclass(frozen=True)
class SlackCommand:
    """Slack komut parser sonucu."""

    kind: SlackCommandKind
    query: str | None = None
    student_number: str | None = None
    otp_code: str | None = None


@dataclass(frozen=True)
class SlackIncomingMessage:
    """Slack eventlerinden adapter'a tasinan sade mesaj modeli."""

    text: str
    user_id: str
    channel_id: str
    ts: str | None = None
    thread_ts: str | None = None


def parse_slack_command(text: str | None) -> SlackCommand:
    """Kullanicinin Slack mesajini komut veya normal soru olarak cozumler."""

    cleaned = normalize_slack_text(text)
    if not cleaned:
        return SlackCommand(kind=SlackCommandKind.HELP)

    parts = cleaned.split()
    keyword = normalize_text(parts[0]).strip()

    if keyword in {"help", "yardim", "komut", "komutlar"}:
        return SlackCommand(kind=SlackCommandKind.HELP)

    if keyword in {"login", "giris", "baglan", "oturum"}:
        if len(parts) < 2:
            return SlackCommand(kind=SlackCommandKind.LOGIN)
        return SlackCommand(kind=SlackCommandKind.LOGIN, student_number=parts[1])

    if keyword in {"verify", "dogrula", "onayla"}:
        if len(parts) < 3:
            return SlackCommand(kind=SlackCommandKind.VERIFY)
        return SlackCommand(
            kind=SlackCommandKind.VERIFY,
            student_number=parts[1],
            otp_code=parts[2],
        )

    if keyword in {"logout", "cikis", "oturumu-kapat", "oturumu_kapat"}:
        return SlackCommand(kind=SlackCommandKind.LOGOUT)

    return SlackCommand(kind=SlackCommandKind.QUERY, query=cleaned)


def build_slack_context_id(message: SlackIncomingMessage) -> str:
    """Thread bazli konusma baglami uretir."""

    if message.channel_id.startswith("D") and not message.thread_ts:
        return f"slack:{message.channel_id}:{message.user_id}"
    thread_key = message.thread_ts or message.ts or message.user_id
    return f"slack:{message.channel_id}:{thread_key}"


def build_help_text() -> str:
    """Slack icin kisa kullanim metni."""

    return (
        "OMÜ destek botu kullanımı:\n"
        "- Normal soru: `Ders kaydı ne zaman başlıyor?`\n"
        "- Giriş: `login 20210001`\n"
        "- OTP doğrulama: `verify 20210001 123456`\n"
        "- Oturum kapatma: `logout`\n\n"
        "Giriş yapmadan genel duyuru, etkinlik, harç ve müfredat sorularını sorabilirsiniz. "
        "Kişisel bilgiler için Slack kullanıcınızı OTP ile doğrulamanız gerekir."
    )


class SlackBotService:
    """Slack mesajlarini auth ve orchestrator akisina baglar."""

    def __init__(
        self,
        *,
        orchestrator: MainOrchestrator,
        auth_service: AuthService,
        llm_profile: str | None = None,
    ) -> None:
        self.orchestrator = orchestrator
        self.auth_service = auth_service
        self.llm_profile = llm_profile

    async def handle_message(self, message: SlackIncomingMessage) -> list[str]:
        """Slack mesajini isler ve gonderilecek cevap parcalarini dondurur."""

        command = parse_slack_command(message.text)
        if command.kind == SlackCommandKind.HELP:
            return split_slack_message(build_help_text())
        if command.kind == SlackCommandKind.LOGIN:
            return split_slack_message(await self._handle_login(command, message.user_id))
        if command.kind == SlackCommandKind.VERIFY:
            return split_slack_message(await self._handle_verify(command, message.user_id))
        if command.kind == SlackCommandKind.LOGOUT:
            return split_slack_message(await self._handle_logout(message.user_id))
        return await self._handle_query(command, message)

    async def _handle_login(self, command: SlackCommand, slack_user_id: str) -> str:
        if not command.student_number:
            return "Giriş için `login <ogrenci_no>` formatını kullanın."

        try:
            result = await self.auth_service.request_otp(
                student_number=command.student_number,
                slack_user_id=slack_user_id,
            )
        except EmailDeliveryError as exc:
            return f"Doğrulama e-postası gönderilemedi: {exc}"
        if result is None:
            return "Bu öğrenci numarası için aktif kayıt bulunamadı."
        if not result.get("success"):
            return str(result.get("message") or "OTP kodu oluşturulamadı.")

        masked_email = result.get("masked_email") or "öğrenci e-postanız"
        return (
            f"Doğrulama kodu {masked_email} adresine gönderildi. "
            f"Slack'te `verify {command.student_number} <kod>` yazarak doğrulayabilirsiniz."
        )

    async def _handle_verify(self, command: SlackCommand, slack_user_id: str) -> str:
        if not command.student_number or not command.otp_code:
            return "Doğrulama için `verify <ogrenci_no> <kod>` formatını kullanın."

        result = await self.auth_service.verify_otp(
            student_number=command.student_number,
            otp_code=command.otp_code,
            slack_user_id=slack_user_id,
        )
        if result is None:
            return "Bu öğrenci numarası için aktif kayıt bulunamadı."
        if not result.get("success"):
            return str(result.get("message") or "OTP doğrulanamadı.")

        full_name = result.get("full_name") or "öğrenci"
        department = result.get("student_department") or "bölüm bilgisi yok"
        return f"Giriş tamamlandı: {full_name} ({department}). Artık kişisel soruları yanıtlayabilirim."

    async def _handle_logout(self, slack_user_id: str) -> str:
        auth_context = await self.auth_service.resolve_auth_context(slack_user_id=slack_user_id)
        if auth_context is None:
            return "Aktif Slack oturumu bulunamadı."
        invalidated = await self.auth_service.invalidate_slack_sessions(slack_user_id)
        if not invalidated:
            return "Oturum kapatılamadı; zaten pasif olabilir."
        return "Slack oturumunuz kapatıldı."

    async def _handle_query(self, command: SlackCommand, message: SlackIncomingMessage) -> list[str]:
        query = command.query or normalize_slack_text(message.text)
        auth_context = await self.auth_service.resolve_auth_context(slack_user_id=message.user_id)
        response = await self.orchestrator.handle_query(
            query,
            context_id=build_slack_context_id(message),
            user_id=message.user_id,
            student_id=auth_context.student_db_id if auth_context else None,
            student_number=auth_context.student_number if auth_context else None,
            student_full_name=auth_context.full_name if auth_context else None,
            student_department=auth_context.student_department if auth_context else None,
            student_faculty=auth_context.student_faculty if auth_context else None,
            student_type=auth_context.student_type if auth_context else None,
            llm_profile=self.llm_profile,
            is_authenticated=auth_context.is_authenticated if auth_context else False,
        )
        return split_slack_message(response.answer)


def auth_context_to_dict(auth_context: AuthContext | None) -> dict:
    """Debug/test amacli AuthContext serilestirme yardimcisi."""

    if auth_context is None:
        return {"is_authenticated": False}
    return {
        "is_authenticated": auth_context.is_authenticated,
        "student_db_id": auth_context.student_db_id,
        "student_number": auth_context.student_number,
        "student_department": auth_context.student_department,
        "student_faculty": auth_context.student_faculty,
        "slack_user_id": auth_context.slack_user_id,
    }
