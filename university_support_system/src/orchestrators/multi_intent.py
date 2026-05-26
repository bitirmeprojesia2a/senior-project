"""Compound-query subtask planning and synthesis helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from src.core.constants import Department, TaskType
from src.core.source_ownership import (
    OWNER_ACADEMIC_CALENDAR,
    OWNER_CURRICULUM_CATALOG,
    OWNER_STUDENT_AFFAIRS_POLICY,
    OWNER_TUITION_FEE_CATALOG,
)
from src.core.text_normalization import normalize_text
from src.db.schemas import DepartmentResponse
from src.orchestrators.response_utils import response_core_answer
from src.quality.answer_style import build_answer_length_instruction

MULTI_INTENT_PLANNER_SCHEMA = "omu.multi_intent_planner.v1"
MULTI_INTENT_SYNTHESIS_SCHEMA = "omu.multi_intent_synthesis.v1"


@dataclass(frozen=True)
class MultiIntentSubtask:
    subtask_id: str
    user_facing_title: str
    effective_question: str
    department: Department
    specialist_hint: str
    task_type: TaskType
    capability: str
    source_family: str
    must_answer: bool = True
    confidence: float = 0.0
    depends_on: tuple[str, ...] = ()
    priority: int = 100

    def to_metadata(self) -> dict[str, Any]:
        return {
            "subtask_id": self.subtask_id,
            "user_facing_title": self.user_facing_title,
            "effective_question": self.effective_question,
            "department": self.department.value,
            "specialist_hint": self.specialist_hint,
            "task_type": self.task_type.value,
            "capability": self.capability,
            "source_family": self.source_family,
            "must_answer": self.must_answer,
            "confidence": self.confidence,
            "depends_on": list(self.depends_on),
            "priority": self.priority,
        }


@dataclass(frozen=True)
class MultiIntentPlan:
    original_query: str
    mode: str
    status: str
    confidence: float
    subtasks: tuple[MultiIntentSubtask, ...] = ()
    fallback_reason: str | None = None
    planner: str = "deterministic"
    schema: str = MULTI_INTENT_PLANNER_SCHEMA

    def is_actionable(self, *, threshold: float) -> bool:
        return (
            self.status == "planned"
            and len(self.subtasks) >= 2
            and self.confidence >= threshold
        )

    def to_metadata(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "mode": self.mode,
            "status": self.status,
            "planner": self.planner,
            "confidence": self.confidence,
            "fallback_reason": self.fallback_reason,
            "subtask_count": len(self.subtasks),
            "subtasks": [subtask.to_metadata() for subtask in self.subtasks],
        }


def plan_multi_intent_query(
    query: str,
    *,
    mode: str,
    student_department: str | None = None,
    max_subtasks: int = 6,
) -> MultiIntentPlan:
    """Build a deterministic subtask plan for clearly compound questions."""

    normalized = normalize_text(query)
    if not normalized:
        return _inactive_plan(query, mode, "empty_query")

    subtasks: list[MultiIntentSubtask] = []

    if _mentions_summer_school(normalized):
        subtasks.append(
            MultiIntentSubtask(
                subtask_id="summer_school_conditions",
                user_facing_title="Yaz okulu",
                effective_question=(
                    "Yaz okulunda ders alma şartları, alınabilecek ders sayısı "
                    "ve kredi sınırı nedir?"
                ),
                department=Department.STUDENT_AFFAIRS,
                specialist_hint="registration_agent",
                task_type=TaskType.REGISTRATION_QUERY,
                capability="student_affairs.policy_lookup",
                source_family=OWNER_STUDENT_AFFAIRS_POLICY,
                confidence=0.90,
                priority=10,
            )
        )

    if _mentions_internship(normalized) and (
        _mentions_summer_school(normalized) or _contains_any(normalized, ("cakisir", "cakisma", "ayni donem"))
    ):
        subtasks.append(
            MultiIntentSubtask(
                subtask_id="internship_overlap",
                user_facing_title="Stajla çakışma",
                effective_question=(
                    "Staj tarihleri yaz okulu dersleri veya sınavları ile çakışırsa "
                    "öğrenci yaz okulunda ders alabilir mi?"
                ),
                department=Department.STUDENT_AFFAIRS,
                specialist_hint="internship_agent",
                task_type=TaskType.PROCEDURE_QUERY,
                capability="student_affairs.policy_lookup",
                source_family=OWNER_STUDENT_AFFAIRS_POLICY,
                confidence=0.91,
                priority=20,
            )
        )

    if _mentions_payment_debt(normalized) and _mentions_registration_or_course_enrollment(normalized):
        subtasks.append(
            MultiIntentSubtask(
                subtask_id="payment_debt_registration",
                user_facing_title="Harç borcu ve kayıt",
                effective_question=(
                    "Katkı payı veya öğrenim ücretini ödemeyen öğrenci ders kaydı "
                    "veya kayıt yenileme yapabilir mi?"
                ),
                department=Department.STUDENT_AFFAIRS,
                specialist_hint="registration_agent",
                task_type=TaskType.REGISTRATION_QUERY,
                capability="student_affairs.policy_lookup",
                source_family=OWNER_STUDENT_AFFAIRS_POLICY,
                confidence=0.93,
                priority=15,
            )
        )

    if _mentions_payment_amount_or_method(normalized):
        subtasks.append(
            MultiIntentSubtask(
                subtask_id="tuition_payment_lookup",
                user_facing_title="Ücret/ödeme bilgisi",
                effective_question="Öğrenim ücreti veya harç ödemesiyle ilgili tutar ya da ödeme bilgisi nedir?",
                department=Department.FINANCE,
                specialist_hint="tuition_agent",
                task_type=TaskType.PAYMENT_QUERY,
                capability="finance.tuition_fee",
                source_family=OWNER_TUITION_FEE_CATALOG,
                confidence=0.86,
                priority=35,
            )
        )

    program_phrase = _program_phrase(query, student_department)
    if _mentions_prerequisite(normalized):
        subtasks.append(
            MultiIntentSubtask(
                subtask_id="prerequisite_check",
                user_facing_title="Önkoşul",
                effective_question=(
                    f"{program_phrase} dersleri için önkoşul açısından dikkat edilmesi gereken şartlar nelerdir?"
                    if program_phrase
                    else "Dersler için önkoşul açısından dikkat edilmesi gereken şartlar nelerdir?"
                ),
                department=Department.ACADEMIC_PROGRAMS,
                specialist_hint="curriculum_agent",
                task_type=TaskType.COURSE_QUERY,
                capability="course.prerequisite_lookup",
                source_family=OWNER_CURRICULUM_CATALOG,
                confidence=0.84,
                priority=40,
            )
        )

    if _mentions_exemption_or_transfer(normalized):
        subtasks.append(
            MultiIntentSubtask(
                subtask_id="course_transfer_or_exemption",
                user_facing_title="Ders saydırma / muafiyet",
                effective_question="Ders saydırma, muafiyet veya intibak işlemlerinde dikkat edilmesi gereken şartlar nelerdir?",
                department=Department.STUDENT_AFFAIRS,
                specialist_hint="registration_agent",
                task_type=TaskType.PROCEDURE_QUERY,
                capability="student_affairs.policy_lookup",
                source_family=OWNER_STUDENT_AFFAIRS_POLICY,
                confidence=0.82,
                priority=45,
            )
        )

    if _mentions_cap(normalized):
        subtasks.append(
            MultiIntentSubtask(
                subtask_id="cap_eligibility",
                user_facing_title="ÇAP/Yandal",
                effective_question="ÇAP veya yandal açısından başvuru ve uygunluk şartları nelerdir?",
                department=Department.ACADEMIC_PROGRAMS,
                specialist_hint="regulation_agent",
                task_type=TaskType.PROCEDURE_QUERY,
                capability="student_affairs.policy_lookup",
                source_family=OWNER_STUDENT_AFFAIRS_POLICY,
                confidence=0.86,
                priority=50,
            )
        )

    if _mentions_graduation(normalized):
        subtasks.append(
            MultiIntentSubtask(
                subtask_id="graduation_requirement",
                user_facing_title="Mezuniyet",
                effective_question="Mezuniyet açısından AKTS, kredi veya ders yükümlülüklerinde dikkat edilmesi gereken şartlar nelerdir?",
                department=Department.STUDENT_AFFAIRS,
                specialist_hint="graduation_agent",
                task_type=TaskType.ACADEMIC_QUERY,
                capability="graduation_akts",
                source_family=OWNER_STUDENT_AFFAIRS_POLICY,
                confidence=0.82,
                priority=55,
            )
        )

    if _mentions_calendar_date(normalized) and len(subtasks) >= 1:
        subtasks.append(
            MultiIntentSubtask(
                subtask_id="academic_calendar_date",
                user_facing_title="Akademik takvim",
                effective_question="Bu süreçle ilgili akademik takvimde belirtilen tarihler nelerdir?",
                department=Department.STUDENT_AFFAIRS,
                specialist_hint="registration_agent",
                task_type=TaskType.REGISTRATION_QUERY,
                capability="calendar.academic_date",
                source_family=OWNER_ACADEMIC_CALENDAR,
                confidence=0.80,
                priority=60,
            )
        )

    subtasks = _deduplicate_subtasks(subtasks)
    subtasks = sorted(subtasks, key=lambda item: (item.priority, item.subtask_id))[:max_subtasks]

    if len(subtasks) < 2:
        return MultiIntentPlan(
            original_query=query,
            mode=mode,
            status="not_compound",
            confidence=0.0 if not subtasks else subtasks[0].confidence,
            subtasks=tuple(subtasks),
            fallback_reason="fewer_than_two_subtasks",
        )

    confidence = min(0.98, sum(item.confidence for item in subtasks) / len(subtasks))
    return MultiIntentPlan(
        original_query=query,
        mode=mode,
        status="planned",
        confidence=round(confidence, 3),
        subtasks=tuple(subtasks),
    )


def has_multi_intent_responses(responses: list[DepartmentResponse]) -> bool:
    return any(_subtask_metadata(response) for response in responses)


def compose_multi_intent_fallback_answer(responses: list[DepartmentResponse]) -> str | None:
    grouped = _group_responses_by_subtask(responses)
    if not grouped:
        return None
    lines: list[str] = []
    for title, subtask_responses in grouped:
        body = _first_meaningful_answer(subtask_responses)
        if not body:
            body = "Bu alt başlık için kaynaklarda net bilgi bulunamadı."
        lines.append(f"{title}:\n{body}")
    return "\n\n".join(lines).strip() or None


def build_multi_intent_synthesis_prompt(
    query: str,
    responses: list[DepartmentResponse],
) -> tuple[str, list[DepartmentResponse]]:
    grouped = _group_responses_by_subtask(responses)
    if not grouped:
        return "", []

    contexts: list[dict[str, Any]] = []
    meaningful: list[DepartmentResponse] = []
    for title, subtask_responses in grouped:
        subtask_payload = _subtask_metadata(subtask_responses[0])
        entries: list[dict[str, Any]] = []
        for response in subtask_responses:
            answer = response_core_answer(response)
            if not answer:
                continue
            meaningful.append(response)
            entries.append(
                {
                    "department": response.department.value,
                    "answer_summary": answer[:1400],
                    "generation_mode": response.generation_mode,
                    "source_count": len(response.sources),
                    "evidence": _compact_sources(response),
                }
            )
        contexts.append(
            {
                "title": title,
                "subtask_id": subtask_payload.get("subtask_id"),
                "effective_question": subtask_payload.get("effective_question"),
                "department": subtask_payload.get("department"),
                "capability": subtask_payload.get("capability"),
                "source_family": subtask_payload.get("source_family"),
                "responses": entries,
            }
        )

    if not meaningful:
        return "", []

    machine_context = json.dumps(
        {
            "schema": MULTI_INTENT_SYNTHESIS_SCHEMA,
            "subtasks": contexts,
        },
        ensure_ascii=False,
        indent=2,
    )
    length_instruction = build_answer_length_instruction(query)
    prompt = (
        f"Kullanıcı sorusu:\n{query}\n\n"
        "Aşağıdaki JSON alt başlıklara ayrılmış kaynak bağlamıdır. "
        "Cevabı bu alt başlıkları koruyarak yaz. Her başlıkta yalnız o alt başlığa ait "
        "kaynakların desteklediği bilgiyi kullan. Kaynakta olmayan tarih, sayı, ücret, portal "
        "veya işlem adımı ekleme. CAP tarihi yalnız kullanıcı tarih sorduysa yazılır. "
        "Harç borcu/kayıt cevabını ücret tutarı sorusuyla karıştırma. "
        "Bir alt başlıkta yeterli kanıt yoksa sadece o başlık altında net bilgi bulunamadığını belirt. "
        "Doğal Türkçe kullan; JSON anahtarlarını ve departman kimliklerini cevapta tekrar etme.\n\n"
        f"{machine_context}\n\n{length_instruction}"
    )
    return prompt, meaningful


def _inactive_plan(query: str, mode: str, reason: str) -> MultiIntentPlan:
    return MultiIntentPlan(
        original_query=query,
        mode=mode,
        status="skipped",
        confidence=0.0,
        fallback_reason=reason,
    )


def _deduplicate_subtasks(subtasks: list[MultiIntentSubtask]) -> list[MultiIntentSubtask]:
    seen: set[str] = set()
    unique: list[MultiIntentSubtask] = []
    for subtask in subtasks:
        if subtask.subtask_id in seen:
            continue
        seen.add(subtask.subtask_id)
        unique.append(subtask)
    return unique


def _subtask_metadata(response: DepartmentResponse) -> dict[str, Any]:
    metadata = response.metadata if isinstance(response.metadata, dict) else {}
    subtask = metadata.get("multi_intent_subtask")
    return subtask if isinstance(subtask, dict) else {}


def _group_responses_by_subtask(
    responses: list[DepartmentResponse],
) -> list[tuple[str, list[DepartmentResponse]]]:
    groups: dict[str, list[DepartmentResponse]] = {}
    titles: dict[str, str] = {}
    order: dict[str, int] = {}
    for response in responses:
        subtask = _subtask_metadata(response)
        subtask_id = str(subtask.get("subtask_id") or "").strip()
        if not subtask_id:
            continue
        groups.setdefault(subtask_id, []).append(response)
        titles[subtask_id] = str(subtask.get("user_facing_title") or subtask_id).strip()
        try:
            order[subtask_id] = int(subtask.get("priority") or 100)
        except (TypeError, ValueError):
            order[subtask_id] = 100
    return [
        (titles[subtask_id], groups[subtask_id])
        for subtask_id in sorted(groups, key=lambda item: (order.get(item, 100), item))
    ]


def _first_meaningful_answer(responses: list[DepartmentResponse]) -> str:
    for response in responses:
        answer = response_core_answer(response)
        if answer:
            return answer
    return ""


def _compact_sources(response: DepartmentResponse) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    for source in response.sources[:2]:
        metadata = source.metadata if isinstance(source.metadata, dict) else {}
        name = (
            metadata.get("source")
            or metadata.get("filename")
            or metadata.get("file_name")
            or "Kaynak"
        )
        sources.append(
            {
                "source": str(name),
                "score": source.score,
                "snippet": source.content[:420],
            }
        )
    return sources


def _program_phrase(query: str, student_department: str | None) -> str:
    if student_department and normalize_text(student_department) in normalize_text(query):
        return student_department.strip()
    normalized = normalize_text(query)
    program_markers = (
        "bilgisayar muhendisligi",
        "elektrik elektronik muhendisligi",
        "elektrik-elektronik muhendisligi",
        "fizik ogretmenligi",
        "fizik egitimi",
    )
    for marker in program_markers:
        if marker in normalized:
            return marker.title().replace("Muhendisligi", "Mühendisliği").replace("Ogretmenligi", "Öğretmenliği")
    return (student_department or "").strip()


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    return any(normalize_text(marker) in text for marker in markers)


def _mentions_summer_school(text: str) -> bool:
    return _contains_any(text, ("yaz okulu", "yaz ogretimi", "yaz donemi"))


def _mentions_internship(text: str) -> bool:
    return _contains_any(text, ("staj", "zorunlu staj", "mesleki uygulama", "mup"))


def _mentions_payment_debt(text: str) -> bool:
    return _contains_any(text, ("harc borcu", "borcum", "borc", "katki payi", "ogrenim ucreti", "odeme"))


def _mentions_registration_or_course_enrollment(text: str) -> bool:
    return _contains_any(text, ("ders kaydi", "kayit yenileme", "kayit", "ders almak", "ders alabilir", "basvuru"))


def _mentions_payment_amount_or_method(text: str) -> bool:
    return _contains_any(
        text,
        (
            "ne kadar",
            "ucret ne",
            "ucreti ne",
            "ucret tutari",
            "nereye yatir",
            "nasil oder",
            "odeme yontemi",
        ),
    ) and _contains_any(text, ("harc", "ucret", "katki payi", "ogrenim ucreti", "odeme"))


def _mentions_prerequisite(text: str) -> bool:
    return _contains_any(text, ("onkosul", "on kosul", "on sart", "onkoşul", "önkoşul"))


def _mentions_exemption_or_transfer(text: str) -> bool:
    return _contains_any(text, ("saydirma", "saydir", "muafiyet", "intibak", "ders transfer"))


def _mentions_cap(text: str) -> bool:
    return _contains_any(text, ("cap", "cift anadal", "cift ana dal", "yandal", "yan dal"))


def _mentions_graduation(text: str) -> bool:
    if _contains_any(text, ("mezuniyet", "mezun olmak", "mezun olma", "mezun olabilir")):
        return True
    return "akts" in text and _contains_any(text, ("toplam", "tamamlamali", "kac akts"))


def _mentions_calendar_date(text: str) -> bool:
    return _contains_any(
        text,
        (
            "ne zaman",
            "takvim",
            "hangi tarihler",
            "basvuru tarihi",
            "sinav tarihi",
            "akademik takvim",
        ),
    )
