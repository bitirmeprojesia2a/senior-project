"""Helpers for dispatching work to department orchestrators."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from src.a2a import extract_department_response
from src.a2a.transport import DepartmentTransport, build_department_transport
from src.core.constants import Department, RoutingStrategy, TaskType
from src.db.schemas import DepartmentResponse, RoutingResult
from src.orchestrators.department import _is_transport_error, _extract_transport_diagnostics
from src.routing.routing_policy import detect_task_type

logger = logging.getLogger(__name__)


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

    try:
        # Orchestrator'un _try_rag_fallback metodunu kullan
        if hasattr(orchestrator, '_try_rag_fallback'):
            agent = orchestrator._select_agent(None, query)
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

    active_transport = transport or build_department_transport()
    use_parallel = (
        routing.strategy == RoutingStrategy.PARALLEL and len(orchestrators) > 1
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
                task_type=_resolve_branch_task_type(
                    query=query,
                    department=orchestrator.department,
                    routed_task_type=routing.task_type,
                ),
                metadata=metadata,
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
                        logger.warning(
                            "department_branch_a2a_failed department=%s error=%s, attempting RAG fallback",
                            orchestrator.department.value,
                            parsed.error[:100],
                        )
                        fallback_diag = _extract_transport_diagnostics(parsed)
                        fallback = await _try_branch_rag_fallback(
                            orchestrator=orchestrator,
                            query=query,
                            metadata=metadata,
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
            task_type=_resolve_branch_task_type(
                query=query,
                department=orchestrator.department,
                routed_task_type=routing.task_type,
            ),
            metadata=metadata,
            disable_specialist_llm=disable_specialist_llm,
        )
        response = extract_department_response(response_task)
        if response is None:
            raise ValueError(
                f"{orchestrator.department.value} orchestrator gecerli department response dondurmedi."
            )
        # Başarısız specialist yanıtı (A2A hatası) — fallback dene
        if not response.success and response.error and _is_transport_error(response.error):
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
