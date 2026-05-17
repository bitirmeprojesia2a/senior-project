"""Offline runtime environment checks for dynamic tenant profiles.

This module deliberately stays outside the live Slack/API/router path. It
compares a tenant profile with environment variables that would be passed to a
Docker/service launch, so profile mistakes can be caught before any runtime
adapter is wired.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from src.dynamic_platform.models import DynamicPlatformBundle
from src.dynamic_platform.runtime_plan import build_runtime_launch_plan


@dataclass(frozen=True)
class RuntimeEnvIssue:
    severity: str
    code: str
    message: str
    key: str | None = None
    expected: str | None = None
    actual: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "key": self.key,
            "expected": self.expected,
            "actual": self.actual,
        }


@dataclass(frozen=True)
class RuntimeEnvCheckReport:
    tenant_key: str
    env_source: str
    ok: bool
    expected_env: dict[str, str]
    observed_env: dict[str, str]
    errors: list[RuntimeEnvIssue] = field(default_factory=list)
    warnings: list[RuntimeEnvIssue] = field(default_factory=list)
    runtime_binding_status: str = ""
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "env_source": self.env_source,
            "ok": self.ok,
            "runtime_binding_status": self.runtime_binding_status,
            "expected_env": self.expected_env,
            "observed_env": self.observed_env,
            "errors": [issue.to_dict() for issue in self.errors],
            "warnings": [issue.to_dict() for issue in self.warnings],
            "notes": self.notes,
        }


def parse_env_file(path: str | Path) -> dict[str, str]:
    """Parse a simple dotenv file without interpolation or shell execution."""

    env_path = Path(path)
    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values[key] = value
    return values


def check_runtime_env(
    bundle: DynamicPlatformBundle,
    *,
    config_root: str | Path,
    env_values: Mapping[str, str] | None = None,
    env_file: str | Path | None = None,
    require_quality_gates: bool = True,
) -> RuntimeEnvCheckReport:
    if env_values is not None and env_file is not None:
        raise ValueError("Use either env_values or env_file, not both.")

    if env_file is not None:
        observed = parse_env_file(env_file)
        env_source = str(env_file)
    elif env_values is not None:
        observed = {str(key): str(value) for key, value in env_values.items()}
        env_source = "provided_mapping"
    else:
        observed = dict(os.environ)
        env_source = "process_environment"

    plan = build_runtime_launch_plan(
        bundle,
        config_root=config_root,
        require_quality_gates=require_quality_gates,
    )
    expected = plan.env
    relevant_observed = {
        key: observed[key]
        for key in sorted(observed)
        if key in expected or key.startswith("TENANT_") or key == "DYNAMIC_PLATFORM_RUNTIME"
    }

    errors: list[RuntimeEnvIssue] = []
    warnings: list[RuntimeEnvIssue] = []
    for key, expected_value in expected.items():
        actual_value = observed.get(key)
        if actual_value is None:
            errors.append(
                RuntimeEnvIssue(
                    severity="error",
                    code="missing_env_key",
                    key=key,
                    expected=expected_value,
                    message=f"{key} is required for tenant {bundle.tenant.tenant_key}.",
                )
            )
            continue
        if not _env_values_equal(key, expected_value, actual_value):
            errors.append(
                RuntimeEnvIssue(
                    severity="error",
                    code="env_value_mismatch",
                    key=key,
                    expected=expected_value,
                    actual=actual_value,
                    message=f"{key} does not match tenant profile {bundle.tenant.tenant_key}.",
                )
            )

    runtime_flag = observed.get("DYNAMIC_PLATFORM_RUNTIME")
    if runtime_flag and runtime_flag not in {"disabled", "shadow"}:
        errors.append(
            RuntimeEnvIssue(
                severity="error",
                code="live_dynamic_runtime_not_wired",
                key="DYNAMIC_PLATFORM_RUNTIME",
                expected=expected.get("DYNAMIC_PLATFORM_RUNTIME"),
                actual=runtime_flag,
                message="Live dynamic runtime is not wired yet; only disabled/shadow env modes are allowed.",
            )
        )

    if bundle.tenant.runtime_strategy in {"dynamic_pilot", "dynamic_on"}:
        errors.append(
            RuntimeEnvIssue(
                severity="error",
                code="runtime_adapter_not_wired",
                expected="dynamic_shadow or classic_protected",
                actual=bundle.tenant.runtime_strategy,
                message="Tenant requests pilot/on behavior, but the live dynamic runtime adapter is not wired yet.",
            )
        )

    for key in sorted(relevant_observed):
        if key.startswith("TENANT_") and key not in expected:
            warnings.append(
                RuntimeEnvIssue(
                    severity="warning",
                    code="unknown_tenant_env_key",
                    key=key,
                    actual=relevant_observed[key],
                    message=f"{key} is not used by the current dynamic tenant runtime contract.",
                )
            )

    notes = [
        "This check is offline and does not start or modify Slack/API/Docker services.",
        "Passing this check means the env file matches the tenant profile contract, not that live dynamic routing is enabled.",
    ]
    ok = not errors and plan.compose_env_ready
    if not plan.compose_env_ready:
        errors.append(
            RuntimeEnvIssue(
                severity="error",
                code="quality_gates_not_ready",
                message="Runtime plan quality gates are not ready for this tenant.",
            )
        )
        ok = False

    return RuntimeEnvCheckReport(
        tenant_key=bundle.tenant.tenant_key,
        env_source=env_source,
        ok=ok,
        expected_env=expected,
        observed_env=relevant_observed,
        errors=errors,
        warnings=warnings,
        runtime_binding_status=plan.runtime_binding_status,
        notes=notes,
    )


def _env_values_equal(key: str, expected: str, actual: str) -> bool:
    if key == "TENANT_CONFIG_ROOT":
        return _normalize_path_value(expected) == _normalize_path_value(actual)
    return expected == actual


def _normalize_path_value(value: str) -> str:
    return value.replace("\\", "/").rstrip("/")
