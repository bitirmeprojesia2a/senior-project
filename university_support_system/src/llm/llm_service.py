"""
LLM Çekirdek Servisi

Ollama (birincil) ve OpenAI (ikincil/fallback) istemcilerini koordine eder.
Hata yönetimi, retry mekanizması, token limit uyarıları ve JSON çıktı garantisini sağlar.
"""

import json
import logging
from typing import Any, AsyncGenerator, Dict, Optional

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.llm.ollama_client import OllamaClient, OllamaClientError
from src.llm.openai_client import OpenAIClient, OpenAIClientError

logger = logging.getLogger(__name__)

# Token limiti (Qwen2.5:7b genellikle 128k, yedek OpenAI modeli de benzer veya daha büyüktür)
TOKEN_WARNING_LIMIT = 100000 
APPROX_CHARS_PER_TOKEN = 4 # Basit bir tahmin hesabı: 1 token ~ 4 karakter


class LLMServiceError(Exception):
    """LLM servisinden yanıt alınamadı (tüm fallbackler tükendi)."""
    pass


class LLMService:
    """Ollama ve OpenAI'ı koordine eden ana LLM Servisi."""

    def __init__(self):
        self.ollama = OllamaClient()
        self.openai = OpenAIClient()
        self.use_fallback = self.openai.is_available

    def _check_token_limit(self, prompt: str, system: Optional[str] = None) -> None:
        """Metin uzunluğunu kontrol eder ve limite yaklaşılırsa uyarı verir."""
        total_len = len(prompt)
        if system:
            total_len += len(system)
            
        estimated_tokens = total_len / APPROX_CHARS_PER_TOKEN
        
        if estimated_tokens > TOKEN_WARNING_LIMIT:
            logger.warning(
                f"LLM Token Uyarı: Tahmini {int(estimated_tokens)} token sınıra yaklaşıyor! "
                "Cevap kesilebilir."
            )

    def _validate_json(self, response: str) -> str:
        """Gelen yanıtın geçerli bir JSON olup olmadığını doğrular."""
        try:
            # Sadece parse edilip edilemediğini kontrol ediyoruz
            json.loads(response)
            return response
        except json.JSONDecodeError as e:
            logger.error(f"LLM yanıtı JSON olarak ayrıştırılamadı. Yanıt: {response[:100]}...")
            raise LLMServiceError(f"Geçersiz JSON formatı: {str(e)}")

    @retry(
        retry=retry_if_exception_type(OllamaClientError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def _generate_ollama_with_retry(
        self, prompt: str, system: Optional[str] = None, json_mode: bool = False
    ) -> str:
        """Ollama üzerinden fail-retry mantığı ile üretim yapar."""
        return await self.ollama.generate(prompt=prompt, system=system, json_mode=json_mode)

    async def get_health(self) -> Dict[str, Any]:
        """Sistemin (Ollama + OpenAI) sağlık durumunu kontrol eder."""
        ollama_health = await self.ollama.get_health()
        
        health_status = {
            "status": "healthy" if ollama_health["status"] == "healthy" else "degraded",
            "primary": {
                "name": "ollama",
                "status": ollama_health["status"],
                "model_loaded": ollama_health.get("model_found", False)
            },
            "fallback": {
                "name": "openai",
                "available": self.use_fallback,
            }
        }
        
        if self.use_fallback:
            openai_health = await self.openai.get_health()
            health_status["fallback"]["status"] = openai_health["status"]
            
            # Eğer ikisi de çökmüşse sistem patlak
            if ollama_health["status"] != "healthy" and openai_health["status"] != "healthy":
                health_status["status"] = "unhealthy"
                
        return health_status

    async def generate(
        self, prompt: str, system: Optional[str] = None, json_mode: bool = False
    ) -> str:
        """
        LLM ile metin üretir.
        Ollama ile 3 kez dener, başarısız olursa OpenAI'a geçer.
        json_mode=True verilirse JSON formatında çıktıyı doğrular.
        """
        self._check_token_limit(prompt, system)
        
        try:
            # 1. Aşama: Ollama'yı dene (Exponential Backoff ile)
            logger.debug("Üretim için Ollama (Yerel LLM) kullanılıyor.")
            response_text = await self._generate_ollama_with_retry(
                prompt=prompt, system=system, json_mode=json_mode
            )
            
        except OllamaClientError as ollama_error:
            logger.warning(f"Ollama başarısız oldu: {str(ollama_error)}. Fallback mekanizması kontrol ediliyor...")
            
            # 2. Aşama: Fallback kontrolü ve OpenAI'ye geçiş
            if not self.use_fallback:
                logger.error("Ollama çöktü ve OpenAI fallback key'i bulunamadı!")
                raise LLMServiceError(f"Yerel LLM servisine ulaşılamıyor ve yedek sistem tanımlı değil. Detay: {str(ollama_error)}")
                
            try:
                logger.info("OpenAI Fallback devrede.")
                response_text = await self.openai.generate(
                    prompt=prompt, system=system, json_mode=json_mode
                )
            except OpenAIClientError as openai_error:
                logger.error(f"OpenAI fallback de başarısız oldu: {str(openai_error)}")
                raise LLMServiceError(f"Tüm LLM servisleri erişilemez durumda. Ollama: {str(ollama_error)} | OpenAI: {str(openai_error)}")

        # 3. Aşama: JSON Modu Doğrulaması
        if json_mode:
            return self._validate_json(response_text)
            
        return response_text

    async def generate_stream(
        self, prompt: str, system: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Streaming formatında yanıt üretir (JSON doğrulaması stream için kapalıdır).
        Burada şimdilik fail mantığında anlık fallback yapılmaz,
        Ollama hata verirse doğrudan fallback akışına aktarım denenir.
        """
        self._check_token_limit(prompt, system)

        try:
            # Ollama Stream
            async for chunk in self.ollama.generate_stream(prompt, system):
                yield chunk
                
        except OllamaClientError as ollama_error:
            logger.warning(f"Ollama stream hata verdi: {str(ollama_error)}. Fallback stream aranıyor...")
            
            if not self.use_fallback:
                raise LLMServiceError(f"Stream: Yerel LLM koptu ve yedek sistem bulunamadı. Detay: {str(ollama_error)}")
                
            # Fallback Stream
            try:
                logger.info("OpenAI Fallback Stream başlatılıyor...")
                async for chunk in self.openai.generate_stream(prompt, system):
                    yield chunk
            except OpenAIClientError as openai_error:
                raise LLMServiceError(f"Stream: Tüm LLM servisleri çöktü. Ollama: {str(ollama_error)} | OpenAI: {str(openai_error)}")

