"""Helpers for building user-facing orchestrator responses."""

from __future__ import annotations

from src.core.profiling import get_current_profiler
from src.db.schemas import DepartmentResponse, QueryDiagnostics, UserQueryResponse
from src.orchestrators.query_policy import personalize_answer
from src.orchestrators.response_utils import (
    ANNOUNCEMENT_SURFACE_DEPARTMENT,
    EVENT_SURFACE_DEPARTMENT,
    append_generation_summary,
    append_source_summary,
    append_source_summary_for_sources,
    clean_final_answer,
    collect_surface_departments,
    collect_generation_modes,
    split_answer_and_contact_flag,
)


def _collect_remote_llm_usage(responses: list[DepartmentResponse] | None) -> list[dict]:
    """Collect LLM usage captured by remote A2A agent services."""
    collected: list[dict] = []
    for response in responses or []:
        metadata = response.metadata or {}
        profile_items = [
            item for item in metadata.get("remote_profiles") or []
            if isinstance(item, dict)
        ]
        if not profile_items and isinstance(metadata.get("remote_profile"), dict):
            profile_items = [
                {
                    "agent_id": metadata.get("remote_agent_id"),
                    "agent_role": metadata.get("remote_agent_role"),
                    "profile": metadata.get("remote_profile"),
                }
            ]
        for profile_item in profile_items:
            profile = profile_item.get("profile")
            if not isinstance(profile, dict):
                continue
            attributes = profile.get("attributes") or {}
            llm_usage = attributes.get("llm_usage") or []
            if not isinstance(llm_usage, list):
                continue
            for item in llm_usage:
                if not isinstance(item, dict):
                    continue
                enriched = dict(item)
                enriched.setdefault("agent_id", profile_item.get("agent_id"))
                enriched.setdefault("agent_role", profile_item.get("agent_role"))
                collected.append(enriched)
    return collected


def _collect_remote_profiles(responses: list[DepartmentResponse] | None) -> list[dict]:
    """Collect remote profiler snapshots from A2A agent responses."""
    collected: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for response in responses or []:
        metadata = response.metadata or {}
        profile_items = [
            item for item in metadata.get("remote_profiles") or []
            if isinstance(item, dict)
        ]
        if not profile_items and isinstance(metadata.get("remote_profile"), dict):
            profile_items = [
                {
                    "agent_id": metadata.get("remote_agent_id"),
                    "agent_role": metadata.get("remote_agent_role"),
                    "profile": metadata.get("remote_profile"),
                }
            ]
        for item in profile_items:
            profile = item.get("profile")
            if not isinstance(profile, dict):
                continue
            key = (
                str(item.get("agent_id") or ""),
                str(profile.get("label") or profile.get("total_ms") or len(collected)),
            )
            if key in seen:
                continue
            seen.add(key)
            collected.append(dict(item))
    return collected


def _build_query_diagnostics(
    responses: list[DepartmentResponse] | None = None,
) -> QueryDiagnostics | None:
    """Surface local and remote profiler-level LLM usage in API/test responses."""
    profiler = get_current_profiler()
    local_profile = profiler.snapshot() if profiler is not None else None
    llm_usage = profiler.get_attribute("llm_usage", []) if profiler is not None else []
    if not isinstance(llm_usage, list):
        llm_usage = []
    sanitized = [dict(item) for item in llm_usage if isinstance(item, dict)]
    sanitized.extend(_collect_remote_llm_usage(responses))
    remote_profiles = _collect_remote_profiles(responses)
    if not sanitized and not remote_profiles and not local_profile:
        return None
    return QueryDiagnostics(
        llm_usage=sanitized,
        local_profile=local_profile,
        remote_profiles=remote_profiles,
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
        diagnostics=_build_query_diagnostics(),
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
    surface_responses = list(department_responses or responses)
    if department_responses:
        seen_surface_departments = set(collect_surface_departments(surface_responses))
        for response in responses:
            response_departments = collect_surface_departments([response])
            if any(department not in seen_surface_departments for department in response_departments):
                surface_responses.append(response)
                seen_surface_departments.update(response_departments)
    cleaned_answer = clean_final_answer(answer)
    cleaned_answer = append_generation_summary(cleaned_answer, responses)
    cleaned_answer = append_source_summary(cleaned_answer, responses)
    personalized_answer = personalize_answer(cleaned_answer, student_full_name)
    sources = [source for response in responses for source in response.sources]
    generation_modes = collect_generation_modes(responses)
    if used_global_synthesis and "llm" not in generation_modes:
        generation_modes = ["llm", *generation_modes]
    diagnostic_responses = list(responses)
    for response in department_responses:
        if all(response is not existing for existing in diagnostic_responses):
            diagnostic_responses.append(response)
    return UserQueryResponse(
        answer=personalized_answer,
        departments_involved=collect_surface_departments(surface_responses),
        generation_modes=generation_modes,
        sources=sources,
        response_time_ms=response_time_ms,
        query_id=context_id,
        diagnostics=_build_query_diagnostics(responses=diagnostic_responses),
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
        diagnostics=_build_query_diagnostics(),
    )


def build_event_user_response(
    *,
    context_id: str,
    answer: str,
    sources,
    response_time_ms: float,
) -> UserQueryResponse:
    departments_involved = [EVENT_SURFACE_DEPARTMENT]
    answer = clean_final_answer(answer)
    if sources:
        answer = append_source_summary_for_sources(answer, sources)
    elif "Kaynak Ozeti:" not in answer:
        answer = (
            f"{answer.rstrip()}\n\n"
            "Kaynak Ozeti:\n"
            "- Veritabani kaydi: etkinlik aramasi (uygun kayit bulunamadi)"
        )
    return UserQueryResponse(
        answer=answer,
        departments_involved=departments_involved,
        generation_modes=["vt"],
        sources=sources,
        response_time_ms=response_time_ms,
        query_id=context_id,
        diagnostics=_build_query_diagnostics(),
    )
