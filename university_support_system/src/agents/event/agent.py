"""Etkinlik ajani."""

from __future__ import annotations

from a2a.types import Task

from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.core.constants import Department, TaskType
from src.db.events import fetch_relevant_events
from src.db.schemas import DepartmentResponse
from src.orchestrators.event_utils import build_event_sources, format_event_answer


class EventAgent(BaseSpecialistAgent):
    """Etkinlik verisini agent sinirina tasiyan DB destekli ajan."""

    def __init__(self, **kwargs):
        super().__init__(
            AgentDefinition(
                agent_id="event_agent",
                name="Event Agent",
                department=Department.STUDENT_AFFAIRS,
                description="Etkinlik sorgulari icin veritabani destekli etkinlik ajani.",
                task_types=(TaskType.PROCEDURE_QUERY,),
                examples=("Bu hafta etkinlik var mi?",),
                tags=("event", "shared"),
                system_prompt="Etkinlik agenti veritabanindaki etkinlikleri listeler.",
            ),
            **kwargs,
        )

    async def handle_department_task(self, task: Task) -> DepartmentResponse:
        metadata = task.metadata or {}
        query_text = str(metadata.get("query_text", "")).strip() or self._extract_query_from_task(task)
        limit = int(metadata.get("limit", 5) or 5)
        events = await fetch_relevant_events(
            query_text,
            department=self._resolve_department_filter(metadata),
            faculty=self._normalize_optional_text(metadata.get("faculty")),
            unit_name=self._normalize_optional_text(metadata.get("unit_name")),
            limit=limit,
        )
        return DepartmentResponse(
            department=self.department,
            answer=format_event_answer(query=query_text, events=events),
            sources=build_event_sources(events),
            generation_mode="vt",
            success=True,
        )

    @staticmethod
    def _normalize_optional_text(value) -> str | None:
        text = str(value).strip() if value is not None else ""
        return text or None

    def _resolve_department_filter(self, metadata: dict) -> str | list[str] | None:
        department = self._normalize_optional_text(metadata.get("department"))
        if department:
            return department

        departments = metadata.get("departments")
        if isinstance(departments, (list, tuple)) and departments:
            resolved = [
                text
                for text in (
                    self._normalize_optional_text(item) for item in departments
                )
                if text is not None
            ]
            if resolved:
                return resolved

        return None
