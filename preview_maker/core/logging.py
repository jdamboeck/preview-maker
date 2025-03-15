"""Logging configuration for Preview Maker.

This module sets up the logging system for the application, providing
a consistent logging interface across all components.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional, Union


# Create a logger for the application
logger = logging.getLogger("preview_maker")


def setup_logging(
    level: int = logging.INFO, log_file: Optional[Union[str, Path]] = None
) -> None:
    """Set up the logging system for the application.

    Args:
        level: The logging level to use
        log_file: Optional path to a log file
    """
    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create a formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Create a console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Create a file handler if a log file is specified
    if log_file:
        log_path = Path(log_file)

        # Create the directory if it doesn't exist
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Set the level for the preview_maker logger
    logger.setLevel(level)

    # Log the setup
    logger.debug("Logging system initialized")


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific component.

    Args:
        name: The name of the component

    Returns:
        A logger instance for the component
    """
    return logging.getLogger(f"preview_maker.{name}")


# Initialize with default settings if this module is imported directly
if __name__ != "__main__":
    # Only set up basic logging if it hasn't been configured yet
    if not logger.handlers and not logging.getLogger().handlers:
        setup_logging()
