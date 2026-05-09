"""Scenario-style acceptance tests for announcement behavior."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

import src.db.announcements as announcements_module
from src.a2a import build_department_response_task
from src.agents.announcement.agent import AnnouncementAgent
from src.core.constants import ConfidenceLevel, Department, RoutingStrategy, TaskType
from src.db.conversation_context import ConversationResolution
from src.db.schemas import DepartmentResponse, IntentAnalysis, RoutingResult
from src.db.support_models import Announcement, AnnouncementLink
from src.orchestrators.main import MainOrchestrator


class _StaticDepartmentOrchestrator:
    def __init__(self, department: Department, answer: str):
        response = DepartmentResponse(
            department=department,
            answer=answer,
            sources=[],
        )

        async def _handle_task(task, *args, **kwargs):
            return build_department_response_task(
                response,
                request_task=task,
                emitter_id=f"{department.value}_orchestrator",
                emitter_name=f"{department.value} Orchestrator",
            )

        self.department = department
        self.handle_task = AsyncMock(side_effect=_handle_task)


def _patch_announcement_session(monkeypatch, db_session) -> None:
    @asynccontextmanager
    async def fake_get_session():
        yield db_session

    monkeypatch.setattr(announcements_module, "get_session", fake_get_session)


def _build_router_for_announcement_only() -> AsyncMock:
    router = AsyncMock()
    router.route = AsyncMock(
        return_value=RoutingResult(
            departments=[],
            confidence=0.95,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.CLARIFICATION,
            reasoning="Duyuru sorgusu",
            task_type=TaskType.PROCEDURE_QUERY,
            intent=IntentAnalysis(
                complexity="simple",
                is_personal=False,
                force_llm_synthesis=False,
                query_type="factual",
                reasoning="Duyuru sorgusu",
                primary_intent="announcement",
                target_capability="announcement",
                required_slots=[],
                missing_slots=[],
            ),
        )
    )
    return router


def _build_telemetry() -> AsyncMock:
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=1201)
    telemetry.finalize_query_log = AsyncMock()
    telemetry.record_agent_task = AsyncMock()
    return telemetry


@pytest.mark.asyncio
async def test_announcement_acceptance_general_query_returns_latest_items_from_db(
    db_session,
    monkeypatch,
):
    _patch_announcement_session(monkeypatch, db_session)
    db_session.add_all(
        [
            Announcement(
                title="Genel Erasmus Duyurusu",
                summary="Erasmus basvurulari acildi.",
                display_summary="Erasmus basvurulari acildi.",
                source_url="https://omu.edu.tr/duyuru/erasmus",
                published_at=datetime.now(UTC),
                is_active=True,
            ),
            Announcement(
                title="Yatay Gecis Sonuclari",
                summary="Yatay gecis sonuclari aciklandi.",
                display_summary="Yatay gecis sonuclari aciklandi.",
                source_url="https://omu.edu.tr/duyuru/yatay-gecis",
                published_at=datetime.now(UTC) - timedelta(days=1),
                is_active=True,
            ),
        ]
    )
    await db_session.flush()

    orchestrator = MainOrchestrator(
        router=_build_router_for_announcement_only(),
        department_orchestrators={},
        announcement_agent=AnnouncementAgent(),
        telemetry_service=_build_telemetry(),
    )

    response = await orchestrator.handle_query(
        "Son duyurular neler?",
        context_id="ctx-ann-accept-1",
    )

    assert response.departments_involved == ["announcement"]
    assert "Genel Erasmus Duyurusu" in response.answer
    assert "Yatay Gecis Sonuclari" in response.answer


@pytest.mark.asyncio
async def test_announcement_acceptance_general_query_is_not_scoped_by_profile_faculty(
    db_session,
    monkeypatch,
):
    _patch_announcement_session(monkeypatch, db_session)
    db_session.add_all(
        [
            Announcement(
                title="Universite Geneli Son Duyuru",
                summary="Universite geneli en guncel duyuru.",
                display_summary="Universite geneli en guncel duyuru.",
                source_url="https://omu.edu.tr/duyuru/genel-son",
                published_at=datetime.now(UTC),
                is_active=True,
            ),
            Announcement(
                title="Muhendislik Fakultesi Daha Eski Duyuru",
                summary="Muhendislik fakultesine ozel ama daha eski duyuru.",
                display_summary="Muhendislik fakultesine ozel ama daha eski duyuru.",
                source_url="https://muhendislik.omu.edu.tr/tr/haberler/eski",
                faculty="Muhendislik Fakultesi",
                department="academic_programs",
                published_at=datetime.now(UTC) - timedelta(days=10),
                is_active=True,
            ),
        ]
    )
    await db_session.flush()

    orchestrator = MainOrchestrator(
        router=_build_router_for_announcement_only(),
        department_orchestrators={},
        announcement_agent=AnnouncementAgent(),
        telemetry_service=_build_telemetry(),
    )

    response = await orchestrator.handle_query(
        "Son duyurular neler?",
        context_id="ctx-ann-accept-general-unscoped",
        student_faculty="Muhendislik Fakultesi",
        student_department="Bilgisayar Muhendisligi",
    )

    assert "Universite Geneli Son Duyuru" in response.answer


@pytest.mark.asyncio
async def test_announcement_acceptance_faculty_query_prefers_faculty_specific_items(
    db_session,
    monkeypatch,
):
    _patch_announcement_session(monkeypatch, db_session)
    db_session.add_all(
        [
            Announcement(
                title="Universite Geneli Duyuru",
                summary="Universite geneli duyuru.",
                display_summary="Universite geneli duyuru.",
                source_url="https://omu.edu.tr/duyuru/genel",
                department="academic_programs",
                published_at=datetime.now(UTC),
                is_active=True,
            ),
            Announcement(
                title="Muhendislik Fakultesi Ara Sinav Programi",
                summary="Muhendislik fakultesi icin ara sinav programi yayinlandi.",
                display_summary="Muhendislik fakultesi icin ara sinav programi yayinlandi.",
                source_url="https://muhendislik.omu.edu.tr/tr/haberler/ara-sinav",
                faculty="Muhendislik Fakultesi",
                department="academic_programs",
                published_at=datetime.now(UTC) - timedelta(hours=1),
                is_active=True,
            ),
        ]
    )
    await db_session.flush()

    orchestrator = MainOrchestrator(
        router=_build_router_for_announcement_only(),
        department_orchestrators={},
        announcement_agent=AnnouncementAgent(),
        telemetry_service=_build_telemetry(),
    )

    response = await orchestrator.handle_query(
        "Muhendislik fakultesindeki son duyurular neler?",
        context_id="ctx-ann-accept-2",
        student_faculty="Muhendislik Fakultesi",
    )

    assert "Muhendislik Fakultesi Ara Sinav Programi" in response.answer
    assert "Universite Geneli Duyuru" not in response.answer


@pytest.mark.asyncio
async def test_announcement_acceptance_follow_up_query_resolves_to_unit_scoped_items(
    db_session,
    monkeypatch,
):
    _patch_announcement_session(monkeypatch, db_session)
    db_session.add_all(
        [
            Announcement(
                title="Muhendislik Fakultesi Mezuniyet Duyurusu",
                summary="Fakulte geneli mezuniyet duyurusu.",
                display_summary="Fakulte geneli mezuniyet duyurusu.",
                source_url="https://muhendislik.omu.edu.tr/tr/haberler/mezuniyet",
                faculty="Muhendislik Fakultesi",
                department="academic_programs",
                published_at=datetime.now(UTC),
                is_active=True,
            ),
            Announcement(
                title="Bilgisayar Muhendisligi Tek Ders Sinavi",
                summary="Bilgisayar Muhendisligi icin tek ders sinav programi duyuruldu.",
                display_summary="Bilgisayar Muhendisligi icin tek ders sinav programi duyuruldu.",
                source_url="https://bil-muhendislik.omu.edu.tr/tr/haberler/tek-ders",
                faculty="Muhendislik Fakultesi",
                unit_name="Bilgisayar Muhendisligi",
                department="academic_programs",
                published_at=datetime.now(UTC) - timedelta(hours=2),
                is_active=True,
            ),
        ]
    )
    await db_session.flush()

    conversation_service = AsyncMock()
    conversation_service.resolve_query = AsyncMock(
        return_value=ConversationResolution(
            original_query="Peki son duyurular neler?",
            effective_query="Bilgisayar muhendisligindeki son duyurular neler?",
            is_follow_up=True,
            used_context=True,
            active_topic="Bilgisayar Muhendisligi",
            department_hints=[],
            source_hints=[],
        )
    )
    conversation_service.record_turn = AsyncMock()

    orchestrator = MainOrchestrator(
        router=_build_router_for_announcement_only(),
        department_orchestrators={},
        announcement_agent=AnnouncementAgent(),
        telemetry_service=_build_telemetry(),
        conversation_service=conversation_service,
    )

    response = await orchestrator.handle_query(
        "Peki son duyurular neler?",
        context_id="ctx-ann-accept-3",
    )

    assert "Bilgisayar Muhendisligi Tek Ders Sinavi" in response.answer
    assert "Muhendislik Fakultesi Mezuniyet Duyurusu" not in response.answer
    record_kwargs = conversation_service.record_turn.await_args.kwargs
    assert record_kwargs["is_follow_up"] is True
    assert record_kwargs["departments"] == ["announcement"]


@pytest.mark.asyncio
async def test_announcement_acceptance_related_announcement_keeps_attachment_link(
    db_session,
    monkeypatch,
):
    _patch_announcement_session(monkeypatch, db_session)
    announcement = Announcement(
        title="Bilgisayar Muhendisligi Ara Sinav Programi",
        summary="Bilgisayar Muhendisligi ara sinav programi aciklandi.",
        display_summary="Bilgisayar Muhendisligi ara sinav programi aciklandi.",
        source_url="https://bil-muhendislik.omu.edu.tr/tr/haberler/ara-sinav-programi",
        faculty="Muhendislik Fakultesi",
        unit_name="Bilgisayar Muhendisligi",
        department="academic_programs",
        published_at=datetime.now(UTC),
        is_active=True,
    )
    db_session.add(announcement)
    await db_session.flush()
    db_session.add(
        AnnouncementLink(
            announcement_id=announcement.id,
            label="Program PDF",
            url="https://bil-muhendislik.omu.edu.tr/files/ara-sinav-programi.pdf",
            link_type="attachment",
            sort_order=0,
        )
    )
    await db_session.flush()

    router = AsyncMock()
    router.route = AsyncMock(
        return_value=RoutingResult(
            departments=[],
            confidence=0.91,
            confidence_level=ConfidenceLevel.HIGH,
            strategy=RoutingStrategy.CLARIFICATION,
            reasoning="Bolum duyuru destekli sorgu",
            task_type=TaskType.PROCEDURE_QUERY,
            intent=IntentAnalysis(
                complexity="simple",
                is_personal=False,
                force_llm_synthesis=False,
                query_type="factual",
                reasoning="Bolum duyuru destekli sorgu",
                primary_intent="announcement",
                target_capability="announcement",
                required_slots=[],
                missing_slots=[],
            ),
        )
    )
    academic_orchestrator = _StaticDepartmentOrchestrator(
        Department.ACADEMIC_PROGRAMS,
        "Ara sinav programlari duyurular uzerinden takip edilir.",
    )

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={
            Department.ACADEMIC_PROGRAMS: academic_orchestrator,
        },
        announcement_agent=AnnouncementAgent(),
        telemetry_service=_build_telemetry(),
    )

    response = await orchestrator.handle_query(
        "Bilgisayar muhendisligi ara sinav programi nereden takip edilir?",
        context_id="ctx-ann-accept-4",
    )

    assert "Bilgisayar Muhendisligi Ara Sinav Programi" in response.answer
    assert "Program PDF" in response.answer
    assert response.departments_involved == ["announcement"]
    router.route.assert_awaited_once()
