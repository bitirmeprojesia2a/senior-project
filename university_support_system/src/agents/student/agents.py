"""Ogrenci isleri uzman ajanlari."""

from __future__ import annotations

from typing import Awaitable, Callable

from a2a.types import Task

from src.agents.base import AgentDefinition, BaseSpecialistAgent
from src.core.constants import Department, TaskType
from src.db.personal_data import fetch_student_academic_snapshot
from src.db.schemas import DepartmentResponse


class RegistrationAgent(BaseSpecialistAgent):
    def __init__(self, **kwargs):
        super().__init__(
            AgentDefinition(
                agent_id="registration_agent",
                name="Registration Agent",
                department=Department.STUDENT_AFFAIRS,
                description="Kayit, muafiyet ve yatay gecis sureclerini yonetir.",
                task_types=(TaskType.REGISTRATION_QUERY, TaskType.PROCEDURE_QUERY),
                examples=("Ders kaydi ne zaman?", "Yatay gecis basvurusu nasil yapilir?"),
                tags=("student_affairs", "registration"),
            ),
            **kwargs,
        )


class GraduationAgent(BaseSpecialistAgent):
    _PERSONAL_KEYWORDS = ("gno", "notlarim", "notlarım", "transkriptim", "ortalamam", "mezun olabilir miyim")

    def __init__(
        self,
        *,
        academic_fetcher: Callable[[int], Awaitable[dict | None]] | None = None,
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
            ),
            **kwargs,
        )
        self._academic_fetcher = academic_fetcher or fetch_student_academic_snapshot

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
                        "Kisisel not, GNO veya transkript bilgilerini paylasabilmem icin "
                        "once kimligini dogrulaman gerekiyor."
                    ),
                    success=False,
                    error="authentication_required",
                )

            snapshot = await self._academic_fetcher(int(student_id))
            if snapshot is None:
                return DepartmentResponse(
                    department=self.department,
                    answer="Ogrenci kaydi bulunamadi.",
                    success=False,
                    error="student_not_found",
                )

            return DepartmentResponse(
                department=self.department,
                answer=self._format_academic_snapshot(snapshot),
                db_data=snapshot,
                success=True,
            )

        return await super().handle_task(task)

    def _is_personal_query(self, query_text: str) -> bool:
        lowered = query_text.casefold()
        return any(keyword in lowered for keyword in self._PERSONAL_KEYWORDS)

    def _format_academic_snapshot(self, snapshot: dict) -> str:
        lines = [f"{snapshot['student_name']} icin akademik durum ozeti:"]
        if snapshot.get("gpa") is not None:
            lines.append(f"- GNO: {float(snapshot['gpa']):.2f}")
        lines.append(
            f"- Tamamlanan kredi: {snapshot.get('completed_credits', 0)} / {snapshot.get('total_credits', 0)}"
        )
        lines.append(f"- Kayit durumu: {snapshot.get('registration_status', 'bilinmiyor')}")

        recent_courses = snapshot.get("recent_courses") or []
        if recent_courses:
            lines.append("- Son ders kayitlari:")
            for course in recent_courses[:3]:
                grade = course.get("grade") or "not girilmedi"
                lines.append(
                    f"  * {course['course_code']} {course['course_name']} | {course['semester']} | {grade}"
                )

        return "\n".join(lines)


class InternshipAgent(BaseSpecialistAgent):
    def __init__(self, **kwargs):
        super().__init__(
            AgentDefinition(
                agent_id="internship_agent",
                name="Internship Agent",
                department=Department.STUDENT_AFFAIRS,
                description="Staj, bitirme projesi ve uygulamali egitim sorularina bakar.",
                task_types=(TaskType.PROCEDURE_QUERY, TaskType.COURSE_QUERY),
                examples=("Staj basvurusu nasil yapilir?", "Bitirme projesi teslimi nasil olur?"),
                tags=("student_affairs", "internship"),
            ),
            **kwargs,
        )


class StudentLifeAgent(BaseSpecialistAgent):
    def __init__(self, **kwargs):
        super().__init__(
            AgentDefinition(
                agent_id="student_life_agent",
                name="Student Life Agent",
                department=Department.STUDENT_AFFAIRS,
                description="Ogrenci hayati, topluluklar ve genel destek sorularini yanitlar.",
                task_types=(TaskType.PROCEDURE_QUERY,),
                examples=("Kimlik karti nasil alinir?", "Ogrenci topluluguna nasil katilirim?"),
                tags=("student_affairs", "student_life"),
            ),
            **kwargs,
        )
