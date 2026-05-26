"""Helpers for building user-facing orchestrator responses."""

from __future__ import annotations

from typing import Any

from src.core.config import settings
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
from src.quality.answer_style import record_answer_length_telemetry


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


def _selected_agent_id(response: DepartmentResponse) -> str:
    metadata = response.metadata or {}
    selection = metadata.get("specialist_selection")
    selection_agent_id = (
        selection.get("selected_agent_id")
        if isinstance(selection, dict)
        else None
    )
    return str(
        selection_agent_id
        or metadata.get("selected_agent_id")
        or metadata.get("agent_id")
        or response.department.value
    )


def _compact_source(source, *, response: DepartmentResponse) -> dict[str, Any]:
    metadata = source.metadata or {}
    return {
        "department": response.department.value,
        "agent": _selected_agent_id(response),
        "source": metadata.get("source") or metadata.get("file_name") or metadata.get("title"),
        "record_type": metadata.get("record_type"),
        "score": source.score,
        "score_type": metadata.get("score_type"),
        "source_owner": metadata.get("source_owner"),
        "chunk_index": metadata.get("chunk_index"),
        "bolum": metadata.get("bolum"),
        "bolum_adi": metadata.get("bolum_adi"),
        "source_ref": metadata.get("source_ref"),
        "cache_version": metadata.get("cache_version"),
    }


def _compact_contract(response: DepartmentResponse) -> dict[str, Any] | None:
    metadata = response.metadata or {}
    keys = (
        "answer_contract",
        "source_owner",
        "policy_facet",
        "capability",
        "capability_planner",
        "source_owner_primary",
        "final_answer_owner",
    )
    contract = {
        key: metadata.get(key)
        for key in keys
        if metadata.get(key) is not None
    }
    if not contract:
        return None
    contract["department"] = response.department.value
    contract["agent"] = _selected_agent_id(response)
    return contract


def _build_answer_debug_report(
    responses: list[DepartmentResponse] | None,
    *,
    local_profile: dict[str, Any] | None,
    remote_profiles: list[dict],
) -> dict[str, Any] | None:
    """Return a compact root-cause map for bad-answer triage."""

    responses = list(responses or [])
    if not responses and not local_profile and not remote_profiles:
        return None

    routes = [
        {
            "department": response.department.value,
            "agent": _selected_agent_id(response),
            "generation_mode": response.generation_mode,
            "success": response.success,
            "error": response.error,
            "source_count": len(response.sources),
        }
        for response in responses
    ]
    sources = [
        _compact_source(source, response=response)
        for response in responses
        for source in response.sources[:3]
    ][:12]
    contracts = [
        contract
        for response in responses
        for contract in [_compact_contract(response)]
        if contract is not None
    ]

    attributes = local_profile.get("attributes") if isinstance(local_profile, dict) else {}
    if not isinstance(attributes, dict):
        attributes = {}

    report: dict[str, Any] = {
        "schema": "omu.answer_debug_report.v1",
        "routes": routes,
        "sources": sources,
        "contracts": contracts,
    }
    for key in (
        "response_filter",
        "evidence_answer_validator",
        "answer_contract_validation",
        "branch_dispatch_gate",
        "conversation_context_audit",
        "multi_intent",
        "specialist_selector",
        "answer_length",
    ):
        if attributes.get(key) is not None:
            report[key] = attributes.get(key)
    if remote_profiles:
        report["remote_profile_count"] = len(remote_profiles)
    return report


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
    answer_debug_report = _build_answer_debug_report(
        responses,
        local_profile=local_profile,
        remote_profiles=remote_profiles,
    )
    if not sanitized and not remote_profiles and not local_profile and not answer_debug_report:
        return None
    return QueryDiagnostics(
        llm_usage=sanitized,
        local_profile=local_profile,
        remote_profiles=remote_profiles,
        answer_debug_report=answer_debug_report,
    )


def build_clarification_user_response(
    *,
    context_id: str,
    message: str,
    response_time_ms: float,
    full_name: str | None = None,
) -> UserQueryResponse:
    personalized_message = personalize_answer(message, full_name)
    record_answer_length_telemetry(answer=personalized_message)
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
    routing_strategy: str | None = None,
    agents_involved: list[str] | None = None,
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
    if settings.server.response_debug_enabled:
        cleaned_answer = append_generation_summary(
            cleaned_answer,
            responses,
            used_global_synthesis=used_global_synthesis,
            routing_strategy=routing_strategy,
            agents_involved=agents_involved,
        )
        cleaned_answer = append_source_summary(cleaned_answer, responses)
    personalized_answer = personalize_answer(cleaned_answer, student_full_name)
    record_answer_length_telemetry(answer=personalized_answer)
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
        agents_involved=agents_involved or [],
        routing_strategy=routing_strategy,
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
    if settings.server.response_debug_enabled:
        answer = append_source_summary_for_sources(answer, sources)
    record_answer_length_telemetry(answer=answer)
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
    if not settings.server.response_debug_enabled:
        pass
    elif sources:
        answer = append_source_summary_for_sources(answer, sources)
    elif "Kaynak Ozeti:" not in answer and "Kaynak Özeti:" not in answer:
        answer = (
            f"{answer.rstrip()}\n\n"
            "Kaynak Özeti:\n"
            "- Veritabanı kaydı: etkinlik araması (uygun kayıt bulunamadı)"
        )
    record_answer_length_telemetry(answer=answer)
    return UserQueryResponse(
        answer=answer,
        departments_involved=departments_involved,
        generation_modes=["vt"],
        sources=sources,
        response_time_ms=response_time_ms,
        query_id=context_id,
        diagnostics=_build_query_diagnostics(),
    )
