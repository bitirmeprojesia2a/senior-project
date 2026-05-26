"""Capability registry and validation helpers."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from src.capabilities.models import CapabilityAction, CapabilitySpec, ValidationResult
from src.core.constants import Department


ACADEMIC_PROGRAMS = Department.ACADEMIC_PROGRAMS.value
STUDENT_AFFAIRS = Department.STUDENT_AFFAIRS.value
FINANCE = Department.FINANCE.value
ANNOUNCEMENT = "announcement"
EVENT = "event"


CAPABILITY_REGISTRY: dict[str, CapabilitySpec] = {
    "announcement.search": CapabilitySpec(
        name="announcement.search",
        description=(
            "Searches active announcements/news/notices in the announcement database. "
            "Use only when the user is asking for announcements, notices, news, or ilan records."
        ),
        departments=(ANNOUNCEMENT,),
        required_params=("query",),
        optional_params=("department", "faculty", "unit_name", "limit", "allow_latest_fallback"),
        param_schemas={
            "limit": {"type": "int", "min": 1, "max": 10},
        },
        executor="announcement.search",
        returns="Announcement records with title, summary, publication date, scope, and links.",
        examples=(
            "Guncel duyurular neler?",
            "Muhendislik fakultesi sinav programi duyurusu var mi?",
        ),
    ),
    "event.search": CapabilitySpec(
        name="event.search",
        description=(
            "Searches active events, seminars, conferences, workshops, and similar records "
            "in the event database."
        ),
        departments=(EVENT,),
        required_params=("query",),
        optional_params=("department", "faculty", "unit_name", "limit"),
        param_schemas={
            "limit": {"type": "int", "min": 1, "max": 10},
        },
        executor="event.search",
        returns="Event records with title, date/time, location, organizer, scope, and links.",
        examples=(
            "Bu hafta seminer var mi?",
            "Bilgisayar Muhendisligi etkinlikleri neler?",
        ),
    ),
    "finance.tuition_fee": CapabilitySpec(
        name="finance.tuition_fee",
        description=(
            "Returns the registered tuition/fee amount for a student type and "
            "academic unit. Use only for explicit amount questions."
        ),
        departments=(FINANCE,),
        required_params=("student_type", "unit_name"),
        optional_params=("academic_year", "query"),
        executor="finance.tuition_fee",
        returns="Tuition fee catalog record with annual and semester amounts.",
        examples=(
            "Fizik ogretmenligi ucreti Turk ogrenci icin ne kadar?",
            "Muhendislik Fakultesi uluslararasi ogrenci ogrenim ucreti nedir?",
        ),
    ),
    "calendar.academic_date": CapabilitySpec(
        name="calendar.academic_date",
        description=(
            "Returns official academic calendar dates such as course start/end, "
            "final exams, make-up exams, or grade entry deadlines."
        ),
        departments=(STUDENT_AFFAIRS,),
        required_any=(("query",), ("label",)),
        optional_params=("term",),
        executor="calendar.academic_date",
        returns="Academic calendar date record.",
        examples=(
            "Akademik takvimde derslerin bitimi ne zaman?",
            "Bahar donemi son ders tarihi nedir?",
        ),
    ),
    "student_affairs.policy_lookup": CapabilitySpec(
        name="student_affairs.policy_lookup",
        description=(
            "Plans a source-grounded student affairs policy/RAG lookup for rules, "
            "eligibility, process, exceptions, or practical guidance. Use for tek ders, "
            "yaz okulu, okul uzamasi, ek AKTS, mezuniyet kosullari, CAP/YAP, ders alma, "
            "general kayit, mazeret, harc borcu policy, and similar procedure questions when no "
            "deterministic catalog/date/fee capability can answer directly. Do not use for "
            "international student admission/registration document questions; use "
            "international.policy_lookup instead."
        ),
        departments=(STUDENT_AFFAIRS,),
        capability_type="policy",
        required_params=("query",),
        optional_params=("topic", "question_type", "must_answer", "preferred_sources", "avoid_sources"),
        executor="policy.student_affairs_lookup",
        returns=(
            "A policy lookup plan. The student affairs agent performs guided retrieval "
            "and LLM synthesis with the supplied answer/evidence contract."
        ),
        examples=(
            "Hic almadigim bir dersten tek derse girebilir miyim?",
            "Yaz okulu uzerinden okulun uzamasini engelleyebilir miyim?",
        ),
    ),
    "international.policy_lookup": CapabilitySpec(
        name="international.policy_lookup",
        description=(
            "Plans a source-grounded international student policy/RAG lookup for "
            "foreign/international student admission, application, registration, required "
            "documents, residence/ikamet documents, YOS, TOMER, equivalence, and similar "
            "international-student procedures. Use this instead of student_affairs.policy_lookup "
            "when the query is specifically about international/yabanci/foreign students."
        ),
        departments=(ACADEMIC_PROGRAMS,),
        capability_type="policy",
        required_params=("query",),
        optional_params=("topic", "question_type", "must_answer", "preferred_sources", "avoid_sources"),
        executor="policy.international_lookup",
        returns=(
            "A policy lookup plan. The international academic agent performs guided retrieval "
            "and LLM synthesis with the supplied answer/evidence contract."
        ),
        examples=(
            "Uluslararasi ogrenci olarak kayit icin hangi belgeler gerekir?",
            "Yabanci ogrenci ikamet evraklari nelerdir?",
        ),
    ),
    "course.exists_in_program": CapabilitySpec(
        name="course.exists_in_program",
        description=(
            "Checks whether a named course is present in a specific program's "
            "curriculum or course plan."
        ),
        departments=(ACADEMIC_PROGRAMS,),
        required_params=("program", "course"),
        optional_params=("course_code",),
        executor="curriculum.course_exists_in_program",
        returns="Course existence result with matching records.",
        examples=(
            "Elektrik Elektronik Muhendisligi mufredatinda Veri Yapilari dersi var mi?",
            "Bilgisayar muhendisliginde Veri Yapilari var mi?",
        ),
    ),
    "course.detail": CapabilitySpec(
        name="course.detail",
        description=(
            "Returns course metadata such as AKTS, credit, class year, semester, "
            "and matched curriculum rows."
        ),
        departments=(ACADEMIC_PROGRAMS,),
        required_any=(("course_code",), ("course",)),
        optional_params=("program",),
        executor="curriculum.course_detail",
        returns="Course detail records.",
        examples=(
            "BIL203 kac AKTS?",
            "Veri Yapilari dersi kac AKTS?",
        ),
    ),
    "course.prerequisites": CapabilitySpec(
        name="course.prerequisites",
        description="Returns prerequisite information for a course.",
        departments=(ACADEMIC_PROGRAMS,),
        required_any=(("course_code",), ("course",)),
        optional_params=("program",),
        executor="curriculum.course_prerequisites",
        returns="Course prerequisite record.",
        examples=(
            "BIL203 on kosulu var mi?",
            "Bu dersin on kosulu ne?",
        ),
    ),
    "curriculum.semester_courses": CapabilitySpec(
        name="curriculum.semester_courses",
        description=(
            "Lists curriculum courses for a program in a given semester/term "
            "number, such as 5th or 7th semester."
        ),
        departments=(ACADEMIC_PROGRAMS,),
        required_params=("program", "semester"),
        optional_params=("class_year", "term"),
        param_schemas={
            "semester": {"type": "int", "min": 1, "max": 12},
            "class_year": {"type": "int", "min": 1, "max": 6},
        },
        executor="curriculum.semester_courses",
        returns="List of curriculum course records.",
        examples=(
            "Bilgisayar Muhendisligi 5. yariyil dersleri neler?",
            "Elektrik Elektronik Muhendisligi 7. yariyil dersleri",
        ),
    ),
    "schedule.weekly_program": CapabilitySpec(
        name="schedule.weekly_program",
        description=(
            "Returns weekly course schedule rows for a program, optionally "
            "filtered by semester, class year, term, or course code."
        ),
        departments=(ACADEMIC_PROGRAMS,),
        required_params=("program",),
        optional_params=("semester", "class_year", "term", "course_code", "course"),
        param_schemas={
            "semester": {"type": "int", "min": 1, "max": 12},
            "class_year": {"type": "int", "min": 1, "max": 6},
        },
        executor="curriculum.weekly_program",
        returns="List of weekly schedule slot records.",
        examples=(
            "Bilgisayar Muhendisligi 4. sinif guz donemi ders programi",
            "Ders programi ne?",
        ),
    ),
}


def _department_value(department: object) -> str:
    if isinstance(department, Department):
        return department.value
    return str(department)


def get_capabilities_for_departments(
    departments: Iterable[object],
) -> list[CapabilitySpec]:
    selected = {_department_value(department) for department in departments}
    return [
        spec
        for spec in CAPABILITY_REGISTRY.values()
        if selected.intersection(spec.departments)
    ]


def format_capabilities_for_prompt(specs: Iterable[CapabilitySpec]) -> str:
    lines: list[str] = []
    for spec in specs:
        required = ", ".join(spec.required_params) or "-"
        if spec.required_any:
            required_any = " OR ".join("/".join(group) for group in spec.required_any)
            required = f"{required}; any_of={required_any}" if required != "-" else required_any
        optional = ", ".join(spec.optional_params) or "-"
        examples = "; ".join(spec.examples[:2])
        lines.append(
            "\n".join(
                [
                    f"- {spec.name}",
                    f"  description: {spec.description}",
                    f"  type: {spec.capability_type}",
                    f"  required: {required}",
                    f"  optional: {optional}",
                    f"  returns: {spec.returns}",
                    f"  examples: {examples}",
                ]
            )
        )
    return "\n".join(lines)


def validate_capability_action(action: CapabilityAction) -> ValidationResult:
    if action.is_none():
        return ValidationResult(valid=True)

    spec = CAPABILITY_REGISTRY.get(action.capability)
    if not spec:
        return ValidationResult(valid=False, error="unknown_capability")

    params = action.params or {}
    missing: list[str] = []

    for name in spec.required_params:
        if _is_blank(params.get(name)):
            missing.append(name)

    if spec.required_any:
        has_group = any(
            all(not _is_blank(params.get(name)) for name in group)
            for group in spec.required_any
        )
        if not has_group:
            missing.append("|".join("/".join(group) for group in spec.required_any))

    if missing:
        return ValidationResult(valid=False, missing_params=tuple(missing), error="missing_params")

    schema_error = _validate_simple_schemas(params, spec.param_schemas)
    if schema_error:
        return ValidationResult(valid=False, error=schema_error)

    return ValidationResult(valid=True)


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def _validate_simple_schemas(
    params: dict[str, Any],
    schemas: dict[str, dict[str, Any]],
) -> str | None:
    for name, schema in schemas.items():
        if name not in params or _is_blank(params.get(name)):
            continue
        value = params.get(name)
        if schema.get("type") == "int":
            try:
                integer = int(value)
            except (TypeError, ValueError):
                return f"invalid_param:{name}"
            if "min" in schema and integer < int(schema["min"]):
                return f"invalid_param:{name}"
            if "max" in schema and integer > int(schema["max"]):
                return f"invalid_param:{name}"
    return None
