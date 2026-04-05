"""Helpers for dispatching work to department orchestrators."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from src.a2a import extract_department_response
from src.core.constants import RoutingStrategy
from src.db.schemas import DepartmentResponse, RoutingResult
from src.orchestrators.query_policy import should_disable_specialist_llm
from src.orchestrators.task_builders import build_department_request_task

logger = logging.getLogger(__name__)


async def invoke_department_orchestrator(
    *,
    orchestrator: Any,
    query: str,
    context_id: str,
    task_type,
    metadata: dict,
    disable_specialist_llm: bool,
):
    """Send a single request task to a department orchestrator."""
    request_task = build_department_request_task(
        department=orchestrator.department,
        query=query,
        context_id=context_id,
        task_type=task_type,
        metadata=metadata,
        disable_specialist_llm=disable_specialist_llm,
    )
    return await orchestrator.handle_task(
        request_task,
        task_type=task_type,
        metadata=metadata,
    )


async def dispatch_to_departments(
    *,
    department_orchestrators: dict,
    query: str,
    context_id: str,
    routing: RoutingResult,
    metadata: dict,
) -> list[DepartmentResponse]:
    """Dispatch a user query to the selected department orchestrators."""
    orchestrators = [
        department_orchestrators[department]
        for department in routing.departments
        if department in department_orchestrators
    ]

    if not orchestrators:
        return []

    use_parallel = (
        routing.strategy == RoutingStrategy.PARALLEL and len(orchestrators) > 1
    )
    disable_specialist_llm = should_disable_specialist_llm(
        query=query,
        orchestrator_count=len(orchestrators),
    )

    if use_parallel:
        tasks = [
            invoke_department_orchestrator(
                orchestrator=orchestrator,
                query=query,
                context_id=context_id,
                task_type=routing.task_type,
                metadata=metadata,
                disable_specialist_llm=disable_specialist_llm,
            )
            for orchestrator in orchestrators
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        responses: list[DepartmentResponse] = []
        for orchestrator, result in zip(orchestrators, results, strict=False):
            if not isinstance(result, Exception):
                parsed = extract_department_response(result)
                if parsed is not None:
                    responses.append(parsed)
                    continue
                logger.error(
                    "department_branch_invalid_response department=%s query=%r",
                    orchestrator.department.value,
                    query,
                )
                continue
            logger.error(
                "department_branch_failed department=%s query=%r error=%s",
                orchestrator.department.value,
                query,
                result,
                exc_info=(type(result), result, result.__traceback__),
            )
        return responses

    responses: list[DepartmentResponse] = []
    for orchestrator in orchestrators:
        response_task = await invoke_department_orchestrator(
            orchestrator=orchestrator,
            query=query,
            context_id=context_id,
            task_type=routing.task_type,
            metadata=metadata,
            disable_specialist_llm=disable_specialist_llm,
        )
        response = extract_department_response(response_task)
        if response is None:
            raise ValueError(
                f"{orchestrator.department.value} orchestrator gecerli department response dondurmedi."
            )
        responses.append(response)
    return responses
