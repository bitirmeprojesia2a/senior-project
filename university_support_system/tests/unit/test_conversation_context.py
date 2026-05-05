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
        last_assistant_answer="Basvuru takvimini takip et.",
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
    assert resolution.effective_query == "Dis hekimligi donem ucreti ne kadar Turk ogrenciyim"
    assert resolution.department_hints == [Department.FINANCE]
    assert resolution.task_type_hint == TaskType.TUITION_QUERY
    fake_llm.generate.assert_not_awaited()


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
        "Elektrik elektronik muhendisligi ogrenim ucreti ne kadar Turk"
    )
    assert resolution.department_hints == [Department.FINANCE]


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
