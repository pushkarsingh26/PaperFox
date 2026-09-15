class AIProviderError(Exception):
    """Base exception for AI provider errors."""
    def __init__(self, message: str, provider: str = "unknown", status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.status_code = status_code


class AIProviderAuthError(AIProviderError):
    """Raised when authentication/API key is invalid or missing."""
    pass


class AIProviderRateLimitError(AIProviderError):
    """Raised when provider hits rate limits (429)."""
    pass


class AIProviderServerError(AIProviderError):
    """Raised when provider returns a server error (5xx)."""
    pass


class AIProviderTimeoutError(AIProviderError):
    """Raised when request times out."""
    pass


class AIProviderJSONError(AIProviderError):
    """Raised when provider output fails JSON parsing or validation."""
    pass
