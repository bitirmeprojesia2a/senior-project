import json
import pytest
from unittest.mock import AsyncMock, patch
from src.llm.llm_service import LLMService, LLMServiceError
from src.llm.ollama_client import OllamaClientError
from src.llm.openai_client import OpenAIClientError

@pytest.fixture
def mock_settings():
    with patch("src.llm.ollama_client.settings") as mock_ollama_settings, \
         patch("src.llm.openai_client.settings") as mock_openai_settings:
        mock_ollama_settings.ollama.host = "http://localhost:11434"
        mock_ollama_settings.ollama.model = "qwen2.5:7b"
        mock_ollama_settings.ollama.timeout = 30
        
        mock_openai_settings.openai.api_key = "test-key"
        mock_openai_settings.openai.model = "gpt-4o-mini"
        yield

@pytest.fixture
def llm_service(mock_settings, monkeypatch):
    """Fixture to provide a configured LLMService."""
    # LLMService __init__ calls OpenAIClient.is_available which uses settings
    service = LLMService()
    # Mock fallback to be available
    service.use_fallback = True
    return service

@pytest.mark.asyncio
async def test_llm_generate_success_ollama(llm_service):
    """Test standard response generation via Ollama (No Fallback needed)."""
    with patch.object(llm_service.ollama, 'generate', new_callable=AsyncMock) as mock_ollama:
        mock_ollama.return_value = "Merhaba Dünya!"
        
        response = await llm_service.generate("Selam", system="Sen asistansın.")
        
        mock_ollama.assert_called_once_with(prompt="Selam", system="Sen asistansın.", json_mode=False)
        assert response == "Merhaba Dünya!"

@pytest.mark.asyncio
async def test_llm_generate_json_mode(llm_service):
    """Test generating and parsing proper JSON formatting."""
    with patch.object(llm_service.ollama, 'generate', new_callable=AsyncMock) as mock_ollama:
        expected_json = '{"departments": ["finance"], "confidence": 0.9}'
        mock_ollama.return_value = expected_json
        
        response = await llm_service.generate("Harç ödememi yapamıyorum", json_mode=True)
        
        mock_ollama.assert_called_once()
        assert "finance" in json.loads(response)["departments"]

@pytest.mark.asyncio
async def test_llm_generate_json_mode_invalid(llm_service):
    """Test generation throws LLMServiceError if JSON is requested but model outputs invalid JSON."""
    with patch.object(llm_service.ollama, 'generate', new_callable=AsyncMock) as mock_ollama:
        mock_ollama.return_value = "Üzgünüm ama sorunuzu anlayamadım."
        
        with pytest.raises(LLMServiceError, match="Geçersiz JSON formatı"):
            await llm_service.generate("Harç", json_mode=True)

@pytest.mark.asyncio
async def test_llm_fallback_to_openai(llm_service):
    """Test fallback mechanism: if Ollama fails, it should use OpenAI."""
    with patch.object(llm_service.ollama, 'generate', new_callable=AsyncMock) as mock_ollama, \
         patch.object(llm_service.openai, 'generate', new_callable=AsyncMock) as mock_openai:
        
        # Make Ollama raise an error
        mock_ollama.side_effect = OllamaClientError("Ollama timeout")
        mock_openai.return_value = "OpenAI'dan selam."
        
        response = await llm_service.generate("Test prompt")
        
        # Tenacity will retry Ollama 3 times, let's just make sure OpenAI is called
        mock_openai.assert_called_once_with(prompt="Test prompt", system=None, json_mode=False)
        assert response == "OpenAI'dan selam."

@pytest.mark.asyncio
async def test_llm_total_failure(llm_service):
    """Test handling when both Ollama and OpenAI fail."""
    with patch.object(llm_service.ollama, 'generate', new_callable=AsyncMock) as mock_ollama, \
         patch.object(llm_service.openai, 'generate', new_callable=AsyncMock) as mock_openai:
        
        mock_ollama.side_effect = OllamaClientError("Ollama failed")
        mock_openai.side_effect = OpenAIClientError("OpenAI API limit exceeded")
        
        with pytest.raises(LLMServiceError, match="Tüm LLM servisleri erişilemez durumda"):
            await llm_service.generate("Bana yardım et")

@pytest.mark.asyncio
async def test_llm_health_check_healthy(llm_service):
    """Test health status aggregation."""
    with patch.object(llm_service.ollama, 'get_health', new_callable=AsyncMock) as mock_ollama_health, \
         patch.object(llm_service.openai, 'get_health', new_callable=AsyncMock) as mock_openai_health:
             
        mock_ollama_health.return_value = {
            "status": "healthy",
            "model_found": True,
            "available_models": ["qwen2.5:7b"]
        }
        
        mock_openai_health.return_value = {
            "status": "healthy",
            "model_found": True
        }
        
        health = await llm_service.get_health()
        assert health["status"] == "healthy"
        assert health["primary"]["status"] == "healthy"
        assert health["fallback"]["status"] == "healthy"

@pytest.mark.asyncio
async def test_ollama_retry_logic(llm_service):
    """Verify tenacity retries 3 times on Ollama before raising/fallback."""
    with patch.object(llm_service.ollama, 'generate', new_callable=AsyncMock) as mock_ollama:
        mock_ollama.side_effect = OllamaClientError("Temporary error")
        llm_service.use_fallback = False  # Disable fallback to check if it raises
        
        # Test needs to run fast, so we mock wait_exponential using tenacity monkeypatch if needed
        # Alternatively, tenacity retry is tested by default here based on wait times.
        # However wait_exponential takes min=2 max=10, which leads to ~6s test.
        with patch("src.llm.llm_service.LLMService._generate_ollama_with_retry.retry.wait", return_value=0):
            with pytest.raises(LLMServiceError, match="Yerel LLM servisine ulaşılamıyor"):
                await llm_service.generate("Retry test")
                
        # Tenacity attempt counting. 1 initial + 2 retries = 3 calls
        assert mock_ollama.call_count == 3
