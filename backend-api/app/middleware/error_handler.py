"""Centralized exception handler — standardized API error responses with crash reporting."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.logging import request_id_var, get_logger
from app.core.crash_reporter import CrashContext
from app.core.metrics import metrics

logger = get_logger("error_handler")


class APIError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details: dict | None = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class InsufficientBalanceError(APIError):
    def __init__(self):
        super().__init__("INSUFFICIENT_BALANCE", "Not enough balance.", 400)


class UnauthorizedError(APIError):
    def __init__(self, message: str = "Authentication required."):
        super().__init__("UNAUTHORIZED", message, 401)


class ForbiddenError(APIError):
    def __init__(self, message: str = "You don't have permission."):
        super().__init__("FORBIDDEN", message, 403)


class NotFoundError(APIError):
    def __init__(self, resource: str = "Resource"):
        super().__init__("NOT_FOUND", f"{resource} not found.", 404)


class ValidationError(APIError):
    def __init__(self, message: str = "Invalid input."):
        super().__init__("VALIDATION_ERROR", message, 422)


class ConflictError(APIError):
    def __init__(self, message: str = "Resource already exists."):
        super().__init__("CONFLICT", message, 409)


class RateLimitError(APIError):
    def __init__(self):
        super().__init__("RATE_LIMITED", "Too many requests.", 429)


class MaintenanceError(APIError):
    def __init__(self):
        super().__init__("MAINTENANCE", "System is under maintenance. Please try again later.", 503)


def _error_response(code: str, message: str, status_code: int, request_id: str, details: dict | None = None) -> dict:
    body = {
        "success": False,
        "code": code,
        "message": message,
        "requestId": request_id,
    }
    if details:
        body["details"] = details
    return body


def register_error_handlers(app: FastAPI):

    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError):
        req_id = request_id_var.get("")
        metrics.increment("api_errors")
        metrics.increment(f"api_error:{exc.code}")
        logger.warning("API error: code=%s message=%s path=%s", exc.code, exc.message, request.url.path)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_response(exc.code, exc.message, exc.status_code, req_id, getattr(exc, "details", None)),
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        req_id = request_id_var.get("")
        metrics.increment("api_errors")
        metrics.increment("api_error:VALIDATION_ERROR")
        return JSONResponse(
            status_code=400,
            content=_error_response("VALIDATION_ERROR", str(exc), 400, req_id),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        req_id = request_id_var.get("")
        metrics.increment("unhandled_exceptions")

        crash = CrashContext(request)
        crash.report_exception(exc)

        return JSONResponse(
            status_code=500,
            content=_error_response("INTERNAL_ERROR", "An unexpected error occurred.", 500, req_id),
        )
