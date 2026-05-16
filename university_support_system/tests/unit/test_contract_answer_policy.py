from __future__ import annotations

from src.core.answer_contracts import resolve_answer_contract
from src.core.contract_answer_policy import (
    build_contract_answer_plan,
    build_graduation_akts_answer_plan,
    render_contract_answer_plan,
)


def test_graduation_answer_plan_separates_fact_state_from_rendered_answer() -> None:
    plan = build_graduation_akts_answer_plan(
        query="Bilgisayar Mühendisliği için kaç AKTS gerekir?"
    )

    assert plan.answer_status == "verified_level_rule"
    assert plan.facts["verified_total_akts"] == 240
    assert plan.facts["education_level"] == "bachelor"
    assert "240 AKTS" in (render_contract_answer_plan(plan) or "")


def test_graduation_answer_plan_special_long_abstains_without_static_program_patch() -> None:
    plan = build_graduation_akts_answer_plan(
        query="Diş hekimliğinden mezun olmak için kaç AKTS lazım?"
    )

    answer = render_contract_answer_plan(plan)

    assert plan.answer_status == "missing_verified_program_requirement"
    assert plan.facts["education_level"] == "special_long"
    assert plan.facts["verified_total_akts"] is None
    assert answer is not None
    assert "doğrulanmış toplam AKTS koşulu yok" in answer
    assert "240 AKTS" not in answer


def test_contract_answer_plan_renders_cap_debt_as_policy_state_not_permission() -> None:
    query = "Harç borcum olsaydı ÇAP'a başvurabilir miydim?"
    contract = resolve_answer_contract(query)
    plan = build_contract_answer_plan(query=query, contract=contract)

    answer = render_contract_answer_plan(plan)

    assert plan is not None
    assert plan.answer_status == "missing_direct_policy_evidence"
    assert plan.facts["direct_debt_bar_found"] is False
    assert answer is not None
    assert "başvuruya engel olduğuna dair açık bir hüküm bulamadım" in answer
    assert "başvurabilir" not in answer
