"""Offline tenant secret requirements for future dynamic runtime phases.

The contract deliberately records secret names and injection rules only. It
must never copy production `.env` values into generated tenant packages.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.dynamic_platform.models import DynamicPlatformBundle


@dataclass(frozen=True)
class SecretRequirement:
    key: str
    category: str
    purpose: str
    required_for: list[str]
    value_policy: str = "never_store_value_in_tenant_package"
    injection: str = "host_environment_or_gitignored_runtime_secret_env"

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "category": self.category,
            "purpose": self.purpose,
            "required_for": self.required_for,
            "value_policy": self.value_policy,
            "injection": self.injection,
        }


@dataclass(frozen=True)
class SecretGroup:
    group_id: str
    mode: str
    keys: list[str]
    required_for: list[str]
    note: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "group_id": self.group_id,
            "mode": self.mode,
            "keys": self.keys,
            "required_for": self.required_for,
            "note": self.note,
        }


@dataclass(frozen=True)
class TenantSecretsContract:
    tenant_key: str
    runtime_strategy: str
    secret_values_allowed_in_package: bool
    smoke_test_allowed_without_llm_secret: bool
    full_answering_requires_llm_secret: bool
    requirements: list[SecretRequirement]
    groups: list[SecretGroup]
    safe_injection_sources: list[str]
    forbidden_actions: list[str]
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_key": self.tenant_key,
            "runtime_strategy": self.runtime_strategy,
            "secret_values_allowed_in_package": self.secret_values_allowed_in_package,
            "smoke_test_allowed_without_llm_secret": self.smoke_test_allowed_without_llm_secret,
            "full_answering_requires_llm_secret": self.full_answering_requires_llm_secret,
            "requirements": [requirement.to_dict() for requirement in self.requirements],
            "groups": [group.to_dict() for group in self.groups],
            "safe_injection_sources": self.safe_injection_sources,
            "forbidden_actions": self.forbidden_actions,
            "notes": self.notes,
        }

    def to_example_env(self) -> str:
        lines = [
            "# Tenant runtime secrets example",
            "# Fill a separate local file only when a pilot/live test is explicitly approved.",
            "# Do not commit real values and do not merge this into tenant.env.",
            "",
        ]
        for requirement in self.requirements:
            lines.append(f"# {requirement.category}: {requirement.purpose}")
            lines.append(f"{requirement.key}=")
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"


def build_tenant_secrets_contract(bundle: DynamicPlatformBundle) -> TenantSecretsContract:
    requirements = [
        SecretRequirement(
            key="SERVER_INTERNAL_API_KEY",
            category="a2a_internal_auth",
            purpose="API and agent internal request authentication.",
            required_for=["a2a_http_runtime", "dynamic_pilot", "dynamic_on"],
        ),
        SecretRequirement(
            key="A2A_INTERNAL_API_KEY",
            category="a2a_internal_auth",
            purpose="Shared internal key used by A2A clients and services.",
            required_for=["a2a_http_runtime", "dynamic_pilot", "dynamic_on"],
        ),
        SecretRequirement(
            key="A2A_REQUEST_SIGNATURE_SECRET",
            category="a2a_internal_auth",
            purpose="Request signing secret when A2A signatures are enabled.",
            required_for=["signed_a2a_requests", "dynamic_pilot", "dynamic_on"],
        ),
        SecretRequirement(
            key="OPENAI_API_KEY",
            category="llm_provider",
            purpose="OpenAI-compatible primary provider key when selected.",
            required_for=["llm_answering", "dynamic_pilot", "dynamic_on"],
        ),
        SecretRequirement(
            key="GOOGLE_AI_API_KEY",
            category="llm_provider",
            purpose="Google AI fallback provider key when selected.",
            required_for=["llm_answering", "dynamic_pilot", "dynamic_on"],
        ),
        SecretRequirement(
            key="ANTHROPIC_API_KEY",
            category="llm_provider",
            purpose="Anthropic/Claude high-value provider key when hybrid profile is enabled.",
            required_for=["hybrid_quality", "dynamic_pilot", "dynamic_on"],
        ),
        SecretRequirement(
            key="SLACK_BOT_TOKEN",
            category="slack_socket_mode",
            purpose="Slack bot token for an approved tenant Slack app.",
            required_for=["tenant-slack-a2a", "manual-inprocess-slack"],
        ),
        SecretRequirement(
            key="SLACK_SIGNING_SECRET",
            category="slack_socket_mode",
            purpose="Slack request signing secret for an approved tenant Slack app.",
            required_for=["tenant-slack-a2a", "manual-inprocess-slack"],
        ),
        SecretRequirement(
            key="SLACK_APP_TOKEN",
            category="slack_socket_mode",
            purpose="Slack Socket Mode app token for an approved tenant Slack app.",
            required_for=["tenant-slack-a2a", "manual-inprocess-slack"],
        ),
    ]
    groups = [
        SecretGroup(
            group_id="llm_provider_key",
            mode="one_of",
            keys=["OPENAI_API_KEY", "GOOGLE_AI_API_KEY", "ANTHROPIC_API_KEY"],
            required_for=["user_facing_llm_answering", "dynamic_pilot", "dynamic_on"],
            note="At least one configured provider key is needed for full user-facing answers.",
        ),
        SecretGroup(
            group_id="a2a_internal_auth",
            mode="all_for_production",
            keys=["SERVER_INTERNAL_API_KEY", "A2A_INTERNAL_API_KEY", "A2A_REQUEST_SIGNATURE_SECRET"],
            required_for=["signed_a2a_http_runtime", "dynamic_pilot", "dynamic_on"],
            note="Local smoke tests may use safe defaults; pilot/live must provide explicit secrets.",
        ),
        SecretGroup(
            group_id="slack_socket_mode",
            mode="all_when_slack_profile_enabled",
            keys=["SLACK_BOT_TOKEN", "SLACK_SIGNING_SECRET", "SLACK_APP_TOKEN"],
            required_for=["tenant-slack-a2a", "manual-inprocess-slack"],
            note="No Slack profile should be enabled until a tenant-specific Slack app is configured.",
        ),
    ]
    return TenantSecretsContract(
        tenant_key=bundle.tenant.tenant_key,
        runtime_strategy=bundle.tenant.runtime_strategy,
        secret_values_allowed_in_package=False,
        smoke_test_allowed_without_llm_secret=True,
        full_answering_requires_llm_secret=True,
        requirements=requirements,
        groups=groups,
        safe_injection_sources=[
            "host environment variables supplied at launch time",
            "a gitignored runtime secret env file kept outside generated tenant packages",
            "future secret-manager adapter",
        ],
        forbidden_actions=[
            "copy production .env into tmp/tenant_packages/<tenant>/tenant.env",
            "commit real tenant secret values",
            "enable tenant Slack profile without a tenant-specific Slack app/token set",
            "treat API /health overall unhealthy from missing LLM key as infrastructure failure during no-secret smoke tests",
        ],
        notes=[
            "This contract is offline documentation and contains no secret values.",
            "Generated tenant.env remains safe for handoff and may intentionally omit LLM/Slack provider secrets.",
            "Full user-facing dynamic tenant answering needs an explicit approved secret injection step.",
        ],
    )
