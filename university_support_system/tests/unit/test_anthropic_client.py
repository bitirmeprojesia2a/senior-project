from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest

from src.llm.anthropic_client import AnthropicClient, AnthropicClientError


def _config(api_key: str | None = "anthropic-key"):
    return SimpleNamespace(
        api_key=api_key,
        base_url="https://api.anthropic.com",
        model="claude-sonnet-4-20250514",
        timeout=60,
        max_tokens=4096,
        anthropic_version="2023-06-01",
        temperature=None,
        provider_name="anthropic",
    )


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
            raise httpx.HTTPStatusError("Error", request=AsyncMock(), response=self)


def test_anthropic_headers_and_availability():
    client = AnthropicClient(_config())

    assert client.is_available is True
    headers = client._get_headers()
    assert headers["x-api-key"] == "anthropic-key"
    assert headers["anthropic-version"] == "2023-06-01"


def test_anthropic_missing_key_raises_for_headers():
    client = AnthropicClient(_config(api_key=None))

    assert client.is_available is False
    with pytest.raises(AnthropicClientError):
        client._get_headers()


@pytest.mark.asyncio
async def test_anthropic_get_health_healthy(monkeypatch):
    client = AnthropicClient(_config())
    mock_resp = MockResponse(
        json_data={"data": [{"id": "claude-sonnet-4-20250514"}, {"id": "claude-3-5-haiku-20241022"}]}
    )
    monkeypatch.setattr("httpx.AsyncClient.get", AsyncMock(return_value=mock_resp))

    result = await client.get_health(models=["claude-sonnet-4-20250514"])

    assert result["status"] == "healthy"
    assert result["configured_models_found"] == {"claude-sonnet-4-20250514": True}


@pytest.mark.asyncio
async def test_anthropic_generate_success(monkeypatch):
    client = AnthropicClient(_config())
    mock_post = AsyncMock(
        return_value=MockResponse(
            json_data={
                "content": [
                    {
                        "type": "text",
                        "text": "Claude cevabi",
                    }
                ]
            }
        )
    )
    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)

    result = await client.generate("Selam", system="Sistem", json_mode=True)

    assert result == "Claude cevabi"
    payload = mock_post.call_args.kwargs["json"]
    assert payload["model"] == "claude-sonnet-4-20250514"
    assert payload["max_tokens"] == 4096
    assert payload["messages"] == [{"role": "user", "content": "Selam"}]
    assert "Return only valid JSON" in payload["system"]


@pytest.mark.asyncio
async def test_anthropic_generate_http_error_is_retryable(monkeypatch):
    client = AnthropicClient(_config())
    mock_post = AsyncMock(return_value=MockResponse(status_code=429, text_data="rate limited"))
    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)

    with pytest.raises(AnthropicClientError) as exc_info:
        await client.generate("Selam")

    assert exc_info.value.retryable is True
