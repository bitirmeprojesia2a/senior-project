"""Central source ownership registry for decision tracing.

This module names the authoritative source family for a query. It deliberately
does not replace LLM routing; it sits after routing/planning and resolves
ownership conflicts such as "calendar date handled by student affairs pipeline".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.core.constants import Department, TaskType
from src.core.text_normalization import normalize_text
from src.routing.query_concepts import (
    CONCEPT_ACADEMIC_CALENDAR,
    CONCEPT_APPLICATION,
    CONCEPT_INTERNATIONAL,
    CONCEPT_REGISTRATION,
    CONCEPT_STUDENT_DOCUMENT,
    extract_query_concepts,
)


OWNER_ACADEMIC_CALENDAR = "academic_calendar"
OWNER_ANNOUNCEMENT_SEARCH = "announcement_search"
OWNER_CURRICULUM_CATALOG = "curriculum_catalog"
OWNER_EVENT_SEARCH = "event_search"
OWNER_INTERNATIONAL_POLICY = "international_policy"
OWNER_PERSONAL_STUDENT_DATA = "personal_student_data"
OWNER_STUDENT_AFFAIRS_POLICY = "student_affairs_policy"
OWNER_TUITION_FEE_CATALOG = "tuition_fee_catalog"
OWNER_WEEKLY_SCHEDULE = "weekly_schedule"
SOURCE_OWNER_METADATA_SCHEMA = "omu.source_owner.v1"

_SOURCE_OWNER_ALIASES = {
    "announcement": OWNER_ANNOUNCEMENT_SEARCH,
    "announcement_search": OWNER_ANNOUNCEMENT_SEARCH,
    "event": OWNER_EVENT_SEARCH,
    "event_search": OWNER_EVENT_SEARCH,
    "calendar": OWNER_ACADEMIC_CALENDAR,
    "academic_calendar": OWNER_ACADEMIC_CALENDAR,
    "student_affairs": OWNER_STUDENT_AFFAIRS_POLICY,
    "student_affairs_policy": OWNER_STUDENT_AFFAIRS_POLICY,
    "tuition": OWNER_TUITION_FEE_CATALOG,
    "tuition_fee": OWNER_TUITION_FEE_CATALOG,
    "tuition_fee_catalog": OWNER_TUITION_FEE_CATALOG,
    "finance": OWNER_TUITION_FEE_CATALOG,
    "curriculum": OWNER_CURRICULUM_CATALOG,
    "curriculum_catalog": OWNER_CURRICULUM_CATALOG,
    "schedule": OWNER_WEEKLY_SCHEDULE,
    "weekly_schedule": OWNER_WEEKLY_SCHEDULE,
    "international": OWNER_INTERNATIONAL_POLICY,
    "international_policy": OWNER_INTERNATIONAL_POLICY,
    "personal_student_data": OWNER_PERSONAL_STUDENT_DATA,
}


@dataclass(frozen=True)
class SourceOwnershipResolution:
    primary: str | None = None
    fallbacks: list[str] = field(default_factory=list)
    confidence: float | None = None
    reasoning: str | None = None


@dataclass(frozen=True)
class SourceOwnerRoutingPolicy:
    """Department ownership policy derived from source owner contracts.

    This is a routing guardrail, not an intent decision. The router/capability
    planner may still propose the branch set; this policy only names the branch
    that must be present when a source owner contract is already known.
    """

    source_owner: str
    capability: str | None
    primary_department: Department
    support_departments: tuple[Department, ...] = ()
    reason: str = "source_owner_routing_policy"

    def to_metadata(self) -> dict[str, Any]:
        return {
            "source_owner": self.source_owner,
            "capability": self.capability,
            "primary_department": self.primary_department.value,
            "support_departments": [department.value for department in self.support_departments],
            "reason": self.reason,
        }


_SOURCE_OWNER_ROUTING_POLICIES: tuple[SourceOwnerRoutingPolicy, ...] = (
    SourceOwnerRoutingPolicy(
        source_owner=OWNER_STUDENT_AFFAIRS_POLICY,
        capability="student_affairs.policy_lookup",
        primary_department=Department.STUDENT_AFFAIRS,
        support_departments=(Department.ACADEMIC_PROGRAMS, Department.FINANCE),
        reason="student_affairs_policy_primary",
    ),
    SourceOwnerRoutingPolicy(
        source_owner=OWNER_TUITION_FEE_CATALOG,
        capability="finance.tuition_fee",
        primary_department=Department.FINANCE,
        reason="finance_tuition_owner_primary",
    ),
    SourceOwnerRoutingPolicy(
        source_owner=OWNER_INTERNATIONAL_POLICY,
        capability="international.policy_lookup",
        primary_department=Department.ACADEMIC_PROGRAMS,
        reason="international_policy_owner_primary",
    ),
    SourceOwnerRoutingPolicy(
        source_owner=OWNER_ACADEMIC_CALENDAR,
        capability="calendar.academic_date",
        primary_department=Department.STUDENT_AFFAIRS,
        reason="academic_calendar_owner_primary",
    ),
    SourceOwnerRoutingPolicy(
        source_owner=OWNER_CURRICULUM_CATALOG,
        capability=None,
        primary_department=Department.ACADEMIC_PROGRAMS,
        reason="curriculum_catalog_owner_primary",
    ),
    SourceOwnerRoutingPolicy(
        source_owner=OWNER_WEEKLY_SCHEDULE,
        capability="schedule.weekly_program",
        primary_department=Department.ACADEMIC_PROGRAMS,
        reason="weekly_schedule_owner_primary",
    ),
)


def source_ownership_to_metadata(
    resolution: SourceOwnershipResolution,
    *,
    producer: str = "source_ownership_registry",
) -> dict[str, Any]:
    """Serialize a source-owner decision for A2A/runtime metadata."""
    return {
        "schema": SOURCE_OWNER_METADATA_SCHEMA,
        "producer": producer,
        "primary": normalize_source_owner(resolution.primary),
        "fallbacks": [
            owner
            for owner in (normalize_source_owner(item) for item in resolution.fallbacks)
            if owner
        ],
        "confidence": resolution.confidence,
        "reasoning": resolution.reasoning,
    }


def normalize_source_owner(value: Any) -> str | None:
    """Return the canonical source-owner id used across runtime metadata."""

    key = _selector_value(value)
    if not key:
        return None
    return _SOURCE_OWNER_ALIASES.get(key, key)


def resolve_source_owner_routing_policy(
    *,
    source_owner: str | None,
    capability: str | None = None,
) -> SourceOwnerRoutingPolicy | None:
    """Resolve primary/support department policy for a source-owner contract."""

    owner_key = _selector_value(source_owner)
    capability_key = _selector_value(capability)
    if not owner_key:
        return None

    owner_matches = [
        policy
        for policy in _SOURCE_OWNER_ROUTING_POLICIES
        if policy.source_owner == owner_key
    ]
    if capability_key:
        for policy in owner_matches:
            if policy.capability == capability_key:
                return policy
    for policy in owner_matches:
        if policy.capability is None:
            return policy
    return owner_matches[0] if owner_matches else None


def source_owner_routing_policies() -> tuple[SourceOwnerRoutingPolicy, ...]:
    """Return all configured source-owner routing policies for audits/tests."""

    return _SOURCE_OWNER_ROUTING_POLICIES


def source_owner_from_capability(capability: str | None) -> str | None:
    value = str(capability or "").strip().lower()
    if not value or value == "none":
        return None
    if value == "finance.tuition_fee":
        return OWNER_TUITION_FEE_CATALOG
    if value == "calendar.academic_date":
        return OWNER_ACADEMIC_CALENDAR
    if value == "announcement.search":
        return OWNER_ANNOUNCEMENT_SEARCH
    if value == "event.search":
        return OWNER_EVENT_SEARCH
    if value.startswith("course.") or value.startswith("curriculum."):
        return OWNER_CURRICULUM_CATALOG
    if value == "schedule.weekly_program":
        return OWNER_WEEKLY_SCHEDULE
    if value == "student_affairs.policy_lookup":
        return OWNER_STUDENT_AFFAIRS_POLICY
    if value == "international.policy_lookup":
        return OWNER_INTERNATIONAL_POLICY
    return None


def source_owner_from_task_type(task_type: TaskType | str | None) -> str | None:
    value = _enum_value(task_type)
    if value in {TaskType.TUITION_QUERY.value, TaskType.PAYMENT_QUERY.value}:
        return OWNER_TUITION_FEE_CATALOG
    if value == TaskType.COURSE_QUERY.value:
        return OWNER_CURRICULUM_CATALOG
    if value in {TaskType.REGISTRATION_QUERY.value, TaskType.PROCEDURE_QUERY.value}:
        return OWNER_STUDENT_AFFAIRS_POLICY
    if value == TaskType.SCHOLARSHIP_QUERY.value:
        return OWNER_STUDENT_AFFAIRS_POLICY
    if value == TaskType.DATA_QUERY.value:
        return OWNER_PERSONAL_STUDENT_DATA
    return None


def resolve_source_ownership(
    *,
    original_query: str | None = None,
    effective_query: str | None = None,
    capability: str | None = None,
    primary_intent: str | None = None,
    target_capability: str | None = None,
    task_type: TaskType | str | None = None,
    is_personal: bool = False,
    confidence: float | None = None,
    final_departments: list[str] | None = None,
    override: str | None = None,
) -> SourceOwnershipResolution:
    """Resolve the source family that owns the answer evidence.

    The ordering is intentional: runtime overrides and explicit capabilities
    win first; then registry-level domain guards resolve known cross-pipeline
    conflicts before coarse task types are consulted.
    """
    if override:
        return SourceOwnershipResolution(
            primary=override,
            confidence=1.0,
            reasoning="runtime_override",
        )

    query = " ".join(
        text
        for text in (original_query, effective_query)
        if isinstance(text, str) and text.strip()
    )
    if _looks_like_special_fee_policy_scope(query):
        return SourceOwnershipResolution(
            primary=OWNER_STUDENT_AFFAIRS_POLICY,
            fallbacks=[OWNER_TUITION_FEE_CATALOG],
            confidence=confidence,
            reasoning="source_registry:special_fee_policy_scope",
        )

    capability_owner = source_owner_from_capability(capability)
    if capability_owner:
        return SourceOwnershipResolution(
            primary=capability_owner,
            confidence=confidence,
            reasoning="capability_planner",
        )

    if is_personal:
        return SourceOwnershipResolution(
            primary=OWNER_PERSONAL_STUDENT_DATA,
            confidence=confidence,
            reasoning="router_intent",
        )

    concepts = extract_query_concepts(query)
    normalized_intent = normalize_text(primary_intent)
    normalized_target = normalize_text(target_capability)

    if (
        concepts.has(CONCEPT_ACADEMIC_CALENDAR)
        or normalized_intent == "academic_calendar"
        or normalized_target in {"calendar", "calendar.academic_date"}
    ):
        return SourceOwnershipResolution(
            primary=OWNER_ACADEMIC_CALENDAR,
            fallbacks=[OWNER_STUDENT_AFFAIRS_POLICY],
            confidence=confidence,
            reasoning="source_registry:academic_calendar",
        )

    if _looks_like_international_policy_domain(
        concepts=concepts,
        query=query,
        primary_intent=normalized_intent,
        target_capability=normalized_target,
    ):
        return SourceOwnershipResolution(
            primary=OWNER_INTERNATIONAL_POLICY,
            fallbacks=[OWNER_STUDENT_AFFAIRS_POLICY],
            confidence=confidence,
            reasoning="source_registry:international_policy",
        )

    runtime_departments = {str(department).strip().lower() for department in final_departments or []}
    if OWNER_ANNOUNCEMENT_SEARCH.split("_", 1)[0] in runtime_departments:
        return SourceOwnershipResolution(
            primary=OWNER_ANNOUNCEMENT_SEARCH,
            confidence=confidence,
            reasoning="runtime_department:announcement",
        )
    if OWNER_EVENT_SEARCH.split("_", 1)[0] in runtime_departments:
        return SourceOwnershipResolution(
            primary=OWNER_EVENT_SEARCH,
            confidence=confidence,
            reasoning="runtime_department:event",
        )

    task_owner = source_owner_from_task_type(task_type)
    if task_owner:
        return SourceOwnershipResolution(
            primary=task_owner,
            confidence=confidence,
            reasoning="task_type",
        )

    return SourceOwnershipResolution(reasoning="unresolved")


def _looks_like_special_fee_policy_scope(query: str) -> bool:
    normalized = normalize_text(query)
    if not any(marker in normalized for marker in ("ucret", "harc", "odeme", "katki payi", "ne kadar")):
        return False
    return any(
        marker in normalized
        for marker in (
            "yaz okulu",
            "yaz donemi",
            "yaz ogretimi",
            "cap",
            "capa",
            "cift anadal",
            "cift ana dal",
            "yandal",
            "yan dal",
            "erasmus",
            "degisim programi",
        )
    )


def _looks_like_international_policy_domain(
    *,
    concepts: Any,
    query: str,
    primary_intent: str,
    target_capability: str,
) -> bool:
    if target_capability == "international.policy_lookup":
        return True
    if primary_intent in {"international_policy", "international_registration", "international_student"}:
        return True
    if not concepts.has(CONCEPT_INTERNATIONAL):
        return False
    if concepts.has_any((CONCEPT_REGISTRATION, CONCEPT_APPLICATION, CONCEPT_STUDENT_DOCUMENT)):
        return True
    normalized_query = normalize_text(query)
    return any(
        marker in normalized_query
        for marker in (
            "ikamet",
            "oturma izni",
            "yabanci ogrenci",
            "uluslararasi ogrenci",
            "foreign student",
            "yos",
            "tomer",
            "denklik",
            "kabul",
            "evrak",
            "belge",
        )
    )


def _enum_value(value: Any) -> str | None:
    if value is None:
        return None
    enum_value = getattr(value, "value", None)
    return str(enum_value if enum_value is not None else value)


def _selector_value(value: Any) -> str | None:
    text = str(value or "").strip().lower()
    return text or None
