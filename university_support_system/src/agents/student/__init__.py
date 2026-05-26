"""Student affairs agent exports."""

from src.agents.student.graduation_agent import GraduationAgent
from src.agents.student.internship_agent import InternshipAgent
from src.agents.student.registration_agent import RegistrationAgent
from src.agents.student.student_life_agent import StudentLifeAgent

__all__ = [
    "RegistrationAgent",
    "GraduationAgent",
    "InternshipAgent",
    "StudentLifeAgent",
]
