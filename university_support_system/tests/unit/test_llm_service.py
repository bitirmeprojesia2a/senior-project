import json
from unittest.mock import AsyncMock, patch

import pytest

from src.core.config import settings
from src.core.profiling import QueryProfiler, activate_profiler
from src.llm.llm_service import LLMService, LLMServiceError
from src.llm.openai_client import OpenAIClientError


@pytest.fixture
def mock_settings():
    with patch("src.llm.openai_client.settings") as mock_openai_settings:
        mock_openai_settings.openai.api_key = "test-key"
        mock_openai_settings.openai.model = "llama-3.3-70b-versatile"
        mock_openai_settings.openai.secondary_model = "llama-3.3-70b-versatile"
        mock_openai_settings.openai.provider_name = "groq"
        mock_openai_settings.openai.base_url = "https://api.groq.com/openai/v1"
        mock_openai_settings.openai.timeout = 30
        mock_openai_settings.openai.routing_model = None
        mock_openai_settings.openai.conversation_model = None
        mock_openai_settings.openai.query_expansion_model = None
        mock_openai_settings.openai.evidence_selection_model = None
        mock_openai_settings.openai.final_refinement_model = None
        mock_openai_settings.openai.specialist_synthesis_model = None
        mock_openai_settings.openai.global_synthesis_model = None
        mock_openai_settings.openai.reasoning_effort = None
        yield


@pytest.fixture
def llm_service(mock_settings):
    service = LLMService()
    service.primary_provider = "openai_compatible"
    service.fallback_provider = "google_ai"
    return service


@pytest.mark.asyncio
async def test_llm_generate_success_openai(llm_service):
    with patch.object(llm_service.openai, "generate", new_callable=AsyncMock) as mock_openai:
        mock_openai.return_value = "Merhaba Dunya!"

        response = await llm_service.generate("Selam", system="Sen asistansin.")

        mock_openai.assert_called_once()
        assert mock_openai.await_args.kwargs["prompt"] == "Selam"
        assert mock_openai.await_args.kwargs["system"] == "Sen asistansin."
        assert mock_openai.await_args.kwargs["json_mode"] is False
        assert mock_openai.await_args.kwargs["model"]
        assert response == "Merhaba Dunya!"


@pytest.mark.asyncio
async def test_llm_generate_json_mode(llm_service):
    with patch.object(llm_service.openai, "generate", new_callable=AsyncMock) as mock_openai:
        expected_json = '{"departments": ["finance"], "confidence": 0.9}'
        mock_openai.return_value = expected_json

        response = await llm_service.generate("Harc odememi yapamiyorum", json_mode=True)

        mock_openai.assert_called_once()
        assert "finance" in json.loads(response)["departments"]


@pytest.mark.asyncio
async def test_llm_generate_json_mode_invalid(llm_service):
    with patch.object(llm_service.openai, "generate", new_callable=AsyncMock) as mock_openai:
        mock_openai.return_value = "Uzgunum ama sorunuzu anlayamadim."

        with pytest.raises(LLMServiceError, match="Gecersiz JSON formati"):
            await llm_service.generate("Harc", json_mode=True)


@pytest.mark.asyncio
async def test_llm_fallback_to_google_ai(llm_service):
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

    with patch.object(llm_service.openai, "generate", new_callable=AsyncMock) as mock_openai:
        mock_openai.return_value = "Merhaba Dunya!"

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
            "provider": "openai_compatible",
            "provider_label": llm_service.openai.provider_name,
            "display_name": llm_service.openai.provider_name or "OpenAI-compatible",
            "model": settings.resolve_llm_model(role="routing", profile="fast"),
            "path": "primary",
            "status": "success",
            "json_mode": False,
            "llm_profile": "fast",
        }
    ]


@pytest.mark.asyncio
async def test_llm_generate_records_fallback_provider_usage(llm_service):
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
    llm_service.google_ai._api_keys = ["google-test-key"]

    with patch.object(llm_service.openai, "generate", new_callable=AsyncMock) as mock_openai, patch.object(
        llm_service.google_ai, "generate", new_callable=AsyncMock
    ) as mock_google:
        mock_openai.side_effect = OpenAIClientError("Groq rate limit", retryable=True)
        mock_google.side_effect = OpenAIClientError("Google AI failed")

        with pytest.raises(LLMServiceError, match="erisilemez durumda"):
            await llm_service.generate("Bana yardim et")


@pytest.mark.asyncio
async def test_llm_health_check_healthy(llm_service):
    llm_service.google_ai._api_keys = ["google-test-key"]

    with patch.object(llm_service.openai, "get_health", new_callable=AsyncMock) as mock_openai_health, patch.object(
        llm_service.google_ai, "get_health", new_callable=AsyncMock
    ) as mock_google_health:
        mock_openai_health.return_value = {
            "status": "healthy",
            "model_found": True,
            "available_models": ["llama-3.3-70b-versatile"],
            "configured_models_found": {"llama-3.3-70b-versatile": True},
            "provider": "groq",
            "base_url": "https://api.groq.com/openai/v1",
        }
        mock_google_health.return_value = {
            "status": "healthy",
            "model_found": True,
            "available_models": ["gemini-2.5-flash"],
            "configured_models_found": {"gemini-2.5-flash": True},
            "provider": "google_ai",
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        }

        health = await llm_service.get_health()
        assert health["status"] == "healthy"
        assert health["primary"]["status"] == "healthy"
        assert health["fallback"]["status"] == "healthy"
        assert mock_openai_health.await_args.kwargs["models"]
        assert mock_google_health.await_args.kwargs["models"]
