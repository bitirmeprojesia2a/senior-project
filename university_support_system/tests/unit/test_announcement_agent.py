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
    assert len(response.sources) == 2
    assert response.sources[0].metadata["record_type"] == "announcement"
    fetcher.assert_awaited_once_with(
        "Cap duyurulari neler?",
        department="academic_programs",
        faculty=None,
        unit_name=None,
        limit=8,
        allow_latest_fallback=True,
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


def test_extract_announcement_keywords_filters_generic_words():
    keywords = extract_announcement_keywords("Son CAP duyurulari ve burs duyurulari neler?")

    assert "cap" in keywords
    assert "burs" in keywords
    assert "duyurulari" not in keywords


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
        allow_latest_fallback=True,
    )
