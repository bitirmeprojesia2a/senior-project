"""
OpenAI (Yedek LLM) İstemcisi

Ollama'nın çalışmadığı durumlarda fallback olarak devreye girer.
Yine zero dependency hedefine uygun olarak REST API üzerinden (httpx ile) implemente edilmiştir.
"""

import json
from typing import Any, AsyncGenerator, Dict, Optional

import httpx

from src.core.config import settings


class OpenAIClientError(Exception):
    """OpenAI ile iletişim sırasında oluşan hatalar."""
    pass


class OpenAIClient:
    """OpenAI HTTP REST API İstemcisi"""

    def __init__(self):
        self.api_key = settings.openai.api_key
        self.model = settings.openai.model
        self.base_url = "https://api.openai.com/v1"
        self.chat_url = f"{self.base_url}/chat/completions"
        self.timeout = 30.0

    @property
    def is_available(self) -> bool:
        """API Key tanımlanmış mı?"""
        return bool(self.api_key)

    def _get_headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise OpenAIClientError("OpenAI API anahtarı (OPENAI_API_KEY) yapılandırılmamış.")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def get_health(self) -> Dict[str, Any]:
        """
        API bağlantısını kontrol eder.
        Sadece API key format kontrolü yapar çünkü OpenAI'ın yetkisiz basit bir test endpointi yok.
        """
        if not self.api_key:
            return {
                "status": "unhealthy",
                "reason": "API_KEY_MISSING",
                "model_found": False
            }
        
        # Sadece basit bir model listesi sorgusu ile key geçerliliğini test et
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return {
                    "status": "healthy",
                    "model_found": True
                }
        except (httpx.HTTPError, OpenAIClientError) as e:
            return {
                "status": "unhealthy",
                "reason": "API_ERROR",
                "error": str(e),
                "model_found": False
            }

    async def generate(self, prompt: str, system: Optional[str] = None, json_mode: bool = False) -> str:
        """
        OpenAI chat completions API'sini kullanarak metin üretir.
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
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
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                return ""
        except httpx.TimeoutException:
            raise OpenAIClientError(f"OpenAI yanıt süresi aşıldı ({self.timeout}s).")
        except httpx.HTTPStatusError as e:
            error_details = e.response.text
            raise OpenAIClientError(f"OpenAI HTTP hatası ({e.response.status_code}): {error_details}")
        except httpx.RequestError as e:
            raise OpenAIClientError(f"OpenAI bağlantı hatası: {str(e)}")

    async def generate_stream(self, prompt: str, system: Optional[str] = None) -> AsyncGenerator[str, None]:
        """
        OpenAI üzerinden streaming ile metin üretir.
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST", 
                    self.chat_url, 
                    headers=self._get_headers(), 
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str.strip() == "[DONE]":
                                break
                            
                            try:
                                chunk = json.loads(data_str)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if "content" in delta and delta["content"]:
                                        yield delta["content"]
                            except json.JSONDecodeError:
                                continue
        except httpx.TimeoutException:
            raise OpenAIClientError(f"OpenAI stream yanıt süresi aşıldı ({self.timeout}s).")
        except httpx.HTTPStatusError as e:
            raise OpenAIClientError(f"OpenAI stream HTTP hatası ({e.response.status_code}): {e.response.text}")
        except httpx.RequestError as e:
            raise OpenAIClientError(f"OpenAI stream bağlantı hatası: {str(e)}")
