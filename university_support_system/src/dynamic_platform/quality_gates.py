"""Offline quality gates for dynamic tenant profiles.

Quality gates are intentionally separate from the live runtime. They combine
validation, optional classic OMU topology parity, and required shadow decision
contract checks into one release/readiness report.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.dynamic_platform.classic_compare import compare_bundle_to_classic
from src.dynamic_platform.decision_shadow import (
    compare_shadow_decisions,
    default_shadow_fixture_path,
    load_shadow_decision_cases,
)
from src.dynamic_platform.models import DynamicPlatformBundle
from src.dynamic_platform.source_audit import audit_source_adapters
from src.dynamic_platform.validator import validate_bundle


@dataclass(frozen=True)
class QualityGate:
    gate_id: str
    status: str
    message: str
    detail: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.status in {"passed", "skipped"}

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "status": self.status,
            "message": self.message,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class QualityGateReport:
    tenant_key: str
    ok: bool
    gates: list[QualityGate]

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "ok": self.ok,
            "summary": {
                "gate_count": len(self.gates),
                "passed": sum(1 for gate in self.gates if gate.status == "passed"),
                "failed": sum(1 for gate in self.gates if gate.status == "failed"),
                "skipped": sum(1 for gate in self.gates if gate.status == "skipped"),
            },
            "gates": [gate.to_dict() for gate in self.gates],
        }


def run_quality_gates(
    bundle: DynamicPlatformBundle,
    *,
    shadow_fixture_path: str | Path | None = None,
    require_shadow_fixture: bool = True,
) -> QualityGateReport:
    gates: list[QualityGate] = []

    validation = validate_bundle(bundle)
    gates.append(
        QualityGate(
            gate_id="validate_bundle",
            status="passed" if validation.ok else "failed",
            message="Tenant bundle schema and topology references are valid."
            if validation.ok
            else "Tenant bundle validation failed.",
            detail=validation.to_dict(),
        )
    )

    if bundle.tenant.runtime_strategy == "classic_protected":
        classic = compare_bundle_to_classic(bundle)
        gates.append(
            QualityGate(
                gate_id="classic_topology_compare",
                status="passed" if classic.ok else "failed",
                message="Dynamic profile matches the protected classic OMU topology."
                if classic.ok
                else "Dynamic profile diverges from the protected classic OMU topology.",
                detail=classic.to_dict(),
            )
        )
    else:
        gates.append(
            QualityGate(
                gate_id="classic_topology_compare",
                status="skipped",
                message="Tenant is not classic_protected; OMU classic topology parity is not required.",
            )
        )

    source_audit = audit_source_adapters(bundle)
    gates.append(
        QualityGate(
            gate_id="source_adapter_audit",
            status="passed" if source_audit.ok else "failed",
            message="Source adapter contracts are valid."
            if source_audit.ok
            else "Source adapter contract audit failed.",
            detail=source_audit.to_dict(),
        )
    )

    fixture_path = Path(shadow_fixture_path) if shadow_fixture_path else default_shadow_fixture_path(bundle.tenant.tenant_key)
    if fixture_path.exists():
        cases = load_shadow_decision_cases(fixture_path)
        shadow = compare_shadow_decisions(bundle, cases, fixture_path=fixture_path)
        gates.append(
            QualityGate(
                gate_id="shadow_decision_contracts",
                status="passed" if shadow.ok else "failed",
                message="Shadow decision contracts are represented by the dynamic profile."
                if shadow.ok
                else "Shadow decision contracts are not fully represented by the dynamic profile.",
                detail=shadow.to_dict(),
            )
        )
    else:
        gates.append(
            QualityGate(
                gate_id="shadow_decision_contracts",
                status="failed" if require_shadow_fixture else "skipped",
                message=f"Shadow decision fixture not found: {fixture_path}",
                detail={"fixture_path": str(fixture_path)},
            )
        )

    return QualityGateReport(
        tenant_key=bundle.tenant.tenant_key,
        ok=all(gate.ok for gate in gates),
        gates=gates,
    )
