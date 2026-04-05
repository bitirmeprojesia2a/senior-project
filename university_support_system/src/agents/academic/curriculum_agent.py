"""Curriculum-focused academic programs agent."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from a2a.types import Task

from src.agents.academic.curriculum_utils import (
    COURSE_CODE_PATTERN,
    DEPARTMENT_CONTEXT_MESSAGE,
    extract_curriculum_semester,
    format_course_line,
    format_course_lines,
    has_department_specific_content,
    is_course_list_query,
    is_personal_progress_query,
    is_prerequisite_query,
    needs_department_context,
    partition_courses_for_department,
)
from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.core.constants import Department, TaskType
from src.core.messages import CONTACT_SUGGESTION
from src.core.text_normalization import normalize_text
from src.db.curriculum_data import (
    fetch_course_prerequisites,
    fetch_courses_by_curriculum_semester,
    fetch_courses_by_semester,
)
from src.db.registration_data import fetch_active_registration_period
from src.db.schemas import DepartmentResponse
from src.llm.prompt_templates import CURRICULUM_AGENT_SYSTEM_PROMPT


class CurriculumAgent(BaseSpecialistAgent):
    def __init__(
        self,
        *,
        course_fetcher: Callable[[str], Awaitable[list[dict[str, Any]]]] | None = None,
        curriculum_course_fetcher: Callable[[int, str | None], Awaitable[list[dict[str, Any]]]] | None = None,
        prerequisite_fetcher: Callable[[str], Awaitable[dict[str, Any] | None]] | None = None,
        period_fetcher: Callable[[], Awaitable[Any]] | None = None,
        **kwargs,
    ):
        super().__init__(
            AgentDefinition(
                agent_id="curriculum_agent",
                name="Curriculum Agent",
                department=Department.ACADEMIC_PROGRAMS,
                description="Mufredat, ders planlari ve onkosul sorularini ele alir.",
                task_types=(TaskType.COURSE_QUERY,),
                examples=("Mufredat nerede?", "Bu donem hangi dersler acik?"),
                tags=("academic_programs", "curriculum"),
                system_prompt=CURRICULUM_AGENT_SYSTEM_PROMPT,
            ),
            **kwargs,
        )
        self._course_fetcher = course_fetcher or fetch_courses_by_semester
        self._curriculum_course_fetcher = (
            curriculum_course_fetcher or fetch_courses_by_curriculum_semester
        )
        self._prerequisite_fetcher = prerequisite_fetcher or fetch_course_prerequisites
        self._period_fetcher = period_fetcher or fetch_active_registration_period

    async def handle_department_task(self, task: Task) -> DepartmentResponse:
        metadata = task.metadata or {}
        query_text = str(metadata.get("query_text", "")).strip()
        if not query_text:
            query_text = self._extract_query_from_task(task)

        lowered = normalize_text(query_text)
        student_id = metadata.get("student_id")
        student_department = str(metadata.get("student_department", "") or "").strip()
        is_authenticated = bool(metadata.get("is_authenticated", False))

        if is_personal_progress_query(lowered):
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
                        "Kisisel ilerleme bilgilerin icin oturumda ogrenci numarasi gerekiyor. "
                        "Lutfen giris yapip tekrar deneyin."
                    ),
                    success=False,
                    error="student_id_required",
                )

        if needs_department_context(lowered, query_text, student_department):
            return DepartmentResponse(
                department=self.department,
                answer=DEPARTMENT_CONTEXT_MESSAGE,
                success=False,
                error="department_context_required",
            )

        if is_prerequisite_query(lowered):
            code_match = COURSE_CODE_PATTERN.search(query_text)
            if code_match:
                prereq_data = await self._prerequisite_fetcher(code_match.group(0).upper().replace(" ", ""))
                if prereq_data is not None:
                    return await self._build_prerequisite_response(query_text, prereq_data)
                return DepartmentResponse(
                    department=self.department,
                    answer=(
                        f"{code_match.group(0).upper().replace(' ', '')} dersi icin kayitli bir onkosul bilgisi bulunamadi. "
                        "Ders kodu guncellenmis olabilir; ilgili bolum sekreterligi ile dogrulaman iyi olur."
                        + CONTACT_SUGGESTION
                    ),
                    success=True,
                )

        curriculum_semester = extract_curriculum_semester(query_text)
        if curriculum_semester is not None and student_department:
            courses = await self._curriculum_course_fetcher(curriculum_semester, student_department)
            if courses:
                return await self._build_course_list_response(
                    query_text,
                    courses,
                    f"{curriculum_semester}. yariyil",
                    student_department=student_department,
                )
            return DepartmentResponse(
                department=self.department,
                answer=(
                    f"{student_department} icin {curriculum_semester}. yariyilda kayitli ders bulunamadi. "
                    "Mufredat verisini bolum sekreterligi ile dogrulaman iyi olur."
                    + CONTACT_SUGGESTION
                ),
                success=True,
            )

        if is_course_list_query(lowered):
            period = await self._period_fetcher()
            if period is not None:
                courses = await self._course_fetcher(period.semester, student_department or None)
                if courses:
                    return await self._build_course_list_response(
                        query_text,
                        courses,
                        period.semester,
                        student_department=student_department or None,
                    )

        if student_department and normalize_text(student_department) not in lowered:
            metadata["query_text"] = f"{student_department} bolumu/programi icin: {query_text}"
        return await super().handle_department_task(task)

    async def _build_prerequisite_response(
        self,
        query_text: str,
        prereq_data: dict[str, Any],
    ) -> DepartmentResponse:
        redirect_prefix = ""
        redirected_from = prereq_data.get("redirected_from")
        if redirected_from:
            redirect_prefix = (
                f"Not: {redirected_from} kodu guncel mufredatta "
                f"{prereq_data['course_code']} olarak gecmektedir.\n\n"
            )

        groups = prereq_data.get("prerequisite_groups", {})
        if groups:
            group_texts = []
            for _gid, members in sorted(groups.items()):
                if len(members) == 1:
                    member = members[0]
                    group_texts.append(f"{member['course_code']} {member['course_name']}")
                else:
                    alternatives = " VEYA ".join(
                        f"{member['course_code']} {member['course_name']}" for member in members
                    )
                    group_texts.append(f"({alternatives})")
            prereq_text = " VE ".join(group_texts)
            akts = prereq_data.get("akts", "")
            akts_str = f", {akts} AKTS" if akts else ""
            db_info = (
                f"{prereq_data['course_code']} {prereq_data['course_name']} "
                f"({prereq_data['credits']} kredi{akts_str}) dersinin onkosullari: {prereq_text}. "
                "Onkosullu derslerden en az DD alinmis olmasi gerekir."
            )
        else:
            db_info = (
                f"{prereq_data['course_code']} {prereq_data['course_name']} "
                "dersinin kayitli onkosulu bulunmamaktadir."
            )

        answer = redirect_prefix + db_info + CONTACT_SUGGESTION
        return DepartmentResponse(
            department=self.department,
            answer=answer,
            db_data=prereq_data,
            sources=[],
            success=True,
        )

    async def _build_course_list_response(
        self,
        query_text: str,
        courses: list[dict[str, Any]],
        semester: str,
        *,
        student_department: str | None = None,
    ) -> DepartmentResponse:
        normalized_department = normalize_text(student_department)
        core_courses, service_courses, elective_groups = partition_courses_for_department(
            courses,
            normalized_department,
        )

        if student_department and not has_department_specific_content(core_courses, elective_groups):
            return DepartmentResponse(
                department=self.department,
                answer=(
                    f"{student_department} icin {semester} ders/mufredat bilgisi veritabaninda bulunmuyor."
                    + CONTACT_SUGGESTION
                ),
                db_data={
                    "semester": semester,
                    "course_count": 0,
                    "courses": [],
                    "requested_department": student_department,
                    "data_available": False,
                },
                sources=[],
                success=True,
            )

        lines = [f"{semester} doneminde kayitli {len(courses)} ders/grup bulundu:"]
        if core_courses:
            lines.append("\nBolum dersleri:")
            lines.extend(format_course_lines(core_courses))
        if service_courses:
            lines.append("\nOrtak dersler:")
            lines.extend(format_course_lines(service_courses))
        if elective_groups:
            lines.append("\nSecmeli gruplar:")
            for group_code in sorted(elective_groups):
                bucket = elective_groups[group_code]
                group_course = bucket["group"]
                options = sorted(bucket["options"], key=lambda item: item["course_code"])
                if group_course is not None:
                    lines.append(f"- {format_course_line(group_course)}")
                else:
                    lines.append(f"- {group_code} secmeli grubu")
                if options:
                    option_summary = "; ".join(
                        f"{item['course_code']} {item['course_name']}" for item in options[:6]
                    )
                    if len(options) > 6:
                        option_summary += f"; ... ve {len(options) - 6} secenek daha"
                    lines.append(f"  Secenekler: {option_summary}")

        db_info = "\n".join(lines)
        answer = db_info + CONTACT_SUGGESTION
        return DepartmentResponse(
            department=self.department,
            answer=answer,
            db_data={"semester": semester, "course_count": len(courses), "courses": courses},
            sources=[],
            success=True,
        )
