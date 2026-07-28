"""Crash reporting — structured error context for every production error."""

import json
import platform
from datetime import datetime, timezone
from app.core.logging import get_logger, request_id_var, correlation_id_var

logger = get_logger("crash_reporter")


class CrashContext:
    def __init__(self, request=None, user_id: str | None = None):
        self.request = request
        self.user_id = user_id
        self.request_id = request_id_var.get("")
        self.correlation_id = correlation_id_var.get("")
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.environment = "production"

    def to_dict(self) -> dict:
        ctx = {
            "timestamp": self.timestamp,
            "environment": self.environment,
            "request_id": self.request_id,
            "correlation_id": self.correlation_id,
            "user_id": self.user_id,
            "platform": platform.platform(),
            "python_version": platform.python_version(),
        }
        if self.request:
            ctx["http"] = {
                "method": self.request.method,
                "url": str(self.request.url),
                "path": self.request.url.path,
                "query": str(self.request.query_params),
                "client": self.request.client.host if self.request.client else None,
                "user_agent": self.request.headers.get("user-agent", ""),
            }
        return ctx

    def report_exception(self, exc: Exception, extra: dict | None = None):
        ctx = self.to_dict()
        ctx["exception"] = {
            "type": type(exc).__name__,
            "message": str(exc),
        }
        if extra:
            ctx["extra"] = extra

        logger.error(
            "CRASH: %s at %s %s — user=%s req=%s",
            type(exc).__name__,
            ctx.get("http", {}).get("method", "?"),
            ctx.get("http", {}).get("path", "?"),
            self.user_id or "anonymous",
            self.request_id,
            exc_info=True,
        )
        return ctx
