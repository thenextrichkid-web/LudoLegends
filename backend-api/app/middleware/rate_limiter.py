"""Rate limiting middleware — Redis-backed sliding window rate limiter."""

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.config import get_settings
from app.core.logging import get_logger, request_id_var

logger = get_logger("rate_limiter")

DEFAULT_LIMITS = {
    "/api/auth/otp/request": {"requests": 5, "window": 60},
    "/api/auth/otp/verify": {"requests": 10, "window": 60},
    "/api/auth/refresh": {"requests": 10, "window": 60},
    "/api/withdrawals/": {"requests": 5, "window": 300},
    "/api/wallet/deposit": {"requests": 10, "window": 60},
    "/api/referrals/process": {"requests": 10, "window": 60},
    "/api/admin": {"requests": 100, "window": 60},
}

GLOBAL_LIMIT = {"requests": 300, "window": 60}


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, custom_limits: dict | None = None):
        super().__init__(app)
        self.limits = {**DEFAULT_LIMITS, **(custom_limits or {})}
        self._memory_store: dict[str, list[float]] = {}

    def _get_key(self, path: str, client_ip: str) -> str:
        for pattern, limit in self.limits.items():
            if path.startswith(pattern):
                return f"rl:{pattern}:{client_ip}"
        return f"rl:global:{client_ip}"

    def _get_limit(self, path: str) -> dict:
        for pattern, limit in self.limits.items():
            if path.startswith(pattern):
                return limit
        return GLOBAL_LIMIT

    def _check_memory_store(self, key: str, window: int) -> int:
        now = time.time()
        cutoff = now - window
        if key not in self._memory_store:
            self._memory_store[key] = []
        self._memory_store[key] = [t for t in self._memory_store[key] if t > cutoff]
        return len(self._memory_store[key])

    def _record_request(self, key: str):
        self._memory_store.setdefault(key, []).append(time.time())
        if len(self._memory_store) > 10000:
            oldest_keys = sorted(self._memory_store.keys())[:1000]
            for k in oldest_keys:
                del self._memory_store[k]

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        if path in ("/health", "/ready", "/live", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = self._get_key(path, client_ip)
        limit_config = self._get_limit(path)
        window = limit_config["window"]
        max_requests = limit_config["requests"]

        current_count = self._check_memory_store(key, window)

        if current_count >= max_requests:
            retry_after = window - (time.time() - self._memory_store[key][0]) if self._memory_store[key] else window
            logger.warning("Rate limit exceeded: path=%s ip=%s count=%d/%d", path, client_ip, current_count, max_requests)
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "code": "RATE_LIMITED",
                    "message": f"Rate limit exceeded. Try again in {int(retry_after)}s.",
                    "requestId": request_id_var.get(""),
                },
                headers={"Retry-After": str(int(retry_after)), "X-RateLimit-Limit": str(max_requests), "X-RateLimit-Remaining": "0"},
            )

        self._record_request(key)
        response = await call_next(request)
        remaining = max(0, max_requests - current_count - 1)
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
