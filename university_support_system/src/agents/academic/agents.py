"""Academic programs agent exports."""

from src.agents.academic.curriculum_agent import CurriculumAgent
from src.agents.academic.international_agent import InternationalAgent
from src.agents.academic.regulation_agent import RegulationAgent

__all__ = [
    "CurriculumAgent",
    "RegulationAgent",
    "InternationalAgent",
]
