"""Student life support agent."""

from __future__ import annotations

from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.core.constants import Department, TaskType
from src.llm.prompt_templates import STUDENT_LIFE_AGENT_SYSTEM_PROMPT


class StudentLifeAgent(BaseSpecialistAgent):
    def __init__(self, **kwargs):
        super().__init__(
            AgentDefinition(
                agent_id="student_life_agent",
                name="Student Life Agent",
                department=Department.STUDENT_AFFAIRS,
                description="Ogrenci hayati, topluluklar ve genel destek sorularini yanitlar.",
                task_types=(TaskType.PROCEDURE_QUERY,),
                examples=("Kimlik karti nasil alinir?", "Ogrenci topluluguna nasil katilirim?"),
                tags=("student_affairs", "student_life"),
                system_prompt=STUDENT_LIFE_AGENT_SYSTEM_PROMPT,
            ),
            **kwargs,
        )
