import json
import httpx
from typing import Any, Dict, Optional
from app.core.config import settings
from app.providers.ai.base import LLMProvider
from app.providers.ai.exceptions import (
    AIProviderAuthError,
    AIProviderJSONError,
    AIProviderRateLimitError,
    AIProviderServerError,
    AIProviderTimeoutError,
    AIProviderError
)


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GOOGLE_API_KEY
        self.model = model or settings.GOOGLE_MODEL
        self.provider_name = "gemini"

    async def generate_completion(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key or self.api_key.startswith("your-"):
            raise AIProviderAuthError("Google Gemini API key not configured", provider=self.provider_name, status_code=401)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        parts = []
        if system_prompt:
            parts.append({"text": f"System: {system_prompt}\n\nUser: {prompt}"})
        else:
            parts.append({"text": prompt})

        payload = {"contents": [{"parts": parts}]}
        timeout = float(settings.AI_TIMEOUT_SECONDS)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if not candidates:
                        raise AIProviderError("Gemini returned empty candidate list", provider=self.provider_name)
                    return candidates[0]["content"]["parts"][0]["text"]
                elif res.status_code in (401, 403):
                    raise AIProviderAuthError(f"Gemini Auth failed ({res.status_code}): {res.text[:150]}", provider=self.provider_name, status_code=res.status_code)
                elif res.status_code == 429:
                    raise AIProviderRateLimitError("Gemini Rate Limit Exceeded", provider=self.provider_name, status_code=429)
                elif res.status_code >= 500:
                    raise AIProviderServerError(f"Gemini Server Error ({res.status_code})", provider=self.provider_name, status_code=res.status_code)
                else:
                    raise AIProviderError(f"Gemini Error ({res.status_code}): {res.text[:150]}", provider=self.provider_name, status_code=res.status_code)
        except httpx.TimeoutException:
            raise AIProviderTimeoutError(f"Gemini Request Timed Out ({timeout}s)", provider=self.provider_name, status_code=504)
        except AIProviderError:
            raise
        except Exception as e:
            raise AIProviderError(f"Gemini Connection Error: {str(e)}", provider=self.provider_name)

    async def generate_structured_json(
        self, prompt: str, schema: Dict[str, Any], system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.api_key or self.api_key.startswith("your-"):
            raise AIProviderAuthError("Google Gemini API key not configured", provider=self.provider_name, status_code=401)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        parts = []
        if system_prompt:
            parts.append({"text": f"System: {system_prompt}\n\nUser: {prompt}"})
        else:
            parts.append({"text": prompt})

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {"responseMimeType": "application/json"}
        }
        timeout = float(settings.AI_TIMEOUT_SECONDS)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if not candidates:
                        raise AIProviderError("Gemini returned empty candidate list", provider=self.provider_name)
                    text = candidates[0]["content"]["parts"][0]["text"]
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError as err:
                        raise AIProviderJSONError(f"Gemini JSON Parse Error: {str(err)}", provider=self.provider_name)
                elif res.status_code in (401, 403):
                    raise AIProviderAuthError(f"Gemini Auth failed ({res.status_code}): {res.text[:150]}", provider=self.provider_name, status_code=res.status_code)
                elif res.status_code == 429:
                    raise AIProviderRateLimitError("Gemini Rate Limit Exceeded", provider=self.provider_name, status_code=429)
                elif res.status_code >= 500:
                    raise AIProviderServerError(f"Gemini Server Error ({res.status_code})", provider=self.provider_name, status_code=res.status_code)
                else:
                    raise AIProviderError(f"Gemini Error ({res.status_code}): {res.text[:150]}", provider=self.provider_name, status_code=res.status_code)
        except httpx.TimeoutException:
            raise AIProviderTimeoutError(f"Gemini Request Timed Out ({timeout}s)", provider=self.provider_name, status_code=504)
        except AIProviderError:
            raise
        except Exception as e:
            raise AIProviderError(f"Gemini Connection Error: {str(e)}", provider=self.provider_name)
