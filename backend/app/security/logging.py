"""Structured JSON logging configuration."""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict

from app.config import settings


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception information if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add custom fields from request context
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Simple text log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as text."""
        request_id = getattr(record, "request_id", "")
        request_id_str = f"[{request_id}] " if request_id else ""
        return f"{self.formatTime(record)} - {record.levelname} - {request_id_str}{record.getMessage()}"


def setup_logging() -> None:
    """Configure application logging."""
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(settings.log_level)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.log_level)

    # Set formatter based on configuration
    if settings.log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    logger.info(f"Logging configured: format={settings.log_format}, level={settings.log_level}")
