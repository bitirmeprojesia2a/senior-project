"""Conversation context service tests."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.core.config import settings
from src.core.constants import Department, TaskType
from src.core.text_normalization import normalize_text
from src.db.conversation_context import (
    ConversationContextService,
    ConversationStateData,
    ConversationTurnData,
    _filter_source_refs_for_topic,
)

pytestmark = pytest.mark.followup


def _state(
    *,
    topic: str = "CAP / Cift Anadal",
    departments: list[str] | None = None,
    task_type: str | None = TaskType.PROCEDURE_QUERY.value,
    last_query: str = "CAP basvurusu nasil yapilir?",
    last_answer: str = "Basvuru takvimini takip et.",
    source_refs: list[str] | None = None,
) -> ConversationStateData:
    return ConversationStateData(
        context_id="ctx-1",
        active_topic=topic,
        rolling_summary="Soru: CAP basvurusu nasil yapilir? | Yanit: Basvuru takvimini takip et.",
        active_entities=[topic],
        last_departments=departments or [Department.STUDENT_AFFAIRS.value, Department.ACADEMIC_PROGRAMS.value],
        last_source_refs=source_refs if source_refs is not None else ["cap_yonergesi.pdf", "akademik_takvim.pdf"],
        last_task_type=task_type,
        last_turn_id=1,
        last_user_query=last_query,
        last_resolved_query=last_query,
        last_assistant_answer=last_answer,
        turn_count=1,
        updated_at=datetime.now(timezone.utc) - timedelta(minutes=5),
    )


def _turn(
    turn_index: int,
    *,
    user_query: str,
    resolved_query: str,
    answer_summary: str,
    active_topic: str,
) -> ConversationTurnData:
    return ConversationTurnData(
        id=turn_index,
        context_id="ctx-1",
        turn_index=turn_index,
        user_query=user_query,
        resolved_query=resolved_query,
        assistant_answer=answer_summary,
        answer_summary=answer_summary,
        active_topic=active_topic,
        task_type=TaskType.PROCEDURE_QUERY.value,
        is_follow_up=turn_index > 1,
        departments=[Department.STUDENT_AFFAIRS.value, Department.ACADEMIC_PROGRAMS.value],
        source_refs=["cap_yonergesi.pdf"],
        created_at=datetime.now(timezone.utc) - timedelta(minutes=turn_index),
    )


def test_short_slot_follow_up_can_reuse_program_from_last_answer():
    state = _state(
        topic="Mufredat ve Ders Yapisi",
        departments=[Department.ACADEMIC_PROGRAMS.value],
        task_type=TaskType.COURSE_QUERY.value,
        last_query="BIL203 kac AKTS?",
        last_answer=(
            "BIL203 Veri Yapilari dersi Bilgisayar Muhendisligi mufredatinda "
            "2. sinif, 3. yariyil icinde gorunuyor."
        ),
    )

    rewritten = ConversationContextService._rewrite_with_heuristics(
        query="Peki 5. yariyildaki dersler neler?",
        state=state,
    )

    assert rewritten == "Bilgisayar Muhendisligi 5. yariyildaki dersler neler"


def test_source_hint_filter_preserves_unknown_topic_refs():
    refs = ["fakulte_duyuru_2026.pdf", "bolum_web_sayfasi.html"]

    assert _filter_source_refs_for_topic(refs, topic="Duyurular") == refs


@pytest.mark.asyncio
async def test_resolve_query_returns_original_when_no_state(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(service, "get_state", AsyncMock(return_value=None))

    resolution = await service.resolve_query(
        context_id="ctx-empty",
        query="CAP basvurusu nasil yapilir?",
    )

    assert resolution.effective_query == "CAP basvurusu nasil yapilir?"
    assert resolution.is_follow_up is False


@pytest.mark.asyncio
async def test_resolve_query_rewrites_follow_up_with_heuristics(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(service, "get_state", AsyncMock(return_value=_state()))

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Peki tarihleri ne zaman?",
        llm_service=None,
    )

    assert resolution.is_follow_up is True
    assert resolution.effective_query == "cap basvurusu tarihleri ne zaman?"
    assert Department.STUDENT_AFFAIRS in resolution.department_hints
    assert Department.ACADEMIC_PROGRAMS in resolution.department_hints


@pytest.mark.asyncio
async def test_strong_marker_topic_shift_is_not_forced_follow_up(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Harc ve Ogrenim Ucretleri",
                departments=[Department.FINANCE.value],
                task_type=TaskType.TUITION_QUERY.value,
                last_query="Harc ucreti ne kadar?",
            )
        ),
    )
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"is_follow_up": false, '
                '"standalone_query": "Staj zorunlu mu?", '
                '"active_topic": "Staj ve Uygulamali Egitim", '
                '"carry_over_departments": [], '
                '"needs_clarification": false, '
                '"clarification_message": null}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Staj zorunlu mu?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is False
    assert resolution.effective_query == "Staj zorunlu mu?"
    assert resolution.department_hints == []
    fake_llm.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_single_exam_question_does_not_inherit_summer_school_context(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Yaz Okulu",
                departments=[Department.STUDENT_AFFAIRS.value],
                last_query="Yaz okulu uzerinden cozum var mi?",
                last_answer="Yaz okulunda ders alabilme kosullari vardir.",
            )
        ),
    )
    fake_llm = SimpleNamespace(generate=AsyncMock())

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Hic almadigim bir dersten tek derse girebilir miyim?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is False
    assert resolution.effective_query == "Hic almadigim bir dersten tek derse girebilir miyim?"
    assert resolution.active_topic in {"Sinav ve Degerlendirme", "Ders Tekrari ve Devam"}
    assert resolution.active_topic != "Yaz Okulu"
    fake_llm.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_explicit_course_code_overrides_previous_course_reference(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Mufredat ve Ders Yapisi",
                departments=[Department.ACADEMIC_PROGRAMS.value],
                task_type=TaskType.COURSE_QUERY.value,
                last_query="BIL203 dersinin on kosulu var mi?",
                last_answer="BIL203 dersinin on kosulu BIL104 Programlamaya Giris II dersidir.",
            )
        ),
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="BIL104 dersinin on kosulu var mi?",
        llm_service=None,
    )

    assert resolution.effective_query == "BIL104 dersinin on kosulu var mi?"
    assert resolution.is_follow_up is False


def test_fake_numeric_fragments_are_not_course_topics():
    service = ConversationContextService()

    assert service._infer_topic("Ders kaydi icin 500 TL odedim, iade nasil yapilir?") != "icin500 dersi"
    assert service._infer_topic("14-25 Eylul 2026 yaziyor nasil bulamadin?") != "Eylul2026 dersi"
    assert service._infer_topic("Lisans icin 240 AKTS gerekir mi?") != "icin240 dersi"


@pytest.mark.asyncio
async def test_explicit_announcement_query_breaks_summer_school_context(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Yaz Okulu",
                departments=[Department.STUDENT_AFFAIRS.value, Department.ACADEMIC_PROGRAMS.value],
                task_type=TaskType.PROCEDURE_QUERY.value,
                last_query="Yaz okulunda hangi dersler acilacak?",
            )
        ),
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Bilgisayar muhendisligi duyurulari",
        llm_service=None,
    )

    assert resolution.is_follow_up is False
    assert resolution.active_topic == "Duyurular"
    assert resolution.frame is not None
    assert resolution.frame.capability == "announcement.search"
    assert resolution.frame.operation == "new_topic"


@pytest.mark.asyncio
async def test_capa_application_question_breaks_summer_school_context(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Yaz Okulu",
                departments=[Department.STUDENT_AFFAIRS.value, Department.ACADEMIC_PROGRAMS.value],
                task_type=TaskType.PROCEDURE_QUERY.value,
                last_query="Yaz okulunda hangi dersler acilacak?",
            )
        ),
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Capa basvurabilir miyim?",
        llm_service=None,
    )

    assert resolution.is_follow_up is False
    assert resolution.active_topic == "CAP / Cift Anadal"
    assert resolution.effective_query == "Capa basvurabilir miyim?"


@pytest.mark.asyncio
async def test_correction_moves_previous_eligibility_question_to_corrected_topic(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Yaz Okulu",
                departments=[Department.STUDENT_AFFAIRS.value],
                task_type=TaskType.PROCEDURE_QUERY.value,
                last_query="Yaz okulu icin basvurabilir miyim?",
            )
        ),
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Yaz okulu degil cap",
        llm_service=None,
    )

    assert resolution.is_follow_up is True
    assert resolution.rewrite_method == "correction"
    assert resolution.active_topic == "CAP / Cift Anadal"
    assert resolution.effective_query == "cap basvurusu icin basvurabilir miyim?"


@pytest.mark.asyncio
async def test_correction_does_not_carry_old_special_fee_topic(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Yaz Okulu",
                departments=[Department.FINANCE.value, Department.STUDENT_AFFAIRS.value],
                task_type=TaskType.TUITION_QUERY.value,
                last_query="Yaz okulu ucreti ne kadar?",
            )
        ),
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="CAP icin sordum",
        llm_service=None,
    )

    assert resolution.rewrite_method == "correction"
    assert resolution.active_topic == "CAP / Cift Anadal"
    assert "yaz okulu" not in normalize_text(resolution.effective_query)
    assert resolution.effective_query == "cap basvurusu ucreti veya harci var mi?"


@pytest.mark.asyncio
async def test_explanation_followup_keeps_previous_topic(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Ders Tekrari ve Devam",
                departments=[Department.STUDENT_AFFAIRS.value],
                task_type=TaskType.PROCEDURE_QUERY.value,
                last_query="Matematik dersi yuzunden okulum uzuyor ne yapabilirim?",
                last_answer="Yaz okulu veya tek ders sinavi gibi secenekler olabilir.",
            )
        ),
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Tam anlamadim daha acik anlatir misin?",
        llm_service=None,
    )

    assert resolution.is_follow_up is True
    assert resolution.active_topic == "Ders Tekrari ve Devam"
    assert resolution.rewrite_method == "clarify"
    assert resolution.effective_query == "Matematik dersi yuzunden okulum uzuyor ne yapabilirim?"
    assert resolution.frame is not None
    assert resolution.frame.operation == "clarify"
    assert resolution.frame.question_type == "explanation"


@pytest.mark.asyncio
async def test_course_property_follow_up_uses_previous_course_when_current_query_has_no_code(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Mufredat ve Ders Yapisi",
                departments=[Department.ACADEMIC_PROGRAMS.value],
                task_type=TaskType.COURSE_QUERY.value,
                last_query="Bilgisayar Muhendisliginde Veri Yapilari dersi var mi?",
                last_answer="BIL203 Veri Yapilari dersi Bilgisayar Muhendisligi mufredatinda bulunur.",
            )
        ),
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Kacinci donemde bu ders?",
        llm_service=None,
    )

    assert resolution.effective_query == "BIL203 dersi hangi yariyilda?"
    assert resolution.is_follow_up is True


@pytest.mark.asyncio
async def test_resolve_query_merges_student_type_answer_fragment_without_profile_drift(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Harc ve Ogrenim Ucretleri",
                departments=[Department.FINANCE.value],
                task_type=TaskType.TUITION_QUERY.value,
                last_query="Dis hekimligi donem ucreti ne kadar?",
            )
        ),
    )
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"is_follow_up": true, '
                '"standalone_query": "Dis hekimligi donem ucreti Turk ogrenci icin ne kadar?", '
                '"active_topic": "Harc ve Ogrenim Ucretleri", '
                '"carry_over_departments": ["finance"], '
                '"needs_clarification": false, '
                '"clarification_message": null}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Turk ogrenciyim",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.effective_query == "Dis hekimligi donem ucreti ne kadar turk ogrenci"
    assert resolution.department_hints == [Department.FINANCE]
    assert resolution.task_type_hint == TaskType.TUITION_QUERY
    fake_llm.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_query_merges_student_type_fragment_after_fee_clarification_without_department_hint(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic=None,
                departments=[],
                task_type=None,
                last_query="Fizik ogretmenligi ucreti ne kadar?",
                last_answer=(
                    "Bu bilgi ogrenci turune gore degisiyor. "
                    "Turk ogrenci misiniz, uluslararasi ogrenci misiniz?"
                ),
            )
        ),
    )
    fake_llm = SimpleNamespace(generate=AsyncMock())

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Turk ogrenciyim",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.rewrite_method == "answer_fragment"
    assert resolution.effective_query == "Fizik ogretmenligi ucreti ne kadar turk ogrenci"
    fake_llm.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_query_maps_hypothetical_fee_condition_to_active_cap_application(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(service, "get_state", AsyncMock(return_value=_state(topic="CAP / Cift Anadal")))
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"is_follow_up": true, '
                '"standalone_query": "CAP basvurusu icin harc borcum olsaydi basvurabilir miydim?", '
                '"active_topic": "Harc ve Ogrenim Ucretleri", '
                '"carry_over_departments": ["finance"], '
                '"needs_clarification": false, '
                '"clarification_message": null}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Harc borcum olsaydi basvurabilir miydim?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.rewrite_method == "llm"
    assert resolution.effective_query == "CAP basvurusu icin harc borcum olsaydi basvurabilir miydim?"
    assert resolution.active_topic == "CAP / Cift Anadal"
    assert resolution.department_hints == [
        Department.STUDENT_AFFAIRS,
        Department.ACADEMIC_PROGRAMS,
        Department.FINANCE,
    ]
    fake_llm.generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_resolve_query_rejects_conditional_fee_rewrite_that_drops_active_topic(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(service, "get_state", AsyncMock(return_value=_state(topic="CAP / Cift Anadal")))
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"is_follow_up": true, '
                '"standalone_query": "Harc borcum olsaydi basvurabilir miydim?", '
                '"active_topic": "Harc ve Ogrenim Ucretleri", '
                '"carry_over_departments": ["finance"], '
                '"needs_clarification": false, '
                '"clarification_message": null}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Harc borcum olsaydi basvurabilir miydim?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.rewrite_method == "heuristic"
    assert resolution.effective_query == "cap basvurusu icin harc borcum olsaydi basvurabilir miydim"
    assert resolution.active_topic == "CAP / Cift Anadal"
    assert resolution.department_hints == [
        Department.STUDENT_AFFAIRS,
        Department.ACADEMIC_PROGRAMS,
    ]
    fake_llm.generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_resolve_query_does_not_carry_fee_facet_to_application_date_followup(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="CAP / Cift Anadal",
                departments=[
                    Department.STUDENT_AFFAIRS.value,
                    Department.ACADEMIC_PROGRAMS.value,
                    Department.FINANCE.value,
                ],
                task_type=TaskType.PROCEDURE_QUERY.value,
                last_query="CAP basvurusu icin harc borcum olsaydi basvurabilir miydim?",
            )
        ),
    )
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"is_follow_up": true, '
                '"standalone_query": "CAP basvurusu icin harc borcum olsaydi basvuru tarihleri ne zaman?", '
                '"active_topic": "CAP / Cift Anadal", '
                '"carry_over_departments": ["student_affairs", "academic_programs", "finance"], '
                '"needs_clarification": false, '
                '"clarification_message": null}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Basvuru tarihleri ne peki?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.rewrite_method == "heuristic"
    assert resolution.effective_query == "cap basvurusu tarihleri ne zaman?"
    assert resolution.active_topic == "CAP / Cift Anadal"
    assert resolution.department_hints == [
        Department.STUDENT_AFFAIRS,
        Department.ACADEMIC_PROGRAMS,
    ]
    fake_llm.generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_resolve_query_keeps_fee_facet_when_user_asks_fee_followup(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="CAP / Cift Anadal",
                departments=[
                    Department.STUDENT_AFFAIRS.value,
                    Department.ACADEMIC_PROGRAMS.value,
                    Department.FINANCE.value,
                ],
                task_type=TaskType.PROCEDURE_QUERY.value,
                last_query="CAP basvurusu icin harc borcum olsaydi basvurabilir miydim?",
            )
        ),
    )
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"is_follow_up": true, '
                '"standalone_query": "CAP basvurusu icin harc borcu nasil odenir?", '
                '"active_topic": "CAP / Cift Anadal", '
                '"carry_over_departments": ["student_affairs", "academic_programs", "finance"], '
                '"needs_clarification": false, '
                '"clarification_message": null}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Peki harç borcu nasıl ödenir?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.rewrite_method == "llm"
    assert resolution.effective_query == "CAP basvurusu icin harc borcu nasil odenir?"
    assert Department.FINANCE in resolution.department_hints
    fake_llm.generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_resolve_query_uses_previous_question_type_for_correction_followup(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Harc ve Ogrenim Ucretleri",
                departments=[
                    Department.FINANCE.value,
                    Department.STUDENT_AFFAIRS.value,
                ],
                task_type=TaskType.TUITION_QUERY.value,
                last_query="Basvuru tarihleri ne peki?",
            )
        ),
    )
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"is_follow_up": true, '
                '"operation": "correct_previous_question", '
                '"standalone_query": "cap basvurusu tarihleri ne zaman?", '
                '"active_topic": "CAP / Cift Anadal", '
                '"carry_over_departments": ["student_affairs", "academic_programs"], '
                '"base_turn_index": null, '
                '"preserve_question_type": "date", '
                '"dropped_facets": ["finance"], '
                '"needs_clarification": false, '
                '"clarification_message": null}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="capi sordum",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.rewrite_method == "correction"
    assert resolution.effective_query == "cap basvurusu tarihleri ne zaman?"
    assert resolution.active_topic == "CAP / Cift Anadal"
    assert resolution.department_hints == [
        Department.STUDENT_AFFAIRS,
        Department.ACADEMIC_PROGRAMS,
    ]
    assert resolution.task_type_hint == TaskType.PROCEDURE_QUERY
    fake_llm.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_query_uses_correction_fallback_when_llm_unavailable(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Harc ve Ogrenim Ucretleri",
                departments=[
                    Department.FINANCE.value,
                    Department.STUDENT_AFFAIRS.value,
                ],
                task_type=TaskType.TUITION_QUERY.value,
                last_query="Basvuru tarihleri ne peki?",
            )
        ),
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="capi sordum",
        llm_service=None,
    )

    assert resolution.is_follow_up is True
    assert resolution.rewrite_method == "correction"
    assert resolution.effective_query == "cap basvurusu tarihleri ne zaman?"
    assert resolution.active_topic == "CAP / Cift Anadal"


@pytest.mark.asyncio
async def test_resolve_query_applies_schedule_term_correction_to_previous_schedule(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Ders Programi",
                departments=[Department.ACADEMIC_PROGRAMS.value],
                task_type=TaskType.COURSE_QUERY.value,
                last_query="Bilgisayar Muhendisligi 4. sinif ders programi",
                last_answer="Bilgisayar Muhendisligi icin bulunan ders programi satirlari (2025-2026 bahar):",
            )
        ),
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Ben guz donemini sormustum",
        llm_service=None,
    )

    assert resolution.is_follow_up is True
    assert resolution.rewrite_method == "correction"
    assert resolution.effective_query == "Bilgisayar Muhendisligi 4. sinif ders programi guz donemi"
    assert resolution.department_hints == [Department.ACADEMIC_PROGRAMS]
    assert resolution.task_type_hint == TaskType.COURSE_QUERY


@pytest.mark.asyncio
async def test_resolve_query_rejects_correction_like_llm_without_correction_operation(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Harc ve Ogrenim Ucretleri",
                departments=[
                    Department.FINANCE.value,
                    Department.STUDENT_AFFAIRS.value,
                ],
                task_type=TaskType.TUITION_QUERY.value,
                last_query="Basvuru tarihleri ne peki?",
            )
        ),
    )
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"is_follow_up": true, '
                '"operation": "follow_last_facet", '
                '"standalone_query": "Harc ucreti basvuru tarihleri ne zaman?", '
                '"active_topic": "Harc ve Ogrenim Ucretleri", '
                '"carry_over_departments": ["finance"], '
                '"needs_clarification": false, '
                '"clarification_message": null}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="capi soruyorum",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.rewrite_method == "correction"
    assert resolution.effective_query == "cap basvurusu tarihleri ne zaman?"
    assert resolution.active_topic == "CAP / Cift Anadal"
    assert resolution.department_hints == [
        Department.STUDENT_AFFAIRS,
        Department.ACADEMIC_PROGRAMS,
    ]
    fake_llm.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_query_falls_back_for_hypothetical_fee_condition_when_llm_unavailable(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(service, "get_state", AsyncMock(return_value=_state(topic="CAP / Cift Anadal")))

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Harc borcum olsaydi basvurabilir miydim?",
        llm_service=None,
    )

    assert resolution.is_follow_up is True
    assert resolution.rewrite_method == "heuristic"
    assert resolution.effective_query == "cap basvurusu icin harc borcum olsaydi basvurabilir miydim"


@pytest.mark.asyncio
async def test_resolve_query_merges_bare_student_type_only_in_fee_context(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Harc ve Ogrenim Ucretleri",
                departments=[Department.FINANCE.value],
                task_type=TaskType.TUITION_QUERY.value,
                last_query="Elektrik elektronik muhendisligi ogrenim ucreti ne kadar?",
            )
        ),
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Turk",
        llm_service=None,
    )

    assert resolution.is_follow_up is True
    assert resolution.effective_query == (
        "Elektrik elektronik muhendisligi ogrenim ucreti ne kadar Turk ogrenci"
    )
    assert resolution.department_hints == [Department.FINANCE]


@pytest.mark.asyncio
async def test_resolve_query_does_not_treat_student_type_as_fragment_after_payment_condition(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="CAP / Cift Anadal",
                departments=[Department.STUDENT_AFFAIRS.value, Department.FINANCE.value],
                task_type=TaskType.PAYMENT_QUERY.value,
                last_query="CAP basvurusu icin harc borcum olsaydi basvurabilir miydim?",
                last_answer="Harc borcu basvuru uygunlugunu etkileyebilir; net bilgi icin birime basvurun.",
            )
        ),
    )
    fake_llm = SimpleNamespace(generate=AsyncMock())

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Turk",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is False
    assert resolution.effective_query == "Turk"
    fake_llm.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_query_uses_program_answer_after_program_clarification(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="CAP / Cift Anadal",
                departments=[Department.STUDENT_AFFAIRS.value, Department.ACADEMIC_PROGRAMS.value],
                task_type=TaskType.PROCEDURE_QUERY.value,
                last_query="Capa basvurabilir miyim?",
                last_answer="Bu soruyu dogru cevaplayabilmem icin fakulte, bolum veya program bilgisini belirtir misiniz?",
            )
        ),
    )
    fake_llm = SimpleNamespace(generate=AsyncMock())

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Bilgisayar Muhendisligi",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.rewrite_method == "answer_fragment"
    assert resolution.effective_query == "Bilgisayar Muhendisligi icin Capa basvurabilir miyim?"
    fake_llm.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_program_answer_fragment_recovers_topic_from_previous_question(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic=None,
                departments=[Department.ACADEMIC_PROGRAMS.value],
                task_type=TaskType.PROCEDURE_QUERY.value,
                last_query="Capa basvurabilir miyim?",
                last_answer="Bu soruyu dogru cevaplayabilmem icin fakulte, bolum veya program bilgisini belirtir misiniz?",
            )
        ),
    )
    fake_llm = SimpleNamespace(generate=AsyncMock())

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Bilgisayar Muhendisligi",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.rewrite_method == "answer_fragment"
    assert resolution.effective_query == "Bilgisayar Muhendisligi icin Capa basvurabilir miyim?"
    assert resolution.active_topic == "CAP / Cift Anadal"
    assert resolution.department_hints == [
        Department.ACADEMIC_PROGRAMS,
        Department.STUDENT_AFFAIRS,
    ]
    fake_llm.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_query_uses_program_answer_after_course_list_clarification(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Mufredat ve Ders Yapisi",
                departments=[Department.ACADEMIC_PROGRAMS.value],
                task_type=TaskType.COURSE_QUERY.value,
                last_query="4. Sinif ilk donem dersleri hakkinda bilgi almak istiyorum",
                last_answer="Fakulte, bolum veya program bilgisini belirtir misiniz?",
            )
        ),
    )
    fake_llm = SimpleNamespace(generate=AsyncMock())

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Bilgisayar Muhendisligi",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.rewrite_method == "answer_fragment"
    assert resolution.effective_query == (
        "Bilgisayar Muhendisligi icin 4. Sinif ilk donem dersleri hakkinda bilgi almak istiyorum?"
    )
    fake_llm.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_explicit_cap_question_after_program_clarification_starts_new_topic(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic=None,
                departments=[Department.ACADEMIC_PROGRAMS.value],
                task_type=TaskType.COURSE_QUERY.value,
                last_query="4. Sinif ilk donem dersleri hakkinda bilgi almak istiyorum",
                last_answer="Fakulte, bolum veya program bilgisini belirtir misiniz?",
            )
        ),
    )
    fake_llm = SimpleNamespace(generate=AsyncMock())

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Capa basvurabilir miyim?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is False
    assert resolution.effective_query == "Capa basvurabilir miyim?"
    assert resolution.active_topic == "CAP / Cift Anadal"
    fake_llm.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_query_merges_program_name_as_missing_slot(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Mufredat ve Ders Yapisi",
                departments=[Department.ACADEMIC_PROGRAMS.value],
                task_type=TaskType.COURSE_QUERY.value,
                last_query="Her donem kac AKTS hakkim var?",
            )
        ),
    )
    fake_llm = SimpleNamespace(generate=AsyncMock())

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Bilgisayar muhendisligi",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.effective_query == "Bilgisayar Muhendisligi icin Her donem kac AKTS hakkim var?"
    assert resolution.department_hints == [Department.ACADEMIC_PROGRAMS]
    assert resolution.rewrite_method == "answer_fragment"
    fake_llm.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_application_type_fragment_after_date_clarification(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Harc ve Ogrenim Ucretleri",
                departments=[Department.STUDENT_AFFAIRS.value, Department.FINANCE.value],
                task_type=TaskType.PAYMENT_QUERY.value,
                last_query="Basvuru tarihleri ne peki?",
                last_answer=(
                    "Hangi basvuru turu icin tarih sordugunuzu yazar misiniz? "
                    "Ornegin yatay gecis, CAP/YAP, Erasmus, staj, yaz okulu veya kayit basvurusu gibi yazabilirsiniz."
                ),
            )
        ),
    )
    fake_llm = SimpleNamespace(generate=AsyncMock())

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Cap",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.rewrite_method == "answer_fragment"
    assert resolution.effective_query == "cap basvurusu tarihleri ne zaman?"
    assert resolution.active_topic == "CAP / Cift Anadal"
    fake_llm.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_query_uses_last_course_reference_for_prerequisite_followup(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Mufredat ve Ders Yapisi",
                departments=[Department.ACADEMIC_PROGRAMS.value],
                task_type=TaskType.COURSE_QUERY.value,
                last_query="Bilgisayar Muhendisliginde var mi peki?",
                last_answer=(
                    "BIL203 Veri Yapilari dersi Bilgisayar Muhendisligi mufredatinda "
                    "2. sinif, 3. yariyil icinde gorunuyor."
                ),
            )
        ),
    )
    fake_llm = SimpleNamespace(generate=AsyncMock())

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Onkosulu var mi?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.effective_query == "BIL203 dersinin onkosulu var mi?"
    assert resolution.task_type_hint == TaskType.COURSE_QUERY
    assert resolution.department_hints == [Department.ACADEMIC_PROGRAMS]
    fake_llm.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_query_uses_last_course_reference_for_akts_followup(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Mufredat ve Ders Yapisi",
                departments=[Department.ACADEMIC_PROGRAMS.value],
                task_type=TaskType.COURSE_QUERY.value,
                last_query="Onkosulu var mi?",
                last_answer=(
                    "BIL203 Veri Yapilari (3 kredi, 5 AKTS) dersinin onkosullari: "
                    "BIL104 Programlamaya Giris II."
                ),
            )
        ),
    )
    fake_llm = SimpleNamespace(generate=AsyncMock())

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Kac AKTS peki?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.effective_query == "BIL203 dersi kac AKTS?"
    assert resolution.task_type_hint == TaskType.COURSE_QUERY
    fake_llm.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_query_merges_course_code_after_course_slot_clarification(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Mufredat ve Ders Yapisi",
                departments=[Department.ACADEMIC_PROGRAMS.value],
                task_type=TaskType.COURSE_QUERY.value,
                last_query="Onkosulu var mi?",
                last_answer=(
                    "On kosul veya AKTS bilgisini kontrol edebilmem icin ders adini "
                    "ya da ders kodunu bolum/program bilgisiyle birlikte yazar misiniz?"
                ),
            )
        ),
    )
    fake_llm = SimpleNamespace(generate=AsyncMock())

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="BIL203 Veri Yapilari Bilgisayar Muhendisligi",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.rewrite_method == "answer_fragment"
    assert resolution.effective_query == (
        "BIL203 Veri Yapilari Bilgisayar Muhendisligi dersinin onkosulu var mi?"
    )
    fake_llm.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_query_merges_student_type_fragment_outside_fee_context(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Yaz Okulu",
                departments=[Department.STUDENT_AFFAIRS.value, Department.ACADEMIC_PROGRAMS.value],
                task_type=TaskType.PROCEDURE_QUERY.value,
                last_query="Yaz okuluna kimler katilabilir?",
            )
        ),
    )
    fake_llm = SimpleNamespace(generate=AsyncMock())

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Lisans ogrencisiyim katilabilir miyim?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.effective_query == "Yaz okuluna kimler katilabilir lisans ogrencisi icin"
    assert resolution.department_hints == [Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS]
    assert resolution.rewrite_method == "answer_fragment"
    fake_llm.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_query_does_not_pollute_staj_question_with_yaz_okulu_context(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Yaz Okulu",
                departments=[Department.STUDENT_AFFAIRS.value, Department.ACADEMIC_PROGRAMS.value],
                task_type=TaskType.PROCEDURE_QUERY.value,
                last_query="Yaz okulu ne zaman, kimler katilabilir ve sinif kapasitesi ne kadar?",
            )
        ),
    )
    fake_llm = SimpleNamespace(generate=AsyncMock())

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Staj yapmazsam mezun olabilir miyim?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is False
    assert resolution.effective_query == "Staj yapmazsam mezun olabilir miyim?"
    assert resolution.active_topic == "Staj ve Uygulamali Egitim"
    assert resolution.department_hints == []
    fake_llm.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_query_does_not_stick_confusion_to_previous_fee_topic(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Harc ve Ogrenim Ucretleri",
                departments=[Department.FINANCE.value],
                task_type=TaskType.TUITION_QUERY.value,
                last_query="Harc ucreti ne kadar?",
            )
        ),
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="hocam isler karisti",
        llm_service=None,
    )

    assert resolution.is_follow_up is False
    assert resolution.effective_query == "hocam isler karisti"
    assert resolution.department_hints == []


@pytest.mark.asyncio
async def test_resolve_query_does_not_stick_vague_application_to_fee_topic(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Harc ve Ogrenim Ucretleri",
                departments=[Department.FINANCE.value],
                task_type=TaskType.TUITION_QUERY.value,
                last_query="Harc borcum ne kadar?",
            )
        ),
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="sey basvuru ne zaman",
        llm_service=None,
    )

    assert resolution.is_follow_up is False
    assert resolution.effective_query == "sey basvuru ne zaman"
    assert resolution.department_hints == []


@pytest.mark.asyncio
async def test_resolve_query_does_not_stick_student_rights_to_registration_topic(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Kayit ve Akademik Takvim",
                departments=[Department.STUDENT_AFFAIRS.value],
                task_type=TaskType.REGISTRATION_QUERY.value,
                last_query="Ders kaydi nasil yapilir?",
            )
        ),
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Ogrencilik haklarim neler",
        llm_service=None,
    )

    assert resolution.is_follow_up is False
    assert resolution.effective_query == "Ogrencilik haklarim neler"
    assert resolution.department_hints == []


@pytest.mark.asyncio
async def test_resolve_query_treats_academic_calendar_question_as_standalone(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Harc ve Ogrenim Ucretleri",
                departments=[Department.FINANCE.value],
                task_type=TaskType.TUITION_QUERY.value,
                last_query="Dis hekimligi donem ucreti ne kadar?",
            )
        ),
    )
    fake_llm = SimpleNamespace(generate=AsyncMock())

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Final sinavlari ne zaman?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is False
    assert resolution.effective_query == "Final sinavlari ne zaman?"
    assert resolution.department_hints == []
    fake_llm.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_query_treats_exam_result_entry_deadline_as_standalone(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Duyurular",
                departments=["announcement"],
                task_type=None,
                last_query="Guncel duyurular nelerdir?",
            )
        ),
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Final sinavlarinin sisteme girilmesinin son gunu ne zaman?",
        llm_service=None,
    )

    assert resolution.is_follow_up is False
    assert resolution.effective_query == "Final sinavlarinin sisteme girilmesinin son gunu ne zaman?"
    assert resolution.department_hints == []


@pytest.mark.asyncio
async def test_resolve_query_uses_llm_when_available(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(service, "get_state", AsyncMock(return_value=_state()))
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
        return_value=(
                '{"is_follow_up": true, '
                '"standalone_query": "CAP basvurusu icin not ortalamasi kac olmali?", '
                '"active_topic": "CAP / Cift Anadal", '
                '"carry_over_departments": ["student_affairs", "academic_programs"], '
                '"needs_clarification": false, '
                '"clarification_message": null}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Peki not ortalamasi kac olmali?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.effective_query == "CAP basvurusu icin not ortalamasi kac olmali?"
    assert resolution.active_topic == "CAP / Cift Anadal"
    assert resolution.task_type_hint == TaskType.PROCEDURE_QUERY


@pytest.mark.asyncio
async def test_follow_up_filters_incompatible_cap_source_hints(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                source_refs=[
                    "on_lisans_ve_lisans_yatay_gecis_yonergesi.pdf",
                    "yonerge_onlisans_lisans_staj.pdf",
                    "cap_staj_karma_yonerge.pdf",
                    "cift_ana_dal_ikinci_lisans_ve_yan_dal_programi.pdf",
                    "yonerge_cift_anadal_yandal.pdf",
                ],
            )
        ),
    )
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"is_follow_up": true, '
                '"standalone_query": "Cift anadal programi basvurusu icin not ortalamasi kac olmali?", '
                '"active_topic": "CAP / Cift Anadal", '
                '"carry_over_departments": ["student_affairs", "academic_programs"], '
                '"needs_clarification": false, '
                '"clarification_message": null}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Peki not ortalamasi kac olmali?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.source_hints == [
        "cift_ana_dal_ikinci_lisans_ve_yan_dal_programi.pdf",
        "yonerge_cift_anadal_yandal.pdf",
    ]


@pytest.mark.asyncio
async def test_followup_llm_prompt_includes_configured_recent_turn_window(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(service, "get_state", AsyncMock(return_value=_state()))
    monkeypatch.setattr(settings.conversation, "max_recent_turns", 2)
    recent_turns = [
        _turn(
            1,
            user_query="CAP basvurusu nasil yapilir?",
            resolved_query="CAP basvurusu nasil yapilir?",
            answer_summary="CAP basvurusu akademik takvimde ilan edilir.",
            active_topic="CAP / Cift Anadal",
        ),
        _turn(
            2,
            user_query="Not ortalamasi kac olmali?",
            resolved_query="CAP basvurusu icin not ortalamasi kac olmali?",
            answer_summary="CAP icin not ortalamasi kosulu vardir.",
            active_topic="CAP / Cift Anadal",
        ),
    ]
    get_recent_turns = AsyncMock(return_value=recent_turns)
    monkeypatch.setattr(service, "_get_recent_turns", get_recent_turns)
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"is_follow_up": true, '
                '"standalone_query": "CAP basvurusu icin hangi belgeler gerekli?", '
                '"active_topic": "CAP / Cift Anadal", '
                '"carry_over_departments": ["student_affairs", "academic_programs"], '
                '"needs_clarification": false, '
                '"clarification_message": null}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Peki hangi belgeler gerekli?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    get_recent_turns.assert_awaited_once_with(context_id="ctx-1", n=2)
    prompt_payload = json.loads(fake_llm.generate.await_args.kwargs["prompt"])
    assert [turn["turn_index"] for turn in prompt_payload["recent_turns"]] == [1, 2]
    assert prompt_payload["recent_turns"][0]["active_topic"] == "CAP / Cift Anadal"
    assert resolution.effective_query == "CAP basvurusu icin hangi belgeler gerekli?"


@pytest.mark.asyncio
async def test_resolve_query_uses_llm_for_short_signal_free_follow_up(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Yatay ve Dikey Gecis",
                departments=[Department.STUDENT_AFFAIRS.value],
            )
        ),
    )
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"is_follow_up": true, '
                '"standalone_query": "Yatay gecis icin not ortalamasi kac olmali?", '
                '"active_topic": "Yatay ve Dikey Gecis", '
                '"carry_over_departments": ["student_affairs"], '
                '"needs_clarification": false, '
                '"clarification_message": null}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Not ortalamasi kac olmali?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.effective_query == "Yatay gecis icin not ortalamasi kac olmali?"
    assert resolution.active_topic == "Yatay ve Dikey Gecis"
    assert resolution.department_hints == [Department.STUDENT_AFFAIRS]


@pytest.mark.asyncio
async def test_resolve_query_uses_llm_for_ambiguous_contextual_query(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(service, "get_state", AsyncMock(return_value=_state()))
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"is_follow_up": true, '
                '"standalone_query": "CAP basvuru belgeleri elektronik ortamdan yuklenebilir mi?", '
                '"active_topic": "CAP / Cift Anadal", '
                '"carry_over_departments": ["student_affairs", "academic_programs"], '
                '"needs_clarification": false, '
                '"clarification_message": null}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Basvuru belgeleri elektronik ortamdan yuklenebilir mi?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.effective_query == "CAP basvuru belgeleri elektronik ortamdan yuklenebilir mi?"
    assert resolution.active_topic == "CAP / Cift Anadal"
    fake_llm.generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_resolve_query_keeps_ambiguous_query_direct_when_llm_unavailable(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(service, "get_state", AsyncMock(return_value=_state()))

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Basvuru belgeleri elektronik ortamdan yuklenebilir mi?",
        llm_service=None,
    )

    assert resolution.is_follow_up is False
    assert resolution.effective_query == "Basvuru belgeleri elektronik ortamdan yuklenebilir mi?"
    assert resolution.department_hints == []


@pytest.mark.asyncio
async def test_resolve_query_does_not_auto_follow_up_for_short_signal_free_query(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(service, "get_state", AsyncMock(return_value=_state()))

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Yatay gecis?",
        llm_service=None,
    )

    assert resolution.is_follow_up is False
    assert resolution.effective_query == "Yatay gecis?"
    assert resolution.department_hints == []
    assert resolution.source_hints == []


@pytest.mark.asyncio
async def test_resolve_query_does_not_allow_llm_to_override_strong_followup(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Staj ve Uygulamali Egitim",
                departments=[Department.STUDENT_AFFAIRS.value],
            )
        ),
    )
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"is_follow_up": false, '
                '"standalone_query": "Suresi ne kadar?", '
                '"active_topic": "Harc ve Ogrenim Ucretleri", '
                '"carry_over_departments": ["finance"], '
                '"needs_clarification": false, '
                '"clarification_message": null}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Suresi ne kadar?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.effective_query == "staj suresi ne kadar?"
    assert resolution.active_topic == "Staj ve Uygulamali Egitim"
    assert resolution.department_hints == [Department.STUDENT_AFFAIRS]


@pytest.mark.asyncio
async def test_resolve_query_treats_topic_changed_weak_marker_query_as_standalone(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(service, "get_state", AsyncMock(return_value=_state()))

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Erasmus programina nasil basvururum?",
        llm_service=None,
    )

    assert resolution.is_follow_up is False
    assert resolution.effective_query == "Erasmus programina nasil basvururum?"
    assert resolution.active_topic == "Erasmus ve Uluslararasi Surecler"


@pytest.mark.asyncio
async def test_resolve_query_treats_short_clear_topic_change_as_standalone(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Harc ve Ogrenim Ucretleri",
                departments=[Department.FINANCE.value],
                task_type=TaskType.TUITION_QUERY.value,
                last_query="Harc ucreti ne kadar?",
            )
        ),
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Staj nasil yapilir?",
        llm_service=None,
    )

    assert resolution.is_follow_up is False
    assert resolution.effective_query == "Staj nasil yapilir?"
    assert resolution.active_topic == "Staj ve Uygulamali Egitim"
    assert resolution.department_hints == []


@pytest.mark.asyncio
async def test_resolve_query_treats_explicit_topic_change_as_standalone(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(return_value=_state(topic="CAP / Cift Anadal")),
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Tek ders sinavina nasil basvurabilirim?",
        llm_service=None,
    )

    assert resolution.is_follow_up is False
    assert resolution.effective_query == "Tek ders sinavina nasil basvurabilirim?"
    assert resolution.active_topic == "Sinav ve Degerlendirme"


@pytest.mark.asyncio
async def test_resolve_query_keeps_short_real_followup_after_weak_marker_tightening(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Kayit Dondurma ve Silme",
                departments=[Department.STUDENT_AFFAIRS.value],
                last_query="Kayit dondurma nasil yapilir?",
            )
        ),
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Ucreti nedir?",
        llm_service=None,
    )

    assert resolution.is_follow_up is True
    assert resolution.effective_query == "kayit dondurma icin ucreti nedir"
    assert resolution.active_topic == "Kayit Dondurma ve Silme"


@pytest.mark.asyncio
async def test_resolve_query_treats_bu_sinav_as_topic_change_when_active_topic_is_not_exam(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(return_value=_state(topic="CAP / Cift Anadal")),
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Bu sinav yazin mi oluyor?",
        llm_service=None,
    )

    assert resolution.is_follow_up is False
    assert resolution.active_topic == "Sinav ve Degerlendirme"


@pytest.mark.asyncio
async def test_answer_fragment_does_not_use_tuition_context_from_answer_only(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Sinav ve Degerlendirme",
                departments=[Department.STUDENT_AFFAIRS.value],
                task_type=TaskType.TUITION_QUERY.value,
                last_query="Tek ders sinavina nasil basvurabilirim?",
            )
        ),
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Turk ogrenciyim",
        llm_service=None,
    )

    assert resolution.is_follow_up is False
    assert resolution.rewrite_method == "none"
    assert resolution.effective_query == "Turk ogrenciyim"


@pytest.mark.asyncio
async def test_resolve_query_maps_bu_deger_lisans_to_previous_akts_context(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Mufredat ve Ders Yapisi",
                departments=[Department.STUDENT_AFFAIRS.value],
                task_type=TaskType.ACADEMIC_QUERY.value,
                last_query="Onlisans ogrencisiyim mezun olmam icin kac akts tamamlamaliyim?",
            )
        ),
    )
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"is_follow_up": true, '
                '"standalone_query": "Lisans programindan mezun olmak icin kac AKTS tamamlanmali?", '
                '"active_topic": "Mufredat ve Ders Yapisi", '
                '"carry_over_departments": ["student_affairs"], '
                '"needs_clarification": false, '
                '"clarification_message": null}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Bu deger lisans icin kac?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.rewrite_method == "heuristic"
    assert resolution.effective_query == "Normal lisans programindan mezun olmak icin toplam kac AKTS tamamlamaliyim?"
    fake_llm.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_query_maps_short_lisans_metric_fragment_to_previous_akts_context(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Mufredat ve Ders Yapisi",
                departments=[Department.STUDENT_AFFAIRS.value],
                task_type=TaskType.ACADEMIC_QUERY.value,
                last_query="Onlisans programindan mezun olmak icin kac AKTS tamamlanmali?",
            )
        ),
    )
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"is_follow_up": true, '
                '"standalone_query": "Lisans programindan mezun olmak icin kac AKTS tamamlanmali?", '
                '"active_topic": "Mufredat ve Ders Yapisi", '
                '"carry_over_departments": ["student_affairs"], '
                '"needs_clarification": false, '
                '"clarification_message": null}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Lisans icin kac?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.rewrite_method == "heuristic"
    assert resolution.effective_query == "Normal lisans programindan mezun olmak icin toplam kac AKTS tamamlamaliyim?"
    fake_llm.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_query_carries_last_explicit_program_for_short_schedule_slot(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Harc ve Ogrenim Ucretleri",
                departments=[Department.FINANCE.value],
                task_type=TaskType.TUITION_QUERY.value,
                last_query="Fizik ogretmenligi ucreti uluslararasi ogrenci icin ne kadar?",
            )
        ),
    )
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"is_follow_up": true, '
                '"standalone_query": "Fizik ogretmenligi ders programi ne?", '
                '"active_topic": "Mufredat ve Ders Yapisi", '
                '"carry_over_departments": ["academic_programs"], '
                '"needs_clarification": false, '
                '"clarification_message": null}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Ders programi ne?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.rewrite_method == "llm"
    assert resolution.effective_query == "Fizik ogretmenligi ders programi ne?"
    assert resolution.department_hints == [Department.ACADEMIC_PROGRAMS]


@pytest.mark.asyncio
async def test_resolve_query_keeps_graduation_akts_for_short_bachelor_followup(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Mezuniyet ve Akademik Durum",
                departments=[Department.STUDENT_AFFAIRS.value],
                task_type=TaskType.PROCEDURE_QUERY.value,
                last_query="Onlisans programindan mezun olmak icin kac AKTS tamamlamaliyim?",
                last_answer="On lisans programindan mezun olmak icin toplam 120 AKTS tamamlanmalidir.",
            )
        ),
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Lisans icin kac peki?",
    )

    assert resolution.is_follow_up is True
    assert resolution.policy_facet == "graduation_akts"
    assert resolution.question_type == "graduation_akts"
    assert resolution.department_hints == [Department.STUDENT_AFFAIRS]
    assert "toplam kac AKTS" in resolution.effective_query


@pytest.mark.asyncio
async def test_resolve_query_keeps_program_graduation_total_not_semester_load(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Mezuniyet ve Akademik Durum",
                departments=[Department.STUDENT_AFFAIRS.value],
                task_type=TaskType.PROCEDURE_QUERY.value,
                last_query="Normal lisans programindan mezun olmak icin toplam kac AKTS tamamlamaliyim?",
                last_answer="Normal dort yillik lisans programindan mezun olmak icin toplam 240 AKTS tamamlanmalidir.",
            )
        ),
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Bilgisayar Muhendisligi icin kac?",
    )

    assert resolution.is_follow_up is True
    assert resolution.policy_facet == "graduation_akts"
    assert "Bilgisayar Muhendisligi" in resolution.effective_query
    assert "toplam kac AKTS" in resolution.effective_query


@pytest.mark.asyncio
async def test_resolve_query_keeps_numeric_graduation_confirmation_on_previous_program(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Mezuniyet ve Akademik Durum",
                departments=[Department.STUDENT_AFFAIRS.value, Department.ACADEMIC_PROGRAMS.value],
                task_type=TaskType.PROCEDURE_QUERY.value,
                last_query="Dis hekimligi programindan mezun olmak icin toplam kac AKTS tamamlamaliyim?",
                last_answer=(
                    "Bu program tipi icin mezuniyet AKTS yukumlulugu program turune gore "
                    "degisebilir; elimde dogrulanmis toplam AKTS kosulu yok."
                ),
            )
        ),
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="240 degil mi?",
    )

    assert resolution.is_follow_up is True
    assert resolution.policy_facet == "graduation_akts"
    assert resolution.department_hints == [Department.STUDENT_AFFAIRS]
    assert "Dis Hekimligi" in resolution.effective_query
    assert "AKTS 240 mi" in resolution.effective_query


@pytest.mark.asyncio
async def test_resolve_query_carries_program_for_semester_program_followup(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Mufredat ve Ders Yapisi",
                departments=[Department.ACADEMIC_PROGRAMS.value],
                task_type=TaskType.COURSE_QUERY.value,
                last_query="Bilgisayar Muhendisligi 4. sinif ilk donem ders programi nelerdir?",
            )
        ),
    )
    fake_llm = SimpleNamespace(generate=AsyncMock())

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="peki 8. yariyil programi ne",
        llm_service=None,
    )

    assert resolution.is_follow_up is True
    assert resolution.rewrite_method == "heuristic"
    assert resolution.effective_query == "Bilgisayar Muhendisligi 8. yariyil programi ne"
    assert resolution.department_hints == [Department.ACADEMIC_PROGRAMS]
    fake_llm.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_query_replaces_previous_program_for_program_change_followup(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Mufredat ve Ders Yapisi",
                departments=[Department.ACADEMIC_PROGRAMS.value],
                task_type=TaskType.COURSE_QUERY.value,
                last_query="Bilgisayar Muhendisligi 5. yariyildaki dersler neler?",
                last_answer="5. yariyil doneminde kayitli dersler bulundu.",
            )
        ),
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Elektrik elektronik muhendisligi icin nasil?",
        llm_service=None,
    )

    assert resolution.is_follow_up is True
    assert resolution.rewrite_method == "answer_fragment"
    assert resolution.effective_query == "elektrik-elektronik muhendisligi 5. yariyildaki dersler neler?"
    assert "bilgisayar" not in resolution.effective_query
    assert resolution.department_hints == [Department.ACADEMIC_PROGRAMS]


@pytest.mark.asyncio
async def test_resolve_query_ignores_state_from_previous_build(monkeypatch):
    service = ConversationContextService()
    stale_state = _state(
        topic="Staj ve Uygulamali Egitim",
        departments=[Department.STUDENT_AFFAIRS.value],
        last_query="Staj yapmazsam mezun olabilir miyim?",
    )
    monkeypatch.setattr(service, "get_state", AsyncMock(return_value=stale_state))
    monkeypatch.setattr(settings.conversation, "reset_on_build", True)
    monkeypatch.setattr(settings.server, "build_timestamp", datetime.now(timezone.utc).isoformat())

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="CAP'a basvurabilir miyim?",
        llm_service=None,
    )

    assert resolution.is_follow_up is False
    assert resolution.effective_query == "CAP'a basvurabilir miyim?"
    assert resolution.active_topic is None
    assert resolution.department_hints == []


@pytest.mark.asyncio
async def test_resolve_query_keeps_state_when_build_timestamp_unknown(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(service, "get_state", AsyncMock(return_value=_state()))
    monkeypatch.setattr(settings.conversation, "reset_on_build", True)
    monkeypatch.setattr(settings.server, "build_timestamp", "unknown")

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Not ortalamasi kac olmali?",
        llm_service=None,
    )

    assert resolution.is_follow_up is True
    assert resolution.active_topic == "CAP / Cift Anadal"


@pytest.mark.asyncio
async def test_resolve_query_rejects_llm_rewrite_that_drops_needed_context(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Yatay ve Dikey Gecis",
                departments=[Department.STUDENT_AFFAIRS.value],
            )
        ),
    )
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"is_follow_up": true, '
                '"standalone_query": "Kontenjan var mi?", '
                '"active_topic": "Mezuniyet ve Akademik Durum", '
                '"carry_over_departments": ["academic_programs"], '
                '"needs_clarification": false, '
                '"clarification_message": null}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Peki kontenjan var mi?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.effective_query == "yatay gecis icin kontenjan var mi"
    assert resolution.active_topic == "Yatay ve Dikey Gecis"
    assert resolution.department_hints == [Department.STUDENT_AFFAIRS]


@pytest.mark.asyncio
async def test_resolve_query_rejects_llm_rewrite_that_changes_question_type(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Kayit Dondurma ve Silme",
                departments=[Department.STUDENT_AFFAIRS.value],
            )
        ),
    )
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"is_follow_up": true, '
                '"standalone_query": "Kayit dondurma nasil yapilir ve ne zaman?", '
                '"active_topic": "Kayit Dondurma ve Silme", '
                '"carry_over_departments": ["student_affairs"], '
                '"needs_clarification": false, '
                '"clarification_message": null}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Ne zaman yapilir?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.effective_query == "kayit dondurma ne zaman yapilir?"
    assert resolution.active_topic == "Kayit Dondurma ve Silme"


@pytest.mark.asyncio
async def test_resolve_query_rejects_llm_rewrite_with_wrong_short_query_context(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Yatay ve Dikey Gecis",
                departments=[Department.STUDENT_AFFAIRS.value],
            )
        ),
    )
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"is_follow_up": true, '
                '"standalone_query": "Kayit dondurma not ortalamasi kac olmali?", '
                '"active_topic": "Yatay ve Dikey Gecis", '
                '"carry_over_departments": ["student_affairs"], '
                '"needs_clarification": false, '
                '"clarification_message": null}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Not ortalamasi kac olmali?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.effective_query == "yatay gecis icin not ortalamasi kac olmali"
    assert resolution.active_topic == "Yatay ve Dikey Gecis"
    assert resolution.department_hints == [Department.STUDENT_AFFAIRS]


@pytest.mark.asyncio
async def test_resolve_query_rejects_llm_rewrite_that_changes_intent(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(service, "get_state", AsyncMock(return_value=_state()))
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"is_follow_up": true, '
                '"standalone_query": "Burs basvurusu ne zaman?", '
                '"active_topic": "Burs ve Destekler", '
                '"carry_over_departments": ["finance"], '
                '"needs_clarification": false, '
                '"clarification_message": null}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Peki not ortalamasi kac olmali?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.effective_query == "cap basvurusu icin not ortalamasi kac olmali"
    assert resolution.active_topic == "CAP / Cift Anadal"
    assert resolution.department_hints == [
        Department.STUDENT_AFFAIRS,
        Department.ACADEMIC_PROGRAMS,
    ]


@pytest.mark.asyncio
async def test_resolve_query_ignores_llm_clarification_when_heuristic_can_rewrite(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Harc ve Ogrenim Ucretleri",
                departments=[Department.FINANCE.value],
            )
        ),
    )
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"is_follow_up": true, '
                '"standalone_query": "Harc ucretini taksitle odeyebilir miyim?", '
                '"active_topic": "Harc ve Ogrenim Ucretleri", '
                '"carry_over_departments": ["finance"], '
                '"needs_clarification": true, '
                '"clarification_message": "Sorunuzdan kacinacaginiz bilgileri giriniz."}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Taksitle odeyebilir miyim?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.effective_query == "Harc ucretini taksitle odeyebilir miyim?"
    assert resolution.department_hints == [Department.FINANCE]
    assert resolution.clarification_message is None


@pytest.mark.asyncio
async def test_resolve_query_rejects_pronoun_rewrite_that_injects_previous_detail(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(service, "get_state", AsyncMock(return_value=_state()))
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"is_follow_up": true, '
                '"standalone_query": "CAP basvuru not ortalamasi icin hangi belge gerekli?", '
                '"active_topic": "CAP / Cift Anadal", '
                '"carry_over_departments": ["student_affairs", "academic_programs"], '
                '"needs_clarification": false, '
                '"clarification_message": null}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Bunun icin hangi belge gerekli?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.effective_query == "cap basvurusu icin hangi belge gerekli"
    assert resolution.active_topic == "CAP / Cift Anadal"


@pytest.mark.asyncio
async def test_resolve_query_rejects_short_followup_rewrite_with_object_drift(monkeypatch):
    service = ConversationContextService()
    monkeypatch.setattr(
        service,
        "get_state",
        AsyncMock(
            return_value=_state(
                topic="Staj ve Uygulamali Egitim",
                departments=[Department.STUDENT_AFFAIRS.value],
            )
        ),
    )
    fake_llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"is_follow_up": true, '
                '"standalone_query": "Staj basvurusu suresine ne kadar zaman var?", '
                '"active_topic": "Staj ve Uygulamali Egitim", '
                '"carry_over_departments": ["student_affairs"], '
                '"needs_clarification": false, '
                '"clarification_message": null}'
            )
        )
    )

    resolution = await service.resolve_query(
        context_id="ctx-1",
        query="Suresi ne kadar?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.effective_query == "staj suresi ne kadar?"
    assert resolution.active_topic == "Staj ve Uygulamali Egitim"
