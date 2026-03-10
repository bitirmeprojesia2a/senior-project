import pytest
from unittest.mock import AsyncMock, patch
import httpx

from src.llm.ollama_client import OllamaClient, OllamaClientError

@pytest.fixture
def ollama_client():
    with patch("src.llm.ollama_client.settings") as mock_settings:
        mock_settings.ollama.host = "http://localhost:11434"
        mock_settings.ollama.model = "test-model"
        mock_settings.ollama.timeout = 5
        return OllamaClient()

class MockResponse:
    def __init__(self, json_data=None, text_data="", status_code=200):
        self._json_data = json_data
        self._text = text_data
        self.status_code = status_code

    def json(self):
        return self._json_data

    @property
    def text(self):
        return self._text

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "Error", request=AsyncMock(), response=self
            )

@pytest.mark.asyncio
async def test_get_health_healthy(ollama_client):
    mock_resp = MockResponse(json_data={"models": [{"name": "test-model"}]})
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        result = await ollama_client.get_health()
        assert result["status"] == "healthy"
        assert result["model_found"] is True

@pytest.mark.asyncio
async def test_get_health_model_missing(ollama_client):
    mock_resp = MockResponse(json_data={"models": [{"name": "other-model"}]})
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        result = await ollama_client.get_health()
        assert result["status"] == "model_missing"
        assert result["model_found"] is False

@pytest.mark.asyncio
async def test_get_health_unhealthy(ollama_client):
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.RequestError("Connection failed", request=AsyncMock())
        result = await ollama_client.get_health()
        assert result["status"] == "unhealthy"
        assert result["model_found"] is False

@pytest.mark.asyncio
async def test_generate_success(ollama_client):
    mock_resp = MockResponse(json_data={"response": "Generated text"})
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        result = await ollama_client.generate("Hello", system="Sys", json_mode=True)
        assert result == "Generated text"
        # Verify post arguments
        args, kwargs = mock_post.call_args
        payload = kwargs["json"]
        assert payload["prompt"] == "Hello"
        assert payload["system"] == "Sys"
        assert payload["format"] == "json"

@pytest.mark.asyncio
async def test_generate_timeout(ollama_client):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.TimeoutException("Timeout")
        with pytest.raises(OllamaClientError, match="Ollama yanıt süresi aşıldı"):
            await ollama_client.generate("Hello")

@pytest.mark.asyncio
async def test_generate_http_error(ollama_client):
    mock_resp = MockResponse(status_code=500, text_data="Internal Error")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.HTTPStatusError("500", request=AsyncMock(), response=mock_resp)
        with pytest.raises(OllamaClientError, match="Ollama HTTP hatası"):
            await ollama_client.generate("Hello")

@pytest.mark.asyncio
async def test_generate_request_error(ollama_client):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.RequestError("Network drop", request=AsyncMock())
        with pytest.raises(OllamaClientError, match="Ollama bağlantı hatası"):
            await ollama_client.generate("Hello")

# Since streaming uses context managers (async with client.stream), it is tricky to mock simply.
# We will mock the aiter_lines method.
@pytest.mark.asyncio
async def test_generate_stream_success(ollama_client):
    class MockStreamResponse:
        def __init__(self):
            self.status_code = 200
        def raise_for_status(self):
            pass
        async def aiter_lines(self):
            yield '{"response": "Hello"}'
            yield '{"response": " World"}'
            
    class MockStreamContext:
        async def __aenter__(self):
            return MockStreamResponse()
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch("httpx.AsyncClient.stream", return_value=MockStreamContext()):
        chunks = []
        async for chunk in ollama_client.generate_stream("Stream this"):
            chunks.append(chunk)
        assert chunks == ["Hello", " World"]

@pytest.mark.asyncio
async def test_generate_stream_error(ollama_client):
    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.side_effect = Exception("Stream failed")
        with pytest.raises(OllamaClientError, match="Şelale akışı"):
            async for _ in ollama_client.generate_stream("Stream this"):
                pass
