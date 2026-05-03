import json
from unittest.mock import AsyncMock, patch

import pytest

from src.core.config import settings
from src.core.profiling import QueryProfiler, activate_profiler
from src.llm.llm_service import LLMService, LLMServiceError
from src.llm.ollama_client import OllamaClientError
from src.llm.openai_client import OpenAIClientError


@pytest.fixture
def mock_settings():
    with patch("src.llm.ollama_client.settings") as mock_ollama_settings, patch(
        "src.llm.openai_client.settings"
    ) as mock_openai_settings:
        mock_ollama_settings.ollama.host = "http://localhost:11434"
        mock_ollama_settings.ollama.model = "qwen2.5:7b"
        mock_ollama_settings.ollama.timeout = 30

        mock_openai_settings.openai.api_key = "test-key"
        mock_openai_settings.openai.model = "gpt-4o-mini"
        mock_openai_settings.openai.provider_name = "openai_compatible"
        yield


@pytest.fixture
def llm_service(mock_settings):
    service = LLMService()
    service.primary_provider = "ollama"
    service.fallback_provider = "openai_compatible"
    return service


@pytest.mark.asyncio
async def test_llm_generate_success_ollama(llm_service):
    with patch.object(llm_service.ollama, "generate", new_callable=AsyncMock) as mock_ollama:
        mock_ollama.return_value = "Merhaba Dunya!"

        response = await llm_service.generate("Selam", system="Sen asistansin.")

        mock_ollama.assert_called_once()
        assert mock_ollama.await_args.kwargs["prompt"] == "Selam"
        assert mock_ollama.await_args.kwargs["system"] == "Sen asistansin."
        assert mock_ollama.await_args.kwargs["json_mode"] is False
        assert mock_ollama.await_args.kwargs["model"]
        assert response == "Merhaba Dunya!"


@pytest.mark.asyncio
async def test_llm_generate_json_mode(llm_service):
    with patch.object(llm_service.ollama, "generate", new_callable=AsyncMock) as mock_ollama:
        expected_json = '{"departments": ["finance"], "confidence": 0.9}'
        mock_ollama.return_value = expected_json

        response = await llm_service.generate("Harc odememi yapamiyorum", json_mode=True)

        mock_ollama.assert_called_once()
        assert "finance" in json.loads(response)["departments"]


@pytest.mark.asyncio
async def test_llm_generate_json_mode_invalid(llm_service):
    with patch.object(llm_service.ollama, "generate", new_callable=AsyncMock) as mock_ollama:
        mock_ollama.return_value = "Uzgunum ama sorunuzu anlayamadim."

        with pytest.raises(LLMServiceError, match="Gecersiz JSON formati"):
            await llm_service.generate("Harc", json_mode=True)


@pytest.mark.asyncio
async def test_llm_fallback_to_openai(llm_service):
    with patch.object(llm_service.ollama, "generate", new_callable=AsyncMock) as mock_ollama, patch.object(
        llm_service.openai, "generate", new_callable=AsyncMock
    ) as mock_openai:
        mock_ollama.side_effect = OllamaClientError("Ollama timeout")
        mock_openai.return_value = "OpenAI'dan selam."

        response = await llm_service.generate("Test prompt")

        mock_openai.assert_called_once_with(
            prompt="Test prompt",
            system=None,
            json_mode=False,
            model=settings.resolve_llm_model(provider="openai_compatible"),
        )
        assert response == "OpenAI'dan selam."


@pytest.mark.asyncio
async def test_llm_fallback_to_google_ai_from_openai_compatible(llm_service):
    llm_service.primary_provider = "openai_compatible"
    llm_service.fallback_provider = "google_ai"
    llm_service.google_ai._api_keys = ["google-test-key"]

    with patch.object(llm_service.openai, "generate", new_callable=AsyncMock) as mock_openai, patch.object(
        llm_service.google_ai, "generate", new_callable=AsyncMock
    ) as mock_google:
        mock_openai.side_effect = OpenAIClientError("Groq rate limit", retryable=True)
        mock_google.return_value = "Google AI fallback cevabi."

        response = await llm_service.generate("Test prompt")

        mock_google.assert_called_once_with(
            prompt="Test prompt",
            system=None,
            json_mode=False,
            model=settings.resolve_llm_model(provider="google_ai"),
        )
        assert response == "Google AI fallback cevabi."


@pytest.mark.asyncio
async def test_llm_generate_records_primary_provider_usage(llm_service):
    profiler = QueryProfiler(label="llm-primary")

    with patch.object(llm_service.ollama, "generate", new_callable=AsyncMock) as mock_ollama:
        mock_ollama.return_value = "Merhaba Dunya!"

        with activate_profiler(profiler):
            response = await llm_service.generate(
                "Selam",
                system="Sen asistansin.",
                model_role="routing",
                llm_profile="fast",
            )

    usage = profiler.get_attribute("llm_usage")
    assert response == "Merhaba Dunya!"
    assert isinstance(usage, list)
    assert usage == [
        {
            "kind": "generate",
            "model_role": "routing",
            "provider": "ollama",
            "provider_label": "ollama",
            "display_name": "Ollama",
            "model": settings.resolve_llm_model(role="routing", profile="fast"),
            "path": "primary",
            "status": "success",
            "json_mode": False,
            "llm_profile": "fast",
        }
    ]


@pytest.mark.asyncio
async def test_llm_generate_records_fallback_provider_usage(llm_service):
    llm_service.primary_provider = "openai_compatible"
    llm_service.fallback_provider = "google_ai"
    llm_service.google_ai._api_keys = ["google-test-key"]
    profiler = QueryProfiler(label="llm-fallback")

    with patch.object(llm_service.openai, "generate", new_callable=AsyncMock) as mock_openai, patch.object(
        llm_service.google_ai, "generate", new_callable=AsyncMock
    ) as mock_google:
        mock_openai.side_effect = OpenAIClientError("Groq rate limit", retryable=True)
        mock_google.return_value = "Google AI fallback cevabi."

        with activate_profiler(profiler):
            response = await llm_service.generate(
                "Test prompt",
                model_role="global_synthesis",
                llm_profile="quality",
            )

    usage = profiler.get_attribute("llm_usage")
    assert response == "Google AI fallback cevabi."
    assert isinstance(usage, list)
    assert len(usage) == 2
    assert usage[0]["provider"] == "openai_compatible"
    assert usage[0]["provider_label"] == llm_service.openai.provider_name
    assert usage[0]["status"] == "error"
    assert usage[0]["model_role"] == "global_synthesis"
    assert usage[0]["path"] == "primary"
    assert usage[0]["error_type"] == "OpenAIClientError"
    assert usage[1]["provider"] == "google_ai"
    assert usage[1]["provider_label"] == llm_service.google_ai.provider_name
    assert usage[1]["status"] == "success"
    assert usage[1]["path"] == "fallback"
    assert usage[1]["fallback_from"] == "openai_compatible"
    assert usage[1]["fallback_from_label"] == llm_service.openai.provider_name


@pytest.mark.asyncio
async def test_llm_total_failure(llm_service):
    with patch.object(llm_service.ollama, "generate", new_callable=AsyncMock) as mock_ollama, patch.object(
        llm_service.openai, "generate", new_callable=AsyncMock
    ) as mock_openai:
        mock_ollama.side_effect = OllamaClientError("Ollama failed")
        mock_openai.side_effect = OpenAIClientError("OpenAI API limit exceeded")

        with pytest.raises(LLMServiceError, match="erisilemez durumda"):
            await llm_service.generate("Bana yardim et")


@pytest.mark.asyncio
async def test_llm_health_check_healthy(llm_service):
    with patch.object(llm_service.ollama, "get_health", new_callable=AsyncMock) as mock_ollama_health, patch.object(
        llm_service.openai, "get_health", new_callable=AsyncMock
    ) as mock_openai_health:
        mock_ollama_health.return_value = {
            "status": "healthy",
            "model_found": True,
            "available_models": ["qwen2.5:7b"],
        }
        mock_openai_health.return_value = {
            "status": "healthy",
            "model_found": True,
            "available_models": ["gpt-4o-mini", "gpt-4o"],
            "configured_models_found": {"gpt-4o-mini": True},
        }

        health = await llm_service.get_health()
        assert health["status"] == "healthy"
        assert health["primary"]["status"] == "healthy"
        assert health["fallback"]["status"] == "healthy"
        assert mock_ollama_health.await_args.kwargs["models"]
        assert mock_openai_health.await_args.kwargs["models"]
        assert health["fallback"]["available_models"] == ["gpt-4o-mini", "gpt-4o"]


@pytest.mark.asyncio
async def test_ollama_retry_logic(llm_service):
    with patch.object(llm_service.ollama, "generate", new_callable=AsyncMock) as mock_ollama:
        mock_ollama.side_effect = OllamaClientError("Temporary error")
        llm_service.fallback_provider = "none"

        with patch("src.llm.llm_service.LLMService._generate_ollama_with_retry.retry.wait", return_value=0):
            with pytest.raises(LLMServiceError, match="Ollama erisilemez durumda"):
                await llm_service.generate("Retry test")

        assert mock_ollama.call_count == 3
