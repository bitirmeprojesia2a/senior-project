"""Conversation context service tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.core.constants import Department, TaskType
from src.db.conversation_context import (
    ConversationContextService,
    ConversationStateData,
)


def _state(
    *,
    topic: str = "CAP / Cift Anadal",
    departments: list[str] | None = None,
    task_type: str | None = TaskType.PROCEDURE_QUERY.value,
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
        last_user_query="CAP basvurusu nasil yapilir?",
        last_resolved_query="CAP basvurusu nasil yapilir?",
        last_assistant_answer="Basvuru takvimini takip et.",
        turn_count=1,
        updated_at=datetime.now(timezone.utc) - timedelta(minutes=5),
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
    assert "CAP / Cift Anadal hakkinda" in resolution.effective_query
    assert Department.STUDENT_AFFAIRS in resolution.department_hints
    assert Department.ACADEMIC_PROGRAMS in resolution.department_hints


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
        query="Not ortalamasi kac olmali?",
        llm_service=fake_llm,
        llm_profile="balanced",
    )

    assert resolution.is_follow_up is True
    assert resolution.effective_query == "CAP basvurusu icin not ortalamasi kac olmali?"
    assert resolution.active_topic == "CAP / Cift Anadal"
    assert resolution.task_type_hint == TaskType.PROCEDURE_QUERY
