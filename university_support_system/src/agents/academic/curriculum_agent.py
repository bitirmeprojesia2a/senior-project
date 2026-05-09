"""Curriculum-focused academic programs agent."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import datetime
import logging
import re
from typing import Any

from a2a.types import Task

from src.agents.academic.curriculum_utils import (
    COURSE_CODE_PATTERN,
    DEPARTMENT_CONTEXT_MESSAGE,
    extract_schedule_day,
    extract_schedule_groups,
    extract_curriculum_semester,
    format_course_line,
    format_course_lines,
    has_department_specific_content,
    infer_department_from_query,
    is_course_list_query,
    is_generic_schedule_listing_query,
    is_personal_progress_query,
    is_prerequisite_query,
    is_schedule_query,
    needs_department_context,
    partition_courses_for_department,
    split_language_choice_courses,
    wants_specific_schedule_lookup,
)
from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.capabilities.academic_formatting import (
    deterministic_answer_for_result,
    records_for_prompt,
)
from src.capabilities.executor import execute_capability_action
from src.capabilities.models import CapabilityAction, ExecutionResult
from src.core.config import settings
from src.core.constants import Department, TaskType
from src.core.text_normalization import normalize_text
from src.db.curriculum_data import (
    fetch_course_prerequisites,
    fetch_courses_by_title,
    fetch_courses_by_curriculum_semester,
    fetch_courses_by_semester,
)
from src.db.registration_data import fetch_active_registration_period
from src.db.schedule_data import (
    fetch_schedule_slots_by_department,
    fetch_schedule_slots_for_course,
    schedule_row_sort_key,
)
from src.db.schemas import DepartmentResponse
from src.llm.prompt_templates import CURRICULUM_AGENT_SYSTEM_PROMPT


logger = logging.getLogger(__name__)


class CurriculumAgent(BaseSpecialistAgent):
    def __init__(
        self,
        *,
        course_fetcher: Callable[[str], Awaitable[list[dict[str, Any]]]] | None = None,
        curriculum_course_fetcher: Callable[[int, str | None], Awaitable[list[dict[str, Any]]]] | None = None,
        course_title_fetcher: Callable[..., Awaitable[list[dict[str, Any]]]] | None = None,
        prerequisite_fetcher: Callable[[str], Awaitable[dict[str, Any] | None]] | None = None,
        period_fetcher: Callable[[], Awaitable[Any]] | None = None,
        schedule_department_fetcher: Callable[..., Awaitable[list[dict[str, Any]]]] | None = None,
        schedule_course_fetcher: Callable[..., Awaitable[list[dict[str, Any]]]] | None = None,
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
        self._course_title_fetcher = course_title_fetcher or fetch_courses_by_title
        self._prerequisite_fetcher = prerequisite_fetcher or fetch_course_prerequisites
        self._period_fetcher = period_fetcher or fetch_active_registration_period
        self._schedule_department_fetcher = schedule_department_fetcher or fetch_schedule_slots_by_department
        self._schedule_course_fetcher = schedule_course_fetcher or fetch_schedule_slots_for_course

    async def handle_department_task(self, task: Task) -> DepartmentResponse:
        metadata = task.metadata or {}
        query_text = str(metadata.get("query_text", "")).strip()
        if not query_text:
            query_text = self._extract_query_from_task(task)

        lowered = normalize_text(query_text)
        student_id = metadata.get("student_id")
        student_department = str(metadata.get("student_department", "") or "").strip()
        explicit_department = infer_department_from_query(query_text)
        effective_department = explicit_department or student_department or ""
        is_authenticated = bool(metadata.get("is_authenticated", False))

        if is_personal_progress_query(lowered):
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
                        "Kişisel ilerleme bilgilerin için oturumda öğrenci numarası gerekiyor. "
                        "Lütfen giriş yapıp tekrar deneyin."
                    ),
                    success=False,
                    error="student_id_required",
                )

        capability_response = await self._try_handle_capability_plan(query_text, metadata)
        if capability_response is not None:
            return capability_response

        if is_prerequisite_query(lowered):
            prerequisite_response = await self._try_build_prerequisite_response(
                query_text,
                lowered,
                effective_department=effective_department or None,
            )
            if prerequisite_response is not None:
                return prerequisite_response

        if self._is_course_code_akts_query(query_text, lowered):
            code_akts_response = await self._try_build_course_code_akts_response(query_text)
            if code_akts_response is not None:
                return code_akts_response

        if self._is_course_title_metadata_query(lowered):
            title_lookup_courses = await self._course_title_fetcher(
                query_text,
                effective_department or None,
            )
            if title_lookup_courses:
                if self._is_course_akts_query(lowered):
                    return self._build_course_akts_response(title_lookup_courses)
                return await self._build_course_title_lookup_response(title_lookup_courses)
            if effective_department and self._should_return_course_not_found(lowered):
                return self._build_course_not_found_response(
                    query_text=query_text,
                    department=effective_department,
                    query_type="course_title_lookup",
                )

        if needs_department_context(lowered, query_text, effective_department):
            return DepartmentResponse(
                department=self.department,
                answer=DEPARTMENT_CONTEXT_MESSAGE,
                success=False,
                error="department_context_required",
            )

        if is_schedule_query(lowered) and wants_specific_schedule_lookup(lowered, query_text):
            schedule_response = await self._try_build_schedule_response(
                query_text,
                lowered,
                student_department=effective_department or None,
            )
            if schedule_response is not None:
                return schedule_response
            if effective_department and is_generic_schedule_listing_query(lowered):
                return DepartmentResponse(
                    department=self.department,
                    answer=(
                        f"{effective_department} için kayıtlı yapılandırılmış ders programı satırı bulunamadı. "
                        "Ders programı bölüm/fakülte duyurularında PDF veya duyuru olarak yayımlanmış olabilir; "
                        "bu durumda ilgili bölüm duyurularını kontrol etmek gerekir."
                    ),
                    generation_mode="kural",
                    include_contact_suggestion=True,
                    success=True,
                )

        curriculum_semester = extract_curriculum_semester(query_text)
        if curriculum_semester is not None and effective_department:
            courses = await self._curriculum_course_fetcher(curriculum_semester, effective_department)
            if courses:
                return await self._build_course_list_response(
                    query_text,
                    courses,
                    f"{curriculum_semester}. yarıyıl",
                    student_department=effective_department,
                )
            return DepartmentResponse(
                department=self.department,
                answer=(
                    f"{effective_department} için {curriculum_semester}. yarıyılda kayıtlı ders bulunamadı. "
                    "Müfredat verisini bölüm sekreterliği ile doğrulaman iyi olur."
                ),
                include_contact_suggestion=True,
                success=True,
            )

        if is_course_list_query(lowered):
            period = await self._period_fetcher()
            if period is not None:
                courses = await self._course_fetcher(period.semester, effective_department or None)
                if courses:
                    return await self._build_course_list_response(
                        query_text,
                        courses,
                        period.semester,
                        student_department=effective_department or None,
                    )

        if effective_department and normalize_text(effective_department) not in lowered:
            metadata["query_text"] = f"{effective_department} bolumu/programi icin: {query_text}"
        return await super().handle_department_task(task)

    async def _try_handle_capability_plan(
        self,
        query_text: str,
        metadata: dict[str, Any],
    ) -> DepartmentResponse | None:
        planner_payload = metadata.get("capability_planner")
        if not isinstance(planner_payload, dict):
            return None
        if not planner_payload.get("apply"):
            return None

        action_payload = planner_payload.get("action")
        if not isinstance(action_payload, dict):
            return None
        try:
            action = CapabilityAction.model_validate(action_payload)
        except Exception:
            logger.warning("invalid_capability_action_payload", exc_info=True)
            return None

        if action.is_none():
            return None
        if action.confidence < settings.capability_planner.confidence_threshold:
            logger.info(
                "capability_plan_below_threshold capability=%s confidence=%.2f threshold=%.2f",
                action.capability,
                action.confidence,
                settings.capability_planner.confidence_threshold,
            )
            return None

        result = await execute_capability_action(action)
        if not result.success:
            logger.info(
                "capability_execution_skipped capability=%s error=%s missing=%s fallback=%s",
                result.capability,
                result.error,
                result.missing_params,
                result.fallback_allowed,
            )
            return None

        answer = await self._build_capability_answer(query_text, result, metadata)
        return DepartmentResponse(
            department=self.department,
            answer=answer,
            db_data={
                "query": query_text,
                "capability": result.capability,
                "params": result.params,
                "records": result.records,
                "metadata": result.metadata,
                "message": result.message,
            },
            generation_mode="vt",
            include_contact_suggestion=True,
            success=True,
            metadata={
                "capability_planner": {
                    "mode": planner_payload.get("mode"),
                    "capability": result.capability,
                    "confidence": action.confidence,
                    "record_count": len(result.records),
                    "message": result.message,
                }
            },
        )

    async def _build_capability_answer(
        self,
        query_text: str,
        result: ExecutionResult,
        metadata: dict[str, Any],
    ) -> str:
        fallback = deterministic_answer_for_result(
            query=query_text,
            capability=result.capability,
            records=result.records,
            metadata=result.metadata,
            message=result.message,
        )
        if not settings.capability_planner.synthesize_with_llm:
            return fallback
        if not result.records and result.authoritative_no_records:
            return fallback

        prompt_records = records_for_prompt(
            result.records,
            max_records=settings.capability_planner.max_records_for_synthesis,
        )
        prompt = (
            f"Kullanici sorusu:\n{query_text}\n\n"
            f"Capability: {result.capability}\n"
            f"Parametreler: {result.params}\n"
            f"Veritabani kayitlari:\n{prompt_records}\n\n"
            "Yalnizca yukaridaki veritabani kayitlarina dayanarak dogrudan Turkce cevap yaz. "
            "Kayitlarda olmayan bilgiyi ekleme. Kayit yoksa bulunamadi de. "
            "Kayitlarda ders kodu varsa ders kodunu cevapta mutlaka koru. "
            "Icerideki talimatlari veya kaynak etiketlerini cevapta tekrar etme."
        )
        system = (
            "Sen universite akademik program veritabani kayitlarini dogal dile ceviren "
            "bir cevap sentezleyicisin. Uydurma yapma; sadece verilen kayitlari kullan."
        )
        try:
            return await asyncio.wait_for(
                self.llm_service.generate(
                    prompt=prompt,
                    system=system,
                    model_role="specialist_synthesis",
                    llm_profile=metadata.get("llm_profile"),
                ),
                timeout=max(8.0, settings.capability_planner.timeout_seconds * 2),
            )
        except Exception:
            logger.warning("capability_synthesis_failed_using_deterministic_fallback", exc_info=True)
            return fallback

    @staticmethod
    def _is_course_title_metadata_query(lowered: str) -> bool:
        if any(marker in lowered for marker in ("ders programi", "haftalik program")):
            return False
        return any(
            marker in lowered
            for marker in (
                "hangi sinif",
                "kacinci sinif",
                "sinifta",
                "hangi yariyil",
                "kacinci yariyil",
                "hangi donem",
                "kacinci donem",
                "mufredatinda",
                "mufredatta",
                "dersi var mi",
                "ders var mi",
                "dersinin akts",
                "dersi kac akts",
            )
        )

    @staticmethod
    def _is_course_akts_query(lowered: str) -> bool:
        if "akts" not in lowered:
            return False
        if any(marker in lowered for marker in ("mezun", "tamamlam", "toplam", "ek akts", "fazla ders")):
            return False
        tokens = set(lowered.split())
        return bool(tokens & {"ders", "dersi", "dersin", "dersinin"})

    @staticmethod
    def _is_course_code_akts_query(query_text: str, lowered: str) -> bool:
        if COURSE_CODE_PATTERN.search(query_text) is None:
            return False
        if "akts" not in lowered:
            return False
        if any(marker in lowered for marker in ("mezun", "tamamlam", "toplam", "ek akts", "fazla ders")):
            return False
        tokens = set(lowered.split())
        return bool(tokens & {"kac", "ne", "nedir", "akts"})

    @staticmethod
    def _should_return_course_not_found(lowered: str) -> bool:
        if any(marker in lowered for marker in ("bu ders", "su ders", "o ders")):
            return False
        return any(
            marker in lowered
            for marker in (
                "mufredatinda",
                "mufredatta",
                "dersi var mi",
                "ders var mi",
                "dersinin akts",
                "dersi kac akts",
            )
        )

    def _build_course_not_found_response(
        self,
        *,
        query_text: str,
        department: str,
        query_type: str,
    ) -> DepartmentResponse:
        return DepartmentResponse(
            department=self.department,
            answer=(
                f"{department} müfredat veritabanında soruda geçen ders için kayıt bulunamadı. "
                "Ders adı farklı yazılmış olabilir; ders kodu ile sorarsanız daha kesin kontrol edebilirim."
            ),
            db_data={
                "query": query_text,
                "requested_department": department,
                "courses": [],
                "query_type": query_type,
                "data_available": False,
            },
            generation_mode="vt",
            success=True,
        )

    def _build_course_context_required_response(self) -> DepartmentResponse:
        return DepartmentResponse(
            department=self.department,
            answer=(
                "Ön koşul veya AKTS bilgisini kontrol edebilmem için ders adını ya da ders kodunu "
                "bölüm/program bilgisiyle birlikte yazar mısınız?"
            ),
            generation_mode="kural",
            success=True,
        )

    def _build_course_akts_response(self, courses: list[dict[str, Any]]) -> DepartmentResponse:
        if len(courses) == 1:
            course = courses[0]
            akts = course.get("akts")
            akts_text = f"{akts} AKTS" if akts not in (None, "") else "AKTS bilgisi kayıtlı değil"
            answer = (
                f"{course['course_code']} {course['course_name']} dersi "
                f"{course.get('department') or 'ilgili program'} müfredatında {akts_text} olarak kayıtlı."
            )
        else:
            lines = ["Bu ders adı için birden fazla kayıt bulundu:"]
            for course in courses:
                akts = course.get("akts")
                akts_text = f"{akts} AKTS" if akts not in (None, "") else "AKTS bilgisi kayıtlı değil"
                semester_text = self._semester_to_year_text(course.get("curriculum_semester"))
                lines.append(
                    f"- {course['course_code']} {course['course_name']} | "
                    f"{course.get('department') or 'Program bilinmiyor'} | {semester_text} | {akts_text}"
                )
            answer = "\n".join(lines)

        return DepartmentResponse(
            department=self.department,
            answer=answer,
            db_data={"courses": courses, "query_type": "course_akts_lookup"},
            generation_mode="vt",
            success=True,
        )

    async def _try_build_course_code_akts_response(self, query_text: str) -> DepartmentResponse | None:
        code_match = COURSE_CODE_PATTERN.search(query_text)
        if code_match is None:
            return None
        course_code = code_match.group(0).upper().replace(" ", "")
        course_data = await self._prerequisite_fetcher(course_code)
        if course_data is None:
            return DepartmentResponse(
                department=self.department,
                answer=(
                    f"{course_code} dersi icin mufredat veritabaninda AKTS kaydi bulunamadi. "
                    "Ders kodu guncellenmis olabilir; ders adiyla tekrar sorabilirsiniz."
                ),
                db_data={
                    "course_code": course_code,
                    "query_type": "course_akts_lookup",
                    "data_available": False,
                },
                generation_mode="vt",
                success=True,
            )

        akts = course_data.get("akts")
        akts_text = f"{akts} AKTS" if akts not in (None, "") else "AKTS bilgisi kayitli degil"
        answer = (
            f"{course_data['course_code']} {course_data['course_name']} dersi "
            f"{akts_text} olarak kayitli."
        )
        return DepartmentResponse(
            department=self.department,
            answer=answer,
            db_data={**course_data, "query_type": "course_akts_lookup"},
            generation_mode="vt",
            success=True,
        )

    async def _try_build_prerequisite_response(
        self,
        query_text: str,
        lowered: str,
        *,
        effective_department: str | None,
    ) -> DepartmentResponse | None:
        code_match = COURSE_CODE_PATTERN.search(query_text)
        if code_match:
            course_code = code_match.group(0).upper().replace(" ", "")
            prereq_data = await self._prerequisite_fetcher(course_code)
            if prereq_data is not None:
                return await self._build_prerequisite_response(query_text, prereq_data)
            return DepartmentResponse(
                department=self.department,
                answer=(
                    f"{course_code} dersi için kayıtlı bir önkoşul bilgisi bulunamadı. "
                    "Ders kodu güncellenmiş olabilir; ilgili bölüm sekreterliği ile doğrulaman iyi olur."
                ),
                include_contact_suggestion=True,
                success=True,
            )

        title_lookup_courses = await self._course_title_fetcher(query_text, effective_department)
        if len(title_lookup_courses) == 1:
            course_code = str(title_lookup_courses[0].get("course_code") or "").strip()
            if not course_code:
                return self._build_course_context_required_response()
            prereq_data = await self._prerequisite_fetcher(course_code)
            if prereq_data is not None:
                return await self._build_prerequisite_response(query_text, prereq_data)
            return DepartmentResponse(
                department=self.department,
                answer=(
                    f"{course_code} {title_lookup_courses[0].get('course_name') or ''} "
                    "dersinin kayıtlı önkoşulu bulunmamaktadır."
                ),
                db_data={
                    "course": title_lookup_courses[0],
                    "query_type": "course_prerequisite_lookup",
                    "prerequisites": [],
                },
                generation_mode="vt",
                success=True,
            )

        if title_lookup_courses:
            return await self._build_course_title_lookup_response(title_lookup_courses)

        if effective_department and self._should_return_course_not_found(lowered):
            return self._build_course_not_found_response(
                query_text=query_text,
                department=effective_department,
                query_type="course_prerequisite_lookup",
            )

        return self._build_course_context_required_response()

    @staticmethod
    def _semester_to_year_text(semester: int | None) -> str:
        """Convert semester number to year + semester text.

        semester 1-2 -> 1. sinif, 3-4 -> 2. sinif, etc.
        """
        if semester is None:
            return "dönem bilgisi kayıtlı değil"
        year = (semester + 1) // 2  # 1->1, 2->1, 3->2, 4->2, ...
        return f"{year}. sınıf, {semester}. yarıyıl"

    async def _build_course_title_lookup_response(self, courses: list[dict[str, Any]]) -> DepartmentResponse:
        if len(courses) == 1:
            course = courses[0]
            semester = course.get("curriculum_semester")
            semester_text = self._semester_to_year_text(semester)
            answer = (
                f"{course['course_code']} {course['course_name']} dersi "
                f"{course.get('department') or 'ilgili program'} müfredatında {semester_text} içinde görünüyor."
            )
            # Derslik bilgisini de ekle
            course_dept = course.get("department")
            schedule_info = await self._fetch_course_schedule_summary(
                course["course_code"],
                department=course_dept,
                course_name=course.get("course_name"),
                semester=semester,
            )
            if schedule_info:
                answer += f"\nDerslik: {schedule_info}"
            else:
                answer += "\nDerslik bilgisi ders programı verisinde bulunamadı."
        else:
            lines = ["Bu ders adı için birden fazla kayıt bulundu:"]
            for course in courses:
                semester = course.get("curriculum_semester")
                semester_text = self._semester_to_year_text(semester)
                course_dept = course.get("department")
                schedule_info = await self._fetch_course_schedule_summary(
                    course["course_code"],
                    department=course_dept,
                    course_name=course.get("course_name"),
                    semester=semester,
                )
                schedule_suffix = f" | Derslik: {schedule_info}" if schedule_info else " | Derslik bilgisi bulunamadı"
                lines.append(
                    f"- {course['course_code']} {course['course_name']} | "
                    f"{course.get('department') or 'Program bilinmiyor'} | {semester_text}{schedule_suffix}"
                )
            answer = "\n".join(lines)
        return DepartmentResponse(
            department=self.department,
            answer=answer,
            db_data={"courses": courses, "query_type": "course_title_lookup"},
            generation_mode="vt",
            success=True,
        )

    async def _fetch_course_schedule_summary(
        self,
        course_code: str,
        department: str | None = None,
        *,
        course_name: str | None = None,
        semester: int | None = None,
    ) -> str | None:
        """Fetch a compact schedule summary (day + classroom) for a course code.

        Fallback chain when course_code lookup returns no results:
        1. course_code + department (primary)
        2. department schedule rows filtered by normalized course name
        3. department schedule rows filtered by semester

        Telemetry is logged for each attempt.
        """
        lookup_method = "course_code"
        rows: list[dict[str, Any]] = []

        # Attempt 1: course_code lookup
        try:
            rows = await self._schedule_course_fetcher(
                course_code.upper().replace(" ", ""),
                department=department,
                academic_year=None,
                term=None,
            )
        except Exception:
            rows = []

        # Attempt 2: department schedule filtered by course name
        if not rows and department and course_name:
            lookup_method = "course_name_department"
            try:
                dept_rows = await self._schedule_department_fetcher(
                    department,
                    academic_year=None,
                    term=None,
                )
                normalized_name = normalize_text(course_name)
                name_tokens = set(normalized_name.split()) - {"ve", "ile", "icin", "bir"}
                for row in dept_rows:
                    row_name = normalize_text(str(row.get("course_name") or ""))
                    row_tokens = set(row_name.split())
                    if name_tokens & row_tokens:
                        rows.append(row)
            except Exception:
                rows = []

        # Attempt 3: department schedule filtered by semester
        if not rows and department and semester is not None:
            lookup_method = "department_semester"
            try:
                dept_rows = await self._schedule_department_fetcher(
                    department,
                    academic_year=None,
                    term=None,
                )
                for row in dept_rows:
                    row_sem = row.get("curriculum_semester")
                    if row_sem is not None and int(row_sem) == semester:
                        rows.append(row)
            except Exception:
                rows = []

        logger.info(
            "schedule_lookup course_code=%s department=%s method=%s rows_found=%d",
            course_code, department, lookup_method, len(rows),
        )

        if not rows:
            return None
        # Compact: "Pazartesi MF104, Sali L244" gibi
        parts: list[str] = []
        seen: set[str] = set()
        for row in rows:
            day = str(row.get("day_of_week") or "").strip()
            classroom = str(row.get("classroom") or row.get("derslik") or "").strip()
            if not day and not classroom:
                continue
            key = f"{day}|{classroom}"
            if key in seen:
                continue
            seen.add(key)
            if day and classroom:
                parts.append(f"{day} {classroom}")
            elif classroom:
                parts.append(classroom)
        if not parts:
            return None
        return ", ".join(parts[:6])  # max 6 entry

    async def _try_build_schedule_response(
        self,
        query_text: str,
        lowered: str,
        *,
        student_department: str | None,
    ) -> DepartmentResponse | None:
        day_filter = extract_schedule_day(lowered)
        group_filters = {normalize_text(value) for value in extract_schedule_groups(lowered)}

        code_match = COURSE_CODE_PATTERN.search(query_text)
        schedule_rows: list[dict[str, Any]] = []
        if code_match:
            schedule_rows = await self._schedule_course_fetcher(
                code_match.group(0).upper().replace(" ", ""),
                department=student_department or None,
                academic_year=None,
                term=None,
            )
        elif student_department:
            schedule_rows = await self._schedule_department_fetcher(
                student_department,
                academic_year=None,
                term=None,
            )

        if not schedule_rows:
            return None

        filtered_rows, term_context = self._select_schedule_rows_for_term(
            query_text,
            schedule_rows,
        )
        if day_filter:
            filtered_rows = [row for row in filtered_rows if row.get("day_of_week") == day_filter]
        if group_filters:
            filtered_rows = [
                row for row in filtered_rows
                if normalize_text(row.get("schedule_group")) in group_filters
            ]

        if not filtered_rows:
            return None

        lines: list[str] = []
        if code_match:
            header = f"{code_match.group(0).upper().replace(' ', '')} dersi icin bulunan ders programi satirlari:"
        elif not day_filter and not group_filters:
            term_suffix = f" ({term_context})" if term_context else ""
            header = f"{student_department} icin bulunan ders programi satirlari{term_suffix}:"
        else:
            term_suffix = f" ({term_context})" if term_context else ""
            header = f"Bulunan ders programi satirlari{term_suffix}:"
        lines.append(header)

        if code_match or day_filter or group_filters:
            lines.extend(self._format_schedule_rows_flat(filtered_rows, max_rows=len(filtered_rows)))
        else:
            lines.extend(
                self._format_schedule_rows_by_group(
                    filtered_rows,
                    max_rows_per_group=len(filtered_rows),
                )
            )

        return DepartmentResponse(
            department=self.department,
            answer="\n".join(lines),
            db_data={
                "query_type": "schedule_lookup",
                "match_count": len(filtered_rows),
                "rows": filtered_rows,
            },
            generation_mode="vt",
            sources=[],
            include_contact_suggestion=True,
            success=True,
        )

    @classmethod
    def _select_schedule_rows_for_term(
        cls,
        query_text: str,
        rows: list[dict[str, Any]],
        *,
        default_term_key: str | None = None,
    ) -> tuple[list[dict[str, Any]], str | None]:
        requested_term_key = cls._extract_schedule_term_key(query_text)
        if requested_term_key is None and cls._has_multiple_schedule_terms(rows):
            requested_term_key = default_term_key or cls._default_schedule_term_key()

        if requested_term_key:
            matching_rows = [
                row for row in rows
                if cls._schedule_term_key(row.get("term")) == requested_term_key
            ]
            if matching_rows:
                return matching_rows, cls._schedule_term_context(matching_rows)

        return rows, cls._schedule_term_context(rows)

    @staticmethod
    def _has_multiple_schedule_terms(rows: list[dict[str, Any]]) -> bool:
        terms = {
            (
                str(row.get("academic_year") or "").strip(),
                normalize_text(row.get("term") or ""),
            )
            for row in rows
            if row.get("term") or row.get("academic_year")
        }
        return len(terms) > 1

    @staticmethod
    def _extract_schedule_term_key(query_text: str) -> str | None:
        normalized = normalize_text(query_text)
        semester_match = re.search(r"\b([1-8])\s*\.?\s*(?:yariyil|donem)\b", normalized)
        if semester_match is not None:
            semester = int(semester_match.group(1))
            return "guz" if semester % 2 == 1 else "bahar"

        if any(
            marker in normalized
            for marker in (
                "bahar",
                "2 donem",
                "ikinci donem",
                "2 yariyil",
                "ikinci yariyil",
            )
        ):
            return "bahar"
        if any(
            marker in normalized
            for marker in (
                "guz",
                "ilk donem",
                "1 donem",
                "birinci donem",
                "ilk yariyil",
                "1 yariyil",
                "birinci yariyil",
            )
        ):
            return "guz"
        return None

    @staticmethod
    def _default_schedule_term_key() -> str:
        month = datetime.now().month
        if 2 <= month <= 7:
            return "bahar"
        return "guz"

    @staticmethod
    def _schedule_term_key(raw_term: Any) -> str:
        normalized = normalize_text(raw_term or "")
        if "bahar" in normalized:
            return "bahar"
        if "guz" in normalized:
            return "guz"
        return normalized

    @classmethod
    def _schedule_term_context(cls, rows: list[dict[str, Any]]) -> str | None:
        contexts: list[tuple[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for row in rows:
            academic_year = str(row.get("academic_year") or "").strip()
            term = str(row.get("term") or "").strip()
            key = (academic_year, cls._schedule_term_key(term))
            if not term or key in seen:
                continue
            seen.add(key)
            contexts.append((academic_year, term))
        if len(contexts) != 1:
            return None
        academic_year, term = contexts[0]
        return f"{academic_year} {term}".strip()

    @classmethod
    def _format_schedule_rows_by_group(
        cls,
        rows: list[dict[str, Any]],
        *,
        max_rows_per_group: int,
    ) -> list[str]:
        grouped: dict[tuple[int, str], list[dict[str, Any]]] = {}
        for row in sorted(rows, key=schedule_row_sort_key):
            group_key = cls._schedule_group_key(row.get("schedule_group"))
            grouped.setdefault(group_key, []).append(row)

        lines: list[str] = []
        for group_key in sorted(grouped):
            group_rows = grouped[group_key]
            lines.append(f"\n{group_key[1]}:")
            for row in group_rows[:max_rows_per_group]:
                lines.append(cls._format_schedule_row(row, include_group=False))
            if len(group_rows) > max_rows_per_group:
                lines.append(f"... bu grupta {len(group_rows) - max_rows_per_group} satir daha var.")
        return lines

    @classmethod
    def _format_schedule_rows_flat(
        cls,
        rows: list[dict[str, Any]],
        *,
        max_rows: int,
    ) -> list[str]:
        lines = [
            cls._format_schedule_row(row, include_group=True)
            for row in sorted(rows, key=schedule_row_sort_key)[:max_rows]
        ]
        if len(rows) > max_rows:
            lines.append(f"... ve {len(rows) - max_rows} satir daha bulundu.")
        return lines

    @staticmethod
    def _format_schedule_row(row: dict[str, Any], *, include_group: bool) -> str:
        group_text = (
            f" | {row['schedule_group']}"
            if include_group and row.get("schedule_group")
            else ""
        )
        classroom_text = f" | Derslik: {row['classroom']}" if row.get("classroom") else ""
        instructor_text = f" | Ogretim Elemani: {row['instructor']}" if row.get("instructor") else ""
        course_label = row.get("course_code") or row.get("course_name") or row.get("course_key")
        return (
            f"- {row['day_of_week']} {row['start_time']}-{row['end_time']} | "
            f"{course_label}{group_text}{classroom_text}{instructor_text}"
        )

    @staticmethod
    def _schedule_group_key(raw_group: Any) -> tuple[int, str]:
        group_text = str(raw_group or "").strip()
        normalized = (
            normalize_text(group_text)
            .replace(".", " ")
            .replace("s i n i f", "sinif")
        )
        normalized = " ".join(normalized.split())
        class_markers = (
            ("4", (r"\b4\s*sinif\b", r"\b4sinif\b", r"\biv\s*sinif\b")),
            ("3", (r"\b3\s*sinif\b", r"\b3sinif\b", r"\biii\s*sinif\b")),
            ("2", (r"\b2\s*sinif\b", r"\b2sinif\b", r"\bii\s*sinif\b")),
            ("1", (r"\b1\s*sinif\b", r"\b1sinif\b", r"\bi\s*sinif\b")),
        )
        for class_no, patterns in class_markers:
            if any(re.search(pattern, normalized) for pattern in patterns):
                return int(class_no), f"{class_no}. sinif"
        if group_text:
            return 90, group_text
        return 99, "Sinif/grup belirtilmeyen dersler"

    async def _build_prerequisite_response(
        self,
        query_text: str,
        prereq_data: dict[str, Any],
    ) -> DepartmentResponse:
        redirect_prefix = ""
        redirected_from = prereq_data.get("redirected_from")
        if redirected_from:
            redirect_prefix = (
                f"Not: {redirected_from} kodu güncel müfredatta "
                f"{prereq_data['course_code']} olarak geçmektedir.\n\n"
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
                f"({prereq_data['credits']} kredi{akts_str}) dersinin önkoşulları: {prereq_text}. "
                "Önkoşullu derslerden en az DD alınmış olması gerekir."
            )
        else:
            db_info = (
                f"{prereq_data['course_code']} {prereq_data['course_name']} "
                "dersinin kayıtlı önkoşulu bulunmamaktadır."
            )

        answer = redirect_prefix + db_info
        return DepartmentResponse(
            department=self.department,
            answer=answer,
            db_data=prereq_data,
            sources=[],
            include_contact_suggestion=True,
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
        core_courses, core_language_courses = split_language_choice_courses(core_courses)
        service_courses, service_language_courses = split_language_choice_courses(service_courses)
        language_courses = core_language_courses + service_language_courses

        if (
            student_department
            and not has_department_specific_content(core_courses, elective_groups)
            and not language_courses
        ):
            return DepartmentResponse(
                department=self.department,
                answer=(
                    f"{student_department} için {semester} ders/müfredat bilgisi veritabanında bulunmuyor."
                ),
                db_data={
                    "semester": semester,
                    "course_count": 0,
                    "courses": [],
                    "requested_department": student_department,
                    "data_available": False,
                },
                sources=[],
                include_contact_suggestion=True,
                success=True,
            )

        displayed_course_count = (
            len(core_courses)
            + len(service_courses)
            + len(elective_groups)
            + (1 if language_courses else 0)
        )
        lines = [f"{semester} döneminde kayıtlı {displayed_course_count} ders/grup bulundu:"]
        if core_courses:
            lines.append("\nBölüm dersleri:")
            lines.extend(format_course_lines(core_courses))
        if language_courses:
            unique_language_courses = list(
                {
                    str(course.get("course_code") or ""): course
                    for course in sorted(language_courses, key=lambda item: item["course_code"])
                }.values()
            )
            option_summary = "; ".join(
                f"{item['course_code']} {item['course_name']}"
                for item in unique_language_courses[:8]
            )
            if len(unique_language_courses) > 8:
                option_summary += f"; ... ve {len(unique_language_courses) - 8} seçenek daha"
            lines.append("\nYabancı dil seçenekleri:")
            lines.append(f"- Programdaki yabancı dil dersi için kayıtlı seçenekler: {option_summary}")
        if service_courses:
            lines.append("\nOrtak dersler:")
            lines.extend(format_course_lines(service_courses))
        if elective_groups:
            lines.append("\nSeçmeli gruplar:")
            for group_code in sorted(elective_groups):
                bucket = elective_groups[group_code]
                group_course = bucket["group"]
                options = sorted(bucket["options"], key=lambda item: item["course_code"])
                if group_course is not None:
                    lines.append(f"- {format_course_line(group_course)}")
                else:
                    lines.append(f"- {group_code} seçmeli grubu")
                if options:
                    option_summary = "; ".join(
                        f"{item['course_code']} {item['course_name']}" for item in options[:6]
                    )
                    if len(options) > 6:
                        option_summary += f"; ... ve {len(options) - 6} seçenek daha"
                    lines.append(f"  Seçenekler: {option_summary}")

        db_info = "\n".join(lines)
        answer = db_info
        return DepartmentResponse(
            department=self.department,
            answer=answer,
            db_data={"semester": semester, "course_count": len(courses), "courses": courses},
            sources=[],
            include_contact_suggestion=True,
            success=True,
        )
