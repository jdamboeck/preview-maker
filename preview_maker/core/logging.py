"""Logging configuration for Preview Maker.

This module sets up application-wide logging using loguru with support for
different log levels, file output, and structured logging.
"""

import sys
from pathlib import Path
from typing import Optional, Union, Dict, Any
from loguru import logger


def setup_logging(
    log_file: Optional[Union[str, Path]] = None,
    log_level: str = "INFO",
    rotation: str = "10 MB",
    retention: str = "1 week",
    format_string: Optional[str] = None,
) -> None:
    """Configure application logging.

    Args:
        log_file: Optional path to log file. If None, logs to stderr only.
        log_level: Minimum log level to record (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        rotation: When to rotate log files (e.g., "10 MB", "1 day")
        retention: How long to keep log files (e.g., "1 week", "1 month")
        format_string: Optional custom format string for log messages
    """
    # Remove default handler
    logger.remove()

    # Default format string if none provided
    if format_string is None:
        format_string = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

    # Add stderr handler
    logger.add(sys.stderr, format=format_string, level=log_level, colorize=True)

    # Add file handler if log file specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(log_path),
            format=format_string,
            level=log_level,
            rotation=rotation,
            retention=retention,
            compression="zip",
        )


def log_error_with_context(
    error: Exception, context: Optional[Dict[str, Any]] = None
) -> None:
    """Log an error with additional context information.

    Args:
        error: The exception to log
        context: Optional dictionary of additional context information
    """
    error_type = type(error).__name__
    error_msg = str(error)

    # Format context information if provided
    context_str = ""
    if context:
        context_str = " | " + " | ".join(f"{k}={v}" for k, v in context.items())

    logger.error(f"Error occurred: {error_type} - {error_msg}{context_str}")
    logger.exception(error)


# Configure default logging to stderr
setup_logging()
