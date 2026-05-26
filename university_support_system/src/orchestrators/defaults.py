"""Default orchestrator factory helpers."""

from __future__ import annotations

from dataclasses import dataclass

from src.agents.academic import CurriculumAgent, InternationalAgent, RegulationAgent
from src.agents.finance import ScholarshipAgent, TuitionAgent
from src.agents.student import (
    GraduationAgent,
    InternshipAgent,
    RegistrationAgent,
    StudentLifeAgent,
)
from src.core.constants import Department
from src.db.telemetry import TelemetryService
from src.orchestrators.department_factories import (
    build_academic_programs_orchestrator,
    build_finance_orchestrator,
    build_student_affairs_orchestrator,
)


@dataclass(frozen=True)
class RemoteDepartmentTarget:
    """Lightweight target for HTTP-only A2A dispatch."""

    department: Department


def build_remote_department_targets() -> dict[Department, RemoteDepartmentTarget]:
    """Build remote-only targets without constructing local agents."""
    return {
        department: RemoteDepartmentTarget(department=department)
        for department in Department
    }


def build_department_orchestrator(department: Department, telemetry_service: TelemetryService):
    """Build only one department orchestrator for separated agent services."""
    if department.value == "student_affairs":
        return build_student_affairs_orchestrator(
            [
                RegistrationAgent(),
                GraduationAgent(),
                InternshipAgent(),
                StudentLifeAgent(),
            ],
            telemetry_service=telemetry_service,
        )
    if department.value == "academic_programs":
        return build_academic_programs_orchestrator(
            [
                CurriculumAgent(),
                RegulationAgent(),
                InternationalAgent(),
            ],
            telemetry_service=telemetry_service,
        )
    if department.value == "finance":
        return build_finance_orchestrator(
            [
                TuitionAgent(),
                ScholarshipAgent(),
            ],
            telemetry_service=telemetry_service,
        )
    raise ValueError(f"Unsupported department: {department!r}")


def build_specialist_agent(department: Department, agent_id: str):
    """Build one specialist agent by department and id for standalone services."""
    specialist_factories = {
        Department.STUDENT_AFFAIRS: {
            "registration_agent": RegistrationAgent,
            "graduation_agent": GraduationAgent,
            "internship_agent": InternshipAgent,
            "student_life_agent": StudentLifeAgent,
        },
        Department.ACADEMIC_PROGRAMS: {
            "curriculum_agent": CurriculumAgent,
            "regulation_agent": RegulationAgent,
            "international_agent": InternationalAgent,
        },
        Department.FINANCE: {
            "tuition_agent": TuitionAgent,
            "scholarship_agent": ScholarshipAgent,
        },
    }
    factory = specialist_factories.get(department, {}).get(agent_id)
    if factory is None:
        raise ValueError(
            f"Unsupported specialist agent for {department.value}: {agent_id}"
        )
    return factory()


def build_default_orchestrators(telemetry_service: TelemetryService) -> dict:
    student_orchestrator = build_department_orchestrator(Department.STUDENT_AFFAIRS, telemetry_service)
    academic_orchestrator = build_department_orchestrator(Department.ACADEMIC_PROGRAMS, telemetry_service)
    finance_orchestrator = build_department_orchestrator(Department.FINANCE, telemetry_service)
    return {
        student_orchestrator.department: student_orchestrator,
        academic_orchestrator.department: academic_orchestrator,
        finance_orchestrator.department: finance_orchestrator,
    }
