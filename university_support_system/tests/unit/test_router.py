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
    async def test_route_skips_llm_for_personal_query_with_low_keyword_score(self):
        """Tek kelime eslesmesi ~0.33 < KEYWORD_MATCH_THRESHOLD olsa bile kisisel soruda LLM yok."""
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Not ortalamam kaç?")

        assert Department.STUDENT_AFFAIRS in result.departments
        assert result.task_type == TaskType.ACADEMIC_QUERY
        llm_service.generate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_route_personal_akts_progress_to_student_affairs(self):
        """Kisisel AKTS tamamlama sorusu akademik program yerine ogrenci islerine gider."""
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Kaç AKTS tamamladım?")

        assert result.departments == [Department.STUDENT_AFFAIRS]
        assert result.task_type == TaskType.ACADEMIC_QUERY
        llm_service.generate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_route_handles_cap_application_with_rule_based_parallel(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(
            return_value='{"departments":["student_affairs","academic_programs"],"confidence":0.82,"reasoning":"CAP sureci ve kosullari iki departmani da ilgilendiriyor."}'
        )
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("ÇAP başvurusu ve müfredat koşulları nelerdir?")

        assert result.departments == [Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS]
        assert result.strategy == RoutingStrategy.PARALLEL
        assert result.confidence == 1.0
        assert result.confidence_level == ConfidenceLevel.HIGH
        assert result.task_type == TaskType.PROCEDURE_QUERY
        llm_service.generate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_route_uses_rule_based_cap_parallel_even_if_llm_is_unavailable(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(side_effect=LLMServiceError("LLM unavailable"))
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("ÇAP başvurusu ve müfredat koşulları nelerdir?")

        assert result.departments == [Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS]
        assert result.strategy == RoutingStrategy.PARALLEL
        assert result.task_type == TaskType.PROCEDURE_QUERY
        llm_service.generate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_route_returns_clarification_when_no_keyword_signal_skips_llm(self):
        """Hic departman anahtar kelimesi yoksa clarification; LLM yonlendirmesi cagrilmaz."""
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Merhaba, bir konuda yardım istiyorum.")

        assert result.departments == []
        assert result.strategy == RoutingStrategy.CLARIFICATION
        assert result.confidence_level == ConfidenceLevel.LOW
        assert result.task_type is None
        llm_service.generate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_route_falls_back_when_llm_returns_invalid_departments(self):
        """Zayif anahtar kelime (LLM cagrilir) ama LLM gecersiz donunce kurala donulur."""
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(return_value='{"departments":["unknown"],"confidence":0.2}')
        router = DepartmentRouter(llm_service=llm_service)

        # Tek "harç" eslesmesi ~0.33; dogrudan yonlendirme esigi altinda, LLM devreye girer
        result = await router.route("Harç hakkında bir şey")

        llm_service.generate.assert_awaited_once()
        assert result.departments == [Department.FINANCE]
        assert result.task_type == TaskType.TUITION_QUERY

    def test_score_departments_matches_known_keywords(self):
        router = DepartmentRouter(llm_service=AsyncMock())
        scores = router._score_departments("Müfredat, AKTS ve bölüm kuralları nerede?")

        assert scores[Department.ACADEMIC_PROGRAMS] > 0
        assert scores[Department.ACADEMIC_PROGRAMS] >= scores[Department.FINANCE]

    def test_score_departments_course_code_boosts_academic(self):
        router = DepartmentRouter(llm_service=AsyncMock())
        scores = router._score_departments("BİL104 dersinin ön koşulu nedir?")
        assert scores[Department.ACADEMIC_PROGRAMS] >= 0.66

    def test_route_with_rules_yariyil_dersleri(self):
        router = DepartmentRouter(llm_service=AsyncMock())
        decision = router._route_with_rules("1. yarıyıl dersleri nelerdir?")
        assert decision.departments == [Department.ACADEMIC_PROGRAMS]
        assert decision.strategy == RoutingStrategy.DIRECT

    @pytest.mark.asyncio
    async def test_route_erasmus_to_academic_programs(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Erasmus başvurusu ne zaman?")

        assert result.departments == [Department.ACADEMIC_PROGRAMS]
        assert result.task_type == TaskType.PROCEDURE_QUERY
        llm_service.generate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_route_academic_calendar_to_student_affairs(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Akademik takvim ne zaman açıklanır?")

        assert result.departments == [Department.STUDENT_AFFAIRS]
        assert result.task_type == TaskType.REGISTRATION_QUERY
        llm_service.generate.assert_not_awaited()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("ascii_query", "turkish_query"),
        [
            ("Kayit yenileme ucreti ne kadar?", "Kayıt yenileme ücreti ne kadar?"),
            ("Cap basvurusu nasil yapilir?", "ÇAP başvurusu nasıl yapılır?"),
        ],
    )
    async def test_route_treats_ascii_and_turkish_variants_the_same(
        self,
        ascii_query,
        turkish_query,
    ):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(
            return_value='{"departments":["finance"],"confidence":0.55,"reasoning":"fallback"}'
        )
        router = DepartmentRouter(llm_service=llm_service)

        ascii_result = await router.route(ascii_query)
        turkish_result = await router.route(turkish_query)

        assert turkish_result.departments == ascii_result.departments
        assert turkish_result.task_type == ascii_result.task_type
        assert turkish_result.strategy == ascii_result.strategy

    @pytest.mark.asyncio
    async def test_route_formal_academic_rules_to_regulation_side(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Bütünleme sınavına kimler girebilir?")

        assert result.departments == [Department.ACADEMIC_PROGRAMS]
        assert result.task_type == TaskType.PROCEDURE_QUERY
        llm_service.generate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_route_generic_department_info_to_clarification(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Bölüm hakkında bilgi verir misin?")

        assert result.departments == []
        assert result.strategy == RoutingStrategy.CLARIFICATION
        llm_service.generate.assert_not_awaited()

    def test_detect_task_type_for_finance_and_student_affairs(self):
        router = DepartmentRouter(llm_service=AsyncMock())

        assert router._detect_task_type("Burs başvuru sonucu nedir?", [Department.FINANCE]) == TaskType.SCHOLARSHIP_QUERY
        assert router._detect_task_type("Ders kaydı ne zaman?", [Department.STUDENT_AFFAIRS]) == TaskType.REGISTRATION_QUERY
