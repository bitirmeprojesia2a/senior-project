"""International and exchange-focused academic programs agent."""

from __future__ import annotations

from a2a.types import Task

from src.agents.academic.regulation_utils import needs_international_finance_reference
from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.core.constants import Department, TaskType
from src.db.schemas import DepartmentResponse
from src.llm.prompt_templates import INTERNATIONAL_AGENT_SYSTEM_PROMPT


class InternationalAgent(BaseSpecialistAgent):
    """Uluslararasi ogrenci uzman ajani. Harc sorularinda finance yonlendirmesi yapar."""

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
                system_prompt=INTERNATIONAL_AGENT_SYSTEM_PROMPT,
            ),
            **kwargs,
        )

    async def handle_department_task(self, task: Task) -> DepartmentResponse:
        response = await super().handle_department_task(task)

        metadata = task.metadata or {}
        query_text = str(metadata.get("query_text", "")).strip()

        if response.success and self._needs_finance_reference(query_text):
            response = response.model_copy(
                update={
                    "answer": response.answer
                    + (
                        "\n\nNot: Uluslararasi ogrenci harc ucretleri ve odeme detaylari icin "
                        "finans birimi (tuition_agent) ile iletisime gecmeniz onerilir."
                    )
                }
            )

        return response

    @staticmethod
    def _needs_finance_reference(query_text: str) -> bool:
        return needs_international_finance_reference(query_text)
