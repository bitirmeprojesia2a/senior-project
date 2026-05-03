"""Query normalization tests."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.core.config import settings
from src.orchestrators.query_normalization import normalize_query_with_llm


@pytest.mark.asyncio
async def test_query_normalization_rewrites_short_announcement_query(monkeypatch):
    monkeypatch.setattr(settings.llm, "query_normalization_enabled", True)
    llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"canonical_query":"Guncel duyurular nelerdir?",'
                '"is_personal":false,'
                '"primary_intent":"announcement",'
                '"target_capability":"announcement",'
                '"confidence":0.91,'
                '"reasoning":"duyuru sorgusu"}'
            )
        )
    )

    result = await normalize_query_with_llm(
        query="Guncel duyur",
        llm_service=llm,
        llm_profile="balanced",
    )

    assert result.canonical_query == "Guncel duyurular nelerdir?"
    assert result.is_rewritten is True
    assert result.target_capability == "announcement"
    llm.generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_query_normalization_rejects_large_topic_drift(monkeypatch):
    monkeypatch.setattr(settings.llm, "query_normalization_enabled", True)
    llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"canonical_query":"Yemek bursu basvurusu nasil yapilir?",'
                '"is_personal":false,'
                '"primary_intent":"procedure",'
                '"target_capability":"none",'
                '"confidence":0.8,'
                '"reasoning":"hatali genisletme"}'
            )
        )
    )

    result = await normalize_query_with_llm(
        query="Bahar donemi final sinavi programi",
        llm_service=llm,
    )

    assert result.canonical_query == "Bahar donemi final sinavi programi"
    assert result.is_rewritten is False


@pytest.mark.asyncio
async def test_query_normalization_preserves_grade_entry_deadline(monkeypatch):
    monkeypatch.setattr(settings.llm, "query_normalization_enabled", True)
    llm = SimpleNamespace(
        generate=AsyncMock(
            return_value=(
                '{"canonical_query":"Final sinavlari genel akademik takvime gore ne zaman?",'
                '"is_personal":false,'
                '"primary_intent":"academic_calendar",'
                '"target_capability":"none",'
                '"confidence":0.82,'
                '"reasoning":"hatali kisaltma"}'
            )
        )
    )

    result = await normalize_query_with_llm(
        query="Final sinavlarinin sisteme girilmesinin son gunu ne zaman?",
        llm_service=llm,
    )

    assert result.canonical_query == "Final sinavlarinin sisteme girilmesinin son gunu ne zaman?"
    assert result.is_rewritten is False
