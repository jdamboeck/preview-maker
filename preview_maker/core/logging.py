"""Logging configuration for Preview Maker.

This module sets up the logging system for the application, providing
a consistent logging interface across all components.

Features:
- Configurable log levels (both string-based and numeric)
- File and console logging
- Log rotation with configurable sizes
- Custom log format strings
- Error logging with context information
- Thread-safe logging operations
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Union


# Create a logger for the application
logger = logging.getLogger("preview_maker")


def setup_logging(
    level: int = logging.INFO,
    log_level: Optional[Union[str, int]] = None,
    log_file: Optional[Union[str, Path]] = None,
    rotation: Optional[str] = None,
    retention: Optional[str] = None,
    format_string: Optional[str] = None,
) -> None:
    """Set up the logging system for the application.

    Args:
        level: The logging level to use (numeric)
        log_level: The logging level to use (string or numeric)
        log_file: Optional path to a log file
        rotation: Optional log rotation size (e.g., "1 MB")
        retention: Optional log retention period (e.g., "1 week")
        format_string: Optional custom format string for logs
    """
    # Handle log_level parameter if provided
    if log_level is not None:
        if isinstance(log_level, str):
            level = getattr(logging, log_level.upper())
        else:
            level = log_level

    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create a formatter
    if format_string:
        # Custom format string handling
        if "{time}" in format_string:
            format_string = format_string.replace("{time}", "%(asctime)s")
        if "{level}" in format_string:
            format_string = format_string.replace("{level}", "%(levelname)s")
        if "{message}" in format_string:
            format_string = format_string.replace("{message}", "%(message)s")
        formatter = logging.Formatter(format_string)
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Create a console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Create a file handler if a log file is specified
    if log_file:
        log_path = Path(log_file)

        # Create the directory if it doesn't exist
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if rotation is specified
        if rotation:
            try:
                from logging.handlers import RotatingFileHandler

                # Parse rotation size
                size_map = {"KB": 1024, "MB": 1024**2, "GB": 1024**3}
                rotation_parts = rotation.split()
                if len(rotation_parts) == 2:
                    size_value = float(rotation_parts[0])
                    size_unit = rotation_parts[1].upper()
                    max_bytes = int(size_value * size_map.get(size_unit, 1))

                    # Create rotating file handler
                    file_handler = RotatingFileHandler(
                        log_path,
                        maxBytes=max_bytes,
                        backupCount=5,  # Default to 5 backup files
                    )
                else:
                    # Fall back to regular file handler
                    file_handler = logging.FileHandler(log_path)
            except (ImportError, ValueError):
                # Fall back to regular file handler
                file_handler = logging.FileHandler(log_path)
        else:
            file_handler = logging.FileHandler(log_path)

        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Set the level for the preview_maker logger
    logger.setLevel(level)

    # Set the level for all component loggers
    component_loggers = [
        name
        for name in logging.Logger.manager.loggerDict
        if name.startswith("preview_maker.")
    ]
    for log_name in component_loggers:
        component_logger = logging.getLogger(log_name)
        component_logger.setLevel(level)

    # Log the setup
    logger.debug("Logging system initialized")


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific component.

    Args:
        name: The name of the component

    Returns:
        A logger instance for the component
    """
    component_logger = logging.getLogger(f"preview_maker.{name}")
    # Ensure component logger inherits level from parent
    component_logger.setLevel(logger.level)
    return component_logger


def log_error_with_context(exception: Exception, context: dict) -> None:
    """Log an error with additional context information.

    Args:
        exception: The exception to log
        context: Dictionary with additional context information
    """
    error_message = f"Error: {type(exception).__name__}: {str(exception)}"
    context_str = ", ".join(f"{k}={v}" for k, v in context.items())
    logger.error(f"{error_message} | Context: {context_str}")


# Initialize with default settings if this module is imported directly
if __name__ != "__main__":
    # Only set up basic logging if it hasn't been configured yet
    if not logger.handlers and not logging.getLogger().handlers:
        setup_logging()
