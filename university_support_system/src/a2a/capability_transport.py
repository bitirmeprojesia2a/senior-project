"""HTTP capability-agent dispatch helpers."""

from __future__ import annotations

import logging
from typing import Any, Literal

from a2a.types import Role, Task
import httpx

from src.a2a import build_text_message, extract_agent_response
from src.a2a.discovery import A2AServiceDiscoveryClient, A2AServiceExpectation
from src.a2a.responses import (
    agent_response_to_department_response,
    build_failed_agent_response,
    validate_agent_response,
)
from src.a2a.service_identity import (
    MAIN_ORCHESTRATOR_SERVICE_ID,
    build_a2a_auth_headers,
    capability_service_id,
)
from src.api.a2a_dispatch import CapabilityDispatchRequest
from src.core.config import settings
from src.core.constants import AgentRole, Capability, Department
from src.db.schemas import DepartmentResponse
from src.db.telemetry import TelemetryService

logger = logging.getLogger(__name__)


class HttpA2ACapabilityTransport:
    """Strict HTTP transport for non-department capability agents."""

    def __init__(
        self,
        *,
        timeout_seconds: float | None = None,
        internal_api_key: str | None = None,
        endpoint_resolver: TelemetryService | None = None,
        transport_protocol: Literal["rest", "jsonrpc"] | None = None,
    ) -> None:
        self.timeout_seconds = timeout_seconds or settings.a2a.timeout_seconds
        self.internal_api_key = (
            internal_api_key
            or settings.a2a.internal_api_key
            or settings.server.internal_api_key
        )
        self.endpoint_resolver = endpoint_resolver or TelemetryService()
        self.discovery_client = A2AServiceDiscoveryClient()
        self.transport_protocol = transport_protocol or settings.a2a.transport_protocol

    async def dispatch(
        self,
        *,
        capability: Capability,
        payload: CapabilityDispatchRequest,
    ) -> DepartmentResponse:
        endpoint = await self._resolve_endpoint(capability)
        if not endpoint:
            return self._build_failed_response(
                capability=capability,
                error_code="a2a_capability_endpoint_missing",
                detail=f"{capability.value} icin A2A HTTP endpoint tanimli degil.",
            )

        wire_payload = self._wire_payload(payload)
        headers = build_a2a_auth_headers(
            internal_api_key=self.internal_api_key,
            caller_id=MAIN_ORCHESTRATOR_SERVICE_ID,
            target_id=capability_service_id(capability),
            body=wire_payload,
            signature_secret=self._request_signature_secret(),
        )

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
                    capability_response = extract_agent_response(response_task)
                    if capability_response is None:
                        raise ValueError("JSON-RPC capability response did not include AgentResponse artifact.")
                    department_response = agent_response_to_department_response(capability_response)
                    if department_response is None:
                        raise ValueError("JSON-RPC capability response cannot be mapped to DepartmentResponse.")
                    return department_response
                agent_response = validate_agent_response(response.json())
                department_response = agent_response_to_department_response(agent_response)
                if department_response is None:
                    raise ValueError("REST capability response cannot be mapped to DepartmentResponse.")
                return department_response
        except Exception as exc:
            logger.warning(
                "a2a_capability_dispatch_failed capability=%s endpoint=%s error=%s",
                capability.value,
                endpoint,
                exc,
                exc_info=True,
            )
            return self._build_failed_response(
                capability=capability,
                error_code="a2a_capability_transport_failed",
                detail=str(exc) or type(exc).__name__,
            )

    async def _resolve_endpoint(self, capability: Capability) -> str | None:
        configured = settings.a2a.endpoint_for(capability.value)
        if configured:
            return await self._ready_endpoint_or_none(
                configured,
                expectation=self._service_expectation(capability),
            )
        discovered = await self.endpoint_resolver.resolve_service_endpoint(
            capability.value,
            role=AgentRole.CAPABILITY_AGENT.value,
        )
        if discovered:
            return await self._ready_endpoint_or_none(
                discovered,
                expectation=self._service_expectation(capability),
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
                "a2a_capability_agent_card_rejected capability=%s endpoint=%s detail=%s",
                expectation.target,
                endpoint,
                card_check.detail,
            )
            return None
        return endpoint

    def _service_expectation(self, capability: Capability) -> A2AServiceExpectation:
        return A2AServiceExpectation(
            service_id=capability_service_id(capability),
            target_kind="capability",
            target=capability.value,
            transport_protocol=self.transport_protocol,
        )

    def _dispatch_url(self, endpoint: str) -> str:
        if self.transport_protocol == "jsonrpc":
            return f"{endpoint}/a2a"
        return f"{endpoint}/a2a/dispatch"

    def _wire_payload(self, payload: CapabilityDispatchRequest) -> dict[str, Any]:
        if self.transport_protocol != "jsonrpc":
            return payload.model_dump(mode="json")
        metadata = payload.model_dump(mode="json", exclude_none=True)
        query = str(metadata.pop("query", payload.query))
        context_id = str(metadata.pop("context_id", payload.context_id or ""))
        message = build_text_message(
            query,
            context_id=context_id,
            role=Role.user,
            metadata=metadata,
        )
        return {
            "jsonrpc": "2.0",
            "id": message.messageId,
            "method": "message/send",
            "params": {
                "message": message.model_dump(mode="json", exclude_none=True),
                "metadata": metadata,
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
            raise RuntimeError(error.get("message") or "A2A JSON-RPC capability error")
        result = payload.get("result")
        if not isinstance(result, dict):
            raise ValueError("A2A JSON-RPC capability response result must be a Task object.")
        return Task.model_validate(result)

    @staticmethod
    def _response_department_for(capability: Capability) -> Department:
        # Duyuru ve etkinlik agent'lari ortak capability olarak dagitildi; mevcut
        # ortak yanit semasinda en yakin idari yuzey student_affairs.
        if capability in {Capability.ANNOUNCEMENT, Capability.EVENT}:
            return Department.STUDENT_AFFAIRS
        return Department.STUDENT_AFFAIRS

    def _build_failed_response(
        self,
        *,
        capability: Capability,
        error_code: str,
        detail: str,
    ) -> DepartmentResponse:
        response = build_failed_agent_response(
            department=self._response_department_for(capability),
            answer=(
                f"{capability.display_name} agent servisine şu anda ulaşılamadı. "
                "Bu modda capability agent'ları yalnızca A2A HTTP üzerinden çalışır; "
                "gerekirse servis durumunu kontrol edip biraz sonra tekrar deneyin."
            ),
            error_code=error_code,
            detail=detail,
            agent_id=f"{capability.value}_transport",
            agent_name=f"{capability.display_name} HTTP A2A",
            agent_role=AgentRole.CAPABILITY_AGENT.value,
            capability=capability.value,
            db_data={
                "capability": capability.value,
                "transport": "http",
                "protocol": self.transport_protocol,
            },
        )
        mapped = agent_response_to_department_response(response)
        if mapped is None:
            raise ValueError("Capability transport failure response cannot be mapped to DepartmentResponse.")
        return mapped
