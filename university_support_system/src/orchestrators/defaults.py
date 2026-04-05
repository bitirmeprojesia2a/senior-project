"""Default orchestrator factory helpers."""

from __future__ import annotations

from src.agents.academic import CurriculumAgent, InternationalAgent, RegulationAgent
from src.agents.finance import ScholarshipAgent, TuitionAgent
from src.agents.student import (
    GraduationAgent,
    InternshipAgent,
    RegistrationAgent,
    StudentLifeAgent,
)
from src.db.telemetry import TelemetryService
from src.orchestrators.department_factories import (
    build_academic_programs_orchestrator,
    build_finance_orchestrator,
    build_student_affairs_orchestrator,
)


def build_default_orchestrators(telemetry_service: TelemetryService) -> dict:
    student_agents = [
        RegistrationAgent(),
        GraduationAgent(),
        InternshipAgent(),
        StudentLifeAgent(),
    ]
    academic_agents = [
        CurriculumAgent(),
        RegulationAgent(),
        InternationalAgent(),
    ]
    finance_agents = [
        TuitionAgent(),
        ScholarshipAgent(),
    ]
    student_orchestrator = build_student_affairs_orchestrator(
        student_agents,
        telemetry_service=telemetry_service,
    )
    academic_orchestrator = build_academic_programs_orchestrator(
        academic_agents,
        telemetry_service=telemetry_service,
    )
    finance_orchestrator = build_finance_orchestrator(
        finance_agents,
        telemetry_service=telemetry_service,
    )
    return {
        student_orchestrator.department: student_orchestrator,
        academic_orchestrator.department: academic_orchestrator,
        finance_orchestrator.department: finance_orchestrator,
    }
