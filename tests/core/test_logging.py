"""Unit tests for the logging module."""

import os
import tempfile
from pathlib import Path
import pytest
from loguru import logger
from preview_maker.core.logging import setup_logging, log_error_with_context


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
