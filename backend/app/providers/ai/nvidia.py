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


class NVIDIAProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.NVIDIA_API_KEY
        self.model = model or settings.NVIDIA_MODEL
        self.provider_name = "nvidia"

    async def generate_completion(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key or self.api_key.startswith("your-"):
            raise AIProviderAuthError("NVIDIA API key not configured", provider=self.provider_name, status_code=401)

        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {"model": self.model, "messages": messages, "temperature": 0.2, "max_tokens": 1024}
        timeout = float(settings.AI_TIMEOUT_SECONDS)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                res = await client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    choices = data.get("choices", [])
                    if not choices:
                        raise AIProviderError("NVIDIA returned empty choices", provider=self.provider_name)
                    return choices[0]["message"]["content"]
                elif res.status_code in (401, 403):
                    raise AIProviderAuthError(f"NVIDIA Auth failed ({res.status_code}): {res.text[:150]}", provider=self.provider_name, status_code=res.status_code)
                elif res.status_code == 429:
                    raise AIProviderRateLimitError("NVIDIA Rate Limit Exceeded", provider=self.provider_name, status_code=429)
                elif res.status_code >= 500:
                    raise AIProviderServerError(f"NVIDIA Server Error ({res.status_code})", provider=self.provider_name, status_code=res.status_code)
                else:
                    raise AIProviderError(f"NVIDIA Error ({res.status_code}): {res.text[:150]}", provider=self.provider_name, status_code=res.status_code)
        except httpx.TimeoutException:
            raise AIProviderTimeoutError(f"NVIDIA Request Timed Out ({timeout}s)", provider=self.provider_name, status_code=504)
        except AIProviderError:
            raise
        except Exception as e:
            raise AIProviderError(f"NVIDIA Connection Error: {str(e)}", provider=self.provider_name)

    async def generate_structured_json(
        self, prompt: str, schema: Dict[str, Any], system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        raw_text = await self.generate_completion(prompt, system_prompt)
        try:
            # Clean markdown JSON block formatting if present
            cleaned = raw_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
        except json.JSONDecodeError as err:
            raise AIProviderJSONError(f"NVIDIA JSON Parse Error: {str(err)}", provider=self.provider_name)
