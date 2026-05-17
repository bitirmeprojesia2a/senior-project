from __future__ import annotations

from src.core.answer_contracts import (
    answer_contract_policy_facet,
    resolve_answer_contract,
    validate_answer_against_contract,
)
from src.core.constants import Department
from src.core.decision_authority import (
    RESOLVED_DECISION_SCHEMA,
    RUNTIME_AUTHORITY_SCHEMA,
    build_resolved_decision_metadata,
    build_runtime_authority_metadata,
)
from src.core.source_ownership import (
    OWNER_ACADEMIC_CALENDAR,
    OWNER_ANNOUNCEMENT_SEARCH,
    OWNER_WEEKLY_SCHEDULE,
    source_owner_from_capability,
)
from src.core.policy_facets import align_policy_evidence
from src.core.specialist_ownership import resolve_specialist_owner
from src.db.schemas import DepartmentResponse, RAGSource
from src.orchestrators.query_policy import should_use_global_synthesis


def test_cap_eligibility_contract_blocks_graduation_facts() -> None:
    contract = resolve_answer_contract("Capa basvurabilir miyim?")

    assert contract is not None
    assert contract.contract_id == "cap_eligibility"
    assert "240 akts" in contract.forbidden_answer_markers

    result = validate_answer_against_contract(
        query="Capa basvurabilir miyim?",
        answer="CAP icin 3,00 gerekir. Lisans icin 240 AKTS sarti vardir.",
        contract=contract,
    )

    assert result["status"] == "fail"


def test_cap_eligibility_contract_requires_core_conditions() -> None:
    contract = resolve_answer_contract("Capa basvurabilir miyim?")

    assert contract is not None
    assert contract.contract_id == "cap_eligibility"

    result = validate_answer_against_contract(
        query="Capa basvurabilir miyim?",
        answer=(
            "CAP'a basvurmak icin OSYM kontenjaninin yuzde 20'sinden az olmamak "
            "uzere belirlenen kontenjana basvurmak gerekir."
        ),
        contract=contract,
    )

    assert result["status"] == "fail"
    assert "missing_cap_minimum_gpa" in result["violations"]
    assert "missing_cap_ranking_requirement" in result["violations"]


def test_cap_debt_contract_rejects_absence_as_permission() -> None:
    contract = resolve_answer_contract("Harc borcum olsaydi CAP'a basvurabilir miydim?")

    assert contract is not None
    assert contract.contract_id == "cap_debt_eligibility"

    result = validate_answer_against_contract(
        query="Harc borcum olsaydi CAP'a basvurabilir miydim?",
        answer=(
            "Başvuru sırasında harç borcu bulunmasının başvuruya engel olduğuna dair "
            "kısıtlayıcı hüküm bulunmamaktadır. Dolayısıyla harç borcu olan öğrenciler başvurabilir."
        ),
        contract=contract,
    )

    assert result["status"] == "fail"
    assert "absence_of_evidence_used_as_permission" in result["violations"]


def test_cap_debt_contract_rejects_unqualified_no_restriction_claim() -> None:
    contract = resolve_answer_contract("Harc borcum olsaydi CAP'a basvurabilir miydim?")

    assert contract is not None
    assert contract.contract_id == "cap_debt_eligibility"

    result = validate_answer_against_contract(
        query="Harc borcum olsaydi CAP'a basvurabilir miydim?",
        answer=(
            "CAP basvurusu yapabilmeniz icin belirlenen kosullar arasinda harc borcu "
            "bulunup bulunmamasiyla ilgili dogrudan bir kisitlama yer almamaktadir."
        ),
        contract=contract,
    )

    assert result["status"] == "fail"
    assert "cap_debt_absence_not_qualified" in result["violations"]


def test_cap_debt_contract_accepts_scoped_missing_evidence_answer() -> None:
    contract = resolve_answer_contract("Harc borcum olsaydi CAP'a basvurabilir miydim?")

    result = validate_answer_against_contract(
        query="Harc borcum olsaydi CAP'a basvurabilir miydim?",
        answer=(
            "CAP basvurusu icin harc borcunun dogrudan basvuruya engel olduguna "
            "dair acik bir hukum bulamadim. Ders kaydi veya kayit yenileme icin "
            "odeme sarti ayri bir konudur."
        ),
        contract=contract,
    )

    assert result["status"] == "pass"


def test_cap_debt_contract_rejects_direct_permission_without_evidence() -> None:
    contract = resolve_answer_contract("Harc borcum olsaydi CAP'a basvurabilir miydim?")

    assert contract is not None
    assert contract.contract_id == "cap_debt_eligibility"

    result = validate_answer_against_contract(
        query="Harc borcum olsaydi CAP'a basvurabilir miydim?",
        answer=(
            "CAP basvurusu icin harc borcu olan ogrenciler basvurabilir. "
            "Basvuru icin 3,00 ortalama gerekir."
        ),
        contract=contract,
    )

    assert result["status"] == "fail"
    assert any(
        violation.startswith("forbidden_marker:harc borcu olan ogrenciler basvurabilir")
        for violation in result["violations"]
    )


def test_cap_debt_contract_rejects_unrelated_transfer_leak() -> None:
    contract = resolve_answer_contract("Harc borcum olsaydi CAP'a basvurabilir miydim?")

    assert contract is not None
    assert contract.contract_id == "cap_debt_eligibility"

    result = validate_answer_against_contract(
        query="Harc borcum olsaydi CAP'a basvurabilir miydim?",
        answer=(
            "CAP basvurusu icin 3,00 ortalama gerekir. "
            "Basvuru kosullarini saglamak sartiyla baska bir programa gecmek mumkundur."
        ),
        contract=contract,
    )

    assert result["status"] == "fail"
    assert any(
        violation.startswith("forbidden_marker:baska bir programa gecmek")
        for violation in result["violations"]
    )


def test_cap_payment_process_query_does_not_use_debt_eligibility_contract() -> None:
    contract = resolve_answer_contract(
        "CAP basvuru sartlari neler ve harc borcumu nasil odeyebilirim?"
    )

    assert contract is not None
    assert contract.contract_id == "cap_eligibility"


def test_cap_debt_policy_facet_demotes_completion_evidence() -> None:
    contract = resolve_answer_contract("Harc borcum olsaydi CAP'a basvurabilir miydim?")

    assert contract is not None
    facet = answer_contract_policy_facet(contract)
    completion_alignment = align_policy_evidence(
        facet,
        content=(
            "CAP programinin tamamlanmasi icin ana dal genel not ortalamasinin "
            "4,00 uzerinden en az 2,75 olmasi gerekir."
        ),
        source_text="yonerge_cift_anadal_yandal.pdf",
    )
    application_alignment = align_policy_evidence(
        facet,
        content=(
            "CAP'a basvurabilmesi icin ana dal not ortalamasinin 4,00 uzerinden "
            "en az 3,00 olmasi ve ilk %20 icinde bulunmasi gerekir."
        ),
        source_text="yonerge_cift_anadal_yandal.pdf",
    )

    assert completion_alignment["status"] == "conflict"
    assert completion_alignment["score_multiplier"] < application_alignment["score_multiplier"]


def test_graduation_contract_rejects_bachelor_120() -> None:
    contract = resolve_answer_contract(
        "Normal lisans programindan mezun olmak icin toplam kac AKTS tamamlamaliyim?"
    )

    assert contract is not None
    assert contract.contract_id == "graduation_akts_total"

    result = validate_answer_against_contract(
        query="Normal lisans programindan mezun olmak icin toplam kac AKTS tamamlamaliyim?",
        answer="Lisans programı için 120 AKTS tamamlanmalıdır.",
        contract=contract,
    )

    assert result["status"] == "fail"
    assert "wrong_bachelor_graduation_akts" in result["violations"]


def test_graduation_contract_accepts_associate_120_without_bachelor_leak() -> None:
    contract = resolve_answer_contract(
        "Onlisans programindan mezun olmak icin kac AKTS tamamlamaliyim?"
    )

    result = validate_answer_against_contract(
        query="Onlisans programindan mezun olmak icin kac AKTS tamamlamaliyim?",
        answer="On lisans programindan mezun olmak icin toplam 120 AKTS tamamlanmalidir.",
        contract=contract,
    )

    assert result["status"] == "pass"
    assert result["violations"] == []


def test_graduation_contract_requires_bachelor_program_total_akts() -> None:
    contract = resolve_answer_contract(
        "Elektrik-Elektronik Muhendisligi icin toplam kac AKTS gerekir?",
        conversation_frame={"policy_facet": "graduation_akts"},
    )

    assert contract is not None
    assert contract.contract_id == "graduation_akts_total"

    result = validate_answer_against_contract(
        query="Elektrik-Elektronik Muhendisligi icin toplam kac AKTS gerekir?",
        answer="Kaynaklarda somut bir AKTS sayisi verilmemistir.",
        contract=contract,
    )

    assert result["status"] == "fail"
    assert "missing_bachelor_graduation_akts" in result["violations"]


def test_graduation_contract_rejects_special_long_bachelor_default() -> None:
    contract = resolve_answer_contract(
        "Tip icin kac AKTS gerekir?",
        conversation_frame={"policy_facet": "graduation_akts"},
    )

    assert contract is not None
    assert contract.contract_id == "graduation_akts_total"

    result = validate_answer_against_contract(
        query="Tip icin kac AKTS gerekir?",
        answer="Tip programi icin 240 AKTS tamamlanmalidir.",
        contract=contract,
    )

    assert result["status"] == "fail"
    assert "special_long_program_must_not_use_bachelor_default" in result["violations"]


def test_graduation_contract_rejects_special_long_source_dump_without_verified_total() -> None:
    contract = resolve_answer_contract(
        "Diş hekimliğinden mezun olmak için kaç AKTS lazım?",
        conversation_frame={"policy_facet": "graduation_akts"},
    )

    assert contract is not None
    assert contract.contract_id == "graduation_akts_total"

    result = validate_answer_against_contract(
        query="Diş hekimliğinden mezun olmak için kaç AKTS lazım?",
        answer=(
            "En ilgili öğrenci işleri kaynağında şu bilgi yer alıyor: "
            "MADDE 5 - Öğrenim gördükleri programların bütün şartlarını yerine getirerek "
            "mezuniyet hakkı kazanan öğrenciler için diploma düzenlenir."
        ),
        contract=contract,
    )

    assert result["status"] == "fail"
    assert "special_long_program_needs_program_specific_verification" in result["violations"]


def test_graduation_contract_accepts_special_long_verification_message() -> None:
    contract = resolve_answer_contract(
        "Diş hekimliğinden mezun olmak için kaç AKTS lazım?",
        conversation_frame={"policy_facet": "graduation_akts"},
    )

    result = validate_answer_against_contract(
        query="Diş hekimliğinden mezun olmak için kaç AKTS lazım?",
        answer=(
            "Bu program tipi için mezuniyet AKTS yükümlülüğü program türüne göre değişebilir; "
            "elimde bu program için doğrulanmış toplam AKTS koşulu yok."
        ),
        contract=contract,
    )

    assert result["status"] == "pass"


def test_cap_date_contract_blocks_graduation_conditions() -> None:
    contract = resolve_answer_contract(
        "Basvuru tarihleri ne peki?",
        conversation_frame={"policy_facet": "cap"},
    )

    assert contract is not None
    assert contract.contract_id == "cap_application_dates"
    assert contract.source_owner == OWNER_ACADEMIC_CALENDAR
    assert contract.capability == "calendar.academic_date"
    assert contract.metadata["calendar_query_prefix"] == "CAP basvuru"

    result = validate_answer_against_contract(
        query="Basvuru tarihleri ne peki?",
        answer="CAP basvuru tarihleri akademik takvimdedir. Mezuniyet icin 240 AKTS gerekir.",
        contract=contract,
    )

    assert result["status"] == "fail"


def test_horizontal_transfer_date_contract_uses_calendar_owner() -> None:
    contract = resolve_answer_contract("Yatay gecis basvuru tarihleri ne zaman?")

    assert contract is not None
    assert contract.contract_id == "horizontal_transfer_application_dates"
    assert contract.source_owner == OWNER_ACADEMIC_CALENDAR
    assert contract.capability == "calendar.academic_date"
    assert contract.metadata["calendar_query_prefix"] == "yatay gecis basvuru"


def test_horizontal_transfer_date_follow_up_uses_frame_facet() -> None:
    contract = resolve_answer_contract(
        "Basvuru tarihleri ne peki?",
        conversation_frame={"policy_facet": "yatay_gecis"},
    )

    assert contract is not None
    assert contract.contract_id == "horizontal_transfer_application_dates"


def test_horizontal_transfer_registration_date_contract_uses_matching_calendar_hint() -> None:
    contract = resolve_answer_contract("Yatay gecis kesin kayit tarihleri ne zaman?")

    assert contract is not None
    assert contract.contract_id == "horizontal_transfer_registration_dates"
    assert contract.metadata["calendar_query_prefix"] == "yatay gecis kesin kayit"


def test_horizontal_transfer_registration_date_follow_up_uses_frame_facet() -> None:
    contract = resolve_answer_contract(
        "Kesin kayit tarihleri ne peki?",
        conversation_frame={"policy_facet": "yatay_gecis"},
    )

    assert contract is not None
    assert contract.contract_id == "horizontal_transfer_registration_dates"
    assert contract.metadata["calendar_query_prefix"] == "yatay gecis kesin kayit"


def test_payment_debt_course_registration_contract_blocks_fee_slot() -> None:
    contract = resolve_answer_contract("Harc borcum bar ders kaydi yapabilir miyim?")

    assert contract is not None
    assert contract.contract_id == "payment_debt_course_registration"

    result = validate_answer_against_contract(
        query="Harc borcum bar ders kaydi yapabilir miyim?",
        answer="Dogru ucreti paylasabilmem icin Turk ogrenci misiniz?",
        contract=contract,
    )

    assert result["status"] == "fail"
    assert "tuition_amount_slot_leak" in result["violations"]


def test_graduation_akts_contract_keeps_llm_as_final_renderer() -> None:
    contract = resolve_answer_contract(
        "Bilgisayar Muhendisligi icin mezuniyette kac AKTS gerekir?"
    )

    assert contract is not None
    assert contract.contract_id == "graduation_akts_total"
    assert contract.synthesis_policy == "llm_with_contract"
    assert contract.final_owner == "main_orchestrator"
    assert contract.metadata["program_level"]["education_level"] == "bachelor"


def test_special_long_graduation_contract_allows_program_specific_support_branch() -> None:
    contract = resolve_answer_contract(
        "Dis hekimliginden mezun olmak icin kac AKTS lazim?"
    )

    assert contract is not None
    assert contract.metadata["program_level"]["education_level"] == "special_long"
    assert contract.metadata["requires_program_specific_verification"] is True
    assert Department.STUDENT_AFFAIRS in contract.allowed_departments
    assert Department.ACADEMIC_PROGRAMS in contract.allowed_departments


def test_payment_debt_course_registration_contract_keeps_llm_as_final_renderer() -> None:
    contract = resolve_answer_contract("Harc borcum varsa ders kaydi yapabilir miyim?")

    assert contract is not None
    assert contract.contract_id == "payment_debt_course_registration"
    assert contract.synthesis_policy == "llm_with_contract"
    assert contract.final_owner == "main_orchestrator"


def test_summer_school_policy_contract_keeps_student_affairs_owner() -> None:
    contract = resolve_answer_contract("Yaz okulu sartlari nelerdir?")

    assert contract is not None
    assert contract.contract_id == "summer_school_policy"
    assert contract.allowed_departments == (Department.STUDENT_AFFAIRS,)
    assert "dis hekimligi" in contract.forbidden_answer_markers


def test_summer_school_open_course_question_is_not_policy_contract() -> None:
    contract = resolve_answer_contract("Yaz okulunda hangi dersler acilacak?")

    assert contract is None


def test_llm_contract_response_can_enter_global_synthesis() -> None:
    contract = resolve_answer_contract(
        "Bilgisayar Muhendisligi icin mezuniyette kac AKTS gerekir?"
    )
    assert contract is not None

    response = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Normal dort yillik lisans programindan mezun olmak icin toplam 240 AKTS tamamlanmalidir.",
        sources=[],
        db_data={"graduation_akts": 240},
        metadata={"answer_contract": contract.to_metadata()},
    )

    assert should_use_global_synthesis(
        query="Bilgisayar Muhendisligi icin mezuniyette kac AKTS gerekir?",
        responses=[response],
    ) is False

    response.sources = [
        # Contract facts are helper evidence; they make LLM refinement eligible.
        RAGSource(
            content=response.answer,
            score=1.0,
            metadata={"source": "education_level_graduation_rule"},
        )
    ]

    assert should_use_global_synthesis(
        query="Bilgisayar Muhendisligi icin mezuniyette kac AKTS gerekir?",
        responses=[response],
    ) is True


def test_deterministic_contract_disables_global_synthesis() -> None:
    contract = resolve_answer_contract("Bilgisayar Muhendisligi ders programi ne?")
    assert contract is not None

    response = DepartmentResponse(
        department=Department.ACADEMIC_PROGRAMS,
        answer="Bilgisayar Muhendisligi icin bulunan ders programi satirlari:",
        db_data={"query_type": "schedule_lookup"},
        metadata={"answer_contract": contract.to_metadata()},
    )

    assert should_use_global_synthesis(
        query="Bilgisayar Muhendisligi ders programi ne?",
        responses=[response],
    ) is False


def test_source_owner_from_schedule_capability_is_weekly_schedule() -> None:
    assert source_owner_from_capability("schedule.weekly_program") == OWNER_WEEKLY_SCHEDULE
    assert source_owner_from_capability("announcement.search") == OWNER_ANNOUNCEMENT_SEARCH


def test_resolved_decision_metadata_carries_contract_authority() -> None:
    contract = resolve_answer_contract("Bilgisayar Muhendisligi ders programi ne?")
    assert contract is not None

    payload = build_resolved_decision_metadata(
        original_query="Ders programi ne?",
        effective_query="Bilgisayar Muhendisligi ders programi ne?",
        answer_contract=contract,
        source_owner_payload={"primary": "schedule"},
        final_answer_owner="department_orchestrator",
        cache_lookup_policy="disabled_for_contract",
        stage="unit_test",
    )

    assert payload["schema"] == RESOLVED_DECISION_SCHEMA
    assert payload["contract"]["id"] == "schedule_full_program"
    assert payload["contract"]["deterministic_final"] is True
    assert payload["source_owner"] == OWNER_WEEKLY_SCHEDULE
    assert "answer_contract" in payload["precedence"]


def test_runtime_authority_metadata_separates_active_and_diagnostic_contract() -> None:
    resolved = {
        "schema": RESOLVED_DECISION_SCHEMA,
        "stage": "unit_test",
        "original_query": "Ders programi ne?",
        "effective_query": "Bilgisayar Muhendisligi ders programi ne?",
        "contract": {"id": "schedule_full_program", "deterministic_final": True},
        "source_owner": OWNER_WEEKLY_SCHEDULE,
        "capability": "schedule.weekly_program",
        "final_answer_owner": "department_orchestrator",
        "diagnostic_contract": {"schema": "omu.decision_contract.v1", "mode": "read_only"},
        "precedence": ["conversation_context", "source_owner", "dispatch"],
    }

    payload = build_runtime_authority_metadata(
        resolved_decision_payload=resolved,
        source_owner_payload={"primary": OWNER_WEEKLY_SCHEDULE},
        decision_contract_payload={"schema": "omu.decision_contract.v1", "mode": "read_only"},
    )

    assert payload["schema"] == RUNTIME_AUTHORITY_SCHEMA
    assert payload["mode"] == "active"
    assert payload["source_owner"] == OWNER_WEEKLY_SCHEDULE
    assert payload["capability"] == "schedule.weekly_program"
    assert payload["diagnostic_contract"]["mode"] == "read_only"
    assert payload["compatibility"]["resolved_decision_schema"] == RESOLVED_DECISION_SCHEMA


def test_course_code_schedule_query_is_not_expanded_to_full_program_contract() -> None:
    assert resolve_answer_contract("BIL203 ders programi ne?") is None


def test_graduation_akts_contract_routes_to_graduation_specialist() -> None:
    contract = resolve_answer_contract(
        "Normal lisans programindan mezun olmak icin toplam kac AKTS tamamlamaliyim?"
    )
    assert contract is not None

    decision = resolve_specialist_owner(
        department=Department.STUDENT_AFFAIRS,
        capability=contract.capability,
        source_owner=contract.source_owner,
        semantic_text=(
            " ".join(
                [
                    contract.contract_id,
                    contract.facet,
                    "Normal lisans programindan mezun olmak icin toplam kac AKTS tamamlamaliyim?",
                ]
            )
        ),
    )

    assert decision is not None
    assert decision.agent_id == "graduation_agent"
