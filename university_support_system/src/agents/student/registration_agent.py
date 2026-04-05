"""Registration-focused student affairs agent."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence

from a2a.types import Task

from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.agents.student.registration_utils import (
    build_registration_intro,
    is_registration_timing_query,
    pick_preferred_registration_result,
    should_skip_registration_llm_synthesis,
)
from src.core.constants import Department, TaskType
from src.core.messages import CONTACT_SUGGESTION
from src.db.registration_data import RegistrationPeriodInfo, fetch_preferred_registration_period
from src.db.schemas import DepartmentResponse
from src.llm.prompt_templates import REGISTRATION_AGENT_SYSTEM_PROMPT


class RegistrationAgent(BaseSpecialistAgent):
    def __init__(
        self,
        *,
        period_fetcher: Callable[[], Awaitable[RegistrationPeriodInfo | None]] | None = None,
        **kwargs,
    ):
        super().__init__(
            AgentDefinition(
                agent_id="registration_agent",
                name="Registration Agent",
                department=Department.STUDENT_AFFAIRS,
                description="Kayit, muafiyet ve yatay gecis sureclerini yonetir.",
                task_types=(TaskType.REGISTRATION_QUERY, TaskType.PROCEDURE_QUERY),
                examples=("Ders kaydi ne zaman?", "Yatay gecis basvurusu nasil yapilir?"),
                tags=("student_affairs", "registration"),
                system_prompt=REGISTRATION_AGENT_SYSTEM_PROMPT,
            ),
            **kwargs,
        )
        self._period_fetcher = period_fetcher or fetch_preferred_registration_period

    async def handle_department_task(self, task: Task) -> DepartmentResponse:
        metadata = task.metadata or {}
        query_text = str(metadata.get("query_text", "")).strip()
        if not query_text:
            query_text = self._extract_query_from_task(task)

        if self._is_timing_query(query_text):
            period = await self._period_fetcher()
            if period is not None:
                start = period.start_date.strftime("%d.%m.%Y")
                end = period.end_date.strftime("%d.%m.%Y")
                if period.timing_status == "active":
                    message = (
                        f"Su anda {period.semester} donemi kayit sureci aktiftir "
                        f"({start} - {end})."
                    )
                elif period.timing_status == "upcoming":
                    message = (
                        f"Veritabanindaki en yakin kayit donemi {period.semester} icin "
                        f"{start} - {end} tarihleri arasinda planlanmistir."
                    )
                else:
                    message = (
                        f"Veritabanindaki son kayit donemi {period.semester} icin "
                        f"{start} - {end} tarihleri arasindaydi. "
                        "Yeni donem tarihi su anda ayrica tanimli degil."
                    )
                answer = f"{message}\n\n{CONTACT_SUGGESTION}"
                return DepartmentResponse(
                    department=self.department,
                    answer=answer,
                    db_data={
                        "semester": period.semester,
                        "start": start,
                        "end": end,
                        "timing_status": period.timing_status,
                    },
                    sources=[],
                    success=True,
                )
            return DepartmentResponse(
                department=self.department,
                answer=(
                    "Kayit donemi tarihleri su anda veritabaninda tanimli degil. "
                    "En guncel tarih bilgisi yayinlandiginda dogrudan paylasabilirim."
                    f"\n\n{CONTACT_SUGGESTION}"
                ),
                db_data={"registration_period_configured": False},
                sources=[],
                success=True,
            )

        return await super().handle_department_task(task)

    @staticmethod
    def _is_timing_query(query_text: str) -> bool:
        return is_registration_timing_query(query_text)

    def _should_skip_llm_synthesis(
        self,
        query_text: str,
        results: Sequence[dict],
        *,
        db_context: str | None = None,
    ) -> bool:
        return should_skip_registration_llm_synthesis(query_text, results)

    def _should_force_llm_synthesis(
        self,
        query_text: str,
        results: Sequence[dict],
        *,
        db_context: str | None = None,
    ) -> bool:
        return False

    def _build_source_only_answer(
        self,
        query_text: str,
        results: Sequence[dict],
        *,
        db_context: str | None = None,
    ) -> str:
        preferred = self._pick_preferred_result(query_text, results)
        if preferred is None:
            return super()._build_source_only_answer(query_text, results, db_context=db_context)

        content = self._compact_source_content(preferred.get("content", ""), max_len=280)
        source = preferred.get("source", "bilinmiyor")
        intro = build_registration_intro(query_text)
        prefix = f"{db_context}\n\n" if db_context else ""
        return f"{prefix}{intro}\n{content}\n\n(Kaynak: {source})"

    def _pick_preferred_result(self, query_text: str, results: Sequence[dict]) -> dict | None:
        return pick_preferred_registration_result(query_text, results)
