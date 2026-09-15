"""
middleware.py — Production Security & Rate Limiting Middlewares for PaperFox.

Provides:
1. SecurityHeadersMiddleware: Standard secure HTTP response headers.
2. RateLimitMiddleware: Lightweight, memory-efficient in-process sliding window rate limiter
   for authentication and expensive AI/render operations.
"""

import logging
import time
import re
from typing import Dict, List, Tuple
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from app.core.config import settings
from app.core.security import decode_token

logger = logging.getLogger("paperfox.middleware")


import uuid


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Appends industry-standard security headers to all HTTP responses
    and safely catches unhandled server exceptions to mask tracebacks.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            response = await call_next(request)
        except Exception as exc:
            error_id = str(uuid.uuid4())
            logger.error(
                f"Unhandled server exception [error_id={error_id}] on {request.method} {request.url.path}: {exc}",
                exc_info=True,
            )
            response = JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "error_id": error_id,
                },
            )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response


class SlidingWindowLimiter:
    """
    In-memory, sliding-window rate limiter with automatic TTL cleanup.
    Suitable for single-instance / serverless production nodes.
    """

    def __init__(self, window_seconds: int = 60):
        self.window_seconds = window_seconds
        # Key -> list of epoch timestamps
        self._records: Dict[str, List[float]] = {}
        self._last_cleanup = time.time()

    def clear(self):
        """Reset all rate limit records."""
        self._records.clear()
        self._last_cleanup = time.time()

    def _cleanup_expired(self, now: float):
        """Remove entries older than 2x the window duration to prevent unbounded memory growth."""
        if now - self._last_cleanup < 60.0:
            return
        cutoff = now - (self.window_seconds * 2)
        expired_keys = []
        for key, timestamps in self._records.items():
            valid = [ts for ts in timestamps if ts > cutoff]
            if not valid:
                expired_keys.append(key)
            else:
                self._records[key] = valid
        for k in expired_keys:
            del self._records[k]
        self._last_cleanup = now

    def is_rate_limited(self, key: str, max_requests: int) -> Tuple[bool, int]:
        """
        Check if request under `key` exceeds `max_requests`.
        Returns (is_limited: bool, retry_after_seconds: int).
        """
        now = time.time()
        self._cleanup_expired(now)

        cutoff = now - self.window_seconds
        timestamps = self._records.get(key, [])
        valid_timestamps = [ts for ts in timestamps if ts > cutoff]

        if len(valid_timestamps) >= max_requests:
            # Rate limited
            oldest_valid = valid_timestamps[0]
            retry_after = max(1, int(self.window_seconds - (now - oldest_valid)))
            self._records[key] = valid_timestamps
            return True, retry_after

        # Record this request
        valid_timestamps.append(now)
        self._records[key] = valid_timestamps
        return False, 0


# Compiled path matchers for rate-limited routes
AUTH_ROUTES_REGEX = re.compile(r"^/api/v1/auth/(login|signup)$")
AI_EXPENSIVE_ROUTES_REGEX = re.compile(
    r"^/api/v1/(jobs/[^/]+/(analyze|optimize|render)|profile/projects/[^/]+/extract-evidence)$"
)


# Shared limiter instances for the application
global_auth_limiter = SlidingWindowLimiter(window_seconds=60)
global_ai_limiter = SlidingWindowLimiter(window_seconds=60)


def reset_rate_limiters():
    """Reset rate limiter state (primarily for test isolation)."""
    global_auth_limiter.clear()
    global_ai_limiter.clear()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Applies route-specific rate limiting:
    - Auth routes: ~10 req/min per IP
    - Expensive AI/render operations: ~30 req/min per authenticated user (or IP fallback)
    """

    def __init__(self, app):
        super().__init__(app)
        self.auth_limiter = global_auth_limiter
        self.ai_limiter = global_ai_limiter

    def _get_client_ip(self, request: Request) -> str:
        # Check standard reverse proxy headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        return request.client.host if request.client else "unknown"

    def _get_user_id_from_auth(self, request: Request) -> str:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
            payload = decode_token(token, settings.SECRET_KEY)
            if payload and payload.get("type") == "access" and payload.get("sub"):
                return str(payload["sub"])
        return ""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not settings.RATE_LIMITING_ENABLED:
            return await call_next(request)

        path = request.url.path

        # 1. Check Auth Routes
        if AUTH_ROUTES_REGEX.match(path):
            client_ip = self._get_client_ip(request)
            key = f"auth:{client_ip}"
            is_limited, retry_after = self.auth_limiter.is_rate_limited(
                key=key, max_requests=settings.RATE_LIMIT_AUTH_PER_MINUTE
            )
            if is_limited:
                logger.warning(f"Rate limit exceeded for auth route {path} from IP {client_ip}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too many requests. Please wait before trying again.",
                        "retry_after": retry_after,
                    },
                    headers={"Retry-After": str(retry_after)},
                )

        # 2. Check AI & Expensive Render Routes
        elif AI_EXPENSIVE_ROUTES_REGEX.match(path):
            user_id = self._get_user_id_from_auth(request)
            identifier = f"user:{user_id}" if user_id else f"ip:{self._get_client_ip(request)}"
            key = f"ai:{identifier}"
            is_limited, retry_after = self.ai_limiter.is_rate_limited(
                key=key, max_requests=settings.RATE_LIMIT_AI_PER_MINUTE
            )
            if is_limited:
                logger.warning(f"Rate limit exceeded for AI/render route {path} for {identifier}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "AI service rate limit reached. Please wait before submitting another request.",
                        "retry_after": retry_after,
                    },
                    headers={"Retry-After": str(retry_after)},
                )

        return await call_next(request)
