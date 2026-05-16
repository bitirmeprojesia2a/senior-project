"""Runtime answer contracts for high-risk query families.

The contract layer is intentionally small and deterministic.  It does not
replace routing or the LLM planner; it names the source/owner and final answer
rules that must survive until synthesis, validation, cache, and conversation
state writes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from src.core.constants import Department
from src.core.source_ownership import (
    OWNER_ANNOUNCEMENT_SEARCH,
    OWNER_STUDENT_AFFAIRS_POLICY,
    OWNER_TUITION_FEE_CATALOG,
    OWNER_WEEKLY_SCHEDULE,
)
from src.core.text_normalization import normalize_text


ANSWER_CONTRACT_SCHEMA = "omu.answer_contract.v1"
_COURSE_CODE_RE = re.compile(r"\b[A-ZÇĞİÖŞÜ]{2,5}\s*\d{3}[A-Z]?\b", re.IGNORECASE)


@dataclass(frozen=True)
class AnswerContract:
    contract_id: str
    facet: str
    source_owner: str
    capability: str | None
    final_owner: str
    synthesis_policy: str = "allow_llm"
    allowed_departments: tuple[Department, ...] = ()
    forbidden_source_families: tuple[str, ...] = ()
    forbidden_answer_markers: tuple[str, ...] = ()
    required_answer_markers: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_metadata(self) -> dict[str, Any]:
        return {
            "schema": ANSWER_CONTRACT_SCHEMA,
            "contract_id": self.contract_id,
            "facet": self.facet,
            "source_owner": self.source_owner,
            "capability": self.capability,
            "final_owner": self.final_owner,
            "synthesis_policy": self.synthesis_policy,
            "allowed_departments": [department.value for department in self.allowed_departments],
            "forbidden_source_families": list(self.forbidden_source_families),
            "forbidden_answer_markers": list(self.forbidden_answer_markers),
            "required_answer_markers": list(self.required_answer_markers),
            **dict(self.metadata),
        }


def resolve_answer_contract(
    query: str,
    *,
    conversation_frame: dict[str, Any] | None = None,
) -> AnswerContract | None:
    """Return a deterministic contract for query families that must not drift."""

    normalized = normalize_text(query)
    frame_facet = ""
    frame_question_type = ""
    if isinstance(conversation_frame, dict):
        frame_facet = normalize_text(str(conversation_frame.get("policy_facet") or ""))
        frame_question_type = normalize_text(str(conversation_frame.get("question_type") or ""))

    if _is_graduation_akts_contract(normalized, frame_facet=frame_facet, frame_question_type=frame_question_type):
        program_level_payload = _graduation_program_level_metadata(query)
        level = str(program_level_payload.get("education_level") or "")
        allowed_departments = (
            (Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS)
            if level in {"special_long", ""}
            else (Department.STUDENT_AFFAIRS,)
        )
        return AnswerContract(
            contract_id="graduation_akts_total",
            facet="graduation_akts_total",
            source_owner=OWNER_STUDENT_AFFAIRS_POLICY,
            capability="student_affairs.policy_lookup",
            final_owner="main_orchestrator",
            synthesis_policy="llm_with_contract",
            allowed_departments=allowed_departments,
            forbidden_source_families=("formasyon", "erasmus", "lisansustu", "staj", "curriculum_catalog"),
            forbidden_answer_markers=(
                "erasmus",
                "formasyon",
                "pedagojik",
                "toplam akts 300",
                "akts belirtilmemistir",
                "akts sayisi belirtilmemistir",
                "kaynaklarda somut bir akts sayisi verilmemistir",
                "300'ün altında",
                "300 un altinda",
                "30 akts tamamlanmal",
            ),
            metadata={
                "cache_policy": "store_if_validated",
                "program_level": program_level_payload,
                "requires_program_specific_verification": level == "special_long",
            },
        )

    if _is_schedule_full_program_contract(normalized, frame_facet=frame_facet, frame_question_type=frame_question_type):
        return AnswerContract(
            contract_id="schedule_full_program",
            facet="schedule_full_program",
            source_owner=OWNER_WEEKLY_SCHEDULE,
            capability="schedule.weekly_program",
            final_owner="department_orchestrator",
            synthesis_policy="deterministic",
            allowed_departments=(Department.ACADEMIC_PROGRAMS,),
            forbidden_source_families=("student_affairs_policy", "announcement_search"),
            forbidden_answer_markers=("gunu ders programi bulunamadi",),
            metadata={"cache_policy": "store_if_validated"},
        )

    if _is_payment_debt_course_registration_contract(normalized, frame_facet=frame_facet):
        return AnswerContract(
            contract_id="payment_debt_course_registration",
            facet="payment_debt_course_registration",
            source_owner=OWNER_STUDENT_AFFAIRS_POLICY,
            capability="student_affairs.policy_lookup",
            final_owner="main_orchestrator",
            synthesis_policy="llm_with_contract",
            allowed_departments=(Department.STUDENT_AFFAIRS,),
            forbidden_source_families=("tuition_fee_catalog", "curriculum_catalog"),
            forbidden_answer_markers=(
                "turk ogrenci misiniz",
                "uluslararasi ogrenci misiniz",
                "dogru ucreti paylasabilmem",
            ),
            required_answer_markers=("ders kayd",),
            metadata={"cache_policy": "store_if_validated"},
        )

    if _is_regular_tuition_exact_contract(normalized, frame_facet=frame_facet):
        return AnswerContract(
            contract_id="regular_tuition_exact",
            facet="regular_tuition_fee",
            source_owner=OWNER_TUITION_FEE_CATALOG,
            capability="finance.tuition_fee",
            final_owner="department_orchestrator",
            synthesis_policy="deterministic",
            allowed_departments=(Department.FINANCE,),
            forbidden_source_families=("student_affairs_policy", "curriculum_catalog"),
            metadata={"cache_policy": "store_if_validated"},
        )

    if _is_summer_school_policy_contract(normalized, frame_facet=frame_facet):
        return AnswerContract(
            contract_id="summer_school_policy",
            facet="summer_school",
            source_owner=OWNER_STUDENT_AFFAIRS_POLICY,
            capability="student_affairs.policy_lookup",
            final_owner="main_orchestrator",
            synthesis_policy="llm_with_contract",
            allowed_departments=(Department.STUDENT_AFFAIRS,),
            forbidden_source_families=("curriculum_catalog", "weekly_schedule", "tuition_fee_catalog"),
            forbidden_answer_markers=(
                "dis hekimligi",
                "tip fakultesi",
                "yabanci dil egitim ogretimi",
                "pedagojik formasyon",
            ),
            metadata={"target_program": "summer_school"},
        )

    if _is_cap_contract(normalized, frame_facet=frame_facet):
        if any(marker in normalized for marker in ("borc", "borcum", "borcu", "harc")):
            return AnswerContract(
                contract_id="cap_debt_eligibility",
                facet="cap_debt_eligibility",
                source_owner=OWNER_STUDENT_AFFAIRS_POLICY,
                capability="student_affairs.policy_lookup",
                final_owner="main_orchestrator",
                synthesis_policy="llm_with_contract",
                allowed_departments=(Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS),
                forbidden_answer_markers=(
                    "harc borcu olan ogrenciler basvurabilir",
                    "harc borcu olanlar basvurabilir",
                    "dolayisiyla harc borcu olan ogrenciler basvurabilir",
                    "baska bir programa gecmek mumkundur",
                    "baska programa gecmek mumkundur",
                    "programa gecmek mumkundur",
                    "baska bir programa gecis",
                ),
                metadata={
                    "negative_evidence_policy": "absence_is_not_permission",
                    "target_program": "double_major",
                },
            )
        if any(marker in normalized for marker in ("tarih", "tarihleri", "ne zaman", "takvim", "son gun", "son tarih")):
            return AnswerContract(
                contract_id="cap_application_dates",
                facet="cap_application_dates",
                source_owner=OWNER_STUDENT_AFFAIRS_POLICY,
                capability="student_affairs.policy_lookup",
                final_owner="main_orchestrator",
                synthesis_policy="llm_with_supplemental_announcement",
                allowed_departments=(Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS),
                forbidden_answer_markers=("2,50", "2.50", "2,75", "2.75", "120 akts", "240 akts"),
                metadata={
                    "supplemental_source_owner": OWNER_ANNOUNCEMENT_SEARCH,
                    "target_program": "double_major",
                },
            )
        return AnswerContract(
            contract_id="cap_eligibility",
            facet="cap_eligibility",
            source_owner=OWNER_STUDENT_AFFAIRS_POLICY,
            capability="student_affairs.policy_lookup",
            final_owner="main_orchestrator",
            synthesis_policy="llm_with_contract",
            allowed_departments=(Department.STUDENT_AFFAIRS, Department.ACADEMIC_PROGRAMS),
            forbidden_answer_markers=(
                "120 akts",
                "240 akts",
                "2,75",
                "2.75",
                "mezuniyet hakk",
                "diplomasi verilir",
            ),
            required_answer_markers=("3,00", "ilk %20"),
            metadata={"target_program": "double_major"},
        )

    return None


def _graduation_program_level_metadata(query: str) -> dict[str, Any]:
    try:
        from src.agents.student.graduation_utils import resolve_program_level
    except Exception:
        return {"education_level": None, "reason": "resolver_unavailable"}
    try:
        return dict(resolve_program_level(query))
    except Exception:
        return {"education_level": None, "reason": "resolver_failed"}


def contract_from_metadata(metadata: dict[str, Any] | None) -> AnswerContract | None:
    payload = (metadata or {}).get("answer_contract")
    if not isinstance(payload, dict):
        return None
    contract_id = str(payload.get("contract_id") or "").strip()
    facet = str(payload.get("facet") or contract_id).strip()
    source_owner = str(payload.get("source_owner") or "").strip()
    final_owner = str(payload.get("final_owner") or "").strip()
    if not contract_id or not facet or not source_owner or not final_owner:
        return None
    allowed = tuple(
        department
        for value in payload.get("allowed_departments") or []
        for department in _department_from_value(value)
    )
    return AnswerContract(
        contract_id=contract_id,
        facet=facet,
        source_owner=source_owner,
        capability=str(payload.get("capability") or "").strip() or None,
        final_owner=final_owner,
        synthesis_policy=str(payload.get("synthesis_policy") or "allow_llm").strip(),
        allowed_departments=allowed,
        forbidden_source_families=tuple(str(item) for item in payload.get("forbidden_source_families") or []),
        forbidden_answer_markers=tuple(str(item) for item in payload.get("forbidden_answer_markers") or []),
        required_answer_markers=tuple(str(item) for item in payload.get("required_answer_markers") or []),
        metadata={key: value for key, value in payload.items() if key not in {
            "schema",
            "contract_id",
            "facet",
            "source_owner",
            "capability",
            "final_owner",
            "synthesis_policy",
            "allowed_departments",
            "forbidden_source_families",
            "forbidden_answer_markers",
            "required_answer_markers",
        }},
    )


def should_use_deterministic_final(contract: AnswerContract | None) -> bool:
    return bool(contract and contract.synthesis_policy == "deterministic")


def answer_contract_policy_facet(contract: AnswerContract) -> dict[str, Any]:
    target_program = str(contract.metadata.get("target_program") or "").strip() or None
    avoid_markers = list(contract.forbidden_answer_markers)
    if contract.contract_id == "cap_eligibility":
        prefer = ["basvurabilmesi", "not ortalamasi", "3,00", "ilk %20", "basvuru kosullari"]
        avoid_markers.extend(["mezun olabilmesi", "diplomasi verilir", "2,75", "120 akts", "240 akts"])
    elif contract.contract_id == "cap_debt_eligibility":
        prefer = ["harc", "borc", "engel", "basvuru"]
        avoid_markers.extend(["ne kadar", "ogrenim ucreti", "ucret tablosu"])
    elif contract.contract_id == "cap_application_dates":
        prefer = ["akademik takvim", "basvuru tarihleri", "oidb", "duyuru"]
        avoid_markers.extend(["mezun olabilmesi", "diplomasi verilir"])
    elif contract.contract_id == "summer_school_policy":
        prefer = ["yaz okulu", "yaz okulunda ders alabilir", "dersin acilabilmesi", "yaz okulu yonergesi"]
        avoid_markers.extend(["dis hekimligi", "tip fakultesi", "yabanci dil", "pedagojik formasyon"])
    else:
        prefer = []
    return {
        "schema": "omu.policy_facet.v2",
        "facet": contract.facet,
        "facets": [contract.facet],
        "target_program": target_program,
        "target_programs": [target_program] if target_program else [],
        "confidence": 0.95,
        "prefer_evidence_markers": prefer,
        "avoid_evidence_markers": [marker for marker in avoid_markers if marker],
        "program_prefer_evidence_markers": ["cap", "cift ana dal", "cift anadal", "ikinci ana dal"] if target_program else [],
        "program_avoid_evidence_markers": ["yan dal not ortalamasi", "yandal not ortalamasi"] if target_program else [],
        "value_aspects": ["date"] if contract.contract_id == "cap_application_dates" else ["gpa", "percentage"] if contract.contract_id == "cap_eligibility" else [],
        "reason": f"answer_contract:{contract.contract_id}",
    }


def validate_answer_against_contract(
    *,
    query: str,
    answer: str,
    contract: AnswerContract | None,
) -> dict[str, Any]:
    if contract is None:
        return {"status": "pass", "reason": "no_contract"}
    normalized_answer = normalize_text(answer)
    normalized_query = normalize_text(query)
    violations: list[str] = []
    for marker in contract.forbidden_answer_markers:
        normalized_marker = normalize_text(marker)
        if normalized_marker and normalized_marker in normalized_answer:
            violations.append(f"forbidden_marker:{marker}")

    if contract.contract_id == "graduation_akts_total":
        associate_query = "onlisans" in normalized_query or "on lisans" in normalized_query
        bachelor_query = "lisans" in normalized_query and not associate_query
        if bachelor_query:
            if "120 akts" in normalized_answer or "30 akts tamamlan" in normalized_answer:
                violations.append("wrong_bachelor_graduation_akts")
        normal_bachelor_program = not associate_query and any(
            marker in normalized_query
            for marker in ("muhendisligi", "ogretmenligi", "egitimi", "fakulte")
        )
        normal_bachelor_program = normal_bachelor_program or bachelor_query
        special_long_program = any(
            marker in normalized_query
            for marker in ("tip", "dis hekimligi", "eczacilik", "veteriner")
        )
        if associate_query and "120 akts" not in normalized_answer:
            violations.append("missing_associate_graduation_akts")
        if special_long_program and "240 akts" in normalized_answer:
            violations.append("special_long_program_must_not_use_bachelor_default")
        if special_long_program and not any(
            marker in normalized_answer
            for marker in (
                "dogrulanmis toplam akts kosulu yok",
                "program turune gore degisebilir",
                "resmi mufredat",
                "programa ozgu",
            )
        ):
            violations.append("special_long_program_needs_program_specific_verification")
        if normal_bachelor_program and not special_long_program:
            if "30 akts" in normalized_answer and "donem" not in normalized_query:
                violations.append("program_total_confused_with_semester_load")
            if "240 akts" not in normalized_answer:
                violations.append("missing_bachelor_graduation_akts")
        if any(
            marker in normalized_answer
            for marker in (
                "akts belirtilmemistir",
                "akts sayisi belirtilmemistir",
                "kaynaklarda somut bir akts sayisi verilmemistir",
            )
        ):
            violations.append("missing_akts_answer_used_for_deterministic_contract")

    if contract.contract_id == "payment_debt_course_registration":
        if not any(marker in normalized_answer for marker in ("ders kayd", "kayit yenile")):
            violations.append("missing_course_registration_policy")
        if any(
            marker in normalized_answer
            for marker in (
                "turk ogrenci misiniz",
                "uluslararasi ogrenci misiniz",
                "dogru ucreti paylasabilmem",
            )
        ):
            violations.append("tuition_amount_slot_leak")

    if contract.contract_id == "cap_eligibility":
        if not any(marker in normalized_answer for marker in ("3,00", "3.00", "en az 3")):
            violations.append("missing_cap_minimum_gpa")
        if not any(marker in normalized_answer for marker in ("ilk %20", "ilk yuzde 20", "ilk 20")):
            violations.append("missing_cap_ranking_requirement")

    if contract.contract_id == "cap_debt_eligibility":
        if (
            "engel" in normalized_answer
            and "bulunmamaktadir" in normalized_answer
            and any(marker in normalized_answer for marker in ("dolayisiyla", "bu nedenle"))
            and "basvurabilir" in normalized_answer
        ):
            violations.append("absence_of_evidence_used_as_permission")
        absence_markers = (
            "dogrudan bir kisitlama yer almamaktadir",
            "dogrudan kisitlama yer almamaktadir",
            "somut bir kisitlama belirtilmemistir",
            "kisitlama belirtilmemistir",
            "engel teskil ettigine dair somut",
            "basvuruya engel olduguna dair somut",
        )
        safe_missing_evidence_markers = (
            "acik bir hukum bulamadim",
            "dogrudan hukum bulamadim",
            "izin var diye yorumlama",
            "otomatik engel olarak tasimiyorum",
            "ders kaydi veya kayit yenileme",
            "ders kaydi/kayit yenileme",
        )
        if any(marker in normalized_answer for marker in absence_markers) and not any(
            marker in normalized_answer for marker in safe_missing_evidence_markers
        ):
            violations.append("cap_debt_absence_not_qualified")

    return {
        "status": "fail" if violations else "pass",
        "reason": "contract_violations" if violations else "ok",
        "contract_id": contract.contract_id,
        "violations": violations,
    }


def _is_graduation_akts_contract(
    normalized: str,
    *,
    frame_facet: str,
    frame_question_type: str,
) -> bool:
    if "cap" in normalized or "cift anadal" in normalized or "yandal" in normalized:
        return False
    if frame_facet in {"graduation_akts", "graduation_akts_total"}:
        return True
    if frame_question_type in {"graduation_akts", "graduation_total_akts"}:
        return True
    return (
        any(marker in normalized for marker in ("mezun", "mezuniyet", "tamamlam"))
        and any(marker in normalized for marker in ("akts", "ects", "kredi", "kac"))
    )


def _is_schedule_full_program_contract(
    normalized: str,
    *,
    frame_facet: str,
    frame_question_type: str,
) -> bool:
    if "ders programi" not in normalized and "haftalik program" not in normalized:
        return False
    if any(marker in normalized for marker in ("hangi gun", "hangi saatte", "derslik", "sinav takvimi")):
        return False
    if _contains_course_code(normalized) and not any(
        marker in normalized for marker in ("muhendisligi", "ogretmenligi", "egitimi", "bolumu")
    ):
        return False
    return True


def _contains_course_code(normalized: str) -> bool:
    for match in _COURSE_CODE_RE.finditer(normalized):
        token = match.group(0)
        prefix = re.sub(r"[^a-zA-ZÇĞİÖŞÜçğıöşü]", "", token)
        if normalize_text(prefix) in {"icin", "eylul", "mayis", "haziran", "temmuz", "agustos"}:
            continue
        return True
    return False


def _is_regular_tuition_exact_contract(normalized: str, *, frame_facet: str) -> bool:
    if frame_facet == "regular_tuition_fee" and any(marker in normalized for marker in ("turk", "uluslararasi")):
        return True
    if any(marker in normalized for marker in ("yaz okulu", "cap", "cift anadal", "erasmus", "iade", "borc")):
        return False
    return any(marker in normalized for marker in ("ogrenim ucreti", "katki payi", "donemlik ucret", "yillik ucret"))


def _is_payment_debt_course_registration_contract(normalized: str, *, frame_facet: str) -> bool:
    if frame_facet == "payment_debt_course_registration":
        return True
    has_debt = any(marker in normalized for marker in ("borc", "borcum", "borcu", "borclu", "harc"))
    has_registration = any(marker in normalized for marker in ("ders kayd", "ders sec", "kayit yenile"))
    has_eligibility = any(
        marker in normalized
        for marker in ("yapabilir", "yaptirabilir", "olur mu", "miyim", "mi", "mumkun mu")
    )
    return has_debt and has_registration and has_eligibility


def _is_cap_contract(normalized: str, *, frame_facet: str) -> bool:
    return (
        frame_facet in {"cap", "cap_eligibility", "cap_debt_eligibility", "cap_application_dates"}
        or "cap" in normalized
        or "capa" in normalized
        or "cift anadal" in normalized
        or "cift ana dal" in normalized
    )


def _is_summer_school_policy_contract(normalized: str, *, frame_facet: str) -> bool:
    if frame_facet == "summer_school":
        return True
    if not any(marker in normalized for marker in ("yaz okulu", "yaz donemi", "yaz ogretimi")):
        return False
    if any(marker in normalized for marker in ("ucret", "harc", "ne kadar", "odeme")):
        return False
    if any(
        marker in normalized
        for marker in (
            "hangi ders",
            "dersler acilacak",
            "acilacak ders",
            "acilan ders",
            "ders listesi",
        )
    ):
        return False
    return any(marker in normalized for marker in ("sart", "kosul", "kimler", "katil", "alabilir", "nasil"))


def _department_from_value(value: Any) -> tuple[Department, ...]:
    try:
        return (Department(str(value)),)
    except ValueError:
        return ()
