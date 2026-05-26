"""A2A service discovery and AgentCard compatibility checks."""

from __future__ import annotations

from dataclasses import dataclass
import logging
import time
from typing import Any, ClassVar, Literal

import httpx

from src.core.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class A2AServiceExpectation:
    """Expected identity/capability values for a remote A2A service."""

    service_id: str | None = None
    target_kind: str | None = None
    target: str | None = None
    transport_protocol: Literal["rest", "jsonrpc"] | None = None


@dataclass(frozen=True)
class A2AAgentCardCheck:
    """Cached AgentCard compatibility result."""

    compatible: bool
    detail: str | None = None
    card: dict[str, Any] | None = None


class A2AServiceDiscoveryClient:
    """Fetch and validate lightweight internal AgentCard payloads."""

    _card_state: ClassVar[dict[str, dict[str, Any]]] = {}

    @classmethod
    def reset_runtime_state(cls) -> None:
        cls._card_state.clear()

    async def verify_agent_card(
        self,
        endpoint: str,
        *,
        expectation: A2AServiceExpectation,
    ) -> A2AAgentCardCheck:
        """Return whether `endpoint` advertises the expected internal A2A service."""
        if not settings.a2a.discovery_agent_card_enabled:
            return A2AAgentCardCheck(compatible=True)

        cache_key = self._cache_key(endpoint, expectation)
        now = time.monotonic()
        cached = self._card_state.get(cache_key)
        if cached and float(cached.get("checked_until", 0.0) or 0.0) > now:
            return A2AAgentCardCheck(
                compatible=bool(cached.get("compatible", False)),
                detail=cached.get("detail"),
                card=cached.get("card"),
            )

        try:
            async with httpx.AsyncClient(
                timeout=max(0.1, settings.a2a.discovery_agent_card_timeout_seconds)
            ) as client:
                response = await client.get(f"{endpoint.rstrip('/')}/agent-card")
                response.raise_for_status()
                card = response.json()
        except Exception as exc:
            check = A2AAgentCardCheck(
                compatible=False,
                detail=f"agent_card_fetch_failed: {type(exc).__name__}",
            )
            self._remember(cache_key, check, now)
            logger.info(
                "a2a_agent_card_fetch_failed endpoint=%s error=%s",
                endpoint,
                exc,
            )
            return check

        check = self._validate_card(card, expectation=expectation)
        self._remember(cache_key, check, now)
        if not check.compatible:
            logger.warning(
                "a2a_agent_card_incompatible endpoint=%s detail=%s",
                endpoint,
                check.detail,
            )
        return check

    @staticmethod
    def _cache_key(endpoint: str, expectation: A2AServiceExpectation) -> str:
        return "|".join(
            [
                endpoint.rstrip("/"),
                expectation.service_id or "",
                expectation.target_kind or "",
                expectation.target or "",
                expectation.transport_protocol or "",
            ]
        )

    @classmethod
    def _remember(
        cls,
        cache_key: str,
        check: A2AAgentCardCheck,
        now: float,
    ) -> None:
        cls._card_state[cache_key] = {
            "compatible": check.compatible,
            "detail": check.detail,
            "card": check.card,
            "checked_until": now + max(0.0, settings.a2a.discovery_agent_card_cache_seconds),
        }

    @staticmethod
    def _validate_card(
        card: Any,
        *,
        expectation: A2AServiceExpectation,
    ) -> A2AAgentCardCheck:
        if not isinstance(card, dict):
            return A2AAgentCardCheck(False, "agent_card_not_object")

        capabilities = card.get("capabilities") or {}
        if not isinstance(capabilities, dict):
            return A2AAgentCardCheck(False, "agent_card_capabilities_not_object", card)

        service_id = str(card.get("service_id") or "").strip()
        if expectation.service_id and service_id != expectation.service_id:
            return A2AAgentCardCheck(
                False,
                f"service_id_mismatch expected={expectation.service_id} actual={service_id or '-'}",
                card,
            )

        target_kind = str(capabilities.get("service_target_kind") or "").strip()
        if expectation.target_kind and target_kind != expectation.target_kind:
            return A2AAgentCardCheck(
                False,
                f"target_kind_mismatch expected={expectation.target_kind} actual={target_kind or '-'}",
                card,
            )

        target = str(capabilities.get("service_target") or "").strip()
        if expectation.target and target != expectation.target:
            return A2AAgentCardCheck(
                False,
                f"target_mismatch expected={expectation.target} actual={target or '-'}",
                card,
            )

        if expectation.transport_protocol == "jsonrpc" and capabilities.get("a2a_jsonrpc") is not True:
            return A2AAgentCardCheck(False, "jsonrpc_not_advertised", card)

        advertised_protocol = str(capabilities.get("a2a_transport_protocol") or "").strip()
        if (
            expectation.transport_protocol
            and advertised_protocol
            and advertised_protocol != expectation.transport_protocol
        ):
            return A2AAgentCardCheck(
                False,
                (
                    "transport_protocol_mismatch "
                    f"expected={expectation.transport_protocol} actual={advertised_protocol}"
                ),
                card,
            )

        return A2AAgentCardCheck(True, card=card)


__all__ = [
    "A2AAgentCardCheck",
    "A2AServiceDiscoveryClient",
    "A2AServiceExpectation",
]
