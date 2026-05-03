"""Application startup warm-up helpers."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

import structlog

from src.a2a import AgentServiceTarget, SpecialistTarget
from src.core.config import settings
from src.core.constants import Capability, Department, academic_schedule_collection_name, collection_name_for_department
from src.llm.llm_service import LLMService
from src.rag.warmup import warm_retrieval_resources

logger = structlog.get_logger()


def resolve_warmup_collections(target: AgentServiceTarget | None = None) -> list[str]:
    """Resolve the retrieval collections that should be warmed for a runtime."""
    if target is None:
        return settings.configured_warmup_collections()

    if isinstance(target, Capability):
        return []

    department = target.department if isinstance(target, SpecialistTarget) else target
    collections = [collection_name_for_department(department)]
    if department is Department.ACADEMIC_PROGRAMS:
        collections.append(academic_schedule_collection_name())
    return collections


def resolve_warmup_llm_roles(target: AgentServiceTarget | None = None) -> list[str]:
    """Resolve which LLM roles should be warmed for a runtime."""
    if not settings.server.warmup_llm_enabled:
        return []

    configured = [
        role.strip()
        for role in settings.server.warmup_llm_roles.split(",")
        if role.strip()
    ]
    if not configured:
        return []

    if target is None:
        return configured

    if isinstance(target, Capability):
        return []

    # Department/specialist services pay their first real LLM cost on evidence
    # selection and specialist synthesis; routing is API/orchestrator-side.
    narrowed = [
        role
        for role in configured
        if role in {"evidence_selection", "specialist_synthesis", "final_refinement"}
    ]
    return narrowed or ["specialist_synthesis"]


async def warm_llm_resources(
    llm_service: LLMService,
    *,
    roles: list[str] | None = None,
    llm_profile: str | None = None,
) -> None:
    """Prime selected LLM roles with a tiny request."""
    if not settings.server.warmup_llm_enabled:
        return

    effective_roles = roles or resolve_warmup_llm_roles()
    if not effective_roles:
        return

    prompt = settings.server.warmup_llm_prompt.strip() or "Yalnizca OK yaz."
    timeout_seconds = max(1, settings.server.warmup_llm_timeout_seconds)

    for role in effective_roles:
        try:
            await asyncio.wait_for(
                llm_service.generate(
                    prompt=prompt,
                    system="Cevap olarak sadece OK yaz.",
                    model_role=role,
                    llm_profile=llm_profile,
                ),
                timeout=timeout_seconds,
            )
        except Exception as exc:
            logger.warning(
                "llm_warmup_failed",
                role=role,
                timeout_seconds=timeout_seconds,
                error_type=type(exc).__name__,
                error=str(exc),
            )
        else:
            logger.info("llm_warmup_complete", role=role, timeout_seconds=timeout_seconds)


async def warm_application_resources(
    *,
    llm_service: LLMService | None = None,
    target: AgentServiceTarget | None = None,
) -> None:
    """Run best-effort startup warm-up for retrieval and LLM resources."""
    if not settings.server.warmup_enabled:
        return

    if not settings.retrieval_service.enabled:
        collections = resolve_warmup_collections(target)
        warm_retrieval_resources(collections=collections)
    else:
        logger.info(
            "local_retrieval_warmup_skipped",
            reason="central_retrieval_service_enabled",
            target=getattr(target, "value", None),
        )

    if llm_service is not None:
        await warm_llm_resources(
            llm_service,
            roles=resolve_warmup_llm_roles(target),
            llm_profile=settings.llm.profile,
        )


def schedule_application_warmup(
    warmup_factory: Callable[[], Awaitable[None]],
    *,
    label: str,
) -> asyncio.Task | None:
    """Schedule best-effort warm-up without delaying HTTP readiness."""
    if not settings.server.warmup_enabled:
        return None

    async def _run() -> None:
        try:
            await warmup_factory()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.warning(
                "startup_warmup_failed",
                label=label,
                error_type=type(exc).__name__,
                error=str(exc),
            )
        else:
            logger.info("startup_warmup_complete", label=label)

    task = asyncio.create_task(_run(), name=f"startup-warmup:{label}")
    logger.info("startup_warmup_scheduled", label=label)
    return task


async def cancel_application_warmup(task: asyncio.Task | None) -> None:
    """Cancel a background warm-up task during service shutdown."""
    if task is None or task.done():
        return

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("startup_warmup_cancelled")
