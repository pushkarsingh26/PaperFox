from typing import Dict, Optional, Type
from app.providers.ai.base import LLMProvider
from app.providers.ai.gemini import GeminiProvider
from app.providers.ai.groq import GroqProvider
from app.providers.ai.openrouter import OpenRouterProvider
from app.providers.ai.nvidia import NVIDIAProvider
from app.providers.ai.exceptions import AIProviderError

PROVIDERS: Dict[str, Type[LLMProvider]] = {
    "gemini": GeminiProvider,
    "groq": GroqProvider,
    "openrouter": OpenRouterProvider,
    "nvidia": NVIDIAProvider,
}

def get_provider(provider_name: str, api_key: Optional[str] = None, model: Optional[str] = None) -> LLMProvider:
    provider_name_clean = provider_name.strip().lower()
    if provider_name_clean not in PROVIDERS:
        raise AIProviderError(f"Unsupported AI provider: {provider_name}", provider=provider_name_clean)
    provider_cls = PROVIDERS[provider_name_clean]
    return provider_cls(api_key=api_key, model=model)
