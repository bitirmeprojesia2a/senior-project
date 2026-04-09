"""Scholarship-focused finance specialist agent."""

from __future__ import annotations

from typing import Awaitable, Callable

from a2a.types import Task

from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.core.constants import Department, TaskType
from src.core.text_normalization import normalize_text
from src.db.finance_data import (
    fetch_eligible_scholarships,
    fetch_student_scholarship_snapshot,
)
from src.db.schemas import DepartmentResponse
from src.llm.prompt_templates import SCHOLARSHIP_AGENT_SYSTEM_PROMPT


class ScholarshipAgent(BaseSpecialistAgent):
    """Handles scholarship programs and personal scholarship status."""

    _PERSONAL_KEYWORDS = (
        "basvurum", "durumum", "aliyor muyum", "yatti mi", "odendi mi", "bursum",
        "burs aliyorum", "burs durumu", "burs kesildimi", "ne zaman yatar",
    )

    def __init__(
        self,
        *,
        scholarship_fetcher: Callable[[int], Awaitable[dict | None]] | None = None,
        eligibility_fetcher: Callable[[float], Awaitable[list[dict]]] | None = None,
        **kwargs,
    ):
        super().__init__(
            AgentDefinition(
                agent_id="scholarship_agent",
                name="Scholarship Agent",
                department=Department.FINANCE,
                description="Burs ve ogrenci destek odakli finans sorularina bakar.",
                task_types=(TaskType.SCHOLARSHIP_QUERY,),
                examples=("Burs basvurusu ne zaman?", "Yemek bursu var mi?"),
                tags=("finance", "scholarship"),
                system_prompt=SCHOLARSHIP_AGENT_SYSTEM_PROMPT,
            ),
            **kwargs,
        )
        self._scholarship_fetcher = (
            scholarship_fetcher or fetch_student_scholarship_snapshot
        )
        self._eligibility_fetcher = eligibility_fetcher or fetch_eligible_scholarships

    async def handle_department_task(self, task: Task) -> DepartmentResponse:
        metadata = task.metadata or {}
        query_text = str(metadata.get("query_text", "")).strip()
        student_id = metadata.get("student_id")
        is_authenticated = bool(metadata.get("is_authenticated", False))

        if self._is_personal_query(query_text):
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
                        "Kisisel burs bilgilerin icin oturumda ogrenci numarasi gerekiyor. "
                        "Lutfen giris yapip tekrar deneyin."
                    ),
                    success=False,
                    error="student_id_required",
                )

            snapshot = await self._scholarship_fetcher(int(student_id))
            if snapshot is None:
                return DepartmentResponse(
                    department=self.department,
                    answer="Ogrenci kaydi bulunamadi.",
                    success=False,
                    error="student_not_found",
                )

            answer = self._format_scholarship_snapshot(snapshot)

            gpa = snapshot.get("gpa")
            if gpa is not None:
                eligible = await self._eligibility_fetcher(float(gpa))
                eligibility_note = self._format_eligible_scholarships(eligible)
                if eligibility_note:
                    answer += "\n\n" + eligibility_note

            return DepartmentResponse(
                department=self.department,
                answer=answer,
                db_data=snapshot,
                success=True,
            )

        return await super().handle_department_task(task)

    def _is_personal_query(self, query_text: str) -> bool:
        lowered = normalize_text(query_text)
        return any(keyword in lowered for keyword in self._PERSONAL_KEYWORDS)

    def _format_scholarship_snapshot(self, snapshot: dict) -> str:
        scholarship = snapshot.get("scholarship")
        latest_application = snapshot.get("latest_application")

        lines = [f"{snapshot['student_name']} icin burs ozeti:"]
        if scholarship is not None:
            status_tr = {"active": "aktif", "inactive": "pasif"}.get(
                scholarship["status"], scholarship["status"]
            )
            lines.append(
                f"- Aktif/son burs: {scholarship['program_name']} | Durum: {status_tr} | "
                f"Aylik tutar: {float(scholarship['monthly_amount'] or 0.0):.2f} TL"
            )
        else:
            lines.append("- Kayitli aktif burs bilgisi bulunamadi.")

        if latest_application is not None:
            app_status_tr = {
                "pending": "beklemede",
                "approved": "onaylandi",
                "rejected": "reddedildi",
            }.get(latest_application["status"], latest_application["status"])
            lines.append(
                f"- Son basvuru: {latest_application['program_name']} | "
                f"Durum: {app_status_tr} | Tarih: {latest_application['application_date']}"
            )

        if snapshot.get("gpa") is not None:
            lines.append(f"- Guncel GNO: {float(snapshot['gpa']):.2f}")

        return "\n".join(lines)

    @staticmethod
    def _format_eligible_scholarships(eligible: list[dict]) -> str:
        if not eligible:
            return ""
        lines = ["Basvurabilecegiz aktif burslar:"]
        for scholarship in eligible[:5]:
            amount = (
                f"{float(scholarship['monthly_amount'] or 0):.0f} TL/ay"
                if scholarship.get("monthly_amount")
                else ""
            )
            deadline = (
                f" | Son basvuru: {scholarship['deadline']}"
                if scholarship.get("deadline")
                else ""
            )
            lines.append(
                f"- {scholarship['name']} (min GNO: {scholarship.get('min_gpa', '-')}) {amount}{deadline}"
            )
        return "\n".join(lines)
