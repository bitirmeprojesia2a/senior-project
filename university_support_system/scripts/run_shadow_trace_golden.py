"""Run a small architecture-focused golden set with shadow decision traces.

This runner is intentionally different from the quality benchmark. It is not
trying to score final answer quality first; it is designed to inspect routing,
source ownership, capability selection, follow-up handling, auth guards, and
LLM call budget through the DecisionTrace JSONL channel.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from src.core.console import configure_utf8_stdio

configure_utf8_stdio()

# Set before importing settings/MainOrchestrator, then reinforce at runtime.
_RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
_DEFAULT_TRACE_PATH = _ROOT / "tmp" / f"shadow_decision_trace_golden_{_RUN_ID}.jsonl"
os.environ.setdefault("DECISION_TRACE_ENABLED", "true")
os.environ.setdefault("DECISION_TRACE_OUTPUT_PATH", str(_DEFAULT_TRACE_PATH))
os.environ.setdefault("DECISION_TRACE_INCLUDE_ANSWER_PREVIEW", "false")

from src.core.config import settings
from src.core.profiling import QueryProfiler, activate_profiler
from src.db.connection import init_engine
from src.db.conversation_context import ConversationContextService
from src.llm.llm_service import LLMService
from src.orchestrators.main import MainOrchestrator
from src.quality.answer_filter import check_answer_quality
from src.rag.retriever import HybridRetriever
from src.startup.warmup import resolve_warmup_collections, resolve_warmup_llm_roles

BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
SEP = "-" * 88


@dataclass(frozen=True)
class GoldenCase:
    id: str
    family: str
    query: str
    expected_owner: str | None = None
    expected_capability: str | None = None
    expected_primary_department: str | None = None
    expected_primary_specialist: str | None = None
    context_key: str | None = None
    note: str = ""
    is_authenticated: bool = False
    profile: dict[str, str] = field(default_factory=dict)


DEFAULT_PROFILE = {
    "student_number": "22000001",
    "student_full_name": "Benchmark Ogrenci",
    "student_department": "Bilgisayar Muhendisligi",
    "student_faculty": "Muhendislik Fakultesi",
    "student_type": "Turk ogrenci",
}


GOLDEN_CASES: tuple[GoldenCase, ...] = (
    GoldenCase(
        id="GT01",
        family="academic_calendar",
        query="Final sinavlari ne zaman basliyor?",
        expected_owner="academic_calendar",
        expected_capability="calendar.academic_date",
        note="Structured calendar vs RAG/announcement ayrimi.",
    ),
    GoldenCase(
        id="GT02",
        family="curriculum",
        query="BIL203 dersinin AKTS'si ve on kosulu nedir?",
        expected_owner="curriculum_catalog",
        expected_capability="course.detail",
        expected_primary_department="academic_programs",
        expected_primary_specialist="curriculum_agent",
        note="Ders katalog/curriculum capability sinyali.",
    ),
    GoldenCase(
        id="GT03",
        family="finance",
        query="Bilgisayar Muhendisligi ikinci ogretim harc ucreti ne kadar?",
        expected_owner="tuition_fee_catalog",
        expected_capability="finance.tuition_fee",
        expected_primary_department="finance",
        expected_primary_specialist="tuition_agent",
        note="Ucret rakami structured finance katalogundan gelmeli.",
    ),
    GoldenCase(
        id="GT04",
        family="student_affairs_policy",
        query="Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?",
        expected_owner="student_affairs_policy",
        expected_capability="student_affairs.policy_lookup",
        expected_primary_department="student_affairs",
        expected_primary_specialist="registration_agent",
        note="Policy RAG + sure/slot sinyali.",
    ),
    GoldenCase(
        id="GT05",
        family="cross_department",
        query="CAP basvuru sartlari neler ve harc borcumu nasil odeyebilirim?",
        expected_owner=None,
        note="Academic + finance parallel karar ve final owner.",
    ),
    GoldenCase(
        id="GT06",
        family="international_policy",
        query="Yabanci ogrenci kayit belgeleri ve ikamet izni icin neler gerekir?",
        expected_owner="international_policy",
        expected_capability="international.policy_lookup",
        expected_primary_department="academic_programs",
        expected_primary_specialist="international_agent",
        note="International policy lookup ve kaynak secimi.",
        profile={"student_type": "Yabanci uyruklu ogrenci"},
    ),
    GoldenCase(
        id="GT07",
        family="announcement",
        query="Bilgisayar muhendisligindeki son duyurular neler?",
        expected_owner="announcement_search",
        expected_primary_department="announcement",
        note="Announcement DB short-circuit ve bolum filtresi.",
    ),
    GoldenCase(
        id="GT08",
        family="event",
        query="Bu hafta Muhendislik Fakultesinde seminer var mi?",
        expected_owner="event_search",
        expected_primary_department="event",
        note="Event DB short-circuit ve zaman penceresi.",
    ),
    GoldenCase(
        id="GT09",
        family="personal_auth",
        query="Harc borcum var mi?",
        expected_owner="personal_student_data",
        note="Auth gerektiren kisisel veri guard'i.",
        profile={},
    ),
    GoldenCase(
        id="GT10",
        family="ambiguous",
        query="Sey basvuru ne zaman?",
        expected_owner=None,
        note="Eksik slot/ambiguity davranisi.",
    ),
    GoldenCase(
        id="GT11",
        family="follow_up_seed",
        query="CAP basvurusu nasil yapilir?",
        expected_owner="student_affairs_policy",
        expected_capability="student_affairs.policy_lookup",
        expected_primary_department="student_affairs",
        expected_primary_specialist="registration_agent",
        context_key="cap-followup",
        note="Follow-up icin seed soru.",
    ),
    GoldenCase(
        id="GT12",
        family="follow_up_resolution",
        query="Peki not ortalamasi kac olmali?",
        expected_owner="student_affairs_policy",
        expected_capability="student_affairs.policy_lookup",
        expected_primary_department="student_affairs",
        expected_primary_specialist="registration_agent",
        context_key="cap-followup",
        note="Onceki CAP baglamina baglanmali.",
    ),
)
FAIL_SET_CASE_IDS = ("GT06", "GT07", "GT08", "GT09", "GT12")
CASE_DEPENDENCIES: dict[str, tuple[str, ...]] = {
    "GT12": ("GT11",),
}
PROVIDER_ROLES = (
    "routing",
    "conversation",
    "query_expansion",
    "evidence_selection",
    "final_refinement",
    "specialist_synthesis",
    "global_synthesis",
    "judge",
)
WARMUP_MODES = ("none", "retrieval", "llm", "full")
RETRYABLE_PROVIDER_ERROR_MARKERS = (
    "429",
    "rate_limit",
    "rate limit",
    "json_validate_failed",
    "failed to generate json",
    "timeout",
    "connection",
    "all connection attempts failed",
)


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(level=level, force=True)
    logging.getLogger("sqlalchemy").setLevel(logging.ERROR)
    try:
        import structlog

        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(level),
        )
    except Exception:
        pass


def _trace_owner(record: dict[str, Any] | None) -> str | None:
    contract = (record or {}).get("shadow_decision_contract") or {}
    return ((contract.get("source_owner") or {}).get("primary") or None)


def _trace_capability(record: dict[str, Any] | None) -> str | None:
    contract = (record or {}).get("shadow_decision_contract") or {}
    return ((contract.get("capabilities") or {}).get("selected") or None)


def _trace_final_owner(record: dict[str, Any] | None) -> str | None:
    contract = (record or {}).get("shadow_decision_contract") or {}
    return ((contract.get("answer") or {}).get("final_owner") or None)


def _trace_departments(record: dict[str, Any] | None) -> list[str]:
    runtime = (record or {}).get("runtime") or {}
    return list(runtime.get("selected_departments") or [])


def _trace_selected_specialists(record: dict[str, Any] | None) -> list[str]:
    runtime = (record or {}).get("runtime") or {}
    return list(runtime.get("selected_specialists") or [])


def _trace_specialist_selections(record: dict[str, Any] | None) -> list[dict[str, Any]]:
    runtime = (record or {}).get("runtime") or {}
    selections = runtime.get("specialist_selections") or []
    if not isinstance(selections, list):
        return []
    return [selection for selection in selections if isinstance(selection, dict)]


def _trace_branch_gate(record: dict[str, Any] | None) -> dict[str, Any]:
    runtime = (record or {}).get("runtime") or {}
    gate = runtime.get("branch_dispatch_gate") or {}
    return gate if isinstance(gate, dict) else {}


def _trace_response_filter(record: dict[str, Any] | None) -> dict[str, Any]:
    runtime = (record or {}).get("runtime") or {}
    response_filter = runtime.get("response_filter") or {}
    return response_filter if isinstance(response_filter, dict) else {}


def _format_branch_gate_summary(gate: dict[str, Any]) -> str:
    if not gate:
        return "-"
    kept = ", ".join(gate.get("kept_departments") or []) or "-"
    pruned = ", ".join(gate.get("pruned_departments") or []) or "-"
    reason = gate.get("reason") or "-"
    applied = "applied" if gate.get("applied") else "observed"
    return f"{applied}: kept={kept}; pruned={pruned}; reason={reason}"


def _format_response_filter_summary(response_filter: dict[str, Any]) -> str:
    if not response_filter:
        return "-"
    kept = response_filter.get("kept_count")
    dropped = response_filter.get("dropped_count")
    primary = response_filter.get("primary_department") or "-"
    dropped_departments = [
        str(item.get("department"))
        for item in response_filter.get("dropped") or []
        if isinstance(item, dict) and item.get("department")
    ]
    dropped_text = ", ".join(dropped_departments) or "-"
    return f"kept={kept}; dropped={dropped} ({dropped_text}); primary={primary}"


def _specialist_selector_mismatch_count(selections: list[dict[str, Any]]) -> int:
    count = 0
    for selection in selections:
        legacy = selection.get("legacy_keyword") or {}
        if not isinstance(legacy, dict):
            continue
        if legacy.get("agent_id") and legacy.get("matches_selected") is False:
            count += 1
    return count


def _format_specialist_selection_summary(selections: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for selection in selections:
        department = selection.get("department") or "?"
        selected = selection.get("selected_agent_id") or "?"
        selected_by = selection.get("selected_by") or "?"
        legacy = selection.get("legacy_keyword") or {}
        legacy_suffix = ""
        if isinstance(legacy, dict) and legacy.get("agent_id"):
            match = legacy.get("matches_selected")
            marker = "match" if match is True else "diff" if match is False else "unknown"
            legacy_suffix = f", legacy={legacy.get('agent_id')}:{marker}"
        parts.append(f"{department}:{selected}/{selected_by}{legacy_suffix}")
    return "; ".join(parts) or "-"


def _trace_response_ms(record: dict[str, Any] | None) -> float | None:
    runtime = (record or {}).get("runtime") or {}
    value = runtime.get("response_time_ms")
    try:
        return float(value) if value is not None else None
    except Exception:
        return None


def _trace_llm_usage(record: dict[str, Any] | None) -> list[dict[str, Any]]:
    usage = (record or {}).get("llm_usage") or []
    return list(usage) if isinstance(usage, list) else []


def _trace_judge_result(record: dict[str, Any] | None) -> dict[str, Any]:
    value = (record or {}).get("judge_result") or {}
    return dict(value) if isinstance(value, dict) else {}


def _trace_answer_validation(record: dict[str, Any] | None) -> dict[str, Any]:
    value = (record or {}).get("answer_validation_result") or {}
    return dict(value) if isinstance(value, dict) else {}


def _trace_answer_coverage(record: dict[str, Any] | None) -> dict[str, Any]:
    value = (record or {}).get("answer_coverage_result") or {}
    return dict(value) if isinstance(value, dict) else {}


def _trace_answer_value_conflict(record: dict[str, Any] | None) -> dict[str, Any]:
    value = (record or {}).get("answer_value_conflict_result") or {}
    return dict(value) if isinstance(value, dict) else {}


def _trace_retrieval_execution(record: dict[str, Any] | None) -> list[dict[str, Any]]:
    runtime = (record or {}).get("runtime") or {}
    items = runtime.get("retrieval_execution") or []
    if not isinstance(items, list):
        return []
    return [dict(item) for item in items if isinstance(item, dict)]


def _format_retrieval_execution_summary(items: list[dict[str, Any]]) -> str:
    if not items:
        return "-"
    parts: list[str] = []
    for item in items[:3]:
        policy = item.get("policy") if isinstance(item.get("policy"), dict) else {}
        role = policy.get("branch_role") or item.get("branch_role") or "?"
        specialist = item.get("specialist") or "?"
        searches = item.get("search_calls")
        variants = item.get("multi_query_variant_count")
        early = item.get("early_stop_reason") or "-"
        lite = "lite" if policy.get("support_lite") or item.get("support_lite_applied") else "full"
        parts.append(f"{role}:{specialist}:{lite}; searches={searches}; mqe={variants}; early={early}")
    return "; ".join(parts)


def _format_answer_validation_summary(validation: dict[str, Any]) -> str:
    if not validation:
        return "-"
    status = str(validation.get("status") or "?")
    mode = str(validation.get("mode") or "?")
    reason = str(validation.get("reason") or "-")
    missing = ", ".join(str(item) for item in validation.get("missing_values") or [])
    if missing:
        return f"{mode}/{status}:{reason}; missing={missing}"
    return f"{mode}/{status}:{reason}"


def _format_answer_coverage_summary(coverage: dict[str, Any]) -> str:
    if not coverage:
        return "-"
    status = str(coverage.get("status") or "?")
    mode = str(coverage.get("mode") or "?")
    facet = str(coverage.get("expected_facet") or "-")
    reason = str(coverage.get("reason") or "-")
    return f"{mode}/{status}:{facet}:{reason}"


def _format_answer_value_conflict_summary(conflict: dict[str, Any]) -> str:
    if not conflict:
        return "-"
    status = str(conflict.get("status") or "?")
    mode = str(conflict.get("mode") or "?")
    reason = str(conflict.get("reason") or "-")
    primary = str(conflict.get("primary_answer_value") or "-")
    competing = ", ".join(str(item) for item in conflict.get("competing_values") or []) or "-"
    return f"{mode}/{status}:{reason}; primary={primary}; competing={competing}"


def _format_judge_repair_summary(judge: dict[str, Any]) -> str:
    if not judge:
        return "-"
    repair = judge.get("repair")
    if not isinstance(repair, dict):
        action = str(judge.get("action") or "-")
        approved = judge.get("approved")
        if approved is None and action == "-":
            return "-"
        return f"judge:{action}; approved={approved}"
    accepted = repair.get("accepted")
    outcome = str(repair.get("outcome") or ("accepted" if accepted else "rejected"))
    reason = str(repair.get("rejection_reason") or repair.get("reason") or "-")
    return f"repair:{outcome}:{reason}"


_EXTRA_FOREIGN_TOKEN_MARKERS = (
    "departamento",
    "alumno",
    "alumnoğuz",
    "necessarytir",
)


def _answer_quality_shadow(answer_preview: str | None) -> dict[str, Any]:
    text = str(answer_preview or "")
    if not text.strip():
        return {}
    answer_body = _answer_body_for_quality(text)
    quality = check_answer_quality(answer_body)
    normalized = answer_body.lower()
    extra_tokens = [
        marker
        for marker in _EXTRA_FOREIGN_TOKEN_MARKERS
        if marker.lower() in normalized
    ]
    boilerplate = _has_boilerplate_shadow(text)
    issues = list(quality.detected_issues)
    if extra_tokens and "foreign_token_shadow" not in issues:
        issues.append("foreign_token_shadow")
    if boilerplate and "boilerplate_shadow" not in issues:
        issues.append("boilerplate_shadow")
    status = "check" if quality.needs_rewrite or extra_tokens or boilerplate else "pass"
    return {
        "mode": "shadow",
        "status": status,
        "reason": "answer_quality_issue" if status == "check" else "clean",
        "issues": issues,
        "bad_tokens": list(dict.fromkeys([*quality.bad_tokens, *extra_tokens]))[:8],
        "foreign_token_shadow": bool(extra_tokens or quality.has_suspicious_english),
        "encoding_noise_shadow": quality.has_foreign_script,
        "boilerplate_shadow": boilerplate,
    }


def _has_boilerplate_shadow(text: str) -> bool:
    normalized = " ".join(text.lower().split())
    return any(
        marker in normalized
        for marker in (
            "daha iyi yardımcı olabilmem",
            "daha iyi yardimci olabilmem",
            "iletişim bilgisi",
            "iletisim bilgisi",
        )
    )


def _answer_body_for_quality(text: str) -> str:
    for marker in ("\n\n---", "\n\nÜretim Türü", "\n\nUretim Turu"):
        if marker in text:
            return text.split(marker, 1)[0]
    return text


def _format_answer_quality_summary(quality: dict[str, Any]) -> str:
    if not quality:
        return "-"
    status = str(quality.get("status") or "?")
    mode = str(quality.get("mode") or "?")
    tokens = ", ".join(str(item) for item in quality.get("bad_tokens") or []) or "-"
    return f"{mode}/{status}:{quality.get('reason') or '-'}; tokens={tokens}"


def _expand_case_dependencies(cases: list[GoldenCase]) -> list[GoldenCase]:
    by_id = {case.id.upper(): case for case in GOLDEN_CASES}
    selected_ids = {case.id.upper() for case in cases}
    expanded: list[GoldenCase] = []
    added: set[str] = set()
    for case in cases:
        for dependency_id in CASE_DEPENDENCIES.get(case.id.upper(), ()):
            if dependency_id not in selected_ids and dependency_id not in added:
                dependency = by_id.get(dependency_id)
                if dependency is not None:
                    expanded.append(dependency)
                    added.add(dependency_id)
        if case.id.upper() not in added:
            expanded.append(case)
            added.add(case.id.upper())
    return expanded


def _answer_validation_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    stats = {
        "total": 0,
        "pass": 0,
        "check": 0,
        "fail": 0,
        "requires_judge": 0,
        "enforceable_by_contract": 0,
    }
    by_reason: dict[str, int] = {}
    for row in rows:
        validation = row.get("answer_validation") or {}
        if not isinstance(validation, dict) or not validation:
            continue
        stats["total"] += 1
        status = str(validation.get("status") or "")
        if status in {"pass", "check", "fail"}:
            stats[status] += 1
        if validation.get("requires_judge"):
            stats["requires_judge"] += 1
        if validation.get("enforceable_by_contract"):
            stats["enforceable_by_contract"] += 1
        reason = str(validation.get("reason") or "-")
        by_reason[reason] = by_reason.get(reason, 0) + 1
    stats["by_reason"] = by_reason
    return stats


def _answer_value_conflict_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    stats = {
        "total": 0,
        "pass": 0,
        "check": 0,
        "skipped": 0,
        "by_reason": {},
    }
    by_reason: dict[str, int] = {}
    for row in rows:
        conflict = row.get("answer_value_conflict") or {}
        if not isinstance(conflict, dict) or not conflict:
            continue
        stats["total"] += 1
        status = str(conflict.get("status") or "")
        if status in {"pass", "check", "skipped"}:
            stats[status] += 1
        reason = str(conflict.get("reason") or "-")
        by_reason[reason] = by_reason.get(reason, 0) + 1
    stats["by_reason"] = by_reason
    return stats


def _classify_provider_error(message: str) -> str:
    lowered = message.lower()
    if "429" in lowered or "rate_limit" in lowered or "rate limit" in lowered:
        return "rate_limit"
    if "json_validate_failed" in lowered or "failed to generate json" in lowered:
        return "json_validate_failed"
    if "timeout" in lowered or "timed out" in lowered:
        return "timeout"
    if "connection" in lowered or "all connection attempts failed" in lowered:
        return "connection"
    return "other"


def _provider_error_stats(
    rows: list[dict[str, Any]],
    *,
    include_llm_usage: bool = True,
    include_retry_attempts: bool = True,
) -> dict[str, Any]:
    stats: dict[str, Any] = {
        "total": 0,
        "by_provider": {},
        "by_reason": {},
        "retryable": 0,
    }
    for row in rows:
        if include_llm_usage:
            for item in row.get("llm_usage") or []:
                if item.get("status") != "error":
                    continue
                provider = str(item.get("provider_label") or item.get("provider") or "?")
                message = str(item.get("error_message") or item.get("error_type") or "")
                reason = _classify_provider_error(message)
                stats["total"] += 1
                stats["by_provider"][provider] = stats["by_provider"].get(provider, 0) + 1
                stats["by_reason"][reason] = stats["by_reason"].get(reason, 0) + 1
                if _is_retryable_provider_error(item):
                    stats["retryable"] += 1
        if include_retry_attempts:
            for attempt in row.get("provider_retry_attempts") or []:
                if not isinstance(attempt, dict):
                    continue
                for error in attempt.get("provider_errors") or []:
                    if not isinstance(error, dict):
                        continue
                    provider = str(error.get("provider") or "?")
                    reason = str(error.get("reason") or "other")
                    stats["total"] += 1
                    stats["by_provider"][provider] = stats["by_provider"].get(provider, 0) + 1
                    stats["by_reason"][reason] = stats["by_reason"].get(reason, 0) + 1
                    if attempt.get("retryable_provider_error"):
                        stats["retryable"] += 1
    return stats


def _llm_token_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    stats: dict[str, Any] = {
        "calls_with_estimate": 0,
        "estimated_input_tokens": 0,
        "prompt_chars": 0,
        "system_chars": 0,
        "by_role": {},
    }
    for row in rows:
        for item in row.get("llm_usage") or []:
            if not isinstance(item, dict):
                continue
            estimated = item.get("estimated_input_tokens")
            prompt_chars = item.get("prompt_chars")
            system_chars = item.get("system_chars")
            if estimated is None and prompt_chars is None and system_chars is None:
                continue
            role = str(item.get("model_role") or "default")
            role_stats = stats["by_role"].setdefault(
                role,
                {
                    "calls_with_estimate": 0,
                    "estimated_input_tokens": 0,
                    "prompt_chars": 0,
                    "system_chars": 0,
                },
            )
            stats["calls_with_estimate"] += 1
            role_stats["calls_with_estimate"] += 1
            if estimated is not None:
                value = int(estimated)
                stats["estimated_input_tokens"] += value
                role_stats["estimated_input_tokens"] += value
            if prompt_chars is not None:
                value = int(prompt_chars)
                stats["prompt_chars"] += value
                role_stats["prompt_chars"] += value
            if system_chars is not None:
                value = int(system_chars)
                stats["system_chars"] += value
                role_stats["system_chars"] += value
    return stats


def _llm_key_distribution(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_provider: dict[str, dict[str, Any]] = {}
    orgs: dict[str, int] = {}
    missing = 0
    for row in rows:
        for item in row.get("llm_usage") or []:
            if not isinstance(item, dict):
                continue
            provider = str(item.get("provider_label") or item.get("provider") or "?")
            fingerprint = item.get("api_key_fingerprint")
            if not fingerprint:
                missing += 1
                continue
            provider_stats = by_provider.setdefault(
                provider,
                {
                    "calls": 0,
                    "key_count": item.get("api_key_count"),
                    "by_fingerprint": {},
                },
            )
            provider_stats["calls"] += 1
            if item.get("api_key_count") is not None:
                provider_stats["key_count"] = item.get("api_key_count")
            key = str(fingerprint)
            provider_stats["by_fingerprint"][key] = (
                provider_stats["by_fingerprint"].get(key, 0) + 1
            )
            org = item.get("provider_org_fingerprint")
            if org:
                org_key = str(org)
                orgs[org_key] = orgs.get(org_key, 0) + 1
    return {
        "by_provider": by_provider,
        "provider_org_fingerprints": orgs,
        "missing_fingerprint_calls": missing,
    }


def _is_retryable_provider_error(item: dict[str, Any]) -> bool:
    if item.get("status") != "error":
        return False
    haystack = " ".join(
        str(item.get(key) or "")
        for key in ("error_message", "error_type", "provider_label", "provider")
    ).lower()
    return any(marker in haystack for marker in RETRYABLE_PROVIDER_ERROR_MARKERS)


def _row_has_retryable_provider_error(row: dict[str, Any]) -> bool:
    return any(
        _is_retryable_provider_error(item)
        for item in (row.get("llm_usage") or [])
        if isinstance(item, dict)
    )


def _timeout_signals(record: dict[str, Any] | None) -> dict[str, Any]:
    if not record:
        return {}
    breakdown = record.get("latency_breakdown") or {}
    if not isinstance(breakdown, dict):
        return {}

    def _float_ms(key: str) -> float | None:
        try:
            value = breakdown.get(key)
            return float(value) if value is not None else None
        except Exception:
            return None

    capability_ms = _float_ms("main.capability_planner")
    routing_ms = _float_ms("main.router.route")
    conversation_ms = _float_ms("main.conversation.resolve")
    final_synthesis_ms = _float_ms("main.final_llm_synthesis")
    capability_budget_ms = float(settings.capability_planner.timeout_seconds) * 1000.0
    routing_budget_ms = 12000.0

    return {
        "capability_planner_ms": capability_ms,
        "capability_planner_timeout_suspected": (
            capability_ms is not None and capability_ms >= capability_budget_ms * 0.90
        ),
        "routing_ms": routing_ms,
        "routing_timeout_suspected": routing_ms is not None and routing_ms >= routing_budget_ms * 0.90,
        "conversation_ms": conversation_ms,
        "final_synthesis_ms": final_synthesis_ms,
    }


def _timeout_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    stats = {
        "capability_planner_timeout_suspected": 0,
        "routing_timeout_suspected": 0,
        "first_case_latency_ms": None,
    }
    if rows:
        stats["first_case_latency_ms"] = rows[0].get("trace_response_time_ms") or rows[0].get("response_time_ms")
    for row in rows:
        signals = row.get("timeout_signals") or {}
        if signals.get("capability_planner_timeout_suspected"):
            stats["capability_planner_timeout_suspected"] += 1
        if signals.get("routing_timeout_suspected"):
            stats["routing_timeout_suspected"] += 1
    return stats


def _has_provider_error(row: dict[str, Any]) -> bool:
    return any(
        isinstance(item, dict) and item.get("status") == "error"
        for item in (row.get("llm_usage") or [])
    )


def _has_blocking_provider_error(row: dict[str, Any]) -> bool:
    return any(
        isinstance(item, dict)
        and item.get("status") == "error"
        and not _is_retryable_provider_error(item)
        for item in (row.get("llm_usage") or [])
    )


def _provider_warning_summary(row: dict[str, Any]) -> str:
    warnings: list[str] = []
    retryable_final = [
        item
        for item in (row.get("llm_usage") or [])
        if isinstance(item, dict)
        and item.get("status") == "error"
        and _is_retryable_provider_error(item)
    ]
    if retryable_final:
        warnings.append(f"final_retryable={len(retryable_final)}")
    retry_attempt_errors = sum(
        len(attempt.get("provider_errors") or [])
        for attempt in (row.get("provider_retry_attempts") or [])
        if isinstance(attempt, dict)
    )
    if retry_attempt_errors:
        warnings.append(f"retry_history={retry_attempt_errors}")
    return "; ".join(warnings) if warnings else "-"


def _primary_department_has_evidence(row: dict[str, Any], department: str) -> bool:
    response_filter = row.get("trace_response_filter") or {}
    if not isinstance(response_filter, dict):
        return False
    for item in response_filter.get("kept") or []:
        if not isinstance(item, dict):
            continue
        if item.get("department") != department:
            continue
        if item.get("source_owner_primary") or item.get("has_source_owner_evidence"):
            return True
    return False


def _has_specialist_for_department(
    row: dict[str, Any],
    *,
    department: str | None,
    specialist: str,
) -> bool:
    for selection in row.get("trace_specialist_selections") or []:
        if not isinstance(selection, dict):
            continue
        if department and selection.get("department") != department:
            continue
        if selection.get("selected_agent_id") == specialist:
            return True
    return False


def _has_missing_specialist_selector_diagnostics(row: dict[str, Any]) -> bool:
    for selection in row.get("trace_specialist_selections") or []:
        if not isinstance(selection, dict):
            continue
        selected_agent = str(selection.get("selected_agent_id") or "").strip()
        if not selected_agent:
            continue
        selected_by = str(selection.get("selected_by") or "").strip().lower()
        reason = str(selection.get("reason") or "").strip().lower()
        if selected_by == "unknown" or reason == "response_metadata_without_selector_diagnostics":
            return True
    return False


_BRANCH_TIMEOUT_MARKERS = (
    "timeout",
    "readtimeout",
    "a2a_transport_timeout",
    "a2a_specialist_transport_timeout",
)


def _is_branch_timeout_error(value: Any) -> bool:
    text = str(value or "").strip().lower()
    if not text:
        return False
    return any(marker in text for marker in _BRANCH_TIMEOUT_MARKERS)


def _branch_timeout_issues(row: dict[str, Any]) -> list[str]:
    response_filter = row.get("trace_response_filter") or {}
    if not isinstance(response_filter, dict):
        return []

    issues: list[str] = []
    for item in response_filter.get("kept") or []:
        if not isinstance(item, dict):
            continue
        if item.get("success") is not False:
            continue
        error = item.get("error")
        if not _is_branch_timeout_error(error):
            continue
        department = str(item.get("department") or "-")
        issue_name = "primary_branch_timeout" if item.get("source_owner_primary") else "branch_timeout"
        issues.append(f"{issue_name} department={department} error={str(error or '-')[:80]}")
    return issues


def _structural_issues(row: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    issues.extend(_branch_timeout_issues(row))

    expected_capability = row.get("expected_capability")
    if expected_capability and row.get("trace_capability") != expected_capability:
        issues.append(
            f"capability expected={expected_capability} actual={row.get('trace_capability') or '-'}"
        )

    expected_department = row.get("expected_primary_department")
    if expected_department:
        trace_departments = row.get("trace_departments") or []
        if expected_department not in trace_departments and not _primary_department_has_evidence(
            row,
            expected_department,
        ):
            issues.append(
                "primary_department "
                f"expected={expected_department} actual={', '.join(trace_departments) or '-'}"
            )

    expected_specialist = row.get("expected_primary_specialist")
    if expected_specialist and not _has_specialist_for_department(
        row,
        department=expected_department,
        specialist=expected_specialist,
    ):
        issues.append(
            "primary_specialist "
            f"expected={expected_specialist} actual={', '.join(row.get('trace_selected_specialists') or []) or '-'}"
        )

    if _row_has_retryable_provider_error(row):
        issues.append("provider_retryable_error_seen")
    if _has_blocking_provider_error(row):
        issues.append("provider_error_seen")
    if _has_missing_specialist_selector_diagnostics(row):
        issues.append("specialist_selector_diagnostics_missing")
    return issues


def _format_structural_issues(row: dict[str, Any]) -> str:
    issues = _structural_issues(row)
    return "; ".join(issues) if issues else "-"


def _row_status(row: dict[str, Any]) -> str:
    if row.get("error"):
        return "ERROR"
    validation = row.get("answer_validation") or {}
    if isinstance(validation, dict):
        validation_status = validation.get("status")
        if validation_status == "fail":
            return "FAIL"
        if validation_status == "check":
            return "CHECK"
    coverage = row.get("answer_coverage") or {}
    if isinstance(coverage, dict) and coverage.get("status") == "check":
        return "CHECK"
    value_conflict = row.get("answer_value_conflict") or {}
    if isinstance(value_conflict, dict) and value_conflict.get("status") == "check":
        return "CHECK"
    if row.get("expected_owner") and row.get("trace_owner") != row.get("expected_owner"):
        return "CHECK"
    if _structural_issues(row):
        return "CHECK"
    return "OK"


def _load_trace_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            records.append(payload)
    return records


def _match_record_by_context(records: list[dict[str, Any]], context_id: str) -> dict[str, Any] | None:
    for record in reversed(records):
        if record.get("context_id") == context_id:
            return record
    return None


async def _run_case(
    *,
    orchestrator: MainOrchestrator,
    case: GoldenCase,
    context_id: str,
    llm_profile: str | None,
    disable_cache: bool,
    answer_preview_chars: int,
) -> dict[str, Any]:
    profile = dict(DEFAULT_PROFILE)
    profile.update(case.profile)
    start = time.perf_counter()
    profiler = QueryProfiler(label=f"shadow_golden_{case.id}")
    try:
        with activate_profiler(profiler):
            response = await orchestrator.handle_query(
                case.query,
                context_id=context_id,
                llm_profile=llm_profile,
                is_authenticated=case.is_authenticated,
                student_number=profile.get("student_number"),
                student_full_name=profile.get("student_full_name"),
                student_department=profile.get("student_department"),
                student_faculty=profile.get("student_faculty"),
                student_type=profile.get("student_type"),
                disable_cache=disable_cache,
            )
        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        answer = response.answer or ""
        preview_limit = max(0, answer_preview_chars)
        return {
            "id": case.id,
            "family": case.family,
            "query": case.query,
            "context_id": context_id,
            "expected_owner": case.expected_owner,
            "expected_capability": case.expected_capability,
            "expected_primary_department": case.expected_primary_department,
            "expected_primary_specialist": case.expected_primary_specialist,
            "departments": list(response.departments_involved or []),
            "generation_modes": list(response.generation_modes or []),
            "source_count": len(response.sources or []),
            "elapsed_ms": elapsed_ms,
            "response_time_ms": response.response_time_ms,
            "answer_preview": answer[:preview_limit] + ("..." if len(answer) > preview_limit else ""),
            "error": None,
            "note": case.note,
        }
    except Exception as exc:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        return {
            "id": case.id,
            "family": case.family,
            "query": case.query,
            "context_id": context_id,
            "expected_owner": case.expected_owner,
            "expected_capability": case.expected_capability,
            "expected_primary_department": case.expected_primary_department,
            "expected_primary_specialist": case.expected_primary_specialist,
            "departments": [],
            "generation_modes": [],
            "source_count": 0,
            "elapsed_ms": elapsed_ms,
            "response_time_ms": None,
            "answer_preview": "",
            "error": f"{type(exc).__name__}: {exc}",
            "note": case.note,
        }


async def _run_warmup(mode: str, *, llm_profile: str | None) -> dict[str, Any]:
    normalized_mode = (mode or "none").strip().lower()
    if normalized_mode not in WARMUP_MODES:
        raise ValueError(f"Unsupported warmup mode: {mode}")

    started = time.perf_counter()
    summary: dict[str, Any] = {
        "mode": normalized_mode,
        "elapsed_ms": 0.0,
        "retrieval": {"enabled": False, "status": "skipped"},
        "llm": {"enabled": False, "status": "skipped"},
    }
    if normalized_mode == "none":
        return summary

    if normalized_mode in {"retrieval", "full"}:
        retrieval_started = time.perf_counter()
        collections = resolve_warmup_collections()
        retrieval_summary = {
            "enabled": True,
            "status": "ok",
            "collections": collections,
            "include_reranker": settings.server.warmup_include_reranker,
            "elapsed_ms": 0.0,
        }
        try:
            HybridRetriever.prewarm(
                collections,
                k=settings.rag.top_k,
                include_reranker=settings.server.warmup_include_reranker,
            )
        except Exception as exc:
            retrieval_summary["status"] = "error"
            retrieval_summary["error_type"] = type(exc).__name__
            retrieval_summary["error"] = str(exc)
        retrieval_summary["elapsed_ms"] = round((time.perf_counter() - retrieval_started) * 1000, 1)
        summary["retrieval"] = retrieval_summary

    if normalized_mode in {"llm", "full"}:
        llm_started = time.perf_counter()
        roles = resolve_warmup_llm_roles()
        role_results: list[dict[str, Any]] = []
        llm_summary = {
            "enabled": True,
            "status": "ok",
            "roles": roles,
            "role_results": role_results,
            "llm_profile": llm_profile or settings.normalize_llm_profile(settings.llm.profile),
            "timeout_seconds": settings.server.warmup_llm_timeout_seconds,
            "elapsed_ms": 0.0,
        }
        service = LLMService()
        timeout_seconds = max(1, settings.server.warmup_llm_timeout_seconds)
        prompt = settings.server.warmup_llm_prompt.strip() or "Yalnizca OK yaz."
        for role in roles:
            role_started = time.perf_counter()
            result = {
                "role": role,
                "status": "ok",
                "elapsed_ms": 0.0,
            }
            try:
                await asyncio.wait_for(
                    service.generate(
                        prompt=prompt,
                        system="Cevap olarak sadece OK yaz.",
                        model_role=role,
                        llm_profile=llm_profile,
                    ),
                    timeout=timeout_seconds,
                )
            except Exception as exc:
                result["status"] = "error"
                result["error_type"] = type(exc).__name__
                result["error"] = str(exc)
                llm_summary["status"] = "error"
            result["elapsed_ms"] = round((time.perf_counter() - role_started) * 1000, 1)
            role_results.append(result)
        llm_summary["elapsed_ms"] = round((time.perf_counter() - llm_started) * 1000, 1)
        summary["llm"] = llm_summary

    summary["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 1)
    return summary


def _hydrate_row_from_trace(row: dict[str, Any], record: dict[str, Any] | None) -> dict[str, Any]:
    row["trace_owner"] = _trace_owner(record)
    row["trace_capability"] = _trace_capability(record)
    row["trace_final_owner"] = _trace_final_owner(record)
    row["trace_departments"] = _trace_departments(record)
    row["trace_selected_specialists"] = _trace_selected_specialists(record)
    row["trace_specialist_selections"] = _trace_specialist_selections(record)
    row["trace_specialist_selection_summary"] = _format_specialist_selection_summary(
        row["trace_specialist_selections"]
    )
    row["trace_specialist_selector_mismatches"] = _specialist_selector_mismatch_count(
        row["trace_specialist_selections"]
    )
    row["trace_branch_gate"] = _trace_branch_gate(record)
    row["trace_branch_gate_summary"] = _format_branch_gate_summary(
        row["trace_branch_gate"]
    )
    row["trace_response_filter"] = _trace_response_filter(record)
    row["trace_response_filter_summary"] = _format_response_filter_summary(
        row["trace_response_filter"]
    )
    row["trace_response_time_ms"] = _trace_response_ms(record)
    row["judge_result"] = _trace_judge_result(record)
    row["judge_repair_summary"] = _format_judge_repair_summary(row["judge_result"])
    row["answer_validation"] = _trace_answer_validation(record)
    row["answer_validation_summary"] = _format_answer_validation_summary(
        row["answer_validation"]
    )
    row["answer_coverage"] = _trace_answer_coverage(record)
    row["answer_coverage_summary"] = _format_answer_coverage_summary(
        row["answer_coverage"]
    )
    row["answer_value_conflict"] = _trace_answer_value_conflict(record)
    row["answer_value_conflict_summary"] = _format_answer_value_conflict_summary(
        row["answer_value_conflict"]
    )
    row["retrieval_execution"] = _trace_retrieval_execution(record)
    row["retrieval_execution_summary"] = _format_retrieval_execution_summary(
        row["retrieval_execution"]
    )
    row["answer_quality"] = _answer_quality_shadow(row.get("answer_preview"))
    row["answer_quality_summary"] = _format_answer_quality_summary(row["answer_quality"])
    row["llm_call_count"] = record.get("llm_call_count") if record else None
    row["llm_roles_used"] = record.get("llm_roles_used") if record else []
    row["llm_usage"] = _trace_llm_usage(record)
    row["timeout_signals"] = _timeout_signals(record)
    row["trace_recorded"] = record is not None
    return row


async def _run_case_with_retries(
    *,
    orchestrator: MainOrchestrator,
    case: GoldenCase,
    context_id: str,
    llm_profile: str | None,
    disable_cache: bool,
    answer_preview_chars: int,
    trace_path: Path,
    provider_retry_count: int,
    provider_retry_backoff: float,
    preserve_context_on_retry: bool,
) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    max_attempts = max(0, provider_retry_count) + 1
    current_context_id = context_id
    selected_row: dict[str, Any] | None = None

    for attempt_index in range(max_attempts):
        if attempt_index > 0 and not preserve_context_on_retry:
            current_context_id = f"{context_id}-retry{attempt_index}"
        if attempt_index > 0 and provider_retry_backoff > 0:
            await asyncio.sleep(provider_retry_backoff)

        row = await _run_case(
            orchestrator=orchestrator,
            case=case,
            context_id=current_context_id,
            llm_profile=llm_profile,
            disable_cache=disable_cache,
            answer_preview_chars=answer_preview_chars,
        )
        trace_records = _load_trace_records(trace_path)
        record = _match_record_by_context(trace_records, current_context_id)
        row = _hydrate_row_from_trace(row, record)
        row["attempt"] = attempt_index + 1
        attempts.append(
            {
                "attempt": attempt_index + 1,
                "context_id": current_context_id,
                "status": _row_status(row),
                "retryable_provider_error": _row_has_retryable_provider_error(row),
                "provider_errors": [
                    {
                        "provider": item.get("provider_label") or item.get("provider"),
                        "role": item.get("model_role"),
                        "reason": _classify_provider_error(
                            str(item.get("error_message") or item.get("error_type") or "")
                        ),
                    }
                    for item in row.get("llm_usage") or []
                    if isinstance(item, dict) and item.get("status") == "error"
                ],
            }
        )
        selected_row = row

        retryable = _row_has_retryable_provider_error(row)
        row_status = _row_status(row)
        should_retry = retryable and attempt_index < max_attempts - 1
        if row_status == "OK":
            should_retry = False
        if not should_retry:
            break

    assert selected_row is not None
    selected_row["provider_retry_attempts"] = attempts
    selected_row["provider_retry_count"] = max(0, len(attempts) - 1)
    selected_row["provider_retryable_error_seen"] = any(
        bool(attempt.get("retryable_provider_error")) for attempt in attempts
    )
    selected_row["provider_warning_summary"] = _provider_warning_summary(selected_row)
    return selected_row


def _markdown_report(
    *,
    run_id: str,
    trace_path: Path,
    results_path: Path,
    rows: list[dict[str, Any]],
    trace_records: list[dict[str, Any]],
    llm_profile: str | None,
    disable_cache: bool,
    warmup_summary: dict[str, Any],
    provider_retry: dict[str, Any],
) -> str:
    ok_owner = 0
    checked_owner = 0
    errors = 0
    answer_validation_risks = 0
    value_conflict_risks = 0
    structural_risks = 0
    for row in rows:
        if row.get("error"):
            errors += 1
        validation = row.get("answer_validation") or {}
        if isinstance(validation, dict) and validation.get("status") in {"check", "fail"}:
            answer_validation_risks += 1
        value_conflict = row.get("answer_value_conflict") or {}
        if isinstance(value_conflict, dict) and value_conflict.get("status") == "check":
            value_conflict_risks += 1
        if _structural_issues(row):
            structural_risks += 1
        expected = row.get("expected_owner")
        owner = row.get("trace_owner")
        if expected:
            checked_owner += 1
            if owner == expected:
                ok_owner += 1

    lines = [
        f"# Shadow Decision Trace Golden Run {run_id}",
        "",
        "Bu rapor kalite benchmark'i degil; karar mimarisi gozlem raporudur.",
        "",
        "## Ozet",
        "",
        f"- Sorgu sayisi: {len(rows)}",
        f"- Trace kaydi: {len(trace_records)}",
        f"- Source owner eslesmesi: {ok_owner}/{checked_owner}",
        f"- Hata sayisi: {errors}",
        f"- Answer validator riskli: {answer_validation_risks}",
        f"- Value conflict riskli: {value_conflict_risks}",
        f"- Structural check riskli: {structural_risks}",
        f"- LLM profile: {llm_profile or 'default'}",
        f"- Question cache: {'bypass' if disable_cache else 'allowed'}",
        f"- Warmup mode: {warmup_summary.get('mode', 'none')} ({float(warmup_summary.get('elapsed_ms') or 0.0):.1f} ms)",
        f"- Provider retry: count={provider_retry.get('count', 0)} backoff={provider_retry.get('backoff_seconds', 0)}s",
        f"- Trace JSONL: `{trace_path}`",
        f"- Makine okunabilir sonuc: `{results_path}`",
        "",
        "## Sorgu Tablosu",
        "",
        "| ID | Aile | Expected Owner | Trace Owner | Capability | Final Owner | Dept | Specialist Selector | Mismatch | Branch Gate | Retrieval Budget | Answer Check | Coverage | Value Conflict | Judge Repair | Provider Warn | Quality | Primary Value | Competing Values | Structure | LLM Calls | Sure ms | Durum |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in rows:
        status = _row_status(row)
        response_ms = row.get("trace_response_time_ms")
        if response_ms is None:
            response_ms = row.get("response_time_ms") or row.get("elapsed_ms")
        lines.append(
            "| {id} | {family} | {expected} | {owner} | {capability} | {final_owner} | {dept} | {selector} | {selector_mismatch} | {branch_gate} | {retrieval_budget} | {answer_check} | {coverage} | {value_conflict} | {judge_repair} | {provider_warn} | {quality} | {primary_value} | {competing_values} | {structure} | {llm_calls} | {ms} | {status} |".format(
                id=row.get("id"),
                family=row.get("family"),
                expected=row.get("expected_owner") or "-",
                owner=row.get("trace_owner") or "-",
                capability=row.get("trace_capability") or "-",
                final_owner=row.get("trace_final_owner") or "-",
                dept=", ".join(row.get("trace_departments") or row.get("departments") or []) or "-",
                selector=row.get("trace_specialist_selection_summary") or "-",
                selector_mismatch=row.get("trace_specialist_selector_mismatches") or 0,
                branch_gate=row.get("trace_branch_gate_summary") or "-",
                retrieval_budget=row.get("retrieval_execution_summary") or "-",
                answer_check=row.get("answer_validation_summary") or "-",
                coverage=row.get("answer_coverage_summary") or "-",
                value_conflict=row.get("answer_value_conflict_summary") or "-",
                judge_repair=row.get("judge_repair_summary") or "-",
                provider_warn=row.get("provider_warning_summary") or _provider_warning_summary(row),
                quality=row.get("answer_quality_summary") or "-",
                primary_value=(row.get("answer_value_conflict") or {}).get("primary_answer_value") or "-",
                competing_values=", ".join(
                    str(item) for item in (row.get("answer_value_conflict") or {}).get("competing_values") or []
                )
                or "-",
                structure=row.get("structural_summary") or _format_structural_issues(row),
                llm_calls=row.get("llm_call_count") if row.get("llm_call_count") is not None else 0,
                ms=f"{float(response_ms):.1f}" if response_ms is not None else "-",
                status=status,
            )
        )

    provider_counts: dict[str, int] = {}
    provider_errors: dict[str, int] = {}
    fallback_count = 0
    for row in rows:
        for item in row.get("llm_usage") or []:
            provider = str(item.get("provider_label") or item.get("provider") or "?")
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
            if item.get("status") == "error":
                provider_errors[provider] = provider_errors.get(provider, 0) + 1
            if item.get("path") == "fallback":
                fallback_count += 1

    if provider_counts:
        provider_error_stats = _provider_error_stats(rows)
        final_provider_error_stats = _provider_error_stats(rows, include_retry_attempts=False)
        retry_provider_error_stats = _provider_error_stats(rows, include_llm_usage=False)
        token_stats = _llm_token_stats(rows)
        key_distribution = _llm_key_distribution(rows)
        token_lines: list[str] = []
        if token_stats["calls_with_estimate"]:
            token_lines = [
                f"- Tahmini input token: {token_stats['estimated_input_tokens']} "
                f"({token_stats['calls_with_estimate']} cagrida)",
                f"- Prompt/system char: {token_stats['prompt_chars']}/{token_stats['system_chars']}",
                "- Role bazli cagri sayisi: "
                + (
                    ", ".join(
                        f"{role}={data['calls_with_estimate']}"
                        for role, data in sorted(token_stats["by_role"].items())
                    )
                    or "-"
                ),
                "- Role bazli tahmini input token: "
                + (
                    ", ".join(
                        f"{role}={data['estimated_input_tokens']}"
                        for role, data in sorted(token_stats["by_role"].items())
                    )
                    or "-"
                ),
            ]
        lines.extend(
            [
                "",
                "## LLM Kullanim Ozeti",
                "",
                f"- Provider cagrilari: {', '.join(f'{name}={count}' for name, count in provider_counts.items())}",
                f"- Provider hatalari: {', '.join(f'{name}={count}' for name, count in provider_errors.items()) or '-'}",
                f"- Fallback cagrilari: {fallback_count}",
                f"- Final attempt provider hata sayisi: {final_provider_error_stats['total']}",
                f"- Retry history provider hata sayisi: {retry_provider_error_stats['total']}",
                "- Provider hata nedenleri: "
                + (
                    ", ".join(
                        f"{reason}={count}"
                        for reason, count in sorted(provider_error_stats["by_reason"].items())
                    )
                    or "-"
                ),
                f"- Retryable provider hata sayisi: {provider_error_stats['retryable']}",
                *token_lines,
            ]
        )
        if key_distribution["by_provider"] or key_distribution["missing_fingerprint_calls"]:
            key_lines = []
            for provider, data in sorted(key_distribution["by_provider"].items()):
                key_lines.append(
                    f"{provider}: calls={data['calls']} configured_keys={data.get('key_count') or '-'} "
                    f"used_keys={len(data['by_fingerprint'])}"
                )
            lines.extend(
                [
                    "",
                    "## API Key Dagilimi",
                    "",
                    "- Provider/key dagilimi: " + (", ".join(key_lines) or "-"),
                    "- Key fingerprint cagrilari: "
                    + json.dumps(key_distribution["by_provider"], ensure_ascii=False),
                    "- Provider org fingerprintleri: "
                    + (
                        ", ".join(
                            f"{fingerprint}={count}"
                            for fingerprint, count in sorted(
                                key_distribution["provider_org_fingerprints"].items()
                            )
                        )
                        or "-"
                    ),
                    f"- Fingerprint eksik cagrilar: {key_distribution['missing_fingerprint_calls']}",
                ]
            )

    timeout_stats = _timeout_stats(rows)
    lines.extend(
        [
            "",
            "## Warmup ve Timeout Ozeti",
            "",
            f"- Warmup: `{json.dumps(warmup_summary, ensure_ascii=False)}`",
            f"- First-case latency ms: `{timeout_stats.get('first_case_latency_ms') or '-'}`",
            (
                "- Timeout sinyalleri: "
                f"capability_planner={timeout_stats['capability_planner_timeout_suspected']}, "
                f"routing={timeout_stats['routing_timeout_suspected']}"
            ),
        ]
    )

    validator_stats = _answer_validation_stats(rows)
    if validator_stats["total"]:
        lines.extend(
            [
                "",
                "## Answer Validator Ozeti",
                "",
                (
                    f"- Kayit: {validator_stats['total']} | pass={validator_stats['pass']} "
                    f"| check={validator_stats['check']} | fail={validator_stats['fail']} "
                    f"| requires_judge={validator_stats['requires_judge']} "
                    f"| contract_enforceable={validator_stats['enforceable_by_contract']}"
                ),
                "- Nedenler: "
                + (
                    ", ".join(
                        f"{reason}={count}"
                        for reason, count in sorted(validator_stats["by_reason"].items())
                    )
                    or "-"
                ),
            ]
        )

    conflict_stats = _answer_value_conflict_stats(rows)
    if conflict_stats["total"]:
        lines.extend(
            [
                "",
                "## Value Conflict Ozeti",
                "",
                (
                    f"- Kayit: {conflict_stats['total']} | pass={conflict_stats['pass']} "
                    f"| check={conflict_stats['check']} | skipped={conflict_stats['skipped']}"
                ),
                "- Nedenler: "
                + (
                    ", ".join(
                        f"{reason}={count}"
                        for reason, count in sorted(conflict_stats["by_reason"].items())
                    )
                    or "-"
                ),
            ]
        )

    lines.extend(["", "## Notlar", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row.get('id')} - {row.get('family')}",
                "",
                f"- Soru: {row.get('query')}",
                f"- Not: {row.get('note')}",
                f"- Context: `{row.get('context_id')}`",
                f"- Trace owner: `{row.get('trace_owner') or '-'}`",
                f"- Capability: `{row.get('trace_capability') or '-'}`",
                f"- Selected specialists: `{', '.join(row.get('trace_selected_specialists') or []) or '-'}`",
                f"- Specialist selector: `{row.get('trace_specialist_selection_summary') or '-'}`",
                f"- Branch gate: `{row.get('trace_branch_gate_summary') or '-'}`",
                f"- Response filter: `{row.get('trace_response_filter_summary') or '-'}`",
                f"- Answer validator: `{row.get('answer_validation_summary') or '-'}`",
                f"- Answer coverage: `{row.get('answer_coverage_summary') or '-'}`",
                f"- Value conflict: `{row.get('answer_value_conflict_summary') or '-'}`",
                f"- Judge repair: `{row.get('judge_repair_summary') or '-'}`",
                f"- Provider warning: `{row.get('provider_warning_summary') or _provider_warning_summary(row)}`",
                f"- Answer quality: `{row.get('answer_quality_summary') or '-'}`",
                f"- Structural checks: `{row.get('structural_summary') or _format_structural_issues(row)}`",
                f"- LLM roles: `{', '.join(row.get('llm_roles_used') or []) or '-'}`",
                f"- LLM usage: `{_format_llm_usage(row.get('llm_usage') or [])}`",
                f"- Provider retry attempts: `{json.dumps(row.get('provider_retry_attempts') or [], ensure_ascii=False)}`",
                f"- Timeout signals: `{json.dumps(row.get('timeout_signals') or {}, ensure_ascii=False)}`",
            ]
        )
        if row.get("error"):
            lines.append(f"- Hata: `{row['error']}`")
        else:
            preview = " ".join(str(row.get("answer_preview") or "").split())
            lines.append(f"- Cevap preview: {preview}")
        lines.append("")
    return "\n".join(lines)


def _format_llm_usage(usage: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for item in usage:
        provider = item.get("provider_label") or item.get("provider") or "?"
        model = item.get("model") or "?"
        role = item.get("model_role") or "default"
        path = item.get("path") or "?"
        status = item.get("status") or "?"
        token_suffix = ""
        if item.get("estimated_input_tokens") is not None:
            token_suffix = f"/in_tok~{item.get('estimated_input_tokens')}"
        parts.append(f"{provider}/{model}/{role}/{path}/{status}{token_suffix}")
    return "; ".join(parts) or "-"


def _apply_llm_provider_override(provider: str | None, fallback_provider: str | None) -> None:
    """Apply a per-run provider override without editing .env."""
    if not provider:
        return
    settings.llm.primary_provider = provider  # type: ignore[assignment]
    settings.llm.fallback_provider = fallback_provider or "none"  # type: ignore[assignment]
    for role in PROVIDER_ROLES:
        setattr(settings.llm, f"{role}_provider", provider)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run shadow decision trace golden set")
    parser.add_argument("--case", nargs="+", default=[], help="Run only selected case ids, e.g. GT01 GT07")
    parser.add_argument("--fail-set", action="store_true", help="Run only current CHECK cases: GT06 GT07 GT08 GT09 GT12")
    parser.add_argument("--limit", type=int, default=0, help="Run only first N selected cases")
    parser.add_argument("--llm-profile", default="balanced", help="fast | balanced | quality")
    parser.add_argument(
        "--llm-provider",
        choices=["openai_compatible", "google_ai", "anthropic"],
        default=None,
        help="Temporarily force all LLM roles to one provider for this run.",
    )
    parser.add_argument(
        "--fallback-provider",
        choices=["none", "openai_compatible", "google_ai", "anthropic"],
        default=None,
        help="Fallback provider for this run. Defaults to none when --llm-provider is used.",
    )
    parser.add_argument("--allow-cache", action="store_true", help="Allow question cache during the run")
    parser.add_argument("--sleep", type=float, default=2.0, help="Seconds to wait between cases")
    parser.add_argument(
        "--warmup-mode",
        choices=list(WARMUP_MODES),
        default="none",
        help="Best-effort pre-run warmup: none, retrieval, llm, or full.",
    )
    parser.add_argument(
        "--provider-retry-count",
        type=int,
        default=0,
        help="Case-level retries for retryable provider errors. Runtime LLM retry behavior is not changed.",
    )
    parser.add_argument(
        "--provider-retry-backoff",
        type=float,
        default=0.0,
        help="Seconds to wait before a provider-error case retry.",
    )
    parser.add_argument("--answer-preview-chars", type=int, default=1000, help="Answer preview length written to reports")
    parser.add_argument("--trace-path", default=str(_DEFAULT_TRACE_PATH), help="Decision trace JSONL path")
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser


async def async_main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    _configure_logging(args.verbose)
    _apply_llm_provider_override(args.llm_provider, args.fallback_provider)
    init_engine(echo=args.verbose)

    trace_path = Path(args.trace_path)
    if not trace_path.is_absolute():
        trace_path = _ROOT / trace_path
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    trace_path.unlink(missing_ok=True)

    settings.decision_trace.enabled = True
    settings.decision_trace.output_path = trace_path
    settings.decision_trace.include_answer_preview = False

    selected = list(GOLDEN_CASES)
    if args.fail_set:
        wanted = set(FAIL_SET_CASE_IDS)
        selected = [case for case in selected if case.id in wanted]
    if args.case:
        wanted = {case_id.upper() for case_id in args.case}
        selected = [case for case in selected if case.id.upper() in wanted]
        selected = _expand_case_dependencies(selected)
    if args.limit and args.limit > 0:
        selected = selected[: args.limit]
    if not selected:
        raise SystemExit("No golden cases selected.")

    run_id = trace_path.stem.replace("shadow_decision_trace_golden_", "") or _RUN_ID
    report_dir = _ROOT / "docs" / "archive" / "benchmarks"
    results_dir = _ROOT / "tests" / "archive" / "benchmarks"
    report_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)
    results_path = results_dir / f"shadow_decision_trace_golden_{run_id}.json"
    report_path = report_dir / f"shadow_decision_trace_golden_{run_id}.md"

    print(f"{BOLD}Shadow Decision Trace Golden{RESET}")
    print(f"Run id: {run_id}")
    print(f"Cases: {len(selected)}")
    print(f"Trace: {trace_path}")
    print(f"A2A mode: {settings.a2a.mode}")
    print(f"LLM provider: primary={settings.llm.primary_provider} fallback={settings.llm.fallback_provider}")
    print(f"Capability planner: mode={settings.capability_planner.mode} scope={settings.capability_planner.scope}")
    print(f"Question cache: {'allowed' if args.allow_cache else 'bypass'}")
    print(f"Warmup mode: {args.warmup_mode}")
    print(f"Provider retry: count={max(0, args.provider_retry_count)} backoff={max(0.0, args.provider_retry_backoff)}s")
    print(SEP)

    warmup_summary = await _run_warmup(args.warmup_mode, llm_profile=args.llm_profile or None)
    if args.warmup_mode != "none":
        print(
            "Warmup: "
            f"mode={warmup_summary.get('mode')} "
            f"elapsed_ms={warmup_summary.get('elapsed_ms')} "
            f"retrieval={warmup_summary.get('retrieval', {}).get('status')} "
            f"llm={warmup_summary.get('llm', {}).get('status')}"
        )

    orchestrator = MainOrchestrator(conversation_service=ConversationContextService())
    context_ids: dict[str, str] = {}
    completed_context_keys: set[str] = set()
    rows: list[dict[str, Any]] = []
    disable_cache = not args.allow_cache

    for index, case in enumerate(selected, 1):
        context_key = case.context_key or case.id
        context_id = context_ids.setdefault(context_key, f"shadow-golden-{run_id}-{context_key}")
        print(f"\n{CYAN}[{case.id}]{RESET} {case.family}: {case.query}")
        preserve_context_on_retry = context_key in completed_context_keys
        row = await _run_case_with_retries(
            orchestrator=orchestrator,
            case=case,
            context_id=context_id,
            llm_profile=args.llm_profile or None,
            disable_cache=disable_cache,
            answer_preview_chars=args.answer_preview_chars,
            trace_path=trace_path,
            provider_retry_count=max(0, args.provider_retry_count),
            provider_retry_backoff=max(0.0, args.provider_retry_backoff),
            preserve_context_on_retry=preserve_context_on_retry,
        )
        context_ids[context_key] = str(row.get("context_id") or context_id)
        completed_context_keys.add(context_key)
        row["structural_issues"] = _structural_issues(row)
        row["structural_summary"] = _format_structural_issues(row)
        row["status"] = _row_status(row)
        rows.append(row)

        owner_label = row.get("trace_owner") or "?"
        status = row["status"]
        color = RED if status in {"ERROR", "FAIL"} else (GREEN if status == "OK" else YELLOW)
        print(
            f"  owner={owner_label} expected={case.expected_owner or '-'} "
            f"capability={row.get('trace_capability') or '-'} "
            f"final_owner={row.get('trace_final_owner') or '-'} "
            f"selector={row.get('trace_specialist_selection_summary') or '-'} "
            f"gate={row.get('trace_branch_gate_summary') or '-'} "
            f"answer_check={row.get('answer_validation_summary') or '-'} "
            f"value_conflict={row.get('answer_value_conflict_summary') or '-'} "
            f"retrieval={row.get('retrieval_execution_summary') or '-'} "
            f"structure={row.get('structural_summary') or '-'} "
            f"llm_calls={row.get('llm_call_count') or 0} "
            f"retry={row.get('provider_retry_count') or 0} "
            f"status={color}{status}{RESET}"
        )
        if row.get("error"):
            print(f"  {RED}{row['error']}{RESET}")
        if index < len(selected) and args.sleep > 0:
            await asyncio.sleep(args.sleep)

    trace_records = _load_trace_records(trace_path)
    payload = {
        "run_id": run_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "trace_path": str(trace_path),
        "report_path": str(report_path),
        "a2a_mode": settings.a2a.mode,
        "llm_provider": {
            "primary": settings.llm.primary_provider,
            "fallback": settings.llm.fallback_provider,
        },
        "capability_planner": {
            "mode": settings.capability_planner.mode,
            "scope": settings.capability_planner.scope,
        },
        "llm_profile": args.llm_profile or None,
        "question_cache": "allowed" if args.allow_cache else "bypass",
        "answer_preview_chars": args.answer_preview_chars,
        "warmup_summary": warmup_summary,
        "provider_retry": {
            "count": max(0, args.provider_retry_count),
            "backoff_seconds": max(0.0, args.provider_retry_backoff),
        },
        "provider_error_stats": _provider_error_stats(rows),
        "final_attempt_provider_error_stats": _provider_error_stats(rows, include_retry_attempts=False),
        "retry_history_provider_error_stats": _provider_error_stats(rows, include_llm_usage=False),
        "llm_key_distribution": _llm_key_distribution(rows),
        "timeout_stats": _timeout_stats(rows),
        "answer_validation_stats": _answer_validation_stats(rows),
        "answer_value_conflict_stats": _answer_value_conflict_stats(rows),
        "results": rows,
    }
    results_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    report_path.write_text(
        _markdown_report(
            run_id=run_id,
            trace_path=trace_path,
            results_path=results_path,
            rows=rows,
            trace_records=trace_records,
            llm_profile=args.llm_profile or None,
            disable_cache=disable_cache,
            warmup_summary=warmup_summary,
            provider_retry={
                "count": max(0, args.provider_retry_count),
                "backoff_seconds": max(0.0, args.provider_retry_backoff),
            },
        ),
        encoding="utf-8",
    )

    print(f"\n{SEP}")
    print(f"{BOLD}Tamamlandi.{RESET}")
    print(f"Trace records: {len(trace_records)}")
    print(f"Results JSON: {results_path}")
    print(f"Markdown report: {report_path}")


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
