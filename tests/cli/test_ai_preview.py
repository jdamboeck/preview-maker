"""Tests for the AI preview CLI tool."""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from PIL import Image
from preview_maker.cli.ai_preview import main, process_image, process_directory


@pytest.fixture
def sample_image():
    """Create a sample image for testing."""
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    return img


@pytest.fixture
def mock_generator():
    """Create a mock AIPreviewGenerator."""
    mock = MagicMock()
    mock.generate_preview.return_value = Image.new("RGB", (100, 100))
    return mock


def test_process_image(mock_generator, tmp_path, sample_image):
    """Test processing a single image."""
    # Create a test image file
    input_path = tmp_path / "test.jpg"
    sample_image.save(input_path)

    # Process the image
    result = process_image(mock_generator, input_path, tmp_path)

    # Check the result
    assert result is True
    mock_generator.generate_preview.assert_called_once()

    # Check that the output path was constructed correctly
    expected_output = tmp_path / "test_preview.jpg"
    mock_generator.generate_preview.assert_called_with(input_path, expected_output)


def test_process_directory(mock_generator, tmp_path, sample_image):
    """Test processing a directory of images."""
    # Create test image files
    for i in range(3):
        input_path = tmp_path / f"test{i}.jpg"
        sample_image.save(input_path)

    # Create a non-image file
    (tmp_path / "not_an_image.txt").write_text("This is not an image")

    # Create output directory
    output_dir = tmp_path / "output"

    # Process the directory
    success_count, total_count = process_directory(mock_generator, tmp_path, output_dir)

    # Check the results
    assert success_count == 3
    assert total_count == 3
    assert mock_generator.generate_preview.call_count == 3
    assert output_dir.exists()


def test_process_image_failure(mock_generator, tmp_path):
    """Test handling of image processing failure."""
    # Set up the mock to return None (failure)
    mock_generator.generate_preview.return_value = None

    # Create a test image path
    input_path = tmp_path / "test.jpg"
    input_path.write_bytes(b"not a real image")

    # Process the image
    result = process_image(mock_generator, input_path, tmp_path)

    # Check the result
    assert result is False


@patch("preview_maker.cli.ai_preview.AIPreviewGenerator")
@patch("preview_maker.cli.ai_preview.setup_logging")
@patch("preview_maker.cli.ai_preview.process_image")
def test_main_single_file(
    mock_process_image, mock_setup_logging, mock_generator_class, tmp_path
):
    """Test main function with a single file."""
    # Set up the mock
    mock_generator = MagicMock()
    mock_generator_class.return_value = mock_generator
    mock_process_image.return_value = True

    # Create a test file
    test_file = tmp_path / "test.jpg"
    test_file.touch()

    # Set up command line arguments
    test_args = ["ai_preview.py", str(test_file), "-k", "test_api_key"]

    with patch.object(sys, "argv", test_args):
        with patch.object(Path, "exists", return_value=True):
            # Call main
            result = main()

            # Check the result
            assert result == 0
            mock_setup_logging.assert_called_once()
            mock_generator_class.assert_called_once_with(
                api_key="test_api_key", model_name="gemini-pro-vision"
            )
            mock_process_image.assert_called_once()


@patch("preview_maker.cli.ai_preview.AIPreviewGenerator")
@patch("preview_maker.cli.ai_preview.setup_logging")
@patch("preview_maker.cli.ai_preview.process_directory")
def test_main_directory(
    mock_process_directory, mock_setup_logging, mock_generator_class, tmp_path
):
    """Test main function with a directory."""
    # Set up the mock
    mock_generator = MagicMock()
    mock_generator_class.return_value = mock_generator
    mock_process_directory.return_value = (3, 3)  # All successful

    # Create a test directory
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    # Set up command line arguments
    test_args = [
        "ai_preview.py",
        str(test_dir),
        "-k",
        "test_api_key",
        "-o",
        str(tmp_path / "output"),
    ]

    with patch.object(sys, "argv", test_args):
        with patch.object(Path, "exists", return_value=True):
            # Call main
            result = main()

            # Check the result
            assert result == 0
            mock_setup_logging.assert_called_once()
            mock_generator_class.assert_called_once_with(
                api_key="test_api_key", model_name="gemini-pro-vision"
            )
            mock_process_directory.assert_called_once()


@patch("preview_maker.cli.ai_preview.AIPreviewGenerator")
@patch("preview_maker.cli.ai_preview.setup_logging")
def test_main_no_api_key(mock_setup_logging, mock_generator_class):
    """Test main function with no API key."""
    # Set up command line arguments
    test_args = ["ai_preview.py", "test.jpg"]

    # Clear environment variable
    with patch.dict(os.environ, {"GOOGLE_API_KEY": ""}, clear=True):
        with patch.object(sys, "argv", test_args):
            # Call main
            result = main()

            # Check the result
            assert result == 1
            mock_setup_logging.assert_called_once()
            mock_generator_class.assert_not_called()


@patch("preview_maker.cli.ai_preview.AIPreviewGenerator")
@patch("preview_maker.cli.ai_preview.setup_logging")
def test_main_nonexistent_path(mock_setup_logging, mock_generator_class):
    """Test main function with a nonexistent path."""
    # Set up command line arguments
    test_args = ["ai_preview.py", "/nonexistent/path", "-k", "test_api_key"]

    with patch.object(sys, "argv", test_args):
        with patch.object(Path, "exists", return_value=False):
            # Call main
            result = main()

            # Check the result
            assert result == 1
            mock_setup_logging.assert_called_once()
            mock_generator_class.assert_called_once()
