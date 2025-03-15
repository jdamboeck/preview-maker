"""Tests for the ImageAnalyzer class."""

import os
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from PIL import Image
from preview_maker.ai.analyzer import ImageAnalyzer


@pytest.fixture
def sample_image():
    """Create a sample image for testing."""
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    return img


@pytest.fixture
def analyzer():
    """Create an ImageAnalyzer with a mock client."""
    mock_client = MagicMock()
    return ImageAnalyzer(client=mock_client)


def test_analyzer_init():
    """Test ImageAnalyzer initialization."""
    analyzer = ImageAnalyzer(api_key="test_key", model_name="custom_model")
    assert analyzer._model_name == "custom_model"


@patch("preview_maker.ai.analyzer.genai")
def test_analyzer_default_init(mock_genai):
    """Test ImageAnalyzer default initialization."""
    # Mock the environment variable
    with patch.dict(os.environ, {"GOOGLE_API_KEY": "env_key"}):
        analyzer = ImageAnalyzer()

        # Check if genai.configure was called with the right API key
        mock_genai.configure.assert_called_once_with(api_key="env_key")

        # Check if the model was created with default name
        assert analyzer._model_name.startswith("gemini")


def test_analyze_image(analyzer, sample_image):
    """Test analyze_image method."""
    # Mock the generate_content method to return a response with highlights
    mock_response = MagicMock()
    mock_response.text = """
    ```json
    {
      "highlights": [
        {
          "x": 0.5,
          "y": 0.5,
          "radius": 0.2,
          "description": "Center of the red square"
        }
      ]
    }
    ```
    """
    analyzer._client.generate_content.return_value = mock_response

    # Call the analyze_image method
    highlights = analyzer.analyze_image(sample_image)

    # Check if the client was called with the image
    analyzer._client.generate_content.assert_called_once()

    # Verify the result
    assert highlights is not None
    assert len(highlights) == 1
    assert highlights[0]["x"] == 0.5
    assert highlights[0]["y"] == 0.5
    assert highlights[0]["radius"] == 0.2
    assert highlights[0]["description"] == "Center of the red square"


def test_analyze_image_from_path(analyzer):
    """Test analyze_image_from_path method."""
    # Mock the PIL.Image.open function
    mock_image = MagicMock()

    with patch(
        "preview_maker.ai.analyzer.Image.open", return_value=mock_image
    ) as mock_open:
        # Mock the generate_content method to return a response with highlights
        mock_response = MagicMock()
        mock_response.text = """
        Here's my analysis:
        Highlight 1:
        x: 0.3
        y: 0.4
        radius: 0.1
        Description: A test point
        """
        analyzer._client.generate_content.return_value = mock_response

        # Call the analyze_image_from_path method
        path = Path("/path/to/image.jpg")
        highlights = analyzer.analyze_image_from_path(path)

        # Check if the image was opened
        mock_open.assert_called_once_with(path)

        # Check if the client was called with the image
        analyzer._client.generate_content.assert_called_once()

        # Verify the result
        assert highlights is not None
        assert len(highlights) == 1
        assert highlights[0]["x"] == 0.3
        assert highlights[0]["y"] == 0.4
        assert highlights[0]["radius"] == 0.1
        assert "test point" in highlights[0]["description"]


def test_analyze_error_handling(analyzer, sample_image):
    """Test error handling in analyze_image method."""
    # Mock the generate_content method to raise an exception
    analyzer._client.generate_content.side_effect = Exception("API Error")

    # Call the analyze_image method
    highlights = analyzer.analyze_image(sample_image)

    # Check if the error was handled and None was returned
    assert highlights is None


def test_convert_highlights_to_pixels(analyzer):
    """Test convert_highlights_to_pixels method."""
    # Create sample highlights
    highlights = [
        {"x": 0.5, "y": 0.5, "radius": 0.1, "description": "Center"},
        {"x": 0.0, "y": 0.0, "radius": 0.2, "description": "Top Left"},
    ]

    # Call the method
    image_size = (200, 100)
    pixel_highlights = analyzer.convert_highlights_to_pixels(highlights, image_size)

    # Verify the conversion
    assert pixel_highlights[0]["x"] == 100  # 0.5 * 200
    assert pixel_highlights[0]["y"] == 50  # 0.5 * 100
    assert pixel_highlights[0]["radius"] == 10  # 0.1 * min(200, 100)

    assert pixel_highlights[1]["x"] == 0
    assert pixel_highlights[1]["y"] == 0
    assert pixel_highlights[1]["radius"] == 20  # 0.2 * min(200, 100)


def test_build_prompt(analyzer, sample_image):
    """Test the prompt building functionality."""
    prompt = analyzer._build_prompt(sample_image)

    # Check if the prompt contains required elements
    assert "Analyze this image" in prompt
    assert "highlight areas of interest" in prompt
    assert "JSON" in prompt
    assert "highlights" in prompt
