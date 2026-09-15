import pytest
from unittest.mock import MagicMock, patch
from app.providers.ai.exceptions import (
    AIProviderAuthError,
    AIProviderError,
    AIProviderJSONError,
    AIProviderRateLimitError,
    AIProviderTimeoutError
)
from app.providers.ai.gemini import GeminiProvider
from app.providers.ai.groq import GroqProvider
from app.providers.ai.openrouter import OpenRouterProvider
from app.services.ai.provider_router import ProviderRouter


@pytest.mark.asyncio
async def test_gemini_provider_success():
    provider = GeminiProvider(api_key="valid-key", model="gemini-2.5-flash")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": '{"status": "ok"}'}]}}]
    }

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        res = await provider.generate_structured_json("prompt", {})
        assert res == {"status": "ok"}


@pytest.mark.asyncio
async def test_gemini_provider_rate_limit():
    provider = GeminiProvider(api_key="valid-key", model="gemini-2.5-flash")
    mock_response = MagicMock()
    mock_response.status_code = 429

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        with pytest.raises(AIProviderRateLimitError):
            await provider.generate_structured_json("prompt", {})


@pytest.mark.asyncio
async def test_groq_provider_success():
    provider = GroqProvider(api_key="valid-key", model="openai/gpt-oss-20b")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": '{"status": "groq_ok"}'}}]
    }

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        res = await provider.generate_structured_json("prompt", {})
        assert res == {"status": "groq_ok"}


@pytest.mark.asyncio
async def test_provider_router_fallback_on_primary_failure():
    router = ProviderRouter(primary_provider="gemini", fallback_providers=["groq", "openrouter"])

    # Primary (Gemini) fails with 429, Fallback (Groq) succeeds
    mock_gemini_res = MagicMock()
    mock_gemini_res.status_code = 429

    mock_groq_res = MagicMock()
    mock_groq_res.status_code = 200
    mock_groq_res.json.return_value = {
        "choices": [{"message": {"content": '{"result": "fallback_success"}'}}]
    }

    async def mock_post(url, *args, **kwargs):
        if "generativelanguage" in str(url):
            return mock_gemini_res
        elif "groq.com" in str(url):
            return mock_groq_res
        raise RuntimeError("Unexpected URL")

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        result = await router.generate_structured_json("test prompt", {})
        assert result["data"] == {"result": "fallback_success"}
        assert result["provider"] == "groq"
        assert len(result["attempt_history"]) > 0


@pytest.mark.asyncio
async def test_provider_router_all_fail():
    router = ProviderRouter(primary_provider="gemini", fallback_providers=["groq"])

    mock_fail = MagicMock()
    mock_fail.status_code = 500
    mock_fail.text = "Internal error"

    with patch("httpx.AsyncClient.post", return_value=mock_fail):
        with pytest.raises(AIProviderError) as exc_info:
            await router.generate_structured_json("test prompt", {})
        assert "All AI providers in fallback chain failed" in str(exc_info.value)
