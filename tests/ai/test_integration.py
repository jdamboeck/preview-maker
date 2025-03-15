"""Tests for the AI integration module."""

import pytest
from unittest.mock import MagicMock, patch, ANY
from pathlib import Path

from PIL import Image
from preview_maker.ai.integration import AIPreviewGenerator


@pytest.fixture
def sample_image():
    """Create a sample image for testing."""
    img = Image.new("RGB", (200, 100), color=(255, 255, 255))
    return img


@pytest.fixture
def mock_analyzer():
    """Create a mock ImageAnalyzer."""
    mock = MagicMock()

    # Set up the analyze_image method to return some highlights
    mock.analyze_image.return_value = [
        {"x": 0.25, "y": 0.5, "radius": 0.1, "description": "Point 1"},
        {"x": 0.75, "y": 0.5, "radius": 0.15, "description": "Point 2"},
    ]

    # Set up the convert_highlights_to_pixels method
    mock.convert_highlights_to_pixels.return_value = [
        {"x": 50, "y": 50, "radius": 10, "description": "Point 1"},
        {"x": 150, "y": 50, "radius": 15, "description": "Point 2"},
    ]

    return mock


@pytest.fixture
def mock_processor():
    """Create a mock ImageProcessor."""
    mock = MagicMock()

    # Set up the load_image method to call the callback with a sample image
    def mock_load_image(path, callback):
        img = Image.new("RGB", (200, 100), color=(255, 255, 255))
        callback(img)

    mock.load_image.side_effect = mock_load_image

    # Set up the create_circular_overlay method to return a full-sized overlay
    def mock_create_overlay(image, position, radius):
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        return overlay

    mock.create_circular_overlay.side_effect = mock_create_overlay

    return mock


@pytest.fixture
def generator(mock_analyzer, mock_processor):
    """Create an AIPreviewGenerator with mock components."""
    generator = AIPreviewGenerator(api_key="test_key")
    generator.analyzer = mock_analyzer
    generator.processor = mock_processor
    return generator


@patch("preview_maker.ai.integration.Path.exists")
def test_generate_preview(mock_exists, generator, sample_image):
    """Test the generate_preview method."""
    # Set up the path to exist
    mock_exists.return_value = True

    # Call the method
    result = generator.generate_preview("test_image.jpg")

    # Verify the result
    assert result is not None
    assert isinstance(result, Image.Image)

    # Check if the analyzer was called
    generator.analyzer.analyze_image.assert_called_once()
    generator.analyzer.convert_highlights_to_pixels.assert_called_once()

    # Check if the processor was called
    generator.processor.load_image.assert_called_once()
    assert generator.processor.create_circular_overlay.call_count == 2


@patch("preview_maker.ai.integration.Path.exists")
def test_generate_preview_with_output(mock_exists, generator, tmp_path):
    """Test the generate_preview method with output path."""
    # Set up the path to exist
    mock_exists.return_value = True

    # Create a temporary output path
    output_path = tmp_path / "preview.jpg"

    # Call the method
    with patch.object(Image.Image, "save") as mock_save:
        result = generator.generate_preview("test_image.jpg", output_path)

        # Verify the result
        assert result is not None
        assert isinstance(result, Image.Image)

        # Check if save was called
        mock_save.assert_called_once_with(output_path)


@patch("preview_maker.ai.integration.Path.exists")
def test_nonexistent_image_path(mock_exists, generator):
    """Test behavior with a nonexistent image path."""
    # Set up the path to not exist
    mock_exists.return_value = False

    # Call the method
    result = generator.generate_preview("nonexistent.jpg")

    # Verify the result
    assert result is None

    # Check that the processor was not called
    generator.processor.load_image.assert_not_called()


def test_no_highlights_found(generator):
    """Test behavior when no highlights are found."""
    # Set up the analyzer to return no highlights
    generator.analyzer.analyze_image.return_value = None

    # Set up the path to exist
    with patch("preview_maker.ai.integration.Path.exists", return_value=True):
        # Call the method
        result = generator.generate_preview("test_image.jpg")

        # Verify the result
        assert result is None


def test_load_image_sync(generator):
    """Test the _load_image_sync method."""
    # Create a sample image path
    image_path = Path("test_image.jpg")

    # Call the method
    result = generator._load_image_sync(image_path)

    # Verify the result
    assert result is not None
    assert isinstance(result, Image.Image)

    # Check if the processor was called
    generator.processor.load_image.assert_called_once_with(str(image_path), ANY)


def test_create_preview_with_overlays(generator, sample_image):
    """Test the _create_preview_with_overlays method."""
    # Create sample highlights
    highlights = [
        {"x": 50, "y": 50, "radius": 10, "description": "Point 1"},
        {"x": 150, "y": 50, "radius": 15, "description": "Point 2"},
    ]

    # Mock alpha_composite to avoid image size issues
    with patch(
        "PIL.Image.alpha_composite", return_value=sample_image.copy().convert("RGBA")
    ):
        # Call the method
        result = generator._create_preview_with_overlays(sample_image, highlights)

        # Verify the result
        assert result is not None
        assert isinstance(result, Image.Image)

        # Check if create_circular_overlay was called correctly
        assert generator.processor.create_circular_overlay.call_count == 2
        generator.processor.create_circular_overlay.assert_any_call(ANY, (50, 50), 10)
        generator.processor.create_circular_overlay.assert_any_call(ANY, (150, 50), 15)
