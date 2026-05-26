"""Graduation-focused student affairs agent."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from a2a.types import Task

from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.agents.student.graduation_utils import (
    format_academic_snapshot,
    is_general_akts_rule_query,
    is_graduation_akts_total_query,
    is_graduation_hybrid_query,
    is_graduation_personal_query,
)
from src.core.contract_answer_policy import (
    build_graduation_akts_answer_plan,
    render_contract_answer_plan,
)
from src.core.constants import Department, TaskType
from src.db.curriculum_data import fetch_program_akts_summary
from src.db.schemas import DepartmentResponse, RAGSource
from src.db.student_academic_data import fetch_student_academic_snapshot
from src.llm.prompt_templates import GRADUATION_AGENT_SYSTEM_PROMPT


class GraduationAgent(BaseSpecialistAgent):
    def __init__(
        self,
        *,
        academic_fetcher: Callable[[int], Awaitable[dict | None]] | None = None,
        curriculum_fetcher: Callable[[str], Awaitable[dict | None]] | None = None,
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
        self._curriculum_fetcher = curriculum_fetcher or fetch_program_akts_summary

    async def handle_department_task(self, task: Task) -> DepartmentResponse:
        metadata = task.metadata or {}
        query_text = str(metadata.get("query_text", "")).strip()
        student_id = metadata.get("student_id")
        is_authenticated = bool(metadata.get("is_authenticated", False))
        student_department = str(metadata.get("student_department", "") or "").strip()

        policy_facet = metadata.get("policy_facet")
        facet_name = ""
        if isinstance(policy_facet, dict):
            facet_name = str(policy_facet.get("facet") or policy_facet.get("policy_facet") or "")
        if self._is_general_akts_rule_query(query_text) or is_graduation_akts_total_query(
            query_text,
            policy_facet=facet_name,
        ):
            plan = build_graduation_akts_answer_plan(
                query=query_text,
                student_department=student_department,
            )
            answer = render_contract_answer_plan(plan)
            if answer is not None and plan.answer_status in {
                "verified_level_rule",
                "missing_verified_program_requirement",
            }:
                total = plan.facts.get("verified_total_akts")
                response_metadata = {
                    "policy_facet": "graduation_akts",
                    "source_contract": (
                        "education_level_graduation_rule"
                        if total is not None
                        else "level_rule_requires_program_specific_verification"
                    ),
                    "program_level": plan.facts.get("program_level") or {},
                    "contract_answer_plan": plan.to_metadata(),
                }
                if total is not None:
                    response_metadata["authoritative_total_akts"] = total
                if isinstance(metadata.get("answer_contract"), dict):
                    response_metadata["answer_contract"] = metadata["answer_contract"]
                source_content = answer
                source_name = (
                    "education_level_graduation_rule"
                    if total is not None
                    else "program_specific_graduation_requirement_check"
                )
                return DepartmentResponse(
                    department=self.department,
                    answer=answer,
                    db_data={
                        "education_level": plan.facts.get("education_level"),
                        "graduation_akts": total,
                    },
                    generation_mode="kural",
                    sources=[
                        RAGSource(
                            content=source_content,
                            score=1.0,
                            metadata={
                                "source": source_name,
                                "record_type": "contract_answer_plan",
                            },
                        )
                    ],
                    success=True,
                    metadata=response_metadata,
                )

        is_personal = self._is_personal_query(query_text)
        is_hybrid = self._is_hybrid_query(query_text)

        if is_personal or is_hybrid:
            if not is_authenticated:
                return DepartmentResponse(
                    department=self.department,
                    answer=(
                        "Kişisel sorunuza yanıt verebilmem için kimliğinizi doğrulamam gerekiyor. "
                        "Doğrulamayı öğrenci e-posta adresinize göndereceğim tek kullanımlık kod ile tamamlayabilirsiniz."
                    ),
                    success=False,
                    error="authentication_required",
                )
            if student_id is None:
                return DepartmentResponse(
                    department=self.department,
                    answer=(
                        "Kişisel durumunuzu gösterebilmem için oturumda öğrenci numarası "
                        "gerekiyor. Lütfen giriş yapıp tekrar deneyin."
                    ),
                    success=False,
                    error="student_id_required",
                )

            snapshot = await self._academic_fetcher(int(student_id))
            if snapshot is None:
                return DepartmentResponse(
                    department=self.department,
                    answer="Öğrenci kaydı bulunamadı.",
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

    def _build_program_akts_response(self, summary: dict) -> DepartmentResponse:
        total_akts = int(summary.get("total_akts", 0))
        department = summary.get("department") or "Bu program"
        semester_totals = summary.get("semester_totals") or {}
        semester_summary = ", ".join(
            f"{semester}. yariyil: {akts} AKTS"
            for semester, akts in semester_totals.items()
        )

        answer_lines = [
            (
                f"{department} programinda mezuniyet icin baz mufredat yukumlulugu "
                f"toplam {total_akts} AKTS'dir."
            ),
            (
                "Yariyil dagilimi: "
                f"{semester_summary}."
            ),
            (
                "Bu toplam, standart mezuniyet planini temel alir; ozel uygulama "
                "kalemleri ayri izlendiginden hesaplamaya ayrica dahil edilmemistir."
            ),
        ]

        return DepartmentResponse(
            department=self.department,
            answer="\n\n".join(answer_lines),
            db_data=summary,
            generation_mode="vt",
            include_contact_suggestion=True,
            success=True,
        )

    def _build_level_akts_response(
        self,
        *,
        level: str,
        program_level: dict | None = None,
        answer_contract: dict | None = None,
    ) -> DepartmentResponse:
        if level == "associate":
            answer = "Ön lisans programından mezun olmak için toplam 120 AKTS tamamlanmalıdır."
            total = 120
        else:
            answer = (
                "Normal dört yıllık lisans programından mezun olmak için toplam "
                "240 AKTS tamamlanmalıdır."
            )
            total = 240
        response_metadata = {
            "policy_facet": "graduation_akts",
            "source_contract": "education_level_graduation_rule",
            "authoritative_total_akts": total,
            "program_level": program_level or {"education_level": level},
        }
        if isinstance(answer_contract, dict):
            response_metadata["answer_contract"] = answer_contract
        return DepartmentResponse(
            department=self.department,
            answer=answer,
            db_data={"education_level": level, "graduation_akts": total},
            generation_mode="kural",
            include_contact_suggestion=False,
            metadata=response_metadata,
            success=True,
        )

    async def _handle_hybrid_query(self, query_text: str, snapshot: dict) -> DepartmentResponse:
        retriever = self._get_retriever()
        results = retriever.search(query_text, department=self.department)
        db_summary = self._format_academic_snapshot(snapshot)

        answer, generation_mode = await self._generate_answer(
            query_text,
            results,
            db_context=db_summary,
            force_llm=True,
        )

        return DepartmentResponse(
            department=self.department,
            answer=answer,
            db_data=snapshot,
            generation_mode=generation_mode,
            include_contact_suggestion=True,
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

    def _is_general_akts_rule_query(self, query_text: str) -> bool:
        return is_general_akts_rule_query(query_text)

    def _format_academic_snapshot(self, snapshot: dict) -> str:
        return format_academic_snapshot(snapshot)
