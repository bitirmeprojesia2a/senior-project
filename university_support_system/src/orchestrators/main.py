"""Ana orkestratör."""

from __future__ import annotations

from time import perf_counter
from uuid import uuid4

from src.a2a import A2AQueryPayload, build_query_task
from src.agents import (
    AnnouncementAgent,
    CurriculumAgent,
    GraduationAgent,
    InternationalAgent,
    InternshipAgent,
    RegistrationAgent,
    RegulationAgent,
    ScholarshipAgent,
    StudentLifeAgent,
    TuitionAgent,
)
from src.db.telemetry import (
    TelemetryService,
    build_main_orchestrator_identity,
    build_specialist_agent_identity,
)
from src.db.schemas import DepartmentResponse, UserQueryResponse
from src.orchestrators.department import (
    DepartmentOrchestrator,
    build_academic_programs_orchestrator,
    build_finance_orchestrator,
    build_student_affairs_orchestrator,
)
from src.routing import DepartmentRouter


class MainOrchestrator:
    """Kullanıcı sorgusunu router ve departman orkestratörleri üzerinden işler."""

    def __init__(
        self,
        *,
        router: DepartmentRouter | None = None,
        department_orchestrators: dict | None = None,
        announcement_agent: AnnouncementAgent | None = None,
        telemetry_service: TelemetryService | None = None,
    ) -> None:
        self.router = router or DepartmentRouter()
        self.telemetry_service = telemetry_service or TelemetryService()
        self.department_orchestrators = department_orchestrators or self._build_default_orchestrators()
        self.announcement_agent = announcement_agent or AnnouncementAgent()

    async def handle_query(
        self,
        query: str,
        *,
        context_id: str | None = None,
        user_id: str | None = None,
        student_id: int | None = None,
        is_authenticated: bool = False,
    ) -> UserQueryResponse:
        start_time = perf_counter()
        context_id = context_id or str(uuid4())

        query_log_id = None
        try:
            routing = await self.router.route(query)
            query_log_id = await self.telemetry_service.create_query_log(
                query_text=query,
                routing=routing,
                orchestrator=build_main_orchestrator_identity(),
                context_id=context_id,
                user_id=user_id,
                student_id=student_id,
            )

            responses: list[DepartmentResponse] = []
            department_responses: list[DepartmentResponse] = []

            for department in routing.departments:
                orchestrator = self.department_orchestrators.get(department)
                if orchestrator is None:
                    continue
                response = await orchestrator.handle(
                    query_text=query,
                    context_id=context_id,
                    task_type=routing.task_type,
                    metadata={
                        "routing_reason": routing.reasoning,
                        "user_id": user_id,
                        "student_id": student_id,
                        "is_authenticated": is_authenticated,
                        "query_log_id": query_log_id,
                    },
                )
                responses.append(response)
                department_responses.append(response)

            if not responses:
                fallback_task = build_query_task(
                    A2AQueryPayload(
                        query_text=query,
                        context_id=context_id,
                        routing_reason=routing.reasoning,
                    )
                )
                fallback = await self.announcement_agent.handle_task(fallback_task)
                await self.telemetry_service.record_agent_task(
                    task_id=fallback_task.id,
                    query_log_id=query_log_id,
                    sender=build_main_orchestrator_identity(),
                    receiver=build_specialist_agent_identity(self.announcement_agent),
                    task_type=routing.task_type,
                    payload=fallback_task.metadata or {},
                    response=fallback,
                )
                responses.append(fallback)
            else:
                announcement_response = await self._get_related_announcements(
                    query=query,
                    context_id=context_id,
                    routing_reason=routing.reasoning,
                    departments=[department.value for department in routing.departments],
                    query_log_id=query_log_id,
                    task_type=routing.task_type,
                )
                if announcement_response is not None and announcement_response.sources:
                    responses.append(announcement_response)

            answer = "\n\n".join(response.answer for response in responses if response.answer)
            sources = [source for response in responses for source in response.sources]
            response_time_ms = round((perf_counter() - start_time) * 1000, 2)
            final_response = UserQueryResponse(
                answer=answer,
                departments_involved=[response.department.value for response in department_responses],
                sources=sources,
                response_time_ms=response_time_ms,
                query_id=context_id,
            )
            await self.telemetry_service.finalize_query_log(
                query_log_id=query_log_id,
                response_text=answer,
                response_time_ms=response_time_ms,
                status="completed",
                departments=final_response.departments_involved,
            )
            return final_response
        except Exception as exc:
            await self.telemetry_service.finalize_query_log(
                query_log_id=query_log_id,
                response_text=None,
                response_time_ms=round((perf_counter() - start_time) * 1000, 2),
                status="failed",
                error=str(exc),
            )
            raise

    async def _get_related_announcements(
        self,
        *,
        query: str,
        context_id: str,
        routing_reason: str | None,
        departments: list[str],
        query_log_id: int | None,
        task_type,
    ) -> DepartmentResponse | None:
        announcement_task = build_query_task(
            A2AQueryPayload(
                query_text=query,
                context_id=context_id,
                routing_reason=routing_reason,
            )
        )
        announcement_task.metadata["departments"] = departments

        response = await self.announcement_agent.handle_task(announcement_task)
        await self.telemetry_service.record_agent_task(
            task_id=announcement_task.id,
            query_log_id=query_log_id,
            sender=build_main_orchestrator_identity(),
            receiver=build_specialist_agent_identity(self.announcement_agent),
            task_type=task_type,
            payload=announcement_task.metadata or {},
            response=response,
        )
        return response

    def _build_default_orchestrators(self) -> dict:
        student_agents = [
            RegistrationAgent(),
            GraduationAgent(),
            InternshipAgent(),
            StudentLifeAgent(),
        ]
        academic_agents = [
            CurriculumAgent(),
            RegulationAgent(),
            InternationalAgent(),
        ]
        finance_agents = [
            TuitionAgent(),
            ScholarshipAgent(),
        ]
        student_orchestrator = build_student_affairs_orchestrator(
            student_agents,
            telemetry_service=self.telemetry_service,
        )
        academic_orchestrator = build_academic_programs_orchestrator(
            academic_agents,
            telemetry_service=self.telemetry_service,
        )
        finance_orchestrator = build_finance_orchestrator(
            finance_agents,
            telemetry_service=self.telemetry_service,
        )
        return {
            student_orchestrator.department: student_orchestrator,
            academic_orchestrator.department: academic_orchestrator,
            finance_orchestrator.department: finance_orchestrator,
        }
