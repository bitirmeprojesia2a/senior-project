"""Finans uzman ajanlari."""

from __future__ import annotations

from typing import Awaitable, Callable

from a2a.types import Task

from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.core.constants import Department, TaskType
from src.db.personal_data import (
    fetch_student_scholarship_snapshot,
    fetch_student_tuition_snapshot,
)
from src.db.schemas import DepartmentResponse


class TuitionAgent(BaseSpecialistAgent):
    _PERSONAL_KEYWORDS = ("borc", "borcum", "odeme", "ödeme", "taksit", "dekont", "gecmisim", "geçmişim")

    def __init__(
        self,
        *,
        tuition_fetcher: Callable[[int], Awaitable[dict | None]] | None = None,
        **kwargs,
    ):
        super().__init__(
            AgentDefinition(
                agent_id="tuition_agent",
                name="Tuition Agent",
                department=Department.FINANCE,
                description="Harc, odeme ve taksit sorgularini yanitlar.",
                task_types=(TaskType.TUITION_QUERY, TaskType.PAYMENT_QUERY),
                examples=("Harc ucreti ne kadar?", "Odeme dekontumu nasil alirim?"),
                tags=("finance", "tuition"),
            ),
            **kwargs,
        )
        self._tuition_fetcher = tuition_fetcher or fetch_student_tuition_snapshot

    async def handle_task(self, task: Task) -> DepartmentResponse:
        metadata = task.metadata or {}
        query_text = str(metadata.get("query_text", "")).strip()
        student_id = metadata.get("student_id")
        is_authenticated = bool(metadata.get("is_authenticated", False))

        if student_id and self._is_personal_query(query_text):
            if not is_authenticated:
                return DepartmentResponse(
                    department=self.department,
                    answer=(
                        "Kisisel harc ve odeme bilgilerini paylasabilmem icin once kimligini "
                        "dogrulaman gerekiyor."
                    ),
                    success=False,
                    error="authentication_required",
                )

            snapshot = await self._tuition_fetcher(int(student_id))
            if snapshot is None:
                return DepartmentResponse(
                    department=self.department,
                    answer="Ogrenci kaydi bulunamadi.",
                    success=False,
                    error="student_not_found",
                )

            return DepartmentResponse(
                department=self.department,
                answer=self._format_tuition_snapshot(snapshot),
                db_data=snapshot,
                success=True,
            )

        return await super().handle_task(task)

    def _is_personal_query(self, query_text: str) -> bool:
        lowered = query_text.casefold()
        return any(keyword in lowered for keyword in self._PERSONAL_KEYWORDS)

    def _format_tuition_snapshot(self, snapshot: dict) -> str:
        tuition = snapshot.get("tuition")
        if tuition is None:
            return f"{snapshot['student_name']} icin kayitli harc verisi bulunamadi."

        debt_amount = float(tuition["debt_amount"] or 0.0)
        paid_amount = float(tuition["paid_amount"] or 0.0)
        total_amount = float(tuition["total_amount"] or 0.0)
        due_date = tuition.get("due_date") or "belirtilmemis"

        if debt_amount > 0:
            return (
                f"{snapshot['student_name']} icin {tuition['semester']} doneminde toplam "
                f"{total_amount:.2f} TL harc kaydi var. Su ana kadar {paid_amount:.2f} TL odeme alinmis "
                f"ve {debt_amount:.2f} TL borc gorunuyor. Son odeme tarihi: {due_date}."
            )

        return (
            f"{snapshot['student_name']} icin {tuition['semester']} donemine ait "
            f"{total_amount:.2f} TL tutarindaki harc kaydi odemeyle kapanmis gorunuyor. "
            f"Son odeme tarihi: {due_date}."
        )


class ScholarshipAgent(BaseSpecialistAgent):
    _PERSONAL_KEYWORDS = ("bursum", "basvurum", "başvurum", "durumum", "aliyor muyum", "alıyor muyum")

    def __init__(
        self,
        *,
        scholarship_fetcher: Callable[[int], Awaitable[dict | None]] | None = None,
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
            ),
            **kwargs,
        )
        self._scholarship_fetcher = scholarship_fetcher or fetch_student_scholarship_snapshot

    async def handle_task(self, task: Task) -> DepartmentResponse:
        metadata = task.metadata or {}
        query_text = str(metadata.get("query_text", "")).strip()
        student_id = metadata.get("student_id")
        is_authenticated = bool(metadata.get("is_authenticated", False))

        if student_id and self._is_personal_query(query_text):
            if not is_authenticated:
                return DepartmentResponse(
                    department=self.department,
                    answer=(
                        "Kisisel burs bilgilerini paylasabilmem icin once kimligini "
                        "dogrulaman gerekiyor."
                    ),
                    success=False,
                    error="authentication_required",
                )

            snapshot = await self._scholarship_fetcher(int(student_id))
            if snapshot is None:
                return DepartmentResponse(
                    department=self.department,
                    answer="Ogrenci kaydi bulunamadi.",
                    success=False,
                    error="student_not_found",
                )

            return DepartmentResponse(
                department=self.department,
                answer=self._format_scholarship_snapshot(snapshot),
                db_data=snapshot,
                success=True,
            )

        return await super().handle_task(task)

    def _is_personal_query(self, query_text: str) -> bool:
        lowered = query_text.casefold()
        return any(keyword in lowered for keyword in self._PERSONAL_KEYWORDS)

    def _format_scholarship_snapshot(self, snapshot: dict) -> str:
        scholarship = snapshot.get("scholarship")
        latest_application = snapshot.get("latest_application")

        lines = [f"{snapshot['student_name']} icin burs ozeti:"]
        if scholarship is not None:
            lines.append(
                f"- Aktif/son burs: {scholarship['program_name']} | Durum: {scholarship['status']} | "
                f"Aylik tutar: {float(scholarship['monthly_amount'] or 0.0):.2f} TL"
            )
        else:
            lines.append("- Kayitli aktif burs bilgisi bulunamadi.")

        if latest_application is not None:
            lines.append(
                f"- Son basvuru: {latest_application['program_name']} | "
                f"Durum: {latest_application['status']} | Tarih: {latest_application['application_date']}"
            )

        if snapshot.get("gpa") is not None:
            lines.append(f"- Guncel GNO: {float(snapshot['gpa']):.2f}")

        return "\n".join(lines)
