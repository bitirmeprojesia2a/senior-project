"""Akademik programlar uzman ajanları."""

from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.core.constants import Department, TaskType


class CurriculumAgent(BaseSpecialistAgent):
    def __init__(self, **kwargs):
        super().__init__(
            AgentDefinition(
                agent_id="curriculum_agent",
                name="Curriculum Agent",
                department=Department.ACADEMIC_PROGRAMS,
                description="Mufredat, ders planlari ve onkosul sorularini ele alir.",
                task_types=(TaskType.COURSE_QUERY,),
                examples=("Mufredat nerede?", "Bu donem hangi dersler acik?"),
                tags=("academic_programs", "curriculum"),
            ),
            **kwargs,
        )


class RegulationAgent(BaseSpecialistAgent):
    def __init__(self, **kwargs):
        super().__init__(
            AgentDefinition(
                agent_id="regulation_agent",
                name="Regulation Agent",
                department=Department.ACADEMIC_PROGRAMS,
                description="Yonerge, yonetmelik ve mevzuat sorularini yanitlar.",
                task_types=(TaskType.PROCEDURE_QUERY,),
                examples=("Yonetmelik nerede?", "Ozel ogrenci yonergesi nedir?"),
                tags=("academic_programs", "regulation"),
            ),
            **kwargs,
        )


class InternationalAgent(BaseSpecialistAgent):
    def __init__(self, **kwargs):
        super().__init__(
            AgentDefinition(
                agent_id="international_agent",
                name="International Agent",
                department=Department.ACADEMIC_PROGRAMS,
                description="Uluslararasi ogrenci ve Erasmus odakli sorulara bakar.",
                task_types=(TaskType.PROCEDURE_QUERY,),
                examples=("Erasmus basvurusu nasil yapilir?", "Ikamet izni icin ne gerekir?"),
                tags=("academic_programs", "international"),
            ),
            **kwargs,
        )
