"""Lazy exports for agent implementations."""

from __future__ import annotations

from typing import Any

__all__ = [
    "RegistrationAgent",
    "GraduationAgent",
    "InternshipAgent",
    "StudentLifeAgent",
    "CurriculumAgent",
    "RegulationAgent",
    "InternationalAgent",
    "TuitionAgent",
    "ScholarshipAgent",
    "AnnouncementAgent",
]


def __getattr__(name: str) -> Any:
    if name in {"RegistrationAgent", "GraduationAgent", "InternshipAgent", "StudentLifeAgent"}:
        from src.agents.student import (
            GraduationAgent,
            InternshipAgent,
            RegistrationAgent,
            StudentLifeAgent,
        )

        mapping = {
            "RegistrationAgent": RegistrationAgent,
            "GraduationAgent": GraduationAgent,
            "InternshipAgent": InternshipAgent,
            "StudentLifeAgent": StudentLifeAgent,
        }
        return mapping[name]

    if name in {"CurriculumAgent", "RegulationAgent", "InternationalAgent"}:
        from src.agents.academic import (
            CurriculumAgent,
            InternationalAgent,
            RegulationAgent,
        )

        mapping = {
            "CurriculumAgent": CurriculumAgent,
            "RegulationAgent": RegulationAgent,
            "InternationalAgent": InternationalAgent,
        }
        return mapping[name]

    if name in {"TuitionAgent", "ScholarshipAgent"}:
        from src.agents.finance import ScholarshipAgent, TuitionAgent

        mapping = {
            "TuitionAgent": TuitionAgent,
            "ScholarshipAgent": ScholarshipAgent,
        }
        return mapping[name]

    if name == "AnnouncementAgent":
        from src.agents.announcement import AnnouncementAgent

        return AnnouncementAgent

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
