"""Contract answer planning for high-risk deterministic fallback states.

This module deliberately stores fact/state plans, not one-off question answers.
LLM synthesis can be layered on top of these plans, but validators and fallback
paths should share the same source of truth when a contract is violated.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.core.answer_contracts import AnswerContract
from src.core.text_normalization import normalize_text


CONTRACT_ANSWER_PLAN_SCHEMA = "omu.contract_answer_plan.v1"


@dataclass(frozen=True)
class ContractAnswerPlan:
    """A small, auditable answer state for a contract-governed response."""

    contract_id: str
    answer_status: str
    facts: dict[str, Any] = field(default_factory=dict)
    guidance: tuple[str, ...] = ()

    def to_metadata(self) -> dict[str, Any]:
        return {
            "schema": CONTRACT_ANSWER_PLAN_SCHEMA,
            "contract_id": self.contract_id,
            "answer_status": self.answer_status,
            "facts": dict(self.facts),
            "guidance": list(self.guidance),
        }


def build_contract_answer_plan(
    *,
    query: str,
    contract: AnswerContract | None,
    student_department: str | None = None,
    student_education_level: str | None = None,
) -> ContractAnswerPlan | None:
    """Build a reusable fact/state plan for a contract fallback."""
    if contract is None:
        return None
    if contract.contract_id == "graduation_akts_total":
        return build_graduation_akts_answer_plan(
            query=query,
            student_department=student_department,
            student_education_level=student_education_level,
        )
    if contract.contract_id == "cap_eligibility":
        return ContractAnswerPlan(
            contract_id=contract.contract_id,
            answer_status="verified_policy_conditions",
            facts={
                "program": "ÇAP",
                "minimum_gpa": "3,00",
                "ranking_requirement": "ilgili sınıfta ilk %20",
                "application_channel": "ÖİDB/birim internet sayfası",
            },
            guidance=(
                "Başvuru koşulu ile mezuniyet/ÇAP tamamlama koşulunu karıştırma.",
                "Program/fakülte bilgisini yalnız kontenjan veya kişisel uygunluk hesabı için iste.",
            ),
        )
    if contract.contract_id == "cap_debt_eligibility":
        return ContractAnswerPlan(
            contract_id=contract.contract_id,
            answer_status="missing_direct_policy_evidence",
            facts={
                "program": "ÇAP",
                "direct_debt_bar_found": False,
                "payment_rule_scope": "ders kaydı/kayıt yenileme",
            },
            guidance=(
                "Kaynakta açık CAP başvuru engeli yoksa bunu izin var diye yorumlama.",
                "Ders kaydı ödeme şartını CAP başvurusuna otomatik taşıma.",
            ),
        )
    if contract.contract_id == "cap_application_dates":
        return ContractAnswerPlan(
            contract_id=contract.contract_id,
            answer_status="missing_active_exact_date",
            facts={
                "program": "ÇAP",
                "date_source": "akademik takvim ve ÖİDB/birim duyuruları",
                "active_announcement_match": False,
            },
            guidance=("Kesin gün aralığı yoksa tarih uydurma.",),
        )
    return None


def build_graduation_akts_answer_plan(
    *,
    query: str,
    student_department: str | None = None,
    student_education_level: str | None = None,
) -> ContractAnswerPlan:
    """Build the graduation-AKTS fact state from level resolver output."""
    from src.agents.student.graduation_utils import resolve_program_level

    program_level = resolve_program_level(
        query,
        student_department=student_department,
        student_education_level=student_education_level,
    )
    level = program_level.get("education_level")
    facts: dict[str, Any] = {
        "program_level": program_level,
        "education_level": level,
    }
    if level == "associate":
        facts["verified_total_akts"] = 120
        return ContractAnswerPlan(
            contract_id="graduation_akts_total",
            answer_status="verified_level_rule",
            facts=facts,
            guidance=("Ön lisans toplam mezuniyet AKTS kuralını kullan.",),
        )
    if level == "bachelor":
        facts["verified_total_akts"] = 240
        facts["program_duration"] = "normal_4_year"
        return ContractAnswerPlan(
            contract_id="graduation_akts_total",
            answer_status="verified_level_rule",
            facts=facts,
            guidance=("Normal dört yıllık lisans toplam mezuniyet AKTS kuralını kullan.",),
        )
    if level == "special_long":
        facts["verified_total_akts"] = None
        facts["verification_scope"] = "program_specific_requirement"
        return ContractAnswerPlan(
            contract_id="graduation_akts_total",
            answer_status="missing_verified_program_requirement",
            facts=facts,
            guidance=(
                "240 AKTS varsayımı yapma.",
                "Programın resmi müfredat veya mezuniyet koşulu kaynağı gerekir.",
            ),
        )

    facts["verified_total_akts"] = None
    return ContractAnswerPlan(
        contract_id="graduation_akts_total",
        answer_status="missing_program_level",
        facts=facts,
        guidance=("Program düzeyi netleşmeden toplam AKTS genellemesi yapma.",),
    )


def render_contract_answer_plan(plan: ContractAnswerPlan | None) -> str | None:
    """Render a conservative user-facing answer from a contract answer plan."""
    if plan is None:
        return None
    if plan.contract_id == "graduation_akts_total":
        return _render_graduation_akts_plan(plan)
    if plan.contract_id == "cap_eligibility":
        return (
            "ÇAP başvurusu için genel koşullar: ana dal not ortalamasının "
            "4,00 üzerinden en az 3,00 olması ve ana dal diploma programının "
            "ilgili sınıfında başarı sıralaması itibarıyla en az ilk %20 içinde "
            "bulunmak gerekir. Kontenjan ve başvuru takvimi ilgili birim/ÖİDB "
            "duyuruları ile ilan edilir."
        )
    if plan.contract_id == "cap_debt_eligibility":
        return (
            "ÇAP başvurusu için harç borcunun doğrudan başvuruya engel olduğuna "
            "dair açık bir hüküm bulamadım. Ders kaydı veya kayıt yenileme için "
            "ödeme şartı ayrı bir konudur; bu hükmü ÇAP başvurusuna otomatik "
            "engel olarak taşımıyorum."
        )
    if plan.contract_id == "cap_application_dates":
        return (
            "ÇAP başvuru tarihleri akademik takvimde ve ÖİDB/birim duyurularında "
            "ilan edilir. Elimde bu soru için kesin gün aralığı veren aktif bir "
            "duyuru kaydı yok; bu nedenle tarih uydurmuyorum."
        )
    return None


def _render_graduation_akts_plan(plan: ContractAnswerPlan) -> str | None:
    total = plan.facts.get("verified_total_akts")
    level = normalize_text(str(plan.facts.get("education_level") or ""))
    if plan.answer_status == "verified_level_rule" and total == 120:
        return "Ön lisans programından mezun olmak için toplam 120 AKTS tamamlanmalıdır."
    if plan.answer_status == "verified_level_rule" and total == 240:
        return (
            "Normal dört yıllık lisans programından mezun olmak için toplam "
            "240 AKTS tamamlanmalıdır."
        )
    if plan.answer_status == "missing_verified_program_requirement":
        return (
            "Bu program tipi için mezuniyet AKTS yükümlülüğü program türüne göre "
            "değişebilir; elimde bu program için doğrulanmış toplam AKTS koşulu yok. "
            "Programın resmi müfredat/mezuniyet koşulu kaynağı ile kontrol edilmelidir."
        )
    if level:
        return (
            "Bu program düzeyi için doğrulanmış toplam AKTS koşulu elimde yok. "
            "Programın resmi müfredat/mezuniyet koşulu kaynağı ile kontrol edilmelidir."
        )
    return (
        "Toplam mezuniyet AKTS bilgisini güvenilir biçimde verebilmem için program "
        "düzeyinin veya resmi mezuniyet koşulu kaynağının netleşmesi gerekir."
    )
