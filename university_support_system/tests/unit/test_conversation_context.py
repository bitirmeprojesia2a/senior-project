"""Conversation context service tests."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.core.config import settings
from src.core.constants import Department, TaskType
from src.db.conversation_context import (
    ConversationContextService,
    ConversationStateData,
    ConversationTurnData,
)

pytestmark = pytest.mark.followup


def _state(
    *,
    topic: str = "CAP / Cift Anadal",
    departments: list[str] | None = None,
    task_type: str | None = TaskType.PROCEDURE_QUERY.value,
    last_query: str = "CAP basvurusu nasil yapilir?",
    last_answer: str = "Basvuru takvimini takip et.",
) -> ConversationStateData:
    return ConversationStateData(
        context_id="ctx-1",
        active_topic=topic,
        rolling_summary="Soru: CAP basvurusu nasil yapilir? | Yanit: Basvuru takvimini takip et.",
        active_entities=[topic],
        last_departments=departments or [Department.STUDENT_AFFAIRS.value, Department.ACADEMIC_PROGRAMS.value],
        last_source_refs=["cap_yonergesi.pdf", "akademik_takvim.pdf"],
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
    assert resolution.rewrite_method == "llm"
    assert resolution.effective_query == "cap basvurusu tarihleri ne zaman?"
    assert resolution.active_topic == "CAP / Cift Anadal"
    assert resolution.department_hints == [
        Department.STUDENT_AFFAIRS,
        Department.ACADEMIC_PROGRAMS,
    ]
    assert resolution.task_type_hint == TaskType.PROCEDURE_QUERY
    fake_llm.generate.assert_awaited_once()


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
    fake_llm.generate.assert_awaited_once()


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
    assert resolution.rewrite_method == "llm"
    assert resolution.effective_query == "Lisans programindan mezun olmak icin kac AKTS tamamlanmali?"
    fake_llm.generate.assert_awaited_once()


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
    assert resolution.rewrite_method == "llm"
    assert resolution.effective_query == "Lisans programindan mezun olmak icin kac AKTS tamamlanmali?"
    fake_llm.generate.assert_awaited_once()


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
