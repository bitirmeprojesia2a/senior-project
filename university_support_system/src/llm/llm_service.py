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

from src.core.config import LLMProvider, settings
from src.core.profiling import get_current_profiler, profile_stage
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
        self.google_ai = OpenAIClient(
            settings.google_ai,
            api_key_env_name="GOOGLE_AI_API_KEY",
        )
        self.primary_provider = settings.llm.primary_provider
        self.fallback_provider = settings.llm.fallback_provider

    def _openai_client_for_provider(self, provider: str) -> OpenAIClient:
        """Return the OpenAI-compatible client backing a provider."""
        if provider == "openai_compatible":
            return self.openai
        if provider == "google_ai":
            return self.google_ai
        raise LLMServiceError(f"Provider OpenAI-compatible degil: {provider}")

    def _is_provider_available(self, provider: str) -> bool:
        """Return whether a configured provider can be used."""
        if provider == "ollama":
            return True
        if provider in {"openai_compatible", "google_ai"}:
            return self._openai_client_for_provider(provider).is_available
        return False

    def _has_fallback(self) -> bool:
        """Return whether a distinct, usable fallback provider exists."""
        if self.fallback_provider in {"", "none"}:
            return False
        if self.fallback_provider == self.primary_provider:
            return False
        return self._is_provider_available(self.fallback_provider)

    def _provider_display_name(self, provider: str) -> str:
        """Render a human-friendly provider label for logs/errors."""
        if provider == "ollama":
            return "Ollama"
        if provider == "openai_compatible":
            return self.openai.provider_name or "OpenAI-compatible"
        if provider == "google_ai":
            return self.google_ai.provider_name or "Google AI"
        return provider

    @staticmethod
    def _is_provider_exception(provider: str, exc: BaseException) -> bool:
        """Return whether exception belongs to the selected provider type."""
        if provider == "ollama":
            return isinstance(exc, OllamaClientError)
        if provider in {"openai_compatible", "google_ai"}:
            return isinstance(exc, OpenAIClientError)
        return False

    def _provider_usage_label(self, provider: str) -> str:
        """Return a stable provider label for profiler/debug output."""
        if provider == "openai_compatible":
            return self.openai.provider_name or "openai_compatible"
        if provider == "google_ai":
            return self.google_ai.provider_name or "google_ai"
        return provider

    def _record_llm_usage(
        self,
        *,
        kind: str,
        model_role: str,
        provider: str,
        model: str,
        path: str,
        status: str,
        json_mode: bool = False,
        llm_profile: str | None = None,
        fallback_from: str | None = None,
        fallback_from_model: str | None = None,
        error: BaseException | None = None,
    ) -> None:
        """Attach provider/model usage metadata to the active query profiler."""
        profiler = get_current_profiler()
        if profiler is None:
            return

        entry: dict[str, Any] = {
            "kind": kind,
            "model_role": model_role,
            "provider": provider,
            "provider_label": self._provider_usage_label(provider),
            "display_name": self._provider_display_name(provider),
            "model": model,
            "path": path,
            "status": status,
            "json_mode": json_mode,
        }
        if llm_profile:
            entry["llm_profile"] = settings.normalize_llm_profile(llm_profile)
        if fallback_from:
            entry["fallback_from"] = fallback_from
            entry["fallback_from_label"] = self._provider_usage_label(fallback_from)
        if fallback_from_model:
            entry["fallback_from_model"] = fallback_from_model
        if error is not None:
            entry["error_type"] = type(error).__name__
            entry["error_message"] = str(error)

        profiler.append_attribute_list("llm_usage", entry)

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
        provider: LLMProvider,
        *,
        model: str | None = None,
        model_role: str = "default",
        llm_profile: str | None = None,
    ) -> str:
        """Resolve model name for a specific provider."""
        if model:
            return model
        if provider in {"openai_compatible", "google_ai"}:
            return settings.resolve_llm_model(
                role=model_role,
                profile=llm_profile,
                provider=provider,
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
        provider: str = "openai_compatible",
    ) -> str:
        """OpenAI-compatible provider uzerinden retry mantigi ile uretim yapar."""
        client = self._openai_client_for_provider(provider)
        return await client.generate(
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
        if provider in {"openai_compatible", "google_ai"}:
            return await self._generate_openai_with_retry(
                prompt=prompt,
                system=system,
                json_mode=json_mode,
                model=model,
                provider=provider,
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
        if provider in {"openai_compatible", "google_ai"}:
            client = self._openai_client_for_provider(provider)
            async for chunk in client.generate_stream(prompt, system, model=model):
                yield chunk
            return
        raise LLMServiceError(f"Desteklenmeyen LLM provider: {provider}")

    async def get_health(self) -> Dict[str, Any]:
        """Sistemin provider bazli saglik durumunu kontrol eder."""
        def _provider_model_map(provider: str) -> Dict[str, Any]:
            return {
                "provider": provider,
                "profile": settings.normalize_llm_profile(settings.llm.profile),
                "primary": settings._resolve_provider_primary_model(provider),
                "secondary": settings._resolve_provider_secondary_model(provider),
                "routing": settings.resolve_llm_model(role="routing", provider=provider),
                "conversation": settings.resolve_llm_model(role="conversation", provider=provider),
                "query_expansion": settings.resolve_llm_model(
                    role="query_expansion",
                    provider=provider,
                ),
                "specialist_synthesis": settings.resolve_llm_model(
                    role="specialist_synthesis",
                    provider=provider,
                ),
                "global_synthesis": settings.resolve_llm_model(
                    role="global_synthesis",
                    provider=provider,
                ),
            }

        def _requested_models(model_map: Dict[str, Any]) -> list[str]:
            keys = (
                "primary",
                "secondary",
                "routing",
                "conversation",
                "query_expansion",
                "specialist_synthesis",
                "global_synthesis",
            )
            return list(dict.fromkeys(str(model_map[key]) for key in keys if model_map.get(key)))

        provider_model_maps: Dict[str, Dict[str, Any]] = {
            "ollama": _provider_model_map("ollama"),
            "openai_compatible": _provider_model_map("openai_compatible"),
            "google_ai": _provider_model_map("google_ai"),
        }
        needed_providers = {
            provider
            for provider in {self.primary_provider, self.fallback_provider}
            if provider and provider != "none"
        }

        provider_healths: Dict[str, Dict[str, Any] | None] = {
            "ollama": None,
            "openai_compatible": None,
            "google_ai": None,
        }

        if "ollama" in needed_providers:
            provider_healths["ollama"] = await self.ollama.get_health(
                models=_requested_models(provider_model_maps["ollama"])
            )
        for provider in ("openai_compatible", "google_ai"):
            if provider in needed_providers:
                client = self._openai_client_for_provider(provider)
                provider_healths[provider] = await client.get_health(
                    models=_requested_models(provider_model_maps[provider])
                )

        def _provider_health_payload(provider: str) -> Dict[str, Any]:
            if provider == "ollama":
                payload = provider_healths["ollama"] or {
                    "status": "unhealthy",
                    "reason": "NOT_CHECKED",
                    "model_found": False,
                }
                return {
                    "name": "ollama",
                    "status": payload.get("status", "unhealthy"),
                    "model_loaded": payload.get("model_found", False),
                    "configured_models": payload.get("configured_models", provider_model_maps["ollama"]),
                    "available_models": payload.get("available_models", []),
                    "configured_models_found": payload.get("configured_models_found", {}),
                }

            client = self._openai_client_for_provider(provider)
            payload = provider_healths.get(provider) or {
                "status": "unhealthy",
                "reason": "NOT_CHECKED",
                "model_found": False,
                "provider": client.provider_name,
            }
            return {
                "name": payload.get("provider", client.provider_name),
                "status": payload.get("status", "unhealthy"),
                "model_loaded": payload.get("model_found", False),
                "configured_models": payload.get("configured_models", provider_model_maps[provider]),
                "available_models": payload.get("available_models", []),
                "configured_models_found": payload.get("configured_models_found", {}),
                "base_url": payload.get("base_url", client.base_url),
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
                self._record_llm_usage(
                    kind="generate",
                    model_role=model_role,
                    provider=primary_provider,
                    model=resolved_model,
                    path="primary",
                    status="success",
                    json_mode=json_mode,
                    llm_profile=llm_profile,
                )
            except Exception as primary_error:
                if not self._is_provider_exception(primary_provider, primary_error):
                    raise

                self._record_llm_usage(
                    kind="generate",
                    model_role=model_role,
                    provider=primary_provider,
                    model=resolved_model,
                    path="primary",
                    status="error",
                    json_mode=json_mode,
                    llm_profile=llm_profile,
                    error=primary_error,
                )

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
                        self._record_llm_usage(
                            kind="generate",
                            model_role=model_role,
                            provider=primary_provider,
                            model=primary_model,
                            path="primary_model_fallback",
                            status="success",
                            json_mode=json_mode,
                            llm_profile=llm_profile,
                            fallback_from_model=resolved_model,
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
                    with profile_stage(
                        f"llm.generate.{fallback_provider}_fallback",
                        model=fallback_model,
                        role=model_role,
                    ):
                        response_text = await self._generate_with_provider(
                            provider=fallback_provider,
                            prompt=prompt,
                            system=system,
                            json_mode=json_mode,
                            model=fallback_model,
                        )
                    self._record_llm_usage(
                        kind="generate",
                        model_role=model_role,
                        provider=fallback_provider,
                        model=fallback_model,
                        path="fallback",
                        status="success",
                        json_mode=json_mode,
                        llm_profile=llm_profile,
                        fallback_from=primary_provider,
                        fallback_from_model=resolved_model,
                    )
                except Exception as fallback_error:
                    if not self._is_provider_exception(self.fallback_provider, fallback_error):
                        raise
                    self._record_llm_usage(
                        kind="generate",
                        model_role=model_role,
                        provider=self.fallback_provider,
                        model=fallback_model,
                        path="fallback",
                        status="error",
                        json_mode=json_mode,
                        llm_profile=llm_profile,
                        fallback_from=primary_provider,
                        fallback_from_model=resolved_model,
                        error=fallback_error,
                    )
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
            self._record_llm_usage(
                kind="stream",
                model_role=model_role,
                provider=primary_provider,
                model=resolved_model,
                path="primary",
                status="success",
                llm_profile=llm_profile,
            )
        except Exception as primary_error:
            if not self._is_provider_exception(primary_provider, primary_error):
                raise

            self._record_llm_usage(
                kind="stream",
                model_role=model_role,
                provider=primary_provider,
                model=resolved_model,
                path="primary",
                status="error",
                llm_profile=llm_profile,
                error=primary_error,
            )

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
                    self._record_llm_usage(
                        kind="stream",
                        model_role=model_role,
                        provider=primary_provider,
                        model=primary_model,
                        path="primary_model_fallback",
                        status="success",
                        llm_profile=llm_profile,
                        fallback_from_model=resolved_model,
                    )
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
                self._record_llm_usage(
                    kind="stream",
                    model_role=model_role,
                    provider=fallback_provider,
                    model=fallback_model,
                    path="fallback",
                    status="success",
                    llm_profile=llm_profile,
                    fallback_from=primary_provider,
                    fallback_from_model=resolved_model,
                )
            except Exception as fallback_error:
                if not self._is_provider_exception(self.fallback_provider, fallback_error):
                    raise
                self._record_llm_usage(
                    kind="stream",
                    model_role=model_role,
                    provider=self.fallback_provider,
                    model=fallback_model,
                    path="fallback",
                    status="error",
                    llm_profile=llm_profile,
                    fallback_from=primary_provider,
                    fallback_from_model=resolved_model,
                    error=fallback_error,
                )
                raise LLMServiceError(
                    "Stream: Tum LLM servisleri coktu. "
                    f"{self._provider_display_name(primary_provider)}: {str(primary_error)} | "
                    f"{self._provider_display_name(self.fallback_provider)}: {str(fallback_error)}"
                ) from fallback_error
