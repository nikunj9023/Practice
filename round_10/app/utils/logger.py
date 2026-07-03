"""
app/utils/logger.py
===================
Centralised structured logging configuration.

Call ``setup_logging()`` once from ``create_app()``; every module then uses
``logging.getLogger(__name__)`` to obtain a correctly configured logger.
"""

from __future__ import annotations

import logging
import logging.handlers
import os
import sys
from typing import Any


# ---------------------------------------------------------------------------
# Log formatter
# ---------------------------------------------------------------------------

class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that produces consistent, machine-readable log lines.

    Format:
        [LEVEL] YYYY-MM-DD HH:MM:SS | module:line | message [key=value ...]
    """

    _DATEFMT = "%Y-%m-%d %H:%M:%S"
    _FMT = "[%(levelname)-8s] %(asctime)s | %(name)s:%(lineno)d | %(message)s"

    def __init__(self) -> None:
        super().__init__(fmt=self._FMT, datefmt=self._DATEFMT)

    def format(self, record: logging.LogRecord) -> str:
        # Abbreviate the logger name to the last two segments for brevity.
        parts = record.name.split(".")
        record.name = ".".join(parts[-2:]) if len(parts) > 2 else record.name
        return super().format(record)


# ---------------------------------------------------------------------------
# Setup function
# ---------------------------------------------------------------------------

def setup_logging(
    level: str = "INFO",
    log_to_file: bool = True,
    log_dir: str = "logs",
    log_filename: str = "crm.log",
) -> None:
    """
    Configure the root logger for the entire application.

    Parameters
    ----------
    level : str
        Minimum log level (e.g. ``"DEBUG"``, ``"INFO"``, ``"WARNING"``).
        Defaults to ``"INFO"``; overridden by the ``LOG_LEVEL`` environment
        variable when present.
    log_to_file : bool
        When ``True``, also write logs to a rotating file in ``log_dir``.
    log_dir : str
        Directory for log files, relative to the current working directory.
    log_filename : str
        Base file name for the rotating log file.
    """
    effective_level_str = os.getenv("LOG_LEVEL", level).upper()
    numeric_level = getattr(logging, effective_level_str, logging.INFO)

    formatter = StructuredFormatter()

    handlers: list[logging.Handler] = []

    # --- Console handler ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    # --- Rotating file handler ---
    if log_to_file:
        os.makedirs(log_dir, exist_ok=True)
        file_path = os.path.join(log_dir, log_filename)
        file_handler = logging.handlers.RotatingFileHandler(
            filename=file_path,
            maxBytes=5 * 1024 * 1024,   # 5 MB per file
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    # Configure root logger – suppress noisy third-party loggers.
    logging.basicConfig(level=numeric_level, handlers=handlers, force=True)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if effective_level_str == "DEBUG" else logging.WARNING
    )

    logging.getLogger(__name__).info(
        "Logging initialised | level=%s | file=%s",
        effective_level_str,
        os.path.join(log_dir, log_filename) if log_to_file else "disabled",
    )


def get_logger(name: str) -> logging.Logger:
    """
    Convenience wrapper – equivalent to ``logging.getLogger(name)``.

    Usage::

        from app.utils.logger import get_logger
        logger = get_logger(__name__)
    """
    return logging.getLogger(name)
