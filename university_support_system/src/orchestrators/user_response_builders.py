"""Helpers for building user-facing orchestrator responses."""

from __future__ import annotations

from src.db.schemas import DepartmentResponse, UserQueryResponse
from src.orchestrators.query_policy import personalize_answer
from src.orchestrators.response_utils import clean_final_answer


def build_clarification_user_response(
    *,
    context_id: str,
    message: str,
    response_time_ms: float,
    full_name: str | None = None,
) -> UserQueryResponse:
    personalized_message = personalize_answer(message, full_name)
    return UserQueryResponse(
        answer=personalized_message,
        departments_involved=[],
        sources=[],
        response_time_ms=response_time_ms,
        query_id=context_id,
    )


def build_final_user_response(
    *,
    answer: str,
    responses: list[DepartmentResponse],
    department_responses: list[DepartmentResponse],
    context_id: str,
    response_time_ms: float,
    student_full_name: str | None,
) -> UserQueryResponse:
    cleaned_answer = clean_final_answer(answer)
    personalized_answer = personalize_answer(cleaned_answer, student_full_name)
    sources = [source for response in responses for source in response.sources]
    return UserQueryResponse(
        answer=personalized_answer,
        departments_involved=[response.department.value for response in department_responses],
        sources=sources,
        response_time_ms=response_time_ms,
        query_id=context_id,
    )


def build_announcement_user_response(
    *,
    context_id: str,
    answer: str,
    sources,
    response_time_ms: float,
) -> UserQueryResponse:
    departments_involved = ["announcement"] if sources else []
    return UserQueryResponse(
        answer=answer,
        departments_involved=departments_involved,
        sources=sources,
        response_time_ms=response_time_ms,
        query_id=context_id,
    )
