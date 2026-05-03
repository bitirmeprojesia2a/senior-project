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
            TaskType.PROCEDURE_QUERY: by_id["registration_agent"],
        },
        # Belirsiz ogrenci isleri sorularinda generic fallback yerine daha guclu
        # idari/prosedurel uzmana dusmek daha guvenli. Student life konulari
        # halen acik keyword eslesmeleriyle kendi ajanina yonlenir.
        fallback_agent=by_id["registration_agent"],
        keyword_routing={
            "kayit": "registration_agent",
            "kayit donemi": "registration_agent",
            "ders kaydi": "registration_agent",
            "akademik takvim": "registration_agent",
            "dondur": "registration_agent",
            "ilisik": "registration_agent",
            "ayril": "registration_agent",
            "birak": "registration_agent",
            "yatay": "registration_agent",
            "muafiyet": "registration_agent",
            "intibak": "registration_agent",
            "takvim": "registration_agent",
            "itiraz": "registration_agent",
            "maddi hata": "registration_agent",
            "kopya": "registration_agent",
            "disiplin": "registration_agent",
            "sorusturma": "registration_agent",
            "tutanak": "registration_agent",
            "notum sisteme": "registration_agent",
            "notlarim sisteme": "registration_agent",
            "not girmemis": "registration_agent",
            "not girilmemis": "registration_agent",
            "sisteme girmemis": "registration_agent",
            "sisteme girilmemis": "registration_agent",
            "cap": "registration_agent",
            "cift anadal": "registration_agent",
            "cift ana dal": "registration_agent",
            "yandal": "registration_agent",
            "yan dal": "registration_agent",
            "sikayet": "registration_agent",
            "hocami sikayet": "registration_agent",
            "hocam sikayet": "registration_agent",
            "ogretim elemani": "registration_agent",
            "akademik personel": "registration_agent",
            "etik": "registration_agent",
            "mezuniyet": "graduation_agent",
            "gano": "registration_agent",
            "gno": "registration_agent",
            "akts hakki": "registration_agent",
            "kredi siniri": "registration_agent",
            "ders yuku": "registration_agent",
            "transkript": "graduation_agent",
            "diploma": "graduation_agent",
            "yaz okulu": "registration_agent",
            "yaz donemi": "registration_agent",
            "yaz ogretimi": "registration_agent",
            "tek ders": "registration_agent",
            "butunleme": "registration_agent",
            "ek sinav": "registration_agent",
            "mazeret": "registration_agent",
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
            "onkosul": "curriculum_agent",
            # AKTS registration markerlari regulation_agent'a oncelikli
            "akts hakki": "regulation_agent",
            "kredi siniri": "regulation_agent",
            "ders yuku": "regulation_agent",
            "donem yuku": "regulation_agent",
            "azami akts": "regulation_agent",
            "azami kredi": "regulation_agent",
            "gano": "regulation_agent",
            "gno": "regulation_agent",
            "akts siniri": "regulation_agent",
            "kredi hakki": "regulation_agent",
            "donemlik akts": "regulation_agent",
            # Generic akts — müfredat sorulari icin (kac akts, ders akts vb.)
            "akts": "curriculum_agent",
            "cap": "regulation_agent",
            "yandal": "regulation_agent",
            "yan dal": "regulation_agent",
            "formasyon": "regulation_agent",
            "yonetmelik": "regulation_agent",
            "yonerge": "regulation_agent",
            "politika": "regulation_agent",
            "prosedur": "regulation_agent",
            "genelge": "regulation_agent",
            "butunleme": "regulation_agent",
            "ek sinav": "regulation_agent",
            "tek ders": "regulation_agent",
            "azami": "regulation_agent",
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
