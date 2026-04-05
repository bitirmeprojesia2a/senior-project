"""
LLM cekirdek servisi.

Ollama (birincil) ve OpenAI (ikincil/fallback) istemcilerini koordine eder.
"""

import json
import logging
from typing import Any, AsyncGenerator, Dict, Optional

from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from src.core.config import settings
from src.core.profiling import profile_stage
from src.llm.ollama_client import OllamaClient, OllamaClientError
from src.llm.openai_client import OpenAIClient, OpenAIClientError

logger = logging.getLogger(__name__)

TOKEN_WARNING_LIMIT = 100000
APPROX_CHARS_PER_TOKEN = 4


def _is_missing_model_error_message(message: str) -> bool:
    lowered = message.lower()
    return (
        "model" in lowered
        and (
            "not found" in lowered
            or "pull" in lowered
            or "missing" in lowered
        )
    )


def _should_retry_ollama_error(exc: BaseException) -> bool:
    return isinstance(exc, OllamaClientError) and not _is_missing_model_error_message(str(exc))


class LLMServiceError(Exception):
    """LLM servisinden yanit alinamadi."""


class LLMService:
    """Ollama ve OpenAI'yi koordine eden ana LLM servisi."""

    def __init__(self):
        self.ollama = OllamaClient()
        self.openai = OpenAIClient()
        self.use_fallback = self.openai.is_available

    def _check_token_limit(self, prompt: str, system: Optional[str] = None) -> None:
        """Metin uzunlugunu kontrol eder ve limite yaklasilirsa uyari verir."""
        total_len = len(prompt)
        if system:
            total_len += len(system)

        estimated_tokens = total_len / APPROX_CHARS_PER_TOKEN
        if estimated_tokens > TOKEN_WARNING_LIMIT:
            logger.warning(
                "LLM Token Uyarisi: Tahmini %s token sinira yaklasiyor. Cevap kesilebilir.",
                int(estimated_tokens),
            )

    def _validate_json(self, response: str) -> str:
        """Gelen yanitin gecerli bir JSON olup olmadigini dogrular."""
        try:
            json.loads(response)
            return response
        except json.JSONDecodeError as exc:
            logger.error("LLM yaniti JSON olarak ayrisamadi. Yanit: %s...", response[:100])
            raise LLMServiceError(f"Gecersiz JSON formati: {str(exc)}") from exc

    def _resolve_ollama_model(
        self,
        *,
        model: str | None = None,
        model_role: str = "default",
        llm_profile: str | None = None,
    ) -> str:
        """Cagri bazli Ollama modelini cozumler."""
        if model:
            return model
        return settings.resolve_llm_model(role=model_role, profile=llm_profile)

    @staticmethod
    def _looks_like_missing_model_error(exc: OllamaClientError) -> bool:
        """Ollama model eksikligi benzeri hatalari ayiklar."""
        return _is_missing_model_error_message(str(exc))

    @retry(
        retry=retry_if_exception(_should_retry_ollama_error),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _generate_ollama_with_retry(
        self,
        prompt: str,
        system: Optional[str] = None,
        json_mode: bool = False,
        *,
        model: str | None = None,
    ) -> str:
        """Ollama uzerinden retry mantigi ile uretim yapar."""
        return await self.ollama.generate(
            prompt=prompt,
            system=system,
            json_mode=json_mode,
            model=model,
        )

    async def get_health(self) -> Dict[str, Any]:
        """Sistemin (Ollama + OpenAI) saglik durumunu kontrol eder."""
        model_map = settings.configured_llm_models()
        ollama_health = await self.ollama.get_health(
            models=[
                model_map["primary"],
                model_map["secondary"],
                model_map["routing"],
                model_map["conversation"],
                model_map["specialist_synthesis"],
                model_map["global_synthesis"],
            ]
        )

        health_status = {
            "status": "healthy" if ollama_health["status"] == "healthy" else "degraded",
            "primary": {
                "name": "ollama",
                "status": ollama_health["status"],
                "model_loaded": ollama_health.get("model_found", False),
                "configured_models": model_map,
                "available_models": ollama_health.get("available_models", []),
                "configured_models_found": ollama_health.get("configured_models_found", {}),
            },
            "fallback": {
                "name": "openai",
                "available": self.use_fallback,
            },
        }

        if self.use_fallback:
            openai_health = await self.openai.get_health()
            health_status["fallback"]["status"] = openai_health["status"]

            if ollama_health["status"] != "healthy" and openai_health["status"] != "healthy":
                health_status["status"] = "unhealthy"

        return health_status

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        json_mode: bool = False,
        *,
        model: str | None = None,
        model_role: str = "default",
        llm_profile: str | None = None,
    ) -> str:
        """
        LLM ile metin uretir.

        Ollama ile 3 kez dener, basarisiz olursa OpenAI'a gecer.
        """
        with profile_stage("llm.generate", json_mode=json_mode):
            self._check_token_limit(prompt, system)
            resolved_model = self._resolve_ollama_model(
                model=model,
                model_role=model_role,
                llm_profile=llm_profile,
            )

            try:
                logger.debug("Uretim icin Ollama (yerel LLM) kullaniliyor. model=%s role=%s", resolved_model, model_role)
                with profile_stage("llm.generate.ollama", model=resolved_model, role=model_role):
                    response_text = await self._generate_ollama_with_retry(
                        prompt=prompt,
                        system=system,
                        json_mode=json_mode,
                        model=resolved_model,
                    )
            except OllamaClientError as ollama_error:
                primary_model = settings.ollama.model
                if (
                    resolved_model != primary_model
                    and self._looks_like_missing_model_error(ollama_error)
                ):
                    logger.warning(
                        "Istenen Ollama modeli kullanilamadi (%s). Birincil modele dusuluyor: %s",
                        resolved_model,
                        primary_model,
                    )
                    try:
                        with profile_stage("llm.generate.ollama_primary_fallback", model=primary_model, role=model_role):
                            response_text = await self._generate_ollama_with_retry(
                                prompt=prompt,
                                system=system,
                                json_mode=json_mode,
                                model=primary_model,
                            )
                    except OllamaClientError as primary_error:
                        ollama_error = primary_error
                    else:
                        if json_mode:
                            with profile_stage("llm.generate.validate_json"):
                                return self._validate_json(response_text)
                        return response_text

                logger.warning(
                    "Ollama basarisiz oldu: %s. Fallback mekanizmasi kontrol ediliyor...",
                    str(ollama_error),
                )

                if not self.use_fallback:
                    logger.error("Ollama coktu ve OpenAI fallback key'i bulunamadi.")
                    raise LLMServiceError(
                        "Yerel LLM servisine ulasilamiyor ve yedek sistem tanimli degil. "
                        f"Detay: {str(ollama_error)}"
                    ) from ollama_error

                try:
                    logger.info("OpenAI fallback devrede.")
                    with profile_stage("llm.generate.openai_fallback"):
                        response_text = await self.openai.generate(
                            prompt=prompt,
                            system=system,
                            json_mode=json_mode,
                        )
                except OpenAIClientError as openai_error:
                    logger.error("OpenAI fallback de basarisiz oldu: %s", str(openai_error))
                    raise LLMServiceError(
                        "Tum LLM servisleri erisilemez durumda. "
                        f"Ollama: {str(ollama_error)} | OpenAI: {str(openai_error)}"
                    ) from openai_error

            if json_mode:
                with profile_stage("llm.generate.validate_json"):
                    return self._validate_json(response_text)

            return response_text

    async def generate_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        *,
        model: str | None = None,
        model_role: str = "default",
        llm_profile: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Streaming formatinda yanit uretir."""
        self._check_token_limit(prompt, system)
        resolved_model = self._resolve_ollama_model(
            model=model,
            model_role=model_role,
            llm_profile=llm_profile,
        )

        try:
            async for chunk in self.ollama.generate_stream(prompt, system, model=resolved_model):
                yield chunk
        except OllamaClientError as ollama_error:
            primary_model = settings.ollama.model
            if (
                resolved_model != primary_model
                and self._looks_like_missing_model_error(ollama_error)
            ):
                logger.warning(
                    "Istenen Ollama stream modeli kullanilamadi (%s). Birincil modele dusuluyor: %s",
                    resolved_model,
                    primary_model,
                )
                try:
                    async for chunk in self.ollama.generate_stream(prompt, system, model=primary_model):
                        yield chunk
                    return
                except OllamaClientError as primary_error:
                    ollama_error = primary_error

            logger.warning("Ollama stream hata verdi: %s. Fallback stream araniyor...", str(ollama_error))

            if not self.use_fallback:
                raise LLMServiceError(
                    f"Stream: Yerel LLM koptu ve yedek sistem bulunamadi. Detay: {str(ollama_error)}"
                ) from ollama_error

            try:
                logger.info("OpenAI fallback stream baslatiliyor...")
                async for chunk in self.openai.generate_stream(prompt, system):
                    yield chunk
            except OpenAIClientError as openai_error:
                raise LLMServiceError(
                    "Stream: Tum LLM servisleri coktu. "
                    f"Ollama: {str(ollama_error)} | OpenAI: {str(openai_error)}"
                ) from openai_error
