"""Tests for the AI integration module."""

import pytest
from unittest.mock import MagicMock, patch, ANY
from pathlib import Path

from PIL import Image
from preview_maker.ai.integration import AIPreviewGenerator
from preview_maker.ai.analyzer import ImageAnalyzer


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


class TestAIPreviewGenerator:
    """Tests for the AIPreviewGenerator class."""

    @pytest.fixture
    def mock_api_key(self):
        """Provide a mock API key for testing."""
        return "mock_api_key_for_testing"

    @pytest.fixture
    def mock_analyzer(self, mock_api_key):
        """Create a mock ImageAnalyzer."""
        analyzer = MagicMock(spec=ImageAnalyzer)
        # Mock the analyze_image method to return a sample result
        analyzer.analyze_image.return_value = [
            {"x": 100, "y": 100, "radius": 50, "confidence": 0.9}
        ]
        return analyzer

    @pytest.fixture
    def mock_image_processor(self):
        """Create a mock ImageProcessor."""
        processor = MagicMock()
        # Mock the create_circular_overlay method to return a sample overlay
        processor.create_circular_overlay.return_value = Image.new(
            "RGBA", (200, 200), (0, 0, 0, 0)
        )
        return processor

    @pytest.fixture
    def test_image_path(self, tmp_path):
        """Create a test image file."""
        image_path = tmp_path / "test_image.jpg"
        # Create a simple test image
        image = Image.new("RGB", (200, 200), "white")
        image.save(image_path)
        return image_path

    @pytest.fixture
    def preview_generator(self, mock_api_key, mock_analyzer, mock_image_processor):
        """Create an AIPreviewGenerator with mocked dependencies."""
        generator = AIPreviewGenerator(api_key=mock_api_key)
        # Replace the real analyzer with our mock
        generator.analyzer = mock_analyzer
        # Replace the real image processor with our mock
        generator.processor = mock_image_processor
        return generator

    def test_init(self, mock_api_key):
        """Test that the generator initializes correctly."""
        generator = AIPreviewGenerator(api_key=mock_api_key)
        assert generator.api_key == mock_api_key
        assert generator.analyzer is not None
        assert generator.processor is not None

    def test_generate_preview(
        self, preview_generator, test_image_path, mock_image_processor
    ):
        """Test generating a preview with mocked components."""
        # Mock the load_image_sync method to return a test image
        test_image = Image.new("RGB", (200, 200), "white")
        mock_image_processor.load_image_sync.return_value = test_image

        # Make sure we're using the right mock in the preview generator
        # This is needed because the fixture creates a separate instance
        preview_generator.processor = mock_image_processor

        # Set up the analyzer to return a highlight
        preview_generator.analyzer.analyze_image.return_value = [
            {"x": 0.5, "y": 0.5, "radius": 0.1}
        ]

        # Set up the convert_highlights_to_pixels method
        preview_generator.analyzer.convert_highlights_to_pixels.return_value = [
            {"x": 100, "y": 100, "radius": 20}
        ]

        # Generate a preview
        result = preview_generator.generate_preview(test_image_path)

        # Check that the analyzer was called
        preview_generator.analyzer.analyze_image.assert_called_once()

        # Check that the image processor was used to create an overlay
        mock_image_processor.create_circular_overlay.assert_called_once()

        # Check that we got a result
        assert result is not None

    def test_generate_preview_with_no_highlights(
        self, preview_generator, test_image_path, mock_image_processor
    ):
        """Test generating a preview with no highlights found."""
        # Mock the load_image_sync method to return a test image
        test_image = Image.new("RGB", (200, 200), "white")
        mock_image_processor.load_image_sync.return_value = test_image

        # Mock the analyzer to return no highlights
        preview_generator.analyzer.analyze_image.return_value = []

        # Make sure we're using the right mock in the preview generator
        preview_generator.processor = mock_image_processor

        # Generate a preview
        result = preview_generator.generate_preview(test_image_path)

        # Check that the analyzer was called
        preview_generator.analyzer.analyze_image.assert_called_once()

        # Check that we got no result (None)
        assert result is None

    def test_generate_preview_with_invalid_image(
        self, preview_generator, test_image_path, mock_image_processor
    ):
        """Test generating a preview with an invalid image."""
        # Mock the load_image_sync method to return None
        mock_image_processor.load_image_sync.return_value = None

        # Make sure we're using the right mock in the preview generator
        preview_generator.processor = mock_image_processor

        # Generate a preview
        result = preview_generator.generate_preview(test_image_path)

        # Check that the analyzer was not called
        preview_generator.analyzer.analyze_image.assert_not_called()

        # Check that we got no result (None)
        assert result is None
