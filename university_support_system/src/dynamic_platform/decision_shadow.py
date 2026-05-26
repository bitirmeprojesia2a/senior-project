"""Offline shadow checks for tenant decision contracts.

This module compares expected decision metadata from golden fixtures against a
dynamic tenant profile. It does not call routers, agents, retrieval, databases,
or LLMs. The purpose is to prove that a future dynamic runtime can represent the
same capability/agent/source-owner contracts before it is allowed near the live
path.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any

from src.dynamic_platform.models import DynamicPlatformBundle


@dataclass(frozen=True)
class ShadowDecisionCase:
    case_id: str
    query: str
    expected_capabilities: list[str]
    expected_agents: list[str] = field(default_factory=list)
    expected_specialists: list[str] = field(default_factory=list)
    expected_source_families: list[str] = field(default_factory=list)
    expected_source_owners: list[str] = field(default_factory=list)
    expected_authority_levels: list[str] = field(default_factory=list)
    expected_final_owner: str | None = None
    notes: str = ""

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ShadowDecisionCase":
        capabilities = payload.get("expected_capabilities")
        if capabilities is None:
            single_capability = payload.get("expected_capability")
            capabilities = [single_capability] if single_capability else []
        return cls(
            case_id=str(payload.get("id") or payload.get("case_id") or ""),
            query=str(payload.get("query") or ""),
            expected_capabilities=list(capabilities or []),
            expected_agents=list(payload.get("expected_agents") or []),
            expected_specialists=list(payload.get("expected_specialists") or []),
            expected_source_families=list(payload.get("expected_source_families") or []),
            expected_source_owners=list(payload.get("expected_source_owners") or []),
            expected_authority_levels=list(payload.get("expected_authority_levels") or []),
            expected_final_owner=payload.get("expected_final_owner"),
            notes=str(payload.get("notes") or ""),
        )


@dataclass(frozen=True)
class ShadowDecisionIssue:
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
class ShadowDecisionRecord:
    case_id: str
    query: str
    ok: bool = True
    expected_capabilities: list[str] = field(default_factory=list)
    dynamic_agents: list[str] = field(default_factory=list)
    dynamic_specialists: list[str] = field(default_factory=list)
    dynamic_source_families: list[str] = field(default_factory=list)
    dynamic_source_owners: list[str] = field(default_factory=list)
    dynamic_authority_levels: list[str] = field(default_factory=list)
    issues: list[ShadowDecisionIssue] = field(default_factory=list)

    def add_error(self, code: str, message: str) -> None:
        self.issues.append(ShadowDecisionIssue("error", code, message))
        self.ok = False

    def add_warning(self, code: str, message: str) -> None:
        self.issues.append(ShadowDecisionIssue("warning", code, message))

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "query": self.query,
            "ok": self.ok,
            "expected_capabilities": self.expected_capabilities,
            "dynamic_agents": self.dynamic_agents,
            "dynamic_specialists": self.dynamic_specialists,
            "dynamic_source_families": self.dynamic_source_families,
            "dynamic_source_owners": self.dynamic_source_owners,
            "dynamic_authority_levels": self.dynamic_authority_levels,
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclass
class ShadowDecisionReport:
    tenant_key: str
    fixture_path: str
    ok: bool
    records: list[ShadowDecisionRecord]

    def to_dict(self) -> dict[str, Any]:
        passed = sum(1 for record in self.records if record.ok)
        return {
            "tenant_key": self.tenant_key,
            "fixture_path": self.fixture_path,
            "ok": self.ok,
            "summary": {
                "case_count": len(self.records),
                "passed": passed,
                "failed": len(self.records) - passed,
            },
            "records": [record.to_dict() for record in self.records],
        }


def default_shadow_fixture_path(tenant_key: str) -> Path:
    return Path("tests/fixtures/dynamic_platform") / f"{tenant_key}_shadow_decisions.json"


def load_shadow_decision_cases(path: str | Path) -> list[ShadowDecisionCase]:
    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    raw_cases = payload.get("cases") if isinstance(payload, dict) else payload
    if not isinstance(raw_cases, list):
        raise ValueError("Shadow decision fixture must be a list or an object with a cases list.")
    return [ShadowDecisionCase.from_dict(item) for item in raw_cases]


def compare_shadow_decisions(
    bundle: DynamicPlatformBundle,
    cases: list[ShadowDecisionCase],
    *,
    fixture_path: str | Path,
) -> ShadowDecisionReport:
    records = [_compare_case(bundle, case) for case in cases]
    return ShadowDecisionReport(
        tenant_key=bundle.tenant.tenant_key,
        fixture_path=str(fixture_path),
        ok=all(record.ok for record in records),
        records=records,
    )


def _compare_case(bundle: DynamicPlatformBundle, case: ShadowDecisionCase) -> ShadowDecisionRecord:
    capability_ids = bundle.capability_ids()
    agents_by_capability = _agents_by_capability(bundle)
    specialists_by_capability = _specialists_by_capability(bundle)
    sources_by_capability = _sources_by_capability(bundle)

    dynamic_agents = _union_for(case.expected_capabilities, agents_by_capability)
    dynamic_specialists = _union_for(case.expected_capabilities, specialists_by_capability)
    dynamic_sources = [
        source
        for capability in case.expected_capabilities
        for source in sources_by_capability.get(capability, [])
    ]
    dynamic_source_families = sorted({source.source_family for source in dynamic_sources})
    dynamic_source_owners = sorted({source.owner_agent for source in dynamic_sources})
    dynamic_authority_levels = sorted({source.authority_level for source in dynamic_sources})

    record = ShadowDecisionRecord(
        case_id=case.case_id,
        query=case.query,
        expected_capabilities=list(case.expected_capabilities),
        dynamic_agents=dynamic_agents,
        dynamic_specialists=dynamic_specialists,
        dynamic_source_families=dynamic_source_families,
        dynamic_source_owners=dynamic_source_owners,
        dynamic_authority_levels=dynamic_authority_levels,
    )

    if not case.case_id:
        record.add_error("case_id_missing", "Shadow decision case has no id.")
    if not case.expected_capabilities:
        record.add_error("expected_capability_missing", f"Case {case.case_id} has no expected capability.")

    _check_subset(
        record,
        code="capability_missing",
        label="capability",
        expected=case.expected_capabilities,
        actual=sorted(capability_ids),
    )
    _check_subset(
        record,
        code="agent_not_represented",
        label="agent",
        expected=case.expected_agents,
        actual=dynamic_agents,
    )
    _check_subset(
        record,
        code="specialist_not_represented",
        label="specialist",
        expected=case.expected_specialists,
        actual=dynamic_specialists,
    )
    _check_subset(
        record,
        code="source_family_not_represented",
        label="source family",
        expected=case.expected_source_families,
        actual=dynamic_source_families,
    )
    _check_subset(
        record,
        code="source_owner_not_represented",
        label="source owner",
        expected=case.expected_source_owners,
        actual=dynamic_source_owners,
    )
    _check_subset(
        record,
        code="authority_level_not_represented",
        label="authority level",
        expected=case.expected_authority_levels,
        actual=dynamic_authority_levels,
    )
    if case.expected_final_owner and case.expected_final_owner not in dynamic_agents:
        record.add_error(
            "final_owner_not_represented",
            (
                f"Expected final owner {case.expected_final_owner} is not among dynamic agents "
                f"for capabilities {', '.join(case.expected_capabilities)}."
            ),
        )
    return record


def _agents_by_capability(bundle: DynamicPlatformBundle) -> dict[str, list[str]]:
    mapping: dict[str, set[str]] = {}
    for agent in bundle.agent_pack.agents:
        for capability in agent.capabilities:
            mapping.setdefault(capability, set()).add(agent.agent_id)
    return {key: sorted(value) for key, value in mapping.items()}


def _specialists_by_capability(bundle: DynamicPlatformBundle) -> dict[str, list[str]]:
    mapping: dict[str, set[str]] = {}
    for agent in bundle.agent_pack.agents:
        for specialist in agent.specialists:
            for capability in specialist.capabilities:
                mapping.setdefault(capability, set()).add(specialist.specialist_id)
    return {key: sorted(value) for key, value in mapping.items()}


def _sources_by_capability(bundle: DynamicPlatformBundle):
    mapping: dict[str, list[Any]] = {}
    for source in bundle.source_catalog.sources:
        if not source.enabled:
            continue
        for capability in source.capabilities:
            mapping.setdefault(capability, []).append(source)
    return mapping


def _union_for(capabilities: list[str], mapping: dict[str, list[str]]) -> list[str]:
    return sorted({item for capability in capabilities for item in mapping.get(capability, [])})


def _check_subset(
    record: ShadowDecisionRecord,
    *,
    code: str,
    label: str,
    expected: list[str],
    actual: list[str],
) -> None:
    missing = sorted(set(expected) - set(actual))
    if missing:
        record.add_error(
            code,
            f"Expected {label}(s) not represented in dynamic profile: {', '.join(missing)}.",
        )
