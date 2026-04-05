"""Factory helpers for department orchestrators."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from src.agents.base import BaseSpecialistAgent
from src.core.constants import Department, TaskType
from src.db.telemetry import TelemetryService

if TYPE_CHECKING:
    from src.orchestrators.department import DepartmentOrchestrator


def build_student_affairs_orchestrator(
    agents: Iterable[BaseSpecialistAgent],
    telemetry_service: TelemetryService | None = None,
) -> "DepartmentOrchestrator":
    from src.orchestrators.department import DepartmentOrchestrator

    by_id = {agent.agent_id: agent for agent in agents}
    return DepartmentOrchestrator(
        department=Department.STUDENT_AFFAIRS,
        agents={
            TaskType.REGISTRATION_QUERY: by_id["registration_agent"],
            TaskType.ACADEMIC_QUERY: by_id["graduation_agent"],
            TaskType.COURSE_QUERY: by_id["graduation_agent"],
            TaskType.PROCEDURE_QUERY: by_id["internship_agent"],
        },
        fallback_agent=by_id["student_life_agent"],
        keyword_routing={
            "kayit": "registration_agent",
            "kayit donemi": "registration_agent",
            "ders kaydi": "registration_agent",
            "akademik takvim": "registration_agent",
            "yatay": "registration_agent",
            "muafiyet": "registration_agent",
            "intibak": "registration_agent",
            "takvim": "registration_agent",
            "cap": "registration_agent",
            "cift anadal": "registration_agent",
            "cift ana dal": "registration_agent",
            "yandal": "registration_agent",
            "yan dal": "registration_agent",
            "mezuniyet": "graduation_agent",
            "gno": "graduation_agent",
            "transkript": "graduation_agent",
            "diploma": "graduation_agent",
            "yaz okulu": "graduation_agent",
            "bagil": "graduation_agent",
            "staj": "internship_agent",
            "bitirme": "internship_agent",
            "mup": "internship_agent",
            "sanayi": "internship_agent",
            "kimlik": "student_life_agent",
            "topluluk": "student_life_agent",
            "konukevi": "student_life_agent",
            "engelli": "student_life_agent",
            "konsey": "student_life_agent",
        },
        agents_by_id=by_id,
        telemetry_service=telemetry_service,
    )


def build_academic_programs_orchestrator(
    agents: Iterable[BaseSpecialistAgent],
    telemetry_service: TelemetryService | None = None,
) -> "DepartmentOrchestrator":
    from src.orchestrators.department import DepartmentOrchestrator

    by_id = {agent.agent_id: agent for agent in agents}
    return DepartmentOrchestrator(
        department=Department.ACADEMIC_PROGRAMS,
        agents={
            TaskType.COURSE_QUERY: by_id["curriculum_agent"],
            TaskType.PROCEDURE_QUERY: by_id["regulation_agent"],
        },
        fallback_agent=by_id["international_agent"],
        keyword_routing={
            "mufredat": "curriculum_agent",
            "ders": "curriculum_agent",
            "akts": "curriculum_agent",
            "cap": "curriculum_agent",
            "yandal": "curriculum_agent",
            "yan dal": "curriculum_agent",
            "onkosul": "curriculum_agent",
            "formasyon": "curriculum_agent",
            "yonetmelik": "regulation_agent",
            "yonerge": "regulation_agent",
            "politika": "regulation_agent",
            "prosedur": "regulation_agent",
            "genelge": "regulation_agent",
            "azami": "regulation_agent",
            "butunleme": "regulation_agent",
            "devam zorunlulugu": "regulation_agent",
            "not sistemi": "regulation_agent",
            "cift anadal": "regulation_agent",
            "cift ana dal": "regulation_agent",
            "erasmus": "international_agent",
            "uluslararasi": "international_agent",
            "yabanci": "international_agent",
            "ikamet": "international_agent",
            "denklik": "international_agent",
            "tomer": "international_agent",
            "yos": "international_agent",
            "kontenjan": "international_agent",
        },
        agents_by_id=by_id,
        telemetry_service=telemetry_service,
    )


def build_finance_orchestrator(
    agents: Iterable[BaseSpecialistAgent],
    telemetry_service: TelemetryService | None = None,
) -> "DepartmentOrchestrator":
    from src.orchestrators.department import DepartmentOrchestrator

    by_id = {agent.agent_id: agent for agent in agents}
    return DepartmentOrchestrator(
        department=Department.FINANCE,
        agents={
            TaskType.TUITION_QUERY: by_id["tuition_agent"],
            TaskType.PAYMENT_QUERY: by_id["tuition_agent"],
            TaskType.SCHOLARSHIP_QUERY: by_id["scholarship_agent"],
        },
        fallback_agent=by_id["tuition_agent"],
        keyword_routing={
            "harc": "tuition_agent",
            "odeme": "tuition_agent",
            "taksit": "tuition_agent",
            "dekont": "tuition_agent",
            "borc": "tuition_agent",
            "burs": "scholarship_agent",
            "yemek bursu": "scholarship_agent",
            "kismi zamanli": "scholarship_agent",
        },
        agents_by_id=by_id,
        telemetry_service=telemetry_service,
    )
