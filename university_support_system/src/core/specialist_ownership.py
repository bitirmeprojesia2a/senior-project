"""Central specialist ownership registry.

The registry is a deterministic guardrail around the LLM/router/capability
contract. It does not decide the user intent; it maps an already-selected
capability/source-owner/topic contract to the safest specialist inside a
department.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from src.core.constants import Department
from src.core.source_ownership import (
    OWNER_ACADEMIC_CALENDAR,
    OWNER_CURRICULUM_CATALOG,
    OWNER_INTERNATIONAL_POLICY,
    OWNER_STUDENT_AFFAIRS_POLICY,
    OWNER_TUITION_FEE_CATALOG,
    OWNER_WEEKLY_SCHEDULE,
)
from src.core.text_normalization import normalize_text


@dataclass(frozen=True)
class SpecialistOwnershipDecision:
    department: Department
    agent_id: str
    reason: str
    topic: str | None = None
    allowed_specialists: tuple[str, ...] = ()
    matched_markers: tuple[str, ...] = ()
    conflict_markers: tuple[str, ...] = ()
    fallback_agent_id: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "department": self.department.value,
            "agent_id": self.agent_id,
            "reason": self.reason,
            "topic": self.topic,
            "allowed_specialists": list(self.allowed_specialists),
            "matched_markers": list(self.matched_markers),
            "conflict_markers": list(self.conflict_markers),
            "fallback_agent_id": self.fallback_agent_id,
        }


@dataclass(frozen=True)
class _PolicyRoute:
    agent_id: str
    topic: str
    markers: tuple[str, ...]
    negative_markers: tuple[str, ...] = ()
    requires_any: tuple[str, ...] = ()


_STUDENT_POLICY_ALLOWED = (
    "registration_agent",
    "graduation_agent",
    "internship_agent",
    "student_life_agent",
)

_REGISTRATION_POLICY = _PolicyRoute(
    agent_id="registration_agent",
    topic="student_affairs_registration_policy",
    markers=(
        "registration",
        "kayit",
        "basvuru",
        "basvuru sarti",
        "basvuru kosulu",
        "dondur",
        "ilisik",
        "yatay",
        "dikey",
        "muafiyet",
        "intibak",
        "cap",
        "cift anadal",
        "cift ana dal",
        "ikinci anadal",
        "ikinci ana dal",
        "yandal",
        "yan dal",
        "gano",
        "gno",
        "not ortalamasi",
        "ortalama",
        "akts hakki",
        "akts siniri",
        "kredi siniri",
        "kredi hakki",
        "ders yuku",
        "itiraz",
        "disiplin",
        "tek ders",
        "yaz okulu",
        "yaz donemi",
        "yaz ogretimi",
        "butunleme",
        "ek sinav",
        "mazeret",
        "takvim",
    ),
    negative_markers=(
        "staj",
        "internship",
        "mesleki uygulama",
        "mup",
        "sanayi",
    ),
)

_INTERNSHIP_POLICY = _PolicyRoute(
    agent_id="internship_agent",
    topic="student_affairs_internship_policy",
    markers=(
        "internship",
        "staj",
        "mesleki uygulama",
        "mup",
        "sanayi",
        "bitirme staji",
        "bitirme staj",
    ),
)

_STUDENT_LIFE_POLICY = _PolicyRoute(
    agent_id="student_life_agent",
    topic="student_affairs_life_policy",
    markers=(
        "student community",
        "ogrenci topluluk",
        "ogrenci toplulugu",
        "topluluk",
        "toplulugu",
        "kulup",
        "konukevi",
        "engelli",
        "konsey",
        "yemek",
        "barinma",
        "kimlik",
        "akademik danisman",
    ),
)

_GRADUATION_POLICY = _PolicyRoute(
    agent_id="graduation_agent",
    topic="student_affairs_graduation_policy",
    markers=(
        "graduation",
        "graduation_akts",
        "graduation akts",
        "mezuniyet islemleri",
        "mezuniyet islemi",
        "mezuniyet basvurusu",
        "mezuniyet belgesi",
        "mezuniyet tamamlama",
        "mezuniyet akts",
        "mezun olma",
        "mezun olmak",
        "mezun olur",
        "toplam akts",
        "tamamlamaliyim",
        "diploma",
        "transkript",
        "not dokumu",
        "bagil",
    ),
    negative_markers=_REGISTRATION_POLICY.markers,
)


def resolve_specialist_owner(
    *,
    department: Department,
    capability: str | None,
    source_owner: str | None,
    semantic_text: str,
) -> SpecialistOwnershipDecision | None:
    """Resolve a specialist from explicit contract ownership signals."""

    capability_key = _value(capability)
    owner_key = _value(source_owner)
    normalized_text = normalize_text(semantic_text or "")

    if department is Department.FINANCE:
        return _finance_decision(department, capability_key, owner_key)
    if department is Department.ACADEMIC_PROGRAMS:
        return _academic_programs_decision(department, capability_key, owner_key)
    if department is Department.STUDENT_AFFAIRS:
        return _student_affairs_decision(
            department,
            capability_key,
            owner_key,
            normalized_text,
        )
    return None


def _finance_decision(
    department: Department,
    capability: str | None,
    source_owner: str | None,
) -> SpecialistOwnershipDecision | None:
    if capability == "finance.tuition_fee" or source_owner == OWNER_TUITION_FEE_CATALOG:
        return SpecialistOwnershipDecision(
            department=department,
            agent_id="tuition_agent",
            reason=_reason(capability=capability, source_owner=source_owner),
            topic="finance_tuition_fee",
            allowed_specialists=("tuition_agent",),
            fallback_agent_id="tuition_agent",
        )
    return None


def _academic_programs_decision(
    department: Department,
    capability: str | None,
    source_owner: str | None,
) -> SpecialistOwnershipDecision | None:
    if capability == "international.policy_lookup" or source_owner == OWNER_INTERNATIONAL_POLICY:
        return SpecialistOwnershipDecision(
            department=department,
            agent_id="international_agent",
            reason=_reason(capability=capability, source_owner=source_owner),
            topic="international_policy",
            allowed_specialists=("international_agent",),
            fallback_agent_id="international_agent",
        )
    if (
        (capability and (capability.startswith("course.") or capability.startswith("curriculum.")))
        or capability == "schedule.weekly_program"
        or source_owner in {OWNER_CURRICULUM_CATALOG, OWNER_WEEKLY_SCHEDULE}
    ):
        return SpecialistOwnershipDecision(
            department=department,
            agent_id="curriculum_agent",
            reason=_reason(capability=capability, source_owner=source_owner),
            topic="academic_catalog",
            allowed_specialists=("curriculum_agent",),
            fallback_agent_id="curriculum_agent",
        )
    if capability == "student_affairs.policy_lookup" or source_owner == OWNER_STUDENT_AFFAIRS_POLICY:
        return SpecialistOwnershipDecision(
            department=department,
            agent_id="regulation_agent",
            reason=_reason(capability=capability, source_owner=source_owner),
            topic="academic_policy_support",
            allowed_specialists=("regulation_agent",),
            fallback_agent_id="regulation_agent",
        )
    return None


def _student_affairs_decision(
    department: Department,
    capability: str | None,
    source_owner: str | None,
    semantic_text: str,
) -> SpecialistOwnershipDecision | None:
    if capability == "calendar.academic_date" or source_owner == OWNER_ACADEMIC_CALENDAR:
        return SpecialistOwnershipDecision(
            department=department,
            agent_id="registration_agent",
            reason=_reason(capability=capability, source_owner=source_owner),
            topic="academic_calendar",
            allowed_specialists=("registration_agent",),
            fallback_agent_id="registration_agent",
        )

    if capability != "student_affairs.policy_lookup" and source_owner != OWNER_STUDENT_AFFAIRS_POLICY:
        return None

    route = _student_policy_route(semantic_text)
    return SpecialistOwnershipDecision(
        department=department,
        agent_id=route.agent_id,
        reason=_reason(capability=capability, source_owner=source_owner, topic=route.topic),
        topic=route.topic,
        allowed_specialists=_STUDENT_POLICY_ALLOWED,
        matched_markers=_matched_markers(semantic_text, route.markers),
        conflict_markers=_conflict_markers(semantic_text, route),
        fallback_agent_id="registration_agent",
    )


def _student_policy_route(semantic_text: str) -> _PolicyRoute:
    # Registration is the safest default for broad student-affairs policy and
    # owns CAP/GPA/application-process topics even when graduation words appear
    # in surrounding context.
    for route in (
        _REGISTRATION_POLICY,
        _INTERNSHIP_POLICY,
        _STUDENT_LIFE_POLICY,
        _GRADUATION_POLICY,
    ):
        if _route_matches(route, semantic_text):
            return route
    if "bitirme" in semantic_text:
        return _PolicyRoute(
            agent_id="registration_agent",
            topic="student_affairs_ambiguous_policy",
            markers=("bitirme",),
        )
    return _REGISTRATION_POLICY


def _route_matches(route: _PolicyRoute, semantic_text: str) -> bool:
    if route.requires_any and not _contains_any(semantic_text, route.requires_any):
        return False
    if route.negative_markers and _contains_any(semantic_text, route.negative_markers):
        return False
    return _contains_any(semantic_text, route.markers)


def _matched_markers(text: str, markers: Iterable[str]) -> tuple[str, ...]:
    return tuple(marker for marker in markers if normalize_text(marker) in text)


def _conflict_markers(text: str, route: _PolicyRoute) -> tuple[str, ...]:
    conflicts = list(_matched_markers(text, route.negative_markers))
    if route.agent_id != "internship_agent" and "bitirme" in text and "staj" not in text:
        conflicts.append("ambiguous:bitirme")
    return tuple(dict.fromkeys(conflicts))


def _contains_any(text: str, markers: Iterable[str]) -> bool:
    return any(normalize_text(marker) in text for marker in markers)


def _value(value: object) -> str | None:
    text = str(value or "").strip().lower()
    return text or None


def _reason(
    *,
    capability: str | None,
    source_owner: str | None,
    topic: str | None = None,
) -> str:
    parts = []
    if capability:
        parts.append(f"capability:{capability}")
    if source_owner:
        parts.append(f"source_owner:{source_owner}")
    if topic:
        parts.append(f"topic:{topic}")
    return "registry:" + ",".join(parts or ["fallback"])


__all__ = ["SpecialistOwnershipDecision", "resolve_specialist_owner"]
