"""Department-level A2A transport implementations."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, ClassVar, Literal, Protocol

import httpx
from a2a.types import Task

from src.a2a.discovery import A2AServiceDiscoveryClient, A2AServiceExpectation
from src.a2a.helpers import build_agent_response_task, extract_agent_response
from src.a2a.responses import build_failed_agent_response, validate_agent_response
from src.a2a.service_identity import (
    MAIN_ORCHESTRATOR_SERVICE_ID,
    build_a2a_auth_headers,
    department_service_id,
)
from src.a2a.tracing import child_trace_metadata
from src.core.config import settings
from src.core.constants import Department, TaskType
from src.db.telemetry import TelemetryService
from src.orchestrators.response_utils import response_core_answer
from src.orchestrators.task_builders import build_department_request_task

logger = logging.getLogger(__name__)


class DepartmentTransport(Protocol):
    """Transport contract used by the main orchestrator dispatch layer."""

    async def dispatch(
        self,
        *,
        department: Department,
        orchestrator: Any,
        query: str,
        context_id: str,
        task_type: TaskType | None,
        metadata: dict,
        disable_specialist_llm: bool,
    ) -> Task:
        """Send a department request and return an A2A response task."""


class InProcessDepartmentTransport:
    """Current behavior: call the department orchestrator in the same process."""

    async def dispatch(
        self,
        *,
        department: Department,
        orchestrator: Any,
        query: str,
        context_id: str,
        task_type: TaskType | None,
        metadata: dict,
        disable_specialist_llm: bool,
    ) -> Task:
        request_metadata = child_trace_metadata(metadata)
        request_task = build_department_request_task(
            department=department,
            query=query,
            context_id=context_id,
            task_type=task_type,
            metadata=request_metadata,
            disable_specialist_llm=disable_specialist_llm,
        )
        return await orchestrator.handle_task(
            request_task,
            task_type=task_type,
            metadata=request_metadata,
        )


class HttpA2ADepartmentTransport:
    """HTTP transport for department services exposing `/a2a/dispatch`."""

    _circuit_state: ClassVar[dict[str, dict[str, float | int]]] = {}
    _health_state: ClassVar[dict[str, dict[str, float | bool]]] = {}

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
        discovery_healthcheck_enabled: bool | None = None,
        discovery_healthcheck_timeout_seconds: float | None = None,
        discovery_healthcheck_cache_seconds: float | None = None,
    ) -> None:
        self.timeout_seconds = (
            timeout_seconds
            if timeout_seconds is not None
            else settings.a2a.effective_department_timeout_seconds()
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
        self.discovery_healthcheck_enabled = (
            settings.a2a.discovery_healthcheck_enabled
            if discovery_healthcheck_enabled is None
            else discovery_healthcheck_enabled
        )
        self.discovery_healthcheck_timeout_seconds = max(
            0.1,
            (
                settings.a2a.discovery_healthcheck_timeout_seconds
                if discovery_healthcheck_timeout_seconds is None
                else discovery_healthcheck_timeout_seconds
            ),
        )
        self.discovery_healthcheck_cache_seconds = max(
            0.0,
            (
                settings.a2a.discovery_healthcheck_cache_seconds
                if discovery_healthcheck_cache_seconds is None
                else discovery_healthcheck_cache_seconds
            ),
        )

    @classmethod
    def reset_circuit_state(cls) -> None:
        cls._circuit_state.clear()

    @classmethod
    def reset_runtime_state(cls) -> None:
        cls._circuit_state.clear()
        cls._health_state.clear()
        A2AServiceDiscoveryClient.reset_runtime_state()

    async def dispatch(
        self,
        *,
        department: Department,
        orchestrator: Any,
        query: str,
        context_id: str,
        task_type: TaskType | None,
        metadata: dict,
        disable_specialist_llm: bool,
    ) -> Task:
        _ = orchestrator
        request_metadata = child_trace_metadata(metadata)
        request_task = build_department_request_task(
            department=department,
            query=query,
            context_id=context_id,
            task_type=task_type,
            metadata=request_metadata,
            disable_specialist_llm=disable_specialist_llm,
        )
        endpoint = await self._resolve_endpoint(department)
        if not endpoint:
            return self._build_failed_response_task(
                department=department,
                request_task=request_task,
                error_code="a2a_endpoint_missing",
                detail=f"{department.value} icin A2A HTTP endpoint tanimli degil.",
                endpoint=None,
            )
        if self._is_circuit_open(endpoint):
            return self._build_failed_response_task(
                department=department,
                request_task=request_task,
                error_code="a2a_circuit_open",
                detail=(
                    f"{department.value} icin A2A circuit breaker aktif. "
                    "Kisa sure sonra tekrar denenecek."
                ),
                endpoint=endpoint,
                circuit_state=self._circuit_state.get(endpoint),
            )

        payload = self._build_dispatch_payload(
            department=department,
            query=str(request_task.metadata.get("query_text") or query),
            context_id=context_id,
            task_type=task_type,
            metadata=request_metadata,
            disable_specialist_llm=disable_specialist_llm,
        )
        wire_payload = self._wire_payload(request_task=request_task, rest_payload=payload)
        headers = build_a2a_auth_headers(
            internal_api_key=self.internal_api_key,
            caller_id=MAIN_ORCHESTRATOR_SERVICE_ID,
            target_id=department_service_id(department),
            body=wire_payload,
            signature_secret=self._request_signature_secret(),
        )

        last_exc: Exception | None = None
        response_task: Task | None = None
        total_attempts = self.retry_count + 1
        for attempt in range(1, total_attempts + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                    response = await client.post(
                        self._dispatch_url(endpoint),
                        json=wire_payload,
                        headers=headers,
                    )
                    response.raise_for_status()
                    if self.transport_protocol == "jsonrpc":
                        response_task = self._parse_jsonrpc_response(response.json())
                        department_response = extract_agent_response(response_task)
                        if department_response is None:
                            raise ValueError("JSON-RPC A2A response did not include AgentResponse artifact.")
                    else:
                        department_response = validate_agent_response(response.json())
                    self._mark_success(endpoint)
                    break
            except httpx.TimeoutException as exc:
                last_exc = exc
                if attempt < total_attempts:
                    await self._sleep_before_retry(
                        department=department,
                        endpoint=endpoint,
                        attempt=attempt,
                        reason="timeout",
                        error=exc,
                    )
                    continue
                logger.warning(
                    "a2a_http_dispatch_timeout department=%s endpoint=%s timeout_s=%s attempts=%s error=%s",
                    department.value,
                    endpoint,
                    self.timeout_seconds,
                    attempt,
                    exc,
                    exc_info=True,
                )
                self._mark_failure(endpoint)
                return self._build_failed_response_task(
                    department=department,
                    request_task=request_task,
                    error_code="a2a_transport_timeout",
                    detail=str(exc) or type(exc).__name__,
                    endpoint=endpoint,
                    attempt=attempt,
                    timeout_seconds=self.timeout_seconds,
                )
            except httpx.HTTPStatusError as exc:
                last_exc = exc
                if self._is_retryable_status(exc.response.status_code) and attempt < total_attempts:
                    await self._sleep_before_retry(
                        department=department,
                        endpoint=endpoint,
                        attempt=attempt,
                        reason=f"http_{exc.response.status_code}",
                        error=exc,
                    )
                    continue
                logger.warning(
                    "a2a_http_dispatch_http_error department=%s endpoint=%s status=%s attempts=%s error=%s",
                    department.value,
                    endpoint,
                    exc.response.status_code,
                    attempt,
                    exc,
                    exc_info=True,
                )
                if self._is_retryable_status(exc.response.status_code):
                    self._mark_failure(endpoint)
                return self._build_failed_response_task(
                    department=department,
                    request_task=request_task,
                    error_code="a2a_transport_failed",
                    detail=self._format_http_error(exc),
                    endpoint=endpoint,
                    attempt=attempt,
                    http_status=exc.response.status_code,
                )
            except httpx.RequestError as exc:
                last_exc = exc
                if attempt < total_attempts:
                    await self._sleep_before_retry(
                        department=department,
                        endpoint=endpoint,
                        attempt=attempt,
                        reason=type(exc).__name__,
                        error=exc,
                    )
                    continue
                logger.warning(
                    "a2a_http_dispatch_request_failed department=%s endpoint=%s attempts=%s error=%s",
                    department.value,
                    endpoint,
                    attempt,
                    exc,
                    exc_info=True,
                )
                self._mark_failure(endpoint)
                return self._build_failed_response_task(
                    department=department,
                    request_task=request_task,
                    error_code="a2a_transport_failed",
                    detail=str(exc) or type(exc).__name__,
                    endpoint=endpoint,
                    attempt=attempt,
                )
            except Exception as exc:
                last_exc = exc
                logger.warning(
                    "a2a_http_dispatch_failed department=%s endpoint=%s attempts=%s error=%s",
                    department.value,
                    endpoint,
                    attempt,
                    exc,
                    exc_info=True,
                )
                return self._build_failed_response_task(
                    department=department,
                    request_task=request_task,
                    error_code="a2a_transport_failed",
                    detail=str(exc) or type(exc).__name__,
                    endpoint=endpoint,
                    attempt=attempt,
                )
        else:
            exc = last_exc or RuntimeError("unknown_a2a_transport_error")
            return self._build_failed_response_task(
                department=department,
                request_task=request_task,
                error_code="a2a_transport_failed",
                detail=str(exc) or type(exc).__name__,
                endpoint=endpoint,
                attempt=total_attempts,
            )

        if response_task is not None:
            return response_task

        return build_agent_response_task(
            department_response,
            request_task=request_task,
            emitter_id=f"{department.value}_http_transport",
            emitter_name=f"{department.display_name} HTTP A2A",
            metadata={"transport": "http", "protocol": self.transport_protocol},
        )

    async def _resolve_endpoint(self, department: Department) -> str | None:
        configured = settings.a2a.endpoint_for(department.value)
        if configured:
            return await self._ready_endpoint_or_none(
                configured,
                expectation=self._service_expectation(department),
                label=department.value,
                require_healthcheck=False,
            )

        discovered = await self.endpoint_resolver.resolve_department_endpoint(department)
        if discovered and await self._ready_endpoint_or_none(
            discovered,
            expectation=self._service_expectation(department),
            label=department.value,
            require_healthcheck=True,
        ):
            logger.info(
                "a2a_http_dispatch_discovered_endpoint department=%s endpoint=%s",
                department.value,
                discovered,
            )
            return discovered
        if discovered:
            logger.warning(
                "a2a_http_dispatch_discovered_endpoint_unhealthy department=%s endpoint=%s",
                department.value,
                discovered,
            )
        return None

    async def _ready_endpoint_or_none(
        self,
        endpoint: str,
        *,
        expectation: A2AServiceExpectation,
        label: str,
        require_healthcheck: bool,
    ) -> str | None:
        if require_healthcheck and not await self._is_endpoint_healthy(endpoint):
            logger.warning(
                "a2a_http_dispatch_endpoint_unhealthy target=%s endpoint=%s",
                label,
                endpoint,
            )
            return None
        card_check = await self.discovery_client.verify_agent_card(
            endpoint,
            expectation=expectation,
        )
        if not card_check.compatible:
            logger.warning(
                "a2a_http_dispatch_agent_card_rejected target=%s endpoint=%s detail=%s",
                label,
                endpoint,
                card_check.detail,
            )
            return None
        return endpoint

    def _service_expectation(self, department: Department) -> A2AServiceExpectation:
        return A2AServiceExpectation(
            service_id=department_service_id(department),
            target_kind="department",
            target=department.value,
            transport_protocol=self.transport_protocol,
        )

    async def _is_endpoint_healthy(self, endpoint: str) -> bool:
        if not self.discovery_healthcheck_enabled:
            return True

        cache_state = self._health_state.get(endpoint)
        now = time.monotonic()
        if cache_state and float(cache_state.get("checked_until", 0.0) or 0.0) > now:
            return bool(cache_state.get("healthy", False))

        try:
            async with httpx.AsyncClient(timeout=self.discovery_healthcheck_timeout_seconds) as client:
                response = await client.get(f"{endpoint}/health")
                response.raise_for_status()
                payload = response.json()
            healthy = payload.get("status") == "ok"
        except Exception as exc:
            logger.info(
                "a2a_http_discovery_healthcheck_failed endpoint=%s error=%s",
                endpoint,
                exc,
            )
            healthy = False

        self._health_state[endpoint] = {
            "healthy": healthy,
            "checked_until": now + self.discovery_healthcheck_cache_seconds,
        }
        return healthy

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
        if opened_until <= 0:
            return False
        logger.info(
            "a2a_http_circuit_open endpoint=%s failures=%s opened_until_in_s=%.2f",
            endpoint,
            state.get("failures", 0),
            opened_until - time.monotonic(),
        )
        return True

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
                "a2a_http_circuit_trip endpoint=%s failures=%s cooldown_s=%.2f",
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

    def _dispatch_url(self, endpoint: str) -> str:
        if self.transport_protocol == "jsonrpc":
            return f"{endpoint}/a2a"
        return f"{endpoint}/a2a/dispatch"

    def _wire_payload(self, *, request_task: Task, rest_payload: dict[str, Any]) -> dict[str, Any]:
        if self.transport_protocol != "jsonrpc":
            return rest_payload
        message = request_task.status.message
        if message is None:
            raise ValueError("JSON-RPC A2A request task has no message.")
        return {
            "jsonrpc": "2.0",
            "id": request_task.id,
            "method": "message/send",
            "params": {
                "message": message.model_dump(mode="json", exclude_none=True),
                "metadata": request_task.metadata or {},
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
            raise RuntimeError(error.get("message") or "A2A JSON-RPC error")
        result = payload.get("result")
        if not isinstance(result, dict):
            raise ValueError("A2A JSON-RPC response result must be a Task object.")
        return Task.model_validate(result)

    async def _sleep_before_retry(
        self,
        *,
        department: Department,
        endpoint: str,
        attempt: int,
        reason: str,
        error: Exception,
    ) -> None:
        delay = self.retry_backoff_seconds * attempt
        logger.info(
            "a2a_http_dispatch_retry department=%s endpoint=%s attempt=%s next_delay_s=%.2f reason=%s error=%s",
            department.value,
            endpoint,
            attempt,
            delay,
            reason,
            error,
        )
        if delay > 0:
            await asyncio.sleep(delay)

    @staticmethod
    def _build_dispatch_payload(
        *,
        department: Department,
        query: str,
        context_id: str,
        task_type: TaskType | None,
        metadata: dict,
        disable_specialist_llm: bool,
    ) -> dict[str, Any]:
        """Build the internal dispatch endpoint payload without session secrets."""
        return {
            "department": department.value,
            "query": query,
            "context_id": context_id,
            "user_id": metadata.get("user_id"),
            "full_name": metadata.get("student_full_name"),
            "student_number": metadata.get("student_number"),
            "student_id": metadata.get("student_id"),
            "student_department": metadata.get("student_department"),
            "student_faculty": metadata.get("student_faculty"),
            "student_type": metadata.get("student_type"),
            "llm_profile": metadata.get("llm_profile"),
            "is_authenticated": bool(metadata.get("is_authenticated", False)),
            "task_type": task_type.value if task_type else None,
            "original_query": metadata.get("original_query"),
            "resolved_query": metadata.get("resolved_query"),
            "conversation_is_follow_up": bool(metadata.get("conversation_is_follow_up", False)),
            "conversation_topic": metadata.get("conversation_topic"),
            "conversation_source_refs": list(metadata.get("conversation_source_refs") or []),
            "force_llm_synthesis": bool(metadata.get("force_llm_synthesis", False)),
            "query_complexity": metadata.get("query_complexity"),
            "is_personal_query": bool(metadata.get("is_personal_query", False)),
            "final_answer_owner": metadata.get("final_answer_owner"),
            "specialist_response_mode": metadata.get("specialist_response_mode"),
            "capability_planner": metadata.get("capability_planner"),
            "trace_id": metadata.get("trace_id"),
            "span_id": metadata.get("span_id"),
            "parent_span_id": metadata.get("parent_span_id"),
            "disable_specialist_llm": disable_specialist_llm,
        }

    @staticmethod
    def _build_failed_response_task(
        *,
        department: Department,
        request_task: Task,
        error_code: str,
        detail: str,
        endpoint: str | None = None,
        attempt: int | None = None,
        timeout_seconds: float | None = None,
        http_status: int | None = None,
        circuit_state: dict | None = None,
    ) -> Task:
        if error_code == "a2a_transport_timeout":
            answer = (
                f"{department.display_name} agent servisi zamanında yanıt veremedi. "
                "Diğer mevcut kaynaklarla yanıt verilebiliyorsa işleme devam edilecek; "
                "gerekirse biraz sonra tekrar deneyin."
            )
        elif error_code == "a2a_circuit_open":
            answer = (
                f"{department.display_name} agent servisi geçici olarak korumaya alındı. "
                "Arka arkaya ulaşılamama hataları görüldüğü için kısa bir süre yeni istek gönderilmeyecek; "
                "biraz sonra tekrar deneyin."
            )
        elif error_code == "a2a_endpoint_missing":
            answer = (
                f"{department.display_name} agent servisine şu anda ulaşılamadı. "
                "Diğer mevcut kaynaklarla yanıt verilebiliyorsa işleme devam edilecek; "
                "gerekirse biraz sonra tekrar deneyin."
            )
        else:
            answer = (
                f"{department.display_name} agent servisine şu anda ulaşılamadı. "
                "Diğer mevcut kaynaklarla yanıt verilebiliyorsa işleme devam edilecek; "
                "gerekirse biraz sonra tekrar deneyin."
            )
        # Zengin diagnostics: kullanıcıya sade mesaj, log/telemetry'de detay.
        diagnostics = {
            "transport": "http",
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
        if circuit_state:
            diagnostics["circuit_failures"] = circuit_state.get("failures")
            diagnostics["circuit_opened_until"] = circuit_state.get("opened_until")
        return build_agent_response_task(
            build_failed_agent_response(
                department=department,
                answer=answer,
                error_code=error_code,
                detail=detail,
                agent_id=f"{department.value}_http_transport",
                agent_name=f"{department.display_name} HTTP A2A",
                agent_role="transport",
            ),
            request_task=request_task,
            emitter_id=f"{department.value}_http_transport",
            emitter_name=f"{department.display_name} HTTP A2A",
            metadata=diagnostics,
        )


class ShadowDepartmentTransport:
    """Return in-process results while comparing HTTP A2A in the background."""

    _pending_tasks: ClassVar[set[asyncio.Task]] = set()

    def __init__(self) -> None:
        self.primary = InProcessDepartmentTransport()
        self.shadow = HttpA2ADepartmentTransport()

    @classmethod
    async def wait_for_pending(cls, timeout_seconds: float = 30.0) -> None:
        """Wait for currently scheduled shadow comparisons.

        Production API requests do not need this. Smoke tests use it so the
        event loop does not exit before background comparison logs are emitted.
        """
        if not cls._pending_tasks:
            return
        await asyncio.wait_for(
            asyncio.gather(*list(cls._pending_tasks), return_exceptions=True),
            timeout=timeout_seconds,
        )

    async def dispatch(
        self,
        *,
        department: Department,
        orchestrator: Any,
        query: str,
        context_id: str,
        task_type: TaskType | None,
        metadata: dict,
        disable_specialist_llm: bool,
    ) -> Task:
        primary_task = await self.primary.dispatch(
            department=department,
            orchestrator=orchestrator,
            query=query,
            context_id=context_id,
            task_type=task_type,
            metadata=metadata,
            disable_specialist_llm=disable_specialist_llm,
        )
        shadow_task = asyncio.create_task(
            self._run_shadow(
                department=department,
                orchestrator=orchestrator,
                query=query,
                context_id=context_id,
                task_type=task_type,
                metadata=metadata,
                disable_specialist_llm=disable_specialist_llm,
                primary_task=primary_task,
            )
        )
        self._pending_tasks.add(shadow_task)
        shadow_task.add_done_callback(self._pending_tasks.discard)
        return primary_task

    async def _run_shadow(
        self,
        *,
        department: Department,
        orchestrator: Any,
        query: str,
        context_id: str,
        task_type: TaskType | None,
        metadata: dict,
        disable_specialist_llm: bool,
        primary_task: Task,
    ) -> None:
        try:
            started = time.perf_counter()
            shadow_task = await self.shadow.dispatch(
                department=department,
                orchestrator=orchestrator,
                query=query,
                context_id=context_id,
                task_type=task_type,
                metadata=metadata,
                disable_specialist_llm=disable_specialist_llm,
            )
            elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
            primary_response = extract_agent_response(primary_task)
            shadow_response = extract_agent_response(shadow_task)
            primary_answer = response_core_answer(primary_response) if primary_response else ""
            shadow_answer = response_core_answer(shadow_response) if shadow_response else ""
            logger.info(
                (
                    "a2a_shadow_complete department=%s context_id=%s "
                    "primary_success=%s shadow_success=%s "
                    "primary_mode=%s shadow_mode=%s "
                    "primary_sources=%s shadow_sources=%s "
                    "primary_error=%s shadow_error=%s "
                    "primary_len=%s shadow_len=%s same_answer=%s elapsed_ms=%s"
                ),
                department.value,
                context_id,
                primary_response.success if primary_response else None,
                shadow_response.success if shadow_response else None,
                primary_response.generation_mode if primary_response else None,
                shadow_response.generation_mode if shadow_response else None,
                len(primary_response.sources) if primary_response else 0,
                len(shadow_response.sources) if shadow_response else 0,
                primary_response.error if primary_response else None,
                shadow_response.error if shadow_response else None,
                len(primary_answer),
                len(shadow_answer),
                bool(
                    primary_response
                    and shadow_response
                    and primary_answer == shadow_answer
                ),
                elapsed_ms,
            )
        except Exception as exc:
            logger.warning(
                "a2a_shadow_failed department=%s error=%s",
                department.value,
                exc,
                exc_info=True,
            )


def build_department_transport() -> DepartmentTransport:
    """Build transport according to `A2A_MODE`."""
    if settings.a2a.mode == "http":
        return HttpA2ADepartmentTransport()
    if settings.a2a.mode == "shadow":
        return ShadowDepartmentTransport()
    return InProcessDepartmentTransport()
