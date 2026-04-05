"""Graduation-focused student affairs agent."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from a2a.types import Task

from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.agents.student.graduation_utils import (
    format_academic_snapshot,
    is_graduation_hybrid_query,
    is_graduation_personal_query,
)
from src.core.constants import Department, TaskType
from src.core.messages import CONTACT_SUGGESTION
from src.db.schemas import DepartmentResponse, RAGSource
from src.db.student_academic_data import fetch_student_academic_snapshot
from src.llm.prompt_templates import GRADUATION_AGENT_SYSTEM_PROMPT


class GraduationAgent(BaseSpecialistAgent):
    def __init__(
        self,
        *,
        academic_fetcher: Callable[[int], Awaitable[dict | None]] | None = None,
        **kwargs,
    ):
        super().__init__(
            AgentDefinition(
                agent_id="graduation_agent",
                name="Graduation Agent",
                department=Department.STUDENT_AFFAIRS,
                description="Mezuniyet, diploma ve not odakli sorulari yanitlar.",
                task_types=(TaskType.ACADEMIC_QUERY, TaskType.COURSE_QUERY),
                examples=("Mezuniyet GNO sarti nedir?", "Transkript nasil alinir?"),
                tags=("student_affairs", "graduation"),
                system_prompt=GRADUATION_AGENT_SYSTEM_PROMPT,
            ),
            **kwargs,
        )
        self._academic_fetcher = academic_fetcher or fetch_student_academic_snapshot

    async def handle_department_task(self, task: Task) -> DepartmentResponse:
        metadata = task.metadata or {}
        query_text = str(metadata.get("query_text", "")).strip()
        student_id = metadata.get("student_id")
        is_authenticated = bool(metadata.get("is_authenticated", False))

        is_personal = self._is_personal_query(query_text)
        is_hybrid = self._is_hybrid_query(query_text)

        if is_personal or is_hybrid:
            if not is_authenticated:
                return DepartmentResponse(
                    department=self.department,
                    answer=(
                        "Kisisel sorunuza yanit verebilmem icin kimliginizi dogrulamam gerekiyor. "
                        "Dogrulamayi ogrenci e-posta adresinize gonderecegim tek kullanimlik kod ile tamamlayabilirsiniz."
                    ),
                    success=False,
                    error="authentication_required",
                )
            if student_id is None:
                return DepartmentResponse(
                    department=self.department,
                    answer=(
                        "Kisisel durumunuzu gosterebilmem icin oturumda ogrenci numarasi "
                        "gerekiyor. Lutfen giris yapip tekrar deneyin."
                    ),
                    success=False,
                    error="student_id_required",
                )

            snapshot = await self._academic_fetcher(int(student_id))
            if snapshot is None:
                return DepartmentResponse(
                    department=self.department,
                    answer="Ogrenci kaydi bulunamadi.",
                    success=False,
                    error="student_not_found",
                )

            if is_hybrid:
                return await self._handle_hybrid_query(query_text, snapshot)

            return DepartmentResponse(
                department=self.department,
                answer=self._format_academic_snapshot(snapshot),
                db_data=snapshot,
                success=True,
            )

        return await super().handle_department_task(task)

    async def _handle_hybrid_query(self, query_text: str, snapshot: dict) -> DepartmentResponse:
        retriever = self._get_retriever()
        results = retriever.search(query_text, department=self.department)
        db_summary = self._format_academic_snapshot(snapshot)

        answer = await self._generate_answer(
            query_text,
            results,
            db_context=db_summary,
            force_llm=True,
        )
        answer += CONTACT_SUGGESTION

        return DepartmentResponse(
            department=self.department,
            answer=answer,
            db_data=snapshot,
            sources=[
                RAGSource(
                    content=item.get("content", ""),
                    score=float(item.get("score", 0.0)),
                    metadata=item.get("metadata", {}),
                )
                for item in results
            ],
            success=True,
        )

    def _is_personal_query(self, query_text: str) -> bool:
        return is_graduation_personal_query(query_text)

    def _is_hybrid_query(self, query_text: str) -> bool:
        return is_graduation_hybrid_query(query_text)

    def _format_academic_snapshot(self, snapshot: dict) -> str:
        return format_academic_snapshot(snapshot)
