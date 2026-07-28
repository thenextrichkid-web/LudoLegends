"""Structured logging with request IDs and correlation IDs."""

import logging
import json
import uuid
import sys
from datetime import datetime, timezone
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="")
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        req_id = request_id_var.get("")
        if req_id:
            log_entry["request_id"] = req_id

        corr_id = correlation_id_var.get("")
        if corr_id:
            log_entry["correlation_id"] = corr_id

        if hasattr(record, "extra_data"):
            log_entry["data"] = record.extra_data

        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = {
                "type": type(record.exc_info[1]).__name__,
                "message": str(record.exc_info[1]),
            }

        return json.dumps(log_entry, default=str)


class HumanFormatter(logging.Formatter):
    FMT = "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s"
    DATE_FMT = "%Y-%m-%d %H:%M:%S"

    def format(self, record: logging.LogRecord) -> str:
        req_id = request_id_var.get("")
        prefix = f"[{req_id[:8]}] " if req_id else ""
        self.datefmt = self.DATE_FMT
        return f"{prefix}{super().format(record)}"


def setup_logging(environment: str = "development"):
    root = logging.getLogger()
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if environment in ("production", "staging"):
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(HumanFormatter())

    handler.setLevel(logging.INFO)
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def generate_request_id() -> str:
    return uuid.uuid4().hex[:16]


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
