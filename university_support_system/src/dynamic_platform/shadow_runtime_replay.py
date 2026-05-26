"""Replay shadow runtime decisions against tenant fixtures."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from src.dynamic_platform.decision_shadow import (
    ShadowDecisionCase,
    default_shadow_fixture_path,
    load_shadow_decision_cases,
)
from src.dynamic_platform.models import DynamicPlatformBundle
from src.dynamic_platform.shadow_runtime import build_shadow_runtime_decision

ReplayMatchMode = Literal["contract", "keyword"]


@dataclass(frozen=True)
class ShadowRuntimeReplayIssue:
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
class ShadowRuntimeReplayRecord:
    case_id: str
    query: str
    ok: bool
    expected_capabilities: list[str]
    selected_capabilities: list[str]
    agents: list[str]
    source_families: list[str]
    final_owner_candidates: list[str]
    confidence: float
    issues: list[ShadowRuntimeReplayIssue] = field(default_factory=list)

    def add_error(self, code: str, message: str) -> None:
        self.issues.append(ShadowRuntimeReplayIssue("error", code, message))
        self.ok = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "query": self.query,
            "ok": self.ok,
            "expected_capabilities": self.expected_capabilities,
            "selected_capabilities": self.selected_capabilities,
            "agents": self.agents,
            "source_families": self.source_families,
            "final_owner_candidates": self.final_owner_candidates,
            "confidence": self.confidence,
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclass(frozen=True)
class ShadowRuntimeReplayReport:
    tenant_key: str
    fixture_path: str
    match_mode: ReplayMatchMode
    runtime_binding_status: str
    ok: bool
    records: list[ShadowRuntimeReplayRecord]
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        passed = sum(1 for record in self.records if record.ok)
        return {
            "tenant_key": self.tenant_key,
            "fixture_path": self.fixture_path,
            "match_mode": self.match_mode,
            "runtime_binding_status": self.runtime_binding_status,
            "ok": self.ok,
            "summary": {
                "case_count": len(self.records),
                "passed": passed,
                "failed": len(self.records) - passed,
            },
            "records": [record.to_dict() for record in self.records],
            "notes": self.notes,
        }


def run_shadow_runtime_replay(
    bundle: DynamicPlatformBundle,
    *,
    fixture_path: str | Path | None = None,
    match_mode: ReplayMatchMode = "contract",
) -> ShadowRuntimeReplayReport:
    path = Path(fixture_path) if fixture_path else default_shadow_fixture_path(bundle.tenant.tenant_key)
    cases = load_shadow_decision_cases(path)
    records = [_replay_case(bundle, case, match_mode=match_mode) for case in cases]
    return ShadowRuntimeReplayReport(
        tenant_key=bundle.tenant.tenant_key,
        fixture_path=str(path),
        match_mode=match_mode,
        runtime_binding_status="shadow_only_runtime_not_wired",
        ok=all(record.ok for record in records),
        records=records,
        notes=[
            "Shadow runtime replay is offline and does not call live router, agents, retrieval, databases, Slack, or LLMs.",
            "contract mode uses fixture expected capabilities as explicit hints; keyword mode tests only the lightweight keyword matcher.",
        ],
    )


def _replay_case(
    bundle: DynamicPlatformBundle,
    case: ShadowDecisionCase,
    *,
    match_mode: ReplayMatchMode,
) -> ShadowRuntimeReplayRecord:
    requested = case.expected_capabilities if match_mode == "contract" else None
    decision = build_shadow_runtime_decision(
        bundle,
        query=case.query,
        requested_capabilities=requested,
    )
    payload = decision.to_dict()
    record = ShadowRuntimeReplayRecord(
        case_id=case.case_id,
        query=case.query,
        ok=True,
        expected_capabilities=case.expected_capabilities,
        selected_capabilities=payload["selected_capabilities"],
        agents=payload["agents"],
        source_families=payload["source_families"],
        final_owner_candidates=payload["final_owner_candidates"],
        confidence=payload["confidence"],
    )
    _check_subset(record, "capability_not_selected", "capability", case.expected_capabilities, payload["selected_capabilities"])
    _check_subset(record, "agent_not_selected", "agent", case.expected_agents, payload["agents"])
    _check_subset(record, "source_family_not_selected", "source family", case.expected_source_families, payload["source_families"])
    _check_subset(record, "source_owner_not_selected", "source owner", case.expected_source_owners, payload["source_owners"])
    _check_subset(record, "authority_level_not_selected", "authority level", case.expected_authority_levels, payload["authority_levels"])
    if case.expected_final_owner and case.expected_final_owner not in payload["final_owner_candidates"]:
        record.add_error(
            "final_owner_not_selected",
            f"Expected final owner {case.expected_final_owner} is not represented.",
        )
    return record


def _check_subset(
    record: ShadowRuntimeReplayRecord,
    code: str,
    label: str,
    expected: list[str],
    actual: list[str],
) -> None:
    missing = sorted(set(expected) - set(actual))
    if missing:
        record.add_error(code, f"Expected {label}(s) missing: {', '.join(missing)}.")
