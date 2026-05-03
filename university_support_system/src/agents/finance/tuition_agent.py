"""Tuition-focused finance specialist agent."""

from __future__ import annotations

from typing import Awaitable, Callable, Sequence

from a2a.types import Task

from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.agents.finance.tuition_utils import (
    build_catalog_fee_answer,
    build_honest_fee_fallback,
    build_structured_fee_answer,
    compact_source_content,
    display_unit_name,
    extract_requested_unit,
    extract_unit_fee_line,
    format_currency_tr,
    format_tuition_snapshot,
    infer_requested_student_type,
    is_personal_query,
    is_structured_fee_query,
    looks_like_fee_result,
    looks_like_tuition_table_source,
    needs_fee_context_clarification,
    normalize_finance_text,
    normalize_student_type,
    pick_preferred_result,
    source_type_mismatch_penalty,
)
from src.core.constants import Department, TaskType
from src.db.finance_data import (
    fetch_student_tuition_snapshot,
    fetch_tuition_fee_catalog_entry,
)
from src.db.schemas import DepartmentResponse
from src.llm.prompt_templates import TUITION_AGENT_SYSTEM_PROMPT


class TuitionAgent(BaseSpecialistAgent):
    """Handles tuition, debt, payment, and structured fee queries."""

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
                system_prompt=TUITION_AGENT_SYSTEM_PROMPT,
            ),
            **kwargs,
        )
        self._tuition_fetcher = tuition_fetcher or fetch_student_tuition_snapshot

    async def handle_department_task(self, task: Task) -> DepartmentResponse:
        metadata = task.metadata or {}
        query_text = str(metadata.get("query_text", "")).strip()
        student_id = metadata.get("student_id")
        is_authenticated = bool(metadata.get("is_authenticated", False))
        profile_student_type = normalize_student_type(metadata.get("student_type"))
        requested_student_type = infer_requested_student_type(query_text)
        student_type = requested_student_type or profile_student_type
        requested_unit = (
            extract_requested_unit(query_text)
            or str(metadata.get("student_faculty") or "").strip()
            or str(metadata.get("student_department") or "").strip()
        )

        if is_personal_query(query_text):
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
                        "Kisisel harc bilgilerin icin oturumda ogrenci numarasi gerekiyor. "
                        "Lutfen giris yapip tekrar deneyin."
                    ),
                    success=False,
                    error="student_id_required",
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

        if needs_fee_context_clarification(query_text, student_type, requested_unit):
            return DepartmentResponse(
                department=self.department,
                answer=(
                    "Ogrenim ucreti ogrenci turune ve birime gore degisiyor. "
                    "Dogru ucreti paylasabilmem icin Turk ogrenci misiniz, "
                    "uluslararasi ogrenci misiniz? Mumkunse fakulte veya bolum bilginizi de ekleyin."
                ),
                generation_mode="kural",
                success=False,
                error="student_type_context_required",
            )

        if is_structured_fee_query(query_text):
            requested_type = student_type or infer_requested_student_type(query_text)
            if requested_type and requested_unit:
                catalog_entry = await fetch_tuition_fee_catalog_entry(
                    student_type=requested_type,
                    unit_name=requested_unit,
                )
                if catalog_entry is not None:
                    return DepartmentResponse(
                        department=self.department,
                        answer=build_catalog_fee_answer(query_text, catalog_entry),
                        db_data=catalog_entry,
                        generation_mode="vt",
                        success=True,
                    )

        return await super().handle_department_task(task)

    def _is_personal_query(self, query_text: str) -> bool:
        return is_personal_query(query_text)

    def _is_structured_fee_query(self, query_text: str) -> bool:
        return is_structured_fee_query(query_text)

    def _build_source_only_answer(
        self,
        query_text: str,
        results: Sequence[dict],
        *,
        db_context: str | None = None,
    ) -> str:
        preferred = self._pick_preferred_result(query_text, results)
        if preferred is None:
            return super()._build_source_only_answer(
                query_text, results, db_context=db_context
            )

        structured = build_structured_fee_answer(
            query_text, preferred, db_context=db_context
        )
        if structured is not None:
            return structured
        honest = build_honest_fee_fallback(
            query_text, preferred, db_context=db_context
        )
        if honest is not None:
            return honest
        return super()._build_source_only_answer(
            query_text, results, db_context=db_context
        )

    def _pick_preferred_result(
        self, query_text: str, results: Sequence[dict]
    ) -> dict | None:
        return pick_preferred_result(query_text, results)

    def _needs_fee_context_clarification(
        self,
        query_text: str,
        student_type: str | None,
        requested_unit: str | None = None,
    ) -> bool:
        return needs_fee_context_clarification(
            query_text, student_type, requested_unit
        )

    def _build_structured_fee_answer(
        self,
        query_text: str,
        preferred: dict,
        *,
        db_context: str | None = None,
    ) -> str | None:
        return build_structured_fee_answer(
            query_text, preferred, db_context=db_context
        )

    def _build_catalog_fee_answer(self, query_text: str, catalog_entry: dict) -> str:
        return build_catalog_fee_answer(query_text, catalog_entry)

    @staticmethod
    def _format_currency_tr(amount: float | int | None) -> str:
        return format_currency_tr(amount)

    @staticmethod
    def _normalize_student_type(value: object) -> str | None:
        return normalize_student_type(value)

    def _infer_requested_student_type(self, query_text: str) -> str | None:
        return infer_requested_student_type(query_text)

    def _source_type_mismatch_penalty(
        self, item: dict, requested_type: str | None
    ) -> int:
        return source_type_mismatch_penalty(item, requested_type)

    @staticmethod
    def _looks_like_fee_result(item: dict) -> bool:
        return looks_like_fee_result(item)

    @classmethod
    def _looks_like_tuition_table_source(cls, item: dict) -> bool:
        _ = cls
        return looks_like_tuition_table_source(item)

    @classmethod
    def _normalize_text(cls, text: str) -> str:
        _ = cls
        return normalize_finance_text(text)

    @staticmethod
    def _compact_source_content(content: str, *, max_len: int | None = 260) -> str:
        return compact_source_content(content, max_len=max_len)

    def _extract_requested_unit(self, query_text: str) -> str | None:
        return extract_requested_unit(query_text)

    @staticmethod
    def _display_unit_name(unit: str) -> str:
        return display_unit_name(unit)

    def _extract_unit_fee_line(self, content: str, requested_unit: str) -> str | None:
        return extract_unit_fee_line(content, requested_unit)

    def _build_honest_fee_fallback(
        self,
        query_text: str,
        preferred: dict,
        *,
        db_context: str | None = None,
    ) -> str | None:
        return build_honest_fee_fallback(query_text, preferred, db_context=db_context)

    def _format_tuition_snapshot(self, snapshot: dict) -> str:
        return format_tuition_snapshot(snapshot)
