"""Router unit testleri."""

from unittest.mock import AsyncMock

import pytest

from src.core.constants import ConfidenceLevel, Department, RoutingStrategy, TaskType
from src.llm.llm_service import LLMServiceError
from src.routing.routing_policy import (
    looks_like_personal_data_query,
    looks_like_vague_application_timing_query,
)
from src.routing.router import DepartmentRouter


class TestDepartmentRouter:
    """DepartmentRouter davranış testleri."""

    @pytest.mark.asyncio
    async def test_route_applies_guardrail_direct_when_query_is_clear(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Harç ödeme dekontumu nasıl alırım?")

        assert result.departments == [Department.FINANCE]
        assert result.strategy == RoutingStrategy.DIRECT
        assert result.confidence_level in (ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH)
        assert result.task_type == TaskType.TUITION_QUERY

    @pytest.mark.asyncio
    async def test_route_skips_llm_for_personal_query_with_low_keyword_score(self):
        """Tek kelime eslesmesi ~0.33 < KEYWORD_MATCH_THRESHOLD olsa bile kisisel soruda LLM yok."""
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Not ortalamam kaç?")

        assert Department.STUDENT_AFFAIRS in result.departments
        assert result.task_type == TaskType.ACADEMIC_QUERY

    def test_personal_query_detection_does_not_match_generic_procedure_terms(self):
        assert not looks_like_personal_data_query("Staj basvurusu nasil yapilir?")
        assert not looks_like_personal_data_query("Ders kaydi nasil yapilir?")
        assert not looks_like_personal_data_query("Not itirazi nasil yapilir?")
        assert not looks_like_personal_data_query("Sinav notlarimi nereden gorebilirim?")
        assert looks_like_personal_data_query("Not ortalamam kac?")
        assert looks_like_personal_data_query("Stajim ne durumda?")

    def test_vague_application_timing_detection_requires_context(self):
        assert looks_like_vague_application_timing_query("sey basvuru ne zaman")
        assert not looks_like_vague_application_timing_query("CAP basvurusu ne zaman?")

    @pytest.mark.asyncio
    async def test_route_personal_akts_progress_to_student_affairs(self):
        """Kisisel AKTS tamamlama sorusu akademik program yerine ogrenci islerine gider."""
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Kaç AKTS tamamladım?")

        assert result.departments == [Department.STUDENT_AFFAIRS]
        assert result.task_type == TaskType.ACADEMIC_QUERY

    @pytest.mark.asyncio
    async def test_route_lost_identity_card_variants_to_student_affairs_with_guardrail(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        for query in (
            "Ogrenci kartimi kaybettim",
            "Ogrenci kimlik kartim kayip",
            "Ogrenciyim kimligim kayip",
        ):
            result = await router.route(query)

            assert result.departments == [Department.STUDENT_AFFAIRS]
            assert result.strategy == RoutingStrategy.DIRECT

        assert llm_service.generate.await_count == 3

    @pytest.mark.asyncio
    async def test_route_handles_cap_application_with_llm_and_guardrail_parallel(self):
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
        assert result.task_type == TaskType.PROCEDURE_QUERY
        llm_service.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_route_uses_rule_fallback_cap_parallel_even_if_llm_is_unavailable(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(side_effect=LLMServiceError("LLM unavailable"))
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("ÇAP başvurusu ve müfredat koşulları nelerdir?")

        assert result.departments == [Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS]
        assert result.strategy == RoutingStrategy.PARALLEL
        assert result.task_type == TaskType.PROCEDURE_QUERY

    @pytest.mark.asyncio
    async def test_route_single_exam_procedure_overrides_llm_academic_guess(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(
            return_value='{"departments":["academic_programs"],"confidence":0.75,"reasoning":"generic exam rule"}'
        )
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Tek ders sinavlari nedir?")

        assert result.departments == [Department.STUDENT_AFFAIRS]
        assert result.strategy == RoutingStrategy.DIRECT

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
    async def test_route_keeps_low_information_greeting_clarification_even_if_llm_would_have_guessed_department(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(
            return_value='{"departments":["academic_programs"],"confidence":0.71,"reasoning":"guess"}'
        )
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Merhaba")

        assert result.departments == []
        assert result.strategy == RoutingStrategy.CLARIFICATION
        llm_service.generate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_route_uses_llm_for_semantic_course_question_without_keyword_signal(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(
            return_value=(
                '{"departments":["academic_programs"],'
                '"confidence":0.82,'
                '"query_type":"factual",'
                '"complexity":"simple",'
                '"canonical_query":"Olasilik ve istatistige giris dersi hangi sinifta?",'
                '"primary_intent":"course_schedule",'
                '"target_capability":"none",'
                '"required_slots":["course_name"],'
                '"missing_slots":[],'
                '"reasoning":"Ders adi ve sinif/yariyil bilgisi soruluyor."}'
            )
        )
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Olasilik ve istatistige giris dersi hangi sinifta?")

        assert result.departments == [Department.ACADEMIC_PROGRAMS]
        assert result.strategy == RoutingStrategy.DIRECT
        assert result.intent is not None
        assert result.intent.canonical_query == "Olasilik ve istatistige giris dersi hangi sinifta?"
        assert result.intent.primary_intent == "course_schedule"
        assert result.intent.target_capability == "none"
        assert result.intent.required_slots == ["course_name"]
        assert result.intent.missing_slots == []
        llm_service.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_route_preserves_llm_missing_slots_without_departments(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(
            return_value=(
                '{"departments":[],'
                '"confidence":0.36,'
                '"query_type":"factual",'
                '"canonical_query":"Hangi basvuru icin tarih soruluyor?",'
                '"primary_intent":"unknown",'
                '"target_capability":"none",'
                '"required_slots":["application_type"],'
                '"missing_slots":["application_type"],'
                '"reasoning":"basvuru turu belirsiz"}'
            )
        )
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("hangi tarihlerde olacak")

        assert result.departments == []
        assert result.strategy == RoutingStrategy.CLARIFICATION
        assert result.intent is not None
        assert result.intent.missing_slots == ["application_type"]
        assert result.intent.required_slots == ["application_type"]
        llm_service.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_route_preserves_llm_capability_without_departments(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(
            return_value=(
                '{"departments":[],'
                '"confidence":0.82,'
                '"query_type":"factual",'
                '"canonical_query":"Guncel duyurular nelerdir?",'
                '"primary_intent":"announcement",'
                '"target_capability":"announcement",'
                '"required_slots":[],'
                '"missing_slots":[],'
                '"reasoning":"guncel duyuru aramasi"}'
            )
        )
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("son aciklananlar var mi")

        assert result.departments == []
        assert result.intent is not None
        assert result.intent.target_capability == "announcement"
        assert result.intent.primary_intent == "announcement"
        llm_service.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_route_uses_finance_guardrail_for_payment_marker(self):
        """Odeme/harc marker'i netse LLM sonucu finance guardrail'i ile korunur."""
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(return_value='{"departments":["unknown"],"confidence":0.2}')
        router = DepartmentRouter(llm_service=llm_service)

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

    @pytest.mark.asyncio
    async def test_route_incoming_erasmus_registration_to_academic_programs(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Arkadasim erasmus ile yeni geldi nasil kayit yaptirabilir?")

        assert result.departments == [Department.ACADEMIC_PROGRAMS]
        assert result.task_type == TaskType.PROCEDURE_QUERY
        llm_service.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_route_incoming_erasmus_ubys_registration_to_academic_programs(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Gelen erasmus ogrencisi UBYS kaydi nasil yapilir?")

        assert result.departments == [Department.ACADEMIC_PROGRAMS]
        assert result.task_type == TaskType.PROCEDURE_QUERY
        llm_service.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_route_academic_calendar_to_student_affairs(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Akademik takvim ne zaman açıklanır?")

        assert result.departments == [Department.STUDENT_AFFAIRS]
        assert result.task_type == TaskType.REGISTRATION_QUERY

    @pytest.mark.asyncio
    async def test_route_exam_date_query_to_student_affairs_calendar(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(
            return_value='{"departments":["academic_programs"],"confidence":0.82,"reasoning":"guess"}'
        )
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Final sinavlari ne zaman?")

        assert result.departments == [Department.STUDENT_AFFAIRS]
        assert result.task_type == TaskType.REGISTRATION_QUERY
        assert result.strategy == RoutingStrategy.DIRECT

    @pytest.mark.asyncio
    async def test_route_vague_application_timing_to_clarification(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("sey basvuru ne zaman")

        assert result.departments == []
        assert result.strategy == RoutingStrategy.CLARIFICATION
        assert result.confidence_level == ConfidenceLevel.LOW
        assert result.intent is not None
        assert result.intent.missing_slots == ["application_type"]
        llm_service.generate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_route_horizontal_transfer_muafiyet_to_student_affairs_not_announcement(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(
            return_value=(
                '{"departments":[],"confidence":0.82,'
                '"primary_intent":"announcement",'
                '"target_capability":"announcement",'
                '"reasoning":"guess"}'
            )
        )
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Yatay gecisle geldim, muafiyet basvurusu ne zaman yapilir?")

        assert result.departments == [Department.STUDENT_AFFAIRS]
        assert result.strategy == RoutingStrategy.DIRECT
        assert result.task_type in (TaskType.PROCEDURE_QUERY, TaskType.REGISTRATION_QUERY)
        llm_service.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_route_complaint_overrides_llm_announcement_to_student_affairs(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(
            return_value=(
                '{"departments":[],"confidence":0.82,'
                '"primary_intent":"announcement",'
                '"target_capability":"announcement",'
                '"reasoning":"guess"}'
            )
        )
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Hocami sikayet etmek istiyorum nasil yapabilirim?")

        assert result.departments == [Department.STUDENT_AFFAIRS]
        assert result.strategy == RoutingStrategy.DIRECT
        assert result.intent is not None
        assert result.intent.target_capability == "none"
        llm_service.generate.assert_awaited_once()

    def test_registration_prompt_preserves_general_exam_calendar_intent(self):
        from src.llm.prompt_templates import REGISTRATION_AGENT_SYSTEM_PROMPT

        prompt = REGISTRATION_AGENT_SYSTEM_PROMPT.lower()
        assert "final sinavlari ne zaman" in prompt
        assert "tek ders adi isteme" in prompt

    def test_routing_prompt_contains_few_shot_decision_examples(self):
        from src.llm.prompt_templates import DEPARTMENT_ROUTING_SYSTEM_PROMPT

        prompt = DEPARTMENT_ROUTING_SYSTEM_PROMPT.lower()
        assert "karar haritasi" in prompt
        assert "sinav notlari nereden goruntulenebilir" in prompt
        assert "hangi basvuru icin tarih soruluyor" in prompt
        assert "final sinavlari genel akademik takvime gore ne zaman" in prompt
        assert "required_slots" in prompt
        assert "missing_slots" in prompt
        assert "student_type" in prompt

    @pytest.mark.asyncio
    async def test_route_freeze_and_fee_burden_query_to_student_affairs_and_finance(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(side_effect=LLMServiceError("LLM unavailable"))
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route(
            "Ikinci ogretim ogrencisiyim ve bir donem kayit dondurmak istiyorum. "
            "Bu donem harc ucretimi yatirmak zorunda miyim?"
        )

        assert result.departments == [Department.STUDENT_AFFAIRS, Department.FINANCE]
        assert result.strategy == RoutingStrategy.PARALLEL
        assert result.task_type == TaskType.TUITION_QUERY

    @pytest.mark.asyncio
    async def test_route_registration_fee_timing_override_stays_student_affairs_and_finance(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(
            return_value=(
                '{"departments":["finance","academic_programs"],'
                '"confidence":0.82,'
                '"query_type":"procedural",'
                '"complexity":"process_chain",'
                '"reasoning":"guess"}'
            )
        )
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Kayit yenileme ucreti ne kadar ve ne zaman yapilir?")

        assert result.departments == [Department.STUDENT_AFFAIRS, Department.FINANCE]
        assert Department.ACADEMIC_PROGRAMS not in result.departments
        assert result.strategy == RoutingStrategy.PARALLEL
        llm_service.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_route_scholarship_application_stays_finance_only(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(
            return_value=(
                '{"departments":["finance","student_affairs"],'
                '"confidence":0.79,'
                '"query_type":"procedural",'
                '"complexity":"process_chain",'
                '"reasoning":"guess"}'
            )
        )
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Burs basvurusu nasil yapilir?")

        assert result.departments == [Department.FINANCE]
        assert result.strategy == RoutingStrategy.DIRECT
        llm_service.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_route_international_scholarship_to_academic_and_finance(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(
            return_value=(
                '{"departments":["finance"],'
                '"confidence":0.72,'
                '"query_type":"procedural",'
                '"complexity":"simple",'
                '"reasoning":"guess"}'
            )
        )
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Erasmus hibe miktari ve burs basvurusu nasil yapilir?")

        assert result.departments == [Department.ACADEMIC_PROGRAMS, Department.FINANCE]
        assert result.strategy == RoutingStrategy.PARALLEL
        assert result.task_type == TaskType.SCHOLARSHIP_QUERY
        llm_service.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_route_personal_finance_query_skips_llm_and_marks_personal(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(
            return_value='{"departments":["finance"],"confidence":0.9,"reasoning":"guess"}'
        )
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Harc borcum ne kadar?")

        assert result.departments == [Department.FINANCE]
        assert result.task_type == TaskType.TUITION_QUERY
        assert result.intent is not None
        assert result.intent.is_personal is True
        llm_service.generate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_route_graduation_payment_personal_query_to_student_affairs_and_finance(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Mezuniyet harc borcu kaldi mi?")

        assert result.departments == [Department.STUDENT_AFFAIRS, Department.FINANCE]
        assert result.strategy == RoutingStrategy.PARALLEL
        assert result.task_type == TaskType.TUITION_QUERY
        assert result.intent is not None
        assert result.intent.is_personal is True
        llm_service.generate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_route_registration_process_query_stays_student_affairs_with_guardrail(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(
            return_value='{"departments":["academic_programs"],"confidence":0.71,"reasoning":"guess"}'
        )
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Kayit yenileme nasil yapilir?")

        assert result.departments == [Department.STUDENT_AFFAIRS]
        assert result.strategy == RoutingStrategy.DIRECT
        llm_service.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_route_internship_procedure_stays_student_affairs_with_guardrail(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(
            return_value='{"departments":["academic_programs"],"confidence":0.82,"reasoning":"guess"}'
        )
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Staj basvurusu nasil yapilir?")

        assert result.departments == [Department.STUDENT_AFFAIRS]
        assert result.strategy == RoutingStrategy.DIRECT
        assert result.task_type == TaskType.PROCEDURE_QUERY
        llm_service.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_route_course_code_query_uses_academic_context_guardrail(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(
            return_value='{"departments":["student_affairs"],"confidence":0.61,"reasoning":"guess"}'
        )
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("BIL104 dersinin on kosulu nedir?")

        assert result.departments == [Department.ACADEMIC_PROGRAMS]
        assert result.strategy == RoutingStrategy.DIRECT
        llm_service.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_route_payment_query_stays_finance_with_guardrail(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(
            return_value='{"departments":["academic_programs"],"confidence":0.61,"reasoning":"guess"}'
        )
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Harc taksitlendirme yapilabiliyor mu?")

        assert result.departments == [Department.FINANCE]
        assert result.strategy == RoutingStrategy.DIRECT
        llm_service.generate.assert_awaited_once()

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

        assert result.departments == [Department.STUDENT_AFFAIRS]
        assert result.task_type == TaskType.ACADEMIC_QUERY

    @pytest.mark.asyncio
    async def test_route_exam_discipline_process_to_student_affairs(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(
            return_value='{"departments":["academic_programs","student_affairs"],"confidence":0.85,"reasoning":"sinav sureci"}'
        )
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Sinavda kopya cekilirse disiplin sureci nasil isler?")

        assert result.departments == [Department.STUDENT_AFFAIRS]

    @pytest.mark.asyncio
    async def test_route_exam_grade_objection_admin_flow_to_student_affairs(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(
            return_value='{"departments":["academic_programs"],"confidence":0.82,"reasoning":"guess"}'
        )
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Not itirazi nasil yapilir?")

        assert result.departments == [Department.STUDENT_AFFAIRS]
        assert result.task_type == TaskType.REGISTRATION_QUERY

    @pytest.mark.asyncio
    async def test_route_grade_visibility_question_to_registration_not_personal_summary(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock(
            return_value='{"departments":["student_affairs"],"confidence":0.82,"reasoning":"grade visibility"}'
        )
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Sinav notlarimi nereden gorebilirim?")

        assert result.departments == [Department.STUDENT_AFFAIRS]
        assert result.task_type == TaskType.REGISTRATION_QUERY
        llm_service.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_route_distance_learning_assessment_to_student_affairs_and_academic_programs(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route(
            "Uzaktan egitim yoluyla alinan 5-i derslerinin sinav ve basari degerlendirmesi yuz yuze derslerden farkli midir?"
        )

        assert result.departments == [Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS]
        assert result.strategy == RoutingStrategy.PARALLEL
        llm_service.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_route_pedagogical_formation_prefers_academic_programs_over_document_markers(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route(
            "Pedagojik formasyon dersleri transkripte dahil mi ve diplomada hangi ibare olur?"
        )

        assert result.departments == [Department.ACADEMIC_PROGRAMS]
        assert result.task_type == TaskType.COURSE_QUERY
        llm_service.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_route_international_registration_with_fee_and_residence_is_three_way(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route(
            "Uluslararasi ogrenci kayit olurken ogrenim ucretini nereye yatirir ve ikamet belgesi gerekir mi?"
        )

        assert result.departments == [
            Department.ACADEMIC_PROGRAMS,
            Department.STUDENT_AFFAIRS,
            Department.FINANCE,
        ]
        assert result.strategy == RoutingStrategy.PARALLEL
        assert result.intent is not None
        assert result.intent.force_llm_synthesis is True

    @pytest.mark.asyncio
    async def test_route_scholarship_transfer_policy_is_not_personal_auth_guard(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route(
            "Burslu ogrenciyim ve yatay gecis yapmak istiyorum. Bursum kesilir mi, harc oder miyim?"
        )

        assert result.departments == [Department.STUDENT_AFFAIRS, Department.FINANCE]
        assert result.strategy == RoutingStrategy.PARALLEL
        assert result.intent is not None
        assert result.intent.is_personal is False
        assert result.intent.force_llm_synthesis is True

    @pytest.mark.asyncio
    async def test_route_max_duration_fee_question_uses_three_departments(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route(
            "Program suresini astim. Ek sure hakkim var mi ve katki payi oder miyim?"
        )

        assert result.departments == [
            Department.ACADEMIC_PROGRAMS,
            Department.STUDENT_AFFAIRS,
            Department.FINANCE,
        ]
        assert result.strategy == RoutingStrategy.PARALLEL
        assert result.intent is not None
        assert result.intent.force_llm_synthesis is True

    @pytest.mark.asyncio
    async def test_route_generic_department_info_to_clarification(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route("Bölüm hakkında bilgi verir misin?")

        assert result.departments == []
        assert result.strategy == RoutingStrategy.CLARIFICATION

    @pytest.mark.asyncio
    async def test_route_with_hints_uses_preferred_departments_for_signal_free_follow_up(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route_with_hints(
            "Peki sonra?",
            preferred_departments=[Department.STUDENT_AFFAIRS],
        )

        assert result.departments == [Department.STUDENT_AFFAIRS]
        assert result.strategy == RoutingStrategy.DIRECT
        assert result.confidence >= 0.74

    @pytest.mark.asyncio
    async def test_route_with_hints_does_not_override_clear_rule_with_unrelated_preference(self):
        llm_service = AsyncMock()
        llm_service.generate = AsyncMock()
        router = DepartmentRouter(llm_service=llm_service)

        result = await router.route_with_hints(
            "Erasmus basvurusu ne zaman?",
            preferred_departments=[Department.FINANCE],
        )

        assert result.departments == [Department.ACADEMIC_PROGRAMS]
        assert result.strategy == RoutingStrategy.DIRECT

    def test_detect_task_type_for_finance_and_student_affairs(self):
        router = DepartmentRouter(llm_service=AsyncMock())

        assert router._detect_task_type("Burs başvuru sonucu nedir?", [Department.FINANCE]) == TaskType.SCHOLARSHIP_QUERY
        assert router._detect_task_type("Ders kaydı ne zaman?", [Department.STUDENT_AFFAIRS]) == TaskType.REGISTRATION_QUERY
    
    def test_detect_task_type_routes_admin_student_affairs_workflows_to_registration(self):
        router = DepartmentRouter(llm_service=AsyncMock())

        assert (
            router._detect_task_type(
                "Sinav notuma itiraz etmek istiyorum.",
                [Department.STUDENT_AFFAIRS],
            )
            == TaskType.REGISTRATION_QUERY
        )
        assert (
            router._detect_task_type(
                "Sinavda kopya cekilirse disiplin sureci nasil isler?",
                [Department.STUDENT_AFFAIRS],
            )
            == TaskType.REGISTRATION_QUERY
        )
        assert (
            router._detect_task_type(
                "Hocam ders notlarimi sisteme girmemis, ne yapabilirim?",
                [Department.STUDENT_AFFAIRS],
            )
            == TaskType.REGISTRATION_QUERY
        )
        assert (
            router._detect_task_type(
                "Hocami sikayet etmek istiyorum, nasil yapabilirim?",
                [Department.STUDENT_AFFAIRS],
            )
            == TaskType.REGISTRATION_QUERY
        )
