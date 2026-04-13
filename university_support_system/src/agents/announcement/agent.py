"""Duyuru ajani."""

from __future__ import annotations

from typing import Awaitable, Callable

from a2a.types import Task

from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.core.constants import Department, TaskType
from src.db.announcements import AnnouncementRecord, fetch_relevant_announcements
from src.db.schemas import DepartmentResponse, RAGSource
from src.llm.prompt_templates import ANNOUNCEMENT_AGENT_SYSTEM_PROMPT


class AnnouncementAgent(BaseSpecialistAgent):
    """Aktif duyurulari veritabanindan okuyup kisa cevap ureten ajan."""

    def __init__(
        self,
        *,
        announcement_fetcher: Callable[..., Awaitable[list[AnnouncementRecord]]] | None = None,
        **kwargs,
    ):
        super().__init__(
            AgentDefinition(
                agent_id="announcement_agent",
                name="Announcement Agent",
                department=Department.STUDENT_AFFAIRS,
                description="Genel duyuru sorgulari icin veritabani destekli duyuru ajani.",
                task_types=(TaskType.PROCEDURE_QUERY,),
                examples=("Son duyurular neler?",),
                tags=("announcement", "shared"),
                system_prompt=ANNOUNCEMENT_AGENT_SYSTEM_PROMPT,
            ),
            **kwargs,
        )
        self._announcement_fetcher = announcement_fetcher or fetch_relevant_announcements

    async def handle_department_task(self, task: Task) -> DepartmentResponse:
        metadata = task.metadata or {}
        query_text = str(metadata.get("query_text", "")).strip()
        if not query_text:
            query_text = self._extract_query_from_task(task)

        announcements = await self._announcement_fetcher(
            query_text,
            department=self._resolve_department_filter(metadata),
            faculty=self._normalize_optional_text(metadata.get("faculty")),
            limit=3,
            allow_latest_fallback=bool(metadata.get("allow_latest_fallback", True)),
        )

        if not announcements:
            answer = (
                "Su anda sistemde kayitli aktif duyuru bulunmuyor. "
                "Duyuru verileri yuklendiginde en guncel duyurulari dogrudan listeleyebilirim."
            )
            sources: list[RAGSource] = []
        else:
            answer = self._format_announcements(announcements)
            sources = [self._build_source(item) for item in announcements]

        return DepartmentResponse(
            department=self.department,
            answer=answer,
            sources=sources,
            generation_mode="vt",
            success=True,
        )

    def _resolve_department_filter(self, metadata: dict) -> str | list[str] | None:
        department = self._normalize_optional_text(metadata.get("department"))
        if department:
            return department

        departments = metadata.get("departments")
        if isinstance(departments, (list, tuple)) and departments:
            resolved_departments = [
                normalized
                for normalized in (
                    self._normalize_optional_text(item) for item in departments
                )
                if normalized is not None
            ]
            if resolved_departments:
                return resolved_departments

        return None

    def _normalize_optional_text(self, value) -> str | None:
        text = str(value).strip() if value is not None else ""
        return text or None

    def _format_announcements(self, announcements: list[AnnouncementRecord]) -> str:
        lines = ["Ilgili duyurular:"]

        for index, item in enumerate(announcements, start=1):
            summary = (item.summary or item.original_text or "Ozet bilgisi bulunmuyor.").strip()
            if len(summary) > 280:
                summary = f"{summary[:277].rstrip()}..."

            published = ""
            if item.published_at is not None:
                published = f" ({item.published_at.date().isoformat()})"

            lines.append(f"{index}. {item.title}{published}")
            lines.append(f"   {summary}")
            if item.source_url:
                lines.append(f"   Detay: {item.source_url}")

        return "\n".join(lines)

    def _build_source(self, item: AnnouncementRecord) -> RAGSource:
        return RAGSource(
            content=item.summary or item.original_text or item.title,
            score=1.0,
            metadata={
                "record_type": "announcement",
                "announcement_id": item.id,
                "title": item.title,
                "source_url": item.source_url,
                "faculty": item.faculty,
                "department": item.department,
                "published_at": item.published_at.isoformat() if item.published_at else None,
            },
        )
