import pytest
from unittest.mock import AsyncMock, patch
import httpx

from src.llm.openai_client import OpenAIClient, OpenAIClientError

@pytest.fixture
def openai_client():
    with patch("src.llm.openai_client.settings") as mock_settings:
        mock_settings.openai.api_key = "test-sk"
        mock_settings.openai.model = "gpt-4o-mini"
        return OpenAIClient()

@pytest.fixture
def openai_client_no_key():
    with patch("src.llm.openai_client.settings") as mock_settings:
        mock_settings.openai.api_key = None
        mock_settings.openai.model = "gpt-4o-mini"
        return OpenAIClient()


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


def test_is_available(openai_client, openai_client_no_key):
    assert openai_client.is_available is True
    assert openai_client_no_key.is_available is False

def test_get_headers(openai_client, openai_client_no_key):
    headers = openai_client._get_headers()
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer test-sk"

    with pytest.raises(OpenAIClientError):
        openai_client_no_key._get_headers()

@pytest.mark.asyncio
async def test_get_health_healthy(openai_client):
    mock_resp = MockResponse()
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        result = await openai_client.get_health()
        assert result["status"] == "healthy"
        assert result["model_found"] is True

@pytest.mark.asyncio
async def test_get_health_unhealthy(openai_client):
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = Exception("Api down")
        result = await openai_client.get_health()
        assert result["status"] == "unhealthy"

@pytest.mark.asyncio
async def test_get_health_no_key(openai_client_no_key):
    result = await openai_client_no_key.get_health()
    assert result["status"] == "unhealthy"
    assert result["reason"] == "API_KEY_MISSING"

@pytest.mark.asyncio
async def test_generate_success(openai_client):
    mock_resp = MockResponse(json_data={"choices": [{"message": {"content": "OpenAI says hi"}}]})
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        result = await openai_client.generate("Hello", system="Sys", json_mode=True)
        assert result == "OpenAI says hi"
        
        args, kwargs = mock_post.call_args
        payload = kwargs["json"]
        assert payload["response_format"] == {"type": "json_object"}
        assert len(payload["messages"]) == 2

@pytest.mark.asyncio
async def test_generate_timeout(openai_client):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.TimeoutException("Timeout")
        with pytest.raises(OpenAIClientError, match="OpenAI yanıt süresi aşıldı"):
            await openai_client.generate("Hello")

@pytest.mark.asyncio
async def test_generate_http_error(openai_client):
    mock_resp = MockResponse(status_code=401, text_data="Unauthorized")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.HTTPStatusError("401", request=AsyncMock(), response=mock_resp)
        with pytest.raises(OpenAIClientError, match="OpenAI HTTP hatası"):
            await openai_client.generate("Hello")

@pytest.mark.asyncio
async def test_generate_request_error(openai_client):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.RequestError("Network drop", request=AsyncMock())
        with pytest.raises(OpenAIClientError, match="OpenAI bağlantı hatası"):
            await openai_client.generate("Hello")

@pytest.mark.asyncio
async def test_generate_stream_success(openai_client):
    class MockStreamResponse:
        def __init__(self):
            self.status_code = 200
        def raise_for_status(self):
            pass
        async def aiter_lines(self):
            yield 'data: {"choices": [{"delta": {"content": "Hello"}}]}'
            yield 'data: {"choices": [{"delta": {"content": " World"}}]}'
            yield 'data: [DONE]'
            
    class MockStreamContext:
        async def __aenter__(self):
            return MockStreamResponse()
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch("httpx.AsyncClient.stream", return_value=MockStreamContext()):
        chunks = []
        async for chunk in openai_client.generate_stream("Stream this"):
            chunks.append(chunk)
        assert chunks == ["Hello", " World"]

@pytest.mark.asyncio
async def test_generate_stream_error(openai_client):
    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.side_effect = Exception("Stream failed")
        with pytest.raises(OpenAIClientError, match="OpenAI streaming sırasında hata"):
            async for _ in openai_client.generate_stream("Stream this"):
                pass
