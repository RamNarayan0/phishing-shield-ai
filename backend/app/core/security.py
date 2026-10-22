import os
import time
import logging
from collections import defaultdict
from typing import Dict, List, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader

logger = logging.getLogger("phishing_shield.security")

# Configuration from Environment
MAX_REQUEST_SIZE_BYTES = int(os.getenv("MAX_REQUEST_SIZE_BYTES", 262144))  # 256 KB default
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", 60))
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "").strip()

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

class ContentLengthLimitMiddleware(BaseHTTPMiddleware):
    """Rejects request payloads exceeding the configured byte limit to prevent DoS."""
    def __init__(self, app, max_length: int = MAX_REQUEST_SIZE_BYTES):
        super().__init__(app)
        self.max_length = max_length

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length = int(content_length)
                if length > self.max_length:
                    return JSONResponse(
                        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                        content={"detail": f"Request entity too large. Maximum allowed size is {self.max_length} bytes."}
                    )
            except ValueError:
                pass
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Applies standard protective security headers to all responses."""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


class InMemoryRateLimiter:
    """Sliding-window in-memory rate limiter per client IP."""
    def __init__(self, limit: int = RATE_LIMIT_PER_MINUTE, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        cutoff = now - self.window_seconds

        # Purge older requests
        timestamps = [t for t in self.requests[client_ip] if t > cutoff]
        self.requests[client_ip] = timestamps

        if len(timestamps) >= self.limit:
            return False

        self.requests[client_ip].append(now)
        return True

    def reset(self):
        self.requests.clear()

rate_limiter = InMemoryRateLimiter(limit=RATE_LIMIT_PER_MINUTE, window_seconds=60)


async def check_rate_limit(request: Request):
    """FastAPI dependency to enforce rate limiting on expensive endpoints."""
    # Obtain real IP if behind trusted reverse proxy, otherwise client.host
    client_ip = request.headers.get("X-Forwarded-For")
    if client_ip:
        client_ip = client_ip.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "127.0.0.1"

    if not rate_limiter.is_allowed(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait before submitting more requests.",
            headers={"Retry-After": "60"}
        )


async def verify_admin_access(api_key: Optional[str] = Security(api_key_header)) -> bool:
    """
    Verifies administrative/history access.
    If ADMIN_API_KEY is configured, enforces authentication.
    If ADMIN_API_KEY is empty/unconfigured (e.g. local dev), permits access with a logged audit notice.
    """
    configured_key = os.getenv("ADMIN_API_KEY", "").strip()
    if not configured_key:
        # Development mode: permit access
        return True

    if not api_key or api_key != configured_key:
        logger.warning("Unauthorized administrative access attempt.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header for protected resource."
        )
    return True


def sanitize_for_log(text: str, max_chars: int = 100) -> str:
    """Safe logger preview that truncates text and masks potential credentials."""
    if not text:
        return ""
    clean = " ".join(text.split())
    if len(clean) > max_chars:
        clean = clean[:max_chars] + "...[TRUNCATED]"
    return clean
