"""Helpers for dispatching work to department orchestrators."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

from src.a2a import extract_department_response
from src.a2a.transport import DepartmentTransport, build_department_transport
from src.core.constants import Department, RoutingStrategy, TaskType
from src.core.profiling import get_current_profiler
from src.core.retrieval_execution_policy import build_branch_retrieval_metadata
from src.core.source_ownership import resolve_source_owner_routing_policy
from src.core.text_normalization import normalize_text
from src.db.schemas import DepartmentResponse, RoutingResult
from src.orchestrators.department import (
    _extract_transport_diagnostics,
    _is_transport_error,
    _is_transport_timeout_error,
)
from src.orchestrators.multi_intent import MultiIntentPlan, MultiIntentSubtask
from src.routing.routing_policy import detect_task_type

logger = logging.getLogger(__name__)

BRANCH_DISPATCH_GATE_SCHEMA = "omu.branch_dispatch_gate.v1"

_ACADEMIC_POLICY_MARKERS = (
    "sart",
    "kosul",
    "uygun",
    "uygunluk",
    "gano",
    "gno",
    "not ortalamasi",
    "ortalama",
    "yuzdelik",
    "kontenjan",
    "akts",
    "kredi",
    "cap",
    "cift anadal",
    "yandal",
    "yan dal",
    "azami",
    "yonetmelik",
    "yonerge",
    "kural",
    "hak",
    "kac olmali",
    "olabilir miyim",
    "girebilir miyim",
)
_FINANCE_BRANCH_MARKERS = (
    "harc",
    "ucret",
    "odeme",
    "borc",
    "taksit",
    "dekont",
    "burs",
    "katki payi",
)
_STUDENT_AFFAIRS_BRANCH_MARKERS = (
    "kayit",
    "basvuru",
    "dilekce",
    "nereye",
    "ne zaman",
    "surec",
    "islem",
    "evrak",
    "belge",
    "muafiyet",
    "intibak",
)


@dataclass(frozen=True)
class _BranchDispatchPlan:
    orchestrators: list[Any]
    task_type_overrides: dict[Department, TaskType] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    force_parallel: bool = False


async def invoke_department_orchestrator(
    *,
    orchestrator: Any,
    transport: DepartmentTransport | None = None,
    query: str,
    context_id: str,
    task_type,
    metadata: dict,
    disable_specialist_llm: bool,
):
    """Send a single request task to a department orchestrator through transport."""
    active_transport = transport or build_department_transport()
    return await active_transport.dispatch(
        department=orchestrator.department,
        orchestrator=orchestrator,
        query=query,
        context_id=context_id,
        task_type=task_type,
        metadata=metadata,
        disable_specialist_llm=disable_specialist_llm,
    )


def _resolve_branch_task_type(
    *,
    query: str,
    department: Department,
    routed_task_type: TaskType | None,
) -> TaskType | None:
    """Recompute a task type for the target branch when possible.

    A single top-level routing task type is often too coarse for mixed
    department queries. Re-evaluating per branch keeps specialists closer to
    the question slice they are expected to answer, while still falling back
    to the original routed task type when no sharper signal exists.
    """

    return detect_task_type(query, [department]) or routed_task_type


def _branch_task_type(
    *,
    query: str,
    department: Department,
    routed_task_type: TaskType | None,
    overrides: dict[Department, TaskType],
) -> TaskType | None:
    return overrides.get(department) or _resolve_branch_task_type(
        query=query,
        department=department,
        routed_task_type=routed_task_type,
    )


def _build_branch_dispatch_plan(
    *,
    orchestrators: list[Any],
    department_orchestrators: dict | None = None,
    query: str,
    metadata: dict,
) -> _BranchDispatchPlan:
    capability = _extract_capability(metadata)
    source_owner = _extract_source_owner(metadata)
    original_departments = [
        orchestrator.department
        for orchestrator in orchestrators
        if isinstance(orchestrator.department, Department)
    ]
    restored_orchestrators, restored_departments, owner_routing_policy = _restore_owner_primary_branches(
        orchestrators=orchestrators,
        department_orchestrators=department_orchestrators or {},
        capability=capability,
        source_owner=source_owner,
    )
    orchestrators = restored_orchestrators
    departments = [
        orchestrator.department
        for orchestrator in orchestrators
        if isinstance(orchestrator.department, Department)
    ]
    diagnostics: dict[str, Any] = {
        "schema": BRANCH_DISPATCH_GATE_SCHEMA,
        "mode": "contract_branch_gate",
        "applied": bool(restored_departments),
        "original_departments": [department.value for department in original_departments],
        "restored_departments": [department.value for department in restored_departments],
    }
    if owner_routing_policy:
        diagnostics["owner_routing_policy"] = owner_routing_policy
        diagnostics["router_departments"] = [department.value for department in original_departments]
        diagnostics["restored_primary_department"] = owner_routing_policy.get("primary_department")
        diagnostics["support_departments"] = owner_routing_policy.get("support_departments") or []
    if len(departments) <= 1:
        diagnostics["reason"] = "single_branch"
        diagnostics["kept_departments"] = [department.value for department in departments]
        diagnostics["pruned_departments"] = []
        return _BranchDispatchPlan(orchestrators=orchestrators, diagnostics=diagnostics)

    semantic_text = _branch_semantic_text(query, metadata)
    allowed, reason, task_type_overrides = _allowed_departments_for_contract(
        capability=capability,
        source_owner=source_owner,
        semantic_text=semantic_text,
        departments=set(departments),
    )
    diagnostics.update(
        {
            "capability": capability,
            "source_owner": source_owner,
            "reason": reason,
            "task_type_overrides": {
                department.value: task_type.value
                for department, task_type in task_type_overrides.items()
            },
        }
    )
    if not allowed:
        diagnostics["kept_departments"] = [department.value for department in departments]
        diagnostics["pruned_departments"] = []
        return _BranchDispatchPlan(
            orchestrators=orchestrators,
            task_type_overrides=task_type_overrides,
            diagnostics=diagnostics,
        )

    allowed_departments = set(allowed)
    planned = [
        orchestrator
        for orchestrator in orchestrators
        if orchestrator.department in allowed_departments
    ]
    if not planned:
        diagnostics["reason"] = "gate_empty_intersection"
        diagnostics["kept_departments"] = [department.value for department in departments]
        diagnostics["pruned_departments"] = []
        return _BranchDispatchPlan(
            orchestrators=orchestrators,
            task_type_overrides=task_type_overrides,
            diagnostics=diagnostics,
        )

    kept = [orchestrator.department for orchestrator in planned]
    pruned = [department for department in departments if department not in set(kept)]
    diagnostics["kept_departments"] = [department.value for department in kept]
    diagnostics["pruned_departments"] = [department.value for department in pruned]
    diagnostics["applied"] = bool(pruned or restored_departments)
    return _BranchDispatchPlan(
        orchestrators=planned,
        task_type_overrides=task_type_overrides,
        diagnostics=diagnostics,
        force_parallel=bool(restored_departments and len(planned) > 1),
    )


def _restore_owner_primary_branches(
    *,
    orchestrators: list[Any],
    department_orchestrators: dict,
    capability: str | None,
    source_owner: str | None,
) -> tuple[list[Any], list[Department], dict[str, Any] | None]:
    capability_key = _selector_value(capability)
    owner_key = _selector_value(source_owner)
    if not owner_key:
        return orchestrators, [], None
    owner_policy = resolve_source_owner_routing_policy(
        source_owner=owner_key,
        capability=capability_key,
    )
    if owner_policy is None:
        return orchestrators, [], None

    departments = [
        orchestrator.department
        for orchestrator in orchestrators
        if isinstance(orchestrator.department, Department)
    ]
    department_set = set(departments)
    restored: list[Department] = []
    planned = list(orchestrators)
    department = owner_policy.primary_department
    if department not in department_set:
        orchestrator = department_orchestrators.get(department)
        if orchestrator is not None:
            planned.insert(0, orchestrator)
            department_set.add(department)
            restored.append(department)
    return planned, restored, owner_policy.to_metadata()


def _allowed_departments_for_contract(
    *,
    capability: str | None,
    source_owner: str | None,
    semantic_text: str,
    departments: set[Department],
) -> tuple[set[Department] | None, str, dict[Department, TaskType]]:
    task_type_overrides: dict[Department, TaskType] = {}
    capability_key = _selector_value(capability)
    owner_key = _selector_value(source_owner)
    owner_policy = resolve_source_owner_routing_policy(
        source_owner=owner_key,
        capability=capability_key,
    )

    if "graduation_akts" in semantic_text:
        allowed = {Department.STUDENT_AFFAIRS}
        if (
            Department.ACADEMIC_PROGRAMS in departments
            and (
                "special_long" in semantic_text
                or "requires_program_specific_verification" in semantic_text
                or "program_specific_requirement" in semantic_text
            )
        ):
            allowed.add(Department.ACADEMIC_PROGRAMS)
            task_type_overrides[Department.ACADEMIC_PROGRAMS] = TaskType.PROCEDURE_QUERY
            return allowed, "graduation_akts_program_specific_support_branch", task_type_overrides
        return allowed, "graduation_akts_policy_single_branch", task_type_overrides
    if owner_policy and owner_policy.source_owner == "academic_calendar":
        return {owner_policy.primary_department}, "calendar_owner_single_branch", task_type_overrides
    if owner_policy and owner_policy.source_owner == "international_policy":
        return {owner_policy.primary_department}, "international_policy_single_branch", task_type_overrides
    if owner_policy and owner_policy.source_owner == "tuition_fee_catalog":
        if _has_non_finance_compound_signal(semantic_text, departments) and _has_special_fee_or_process_scope(semantic_text):
            return None, "finance_owner_compound_query_keep_all", task_type_overrides
        return {owner_policy.primary_department}, "finance_owner_single_branch", task_type_overrides
    if (
        capability_key
        and (
            capability_key.startswith("course.")
            or capability_key.startswith("curriculum.")
            or capability_key == "schedule.weekly_program"
        )
    ) or (owner_policy and owner_policy.source_owner in {"curriculum_catalog", "weekly_schedule"}):
        if _has_cross_domain_compound_signal(semantic_text, departments):
            return None, "academic_owner_compound_query_keep_all", task_type_overrides
        department = owner_policy.primary_department if owner_policy else Department.ACADEMIC_PROGRAMS
        return {department}, "academic_catalog_single_branch", task_type_overrides
    if owner_policy and owner_policy.source_owner == "student_affairs_policy":
        allowed = {owner_policy.primary_department}
        if "cap_debt_eligibility" in semantic_text:
            if Department.ACADEMIC_PROGRAMS in departments:
                allowed.add(Department.ACADEMIC_PROGRAMS)
                task_type_overrides[Department.ACADEMIC_PROGRAMS] = TaskType.PROCEDURE_QUERY
            return allowed, "answer_contract_cap_debt_policy_gate", task_type_overrides
        if Department.ACADEMIC_PROGRAMS in departments and _needs_academic_policy_branch(semantic_text):
            allowed.add(Department.ACADEMIC_PROGRAMS)
            task_type_overrides[Department.ACADEMIC_PROGRAMS] = TaskType.PROCEDURE_QUERY
        if Department.FINANCE in departments and _contains_any(semantic_text, _FINANCE_BRANCH_MARKERS):
            allowed.add(Department.FINANCE)
        return allowed, "student_affairs_policy_contract_gate", task_type_overrides

    return None, "no_contract_gate", task_type_overrides


def _has_non_finance_compound_signal(semantic_text: str, departments: set[Department]) -> bool:
    if Department.ACADEMIC_PROGRAMS in departments and _needs_academic_policy_branch(semantic_text):
        return True
    return Department.STUDENT_AFFAIRS in departments and _contains_any(
        semantic_text,
        _STUDENT_AFFAIRS_BRANCH_MARKERS,
    )


def _has_special_fee_or_process_scope(semantic_text: str) -> bool:
    return _contains_any(
        semantic_text,
        (
            "yaz okulu",
            "yaz donemi",
            "cap",
            "cift anadal",
            "yandal",
            "erasmus",
            "iade",
            "borc",
            "basvuru",
            "uygunluk",
            "odeme yontemi",
        ),
    )


def _has_cross_domain_compound_signal(semantic_text: str, departments: set[Department]) -> bool:
    if Department.FINANCE in departments and _contains_any(semantic_text, _FINANCE_BRANCH_MARKERS):
        return True
    return Department.STUDENT_AFFAIRS in departments and _contains_any(
        semantic_text,
        _STUDENT_AFFAIRS_BRANCH_MARKERS,
    )


def _needs_academic_policy_branch(semantic_text: str) -> bool:
    return _contains_any(semantic_text, _ACADEMIC_POLICY_MARKERS)


def _branch_semantic_text(query: str, metadata: dict) -> str:
    parts = [query]
    planner = _as_dict(metadata.get("capability_planner"))
    action = _as_dict(planner.get("action"))
    for key in ("capability", "intent", "params", "answer_contract", "evidence_contract"):
        _collect_semantic_values(action.get(key), parts)
    authority = _as_dict(metadata.get("runtime_authority"))
    if authority:
        for key in ("contract", "capability", "source_owner"):
            _collect_semantic_values(authority.get(key), parts)
    else:
        resolved = _as_dict(metadata.get("resolved_decision"))
        if resolved:
            for key in ("contract", "capability", "source_owner"):
                _collect_semantic_values(resolved.get(key), parts)
        else:
            contract = _as_dict(_as_dict(metadata.get("decision_contract")).get("contract"))
            for key in ("intent", "capabilities", "source_owner", "retrieval", "evidence"):
                _collect_semantic_values(contract.get(key), parts)
    source_owner = _as_dict(metadata.get("source_owner"))
    _collect_semantic_values(source_owner.get("primary"), parts)
    _collect_semantic_values(metadata.get("policy_facet"), parts)
    return normalize_text(" ".join(parts))


def _extract_capability(metadata: dict) -> str | None:
    authority = _as_dict(metadata.get("runtime_authority"))
    if authority.get("capability"):
        return _selector_value(authority.get("capability"))
    planner = _as_dict(metadata.get("capability_planner"))
    action = _as_dict(planner.get("action"))
    capability = action.get("capability") or planner.get("capability")
    if capability:
        return _selector_value(capability)
    resolved = _as_dict(metadata.get("resolved_decision"))
    if resolved.get("capability"):
        return _selector_value(resolved.get("capability"))
    contract = _as_dict(_as_dict(metadata.get("decision_contract")).get("contract"))
    return _selector_value(_as_dict(contract.get("capabilities")).get("selected"))


def _extract_source_owner(metadata: dict) -> str | None:
    authority = _as_dict(metadata.get("runtime_authority"))
    if authority.get("source_owner"):
        return _selector_value(authority.get("source_owner"))
    source_owner = _as_dict(metadata.get("source_owner"))
    owner = source_owner.get("primary")
    if owner:
        return _selector_value(owner)
    resolved = _as_dict(metadata.get("resolved_decision"))
    if resolved.get("source_owner"):
        return _selector_value(resolved.get("source_owner"))
    contract = _as_dict(_as_dict(metadata.get("decision_contract")).get("contract"))
    return _selector_value(_as_dict(contract.get("source_owner")).get("primary"))


def _selector_value(value: Any) -> str | None:
    text = str(value or "").strip().lower()
    return text or None


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _collect_semantic_values(value: Any, parts: list[str]) -> None:
    if value is None:
        return
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).strip().lower() in {"query", "original_query", "resolved_query"}:
                continue
            parts.append(str(key))
            _collect_semantic_values(nested, parts)
        return
    if isinstance(value, (list, tuple, set)):
        for item in value:
            _collect_semantic_values(item, parts)
        return
    if isinstance(value, bool):
        return
    text = str(value).strip()
    if text:
        parts.append(text)


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    return any(normalize_text(marker) in text for marker in markers)


async def _try_branch_rag_fallback(
    *,
    orchestrator: Any,
    query: str,
    metadata: dict,
    original_error: str,
) -> DepartmentResponse | None:
    """Paralel dispatch'te A2A hatası durumunda RAG fallback dene."""
    from src.routing.routing_policy import looks_like_personal_data_query, has_payment_markers
    from src.core.text_normalization import normalize_text as _norm

    normalized = _norm(query)
    if looks_like_personal_data_query(query) or has_payment_markers(normalized):
        return None
    if _is_transport_timeout_error(original_error):
        logger.info(
            "branch_rag_fallback_skipped_timeout department=%s",
            getattr(orchestrator, 'department', '?'),
        )
        return None

    try:
        # Orchestrator'un _try_rag_fallback metodunu kullan
        if hasattr(orchestrator, '_try_rag_fallback'):
            agent = orchestrator._select_agent(None, query, metadata=metadata)
            return await orchestrator._try_rag_fallback(
                agent=agent,
                query_text=query,
                error_msg=original_error,
                metadata=metadata,
            )
    except Exception as exc:
        logger.warning("branch_rag_fallback_failed department=%s error=%s", 
                      getattr(orchestrator, 'department', '?'), exc)
    return None


async def dispatch_to_departments(
    *,
    department_orchestrators: dict,
    query: str,
    context_id: str,
    routing: RoutingResult,
    metadata: dict,
    transport: DepartmentTransport | None = None,
) -> list[DepartmentResponse]:
    """Dispatch a user query to the selected department orchestrators."""
    orchestrators = [
        department_orchestrators[department]
        for department in routing.departments
        if department in department_orchestrators
    ]

    if not orchestrators:
        return []

    metadata = dict(metadata or {})
    plan = _build_branch_dispatch_plan(
        orchestrators=orchestrators,
        department_orchestrators=department_orchestrators,
        query=query,
        metadata=metadata,
    )
    orchestrators = plan.orchestrators
    metadata["branch_dispatch_gate"] = plan.diagnostics
    profiler = get_current_profiler()
    if profiler is not None:
        profiler.set_attribute("branch_dispatch_gate", plan.diagnostics)

    active_transport = transport or build_department_transport()
    use_parallel = (
        (routing.strategy == RoutingStrategy.PARALLEL or plan.force_parallel)
        and len(orchestrators) > 1
    )
    # Multi-department sorularda maliyeti kontrol etmek icin branch uzman LLM
    # sentezini kapatip final/global sentezin cevaplari toplamasina izin veriyoruz.
    # Tek departmanda ise uzman LLM sentezi varsayilan olarak acik kalir.
    disable_specialist_llm = use_parallel

    if use_parallel:
        tasks = [
            invoke_department_orchestrator(
                orchestrator=orchestrator,
                transport=active_transport,
                query=query,
                context_id=context_id,
                task_type=_branch_task_type(
                    query=query,
                    department=orchestrator.department,
                    routed_task_type=routing.task_type,
                    overrides=plan.task_type_overrides,
                ),
                metadata=build_branch_retrieval_metadata(
                    department=orchestrator.department,
                    metadata=metadata,
                ),
                disable_specialist_llm=disable_specialist_llm,
            )
            for orchestrator in orchestrators
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        responses: list[DepartmentResponse] = []
        had_branch_failure = False
        for orchestrator, result in zip(orchestrators, results, strict=False):
            if not isinstance(result, Exception):
                parsed = extract_department_response(result)
                if parsed is not None:
                    # Başarısız specialist yanıtı (A2A hatası) — fallback dene
                    if not parsed.success and parsed.error and _is_transport_error(parsed.error):
                        if _is_transport_timeout_error(parsed.error):
                            parsed.metadata = dict(parsed.metadata or {})
                            parsed.metadata["fallback_skipped_reason"] = "transport_timeout"
                            parsed.metadata["branch_timeout"] = True
                            responses.append(parsed)
                            logger.warning(
                                "department_branch_a2a_timeout_no_rag_fallback department=%s error=%s",
                                orchestrator.department.value,
                                parsed.error[:100],
                            )
                            continue
                        logger.warning(
                            "department_branch_a2a_failed department=%s error=%s, attempting RAG fallback",
                            orchestrator.department.value,
                            parsed.error[:100],
                        )
                        fallback_diag = _extract_transport_diagnostics(parsed)
                        fallback = await _try_branch_rag_fallback(
                            orchestrator=orchestrator,
                            query=query,
                            metadata=build_branch_retrieval_metadata(
                                department=orchestrator.department,
                                metadata=metadata,
                            ),
                            original_error=parsed.error,
                        )
                        if fallback is not None:
                            fallback.metadata = dict(fallback.metadata or {})
                            fallback.metadata.update(fallback_diag)
                            fallback.metadata["fallback_from_error"] = True
                            responses.append(fallback)
                            continue
                    responses.append(parsed)
                    continue
                had_branch_failure = True
                logger.error(
                    "department_branch_invalid_response department=%s query=%r",
                    orchestrator.department.value,
                    query,
                )
                continue
            had_branch_failure = True
            logger.error(
                "department_branch_failed department=%s query=%r error=%s",
                orchestrator.department.value,
                query,
                result,
                exc_info=(type(result), result, result.__traceback__),
            )
        if not responses and had_branch_failure:
            raise RuntimeError(
                "Secili departman ajanlarindan gecerli yanit alinamadi."
            )
        return responses

    responses: list[DepartmentResponse] = []
    for orchestrator in orchestrators:
        response_task = await invoke_department_orchestrator(
            orchestrator=orchestrator,
            transport=active_transport,
            query=query,
            context_id=context_id,
            task_type=_branch_task_type(
                query=query,
                department=orchestrator.department,
                routed_task_type=routing.task_type,
                overrides=plan.task_type_overrides,
            ),
            metadata=build_branch_retrieval_metadata(
                department=orchestrator.department,
                metadata=metadata,
            ),
            disable_specialist_llm=disable_specialist_llm,
        )
        response = extract_department_response(response_task)
        if response is None:
            raise ValueError(
                f"{orchestrator.department.value} orchestrator gecerli department response dondurmedi."
            )
        # Başarısız specialist yanıtı (A2A hatası) — fallback dene
        if not response.success and response.error and _is_transport_error(response.error):
            if _is_transport_timeout_error(response.error):
                response.metadata = dict(response.metadata or {})
                response.metadata["fallback_skipped_reason"] = "transport_timeout"
                response.metadata["branch_timeout"] = True
                responses.append(response)
                logger.warning(
                    "department_sequential_a2a_timeout_no_rag_fallback department=%s error=%s",
                    orchestrator.department.value,
                    response.error[:100],
                )
                continue
            logger.warning(
                "department_sequential_a2a_failed department=%s error=%s, attempting RAG fallback",
                orchestrator.department.value,
                response.error[:100],
            )
            fallback_diag = _extract_transport_diagnostics(response)
            fallback = await _try_branch_rag_fallback(
                orchestrator=orchestrator,
                query=query,
                metadata=metadata,
                original_error=response.error,
            )
            if fallback is not None:
                fallback.metadata = dict(fallback.metadata or {})
                fallback.metadata.update(fallback_diag)
                fallback.metadata["fallback_from_error"] = True
                responses.append(fallback)
                continue
        responses.append(response)
    return responses


async def dispatch_multi_intent_subtasks(
    *,
    department_orchestrators: dict,
    plan: MultiIntentPlan,
    context_id: str,
    metadata: dict,
    transport: DepartmentTransport | None = None,
) -> list[DepartmentResponse]:
    """Dispatch planned subtasks independently while preserving existing agents."""

    active_transport = transport or build_department_transport()
    tasks: list[tuple[MultiIntentSubtask, Any, Any]] = []
    for subtask in plan.subtasks:
        orchestrator = department_orchestrators.get(subtask.department)
        if orchestrator is None:
            continue
        subtask_metadata = _build_multi_intent_subtask_metadata(
            metadata=metadata,
            plan=plan,
            subtask=subtask,
        )
        dispatch_metadata = build_branch_retrieval_metadata(
            department=subtask.department,
            metadata=subtask_metadata,
        )
        tasks.append(
            (
                subtask,
                orchestrator,
                invoke_department_orchestrator(
                    orchestrator=orchestrator,
                    transport=active_transport,
                    query=subtask.effective_question,
                    context_id=context_id,
                    task_type=subtask.task_type,
                    metadata=dispatch_metadata,
                    disable_specialist_llm=True,
                ),
            )
        )

    if not tasks:
        return []

    results = await asyncio.gather(*(item[2] for item in tasks), return_exceptions=True)
    responses: list[DepartmentResponse] = []
    for (subtask, orchestrator, _), result in zip(tasks, results, strict=False):
        if isinstance(result, Exception):
            logger.error(
                "multi_intent_subtask_dispatch_failed subtask=%s department=%s error=%s",
                subtask.subtask_id,
                subtask.department.value,
                result,
                exc_info=(type(result), result, result.__traceback__),
            )
            continue
        parsed = extract_department_response(result)
        if parsed is None:
            logger.error(
                "multi_intent_subtask_invalid_response subtask=%s department=%s",
                subtask.subtask_id,
                subtask.department.value,
            )
            continue
        parsed.metadata = {
            **(parsed.metadata or {}),
            "multi_intent": plan.to_metadata(),
            "multi_intent_subtask": subtask.to_metadata(),
        }
        if not parsed.success and parsed.error and _is_transport_error(parsed.error):
            fallback = await _try_branch_rag_fallback(
                orchestrator=orchestrator,
                query=subtask.effective_question,
                metadata=_build_multi_intent_subtask_metadata(
                    metadata=metadata,
                    plan=plan,
                    subtask=subtask,
                ),
                original_error=parsed.error,
            )
            if fallback is not None:
                fallback.metadata = {
                    **(fallback.metadata or {}),
                    "multi_intent": plan.to_metadata(),
                    "multi_intent_subtask": subtask.to_metadata(),
                    "fallback_from_error": True,
                }
                responses.append(fallback)
                continue
        responses.append(parsed)
    return responses


def _build_multi_intent_subtask_metadata(
    *,
    metadata: dict,
    plan: MultiIntentPlan,
    subtask: MultiIntentSubtask,
) -> dict[str, Any]:
    enriched = dict(metadata or {})
    plan_payload = plan.to_metadata()
    subtask_payload = subtask.to_metadata()
    enriched["multi_intent"] = plan_payload
    enriched["multi_intent_subtask"] = subtask_payload
    enriched["multi_intent_original_query"] = plan.original_query
    enriched["resolved_query"] = subtask.effective_question
    enriched["final_answer_owner"] = "main_orchestrator"
    enriched["specialist_response_mode"] = "evidence_packet"
    enriched["source_owner"] = {
        "schema": "omu.source_owner.v1",
        "primary": subtask.source_family,
        "capability": subtask.capability,
        "reasoning": f"multi_intent_subtask:{subtask.subtask_id}",
        "confidence": subtask.confidence,
        "final_answer_owner": "main_orchestrator",
    }
    enriched["runtime_authority"] = {
        "schema": "omu.runtime_authority.v1",
        "source_owner": subtask.source_family,
        "capability": subtask.capability,
        "final_answer_owner": "main_orchestrator",
        "producer": "multi_intent_subtask",
        "subtask_id": subtask.subtask_id,
    }
    enriched["resolved_decision"] = {
        "schema": "omu.resolved_decision.v1",
        "source_owner": subtask.source_family,
        "capability": subtask.capability,
        "final_answer_owner": "main_orchestrator",
        "stage": "multi_intent_subtask_dispatch",
        "subtask_id": subtask.subtask_id,
    }
    enriched["policy_facet"] = {
        "facet": subtask.subtask_id,
        "source_family": subtask.source_family,
        "capability": subtask.capability,
    }
    return enriched
