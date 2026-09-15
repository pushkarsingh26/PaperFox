import logging
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.providers.ai.factory import get_provider
from app.providers.ai.exceptions import (
    AIProviderError,
    AIProviderAuthError,
    AIProviderRateLimitError,
    AIProviderServerError,
    AIProviderTimeoutError,
    AIProviderJSONError
)

logger = logging.getLogger(__name__)


class ProviderRouter:
    """
    Multi-Provider AI Router with task-based routing, ordered fallback chains,
    bounded retries, timeout management, and schema validation.
    """

    def __init__(
        self,
        primary_provider: Optional[str] = None,
        fallback_providers: Optional[List[str]] = None,
        max_retries: Optional[int] = None
    ):
        self.primary_provider = (primary_provider or settings.JD_ANALYSIS_PRIMARY_PROVIDER).lower()
        
        fallbacks_raw = fallback_providers or settings.JD_ANALYSIS_FALLBACK_PROVIDERS
        if isinstance(fallbacks_raw, str):
            fallbacks_list = [f.strip().lower() for f in fallbacks_raw.split(",") if f.strip()]
        else:
            fallbacks_list = [f.lower() for f in fallbacks_raw]

        # Build fallback chain: primary -> fallbacks (no duplicate adjacent providers)
        chain = [self.primary_provider]
        for f in fallbacks_list:
            if f not in chain:
                chain.append(f)
        self.provider_chain = chain
        self.max_retries = max_retries if max_retries is not None else settings.AI_MAX_RETRIES

    async def generate_structured_json(
        self, prompt: str, schema: Dict[str, Any], system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes structured JSON generation across the provider fallback chain.
        Returns:
            {
                "data": Dict[str, Any],
                "provider": str,
                "model": str,
                "attempt_history": List[Dict[str, Any]]
            }
        """
        attempt_history = []

        for provider_name in self.provider_chain:
            try:
                provider_instance = get_provider(provider_name)
            except Exception as e:
                logger.warning(f"Could not initialize provider {provider_name}: {str(e)}")
                attempt_history.append({"provider": provider_name, "error": str(e), "status": "INIT_FAILED"})
                continue

            for attempt in range(1, self.max_retries + 1):
                logger.info(f"Attempting AI request with provider={provider_name} (Attempt {attempt}/{self.max_retries})")
                try:
                    res_data = await provider_instance.generate_structured_json(
                        prompt=prompt, schema=schema, system_prompt=system_prompt
                    )
                    logger.info(f"AI request succeeded with provider={provider_name}")
                    return {
                        "data": res_data,
                        "provider": provider_name,
                        "model": provider_instance.model,
                        "attempt_history": attempt_history
                    }
                except (AIProviderAuthError, AIProviderRateLimitError, AIProviderServerError, AIProviderTimeoutError, AIProviderJSONError, AIProviderError) as exc:
                    err_msg = f"Provider {provider_name} failed (Attempt {attempt}): {exc.message}"
                    logger.warning(err_msg)
                    attempt_history.append({
                        "provider": provider_name,
                        "attempt": attempt,
                        "error": exc.message,
                        "status_code": getattr(exc, "status_code", 500)
                    })
                    # If Auth failure or non-retryable error, jump to next provider immediately
                    if isinstance(exc, AIProviderAuthError):
                        break

        # If all providers fail:
        history_summary = "; ".join([f"{h['provider']}: {h.get('error', 'failed')}" for h in attempt_history])
        raise AIProviderError(
            f"All AI providers in fallback chain failed. Failure history: [{history_summary}]",
            provider="router",
            status_code=503
        )
