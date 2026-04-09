"""
Ollama istemcisi.

Docker icindeki Ollama sunucusuyla HTTP uzerinden haberlesir.
Resmi Python paketine bagli kalmadan REST API kullanir.
"""

from __future__ import annotations

import json
from typing import Any, AsyncGenerator, Dict, Optional

import httpx

from src.core.config import settings


class OllamaClientError(Exception):
    """Ollama ile iletisim sirasinda olusan hatalar."""


class OllamaClient:
    """Ollama HTTP REST API istemcisi."""

    def __init__(self):
        self.host = settings.ollama.host
        self.default_model = settings.ollama.model
        self.timeout = settings.ollama.timeout
        self.generate_url = f"{self.host}/api/generate"
        self.chat_url = f"{self.host}/api/chat"
        self.tags_url = f"{self.host}/api/tags"

    async def get_health(self, *, models: list[str] | None = None) -> Dict[str, Any]:
        """Ollama ayakta mi ve gerekli modeller yuklu mu kontrol eder."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(self.tags_url)
                response.raise_for_status()
                data = response.json()

                available_models = [
                    str(model_name)
                    for model_name in (item.get("name") for item in data.get("models", []))
                    if model_name
                ]
                requested_models = list(dict.fromkeys(model for model in (models or []) if model))
                if not requested_models:
                    requested_models = [self.default_model]

                found_models = {
                    model: any(model in available for available in available_models)
                    for model in requested_models
                }
                is_model_loaded = found_models.get(self.default_model, False)

                return {
                    "status": "healthy" if all(found_models.values()) else "model_missing",
                    "model_found": is_model_loaded,
                    "available_models": available_models,
                    "configured_models": requested_models,
                    "configured_models_found": found_models,
                }
        except httpx.RequestError as exc:
            return {
                "status": "unhealthy",
                "error": str(exc),
                "model_found": False,
            }

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        json_mode: bool = False,
        *,
        model: str | None = None,
    ) -> str:
        """Standart metin uretimi yapar."""
        payload = {
            "model": model or self.default_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": settings.ollama.num_ctx,
                "num_predict": settings.ollama.num_predict,
            },
        }

        if system:
            payload["system"] = system

        if json_mode:
            payload["format"] = "json"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.generate_url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
        except httpx.TimeoutException as exc:
            raise OllamaClientError(f"Ollama yanit suresi asildi ({self.timeout}s).") from exc
        except httpx.HTTPStatusError as exc:
            raise OllamaClientError(
                f"Ollama HTTP hatasi: {exc.response.status_code} - {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            raise OllamaClientError(f"Ollama baglanti hatasi: {str(exc)}") from exc

    async def generate_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        *,
        model: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Streaming destekli metin uretimi yapar."""
        payload = {
            "model": model or self.default_model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "num_ctx": settings.ollama.num_ctx,
                "num_predict": settings.ollama.num_predict,
            },
        }

        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", self.generate_url, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            chunk = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if "response" in chunk:
                            yield chunk["response"]
        except httpx.TimeoutException as exc:
            raise OllamaClientError(f"Ollama stream yanit suresi asildi ({self.timeout}s).") from exc
        except httpx.HTTPStatusError as exc:
            raise OllamaClientError(
                f"Ollama stream HTTP hatasi: {exc.response.status_code} - {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            raise OllamaClientError(f"Ollama stream baglanti hatasi: {str(exc)}") from exc
        except Exception as exc:
            raise OllamaClientError(f"Ollama stream hatasi: {str(exc)}") from exc
