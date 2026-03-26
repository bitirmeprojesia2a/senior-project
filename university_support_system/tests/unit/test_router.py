"""Router unit testleri."""

from unittest.mock import AsyncMock

import pytest

from src.core.constants import ConfidenceLevel, Department, RoutingStrategy, TaskType
from src.llm.llm_service import LLMServiceError
from src.routing.router import DepartmentRouter


class TestDepartmentRouter:
    """DepartmentRouter davranış testleri."""

    @pytest.mark.asyncio
    async def test_route_uses_rule_based_direct_when_query_is_clear(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Harç ödeme dekontumu nasıl alırım?")

        assert result.departments == [Department.FINANCE]
        assert result.strategy == RoutingStrategy.DIRECT
        assert result.confidence_level in (ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH)
        assert result.task_type == TaskType.TUITION_QUERY
        llm_service.generate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_route_uses_llm_when_rule_based_result_is_ambiguous(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(
            return_value='{"departments":["student_affairs","academic_programs"],"confidence":0.82,"reasoning":"CAP sureci ve kosullari iki departmani da ilgilendiriyor."}'
        )
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("ÇAP başvurusu ve müfredat koşulları nelerdir?")

        assert result.departments == [Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS]
        assert result.strategy == RoutingStrategy.PARALLEL
        assert result.confidence == 0.82
        assert result.confidence_level == ConfidenceLevel.HIGH
        llm_service.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_route_falls_back_to_rule_based_decision_when_llm_fails(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(side_effect=LLMServiceError("LLM unavailable"))
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("ÇAP başvurusu ve müfredat koşulları nelerdir?")

        assert result.departments == [Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS]
        assert result.strategy == RoutingStrategy.PARALLEL
        assert result.task_type == TaskType.COURSE_QUERY

    @pytest.mark.asyncio
    async def test_route_returns_clarification_when_no_signal_and_llm_invalid(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(return_value='{"departments":["unknown"],"confidence":0.2}')
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Merhaba, bir konuda yardım istiyorum.")

        assert result.departments == []
        assert result.strategy == RoutingStrategy.CLARIFICATION
        assert result.confidence_level == ConfidenceLevel.LOW
        assert result.task_type is None

    def test_score_departments_matches_known_keywords(self):
        router = DepartmentRouter(llm_service=AsyncMock())
        scores = router._score_departments("Müfredat, AKTS ve bölüm kuralları nerede?")

        assert scores[Department.ACADEMIC_PROGRAMS] > 0
        assert scores[Department.ACADEMIC_PROGRAMS] >= scores[Department.FINANCE]

    def test_detect_task_type_for_finance_and_student_affairs(self):
        router = DepartmentRouter(llm_service=AsyncMock())

        assert router._detect_task_type("Burs başvuru sonucu nedir?", [Department.FINANCE]) == TaskType.SCHOLARSHIP_QUERY
        assert router._detect_task_type("Ders kaydı ne zaman?", [Department.STUDENT_AFFAIRS]) == TaskType.REGISTRATION_QUERY
