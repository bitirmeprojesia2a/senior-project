"""Anthropic Claude Messages API istemcisi."""

from __future__ import annotations

import json
import logging
from typing import Any, AsyncGenerator, Dict, Optional, Protocol

import httpx

from src.core.config import settings
from src.llm.api_key_pool import ApiKeyLease, get_api_key_pool, split_api_keys

logger = logging.getLogger(__name__)


class AnthropicClientError(Exception):
    """Anthropic provider ile iletisim sirasinda olusan hatalar."""

    def __init__(
        self,
        message: str,
        *,
        retryable: bool = False,
        api_key_fingerprint: str | None = None,
        api_key_index: int | None = None,
    ):
        super().__init__(message)
        self.retryable = retryable
        self.api_key_fingerprint = api_key_fingerprint
        self.api_key_index = api_key_index


class AnthropicConfig(Protocol):
    api_key: Optional[str]
    base_url: str
    model: str
    timeout: int
    max_tokens: int
    anthropic_version: str
    temperature: Optional[float]
    provider_name: str


class AnthropicClient:
    """Anthropic Messages API REST istemcisi."""

    def __init__(
        self,
        config: AnthropicConfig | None = None,
        *,
        api_key_env_name: str = "ANTHROPIC_API_KEY",
    ):
        provider_config = config or settings.anthropic
        self.api_key_env_name = api_key_env_name
        raw_key = provider_config.api_key or ""
        self._key_pool = get_api_key_pool(
            f"{provider_config.provider_name or 'anthropic'}:{provider_config.base_url.rstrip('/')}",
            raw_key,
        )
        self._api_keys: list[str] = split_api_keys(raw_key)
        if self._key_pool.key_count > 1:
            logger.info("anthropic_client_key_rotation enabled=%d keys", self._key_pool.key_count)
        self.api_key = self._api_keys[0] if self._api_keys else ""
        self.last_api_key_fingerprint: str | None = None
        self.last_api_key_index: int | None = None
        self.last_provider_org_fingerprint: str | None = None
        self.model = provider_config.model
        self.base_url = provider_config.base_url.rstrip("/")
        self.messages_url = f"{self.base_url}/v1/messages"
        self.models_url = f"{self.base_url}/v1/models"
        self.timeout = float(provider_config.timeout)
        self.max_tokens = int(provider_config.max_tokens)
        self.anthropic_version = provider_config.anthropic_version
        self.temperature = provider_config.temperature
        self.provider_name = provider_config.provider_name or "anthropic"

    @property
    def is_available(self) -> bool:
        return self._key_pool.is_available or bool(self._api_keys)

    @property
    def api_key_count(self) -> int:
        return self._key_pool.key_count

    def _next_api_key(self) -> str:
        if not self._key_pool.is_available:
            raise AnthropicClientError(
                f"{self.provider_name} API anahtari ({self.api_key_env_name}) yapilandirilmamis."
            )
        return self._next_api_key_lease().key

    def _next_api_key_lease(self) -> ApiKeyLease:
        try:
            lease = self._key_pool.next_key()
        except ValueError as exc:
            raise AnthropicClientError(
                f"{self.provider_name} API anahtari ({self.api_key_env_name}) yapilandirilmamis."
            ) from exc
        self.last_api_key_fingerprint = lease.fingerprint
        self.last_api_key_index = lease.index
        self.last_provider_org_fingerprint = None
        return lease

    def _get_headers(self) -> Dict[str, str]:
        lease = self._next_api_key_lease()
        return {
            "x-api-key": lease.key,
            "anthropic-version": self.anthropic_version,
            "content-type": "application/json",
        }

    def _headers_for_request(self) -> tuple[Dict[str, str], ApiKeyLease]:
        lease = self._next_api_key_lease()
        return (
            {
                "x-api-key": lease.key,
                "anthropic-version": self.anthropic_version,
                "content-type": "application/json",
            },
            lease,
        )

    @staticmethod
    def _extract_available_models(payload: Any) -> list[str]:
        raw_models = payload.get("data", []) if isinstance(payload, dict) else []
        models: list[str] = []
        for item in raw_models or []:
            if isinstance(item, dict) and item.get("id"):
                models.append(str(item["id"]))
        return list(dict.fromkeys(models))

    def _build_payload(
        self,
        prompt: str,
        system: Optional[str],
        json_mode: bool,
        model: str | None,
        *,
        stream: bool = False,
    ) -> dict[str, Any]:
        effective_system = system or ""
        if json_mode:
            json_instruction = "Return only valid JSON. Do not use Markdown, explanations, or code fences."
            effective_system = f"{effective_system}\n\n{json_instruction}".strip()

        payload: dict[str, Any] = {
            "model": model or self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
            "stream": stream,
        }
        if effective_system:
            payload["system"] = effective_system
        if self.temperature is not None:
            payload["temperature"] = self.temperature
        return payload

    @staticmethod
    def _extract_text(data: dict[str, Any]) -> str:
        chunks: list[str] = []
        for item in data.get("content") or []:
            if isinstance(item, dict) and item.get("type") == "text":
                text = str(item.get("text") or "")
                if text:
                    chunks.append(text)
        return "".join(chunks).strip()

    async def get_health(self, *, models: list[str] | None = None) -> Dict[str, Any]:
        configured_models = list(dict.fromkeys(model for model in (models or []) if model)) or [self.model]
        if not self._api_keys:
            return {
                "status": "unhealthy",
                "reason": "API_KEY_MISSING",
                "model_found": False,
                "provider": self.provider_name,
                "base_url": self.base_url,
                "available_models": [],
                "configured_models": configured_models,
                "configured_models_found": {model_name: False for model_name in configured_models},
            }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                headers, _lease = self._headers_for_request()
                response = await client.get(
                    self.models_url,
                    headers=headers,
                    params={"limit": 1000},
                )
                response.raise_for_status()
                available_models = self._extract_available_models(response.json())
                found_models = {
                    model_name: model_name in available_models
                    for model_name in configured_models
                }
                return {
                    "status": "healthy" if all(found_models.values()) else "model_missing",
                    "model_found": found_models.get(self.model, all(found_models.values())),
                    "provider": self.provider_name,
                    "base_url": self.base_url,
                    "available_models": available_models,
                    "configured_models": configured_models,
                    "configured_models_found": found_models,
                }
        except (httpx.HTTPError, AnthropicClientError) as exc:
            return {
                "status": "unhealthy",
                "reason": "API_ERROR",
                "error": str(exc),
                "model_found": False,
                "provider": self.provider_name,
                "base_url": self.base_url,
                "available_models": [],
                "configured_models": configured_models,
                "configured_models_found": {model_name: False for model_name in configured_models},
            }

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        json_mode: bool = False,
        *,
        model: str | None = None,
    ) -> str:
        payload = self._build_payload(prompt, system, json_mode, model)
        lease: ApiKeyLease | None = None
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers, lease = self._headers_for_request()
                response = await client.post(
                    self.messages_url,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                text = self._extract_text(response.json())
                if not text:
                    raise AnthropicClientError(
                        f"{self.provider_name} yaniti bos icerik dondu.",
                        retryable=False,
                    )
                return text
        except httpx.TimeoutException:
            raise AnthropicClientError(
                f"{self.provider_name} yanit suresi asildi ({self.timeout}s).",
                retryable=True,
                api_key_fingerprint=lease.fingerprint if lease else self.last_api_key_fingerprint,
                api_key_index=lease.index if lease else self.last_api_key_index,
            )
        except httpx.HTTPStatusError as exc:
            retryable = exc.response.status_code == 429 or exc.response.status_code >= 500
            if lease is not None and exc.response.status_code == 429:
                self._key_pool.mark_error(
                    fingerprint=lease.fingerprint,
                    reason="rate_limit",
                    cooldown_seconds=60.0,
                )
            raise AnthropicClientError(
                f"{self.provider_name} HTTP hatasi ({exc.response.status_code}): {exc.response.text}",
                retryable=retryable,
                api_key_fingerprint=lease.fingerprint if lease else self.last_api_key_fingerprint,
                api_key_index=lease.index if lease else self.last_api_key_index,
            )
        except httpx.RequestError as exc:
            raise AnthropicClientError(
                f"{self.provider_name} baglanti hatasi: {str(exc)}",
                retryable=True,
                api_key_fingerprint=lease.fingerprint if lease else self.last_api_key_fingerprint,
                api_key_index=lease.index if lease else self.last_api_key_index,
            )

    async def generate_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        *,
        model: str | None = None,
    ) -> AsyncGenerator[str, None]:
        payload = self._build_payload(prompt, system, False, model, stream=True)
        lease: ApiKeyLease | None = None
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers, lease = self._headers_for_request()
                async with client.stream(
                    "POST",
                    self.messages_url,
                    headers=headers,
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        try:
                            event = json.loads(line[6:])
                        except json.JSONDecodeError:
                            continue
                        if event.get("type") != "content_block_delta":
                            continue
                        delta = event.get("delta") or {}
                        text = delta.get("text")
                        if text:
                            yield str(text)
        except httpx.TimeoutException:
            raise AnthropicClientError(
                f"{self.provider_name} stream yanit suresi asildi ({self.timeout}s).",
                retryable=True,
                api_key_fingerprint=lease.fingerprint if lease else self.last_api_key_fingerprint,
                api_key_index=lease.index if lease else self.last_api_key_index,
            )
        except httpx.HTTPStatusError as exc:
            retryable = exc.response.status_code == 429 or exc.response.status_code >= 500
            if lease is not None and exc.response.status_code == 429:
                self._key_pool.mark_error(
                    fingerprint=lease.fingerprint,
                    reason="rate_limit",
                    cooldown_seconds=60.0,
                )
            raise AnthropicClientError(
                f"{self.provider_name} stream HTTP hatasi ({exc.response.status_code}): {exc.response.text}",
                retryable=retryable,
                api_key_fingerprint=lease.fingerprint if lease else self.last_api_key_fingerprint,
                api_key_index=lease.index if lease else self.last_api_key_index,
            )
        except httpx.RequestError as exc:
            raise AnthropicClientError(
                f"{self.provider_name} stream baglanti hatasi: {str(exc)}",
                retryable=True,
                api_key_fingerprint=lease.fingerprint if lease else self.last_api_key_fingerprint,
                api_key_index=lease.index if lease else self.last_api_key_index,
            )
