"""
OpenAI-compatible LLM istemcisi.

OpenAI veya Groq gibi OpenAI-compatible endpoint'lerle calisabilir.
Yine zero dependency hedefine uygun olarak REST API uzerinden (httpx ile)
implemente edilmistir.
"""

import itertools
import json
import logging
from typing import Any, AsyncGenerator, Dict, Optional

import httpx

from src.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIClientError(Exception):
    """OpenAI-compatible provider ile iletisim sirasinda olusan hatalar."""

    def __init__(self, message: str, *, retryable: bool = False):
        super().__init__(message)
        self.retryable = retryable


class OpenAIClient:
    """OpenAI-compatible HTTP REST API istemcisi."""

    def __init__(self):
        raw_key = settings.openai.api_key or ""
        self._api_keys: list[str] = [k.strip() for k in raw_key.split(",") if k.strip()]
        self._key_cycle = itertools.cycle(self._api_keys) if self._api_keys else None
        if len(self._api_keys) > 1:
            logger.info("openai_client_key_rotation enabled=%d keys", len(self._api_keys))
        self.api_key = self._api_keys[0] if self._api_keys else ""
        self.model = settings.openai.model
        self.base_url = settings.openai.base_url.rstrip("/")
        self.chat_url = f"{self.base_url}/chat/completions"
        self.timeout = float(settings.openai.timeout)
        self.provider_name = settings.openai.provider_name or "openai_compatible"

    @property
    def is_available(self) -> bool:
        """API key tanimli mi?"""
        return bool(self._api_keys)

    def _next_api_key(self) -> str:
        """Round-robin ile siradaki API key'i dondurur."""
        if self._key_cycle is None:
            raise OpenAIClientError(
                f"{self.provider_name} API anahtari (OPENAI_API_KEY) yapilandirilmamis."
            )
        return next(self._key_cycle)

    def _get_headers(self) -> Dict[str, str]:
        api_key = self._next_api_key()
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def get_health(self) -> Dict[str, Any]:
        """
        API baglantisini kontrol eder.
        Basit bir model listesi sorgusu ile key/gecerlilik testi yapar.
        """
        if not self._api_keys:
            return {
                "status": "unhealthy",
                "reason": "API_KEY_MISSING",
                "model_found": False,
                "provider": self.provider_name,
            }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                return {
                    "status": "healthy",
                    "model_found": True,
                    "provider": self.provider_name,
                    "base_url": self.base_url,
                }
        except (httpx.HTTPError, OpenAIClientError) as exc:
            return {
                "status": "unhealthy",
                "reason": "API_ERROR",
                "error": str(exc),
                "model_found": False,
                "provider": self.provider_name,
                "base_url": self.base_url,
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

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.chat_url,
                    headers=self._get_headers(),
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
            )
        except httpx.HTTPStatusError as exc:
            error_details = exc.response.text
            retryable = exc.response.status_code == 429 or exc.response.status_code >= 500
            raise OpenAIClientError(
                f"{self.provider_name} HTTP hatasi ({exc.response.status_code}): {error_details}",
                retryable=retryable,
            )
        except httpx.RequestError as exc:
            raise OpenAIClientError(
                f"{self.provider_name} baglanti hatasi: {str(exc)}",
                retryable=True,
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

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    self.chat_url,
                    headers=self._get_headers(),
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
            )
        except httpx.HTTPStatusError as exc:
            retryable = exc.response.status_code == 429 or exc.response.status_code >= 500
            raise OpenAIClientError(
                f"{self.provider_name} stream HTTP hatasi ({exc.response.status_code}): {exc.response.text}",
                retryable=retryable,
            )
        except httpx.RequestError as exc:
            raise OpenAIClientError(
                f"{self.provider_name} stream baglanti hatasi: {str(exc)}",
                retryable=True,
            )
