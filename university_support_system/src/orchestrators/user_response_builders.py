"""Helpers for building user-facing orchestrator responses."""

from __future__ import annotations

from src.db.schemas import DepartmentResponse, UserQueryResponse
from src.orchestrators.query_policy import personalize_answer
from src.orchestrators.response_utils import (
    ANNOUNCEMENT_SURFACE_DEPARTMENT,
    append_generation_summary,
    append_source_summary,
    append_source_summary_for_sources,
    clean_final_answer,
    collect_surface_departments,
    collect_generation_modes,
    split_answer_and_contact_flag,
)


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
        generation_modes=["kural"],
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
    used_global_synthesis: bool = False,
) -> UserQueryResponse:
    cleaned_answer = clean_final_answer(answer)
    cleaned_answer = append_generation_summary(cleaned_answer, responses)
    cleaned_answer = append_source_summary(cleaned_answer, responses)
    personalized_answer = personalize_answer(cleaned_answer, student_full_name)
    sources = [source for response in responses for source in response.sources]
    generation_modes = collect_generation_modes(responses)
    if used_global_synthesis and "llm" not in generation_modes:
        generation_modes = ["llm", *generation_modes]
    return UserQueryResponse(
        answer=personalized_answer,
        departments_involved=collect_surface_departments(responses),
        generation_modes=generation_modes,
        sources=sources,
        response_time_ms=response_time_ms,
        query_id=context_id,
    )


def build_memory_answer(*, answer: str) -> str:
    """Conversation memory icin kanonik cevap govdesi uretir."""
    cleaned_answer = clean_final_answer(answer)
    core_answer, _ = split_answer_and_contact_flag(cleaned_answer)
    return core_answer


def build_announcement_user_response(
    *,
    context_id: str,
    answer: str,
    sources,
    response_time_ms: float,
) -> UserQueryResponse:
    departments_involved = [ANNOUNCEMENT_SURFACE_DEPARTMENT]
    answer = clean_final_answer(answer)
    answer = append_source_summary_for_sources(answer, sources)
    return UserQueryResponse(
        answer=answer,
        departments_involved=departments_involved,
        generation_modes=["vt"],
        sources=sources,
        response_time_ms=response_time_ms,
        query_id=context_id,
    )
