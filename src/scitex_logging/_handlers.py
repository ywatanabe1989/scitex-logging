#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Custom handlers for SciTeX logging."""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path

from ._formatters import SciTeXConsoleFormatter, SciTeXFileFormatter


def _get_scitex_dir() -> Path:
    """Get SCITEX_DIR with priority: env → default (~/.scitex)."""
    env_val = os.getenv("SCITEX_DIR")
    if env_val:
        return Path(env_val).expanduser()
    return Path.home() / ".scitex"


def create_console_handler(level=logging.INFO):
    """Create a console handler with SciTeX formatting."""
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(SciTeXConsoleFormatter())
    return handler


def create_file_handler(
    log_file_path, level=logging.INFO, max_bytes=10 * 1024 * 1024, backup_count=5
):
    """Create a rotating file handler for log files.

    Args:
        log_file_path: Path to the log file
        level: Log level for the handler
        max_bytes: Maximum size of log file before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)
    """
    # Ensure the log directory exists
    log_dir = Path(log_file_path).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # Use RotatingFileHandler to prevent log files from growing too large
    handler = logging.handlers.RotatingFileHandler(
        log_file_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    handler.setLevel(level)
    handler.setFormatter(SciTeXFileFormatter())
    return handler


def get_default_log_path():
    """Get the default log file path for SciTeX.

    Uses SCITEX_DIR environment variable with fallback to ~/.scitex.
    Supports .env file loading for configuration.
    """
    scitex_dir = _get_scitex_dir()
    logs_dir = scitex_dir / "logs"

    # Create timestamped log file
    timestamp = datetime.now().strftime("%Y-%m-%d")
    log_file = logs_dir / f"scitex-{timestamp}.log"

    return str(log_file)


__all__ = ["create_console_handler", "create_file_handler", "get_default_log_path"]
