"""Tests for the logging module.

This module contains tests for the logging configuration and functionality.
"""

import logging
import os
import tempfile
from pathlib import Path

import pytest

from preview_maker.core.logging import setup_logging, get_logger, logger


class TestLogging:
    """Tests for the logging module."""

    def test_setup_logging_default(self):
        """Test setting up logging with default parameters."""
        # Reset logging
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Set up logging with defaults
        setup_logging()

        # Check that the root logger has a handler
        assert len(root_logger.handlers) > 0

        # Check that the preview_maker logger is configured
        assert logger.level == logging.INFO

    def test_setup_logging_with_file(self):
        """Test setting up logging with a log file."""
        # Create a temporary file for logging
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"

            # Reset logging
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

            # Set up logging with a file
            setup_logging(level=logging.DEBUG, log_file=log_file)

            # Check that the root logger has handlers
            assert len(root_logger.handlers) > 0

            # Check that the preview_maker logger is configured
            assert logger.level == logging.DEBUG

            # Log a message
            logger.debug("Test debug message")
            logger.info("Test info message")

            # Check that the log file exists and contains the messages
            assert log_file.exists()
            log_content = log_file.read_text()
            assert "Test debug message" in log_content
            assert "Test info message" in log_content

    def test_get_logger(self):
        """Test getting a logger for a specific component."""
        # Get a logger for a component
        component_logger = get_logger("test_component")

        # Check that the logger has the correct name
        assert component_logger.name == "preview_maker.test_component"

        # Check that the logger inherits the level from the parent
        assert component_logger.level == logger.level


@pytest.fixture
def temp_log_file():
    """Fixture providing a temporary log file."""
    with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as f:
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


def test_setup_logging_stderr(capsys):
    """Test that logging to stderr works."""
    setup_logging(log_level="INFO")
    logger.info("Test message")

    captured = capsys.readouterr()
    assert "Test message" in captured.err


def test_setup_logging_file(temp_log_file):
    """Test that logging to file works."""
    setup_logging(log_file=temp_log_file, log_level="INFO")
    test_message = "Test file logging"
    logger.info(test_message)

    with open(temp_log_file, "r") as f:
        log_content = f.read()

    assert test_message in log_content


def test_log_error_with_context(capsys):
    """Test error logging with context."""
    setup_logging(log_level="ERROR")

    try:
        raise ValueError("Test error")
    except Exception as e:
        context = {"operation": "test", "status": "failed"}
        log_error_with_context(e, context)

    captured = capsys.readouterr()
    assert "ValueError" in captured.err
    assert "Test error" in captured.err
    assert "operation" in captured.err
    assert "status" in captured.err


def test_log_rotation(temp_log_file):
    """Test log rotation functionality."""
    # Set up logging with small rotation size
    setup_logging(
        log_file=temp_log_file, log_level="INFO", rotation="1 KB", retention="1 day"
    )

    # Write enough logs to trigger rotation
    for i in range(100):
        logger.info(f"Test message {i} with some padding to increase size")

    # Check that rotation occurred
    log_dir = Path(temp_log_file).parent
    rotated_files = list(log_dir.glob("*.log.*"))
    assert len(rotated_files) > 0


def test_custom_format(capsys):
    """Test custom log format."""
    custom_format = "{time} | {level} | {message}"
    setup_logging(log_level="INFO", format_string=custom_format)

    logger.info("Test message")

    captured = capsys.readouterr()
    assert "|" in captured.err
    assert "Test message" in captured.err
