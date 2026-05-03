"""Internship-focused student affairs agent."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence

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

    _SIMPLE_STAJ_FORM_MARKERS = (
        "zorunlu staj form",
        "staj form",
        "formunu nereden",
        "formu nereden",
        "nereden alirim",
        "nereden alırım",
    )
    _SIMPLE_STAJ_GRADUATION_MARKERS = (
        "staj yapmazsam",
        "staj yapmadan",
        "staji yapmazsam",
        "stajı yapmazsam",
    )

    _TEACHING_PROGRAM_MARKERS = (
        "ogretmenligi",
        "ogretmenlik",
        "egitim fakultesi",
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

        if self._is_teaching_program_specific_staj_query(query_text):
            return DepartmentResponse(
                department=self.department,
                answer=(
                    "Matematik ogretmenligi gibi ogretmenlik programlari icin staj/ogretmenlik uygulamasi "
                    "yukumlulugunu bu kaynaklarla bolum bazinda net dogrulayamiyorum. Bu nedenle muhendislik "
                    "staj belgelerine gore kesin hukum vermem dogru olmaz. En dogru belge ve surec icin "
                    "Egitim Fakultesi ilgili bolum sekreterligi veya akademik danismaninizla gorusun; varsa "
                    "ogretmenlik uygulamasi/staj formu birimin web sayfasi, bolum duyurulari veya OMU Kalem "
                    "formlari uzerinden paylasilir."
                ),
                sources=[],
                generation_mode="kural",
                include_contact_suggestion=True,
                success=True,
            )

        response = await super().handle_department_task(task)

        if response.success and self._needs_cross_reference(query_text):
            response = response.model_copy(
                update={
                    "answer": (
                        f"{response.answer}\n\n"
                        "Not: Staj ucreti geri odemesi veya mali detaylar icin "
                        "finans birimi (scholarship_agent) ile iletisime gecmeniz onerilir."
                    )
                }
            )

        return response

    @classmethod
    def _needs_cross_reference(cls, query_text: str) -> bool:
        lowered = normalize_text(query_text)
        return any(keyword in lowered for keyword in cls._CROSS_REF_KEYWORDS)

    @classmethod
    def _is_teaching_program_specific_staj_query(cls, query_text: str) -> bool:
        lowered = normalize_text(query_text)
        return "staj" in lowered and any(
            marker in lowered for marker in cls._TEACHING_PROGRAM_MARKERS
        )

    def _should_enrich_results(self, query_text: str, results: Sequence[dict]) -> bool:
        lowered = normalize_text(query_text)
        if any(marker in lowered for marker in self._SIMPLE_STAJ_FORM_MARKERS):
            return False
        if "mezun" in lowered and any(marker in lowered for marker in self._SIMPLE_STAJ_GRADUATION_MARKERS):
            return False
        return super()._should_enrich_results(query_text, results)
