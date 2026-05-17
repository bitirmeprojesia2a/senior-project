"""Shadow comparison between OMU classic runtime shape and dynamic profiles.

This module is read-only and additive. It does not instantiate orchestrators or
agents, and it does not alter the classic runtime. The goal is to catch whether
the dynamic OMU profile stops representing the currently published runtime
shape before any future pilot/on mode is considered.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.core.constants import Capability, Department
from src.dynamic_platform.models import DynamicPlatformBundle


@dataclass(frozen=True)
class ClassicTopologySnapshot:
    department_agents: set[str]
    capability_agents: set[str]
    specialist_agents: set[str]

    def to_dict(self) -> dict[str, list[str]]:
        return {
            "department_agents": sorted(self.department_agents),
            "capability_agents": sorted(self.capability_agents),
            "specialist_agents": sorted(self.specialist_agents),
        }


@dataclass(frozen=True)
class ClassicCompareIssue:
    severity: str
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
        }


@dataclass
class ClassicCompareReport:
    tenant_key: str
    ok: bool
    classic: ClassicTopologySnapshot
    dynamic: dict[str, list[str]]
    errors: list[ClassicCompareIssue] = field(default_factory=list)
    warnings: list[ClassicCompareIssue] = field(default_factory=list)

    def add_error(self, code: str, message: str) -> None:
        self.errors.append(ClassicCompareIssue("error", code, message))
        self.ok = False

    def add_warning(self, code: str, message: str) -> None:
        self.warnings.append(ClassicCompareIssue("warning", code, message))

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "ok": self.ok,
            "classic": self.classic.to_dict(),
            "dynamic": self.dynamic,
            "errors": [issue.to_dict() for issue in self.errors],
            "warnings": [issue.to_dict() for issue in self.warnings],
        }


def build_classic_topology_snapshot() -> ClassicTopologySnapshot:
    """Return the published OMU classic runtime's stable topology identifiers."""

    specialist_ids = _read_specialist_service_ids()
    return ClassicTopologySnapshot(
        department_agents={department.value for department in Department},
        capability_agents={capability.value for capability in Capability},
        specialist_agents=specialist_ids,
    )


def _read_specialist_service_ids() -> set[str]:
    """Read specialist ids without importing the A2A package dependency graph."""

    service_identity_path = Path(__file__).parents[1] / "a2a" / "service_identity.py"
    tree = ast.parse(service_identity_path.read_text(encoding="utf-8"))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "_SPECIALIST_SERVICE_IDS" for target in node.targets):
            continue
        if not isinstance(node.value, ast.Dict):
            break
        keys: set[str] = set()
        for key in node.value.keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                keys.add(key.value)
        return keys
    return set()


def compare_bundle_to_classic(bundle: DynamicPlatformBundle) -> ClassicCompareReport:
    classic = build_classic_topology_snapshot()
    department_agents = {
        agent.agent_id
        for agent in bundle.agent_pack.agents
        if agent.role == "department_agent"
    }
    capability_agents = {
        agent.agent_id
        for agent in bundle.agent_pack.agents
        if agent.role == "capability_agent"
    }
    specialist_agents = {
        specialist.specialist_id
        for agent in bundle.agent_pack.agents
        for specialist in agent.specialists
    }
    dynamic = {
        "department_agents": sorted(department_agents),
        "capability_agents": sorted(capability_agents),
        "specialist_agents": sorted(specialist_agents),
    }
    report = ClassicCompareReport(
        tenant_key=bundle.tenant.tenant_key,
        ok=True,
        classic=classic,
        dynamic=dynamic,
    )

    if bundle.tenant.runtime_strategy != "classic_protected":
        report.add_warning(
            "tenant_not_classic_protected",
            (
                f"Tenant {bundle.tenant.tenant_key} uses runtime_strategy "
                f"{bundle.tenant.runtime_strategy}; classic parity is intended for protected OMU-like profiles."
            ),
        )

    _compare_required(
        report=report,
        label="department agent",
        code_prefix="department_agents",
        expected=classic.department_agents,
        actual=department_agents,
    )
    _compare_required(
        report=report,
        label="capability agent",
        code_prefix="capability_agents",
        expected=classic.capability_agents,
        actual=capability_agents,
    )
    _compare_required(
        report=report,
        label="specialist agent",
        code_prefix="specialist_agents",
        expected=classic.specialist_agents,
        actual=specialist_agents,
    )
    return report


def _compare_required(
    *,
    report: ClassicCompareReport,
    label: str,
    code_prefix: str,
    expected: set[str],
    actual: set[str],
) -> None:
    missing = sorted(expected - actual)
    extras = sorted(actual - expected)
    if missing:
        report.add_error(
            f"{code_prefix}_missing",
            f"Dynamic profile is missing classic {label}(s): {', '.join(missing)}.",
        )
    if extras:
        report.add_warning(
            f"{code_prefix}_extra",
            f"Dynamic profile has extra {label}(s) beyond classic runtime: {', '.join(extras)}.",
        )
