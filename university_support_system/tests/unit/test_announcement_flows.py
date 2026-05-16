"""End-to-end-style orchestrator tests for announcement flows."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from src.a2a import build_department_response_task
from src.agents.announcement.agent import AnnouncementAgent
from src.core.constants import ConfidenceLevel, Department, RoutingStrategy, TaskType
from src.db.announcements import AnnouncementLinkRecord, AnnouncementRecord
from src.db.conversation_context import ConversationResolution
from src.db.schemas import DepartmentResponse, IntentAnalysis, RoutingResult
from src.orchestrators.main import MainOrchestrator


def _build_announcement_record(
    *,
    title: str,
    source_url: str,
    display_summary: str,
    faculty: str | None = None,
    unit_name: str | None = None,
    links: tuple[AnnouncementLinkRecord, ...] = (),
) -> AnnouncementRecord:
    return AnnouncementRecord(
        id=1,
        title=title,
        display_summary=display_summary,
        summary=display_summary,
        original_text=display_summary,
        source_url=source_url,
        faculty=faculty,
        unit_name=unit_name,
        department="academic_programs",
        published_at=datetime(2026, 4, 17, tzinfo=UTC),
        links=links,
    )


def _announcement_routing_result(reasoning: str = "Routing LLM duyuru capability'sini secti.") -> RoutingResult:
    return RoutingResult(
        departments=[],
        confidence=0.92,
        confidence_level=ConfidenceLevel.HIGH,
        strategy=RoutingStrategy.CLARIFICATION,
        reasoning=reasoning,
        task_type=TaskType.PROCEDURE_QUERY,
        intent=IntentAnalysis(
            complexity="simple",
            is_personal=False,
            force_llm_synthesis=False,
            query_type="factual",
            reasoning=reasoning,
            primary_intent="announcement",
            target_capability="announcement",
            required_slots=[],
            missing_slots=[],
        ),
    )


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


@pytest.mark.asyncio
async def test_main_orchestrator_returns_direct_announcement_response_with_attachment_links():
    router = AsyncMock()
    router.route = AsyncMock(return_value=_announcement_routing_result("Duyuru sorgusu"))
    fetcher = AsyncMock(
        return_value=[
            _build_announcement_record(
                title="Ara Sinav Programi Duyurusu",
                source_url="https://omu.edu.tr/duyuru/ara-sinav",
                display_summary="Ara sinav programi yayimlandi.",
                faculty="Muhendislik Fakultesi",
                links=(
                    AnnouncementLinkRecord(
                        label="Program PDF",
                        url="https://omu.edu.tr/dosyalar/ara-sinav-programi.pdf",
                        link_type="attachment",
                    ),
                ),
            )
        ]
    )
    announcement_agent = AnnouncementAgent(announcement_fetcher=fetcher)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=901)
    telemetry.finalize_query_log = AsyncMock()
    telemetry.record_agent_task = AsyncMock()

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={},
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
    )

    response = await orchestrator.handle_query(
        "Güncel duyurular nelerdir?",
        context_id="ctx-ann-flow-1",
    )

    assert response.departments_involved == ["announcement"]
    assert response.generation_modes == ["vt"]
    assert "Ara Sinav Programi Duyurusu" in response.answer
    assert "Detay: https://omu.edu.tr/duyuru/ara-sinav" in response.answer
    assert response.sources[0].metadata["links"][0]["url"] == "https://omu.edu.tr/dosyalar/ara-sinav-programi.pdf"
    fetcher.assert_awaited_once_with(
        "Güncel duyurular nelerdir?",
        department=None,
        faculty=None,
        unit_name=None,
        limit=8,
        recent_days=30,
        allow_latest_fallback=True,
        probe_mode=None,
        require_keyword_match=False,
        minimum_match_score=0,
    )
    router.route.assert_awaited_once()
    telemetry.create_query_log.assert_awaited_once()


@pytest.mark.asyncio
async def test_announcement_short_circuit_quality_failure_is_not_recorded_to_conversation():
    router = AsyncMock()
    router.route = AsyncMock(return_value=_announcement_routing_result("Duyuru sorgusu"))
    fetcher = AsyncMock(
        return_value=[
            _build_announcement_record(
                title="CAP Basvuru Duyurusu",
                source_url="https://omu.edu.tr/duyuru/cap",
                display_summary="Detayli bilgi icin duyurulari takip etmeniz sorumlusanz.",
            )
        ]
    )
    announcement_agent = AnnouncementAgent(announcement_fetcher=fetcher)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=909)
    telemetry.finalize_query_log = AsyncMock()
    telemetry.record_agent_task = AsyncMock()
    conversation_service = AsyncMock()
    conversation_service.resolve_query = AsyncMock(
        return_value=ConversationResolution(
            original_query="CAP basvuru duyurusu var mi?",
            effective_query="CAP basvuru duyurusu var mi?",
            is_follow_up=False,
            used_context=False,
            active_topic=None,
            department_hints=[],
            source_hints=[],
        )
    )
    conversation_service.record_turn = AsyncMock()

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={},
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
        conversation_service=conversation_service,
    )

    response = await orchestrator.handle_query(
        "CAP basvuru duyurusu var mi?",
        context_id="ctx-ann-quality-fail",
    )

    assert "güvenilir biçimde sentezleyemiyorum" in response.answer
    conversation_service.record_turn.assert_not_awaited()
    finalize_kwargs = telemetry.finalize_query_log.await_args.kwargs
    assert finalize_kwargs["status"] == "failed"
    assert finalize_kwargs["error"] == "final_quality_gate_failed"


@pytest.mark.asyncio
async def test_main_orchestrator_records_follow_up_state_for_announcement_only_queries():
    router = AsyncMock()
    router.route = AsyncMock(return_value=_announcement_routing_result("Duyuru follow-up sorgusu"))
    fetcher = AsyncMock(
        return_value=[
            _build_announcement_record(
                title="Bilgisayar Muhendisligi Sinav Duyurusu",
                source_url="https://bil-muhendislik.omu.edu.tr/tr/haberler/sinav-duyurusu",
                display_summary="Bolum ogrencileri icin sinav duyurusu paylasildi.",
                faculty="Muhendislik Fakultesi",
                unit_name="Bilgisayar Muhendisligi",
            )
        ]
    )
    announcement_agent = AnnouncementAgent(announcement_fetcher=fetcher)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=902)
    telemetry.finalize_query_log = AsyncMock()
    telemetry.record_agent_task = AsyncMock()
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
        router=router,
        department_orchestrators={},
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
        conversation_service=conversation_service,
    )

    response = await orchestrator.handle_query(
        "Peki son duyurular neler?",
        context_id="ctx-ann-flow-followup",
    )

    assert "Bilgisayar Muhendisligi Sinav Duyurusu" in response.answer
    fetcher.assert_awaited_once_with(
        "Bilgisayar muhendisligindeki son duyurular neler?",
        department=None,
        faculty=None,
        unit_name="Bilgisayar Muhendisligi",
        limit=8,
        recent_days=30,
        allow_latest_fallback=True,
        probe_mode=None,
        require_keyword_match=False,
        minimum_match_score=0,
    )
    record_kwargs = conversation_service.record_turn.await_args.kwargs
    assert record_kwargs["resolved_query"] == "Bilgisayar muhendisligindeki son duyurular neler?"
    assert record_kwargs["is_follow_up"] is True
    assert record_kwargs["active_topic"] == "Bilgisayar Muhendisligi"
    assert record_kwargs["departments"] == ["announcement"]


@pytest.mark.asyncio
async def test_main_orchestrator_derives_announcement_topic_from_source_metadata():
    router = AsyncMock()
    router.route = AsyncMock(return_value=_announcement_routing_result())
    fetcher = AsyncMock(
        return_value=[
            _build_announcement_record(
                title="Bilgisayar Muhendisligi Duyurusu",
                source_url="https://bil-muhendislik.omu.edu.tr/tr/haberler/duyuru",
                display_summary="Bolum duyurusu paylasildi.",
                faculty="Muhendislik Fakultesi",
                unit_name="Bilgisayar Muhendisligi",
            )
        ]
    )
    announcement_agent = AnnouncementAgent(announcement_fetcher=fetcher)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=905)
    telemetry.finalize_query_log = AsyncMock()
    telemetry.record_agent_task = AsyncMock()
    conversation_service = AsyncMock()
    conversation_service.resolve_query = AsyncMock(
        return_value=ConversationResolution(
            original_query="Bilgisayar muhendisligindeki son duyurular neler?",
            effective_query="Bilgisayar muhendisligindeki son duyurular neler?",
            is_follow_up=False,
            used_context=False,
            active_topic=None,
            department_hints=[],
            source_hints=[],
        )
    )
    conversation_service.record_turn = AsyncMock()

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={},
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
        conversation_service=conversation_service,
    )

    await orchestrator.handle_query(
        "Bilgisayar muhendisligindeki son duyurular neler?",
        context_id="ctx-ann-flow-topic-derive",
    )

    record_kwargs = conversation_service.record_turn.await_args.kwargs
    assert record_kwargs["active_topic"] == "Bilgisayar Muhendisligi"


@pytest.mark.asyncio
async def test_main_orchestrator_uses_announcement_context_for_markerless_follow_up():
    router = AsyncMock()
    router.route = AsyncMock(return_value=_announcement_routing_result())
    fetcher = AsyncMock(
        return_value=[
            _build_announcement_record(
                title="Bilgisayar Muhendisligi Sinav Programi",
                source_url="https://bil-muhendislik.omu.edu.tr/tr/haberler/sinav-programi",
                display_summary="Sinav programi ve salon bilgileri paylasildi.",
                faculty="Muhendislik Fakultesi",
                unit_name="Bilgisayar Muhendisligi",
                links=(
                    AnnouncementLinkRecord(
                        label="Program PDF",
                        url="https://bil-muhendislik.omu.edu.tr/files/sinav-programi.pdf",
                        link_type="attachment",
                    ),
                ),
            )
        ]
    )
    announcement_agent = AnnouncementAgent(announcement_fetcher=fetcher)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=904)
    telemetry.finalize_query_log = AsyncMock()
    telemetry.record_agent_task = AsyncMock()
    conversation_service = AsyncMock()
    conversation_service.resolve_query = AsyncMock(
        return_value=ConversationResolution(
            original_query="Peki sinav programi ile ilgili olan var mi?",
            effective_query="sinav programi ile ilgili olan var mi?",
            is_follow_up=True,
            used_context=True,
            active_topic="Bilgisayar Muhendisligi",
            department_hints=[],
            source_hints=[],
            announcement_context=True,
        )
    )
    conversation_service.record_turn = AsyncMock()

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={},
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
        conversation_service=conversation_service,
    )

    response = await orchestrator.handle_query(
        "Peki sinav programi ile ilgili olan var mi?",
        context_id="ctx-ann-flow-followup-markerless",
    )

    assert response.departments_involved == ["announcement"]
    assert "Bilgisayar Muhendisligi Sinav Programi" in response.answer
    assert "Program PDF" in response.answer
    fetcher.assert_awaited_once_with(
        "sinav programi ile ilgili olan var mi?",
        department=None,
        faculty=None,
        unit_name=None,
        limit=8,
        recent_days=30,
        allow_latest_fallback=False,
        probe_mode=None,
        require_keyword_match=False,
        minimum_match_score=0,
    )
    router.route.assert_awaited_once()


@pytest.mark.asyncio
async def test_main_orchestrator_appends_related_announcement_links_to_specialist_answer():
    router = AsyncMock()
    router.route = AsyncMock(
        return_value=_announcement_routing_result("Akademik duyuru destekli sorgu")
    )
    academic_orchestrator = _StaticDepartmentOrchestrator(
        Department.ACADEMIC_PROGRAMS,
        "Ara sinav programlari genellikle bolum duyurularindan ilan edilir.",
    )
    fetcher = AsyncMock(
        return_value=[
            _build_announcement_record(
                title="Bilgisayar Muhendisligi Ara Sinav Programi",
                source_url="https://bil-muhendislik.omu.edu.tr/tr/haberler/ara-sinav-programi",
                display_summary="Ara sinav programi ve salon bilgileri paylasildi.",
                faculty="Muhendislik Fakultesi",
                unit_name="Bilgisayar Muhendisligi",
                links=(
                    AnnouncementLinkRecord(
                        label="Program PDF",
                        url="https://bil-muhendislik.omu.edu.tr/files/ara-sinav-programi.pdf",
                        link_type="attachment",
                    ),
                ),
            )
        ]
    )
    announcement_agent = AnnouncementAgent(announcement_fetcher=fetcher)
    telemetry = AsyncMock()
    telemetry.create_query_log = AsyncMock(return_value=903)
    telemetry.finalize_query_log = AsyncMock()
    telemetry.record_agent_task = AsyncMock()

    orchestrator = MainOrchestrator(
        router=router,
        department_orchestrators={
            Department.ACADEMIC_PROGRAMS: academic_orchestrator,
        },
        announcement_agent=announcement_agent,
        telemetry_service=telemetry,
    )

    response = await orchestrator.handle_query(
        "Bilgisayar muhendisligi ara sinav programi nereden takip edilir?",
        context_id="ctx-ann-flow-3",
    )

    assert "Bilgisayar Muhendisligi Ara Sinav Programi" in response.answer
    assert "Program PDF" in response.answer
    assert response.departments_involved == ["announcement"]
    assert any(source.metadata.get("record_type") == "announcement" for source in response.sources)
    router.route.assert_awaited_once()
