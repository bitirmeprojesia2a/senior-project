"""Capability planner primitives.

This package is intentionally feature-flagged from the orchestrator. Importing
it does not change routing or agent behavior by itself.
"""

from .models import CapabilityAction, ExecutionResult

__all__ = ["CapabilityAction", "ExecutionResult"]
