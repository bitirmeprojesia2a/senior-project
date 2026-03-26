"""Öğrenci işleri departmanı ajanları - ders, kayıt, not."""

from src.agents.student.agents import (
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
]
