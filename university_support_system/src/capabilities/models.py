"""Shared models for capability planning and execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field


class CapabilityAction(BaseModel):
    """Planner output constrained to a whitelisted capability."""

    capability: str = "none"
    departments: list[str] = Field(default_factory=list)
    params: dict[str, Any] = Field(default_factory=dict)
    missing_params: list[str] = Field(default_factory=list)
    intent: str | None = None
    answer_contract: dict[str, Any] = Field(default_factory=dict)
    evidence_contract: dict[str, Any] = Field(default_factory=dict)
    fallback_route: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    fallback: str | None = None
    reasoning: str | None = None

    def is_none(self) -> bool:
        return self.capability.strip().lower() in {"", "none"}

    def to_plan_decision(self) -> "PlanDecision":
        return PlanDecision(
            intent=self.intent,
            capability=self.capability,
            departments=list(self.departments or []),
            params=dict(self.params or {}),
            missing_slots=list(self.missing_params or []),
            answer_contract=dict(self.answer_contract or {}),
            evidence_contract=dict(self.evidence_contract or {}),
            fallback_route=self.fallback_route or self.fallback,
            confidence=self.confidence,
            reasoning=self.reasoning,
        )


class PlanDecision(BaseModel):
    """Capability planner decision shared with routing, synthesis, and judge."""

    intent: str | None = None
    capability: str = "none"
    departments: list[str] = Field(default_factory=list)
    params: dict[str, Any] = Field(default_factory=dict)
    missing_slots: list[str] = Field(default_factory=list)
    answer_contract: dict[str, Any] = Field(default_factory=dict)
    evidence_contract: dict[str, Any] = Field(default_factory=dict)
    fallback_route: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning: str | None = None

    def is_none(self) -> bool:
        return self.capability.strip().lower() in {"", "none"}


@dataclass(frozen=True)
class CapabilitySpec:
    """Static capability definition used by the planner and validator."""

    name: str
    description: str
    executor: str
    departments: tuple[str, ...]
    capability_type: str = "deterministic"
    required_params: tuple[str, ...] = ()
    required_any: tuple[tuple[str, ...], ...] = ()
    optional_params: tuple[str, ...] = ()
    param_schemas: dict[str, dict[str, Any]] = field(default_factory=dict)
    returns: str = ""
    examples: tuple[str, ...] = ()


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    missing_params: tuple[str, ...] = ()
    error: str | None = None


class ExecutionResult(BaseModel):
    """Deterministic executor result sent to the agent synthesis layer."""

    success: bool
    capability: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)
    records: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    message: str | None = None
    error: str | None = None
    missing_params: list[str] = Field(default_factory=list)
    authoritative_no_records: bool = False
    fallback_allowed: bool = True
