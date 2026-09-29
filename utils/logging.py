"""Secure logging configuration with automatic secret masking."""
import logging
import re
import sys

_SENSITIVE_PATTERNS = [
    re.compile(r'(?i)(api[_-]?key|secret|password|token|bearer)\s*[:=]\s*([\'"]?)([a-zA-Z0-9_\-\.]{6,})(\2)'),
    re.compile(r'postgresql://([^:]+):([^@]+)@'),
]


class SecretMaskingFormatter(logging.Formatter):
    """Custom formatter to mask sensitive credentials in logs."""

    def format(self, record: logging.LogRecord) -> str:
        original = super().format(record)
        sanitized = original
        for pattern in _SENSITIVE_PATTERNS:
            if 'postgresql://' in pattern.pattern:
                sanitized = pattern.sub(r'postgresql://\1:***@', sanitized)
            else:
                sanitized = pattern.sub(r'\1=***REDACTED***', sanitized)
        return sanitized


def setup_logger(name: str = "customer_support_agent") -> logging.Logger:
    """Set up and return a configured logger with secret redaction."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = SecretMaskingFormatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
    return logger


logger = setup_logger()
