"""Offline secret readiness checks for dynamic tenant runtime experiments.

The checker may read an env file or mapping, but it never returns secret
values. It reports presence/emptiness/placeholder status so pilot gates can be
evaluated without leaking credentials into logs or package artifacts.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from src.dynamic_platform.models import DynamicPlatformBundle
from src.dynamic_platform.runtime_env_check import parse_env_file
from src.dynamic_platform.secrets_contract import build_tenant_secrets_contract

SECRET_READINESS_MODES = {
    "no_secret_smoke",
    "llm_answering",
    "a2a_runtime",
    "slack_socket_mode",
    "dynamic_pilot",
}

_LLM_KEYS = ("OPENAI_API_KEY", "GOOGLE_AI_API_KEY", "ANTHROPIC_API_KEY")
_A2A_KEYS = ("SERVER_INTERNAL_API_KEY", "A2A_INTERNAL_API_KEY", "A2A_REQUEST_SIGNATURE_SECRET")
_SLACK_KEYS = ("SLACK_BOT_TOKEN", "SLACK_SIGNING_SECRET", "SLACK_APP_TOKEN")
_PLACEHOLDER_VALUES = {
    "changeme",
    "change-me",
    "dummy",
    "example",
    "local-a2a-secret",
    "test",
    "todo",
    "your-api-key",
    "your-token",
}


@dataclass(frozen=True)
class SecretReadinessIssue:
    severity: str
    code: str
    message: str
    key: str | None = None
    group_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "key": self.key,
            "group_id": self.group_id,
        }


@dataclass(frozen=True)
class SecretKeyStatus:
    key: str
    category: str
    required: bool
    present: bool
    non_empty: bool
    placeholder: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "category": self.category,
            "required": self.required,
            "present": self.present,
            "non_empty": self.non_empty,
            "placeholder": self.placeholder,
            "value": "<redacted>" if self.present else None,
        }


@dataclass(frozen=True)
class SecretGroupStatus:
    group_id: str
    mode: str
    required: bool
    ok: bool
    keys: list[str]
    present_keys: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "group_id": self.group_id,
            "mode": self.mode,
            "required": self.required,
            "ok": self.ok,
            "keys": self.keys,
            "present_keys": self.present_keys,
        }


@dataclass(frozen=True)
class SecretReadinessReport:
    tenant_key: str
    runtime_strategy: str
    mode: str
    include_slack: bool
    env_source: str
    ok: bool
    key_statuses: list[SecretKeyStatus]
    group_statuses: list[SecretGroupStatus]
    errors: list[SecretReadinessIssue] = field(default_factory=list)
    warnings: list[SecretReadinessIssue] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "runtime_strategy": self.runtime_strategy,
            "mode": self.mode,
            "include_slack": self.include_slack,
            "env_source": self.env_source,
            "ok": self.ok,
            "key_statuses": [status.to_dict() for status in self.key_statuses],
            "group_statuses": [status.to_dict() for status in self.group_statuses],
            "errors": [issue.to_dict() for issue in self.errors],
            "warnings": [issue.to_dict() for issue in self.warnings],
            "notes": self.notes,
        }


def check_tenant_secret_readiness(
    bundle: DynamicPlatformBundle,
    *,
    mode: str = "no_secret_smoke",
    include_slack: bool = False,
    env_values: Mapping[str, str] | None = None,
    env_file: str | Path | None = None,
) -> SecretReadinessReport:
    if mode not in SECRET_READINESS_MODES:
        raise ValueError(f"Unsupported secret readiness mode: {mode}")
    if env_values is not None and env_file is not None:
        raise ValueError("Use either env_values or env_file, not both.")

    observed, env_source = _observed_env(env_values=env_values, env_file=env_file)
    contract = build_tenant_secrets_contract(bundle)
    required_groups = _required_groups(mode, include_slack=include_slack)
    required_keys = set().union(*required_groups) if required_groups else set()
    requirements = {item.key: item for item in contract.requirements}

    key_statuses = [
        _key_status(key, requirements[key].category, observed, required=key in required_keys)
        for key in sorted(requirements)
    ]
    key_status_by_key = {status.key: status for status in key_statuses}
    group_statuses = _group_statuses(mode, required_groups, key_status_by_key)
    errors: list[SecretReadinessIssue] = []
    warnings: list[SecretReadinessIssue] = []

    if env_file is not None:
        path_warning = _env_file_path_issue(Path(env_file), mode)
        if path_warning:
            (errors if path_warning.severity == "error" else warnings).append(path_warning)

    for group in group_statuses:
        if group.required and not group.ok:
            errors.append(
                SecretReadinessIssue(
                    severity="error",
                    code="secret_group_not_ready",
                    group_id=group.group_id,
                    message=f"{group.group_id} is required for mode {mode}, but required keys are not ready.",
                )
            )

    if mode == "no_secret_smoke":
        warnings.append(
            SecretReadinessIssue(
                severity="warning",
                code="no_secret_smoke_not_user_facing",
                message="No-secret smoke validates infrastructure only; user-facing LLM answers are not expected.",
            )
        )

    ok = not errors
    return SecretReadinessReport(
        tenant_key=bundle.tenant.tenant_key,
        runtime_strategy=bundle.tenant.runtime_strategy,
        mode=mode,
        include_slack=include_slack,
        env_source=env_source,
        ok=ok,
        key_statuses=key_statuses,
        group_statuses=group_statuses,
        errors=errors,
        warnings=warnings,
        notes=[
            "Secret readiness is offline and never returns secret values.",
            "Generated tenant.env is allowed to omit LLM/Slack secrets for no-secret smoke tests.",
            "Pilot/live modes must inject secrets from host env, a gitignored runtime env file, or a future secret manager.",
        ],
    )


def _observed_env(
    *,
    env_values: Mapping[str, str] | None,
    env_file: str | Path | None,
) -> tuple[dict[str, str], str]:
    if env_file is not None:
        return parse_env_file(env_file), str(env_file)
    if env_values is not None:
        return {str(key): str(value) for key, value in env_values.items()}, "provided_mapping"
    return dict(os.environ), "process_environment"


def _required_groups(mode: str, *, include_slack: bool) -> list[tuple[str, ...]]:
    if mode == "no_secret_smoke":
        return []
    if mode == "llm_answering":
        return [_LLM_KEYS]
    if mode == "a2a_runtime":
        return [_A2A_KEYS]
    if mode == "slack_socket_mode":
        return [_SLACK_KEYS]
    groups = [_LLM_KEYS, _A2A_KEYS]
    if include_slack:
        groups.append(_SLACK_KEYS)
    return groups


def _key_status(
    key: str,
    category: str,
    observed: Mapping[str, str],
    *,
    required: bool,
) -> SecretKeyStatus:
    value = observed.get(key)
    present = value is not None
    non_empty = bool(str(value).strip()) if value is not None else False
    return SecretKeyStatus(
        key=key,
        category=category,
        required=required,
        present=present,
        non_empty=non_empty,
        placeholder=_is_placeholder(value) if value is not None else False,
    )


def _group_statuses(
    mode: str,
    required_groups: list[tuple[str, ...]],
    key_status_by_key: dict[str, SecretKeyStatus],
) -> list[SecretGroupStatus]:
    groups = [
        ("llm_provider_key", "one_of", list(_LLM_KEYS)),
        ("a2a_internal_auth", "all", list(_A2A_KEYS)),
        ("slack_socket_mode", "all", list(_SLACK_KEYS)),
    ]
    required_sets = {tuple(group) for group in required_groups}
    statuses: list[SecretGroupStatus] = []
    for group_id, group_mode, keys in groups:
        required = tuple(keys) in required_sets
        ready_keys = [
            key
            for key in keys
            if (status := key_status_by_key[key]).present and status.non_empty and not status.placeholder
        ]
        if not required:
            ok = True
        elif group_mode == "one_of":
            ok = bool(ready_keys)
        else:
            ok = len(ready_keys) == len(keys)
        statuses.append(
            SecretGroupStatus(
                group_id=group_id,
                mode=group_mode,
                required=required,
                ok=ok,
                keys=keys,
                present_keys=ready_keys,
            )
        )
    return statuses


def _env_file_path_issue(env_file: Path, mode: str) -> SecretReadinessIssue | None:
    normalized = env_file.as_posix().lower()
    if "tmp/tenant_packages/" in normalized and mode != "no_secret_smoke":
        return SecretReadinessIssue(
            severity="error",
            code="secret_file_inside_tenant_package",
            message="Pilot/live secret files must stay outside generated tenant packages.",
        )
    if env_file.name in {"tenant.env", ".env"} and mode != "no_secret_smoke":
        return SecretReadinessIssue(
            severity="warning",
            code="sensitive_env_file_name",
            message="Use a separate gitignored runtime secret env file instead of tenant.env or production .env.",
        )
    return None


def _is_placeholder(value: str | None) -> bool:
    if value is None:
        return False
    normalized = value.strip().lower()
    if not normalized:
        return False
    if normalized in _PLACEHOLDER_VALUES:
        return True
    return normalized.startswith("your_") or normalized.startswith("your-") or "changeme" in normalized
