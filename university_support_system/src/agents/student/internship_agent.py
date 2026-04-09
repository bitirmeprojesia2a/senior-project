"""Internship-focused student affairs agent."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from a2a.types import Task

from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.core.constants import Department, TaskType
from src.core.text_normalization import normalize_text
from src.db.schemas import DepartmentResponse
from src.db.student_academic_data import fetch_student_academic_snapshot
from src.llm.prompt_templates import INTERNSHIP_AGENT_SYSTEM_PROMPT


class InternshipAgent(BaseSpecialistAgent):
    _CROSS_REF_KEYWORDS = (
        "ucret", "ücret", "odeme", "ödeme", "geri odeme", "geri ödeme",
        "sigorta", "sgk", "staj ucreti", "staj ücreti",
    )

    def __init__(
        self,
        *,
        student_fetcher: Callable[[int], Awaitable[dict | None]] | None = None,
        **kwargs,
    ):
        super().__init__(
            AgentDefinition(
                agent_id="internship_agent",
                name="Internship Agent",
                department=Department.STUDENT_AFFAIRS,
                description="Staj, bitirme projesi ve uygulamali egitim sorularina bakar.",
                task_types=(TaskType.PROCEDURE_QUERY,),
                examples=("Staj basvurusu nasil yapilir?", "Bitirme projesi teslimi nasil olur?"),
                tags=("student_affairs", "internship"),
                system_prompt=INTERNSHIP_AGENT_SYSTEM_PROMPT,
            ),
            **kwargs,
        )
        self._student_fetcher = student_fetcher or fetch_student_academic_snapshot

    async def handle_department_task(self, task: Task) -> DepartmentResponse:
        metadata = task.metadata or {}
        query_text = str(metadata.get("query_text", "")).strip()
        if not query_text:
            query_text = self._extract_query_from_task(task)

        student_id = metadata.get("student_id")
        is_authenticated = bool(metadata.get("is_authenticated", False))

        dept_context = ""
        if student_id and is_authenticated:
            snapshot = await self._student_fetcher(int(student_id))
            if snapshot is not None:
                student_dept = snapshot.get("department")
                registration_status = snapshot.get("registration_status", "bilinmiyor")
                parts = []
                if student_dept:
                    parts.append(f"Ogrencinin bolumu: {student_dept}. ")
                parts.append(f"Kayit durumu: {registration_status}. ")
                dept_context = "".join(parts)

        response = await super().handle_department_task(task)

        if response.success:
            parts = []
            if dept_context:
                parts.append(dept_context)
            parts.append(response.answer)
            if self._needs_cross_reference(query_text):
                parts.append(
                    "\n\nNot: Staj ucreti geri odemesi veya mali detaylar icin "
                    "finans birimi (scholarship_agent) ile iletisime gecmeniz onerilir."
                )
            response = response.model_copy(update={"answer": "".join(parts)})

        return response

    @classmethod
    def _needs_cross_reference(cls, query_text: str) -> bool:
        lowered = normalize_text(query_text)
        return any(keyword in lowered for keyword in cls._CROSS_REF_KEYWORDS)
