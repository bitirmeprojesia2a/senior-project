"""Uctan uca sistem testleri.

MainOrchestrator → DepartmentRouter → DepartmentOrchestrator → Uzman Ajan
akisini basindan sonuna kadar test eder.

Tum harici bagimliliklar (LLM, RAG, DB) mock'lanmistir.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.agents.academic.agents import CurriculumAgent, RegulationAgent, InternationalAgent
from src.agents.announcement.agent import AnnouncementAgent
from src.agents.finance.agents import ScholarshipAgent, TuitionAgent
from src.agents.student.agents import (
    GraduationAgent,
    InternshipAgent,
    RegistrationAgent,
    StudentLifeAgent,
)
from src.core.constants import (
    ConfidenceLevel,
    Department,
    RoutingStrategy,
    TaskType,
)
from src.db.schemas import DepartmentResponse, IntentAnalysis, RoutingResult, UserQueryResponse
from src.orchestrators.department import (
    DepartmentOrchestrator,
    build_academic_programs_orchestrator,
    build_finance_orchestrator,
    build_student_affairs_orchestrator,
)
from src.orchestrators.main import MainOrchestrator


# ──────────────────────────────────────────────────────────
# Yardimci: mock'lanmis agent + orkestratorler
# ──────────────────────────────────────────────────────────

def _mock_retriever_factory():
    mock_retriever = MagicMock()
    mock_retriever.search = MagicMock(return_value=[
        {"content": "Test icerik.", "source": "test.pdf", "score": 0.9, "metadata": {}},
    ])
    mock_retriever.enrich_results = MagicMock(side_effect=lambda results, department=None: results)
    return MagicMock(return_value=mock_retriever)


def _mock_llm():
    llm = MagicMock()
    llm.generate = AsyncMock(return_value="Mock LLM yaniti.")
    llm.is_available = True
    return llm


def _base_kwargs():
    return {
        "llm_service": _mock_llm(),
        "retriever_factory": _mock_retriever_factory(),
        "contact_fetcher": AsyncMock(return_value=[]),
    }


def _build_all_agents():
    """Tum ajanlar mock bagimliliklar ile olusturulur."""
    kw = _base_kwargs

    return {
        "registration": RegistrationAgent(
            period_fetcher=AsyncMock(return_value=None), **kw(),
        ),
        "graduation": GraduationAgent(
            academic_fetcher=AsyncMock(return_value=None), **kw(),
        ),
        "internship": InternshipAgent(**kw()),
        "student_life": StudentLifeAgent(**kw()),
        "curriculum": CurriculumAgent(
            prerequisite_fetcher=AsyncMock(return_value=None),
            period_fetcher=AsyncMock(return_value=None),
            **kw(),
        ),
        "regulation": RegulationAgent(**kw()),
        "international": InternationalAgent(**kw()),
        "tuition": TuitionAgent(tuition_fetcher=AsyncMock(return_value=None), **kw()),
        "scholarship": ScholarshipAgent(
            scholarship_fetcher=AsyncMock(return_value=None),
            eligibility_fetcher=AsyncMock(return_value=[]),
            **kw(),
        ),
        "announcement": AnnouncementAgent(
            announcement_fetcher=AsyncMock(return_value=[]), **kw(),
        ),
    }


def _build_orchestrators(agents: dict):
    telemetry = AsyncMock()
    telemetry.record_agent_task = AsyncMock()

    student_affairs = build_student_affairs_orchestrator(
        agents=[agents["registration"], agents["graduation"],
                agents["internship"], agents["student_life"]],
        telemetry_service=telemetry,
    )
    academic = build_academic_programs_orchestrator(
        agents=[agents["curriculum"], agents["regulation"], agents["international"]],
        telemetry_service=telemetry,
    )
    finance = build_finance_orchestrator(
        agents=[agents["tuition"], agents["scholarship"]],
        telemetry_service=telemetry,
    )

    return {
        Department.STUDENT_AFFAIRS: student_affairs,
        Department.ACADEMIC_PROGRAMS: academic,
        Department.FINANCE: finance,
    }, telemetry


def _build_main_orchestrator(
    routing_result: RoutingResult,
    agents: dict | None = None,
):
    if agents is None:
        agents = _build_all_agents()

    dept_orchestrators, telemetry = _build_orchestrators(agents)

    router = AsyncMock()
    router.route = AsyncMock(return_value=routing_result)

    telemetry.create_query_log = AsyncMock(return_value=1)
    telemetry.finalize_query_log = AsyncMock()

    return MainOrchestrator(
        router=router,
        department_orchestrators=dept_orchestrators,
        announcement_agent=agents["announcement"],
        telemetry_service=telemetry,
    )


# ══════════════════════════════════════════════════════════
# SENARYO 1: Ogrenci Isleri DIRECT Routing
# ══════════════════════════════════════════════════════════

class TestDirectRoutingStudentAffairs:

    @pytest.mark.asyncio
    async def test_registration_query_routed_to_student_affairs(self):
        orchestrator = _build_main_orchestrator(
            RoutingResult(
                departments=[Department.STUDENT_AFFAIRS],
                confidence=0.90,
                confidence_level=ConfidenceLevel.HIGH,
                strategy=RoutingStrategy.DIRECT,
                reasoning="Kayit sorgusu",
                task_type=TaskType.REGISTRATION_QUERY,
            )
        )

        response = await orchestrator.handle_query(
            "Ders kaydi ne zaman?", context_id="e2e-1"
        )

        assert isinstance(response, UserQueryResponse)
        assert "student_affairs" in response.departments_involved
        assert response.answer is not None and len(response.answer) > 0

    @pytest.mark.asyncio
    async def test_graduation_query_with_personal_data(self):
        agents = _build_all_agents()
        agents["graduation"] = GraduationAgent(
            academic_fetcher=AsyncMock(return_value={
                "student_id": 9,
                "student_name": "Test Ogrenci",
                "gpa": 3.50,
                "completed_credits": 200,
                "total_credits": 240,
                "registration_status": "active",
                "recent_courses": [],
            }),
            **_base_kwargs(),
        )

        orchestrator = _build_main_orchestrator(
            RoutingResult(
                departments=[Department.STUDENT_AFFAIRS],
                confidence=0.85,
                confidence_level=ConfidenceLevel.HIGH,
                strategy=RoutingStrategy.DIRECT,
                reasoning="Akademik durum sorgusu",
                task_type=TaskType.ACADEMIC_QUERY,
            ),
            agents=agents,
        )

        response = await orchestrator.handle_query(
            "GNO'm kac?",
            context_id="e2e-2",
            student_id=9,
            is_authenticated=True,
        )

        assert "student_affairs" in response.departments_involved
        assert "3.50" in response.answer


# ══════════════════════════════════════════════════════════
# SENARYO 2: Finans DIRECT Routing
# ══════════════════════════════════════════════════════════

class TestDirectRoutingFinance:

    @pytest.mark.asyncio
    async def test_tuition_personal_query(self):
        agents = _build_all_agents()
        agents["tuition"] = TuitionAgent(
            tuition_fetcher=AsyncMock(return_value={
                "student_id": 7,
                "student_name": "Ahmet",
                "tuition": {
                    "semester": "2026-Bahar",
                    "total_amount": 15000.0,
                    "paid_amount": 10000.0,
                    "has_debt": True,
                    "debt_amount": 5000.0,
                    "due_date": "2026-03-31",
                    "last_payment_date": None,
                },
            }),
            **_base_kwargs(),
        )

        orchestrator = _build_main_orchestrator(
            RoutingResult(
                departments=[Department.FINANCE],
                confidence=0.92,
                confidence_level=ConfidenceLevel.HIGH,
                strategy=RoutingStrategy.DIRECT,
                reasoning="Harc sorgusu",
                task_type=TaskType.TUITION_QUERY,
            ),
            agents=agents,
        )

        response = await orchestrator.handle_query(
            "Harc borcum ne kadar?",
            context_id="e2e-fin-1",
            student_id=7,
            is_authenticated=True,
        )

        assert "finance" in response.departments_involved
        assert "5000.00 TL borc" in response.answer


# ══════════════════════════════════════════════════════════
# SENARYO 3: Akademik DIRECT Routing
# ══════════════════════════════════════════════════════════

class TestDirectRoutingAcademic:

    @pytest.mark.asyncio
    async def test_course_prerequisite_query(self):
        agents = _build_all_agents()
        agents["curriculum"] = CurriculumAgent(
            prerequisite_fetcher=AsyncMock(return_value={
                "course_code": "BIL204",
                "course_name": "Algoritmalar",
                "credits": 3,
                "akts": 6,
                "prerequisites": [
                    {"course_code": "BIL203", "course_name": "Veri Yapilari", "group": 1}
                ],
                "prerequisite_groups": {
                    1: [{"course_code": "BIL203", "course_name": "Veri Yapilari", "group": 1}]
                },
                "redirected_from": None,
            }),
            period_fetcher=AsyncMock(return_value=None),
            **_base_kwargs(),
        )

        orchestrator = _build_main_orchestrator(
            RoutingResult(
                departments=[Department.ACADEMIC_PROGRAMS],
                confidence=0.88,
                confidence_level=ConfidenceLevel.HIGH,
                strategy=RoutingStrategy.DIRECT,
                reasoning="Onkosul sorgusu",
                task_type=TaskType.COURSE_QUERY,
            ),
            agents=agents,
        )

        response = await orchestrator.handle_query(
            "BIL204 onkosulu ne?", context_id="e2e-acad-1"
        )

        assert "academic_programs" in response.departments_involved


# ══════════════════════════════════════════════════════════
# SENARYO 4: Paralel Coklu Departman Routing
# ══════════════════════════════════════════════════════════

class TestParallelRouting:

    @pytest.mark.asyncio
    async def test_parallel_student_affairs_and_finance(self):
        orchestrator = _build_main_orchestrator(
            RoutingResult(
                departments=[Department.STUDENT_AFFAIRS, Department.FINANCE],
                confidence=0.80,
                confidence_level=ConfidenceLevel.HIGH,
                strategy=RoutingStrategy.PARALLEL,
                reasoning="Coklu departman sorgusu",
                task_type=TaskType.REGISTRATION_QUERY,
            )
        )

        response = await orchestrator.handle_query(
            "Yatay gecis harc durumu nedir?", context_id="e2e-par-1"
        )

        assert len(response.departments_involved) >= 2
        assert "student_affairs" in response.departments_involved
        assert "finance" in response.departments_involved

    @pytest.mark.asyncio
    async def test_parallel_all_three_departments(self):
        orchestrator = _build_main_orchestrator(
            RoutingResult(
                departments=[
                    Department.STUDENT_AFFAIRS,
                    Department.ACADEMIC_PROGRAMS,
                    Department.FINANCE,
                ],
                confidence=0.75,
                confidence_level=ConfidenceLevel.MEDIUM,
                strategy=RoutingStrategy.PARALLEL,
                reasoning="Genis kapsamli sorgu",
                task_type=None,
            )
        )

        response = await orchestrator.handle_query(
            "Universite hakkinda genel bilgi istiyorum",
            context_id="e2e-par-2",
        )

        assert len(response.departments_involved) == 3


# ══════════════════════════════════════════════════════════
# SENARYO 5: CLARIFICATION Strategy
# ══════════════════════════════════════════════════════════

class TestClarificationRouting:

    @pytest.mark.asyncio
    async def test_low_confidence_triggers_clarification(self):
        orchestrator = _build_main_orchestrator(
            RoutingResult(
                departments=[],
                confidence=0.15,
                confidence_level=ConfidenceLevel.LOW,
                strategy=RoutingStrategy.CLARIFICATION,
                reasoning="Belirsiz sorgu",
                task_type=None,
            )
        )

        response = await orchestrator.handle_query("Merhaba", context_id="e2e-clar-1")

        assert response.answer is not None and len(response.answer) > 0
        assert response.departments_involved == []
        assert response.generation_modes == ["kural"]
        assert response.sources == []


# ══════════════════════════════════════════════════════════
# SENARYO 6: Kimlik Dogrulama Gerektiren Sorgular
# ══════════════════════════════════════════════════════════

class TestAuthenticationFlow:

    @pytest.mark.asyncio
    async def test_unauthenticated_personal_query_rejected(self):
        agents = _build_all_agents()
        agents["tuition"] = TuitionAgent(
            tuition_fetcher=AsyncMock(), **_base_kwargs(),
        )

        orchestrator = _build_main_orchestrator(
            RoutingResult(
                departments=[Department.FINANCE],
                confidence=0.90,
                confidence_level=ConfidenceLevel.HIGH,
                strategy=RoutingStrategy.DIRECT,
                reasoning="Harc sorgusu",
                task_type=TaskType.TUITION_QUERY,
            ),
            agents=agents,
        )

        response = await orchestrator.handle_query(
            "Harc borcum ne kadar?",
            context_id="e2e-auth-1",
            student_id=7,
            is_authenticated=False,
        )

        assert "kimlig" in response.answer.lower() or "dogrulam" in response.answer.lower()

    @pytest.mark.asyncio
    async def test_authenticated_personal_query_succeeds(self):
        agents = _build_all_agents()
        agents["scholarship"] = ScholarshipAgent(
            scholarship_fetcher=AsyncMock(return_value={
                "student_id": 8,
                "student_name": "Zeynep",
                "gpa": 3.60,
                "scholarship": {
                    "program_name": "Basari Bursu",
                    "monthly_amount": 1500.0,
                    "status": "active",
                    "start_date": "2025-10-01",
                    "end_date": None,
                },
                "latest_application": None,
            }),
            eligibility_fetcher=AsyncMock(return_value=[]),
            **_base_kwargs(),
        )

        orchestrator = _build_main_orchestrator(
            RoutingResult(
                departments=[Department.FINANCE],
                confidence=0.89,
                confidence_level=ConfidenceLevel.HIGH,
                strategy=RoutingStrategy.DIRECT,
                reasoning="Burs sorgusu",
                task_type=TaskType.SCHOLARSHIP_QUERY,
            ),
            agents=agents,
        )

        response = await orchestrator.handle_query(
            "Burs durumum ne?",
            context_id="e2e-auth-2",
            student_id=8,
            is_authenticated=True,
        )

        assert "Basari Bursu" in response.answer


# ══════════════════════════════════════════════════════════
# SENARYO 7: Departman Orkestratoru Keyword Routing
# ══════════════════════════════════════════════════════════

class TestDepartmentKeywordRouting:

    @pytest.mark.asyncio
    async def test_keyword_routing_selects_correct_agent(self):
        agents = _build_all_agents()
        dept_orchestrators, telemetry = _build_orchestrators(agents)

        sa_orchestrator = dept_orchestrators[Department.STUDENT_AFFAIRS]

        response = await sa_orchestrator.handle(
            query_text="Staj basvurusu nasil yapilir?",
            context_id="e2e-kw-1",
            task_type=None,
        )

        assert response.success is True
        assert response.department == Department.STUDENT_AFFAIRS

    @pytest.mark.asyncio
    async def test_finance_keyword_routing(self):
        agents = _build_all_agents()
        dept_orchestrators, telemetry = _build_orchestrators(agents)

        fin_orchestrator = dept_orchestrators[Department.FINANCE]

        response = await fin_orchestrator.handle(
            query_text="Burs basvurusu ne zaman?",
            context_id="e2e-kw-2",
            task_type=None,
        )

        assert response.success is True
        assert response.department == Department.FINANCE


# ══════════════════════════════════════════════════════════
# SENARYO 8: Duyuru Entegrasyonu
# ══════════════════════════════════════════════════════════

class TestAnnouncementIntegration:

    @pytest.mark.asyncio
    async def test_announcement_target_capability_when_no_department(self):
        orchestrator = _build_main_orchestrator(
            RoutingResult(
                departments=[],
                confidence=0.10,
                confidence_level=ConfidenceLevel.LOW,
                strategy=RoutingStrategy.CLARIFICATION,
                reasoning="Departman secilemedi",
                task_type=None,
                intent=IntentAnalysis(
                    complexity="simple",
                    is_personal=False,
                    force_llm_synthesis=False,
                    query_type="factual",
                    reasoning="duyuru aramasi",
                    primary_intent="announcement",
                    target_capability="announcement",
                    required_slots=[],
                    missing_slots=[],
                ),
            )
        )

        response = await orchestrator.handle_query(
            "Guncel duyurular neler?", context_id="e2e-ann-1"
        )

        assert response.answer is not None
        assert response.departments_involved == ["announcement"]
        assert response.generation_modes == ["vt"]
        assert "duyuru" in response.answer.lower()
