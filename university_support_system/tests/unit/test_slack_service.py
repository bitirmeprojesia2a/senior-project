"""Slack adapter servis testleri."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.db.auth import AuthContext
from src.db.schemas import UserQueryResponse
import src.slack.service as slack_service_module
import src.transcripts.service as transcript_service_module
from src.slack.service import (
    SlackBotService,
    SlackCommandKind,
    SlackFileAttachment,
    SlackIncomingMessage,
    build_help_text,
    build_slack_context_id,
    build_uploaded_document_rag_context_id,
    build_welcome_text,
    parse_slack_command,
)
from src.transcripts import TranscriptProcessor, TranscriptSessionStore
from src.transcripts.service import TranscriptProcessingError


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


def test_slack_help_and_welcome_text_cover_core_commands_and_transcript():
    help_text = build_help_text()
    welcome_text = build_welcome_text(user_mention="<@U123>")

    assert "login 20210001" in help_text
    assert "verify 20210001 123456" in help_text
    assert "logout" in help_text
    assert "Transkript" in help_text
    assert "duyuru" in help_text
    assert "<@U123>" in welcome_text
    assert "help" in welcome_text


def test_slack_help_uses_institution_bot_name(monkeypatch):
    monkeypatch.setattr(slack_service_module.settings.institution, "support_bot_name", "ABC Destek Botu")

    assert build_help_text().startswith("ABC Destek Botu")
    assert "ben ABC Destek Botu" in build_welcome_text()


def test_build_slack_context_id_prefers_thread_ts():
    message = SlackIncomingMessage(
        text="soru",
        user_id="U1",
        channel_id="C1",
        ts="100.1",
        thread_ts="99.9",
    )

    assert build_slack_context_id(message) == "slack:C1:99.9"


def test_build_slack_context_id_separates_dm_top_level_messages():
    first = SlackIncomingMessage(
        text="Di? hekimli?i d?nem ?creti ne kadar?",
        user_id="U1",
        channel_id="D1",
        ts="100.1",
    )
    second = SlackIncomingMessage(
        text="T?rk ??renciyim",
        user_id="U1",
        channel_id="D1",
        ts="101.1",
    )

    assert build_slack_context_id(first) == "slack:D1:100.1"
    assert build_slack_context_id(second) == "slack:D1:101.1"


def test_build_uploaded_document_rag_context_id_isolated_from_normal_context():
    message = SlackIncomingMessage(
        text="Bu belgeyi nereye teslim edecegim?",
        user_id="U1",
        channel_id="C1",
        ts="100.1",
        thread_ts="99.9",
    )

    assert build_uploaded_document_rag_context_id(message) == "slack:C1:99.9:uploaded-document-rag"


def test_build_slack_context_id_keeps_dm_thread_replies_in_thread_context():
    message = SlackIncomingMessage(
        text="Ba?vuru tarihleri ne peki?",
        user_id="U1",
        channel_id="D1",
        ts="101.1",
        thread_ts="100.1",
    )

    assert build_slack_context_id(message) == "slack:D1:100.1"


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
    assert "verify 20210001 <kod>" in login_reply[0]
    assert "tamamland" in verify_reply[0]


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
    assert orchestrator.last_call["context_id"] == "slack:D1:100.1"
    assert orchestrator.last_call["student_id"] == 42
    assert orchestrator.last_call["student_department"] == "Bilgisayar Muhendisligi"
    assert orchestrator.last_call["student_type"] == "domestic"
    assert orchestrator.last_call["is_authenticated"] is True


@pytest.mark.asyncio
async def test_slack_service_processes_transcript_upload_and_answers_followup():
    auth_service = _FakeAuthService()
    orchestrator = _FakeOrchestrator()
    service = SlackBotService(
        orchestrator=orchestrator,
        auth_service=auth_service,
        transcript_processor=TranscriptProcessor(),
        transcript_store=TranscriptSessionStore(),
    )
    transcript_text = (
        "Genel Not Ortalamas? 3,12\n"
        "Toplam AKTS 90\n"
        "Toplam Kredi 60\n"
        "BIL101 Programlamaya Giris 3 5 AA\n"
        "MAT101 Matematik I 4 6 FF\n"
    )

    upload_reply = await service.handle_message(
        SlackIncomingMessage(
            text="transkriptimi yukledim",
            user_id="U123",
            channel_id="D1",
            ts="100.1",
            files=(
                SlackFileAttachment(
                    name="transkript.txt",
                    mimetype="text/plain",
                    content=transcript_text.encode("utf-8"),
                ),
            ),
        )
    )
    failed_reply = await service.handle_message(
        SlackIncomingMessage(
            text="kaldigim dersler neler?",
            user_id="U123",
            channel_id="D1",
            ts="100.2",
            thread_ts="100.1",
        )
    )

    assert "Transkript" in upload_reply[0]
    assert "Toplam AKTS: 90" in upload_reply[0]
    assert "MAT101 Matematik I" in failed_reply[0]
    assert orchestrator.last_call is None


@pytest.mark.asyncio
async def test_slack_transcript_public_channel_adds_privacy_note():
    auth_service = _FakeAuthService()
    service = SlackBotService(
        orchestrator=_FakeOrchestrator(),
        auth_service=auth_service,
        transcript_processor=TranscriptProcessor(),
        transcript_store=TranscriptSessionStore(),
    )
    transcript_text = (
        "Genel Not Ortalamasi 3,12\n"
        "Toplam AKTS 90\n"
        "Toplam Kredi 60\n"
        "BIL101 Programlamaya Giris 3 5 AA\n"
    )

    upload_reply = await service.handle_message(
        SlackIncomingMessage(
            text="Mezun olmak icin kac akts gerekiyor bu belgeyi incele?",
            user_id="U123",
            channel_id="C1",
            ts="200.1",
            files=(
                SlackFileAttachment(
                    name="transkript.txt",
                    mimetype="text/plain",
                    content=transcript_text.encode("utf-8"),
                ),
            ),
        )
    )
    followup_reply = await service.handle_message(
        SlackIncomingMessage(
            text="toplam AKTS'im kac?",
            user_id="U123",
            channel_id="C1",
            ts="200.2",
            thread_ts="200.1",
        )
    )

    assert "Toplam AKTS: 90" in upload_reply[0]
    assert "kisisel veri" in upload_reply[0]
    assert "DM" in upload_reply[0]
    assert "toplam AKTS" in followup_reply[0]
    assert "90" in followup_reply[0]
    assert "kisisel veri" in followup_reply[0]


@pytest.mark.asyncio
async def test_slack_transcript_belgeye_gore_followup_stays_on_uploaded_context():
    auth_service = _FakeAuthService()
    orchestrator = _FakeOrchestrator()
    service = SlackBotService(
        orchestrator=orchestrator,
        auth_service=auth_service,
        transcript_processor=TranscriptProcessor(),
        transcript_store=TranscriptSessionStore(),
    )
    transcript_text = (
        "Ondokuz Mayis Universitesi Transkript\n"
        "Program: Bilgisayar Muhendisligi\n"
        "Toplam AKTS 90\n"
        "BIL101 Programlamaya Giris 3 5 AA\n"
    )

    await service.handle_message(
        SlackIncomingMessage(
            text="Mezun olmam icin kac akts gerekiyor bu belgeyi incele?",
            user_id="U123",
            channel_id="C1",
            ts="300.1",
            files=(
                SlackFileAttachment(
                    name="transkript.txt",
                    mimetype="text/plain",
                    content=transcript_text.encode("utf-8"),
                ),
            ),
        )
    )
    followup_reply = await service.handle_message(
        SlackIncomingMessage(
            text="Belgeye gore cevaplamadin?",
            user_id="U123",
            channel_id="C1",
            ts="300.2",
            thread_ts="300.1",
        )
    )

    assert "Toplam AKTS: 90" in followup_reply[0]
    assert "240 AKTS" in followup_reply[0]
    assert orchestrator.last_call is None


@pytest.mark.asyncio
async def test_slack_transcript_context_survives_login_verify_and_lists_courses():
    auth_service = _FakeAuthService()
    orchestrator = _FakeOrchestrator()
    service = SlackBotService(
        orchestrator=orchestrator,
        auth_service=auth_service,
        transcript_processor=TranscriptProcessor(),
        transcript_store=TranscriptSessionStore(),
    )
    transcript_text = (
        "Ondokuz Mayis Universitesi Transkript\n"
        "Program(KEA/ASI): Bilgisayar Muhendisligi\n"
        "Toplam AKTS 211\n"
        "BIL101 Programlamaya Giris 3 5 AA\n"
        "MAT101 Matematik I 4 6 BB\n"
    )

    await service.handle_message(
        SlackIncomingMessage(
            text="Mezun olmam icin kac akts gerekiyor bu belgeyi incele?",
            user_id="U123",
            channel_id="C1",
            ts="500.1",
            files=(
                SlackFileAttachment(
                    name="transkript.txt",
                    mimetype="text/plain",
                    content=transcript_text.encode("utf-8"),
                ),
            ),
        )
    )
    await service.handle_message(
        SlackIncomingMessage(text="login 20210001", user_id="U123", channel_id="C1", ts="500.2", thread_ts="500.1")
    )
    await service.handle_message(
        SlackIncomingMessage(
            text="verify 20210001 123456",
            user_id="U123",
            channel_id="C1",
            ts="500.3",
            thread_ts="500.1",
        )
    )
    course_reply = await service.handle_message(
        SlackIncomingMessage(
            text="Hangi dersleri almisim su ana kadar?",
            user_id="U123",
            channel_id="C1",
            ts="500.4",
            thread_ts="500.1",
        )
    )

    assert "BIL101 Programlamaya Giris" in course_reply[0]
    assert "MAT101 Matematik I" in course_reply[0]
    assert orchestrator.last_call is None

    grade_reply = await service.handle_message(
        SlackIncomingMessage(
            text="Kac tane AA dersim var?",
            user_id="U123",
            channel_id="C1",
            ts="500.5",
            thread_ts="500.1",
        )
    )

    assert "AA notlu 1 ders" in grade_reply[0]
    assert "BIL101 Programlamaya Giris" in grade_reply[0]
    assert orchestrator.last_call is None

    rag_reply = await service.handle_message(
        SlackIncomingMessage(
            text="Harc borcum varsa ders kaydi yapabilir miyim?",
            user_id="U123",
            channel_id="C1",
            ts="500.6",
            thread_ts="500.1",
        )
    )

    assert rag_reply == ["yanit: Harc borcum varsa ders kaydi yapabilir miyim?"]
    assert orchestrator.last_call["query"] == "Harc borcum varsa ders kaydi yapabilir miyim?"
    assert service.last_document_context_decision["target"] == "institutional_rag"

    document_fee_reply = await service.handle_message(
        SlackIncomingMessage(
            text="Bu belgeye gore harc borcum var mi?",
            user_id="U123",
            channel_id="C1",
            ts="500.7",
            thread_ts="500.1",
        )
    )

    assert "ödeme bilgisi tespit edemedim" in document_fee_reply[0]
    assert service.last_document_context_decision["target"] == "uploaded_document"


@pytest.mark.asyncio
async def test_slack_generic_document_upload_does_not_claim_transcript():
    auth_service = _FakeAuthService()
    service = SlackBotService(
        orchestrator=_FakeOrchestrator(),
        auth_service=auth_service,
        transcript_processor=TranscriptProcessor(),
        transcript_store=TranscriptSessionStore(),
    )

    upload_reply = await service.handle_message(
        SlackIncomingMessage(
            text="Bu belgeyi yorumlar misin?",
            user_id="U123",
            channel_id="D1",
            ts="400.1",
            files=(
                SlackFileAttachment(
                    name="dilekce.txt",
                    mimetype="text/plain",
                    content="Bu belge yaz okulu basvurusu icin dilekce ornegidir.".encode("utf-8"),
                ),
            ),
        )
    )

    assert "Belge okundu" in upload_reply[0] or "Belge" in upload_reply[0]
    assert "Transkript y" not in upload_reply[0]


@pytest.mark.asyncio
async def test_slack_transcript_upload_answers_initial_course_question():
    auth_service = _FakeAuthService()
    orchestrator = _FakeOrchestrator()
    service = SlackBotService(
        orchestrator=orchestrator,
        auth_service=auth_service,
        transcript_processor=TranscriptProcessor(),
        transcript_store=TranscriptSessionStore(),
    )

    reply = await service.handle_message(
        SlackIncomingMessage(
            text="Su ana kadar hangi dersleri almis bu ogrenci?",
            user_id="U123",
            channel_id="C1",
            ts="700.1",
            files=(
                SlackFileAttachment(
                    name="transkript.txt",
                    mimetype="text/plain",
                    content=(
                        "Ondokuz Mayis Universitesi Transkript\n"
                        "BIL101 Programlamaya Giris 3 5 AA\n"
                        "MAT101 Matematik I 4 6 BB\n"
                    ).encode("utf-8"),
                ),
            ),
        )
    )

    assert "BIL101 Programlamaya Giris" in reply[0]
    assert "MAT101 Matematik I" in reply[0]
    assert orchestrator.last_call is None


@pytest.mark.asyncio
async def test_slack_updates_uploaded_document_last_query_for_institutional_rag_followup():
    auth_service = _FakeAuthService()
    orchestrator = _FakeOrchestrator()
    service = SlackBotService(
        orchestrator=orchestrator,
        auth_service=auth_service,
        transcript_processor=TranscriptProcessor(),
        transcript_store=TranscriptSessionStore(),
    )

    await service.handle_message(
        SlackIncomingMessage(
            text="Bu belge nedir?",
            user_id="U123",
            channel_id="C1",
            ts="701.1",
            files=(
                SlackFileAttachment(
                    name="zorunlu-staj-formu.txt",
                    mimetype="text/plain",
                    content="Zorunlu Staj Formu\nStaja Baslama Tarihi\nSuresi(gun)\n".encode("utf-8"),
                ),
            ),
        )
    )
    await service.handle_message(
        SlackIncomingMessage(
            text="CAP basvuru tarihleri neler?",
            user_id="U123",
            channel_id="C1",
            ts="701.2",
            thread_ts="701.1",
        )
    )
    reply = await service.handle_message(
        SlackIncomingMessage(
            text="Tarihleri neler?",
            user_id="U123",
            channel_id="C1",
            ts="701.3",
            thread_ts="701.1",
        )
    )

    assert reply == ["yanit: Tarihleri neler?"]
    assert orchestrator.last_call["query"] == "Tarihleri neler?"
    assert service.last_document_context_decision["target"] == "institutional_rag"


@pytest.mark.asyncio
async def test_slack_generic_document_followup_field_question_stays_on_document():
    class _FakeLLM:
        async def generate(self, prompt, system=None, json_mode=False, **kwargs):
            assert "Baba Adi Mehmet" in prompt
            return "Belgeye g?re baba ad? Mehmet olarak g?r?n?yor."

    auth_service = _FakeAuthService()
    orchestrator = _FakeOrchestrator()
    service = SlackBotService(
        orchestrator=orchestrator,
        auth_service=auth_service,
        transcript_processor=TranscriptProcessor(llm_service=_FakeLLM()),
        transcript_store=TranscriptSessionStore(),
    )

    await service.handle_message(
        SlackIncomingMessage(
            text="Bu belgede ne goruyorsun?",
            user_id="U123",
            channel_id="D1",
            ts="600.1",
            files=(
                SlackFileAttachment(
                    name="ogrenci-belgesi.txt",
                    mimetype="text/plain",
                    content=(
                        "Ogrenci Belgesi\nAdi Soyadi Test Ogrenci\n"
                        "Baba Adi Mehmet\nBolum Bilgisayar Muhendisligi"
                    ).encode("utf-8"),
                ),
            ),
        )
    )
    reply = await service.handle_message(
        SlackIncomingMessage(text="Baba adi neymis?", user_id="U123", channel_id="D1", ts="600.2", thread_ts="600.1")
    )

    assert "Mehmet" in reply[0]
    assert orchestrator.last_call is None


@pytest.mark.asyncio
async def test_slack_generic_document_field_repair_followup_stays_on_document():
    auth_service = _FakeAuthService()
    orchestrator = _FakeOrchestrator()
    service = SlackBotService(
        orchestrator=orchestrator,
        auth_service=auth_service,
        transcript_processor=TranscriptProcessor(),
        transcript_store=TranscriptSessionStore(),
    )

    await service.handle_message(
        SlackIncomingMessage(
            text="Bu belge ne?",
            user_id="U123",
            channel_id="D1",
            ts="650.1",
            files=(
                SlackFileAttachment(
                    name="zorunlu-staj-formu.txt",
                    mimetype="text/plain",
                    content=(
                        "Zorunlu Staj Formu\n"
                        "Adi Soyadi    T.C. Kimlik No    Ogrenci No\n"
                        "E-posta Adresi    Telefon No\n"
                    ).encode("utf-8"),
                ),
            ),
        )
    )
    first_reply = await service.handle_message(
        SlackIncomingMessage(text="TC kimlik neymis?", user_id="U123", channel_id="D1", ts="650.2", thread_ts="650.1")
    )
    repair_reply = await service.handle_message(
        SlackIncomingMessage(text="tc kimlik no var ya", user_id="U123", channel_id="D1", ts="650.3", thread_ts="650.1")
    )

    assert "alani var" in first_reply[0]
    assert "alani var" in repair_reply[0]
    assert orchestrator.last_call is None
    assert service.last_document_context_decision["target"] == "uploaded_document"
    assert service.last_document_context_decision["document_intent"] == "document_field_lookup"


@pytest.mark.asyncio
async def test_slack_generic_document_upload_summary_reports_field_counts():
    service = SlackBotService(
        orchestrator=_FakeOrchestrator(),
        auth_service=_FakeAuthService(),
        transcript_processor=TranscriptProcessor(),
        transcript_store=TranscriptSessionStore(),
    )

    replies = await service.handle_message(
        SlackIncomingMessage(
            text="",
            user_id="U123",
            channel_id="D1",
            ts="651.1",
            files=(
                SlackFileAttachment(
                    name="zorunlu-staj-formu.txt",
                    mimetype="text/plain",
                    content=(
                        "Zorunlu Staj Formu\n"
                        "Adi Soyadi    T.C. Kimlik No    Ogrenci No\n"
                        "E-posta Adresi    Telefon No\n"
                    ).encode("utf-8"),
                ),
            ),
        )
    )

    assert "Belge" in replies[0]
    assert "Tespit edilen alan:" in replies[0]
    assert "etiket alan:" in replies[0]


@pytest.mark.asyncio
async def test_slack_generic_document_hybrid_question_combines_document_and_rag():
    class _FakeLLM:
        async def generate(self, prompt, system=None, json_mode=False, **kwargs):
            assert "hybrid_document_rag" in prompt
            return "Bu belge zorunlu staj formudur; ??renci, staj tarihi ve i?yeri bilgileri doldurulur."

    auth_service = _FakeAuthService()
    orchestrator = _FakeOrchestrator()
    service = SlackBotService(
        orchestrator=orchestrator,
        auth_service=auth_service,
        transcript_processor=TranscriptProcessor(llm_service=_FakeLLM()),
        transcript_store=TranscriptSessionStore(),
    )

    await service.handle_message(
        SlackIncomingMessage(
            text="Bu belge ne?",
            user_id="U123",
            channel_id="D1",
            ts="700.1",
            files=(
                SlackFileAttachment(
                    name="zorunlu-staj-formu.txt",
                    mimetype="text/plain",
                    content=(
                        "Zorunlu Staj Formu\n"
                        "Ogrenci bilgileri, staj tarihleri, isyeri bilgileri ve imza/kase alanlari bulunur."
                    ).encode("utf-8"),
                ),
            ),
        )
    )

    reply = await service.handle_message(
        SlackIncomingMessage(
            text="Bu belgeyle nasil basvuracagim?",
            user_id="U123",
            channel_id="D1",
            ts="700.2",
            thread_ts="700.1",
        )
    )

    assert "Belgeye" in reply[0]
    assert "kaynaklar" in reply[0]
    assert "zorunlu staj basvurusu" in orchestrator.last_call["query"]
    assert orchestrator.last_call["context_id"].endswith(":uploaded-document-rag")
    assert service.last_document_context_decision["target"] == "hybrid_document_rag"
    assert service.last_document_context_decision["document_intent"] == "hybrid_document_rag"


@pytest.mark.asyncio
async def test_slack_uploaded_schedule_detail_question_uses_hybrid_schedule_rag(monkeypatch):
    monkeypatch.setattr(
        transcript_service_module,
        "_extract_pdf_text",
        lambda content: (
            "Bilgisayar Muhendisligi Lisans Ders Programi Bahar\n"
            "Pazartesi 4. SINIF Bilg. Muh. Oz. Kon. II\n"
            "Sali 4. SINIF Yaz. Muh. Lab.\n"
        ),
        raising=False,
    )
    auth_service = _FakeAuthService()
    orchestrator = _FakeOrchestrator()
    service = SlackBotService(
        orchestrator=orchestrator,
        auth_service=auth_service,
        transcript_processor=TranscriptProcessor(),
        transcript_store=TranscriptSessionStore(),
    )

    await service.handle_message(
        SlackIncomingMessage(
            text="Bu belge nedir?",
            user_id="U123",
            channel_id="D1",
            ts="710.1",
            files=(
                SlackFileAttachment(
                    name="2025-26 Lisans_Ders_Programi_Bahar_Bilgisayar_Muh.pdf",
                    mimetype="application/pdf",
                    content=b"%PDF fake",
                ),
            ),
        )
    )
    reply = await service.handle_message(
        SlackIncomingMessage(
            text="4. siniflarin cuma dersi var mi bu programa gore?",
            user_id="U123",
            channel_id="D1",
            ts="710.2",
            thread_ts="710.1",
        )
    )

    assert "kaynaklar" in reply[0]
    assert "Bilgisayar Muhendisligi" in orchestrator.last_call["query"]
    assert "haftalik ders programi" in orchestrator.last_call["query"]
    assert service.last_document_context_decision["target"] == "hybrid_document_rag"


@pytest.mark.asyncio
async def test_slack_file_download_rejects_html_login_page(monkeypatch):
    class _FakeResponse:
        headers = {"content-type": "text/html; charset=utf-8"}
        content = b"<!DOCTYPE html><html>login</html>"

        def raise_for_status(self):
            return None

    class _FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def get(self, url, headers=None):
            return _FakeResponse()

    monkeypatch.setattr(slack_service_module.settings.slack, "bot_token", "xoxb-test")
    monkeypatch.setattr(slack_service_module.httpx, "AsyncClient", _FakeClient)
    service = SlackBotService(orchestrator=_FakeOrchestrator(), auth_service=_FakeAuthService())

    with pytest.raises(TranscriptProcessingError) as exc_info:
        await service._read_file_content(
            SlackFileAttachment(
                name="transkript.pdf",
                mimetype="application/pdf",
                url_private_download="https://files.slack.com/files-pri/test/download/transkript.pdf",
            )
        )

    assert "files:read" in str(exc_info.value)


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
    assert "Slack oturumunuz" in replies[0]
    assert "kapat" in replies[0]

