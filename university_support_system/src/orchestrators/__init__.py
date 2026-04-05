"""Lazy exports for orchestrator implementations."""

from __future__ import annotations

from typing import Any

__all__ = [
    "DepartmentOrchestrator",
    "build_student_affairs_orchestrator",
    "build_academic_programs_orchestrator",
    "build_finance_orchestrator",
    "MainOrchestrator",
]


def __getattr__(name: str) -> Any:
    if name in {
        "DepartmentOrchestrator",
        "build_student_affairs_orchestrator",
        "build_academic_programs_orchestrator",
        "build_finance_orchestrator",
    }:
        from src.orchestrators.department import (
            DepartmentOrchestrator,
            build_academic_programs_orchestrator,
            build_finance_orchestrator,
            build_student_affairs_orchestrator,
        )

        mapping = {
            "DepartmentOrchestrator": DepartmentOrchestrator,
            "build_student_affairs_orchestrator": build_student_affairs_orchestrator,
            "build_academic_programs_orchestrator": build_academic_programs_orchestrator,
            "build_finance_orchestrator": build_finance_orchestrator,
        }
        return mapping[name]

    if name == "MainOrchestrator":
        from src.orchestrators.main import MainOrchestrator

        return MainOrchestrator

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
