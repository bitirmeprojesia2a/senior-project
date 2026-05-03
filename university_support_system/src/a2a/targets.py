"""Shared target model for published A2A services."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.constants import Capability, Department


@dataclass(frozen=True)
class SpecialistTarget:
    """Standalone specialist-agent service target."""

    department: Department
    agent_id: str

    @property
    def value(self) -> str:
        return self.agent_id

    @property
    def display_name(self) -> str:
        return self.agent_id.replace("_", " ").title()


AgentServiceTarget = Department | Capability | SpecialistTarget


def resolve_agent_service_target(
    *,
    raw_target: str | None,
    specialist_id: str | None = None,
) -> AgentServiceTarget:
    """Resolve a configured A2A service target without reading global settings."""
    if not raw_target:
        raise RuntimeError(
            "AGENT_DEPARTMENT ayarlanmali: student_affairs, academic_programs, finance, announcement veya event."
        )

    cleaned_specialist_id = (specialist_id or "").strip()
    if cleaned_specialist_id:
        try:
            return SpecialistTarget(
                department=Department(raw_target),
                agent_id=cleaned_specialist_id,
            )
        except ValueError as exc:
            raise RuntimeError(
                f"Specialist servisleri icin AGENT_DEPARTMENT bir departman olmali: {raw_target}"
            ) from exc

    try:
        return Department(raw_target)
    except ValueError:
        try:
            return Capability(raw_target)
        except ValueError as exc:
            raise RuntimeError(f"Desteklenmeyen AGENT_DEPARTMENT: {raw_target}") from exc


def agent_target_kind(target: AgentServiceTarget) -> str:
    """Return the published service layer for a target."""
    if isinstance(target, Department):
        return "department"
    if isinstance(target, Capability):
        return "capability"
    return "specialist"


def agent_target_department(target: AgentServiceTarget) -> Department | None:
    """Return owning department when the target has one."""
    if isinstance(target, Department):
        return target
    if isinstance(target, SpecialistTarget):
        return target.department
    return None


__all__ = [
    "AgentServiceTarget",
    "SpecialistTarget",
    "agent_target_department",
    "agent_target_kind",
    "resolve_agent_service_target",
]
