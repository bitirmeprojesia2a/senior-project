"""Specialist-agent A2A transport implementations."""

from __future__ import annotations

import asyncio
import logging
import random
import time
from typing import Any, ClassVar, Literal, Protocol

import httpx
from a2a.types import Task

from src.a2a.discovery import A2AServiceDiscoveryClient, A2AServiceExpectation
from src.a2a.helpers import build_agent_response_task, extract_agent_response
from src.a2a.responses import build_failed_agent_response, validate_agent_response
from src.a2a.service_identity import (
    build_a2a_auth_headers,
    department_service_id,
    specialist_service_id,
)
from src.agents.base import BaseSpecialistAgent
from src.api.a2a_dispatch import SpecialistDispatchRequest
from src.core.config import settings
from src.core.constants import AgentRole
from src.db.telemetry import TelemetryService

logger = logging.getLogger(__name__)


class SpecialistTransport(Protocol):
    """Transport contract used by department orchestrators for selected specialists."""

    async def dispatch(
        self,
        *,
        agent: BaseSpecialistAgent,
        task: Task,
    ) -> Task:
        """Send a specialist task and return an A2A response task."""


class InProcessSpecialistTransport:
    """Current behavior: call the selected specialist in the same process."""

    async def dispatch(
        self,
        *,
        agent: BaseSpecialistAgent,
        task: Task,
    ) -> Task:
        return await agent.handle_task(task)


class HttpA2ASpecialistTransport:
    """Strict HTTP transport for specialist services exposing `/a2a/dispatch`."""

    _circuit_state: ClassVar[dict[str, dict[str, float | int]]] = {}

    def __init__(
        self,
        *,
        timeout_seconds: float | None = None,
        retry_count: int | None = None,
        retry_backoff_seconds: float | None = None,
        circuit_breaker_threshold: int | None = None,
        circuit_breaker_cooldown_seconds: float | None = None,
        internal_api_key: str | None = None,
        endpoint_resolver: TelemetryService | None = None,
        transport_protocol: Literal["rest", "jsonrpc"] | None = None,
    ) -> None:
        self.timeout_seconds = (
            timeout_seconds
            if timeout_seconds is not None
            else settings.a2a.specialist_timeout_seconds or settings.a2a.timeout_seconds
        )
        self.retry_count = max(0, retry_count if retry_count is not None else settings.a2a.retry_count)
        self.retry_backoff_seconds = max(
            0.0,
            retry_backoff_seconds
            if retry_backoff_seconds is not None
            else settings.a2a.retry_backoff_seconds,
        )
        self.circuit_breaker_threshold = max(
            0,
            circuit_breaker_threshold
            if circuit_breaker_threshold is not None
            else settings.a2a.circuit_breaker_threshold,
        )
        self.circuit_breaker_cooldown_seconds = max(
            0.0,
            circuit_breaker_cooldown_seconds
            if circuit_breaker_cooldown_seconds is not None
            else settings.a2a.circuit_breaker_cooldown_seconds,
        )
        self.internal_api_key = (
            internal_api_key
            or settings.a2a.internal_api_key
            or settings.server.internal_api_key
        )
        self.endpoint_resolver = endpoint_resolver or TelemetryService()
        self.discovery_client = A2AServiceDiscoveryClient()
        self.transport_protocol = transport_protocol or settings.a2a.transport_protocol

    @classmethod
    def reset_circuit_state(cls) -> None:
        cls._circuit_state.clear()

    async def dispatch(
        self,
        *,
        agent: BaseSpecialistAgent,
        task: Task,
    ) -> Task:
        endpoint = await self._resolve_endpoint(agent)
        if not endpoint:
            logger.info(
                "a2a_specialist_endpoint_missing agent_id=%s department=%s",
                agent.agent_id,
                agent.department.value,
            )
            return self._build_failed_response_task(
                agent=agent,
                request_task=task,
                error_code="a2a_specialist_endpoint_missing",
                detail=f"{agent.agent_id} icin A2A HTTP endpoint tanimli degil.",
                endpoint=None,
            )
        if self._is_circuit_open(endpoint):
            return self._build_failed_response_task(
                agent=agent,
                request_task=task,
                error_code="a2a_specialist_circuit_open",
                detail=(
                    f"{agent.agent_id} icin A2A circuit breaker aktif. "
                    "Kisa sure sonra tekrar denenecek."
                ),
                endpoint=endpoint,
            )

        wire_payload = self._wire_payload(agent=agent, task=task)
        last_exc: Exception | None = None
        total_attempts = self.retry_count + 1
        for attempt in range(1, total_attempts + 1):
            try:
                headers = build_a2a_auth_headers(
                    internal_api_key=self.internal_api_key,
                    caller_id=department_service_id(agent.department),
                    target_id=specialist_service_id(agent.agent_id),
                    body=wire_payload,
                    signature_secret=self._request_signature_secret(),
                )
                async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                    response = await client.post(
                        self._dispatch_url(endpoint),
                        json=wire_payload,
                        headers=headers,
                    )
                    response.raise_for_status()
                    if self.transport_protocol == "jsonrpc":
                        response_task = self._parse_jsonrpc_response(response.json())
                        if extract_agent_response(response_task) is None:
                            raise ValueError("JSON-RPC specialist response did not include AgentResponse artifact.")
                        self._mark_success(endpoint)
                        return response_task
                    department_response = validate_agent_response(response.json())
                    self._mark_success(endpoint)
                    break
            except httpx.TimeoutException as exc:
                last_exc = exc
                if attempt < total_attempts:
                    await self._sleep_before_retry(
                        agent=agent,
                        endpoint=endpoint,
                        attempt=attempt,
                        reason=type(exc).__name__,
                        error=exc,
                    )
                    continue
                self._mark_failure(endpoint)
                return self._build_failed_response_task(
                    agent=agent,
                    request_task=task,
                    error_code="a2a_specialist_transport_timeout",
                    detail=str(exc) or type(exc).__name__,
                    endpoint=endpoint,
                    attempt=attempt,
                    timeout_seconds=self.timeout_seconds,
                )
            except httpx.HTTPStatusError as exc:
                last_exc = exc
                if self._is_retryable_status(exc.response.status_code) and attempt < total_attempts:
                    await self._sleep_before_retry(
                        agent=agent,
                        endpoint=endpoint,
                        attempt=attempt,
                        reason=f"http_{exc.response.status_code}",
                        error=exc,
                    )
                    continue
                if self._is_retryable_status(exc.response.status_code):
                    self._mark_failure(endpoint)
                return self._build_failed_response_task(
                    agent=agent,
                    request_task=task,
                    error_code="a2a_specialist_transport_failed",
                    detail=self._format_http_error(exc),
                    endpoint=endpoint,
                    attempt=attempt,
                    http_status=exc.response.status_code,
                )
            except httpx.RequestError as exc:
                last_exc = exc
                if attempt < total_attempts:
                    await self._sleep_before_retry(
                        agent=agent,
                        endpoint=endpoint,
                        attempt=attempt,
                        reason=type(exc).__name__,
                        error=exc,
                    )
                    continue
                self._mark_failure(endpoint)
                return self._build_failed_response_task(
                    agent=agent,
                    request_task=task,
                    error_code="a2a_specialist_transport_failed",
                    detail=str(exc) or type(exc).__name__,
                    endpoint=endpoint,
                    attempt=attempt,
                )
            except Exception as exc:
                last_exc = exc
                logger.warning(
                    "a2a_specialist_dispatch_failed agent_id=%s endpoint=%s attempts=%s error=%s",
                    agent.agent_id,
                    endpoint,
                    attempt,
                    exc,
                    exc_info=True,
                )
                return self._build_failed_response_task(
                    agent=agent,
                    request_task=task,
                    error_code="a2a_specialist_transport_failed",
                    detail=str(exc) or type(exc).__name__,
                    endpoint=endpoint,
                    attempt=attempt,
                )
        else:
            exc = last_exc or RuntimeError("unknown_a2a_specialist_transport_error")
            return self._build_failed_response_task(
                agent=agent,
                request_task=task,
                error_code="a2a_specialist_transport_failed",
                detail=str(exc) or type(exc).__name__,
                endpoint=endpoint,
                attempt=total_attempts,
            )

        return build_agent_response_task(
            department_response,
            request_task=task,
            emitter_id=f"{agent.agent_id}_http_transport",
            emitter_name=f"{agent.definition.name} HTTP A2A",
            metadata={
                "transport": "http",
                "protocol": self.transport_protocol,
                "selected_agent_id": agent.agent_id,
            },
        )

    @staticmethod
    def _is_retryable_status(status_code: int) -> bool:
        return status_code in {502, 503, 504}

    def _is_circuit_open(self, endpoint: str) -> bool:
        if self.circuit_breaker_threshold <= 0 or self.circuit_breaker_cooldown_seconds <= 0:
            return False
        state = self._circuit_state.get(endpoint)
        if not state:
            return False
        opened_until = float(state.get("opened_until", 0.0) or 0.0)
        if opened_until > 0 and opened_until <= time.monotonic():
            self._circuit_state.pop(endpoint, None)
            return False
        return opened_until > 0

    def _mark_success(self, endpoint: str) -> None:
        self._circuit_state.pop(endpoint, None)

    def _mark_failure(self, endpoint: str) -> None:
        if self.circuit_breaker_threshold <= 0 or self.circuit_breaker_cooldown_seconds <= 0:
            return
        state = self._circuit_state.get(endpoint) or {"failures": 0, "opened_until": 0.0}
        failures = int(state.get("failures", 0)) + 1
        opened_until = float(state.get("opened_until", 0.0) or 0.0)
        if failures >= self.circuit_breaker_threshold:
            opened_until = time.monotonic() + self.circuit_breaker_cooldown_seconds
            logger.warning(
                "a2a_specialist_circuit_trip endpoint=%s failures=%s cooldown_s=%.2f",
                endpoint,
                failures,
                self.circuit_breaker_cooldown_seconds,
            )
        self._circuit_state[endpoint] = {
            "failures": failures,
            "opened_until": opened_until,
        }

    @staticmethod
    def _format_http_error(exc: httpx.HTTPStatusError) -> str:
        response = exc.response
        detail = f"HTTP {response.status_code}"
        try:
            body = response.text.strip()
        except Exception:
            body = ""
        if body:
            compact_body = " ".join(body.split())
            detail = f"{detail}: {compact_body[:300]}"
        return detail

    async def _sleep_before_retry(
        self,
        *,
        agent: BaseSpecialistAgent,
        endpoint: str,
        attempt: int,
        reason: str,
        error: Exception,
    ) -> None:
        delay = self.retry_backoff_seconds * attempt
        if delay > 0:
            delay *= random.uniform(0.8, 1.2)
        logger.info(
            "a2a_specialist_dispatch_retry agent_id=%s endpoint=%s attempt=%s next_delay_s=%.2f reason=%s error=%s",
            agent.agent_id,
            endpoint,
            attempt,
            delay,
            reason,
            error,
        )
        if delay > 0:
            await asyncio.sleep(delay)

    async def _resolve_endpoint(self, agent: BaseSpecialistAgent) -> str | None:
        configured = settings.a2a.specialist_endpoint_for(agent.agent_id)
        if configured:
            return await self._ready_endpoint_or_none(
                configured,
                expectation=self._service_expectation(agent),
            )
        discovered = await self.endpoint_resolver.resolve_agent_endpoint(
            agent.agent_id,
            role=AgentRole.SPECIALIST_AGENT.value,
        )
        if discovered:
            return await self._ready_endpoint_or_none(
                discovered,
                expectation=self._service_expectation(agent),
            )
        return None

    async def _ready_endpoint_or_none(
        self,
        endpoint: str,
        *,
        expectation: A2AServiceExpectation,
    ) -> str | None:
        card_check = await self.discovery_client.verify_agent_card(
            endpoint,
            expectation=expectation,
        )
        if not card_check.compatible:
            logger.warning(
                "a2a_specialist_agent_card_rejected agent_id=%s endpoint=%s detail=%s",
                expectation.target,
                endpoint,
                card_check.detail,
            )
            return None
        return endpoint

    def _service_expectation(self, agent: BaseSpecialistAgent) -> A2AServiceExpectation:
        return A2AServiceExpectation(
            service_id=specialist_service_id(agent.agent_id),
            target_kind="specialist",
            target=agent.agent_id,
            transport_protocol=self.transport_protocol,
        )

    @staticmethod
    def _build_dispatch_payload(
        *,
        agent: BaseSpecialistAgent,
        task: Task,
    ) -> dict:
        meta = task.metadata or {}
        payload = SpecialistDispatchRequest(
            department=agent.department,
            agent_id=agent.agent_id,
            query=str(meta.get("query_text") or ""),
            context_id=task.contextId,
            task_type=meta.get("task_type"),
            student_id=meta.get("student_id"),
            student_department=meta.get("student_department"),
            student_faculty=meta.get("student_faculty"),
            student_type=meta.get("student_type"),
            llm_profile=meta.get("llm_profile"),
            is_authenticated=bool(meta.get("is_authenticated", False)),
            original_query=meta.get("original_query"),
            resolved_query=meta.get("resolved_query"),
            conversation_is_follow_up=bool(meta.get("conversation_is_follow_up", False)),
            conversation_topic=meta.get("conversation_topic"),
            conversation_source_refs=list(meta.get("conversation_source_refs") or []),
            force_llm_synthesis=bool(meta.get("force_llm_synthesis", False)),
            query_complexity=meta.get("query_complexity"),
            is_personal_query=bool(meta.get("is_personal_query", False)),
            final_answer_owner=meta.get("final_answer_owner"),
            specialist_response_mode=meta.get("specialist_response_mode"),
            capability_planner=meta.get("capability_planner"),
            source_owner=meta.get("source_owner"),
            policy_facet=meta.get("policy_facet"),
            decision_contract=meta.get("decision_contract"),
            resolved_decision=meta.get("resolved_decision"),
            branch_dispatch_gate=meta.get("branch_dispatch_gate"),
            specialist_selection=meta.get("specialist_selection"),
            branch_role=meta.get("branch_role"),
            retrieval_execution_policy=meta.get("retrieval_execution_policy"),
            disable_specialist_llm=bool(meta.get("disable_specialist_llm", False)),
            trace_id=meta.get("trace_id"),
            span_id=meta.get("span_id"),
            parent_span_id=meta.get("parent_span_id"),
        )
        return payload.model_dump(mode="json")

    def _dispatch_url(self, endpoint: str) -> str:
        if self.transport_protocol == "jsonrpc":
            return f"{endpoint}/a2a"
        return f"{endpoint}/a2a/dispatch"

    def _wire_payload(self, *, agent: BaseSpecialistAgent, task: Task) -> dict[str, Any]:
        if self.transport_protocol != "jsonrpc":
            return self._build_dispatch_payload(agent=agent, task=task)
        message = task.status.message
        if message is None:
            raise ValueError("JSON-RPC specialist request task has no message.")
        return {
            "jsonrpc": "2.0",
            "id": task.id,
            "method": "message/send",
            "params": {
                "message": message.model_dump(mode="json", exclude_none=True),
                "metadata": task.metadata or {},
            },
        }

    @staticmethod
    def _request_signature_secret() -> str | None:
        if not settings.a2a.require_request_signature:
            return None
        return settings.a2a.resolved_request_signature_secret(settings.server.internal_api_key)

    @staticmethod
    def _parse_jsonrpc_response(payload: dict[str, Any]) -> Task:
        if "error" in payload:
            error = payload.get("error") or {}
            detail = error.get("data") or error.get("message") or "A2A JSON-RPC specialist error"
            raise RuntimeError(str(detail))
        result = payload.get("result")
        if not isinstance(result, dict):
            raise ValueError("A2A JSON-RPC specialist response result must be a Task object.")
        return Task.model_validate(result)

    def _build_failed_response_task(
        self,
        *,
        agent: BaseSpecialistAgent,
        request_task: Task,
        error_code: str,
        detail: str,
        endpoint: str | None = None,
        attempt: int | None = None,
        timeout_seconds: float | None = None,
        http_status: int | None = None,
    ) -> Task:
        if error_code == "a2a_specialist_transport_timeout":
            answer = (
                f"{agent.definition.name} agent servisi zamanında yanıt veremedi. "
                "Bu modda uzman ajanlar yalnızca A2A HTTP üzerinden çalışır; "
                "gerekirse biraz sonra tekrar deneyin."
            )
        elif error_code == "a2a_specialist_circuit_open":
            answer = (
                f"{agent.definition.name} agent servisi geçici olarak korumaya alındı. "
                "Arka arkaya ulaşılamama hataları görüldüğü için kısa bir süre yeni istek gönderilmeyecek; "
                "biraz sonra tekrar deneyin."
            )
        else:
            answer = (
                f"{agent.definition.name} agent servisine şu anda ulaşılamadı. "
                "Bu modda uzman ajanlar yalnızca A2A HTTP üzerinden çalışır; "
                "gerekirse servis durumunu kontrol edip biraz sonra tekrar deneyin."
            )
        # Zengin diagnostics: kullanıcıya sade mesaj, log/telemetry'de detay.
        diagnostics = {
            "transport": "http",
            "protocol": self.transport_protocol,
            "selected_agent_id": agent.agent_id,
            "transport_error": error_code,
            "detail": detail,
        }
        if endpoint:
            diagnostics["endpoint"] = endpoint
        if attempt is not None:
            diagnostics["attempt"] = attempt
        if timeout_seconds is not None:
            diagnostics["timeout_seconds"] = timeout_seconds
        if http_status is not None:
            diagnostics["http_status"] = http_status
        return build_agent_response_task(
            build_failed_agent_response(
                department=agent.department,
                answer=answer,
                error_code=error_code,
                detail=detail,
                agent_id=f"{agent.agent_id}_http_transport",
                agent_name=f"{agent.definition.name} HTTP A2A",
                agent_role=AgentRole.SPECIALIST_AGENT.value,
            ),
            request_task=request_task,
            emitter_id=f"{agent.agent_id}_http_transport",
            emitter_name=f"{agent.definition.name} HTTP A2A",
            metadata=diagnostics,
        )


def build_specialist_transport() -> SpecialistTransport:
    """Build specialist transport according to `A2A_SPECIALIST_MODE`."""
    if settings.a2a.specialist_mode == "http":
        return HttpA2ASpecialistTransport()
    return InProcessSpecialistTransport()
