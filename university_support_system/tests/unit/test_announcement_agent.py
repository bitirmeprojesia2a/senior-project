"""Announcement agent testleri."""

from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.agents.announcement.agent import AnnouncementAgent
from src.a2a.helpers import extract_department_response
from src.db.announcements import (
    AnnouncementLinkRecord,
    AnnouncementRecord,
    extract_announcement_keywords,
)


def _build_task(metadata: dict | None = None):
    return SimpleNamespace(
        id=f"task-{uuid4()}",
        contextId="ctx-announcement-test",
        metadata=metadata or {},
        status=SimpleNamespace(message=None),
    )


class _FakeSummaryLLM:
    def __init__(self, answer: str = "LLM tarafindan hazirlanan temiz duyuru ozeti."):
        self.answer = answer
        self.calls = []

    async def generate(self, prompt: str, system: str | None = None, **kwargs):
        self.calls.append({"prompt": prompt, "system": system, **kwargs})
        return self.answer


@pytest.mark.asyncio
async def test_announcement_agent_formats_matching_announcements():
    fetcher = AsyncMock(
        return_value=[
            AnnouncementRecord(
                id=1,
                title="Cap Basvurulari Acildi",
                display_summary="CAP basvurulari 5 Nisan'a kadar devam ediyor.",
                summary="Cap basvurulari 5 Nisan'a kadar aciktir.",
                original_text=None,
                source_url="https://omu.edu.tr/duyuru/cap",
                faculty="Muhendislik Fakultesi",
                unit_name=None,
                department="academic_programs",
                published_at=None,
                links=(
                    AnnouncementLinkRecord(
                        label="Basvuru Kilavuzu",
                        url="https://omu.edu.tr/dosyalar/cap-kilavuz.pdf",
                        link_type="attachment",
                    ),
                ),
                content_hash="abcdef1234567890",
            ),
            AnnouncementRecord(
                id=2,
                title="Yeni Ders Programi",
                display_summary=None,
                summary="Bahar donemi ders programi yayinlandi.",
                original_text=None,
                source_url=None,
                faculty=None,
                unit_name=None,
                department="academic_programs",
                published_at=None,
                links=(),
            ),
        ]
    )
    agent = AnnouncementAgent(announcement_fetcher=fetcher)

    response_task = await agent.handle_task(
        _build_task(
            {
                "query_text": "Cap duyurulari neler?",
                "department": "academic_programs",
            }
        )
    )
    response = extract_department_response(response_task)

    assert response is not None
    assert response.success is True
    assert "Cap Basvurulari Acildi" in response.answer
    assert "https://omu.edu.tr/duyuru/cap" in response.answer
    assert "CAP basvurulari 5 Nisan'a kadar devam ediyor." in response.answer
    assert "Basvuru Kilavuzu" in response.answer
    assert response.sources[0].metadata["links"][0]["url"] == "https://omu.edu.tr/dosyalar/cap-kilavuz.pdf"
    assert response.sources[0].metadata["source_ref"] == "announcement:1:abcdef123456"
    assert response.sources[0].metadata["cache_version"] == "announcement:1:abcdef123456"
    assert len(response.sources) == 2
    assert response.sources[0].metadata["record_type"] == "announcement"
    assert "numarasini ya da basligini" in response.answer
    fetcher.assert_awaited_once_with(
        "Cap duyurulari neler?",
        department="academic_programs",
        faculty=None,
        unit_name=None,
        limit=8,
        recent_days=30,
        allow_latest_fallback=False,
        probe_mode=None,
        require_keyword_match=False,
        minimum_match_score=0,
    )


@pytest.mark.asyncio
async def test_announcement_agent_returns_empty_state_when_no_announcement_found():
    fetcher = AsyncMock(return_value=[])
    agent = AnnouncementAgent(announcement_fetcher=fetcher)

    response_task = await agent.handle_task(_build_task({"query_text": "Son duyurular neler?"}))
    response = extract_department_response(response_task)

    assert response is not None
    assert response.success is True
    assert "aktif duyuru" in response.answer
    assert response.sources == []


@pytest.mark.asyncio
async def test_announcement_agent_summarizes_selected_follow_up_source_ref():
    fetcher = AsyncMock(
        return_value=[
            AnnouncementRecord(
                id=42,
                title="CAP Basvuru Duyurusu",
                display_summary=None,
                summary="CAP basvurulari icin gerekli belgeler ve basvuru takvimi duyuruda aciklanmistir.",
                original_text="Uzun duyuru metni",
                source_url="https://omu.edu.tr/duyuru/cap-basvuru",
                faculty="Muhendislik Fakultesi",
                unit_name=None,
                department="academic_programs",
                published_at=None,
                links=(),
            ),
        ]
    )
    agent = AnnouncementAgent(announcement_fetcher=fetcher)

    response_task = await agent.handle_task(
        _build_task(
            {
                "query_text": "2. duyuruyu ozetle",
                "department": "academic_programs",
                "conversation_source_refs": [
                    "Bahar Yariyili Ders Programi",
                    "CAP Basvuru Duyurusu",
                ],
            }
        )
    )
    response = extract_department_response(response_task)

    assert response is not None
    assert "Duyuru özeti: CAP Basvuru Duyurusu" in response.answer
    assert "https://omu.edu.tr/duyuru/cap-basvuru" in response.answer
    assert response.sources[0].metadata["title"] == "CAP Basvuru Duyurusu"
    fetcher.assert_awaited_once_with(
        "CAP Basvuru Duyurusu",
        department="academic_programs",
        faculty=None,
        unit_name=None,
        limit=1,
        allow_latest_fallback=False,
    )


@pytest.mark.asyncio
async def test_announcement_agent_uses_versioned_source_ref_for_summary_follow_up(monkeypatch):
    fetcher = AsyncMock(return_value=[])
    selected = AnnouncementRecord(
        id=42,
        title="CAP Basvuru Duyurusu",
        display_summary="CAP basvuru duyurusunun kisa ozeti.",
        summary="CAP basvuru duyurusunun kisa ozeti.",
        original_text="Uzun duyuru metni",
        source_url="https://omu.edu.tr/duyuru/cap-basvuru",
        faculty="Muhendislik Fakultesi",
        unit_name=None,
        department="academic_programs",
        published_at=None,
        links=(),
        content_hash="123456abcdef7890",
    )
    detail_fetcher = AsyncMock(return_value=selected)
    monkeypatch.setattr(
        "src.agents.announcement.agent.fetch_announcement_by_source_ref",
        detail_fetcher,
    )
    agent = AnnouncementAgent(announcement_fetcher=fetcher)

    response_task = await agent.handle_task(
        _build_task(
            {
                "query_text": "1. duyuruyu ozetle",
                "conversation_source_refs": ["announcement:42:123456abcdef"],
            }
        )
    )
    response = extract_department_response(response_task)

    assert response is not None
    assert "Duyuru" in response.answer
    assert response.sources[0].metadata["source_ref"] == "announcement:42:123456abcdef"
    detail_fetcher.assert_awaited_once_with("announcement:42:123456abcdef")
    fetcher.assert_not_awaited()


@pytest.mark.asyncio
async def test_announcement_agent_summarizes_title_follow_up_without_defaulting_to_first_ref():
    fetcher = AsyncMock(
        return_value=[
            AnnouncementRecord(
                id=77,
                title="CAP Basvuru Duyurusu",
                display_summary="CAP basvurulari icin duyuru ozeti.",
                summary="CAP basvurulari icin duyuru ozeti.",
                original_text="CAP basvurulari icin uzun duyuru metni.",
                source_url="https://omu.edu.tr/duyuru/cap-basvuru",
                faculty="Muhendislik Fakultesi",
                unit_name=None,
                department="academic_programs",
                published_at=None,
                links=(),
                content_hash="capref1234567890",
            ),
        ]
    )
    agent = AnnouncementAgent(announcement_fetcher=fetcher)

    response_task = await agent.handle_task(
        _build_task(
            {
                "query_text": "CAP Basvuru Duyurusunu ozetle",
                "conversation_source_refs": [
                    "announcement:12:firstref",
                    "announcement:77:capref123456",
                ],
            }
        )
    )
    response = extract_department_response(response_task)

    assert response is not None
    assert "CAP Basvuru Duyurusu" in response.answer
    assert response.sources[0].metadata["source_ref"] == "announcement:77:capref123456"
    fetcher.assert_awaited_once_with(
        "CAP Basvuru Duyurusunu ozetle",
        department=None,
        faculty=None,
        unit_name=None,
        limit=1,
        allow_latest_fallback=False,
    )


@pytest.mark.asyncio
async def test_announcement_agent_uses_llm_summary_for_long_detail_follow_up():
    long_text = " ".join(
        [
            "Bu duyuruda basvuru kosullari, takvim, belgeler ve degerlendirme sureci anlatilmaktadir."
        ]
        * 20
    )
    fetcher = AsyncMock(
        return_value=[
            AnnouncementRecord(
                id=88,
                title="Yaz Okulu Basvuru Duyurusu",
                display_summary="Eski kisa ozet.",
                summary="Eski kisa ozet.",
                original_text=long_text,
                source_url="https://omu.edu.tr/duyuru/yaz-okulu",
                faculty=None,
                unit_name=None,
                department="student_affairs",
                published_at=None,
                links=(),
                content_hash="llmref1234567890",
            ),
        ]
    )
    llm = _FakeSummaryLLM("LLM tarafindan hazirlanan yaz okulu ozeti.")
    agent = AnnouncementAgent(announcement_fetcher=fetcher, llm_service=llm)

    response_task = await agent.handle_task(
        _build_task(
            {
                "query_text": "1. duyuruyu ozetle",
                "conversation_source_refs": ["Yaz Okulu Basvuru Duyurusu"],
                "llm_profile": "fast",
            }
        )
    )
    response = extract_department_response(response_task)

    assert response is not None
    assert "LLM tarafindan hazirlanan yaz okulu ozeti." in response.answer
    assert llm.calls
    assert llm.calls[0]["model_role"] == "final_refinement"
    assert llm.calls[0]["llm_profile"] == "fast"


def test_extract_announcement_keywords_filters_generic_words():
    keywords = extract_announcement_keywords("Son CAP duyurulari ve burs duyurulari neler?")

    assert "cap" in keywords
    assert "burs" in keywords
    assert "duyurulari" not in keywords


def test_announcement_safe_bool_accepts_turkish_no():
    agent = AnnouncementAgent(announcement_fetcher=AsyncMock())

    assert agent._safe_bool("hayır", default=True) is False


@pytest.mark.asyncio
async def test_announcement_agent_uses_all_departments_when_multiple_departments_exist():
    fetcher = AsyncMock(return_value=[])
    agent = AnnouncementAgent(announcement_fetcher=fetcher)

    await agent.handle_task(
        _build_task(
            {
                "query_text": "Yatay gecis ve burs duyurulari neler?",
                "departments": ["student_affairs", "finance"],
            }
        )
    )

    fetcher.assert_awaited_once_with(
        "Yatay gecis ve burs duyurulari neler?",
        department=["student_affairs", "finance"],
        faculty=None,
        unit_name=None,
        limit=8,
        recent_days=30,
        allow_latest_fallback=True,
        probe_mode=None,
        require_keyword_match=False,
        minimum_match_score=0,
    )
