"""
Ollama (Yerel LLM) İstemcisi

Doğrudan docker container'ı ile HTTP üzerinden (httpx) konuşur.
Zero dependency felsefesine sadık kalmak ve lightweight bir mimari sunmak için
resmi 'ollama' python paketine bağlı kalmadan REST API kullanarak implemente edilmiştir.
"""

import json
from typing import Any, AsyncGenerator, Dict, Optional

import httpx

from src.core.config import settings


class OllamaClientError(Exception):
    """Ollama ile iletişim sırasında oluşan hatalar."""
    pass


class OllamaClient:
    """Ollama HTTP REST API İstemcisi"""

    def __init__(self):
        self.host = settings.ollama.host
        self.default_model = settings.ollama.model
        self.timeout = settings.ollama.timeout
        self.generate_url = f"{self.host}/api/generate"
        self.chat_url = f"{self.host}/api/chat"
        self.tags_url = f"{self.host}/api/tags"

    async def get_health(self, *, models: list[str] | None = None) -> Dict[str, Any]:
        """
        Ollama ayakta mı ve kullanılacak model yüklü mü kontrol eder.
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(self.tags_url)
                response.raise_for_status()
                data = response.json()
                
                available_models = [
                    str(model_name)
                    for model_name in (m.get("name") for m in data.get("models", []))
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
        except httpx.RequestError as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "model_found": False
            }

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        json_mode: bool = False,
        *,
        model: str | None = None,
    ) -> str:
        """
        Standart meteryal üretimi (/api/generate) yapar.
        Eğer json_mode True ise modelin çıktısını JSON olarak sınırlandırmaya çalışır.
        """
        payload = {
            "model": model or self.default_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                # Qwen modelleri için timeout veya context spesifik ayarlar buraya gelebilir
                "num_ctx": 16384  # Güvenli bir bağlam boyutu
            }
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
        except httpx.TimeoutException:
            raise OllamaClientError(f"Ollama yanıt süresi aşıldı ({self.timeout}s).")
        except httpx.HTTPStatusError as e:
            raise OllamaClientError(f"Ollama HTTP hatası: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise OllamaClientError(f"Ollama bağlantı hatası: {str(e)}")

    async def generate_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        *,
        model: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        Streaming destekli materyal üretimi (Slack / WebUI için).
        """
        payload = {
            "model": model or self.default_model,
            "prompt": prompt,
            "stream": True
        }
        
        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", self.generate_url, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                chunk = json.loads(line)
                                if "response" in chunk:
                                    yield chunk["response"]
                            except json.JSONDecodeError:
                                continue
        except httpx.TimeoutException:
            raise OllamaClientError(f"Ollama stream yanıt süresi aşıldı ({self.timeout}s).")
        except httpx.HTTPStatusError as e:
            raise OllamaClientError(f"Ollama stream HTTP hatası: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise OllamaClientError(f"Ollama stream bağlantı hatası: {str(e)}")
