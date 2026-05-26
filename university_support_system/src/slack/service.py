"""Slack adapter servis katmani."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

import httpx

from src.core.config import settings
from src.core.text_normalization import normalize_text
from src.db.auth import AuthContext, AuthService
from src.notifications import EmailDeliveryError
from src.orchestrators.main import MainOrchestrator
from src.slack.formatting import normalize_slack_text, split_slack_message
from src.transcripts import (
    DocumentContextTarget,
    TranscriptDocument,
    TranscriptProcessor,
    TranscriptSessionStore,
    UploadedDocumentArbiter,
    is_transcript_followup_query,
    is_uploaded_document_followup_query,
)
from src.transcripts.service import TranscriptProcessingError


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
class SlackFileAttachment:
    """Slack file metadata carried into the adapter."""

    id: str | None = None
    name: str | None = None
    mimetype: str | None = None
    filetype: str | None = None
    size: int | None = None
    url_private: str | None = None
    url_private_download: str | None = None
    content: bytes | None = None


@dataclass(frozen=True)
class SlackIncomingMessage:
    """Slack eventlerinden adapter'a tasinan sade mesaj modeli."""

    text: str
    user_id: str
    channel_id: str
    ts: str | None = None
    thread_ts: str | None = None
    files: tuple[SlackFileAttachment, ...] = ()


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

    thread_key = message.thread_ts or message.ts or message.user_id
    return f"slack:{message.channel_id}:{thread_key}"


def build_uploaded_document_rag_context_id(message: SlackIncomingMessage) -> str:
    """Belge+RAG yardimci aramalarini normal konusma baglamindan ayirir."""

    return f"{build_slack_context_id(message)}:uploaded-document-rag"


def _legacy_build_help_text() -> str:
    """Slack icin kisa kullanim metni."""

    return (
        f"{settings.institution.support_bot_name} kullanımı:\n"
        "- Normal soru: `Ders kaydı ne zaman başlıyor?`\n"
        "- Giriş: `login 20210001`\n"
        "- OTP doğrulama: `verify 20210001 123456`\n"
        "- Oturum kapatma: `logout`\n\n"
        "Giriş yapmadan genel duyuru, etkinlik, harç ve müfredat sorularını sorabilirsiniz. "
        "Kişisel bilgiler için Slack kullanıcınızı OTP ile doğrulamanız gerekir."
    )


def build_help_text() -> str:
    """Slack icin kisa kullanim metni."""

    return (
        f"{settings.institution.support_bot_name} ile şunları sorabilirsiniz:\n"
        "- Öğrenci işleri: ders kaydı, harç borcu, mezuniyet, yaz okulu, staj, yatay geçiş, ÇAP/Yandal\n"
        "- Akademik programlar: ders programı, müfredat, ön koşul, AKTS, derslik\n"
        "- Finans: öğrenim ücreti, katkı payı, Türk/uluslararası öğrenci ücretleri\n"
        "- Duyurular: `güncel duyurular neler?`, `2. duyuruyu özetle`\n"
        "- Transkript: PDF/metin transkript yükleyip `toplam AKTS'im kaç?`, `kaldığım dersler neler?` diye sorabilirsiniz.\n\n"
        "Hesap komutları:\n"
        "- Giriş: `login 20210001`\n"
        "- OTP doğrulama: `verify 20210001 123456`\n"
        "- Oturum kapatma: `logout`\n\n"
        "Giriş yapmadan genel soruları sorabilirsiniz. Kişisel bilgiler için Slack hesabınızı OTP ile doğrulamanız gerekir."
    )


def build_welcome_text(*, user_mention: str | None = None) -> str:
    """Kanal/DM ilk temasinda gonderilecek kisa onboarding metni."""

    bot_name = settings.institution.support_bot_name
    prefix = f"Merhaba {user_mention}, ben {bot_name}.\n\n" if user_mention else f"Merhaba, ben {bot_name}.\n\n"
    return prefix + build_help_text() + "\n\nYardım menüsünü tekrar görmek için `help` yazabilirsiniz."


class SlackBotService:
    """Slack mesajlarini auth ve orchestrator akisina baglar."""

    def __init__(
        self,
        *,
        orchestrator: MainOrchestrator,
        auth_service: AuthService,
        llm_profile: str | None = None,
        transcript_processor: TranscriptProcessor | None = None,
        transcript_store: TranscriptSessionStore | None = None,
        uploaded_document_arbiter: UploadedDocumentArbiter | None = None,
        max_file_bytes: int = 8 * 1024 * 1024,
    ) -> None:
        self.orchestrator = orchestrator
        self.auth_service = auth_service
        self.llm_profile = llm_profile
        self.transcript_processor = transcript_processor
        self.transcript_store = transcript_store or TranscriptSessionStore()
        self.uploaded_document_arbiter = uploaded_document_arbiter or UploadedDocumentArbiter(
            llm_service=getattr(orchestrator, "llm_service", None)
        )
        self.last_document_context_decision: dict[str, object] | None = None
        self.max_file_bytes = max_file_bytes

    async def handle_message(self, message: SlackIncomingMessage, *, slack_client: Any | None = None) -> list[str]:
        """Slack mesajini isler ve gonderilecek cevap parcalarini dondurur."""

        if message.files:
            return await self._handle_file_message(message, slack_client=slack_client)

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

    async def _handle_file_message(
        self,
        message: SlackIncomingMessage,
        *,
        slack_client: Any | None = None,
    ) -> list[str]:
        if self.transcript_processor is None:
            return split_slack_message(
                "Dosya alındı ancak transkript işleme servisi bu çalışma ortamında etkin değil."
            )

        context_id = build_slack_context_id(message)
        processed: list[TranscriptDocument] = []
        errors: list[str] = []
        for file in message.files:
            filename = file.name or file.id or "transkript"
            try:
                content = await self._read_file_content(file, slack_client=slack_client)
                if len(content) > self.max_file_bytes:
                    errors.append(f"{filename}: dosya boyutu sınırı aşıyor.")
                    continue
                processed.append(
                    self.transcript_processor.process_bytes(
                        filename=filename,
                        content=content,
                        mimetype=file.mimetype,
                    )
                )
            except TranscriptProcessingError as exc:
                errors.append(f"{filename}: {exc}")
            except Exception:
                errors.append(f"{filename}: dosya işlenirken beklenmeyen hata oluştu.")

        if not processed:
            detail = "\n".join(f"- {error}" for error in errors) if errors else "- Uygun transkript dosyası bulunamadı."
            return split_slack_message(f"Transkript işlenemedi:\n{detail}")

        document = processed[0]
        query = normalize_slack_text(message.text)
        self.transcript_store.put(
            context_id=context_id,
            user_id=message.user_id,
            document=document,
            last_query=query or None,
        )
        privacy_note = _transcript_privacy_note(message)
        if query and is_uploaded_document_followup_query(query) and _looks_like_uploaded_document_question(query):
            answer = await self.transcript_processor.answer_question(
                document=document,
                query=query,
                llm_profile=self.llm_profile,
            )
            answer = _append_transcript_privacy_note(answer, privacy_note)
            return split_slack_message(answer)

        answer = _format_upload_ready_answer(document)
        if errors:
            answer += "\n\nDiğer dosyalar işlenemedi:\n" + "\n".join(f"- {error}" for error in errors)
        answer = _append_transcript_privacy_note(answer, privacy_note)
        return split_slack_message(answer)

    async def _read_file_content(self, file: SlackFileAttachment, *, slack_client: Any | None = None) -> bytes:
        if file.content is not None:
            return file.content

        resolved_file = file
        if not (file.url_private_download or file.url_private) and file.id and slack_client is not None:
            info = await slack_client.files_info(file=file.id)
            slack_file = (info or {}).get("file") or {}
            resolved_file = SlackFileAttachment(
                id=file.id,
                name=str(slack_file.get("name") or file.name or file.id),
                mimetype=str(slack_file.get("mimetype") or file.mimetype or ""),
                filetype=str(slack_file.get("filetype") or file.filetype or ""),
                size=_safe_int(slack_file.get("size")) or file.size,
                url_private=str(slack_file.get("url_private") or file.url_private or ""),
                url_private_download=str(
                    slack_file.get("url_private_download") or file.url_private_download or ""
                ),
            )

        url = resolved_file.url_private_download or resolved_file.url_private
        if not url:
            raise TranscriptProcessingError("Slack dosya bağlantısı bulunamadı.")
        token = settings.slack.bot_token
        if not token:
            raise TranscriptProcessingError("Slack dosyasını indirmek için bot token gerekli.")

        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.get(url, headers={"Authorization": f"Bearer {token}"})
            response.raise_for_status()
            content = response.content
            content_type = (response.headers.get("content-type") or "").lower()
            mimetype = (resolved_file.mimetype or "").lower()
            filename = (resolved_file.name or "").lower()
            expects_binary_document = (
                "pdf" in mimetype
                or filename.endswith(".pdf")
                or mimetype.startswith("image/")
                or any(filename.endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"))
            )
            if expects_binary_document and (
                "text/html" in content_type
                or content.lstrip().startswith((b"<!DOCTYPE", b"<html", b"<HTML"))
            ):
                raise TranscriptProcessingError(
                    "Slack dosyası indirilemedi. Bot token için `files:read` yetkisini ekleyip Slack app'i "
                    "workspace'e yeniden kurmanız gerekir."
                )
            if "pdf" in mimetype or filename.endswith(".pdf"):
                if not content.lstrip().startswith(b"%PDF"):
                    raise TranscriptProcessingError(
                        "Slack'ten indirilen içerik PDF değil. Botun dosyaya erişimi veya `files:read` yetkisi "
                        "kontrol edilmelidir."
                    )
            return content

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
        self.last_document_context_decision = None
        if self.transcript_processor is not None:
            document = self.transcript_store.get(
                context_id=build_slack_context_id(message),
                user_id=message.user_id,
            )
            if document is not None:
                last_query = self.transcript_store.get_last_query(
                    context_id=build_slack_context_id(message),
                    user_id=message.user_id,
                )
                decision = await self.uploaded_document_arbiter.decide(
                    query=query,
                    document=document,
                    last_query=last_query,
                    llm_profile=self.llm_profile,
                )
                self.last_document_context_decision = decision.to_metadata()
                if decision.target == DocumentContextTarget.UPLOADED_DOCUMENT:
                    answer = await self.transcript_processor.answer_question(
                        document=document,
                        query=decision.effective_query,
                        llm_profile=self.llm_profile,
                        document_intent=decision.document_intent,
                    )
                    self.transcript_store.update_last_query(
                        context_id=build_slack_context_id(message),
                        user_id=message.user_id,
                        last_query=query or decision.effective_query,
                    )
                    answer = _append_transcript_privacy_note(answer, _transcript_privacy_note(message))
                    return split_slack_message(answer)
                if decision.target == DocumentContextTarget.HYBRID_DOCUMENT_RAG:
                    document_answer = await self.transcript_processor.answer_question(
                        document=document,
                        query=decision.effective_query,
                        llm_profile=self.llm_profile,
                        document_intent=decision.document_intent,
                    )
                    auth_context = await self.auth_service.resolve_auth_context(slack_user_id=message.user_id)
                    rag_response = await self.orchestrator.handle_query(
                        _build_hybrid_document_rag_query(query=query, document=document),
                        context_id=build_uploaded_document_rag_context_id(message),
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
                    answer = _format_hybrid_document_rag_answer(
                        document_answer=document_answer,
                        rag_answer=rag_response.answer,
                    )
                    self.transcript_store.update_last_query(
                        context_id=build_slack_context_id(message),
                        user_id=message.user_id,
                        last_query=query or decision.effective_query,
                    )
                    answer = _append_transcript_privacy_note(answer, _transcript_privacy_note(message))
                    return split_slack_message(answer)
                if decision.target == DocumentContextTarget.CLARIFY:
                    return split_slack_message(
                        "Bunu yüklediğiniz belgeye göre mi, yoksa genel üniversite kaynaklarına göre mi cevaplayayım?"
                    )
                if decision.target == DocumentContextTarget.INSTITUTIONAL_RAG:
                    self.transcript_store.update_last_query(
                        context_id=build_slack_context_id(message),
                        user_id=message.user_id,
                        last_query=query,
                    )
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


def _format_transcript_upload_summary(document: TranscriptDocument) -> str:
    lines = [f"- Dosya: {document.filename}", f"- Tespit edilen ders: {len(document.courses)}"]
    if document.program_name:
        lines.append(f"- Program: {document.program_name}")
    if document.total_akts is not None:
        lines.append(f"- Toplam AKTS: {_format_number(document.total_akts)}")
    if document.total_credit is not None:
        lines.append(f"- Toplam kredi: {_format_number(document.total_credit)}")
    if document.gpa is not None:
        lines.append(f"- GNO/AGNO: {_format_number(document.gpa)}")
    if document.failed_courses:
        lines.append(f"- Başarısız görünen ders: {len(document.failed_courses)}")
    if document.warnings:
        lines.append("- Not: " + " ".join(document.warnings))
    return "\n".join(lines)


def _format_upload_ready_answer(document: TranscriptDocument) -> str:
    if document.document_type == "transcript":
        return (
            "Transkript yüklendi ve bu konuşma bağlamına eklendi.\n"
            f"{_format_transcript_upload_summary(document)}\n"
            "Transkriptle ilgili `toplam AKTS`, `mezuniyet için kaç AKTS kaldı`, "
            "`kaldığım dersler`, `geçtiğim dersler` veya `ortalamam nedir` gibi sorular sorabilirsiniz."
        )
    return (
        "Belge yüklendi ve bu konuşma bağlamına eklendi.\n"
        f"{_format_generic_document_upload_summary(document)}\n"
        "Bu belgeyle ilgili `özetler misin?` veya `belgeye göre ...?` şeklinde sorular sorabilirsiniz."
    )


def _format_generic_document_upload_summary(document: TranscriptDocument) -> str:
    debug = document.extraction_debug or {}
    field_count = int(debug.get("field_count") or len(document.fields))
    filled_count = int(
        debug.get("filled_field_count")
        or len([field for field in document.fields if field.state == "filled" and field.value.strip()])
    )
    empty_count = int(
        debug.get("empty_field_count")
        or len([field for field in document.fields if field.state != "filled" or not field.value.strip()])
    )
    lines = [
        f"- Dosya: {document.filename}",
        f"- Tür: {_display_uploaded_document_type(document.document_type)}",
        f"- Metin çıkarma yöntemi: {document.extraction_mode}",
        f"- Tespit edilen alan: {field_count}",
    ]
    if field_count:
        lines.append(f"- Dolu görünen alan: {filled_count}")
        lines.append(f"- Boş/etiket alan: {empty_count}")
    if document.warnings:
        lines.append("- Not: " + " ".join(document.warnings))
    return "\n".join(lines)


def _display_uploaded_document_type(document_type: str) -> str:
    if document_type == "schedule_document":
        return "ders programı belgesi"
    if document_type == "transcript":
        return "transkript"
    if document_type == "form_document":
        return "form/basvuru belgesi"
    if document_type == "student_document":
        return "ogrenci belgesi"
    if document_type == "criminal_record":
        return "adli sicil/sonuc belgesi"
    if document_type == "certificate_or_result":
        return "sonuc belgesi"
    if document_type == "policy_or_instruction":
        return "yonerge/talimat belgesi"
    if document_type == "unknown_document":
        return "bilinmeyen belge"
    return "genel belge"

def _format_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:.2f}".replace(".", ",").rstrip("0").rstrip(",")


def _transcript_privacy_note(message: SlackIncomingMessage) -> str:
    if message.channel_id.startswith("D"):
        return ""
    return (
        "Not: Transkript kisisel veri icerir. Bu belge ve cevap yalnizca bu Slack thread'i "
        "baglaminda tutulur; mumkunse transkriptleri DM uzerinden paylasin."
    )


def _append_transcript_privacy_note(answer: str, note: str) -> str:
    if not note or note in answer:
        return answer
    return f"{answer.rstrip()}\n\n{note}"


def _build_hybrid_document_rag_query(*, query: str, document: TranscriptDocument) -> str:
    topic = _infer_document_rag_topic(document)
    if topic:
        return f"{topic} hakkinda yuklenen belgeyle ilgili kurumsal surec: {query}"
    return f"Yuklenen belgeyle ilgili kurumsal surec: {query}"


def _infer_document_rag_topic(document: TranscriptDocument) -> str | None:
    haystack = normalize_text(f"{document.filename}\n{document.text[:1600]}")
    facts = getattr(document, "facts", None)
    if facts is not None:
        fact_bits = " ".join(
            str(part or "")
            for part in (getattr(facts, "title", None), getattr(facts, "issuer", None), getattr(facts, "status", None))
        )
        haystack = normalize_text(f"{haystack}\n{fact_bits}")
    if document.document_type == "schedule_document" or "ders program" in haystack:
        department_hint = _infer_schedule_department_hint(haystack)
        term_hint = _infer_schedule_term_hint(haystack)
        parts = [part for part in (department_hint, term_hint, "haftalik ders programi") if part]
        return " ".join(parts)
    if document.document_type == "form_document" and "staj" in haystack:
        return "zorunlu staj basvurusu ve staj formu teslim sureci"
    if "staj" in haystack:
        return "zorunlu staj basvurusu ve staj formu teslim sureci"
    if document.document_type == "student_document" or "ogrenci belgesi" in haystack or "ogrencilik" in haystack:
        return "ogrenci belgesi ve ogrencilik durumu"
    if "transkript" in haystack or "not dokum" in haystack:
        return "transkript ve mezuniyet kosullari"
    if "mufredat" in haystack or "ders icer" in haystack:
        return "mufredat ve ders icerikleri"
    return None


def _infer_schedule_department_hint(haystack: str) -> str | None:
    if "bilgisayar muhendis" in haystack:
        return "Bilgisayar Muhendisligi"
    if "elektrik elektronik" in haystack or "elektrik-elektronik" in haystack:
        return "Elektrik-Elektronik Muhendisligi"
    if "fizik ogretmen" in haystack or "fizik egitimi" in haystack:
        return "Fizik Ogretmenligi"
    return None


def _infer_schedule_term_hint(haystack: str) -> str | None:
    year_match = re.search(r"\b(20\d{2})\s*[-/]\s*(\d{2,4})\b", haystack)
    year = ""
    if year_match:
        second = year_match.group(2)
        if len(second) == 2:
            second = year_match.group(1)[:2] + second
        year = f"{year_match.group(1)}-{second}"
    if "bahar" in haystack:
        return f"{year} bahar yariyili".strip()
    if "guz" in haystack:
        return f"{year} guz yariyili".strip()
    return year or None


def _format_hybrid_document_rag_answer(*, document_answer: str, rag_answer: str) -> str:
    clean_document = (document_answer or "").strip()
    clean_rag = (rag_answer or "").strip() or "Kurum kaynaklarında bu adım için net bir bilgi bulamadım."
    if not clean_document:
        return f"Üniversite kaynaklarına göre:\n{clean_rag}"
    return f"Belgeye göre:\n{clean_document}\n\nÜniversite kaynaklarına göre:\n{clean_rag}"


def _uploaded_document_effective_query(*, query: str, last_query: str | None) -> str:
    normalized = normalize_text(query)
    vague_document_repair = any(
        marker in normalized
        for marker in (
            "belgeye gore cevaplamadin",
            "belgeye gore cevaplamadın",
            "belgeye gore cevapla",
            "bu belgeye gore",
        )
    )
    if vague_document_repair and last_query:
        return f"{last_query}\nKullanici duzeltmesi: {query}"
    return query


def _safe_int(value: object) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _looks_like_uploaded_document_question(query: str) -> bool:
    normalized = normalize_text(query)
    if "?" in query:
        return True
    if any(marker in normalized for marker in ("kac", "nedir", "neler", "hangileri", "yorum", "ozet", "listele")):
        return True
    if any(
        marker in normalized
        for marker in (
            "hangi ders",
            "aldigim",
            "aldigi",
            "aldiklarim",
            "aldiklari",
            "almis",
            "almisim",
            "kaldigim",
            "gectigim",
            "basarisiz",
            "basarili",
            "ortalama",
        )
    ):
        return True
    return False
