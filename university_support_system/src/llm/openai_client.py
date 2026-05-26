"""
OpenAI-compatible LLM istemcisi.

OpenAI veya Groq gibi OpenAI-compatible endpoint'lerle calisabilir.
Yine zero dependency hedefine uygun olarak REST API uzerinden (httpx ile)
implemente edilmistir.
"""

import json
import logging
import re
from typing import Any, AsyncGenerator, Dict, Optional, Protocol

import httpx

from src.core.config import settings
from src.llm.api_key_pool import (
    ApiKeyLease,
    get_api_key_pool,
    org_fingerprint_from_message,
    split_api_keys,
)

logger = logging.getLogger(__name__)

_TRY_AGAIN_RE = re.compile(r"try again in\s+([0-9a-zA-Z.]+)", re.IGNORECASE)
_DURATION_PART_RE = re.compile(r"(\d+(?:\.\d+)?)(ms|h|m|s)")


class OpenAIClientError(Exception):
    """OpenAI-compatible provider ile iletisim sirasinda olusan hatalar."""

    def __init__(
        self,
        message: str,
        *,
        retryable: bool = False,
        api_key_fingerprint: str | None = None,
        api_key_index: int | None = None,
        provider_org_fingerprint: str | None = None,
    ):
        super().__init__(message)
        self.retryable = retryable
        self.api_key_fingerprint = api_key_fingerprint
        self.api_key_index = api_key_index
        self.provider_org_fingerprint = provider_org_fingerprint


class OpenAICompatibleConfig(Protocol):
    """Minimum config surface required by OpenAI-compatible providers."""

    api_key: Optional[str]
    base_url: str
    model: str
    timeout: int
    provider_name: str


class OpenAIClient:
    """OpenAI-compatible HTTP REST API istemcisi."""

    def __init__(
        self,
        config: OpenAICompatibleConfig | None = None,
        *,
        api_key_env_name: str = "OPENAI_API_KEY",
    ):
        provider_config = config or settings.openai
        self.api_key_env_name = api_key_env_name
        raw_key = provider_config.api_key or ""
        self._key_pool = get_api_key_pool(
            f"{provider_config.provider_name or 'openai_compatible'}:{provider_config.base_url.rstrip('/')}",
            raw_key,
        )
        self._api_keys: list[str] = split_api_keys(raw_key)
        if self._key_pool.key_count > 1:
            logger.info("openai_client_key_rotation enabled=%d keys", self._key_pool.key_count)
        self.api_key = self._api_keys[0] if self._api_keys else ""
        self.last_api_key_fingerprint: str | None = None
        self.last_api_key_index: int | None = None
        self.last_provider_org_fingerprint: str | None = None
        self.model = provider_config.model
        self.base_url = provider_config.base_url.rstrip("/")
        self.chat_url = f"{self.base_url}/chat/completions"
        self.timeout = float(provider_config.timeout)
        self.provider_name = provider_config.provider_name or "openai_compatible"
        self.reasoning_effort = getattr(provider_config, "reasoning_effort", None)

    @property
    def is_available(self) -> bool:
        """API key tanimli mi?"""
        return self._key_pool.is_available or bool(self._api_keys)

    @property
    def api_key_count(self) -> int:
        return self._key_pool.key_count

    def _next_api_key(self) -> str:
        """Round-robin ile siradaki API key'i dondurur."""
        if not self._key_pool.is_available:
            raise OpenAIClientError(
                f"{self.provider_name} API anahtari ({self.api_key_env_name}) yapilandirilmamis."
            )
        return self._next_api_key_lease().key

    def _next_api_key_lease(self) -> ApiKeyLease:
        try:
            lease = self._key_pool.next_key()
        except ValueError as exc:
            raise OpenAIClientError(
                f"{self.provider_name} API anahtari ({self.api_key_env_name}) yapilandirilmamis."
            ) from exc
        self.last_api_key_fingerprint = lease.fingerprint
        self.last_api_key_index = lease.index
        self.last_provider_org_fingerprint = None
        return lease

    def _get_headers(self) -> Dict[str, str]:
        api_key = self._next_api_key()
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _headers_for_request(self) -> tuple[Dict[str, str], ApiKeyLease]:
        lease = self._next_api_key_lease()
        return (
            {
                "Authorization": f"Bearer {lease.key}",
                "Content-Type": "application/json",
            },
            lease,
        )

    @staticmethod
    def _rate_limit_cooldown_seconds(response: httpx.Response) -> float:
        retry_after = response.headers.get("retry-after")
        if retry_after:
            try:
                return max(1.0, float(retry_after))
            except ValueError:
                pass
        parsed = OpenAIClient._cooldown_seconds_from_provider_message(response.text)
        if parsed is not None:
            return parsed
        return 60.0

    @staticmethod
    def _cooldown_seconds_from_provider_message(message: str) -> float | None:
        match = _TRY_AGAIN_RE.search(message or "")
        if not match:
            return None
        duration = match.group(1)
        total = 0.0
        for part in _DURATION_PART_RE.finditer(duration):
            value = float(part.group(1))
            unit = part.group(2)
            if unit == "ms":
                total += value / 1000.0
            elif unit == "s":
                total += value
            elif unit == "m":
                total += value * 60.0
            elif unit == "h":
                total += value * 3600.0
        if total <= 0:
            return None
        return max(1.0, min(total, 6 * 3600.0))

    @staticmethod
    def _normalize_model_name(model_name: str) -> str:
        """Normalize provider-specific model ids to a comparable form."""
        normalized = model_name.strip()
        if normalized.startswith("models/"):
            normalized = normalized.split("/", 1)[1]
        return normalized

    @classmethod
    def _extract_available_models(cls, payload: Any) -> list[str]:
        """Normalize model-list payloads returned by OpenAI-compatible providers."""
        raw_models: Any
        if isinstance(payload, dict):
            raw_models = payload.get("data")
            if raw_models is None:
                raw_models = payload.get("models", [])
        elif isinstance(payload, list):
            raw_models = payload
        else:
            raw_models = []

        available_models: list[str] = []
        for item in raw_models or []:
            if isinstance(item, str):
                available_models.append(cls._normalize_model_name(item))
                continue
            if isinstance(item, dict):
                model_name = item.get("id") or item.get("name")
                if model_name:
                    available_models.append(cls._normalize_model_name(str(model_name)))

        return list(dict.fromkeys(available_models))

    async def get_health(self, *, models: list[str] | None = None) -> Dict[str, Any]:
        """
        API baglantisini kontrol eder.
        Basit bir model listesi sorgusu ile key/gecerlilik testi yapar.
        """
        configured_models = list(dict.fromkeys(model for model in (models or []) if model))
        if not configured_models:
            configured_models = [self.model]

        if not self._api_keys:
            return {
                "status": "unhealthy",
                "reason": "API_KEY_MISSING",
                "model_found": False,
                "provider": self.provider_name,
                "base_url": self.base_url,
                "available_models": [],
                "configured_models": configured_models,
                "configured_models_found": {
                    model_name: False for model_name in configured_models
                },
            }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                headers, _lease = self._headers_for_request()
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=headers,
                )
                response.raise_for_status()
                payload = response.json()
                available_models = self._extract_available_models(payload)
                found_models = {
                    model_name: model_name in available_models
                    for model_name in configured_models
                }
                default_model_found = found_models.get(self.model, all(found_models.values()))
                return {
                    "status": "healthy" if all(found_models.values()) else "model_missing",
                    "model_found": default_model_found,
                    "provider": self.provider_name,
                    "base_url": self.base_url,
                    "available_models": available_models,
                    "configured_models": configured_models,
                    "configured_models_found": found_models,
                }
        except (httpx.HTTPError, OpenAIClientError) as exc:
            return {
                "status": "unhealthy",
                "reason": "API_ERROR",
                "error": str(exc),
                "model_found": False,
                "provider": self.provider_name,
                "base_url": self.base_url,
                "available_models": [],
                "configured_models": configured_models,
                "configured_models_found": {
                    model_name: False for model_name in configured_models
                },
            }

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        json_mode: bool = False,
        *,
        model: str | None = None,
    ) -> str:
        """OpenAI-compatible chat completions API kullanarak metin uretir."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model or self.model,
            "messages": messages,
            "stream": False,
        }
        if self.reasoning_effort:
            payload["reasoning_effort"] = self.reasoning_effort

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        lease: ApiKeyLease | None = None
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers, lease = self._headers_for_request()
                response = await client.post(
                    self.chat_url,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

                choices = data.get("choices") or []
                if not choices:
                    raise OpenAIClientError(
                        f"{self.provider_name} yaniti bos dondu: choices alani yok.",
                        retryable=False,
                    )

                content = choices[0].get("message", {}).get("content")
                if not content or not str(content).strip():
                    raise OpenAIClientError(
                        f"{self.provider_name} yaniti bos icerik dondu.",
                        retryable=False,
                    )
                return str(content)
        except httpx.TimeoutException:
            raise OpenAIClientError(
                f"{self.provider_name} yanit suresi asildi ({self.timeout}s).",
                retryable=True,
                api_key_fingerprint=lease.fingerprint if lease else self.last_api_key_fingerprint,
                api_key_index=lease.index if lease else self.last_api_key_index,
            )
        except httpx.HTTPStatusError as exc:
            error_details = exc.response.text
            retryable = exc.response.status_code == 429 or exc.response.status_code >= 500
            org_fingerprint = org_fingerprint_from_message(error_details)
            self.last_provider_org_fingerprint = org_fingerprint
            if lease is not None and exc.response.status_code == 429:
                self._key_pool.mark_error(
                    fingerprint=lease.fingerprint,
                    reason="rate_limit",
                    cooldown_seconds=self._rate_limit_cooldown_seconds(exc.response),
                    provider_org_fingerprint=org_fingerprint,
                )
            raise OpenAIClientError(
                f"{self.provider_name} HTTP hatasi ({exc.response.status_code}): {error_details}",
                retryable=retryable,
                api_key_fingerprint=lease.fingerprint if lease else self.last_api_key_fingerprint,
                api_key_index=lease.index if lease else self.last_api_key_index,
                provider_org_fingerprint=org_fingerprint,
            )
        except httpx.RequestError as exc:
            raise OpenAIClientError(
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
        """OpenAI-compatible provider uzerinden streaming ile metin uretir."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model or self.model,
            "messages": messages,
            "stream": True,
        }
        if self.reasoning_effort:
            payload["reasoning_effort"] = self.reasoning_effort

        lease: ApiKeyLease | None = None
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers, lease = self._headers_for_request()
                async with client.stream(
                    "POST",
                    self.chat_url,
                    headers=headers,
                    json=payload,
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if not line.startswith("data: "):
                            continue

                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break

                        try:
                            chunk = json.loads(data_str)
                        except json.JSONDecodeError:
                            continue

                        choices = chunk.get("choices") or []
                        if not choices:
                            continue
                        delta = choices[0].get("delta", {})
                        content = delta.get("content")
                        if content:
                            yield content
        except httpx.TimeoutException:
            raise OpenAIClientError(
                f"{self.provider_name} stream yanit suresi asildi ({self.timeout}s).",
                retryable=True,
                api_key_fingerprint=lease.fingerprint if lease else self.last_api_key_fingerprint,
                api_key_index=lease.index if lease else self.last_api_key_index,
            )
        except httpx.HTTPStatusError as exc:
            retryable = exc.response.status_code == 429 or exc.response.status_code >= 500
            org_fingerprint = org_fingerprint_from_message(exc.response.text)
            self.last_provider_org_fingerprint = org_fingerprint
            if lease is not None and exc.response.status_code == 429:
                self._key_pool.mark_error(
                    fingerprint=lease.fingerprint,
                    reason="rate_limit",
                    cooldown_seconds=self._rate_limit_cooldown_seconds(exc.response),
                    provider_org_fingerprint=org_fingerprint,
                )
            raise OpenAIClientError(
                f"{self.provider_name} stream HTTP hatasi ({exc.response.status_code}): {exc.response.text}",
                retryable=retryable,
                api_key_fingerprint=lease.fingerprint if lease else self.last_api_key_fingerprint,
                api_key_index=lease.index if lease else self.last_api_key_index,
                provider_org_fingerprint=org_fingerprint,
            )
        except httpx.RequestError as exc:
            raise OpenAIClientError(
                f"{self.provider_name} stream baglanti hatasi: {str(exc)}",
                retryable=True,
                api_key_fingerprint=lease.fingerprint if lease else self.last_api_key_fingerprint,
                api_key_index=lease.index if lease else self.last_api_key_index,
            )
