"""Validate and execute whitelisted capability actions."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import ValidationError

from src.capabilities import (
    announcement_executor,
    calendar_executor,
    curriculum_executor,
    event_executor,
    finance_executor,
    policy_executor,
)
from src.capabilities.models import CapabilityAction, ExecutionResult
from src.capabilities.registry import CAPABILITY_REGISTRY, validate_capability_action

logger = logging.getLogger(__name__)

ExecutorFn = Callable[[dict[str, Any]], Awaitable[ExecutionResult]]


EXECUTOR_MAP: dict[str, ExecutorFn] = {
    "announcement.search": announcement_executor.search,
    "calendar.academic_date": calendar_executor.academic_date,
    "curriculum.course_exists_in_program": curriculum_executor.course_exists_in_program,
    "curriculum.course_detail": curriculum_executor.course_detail,
    "curriculum.course_prerequisites": curriculum_executor.course_prerequisites,
    "curriculum.semester_courses": curriculum_executor.semester_courses,
    "curriculum.weekly_program": curriculum_executor.weekly_program,
    "event.search": event_executor.search,
    "finance.tuition_fee": finance_executor.tuition_fee,
    "policy.international_lookup": policy_executor.international_lookup,
    "policy.student_affairs_lookup": policy_executor.student_affairs_lookup,
}


async def execute_capability_action(raw_action: dict[str, Any] | CapabilityAction) -> ExecutionResult:
    try:
        action = (
            raw_action
            if isinstance(raw_action, CapabilityAction)
            else CapabilityAction.model_validate(raw_action)
        )
    except ValidationError as exc:
        return ExecutionResult(
            success=False,
            error="invalid_action",
            metadata={"details": str(exc)},
            fallback_allowed=True,
        )

    if action.is_none():
        return ExecutionResult(
            success=False,
            capability="none",
            error="no_capability",
            fallback_allowed=True,
        )

    validation = validate_capability_action(action)
    if not validation.valid:
        return ExecutionResult(
            success=False,
            capability=action.capability,
            params=action.params,
            error=validation.error or "invalid_params",
            missing_params=list(validation.missing_params),
            fallback_allowed=validation.error != "missing_params",
        )

    spec = CAPABILITY_REGISTRY.get(action.capability)
    if spec is None:
        return ExecutionResult(
            success=False,
            capability=action.capability,
            params=action.params,
            error="unknown_capability",
            fallback_allowed=True,
        )

    executor_fn = EXECUTOR_MAP.get(spec.executor)
    if executor_fn is None:
        return ExecutionResult(
            success=False,
            capability=action.capability,
            params=action.params,
            error="executor_not_registered",
            fallback_allowed=True,
        )

    try:
        result = await executor_fn(dict(action.params))
    except Exception as exc:  # pragma: no cover - defensive fallback
        logger.exception("Capability executor failed: %s", action.capability)
        return ExecutionResult(
            success=False,
            capability=action.capability,
            params=action.params,
            error="executor_error",
            metadata={"details": str(exc)},
            fallback_allowed=True,
        )

    result.capability = result.capability or action.capability
    result.params = result.params or dict(action.params)
    return result
