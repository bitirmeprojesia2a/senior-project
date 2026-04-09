"""
LLM cekirdek servisi.

Ollama ve OpenAI-compatible provider'lari primary/fallback olarak koordine eder.
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


def _should_retry_openai_error(exc: BaseException) -> bool:
    return isinstance(exc, OpenAIClientError) and bool(getattr(exc, "retryable", False))


class LLMServiceError(Exception):
    """LLM servisinden yanit alinamadi."""


class LLMService:
    """Ollama ve OpenAI-compatible provider'lari koordine eden ana LLM servisi."""

    def __init__(self):
        self.ollama = OllamaClient()
        self.openai = OpenAIClient()
        self.primary_provider = settings.llm.primary_provider
        self.fallback_provider = settings.llm.fallback_provider

    def _is_provider_available(self, provider: str) -> bool:
        """Return whether a configured provider can be used."""
        if provider == "ollama":
            return True
        if provider == "openai_compatible":
            return self.openai.is_available
        return False

    def _has_fallback(self) -> bool:
        """Return whether a distinct, usable fallback provider exists."""
        if self.fallback_provider in {"", "none"}:
            return False
        if self.fallback_provider == self.primary_provider:
            return False
        return self._is_provider_available(self.fallback_provider)

    @staticmethod
    def _provider_display_name(provider: str) -> str:
        """Render a human-friendly provider label for logs/errors."""
        if provider == "ollama":
            return "Ollama"
        if provider == "openai_compatible":
            return "OpenAI-compatible"
        return provider

    @staticmethod
    def _is_provider_exception(provider: str, exc: BaseException) -> bool:
        """Return whether exception belongs to the selected provider type."""
        if provider == "ollama":
            return isinstance(exc, OllamaClientError)
        if provider == "openai_compatible":
            return isinstance(exc, OpenAIClientError)
        return False

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

    def _resolve_provider_model(
        self,
        provider: str,
        *,
        model: str | None = None,
        model_role: str = "default",
        llm_profile: str | None = None,
    ) -> str:
        """Resolve model name for a specific provider."""
        if model:
            return model
        if provider == "openai_compatible":
            return settings.resolve_llm_model(
                role=model_role,
                profile=llm_profile,
                provider="openai_compatible",
            )
        return self._resolve_ollama_model(
            model=model,
            model_role=model_role,
            llm_profile=llm_profile,
        )

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

    @retry(
        retry=retry_if_exception(_should_retry_openai_error),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _generate_openai_with_retry(
        self,
        prompt: str,
        system: Optional[str] = None,
        json_mode: bool = False,
        *,
        model: str | None = None,
    ) -> str:
        """OpenAI-compatible provider uzerinden retry mantigi ile uretim yapar."""
        return await self.openai.generate(
            prompt=prompt,
            system=system,
            json_mode=json_mode,
            model=model,
        )

    async def _generate_with_provider(
        self,
        *,
        provider: str,
        prompt: str,
        system: Optional[str] = None,
        json_mode: bool = False,
        model: str,
    ) -> str:
        """Dispatch generate calls to the configured provider."""
        if provider == "ollama":
            return await self._generate_ollama_with_retry(
                prompt=prompt,
                system=system,
                json_mode=json_mode,
                model=model,
            )
        if provider == "openai_compatible":
            return await self._generate_openai_with_retry(
                prompt=prompt,
                system=system,
                json_mode=json_mode,
                model=model,
            )
        raise LLMServiceError(f"Desteklenmeyen LLM provider: {provider}")

    async def _generate_stream_with_provider(
        self,
        *,
        provider: str,
        prompt: str,
        system: Optional[str] = None,
        model: str,
    ) -> AsyncGenerator[str, None]:
        """Dispatch streaming calls to the configured provider."""
        if provider == "ollama":
            async for chunk in self.ollama.generate_stream(prompt, system, model=model):
                yield chunk
            return
        if provider == "openai_compatible":
            async for chunk in self.openai.generate_stream(prompt, system, model=model):
                yield chunk
            return
        raise LLMServiceError(f"Desteklenmeyen LLM provider: {provider}")

    async def get_health(self) -> Dict[str, Any]:
        """Sistemin provider bazli saglik durumunu kontrol eder."""
        model_map = settings.configured_llm_models()
        ollama_needed = "ollama" in {self.primary_provider, self.fallback_provider}
        openai_needed = "openai_compatible" in {self.primary_provider, self.fallback_provider}

        ollama_health: Dict[str, Any] | None = None
        openai_health: Dict[str, Any] | None = None

        if ollama_needed:
            ollama_model_map = {
                "primary": settings._resolve_provider_primary_model("ollama"),
                "secondary": settings._resolve_provider_secondary_model("ollama"),
                "routing": settings.resolve_llm_model(role="routing", provider="ollama"),
                "conversation": settings.resolve_llm_model(role="conversation", provider="ollama"),
                "specialist_synthesis": settings.resolve_llm_model(role="specialist_synthesis", provider="ollama"),
                "global_synthesis": settings.resolve_llm_model(role="global_synthesis", provider="ollama"),
            }
            ollama_health = await self.ollama.get_health(
                models=[
                    ollama_model_map["primary"],
                    ollama_model_map["secondary"],
                    ollama_model_map["routing"],
                    ollama_model_map["conversation"],
                    ollama_model_map["specialist_synthesis"],
                    ollama_model_map["global_synthesis"],
                ]
            )
        if openai_needed:
            openai_health = await self.openai.get_health()

        def _provider_health_payload(provider: str) -> Dict[str, Any]:
            if provider == "ollama":
                payload = ollama_health or {
                    "status": "unhealthy",
                    "reason": "NOT_CHECKED",
                    "model_found": False,
                }
                return {
                    "name": "ollama",
                    "status": payload.get("status", "unhealthy"),
                    "model_loaded": payload.get("model_found", False),
                    "configured_models": model_map,
                    "available_models": payload.get("available_models", []),
                    "configured_models_found": payload.get("configured_models_found", {}),
                }

            payload = openai_health or {
                "status": "unhealthy",
                "reason": "NOT_CHECKED",
                "model_found": False,
                "provider": self.openai.provider_name,
            }
            return {
                "name": payload.get("provider", self.openai.provider_name),
                "status": payload.get("status", "unhealthy"),
                "model_loaded": payload.get("model_found", False),
                "configured_models": model_map,
                "base_url": payload.get("base_url", self.openai.base_url),
            }

        primary_health = _provider_health_payload(self.primary_provider)
        fallback_available = self._has_fallback()
        fallback_health = (
            _provider_health_payload(self.fallback_provider)
            if fallback_available
            else {
                "name": self.fallback_provider,
                "available": False,
                "status": "disabled" if self.fallback_provider == "none" else "unavailable",
            }
        )

        overall_status = "healthy"
        if primary_health.get("status") != "healthy":
            overall_status = "degraded" if fallback_available and fallback_health.get("status") == "healthy" else "unhealthy"

        return {
            "status": overall_status,
            "primary": primary_health,
            "fallback": fallback_health,
        }

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

        Primary provider ile dener, basarisiz olursa uygun fallback provider'a gecer.
        """
        with profile_stage("llm.generate", json_mode=json_mode):
            self._check_token_limit(prompt, system)
            primary_provider = self.primary_provider
            resolved_model = self._resolve_provider_model(
                primary_provider,
                model=model,
                model_role=model_role,
                llm_profile=llm_profile,
            )

            try:
                logger.debug(
                    "Uretim icin primary provider kullaniliyor. provider=%s model=%s role=%s",
                    primary_provider,
                    resolved_model,
                    model_role,
                )
                with profile_stage(f"llm.generate.{primary_provider}", model=resolved_model, role=model_role):
                    response_text = await self._generate_with_provider(
                        provider=primary_provider,
                        prompt=prompt,
                        system=system,
                        json_mode=json_mode,
                        model=resolved_model,
                    )
            except Exception as primary_error:
                if not self._is_provider_exception(primary_provider, primary_error):
                    raise

                if primary_provider == "ollama":
                    ollama_error = primary_error
                else:
                    ollama_error = None

                primary_model = settings.ollama.model
                if (
                    primary_provider == "ollama"
                    and ollama_error is not None
                    and resolved_model != primary_model
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
                    "%s basarisiz oldu: %s. Fallback mekanizmasi kontrol ediliyor...",
                    self._provider_display_name(primary_provider),
                    str(primary_error),
                )

                if not self._has_fallback():
                    logger.error(
                        "%s basarisiz oldu ve kullanilabilir fallback provider bulunamadi.",
                        self._provider_display_name(primary_provider),
                    )
                    raise LLMServiceError(
                        f"{self._provider_display_name(primary_provider)} erisilemez durumda ve yedek sistem tanimli degil. "
                        f"Detay: {str(primary_error)}"
                    ) from primary_error

                try:
                    fallback_provider = self.fallback_provider
                    fallback_model = self._resolve_provider_model(
                        fallback_provider,
                        model=model if fallback_provider == primary_provider else None,
                        model_role=model_role,
                        llm_profile=llm_profile,
                    )
                    logger.info("Fallback provider devrede. provider=%s model=%s", fallback_provider, fallback_model)
                    with profile_stage(f"llm.generate.{fallback_provider}_fallback"):
                        response_text = await self._generate_with_provider(
                            provider=fallback_provider,
                            prompt=prompt,
                            system=system,
                            json_mode=json_mode,
                            model=fallback_model,
                        )
                except Exception as fallback_error:
                    if not self._is_provider_exception(self.fallback_provider, fallback_error):
                        raise
                    logger.error(
                        "Fallback provider de basarisiz oldu. provider=%s error=%s",
                        self.fallback_provider,
                        str(fallback_error),
                    )
                    raise LLMServiceError(
                        "Tum LLM servisleri erisilemez durumda. "
                        f"{self._provider_display_name(primary_provider)}: {str(primary_error)} | "
                        f"{self._provider_display_name(self.fallback_provider)}: {str(fallback_error)}"
                    ) from fallback_error

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
        primary_provider = self.primary_provider
        resolved_model = self._resolve_provider_model(
            primary_provider,
            model=model,
            model_role=model_role,
            llm_profile=llm_profile,
        )

        try:
            async for chunk in self._generate_stream_with_provider(
                provider=primary_provider,
                prompt=prompt,
                system=system,
                model=resolved_model,
            ):
                yield chunk
        except Exception as primary_error:
            if not self._is_provider_exception(primary_provider, primary_error):
                raise

            if primary_provider == "ollama":
                ollama_error = primary_error
            else:
                ollama_error = None

            primary_model = settings.ollama.model
            if (
                primary_provider == "ollama"
                and ollama_error is not None
                and resolved_model != primary_model
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

            logger.warning(
                "%s stream hata verdi: %s. Fallback stream araniyor...",
                self._provider_display_name(primary_provider),
                str(primary_error),
            )

            if not self._has_fallback():
                raise LLMServiceError(
                    f"Stream: {self._provider_display_name(primary_provider)} koptu ve yedek sistem bulunamadi. "
                    f"Detay: {str(primary_error)}"
                ) from primary_error

            try:
                fallback_provider = self.fallback_provider
                fallback_model = self._resolve_provider_model(
                    fallback_provider,
                    model=model if fallback_provider == primary_provider else None,
                    model_role=model_role,
                    llm_profile=llm_profile,
                )
                logger.info("Fallback stream baslatiliyor. provider=%s model=%s", fallback_provider, fallback_model)
                async for chunk in self._generate_stream_with_provider(
                    provider=fallback_provider,
                    prompt=prompt,
                    system=system,
                    model=fallback_model,
                ):
                    yield chunk
            except Exception as fallback_error:
                if not self._is_provider_exception(self.fallback_provider, fallback_error):
                    raise
                raise LLMServiceError(
                    "Stream: Tum LLM servisleri coktu. "
                    f"{self._provider_display_name(primary_provider)}: {str(primary_error)} | "
                    f"{self._provider_display_name(self.fallback_provider)}: {str(fallback_error)}"
                ) from fallback_error
