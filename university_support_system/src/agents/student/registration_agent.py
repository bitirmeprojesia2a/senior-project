"""Registration-focused student affairs agent."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence

from a2a.types import Task

from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.agents.student.registration_utils import (
    build_general_exam_calendar_answer,
    build_registration_intro,
    preferred_registration_search_top_k,
    filter_registration_answer_results,
    is_course_registration_process_query,
    is_registration_timing_query,
    pick_preferred_registration_result,
    rank_registration_results,
    rank_course_registration_process_results,
    should_skip_registration_result_enrichment,
    should_reject_registration_source_only_result,
    should_force_registration_llm_synthesis,
)
from src.core.constants import Department, TaskType
from src.db.registration_data import RegistrationPeriodInfo, fetch_preferred_registration_period
from src.db.schemas import DepartmentResponse, RAGSource
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
                task_types=(TaskType.REGISTRATION_QUERY,),
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

        exam_calendar = build_general_exam_calendar_answer(query_text)
        if exam_calendar is not None:
            answer, calendar_data = exam_calendar
            return DepartmentResponse(
                department=self.department,
                answer=answer,
                db_data=calendar_data,
                generation_mode="vt",
                sources=[
                    RAGSource(
                        content=f"{calendar_data['label']}: {calendar_data['fall']} / {calendar_data['spring']}",
                        score=1.0,
                        metadata={
                            "source": "2025_2026_genel_akademik_takvim.pdf",
                            "record_type": "academic_calendar",
                        },
                    )
                ],
                include_contact_suggestion=True,
                success=True,
            )

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
                return DepartmentResponse(
                    department=self.department,
                    answer=message,
                    db_data={
                        "semester": period.semester,
                        "start": start,
                        "end": end,
                        "timing_status": period.timing_status,
                    },
                    sources=[],
                    include_contact_suggestion=True,
                    success=True,
                )
            return DepartmentResponse(
                department=self.department,
                answer=(
                    "Kayıt dönemi tarihleri şu anda veritabanında tanımlı değil. "
                    "En güncel tarih bilgisi yayımlandığında doğrudan paylaşabilirim."
                ),
                db_data={"registration_period_configured": False},
                sources=[],
                include_contact_suggestion=True,
                success=True,
            )

        return await super().handle_department_task(task)

    @staticmethod
    def _is_timing_query(query_text: str) -> bool:
        return is_registration_timing_query(query_text)

    def _should_force_llm_synthesis(
        self,
        query_text: str,
        results: Sequence[dict],
        *,
        db_context: str | None = None,
    ) -> bool:
        if should_force_registration_llm_synthesis(query_text, results):
            return True
        return super()._should_force_llm_synthesis(
            query_text,
            results,
            db_context=db_context,
        )

    def _should_use_llm_evidence_selection(
        self,
        query_text: str,
        evidence_items: Sequence,
        *,
        force_llm: bool,
        db_context: str | None = None,
    ) -> bool:
        if is_course_registration_process_query(query_text):
            return False
        return super()._should_use_llm_evidence_selection(
            query_text,
            evidence_items,
            force_llm=force_llm,
            db_context=db_context,
        )

    def _should_enrich_results(self, query_text: str, results: Sequence[dict]) -> bool:
        if should_skip_registration_result_enrichment(query_text):
            return False
        return super()._should_enrich_results(query_text, results)

    def _llm_synthesis_timeout_seconds(
        self,
        query_text: str,
        results: Sequence[dict],
        *,
        llm_profile: str | None = None,
    ) -> float:
        if should_skip_registration_result_enrichment(query_text):
            return 4.0
        return super()._llm_synthesis_timeout_seconds(
            query_text,
            results,
            llm_profile=llm_profile,
        )

    def _filter_results_for_answer(
        self,
        query_text: str,
        results: Sequence[dict],
    ) -> list[dict]:
        filtered_results = filter_registration_answer_results(query_text, results)
        if is_course_registration_process_query(query_text):
            return rank_course_registration_process_results(
                filtered_results,
                query_text=query_text,
            )[:5]
        return rank_registration_results(
            filtered_results,
            query_text=query_text,
        )[:8]

    def _search_top_k(self, query_text: str, metadata: dict) -> int | None:
        _ = metadata
        return preferred_registration_search_top_k(query_text)

    def _build_source_only_answer(
        self,
        query_text: str,
        results: Sequence[dict],
        *,
        db_context: str | None = None,
    ) -> str:
        if is_course_registration_process_query(query_text):
            prefix = f"{db_context}\n\n" if db_context else ""
            return (
                prefix
                + "Ders kaydınızı akademik takvimde belirtilen süre içinde "
                "ubys.omu.edu.tr adresinden/öğrenci bilgi sistemi üzerinden yapabilirsiniz. "
                "Kayıt öncesinde müfredat durumunuzu kontrol edin; ders seçimini tamamladıktan sonra "
                "danışman onayına gönderin. Danışman onayı olmayan ders kayıtları geçersizdir.\n\n"
                "(Kaynak: sık_sorulan_sorular.txt)"
            )

        preferred = self._pick_preferred_result(query_text, results)
        if preferred is None:
            return super()._build_source_only_answer(query_text, results, db_context=db_context)
        if should_reject_registration_source_only_result(query_text, preferred):
            safer_results = [
                item
                for item in results
                if not should_reject_registration_source_only_result(query_text, item)
            ]
            if safer_results:
                preferred = self._pick_preferred_result(query_text, safer_results)
            else:
                prefix = f"{db_context}\n\n" if db_context else ""
                return (
                    prefix
                    + "Bu konuda öğrenci işleri kaynaklarında doğrudan teyit edebildiğim net bir cevap bulamadım. "
                    "Soruyu biraz daha açık sorarsan zaman, belge veya koşul bilgisini daha doğru daraltabilirim."
                )

        content = self._compact_source_content(preferred.get("content", ""), max_len=None)
        source = preferred.get("source", "bilinmiyor")
        intro = build_registration_intro(query_text)
        prefix = f"{db_context}\n\n" if db_context else ""
        return f"{prefix}{intro}\n{content}\n\n(Kaynak: {source})"

    def _pick_preferred_result(self, query_text: str, results: Sequence[dict]) -> dict | None:
        return pick_preferred_registration_result(query_text, results)
