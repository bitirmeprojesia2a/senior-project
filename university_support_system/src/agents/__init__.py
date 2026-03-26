"""Ajan modülü - tüm ajan implementasyonları."""

from src.agents.academic import CurriculumAgent, InternationalAgent, RegulationAgent
from src.agents.announcement import AnnouncementAgent
from src.agents.finance import ScholarshipAgent, TuitionAgent
from src.agents.student import (
    GraduationAgent,
    InternshipAgent,
    RegistrationAgent,
    StudentLifeAgent,
)

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
