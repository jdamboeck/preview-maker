"""Tests for the ResponseParser class."""

import pytest

from preview_maker.ai.parser import ResponseParser


@pytest.fixture
def parser():
    """Create a response parser instance."""
    return ResponseParser()


@pytest.fixture
def json_response():
    """Create a sample JSON response."""
    return {
        "raw_response": """
        Here's my analysis of the image:

        ```json
        {
          "highlights": [
            {
              "x": 0.3,
              "y": 0.4,
              "radius": 0.1,
              "description": "A red flower in the foreground"
            },
            {
              "x": 0.7,
              "y": 0.5,
              "radius": 0.15,
              "description": "A butterfly on a leaf"
            }
          ]
        }
        ```
        """
    }


@pytest.fixture
def text_response():
    """Create a sample text response."""
    return {
        "raw_response": """
        Here's my analysis of the image:

        Highlight 1:
        x: 0.3
        y: 0.4
        radius: 0.1
        Description: A red flower in the foreground

        Highlight 2:
        x: 0.7
        y: 0.5
        radius: 0.15
        Description: A butterfly on a leaf
        """
    }


@pytest.fixture
def invalid_response():
    """Create an invalid response."""
    return {
        "raw_response": "I couldn't identify any interesting regions in this image."
    }


def test_parse_json_response(parser, json_response):
    """Test parsing a JSON response."""
    highlights = parser.parse_response(json_response)

    assert highlights is not None
    assert len(highlights) == 2

    assert highlights[0]["x"] == 0.3
    assert highlights[0]["y"] == 0.4
    assert highlights[0]["radius"] == 0.1
    assert highlights[0]["description"] == "A red flower in the foreground"

    assert highlights[1]["x"] == 0.7
    assert highlights[1]["y"] == 0.5
    assert highlights[1]["radius"] == 0.15
    assert highlights[1]["description"] == "A butterfly on a leaf"


def test_parse_text_response(parser, text_response):
    """Test parsing a text response."""
    highlights = parser.parse_response(text_response)

    assert highlights is not None
    assert len(highlights) == 2

    assert highlights[0]["x"] == 0.3
    assert highlights[0]["y"] == 0.4
    assert highlights[0]["radius"] == 0.1
    assert "flower" in highlights[0]["description"]

    assert highlights[1]["x"] == 0.7
    assert highlights[1]["y"] == 0.5
    assert highlights[1]["radius"] == 0.15
    assert "butterfly" in highlights[1]["description"]


def test_parse_invalid_response(parser, invalid_response):
    """Test parsing an invalid response."""
    highlights = parser.parse_response(invalid_response)
    assert highlights is None


def test_normalize_coordinates(parser):
    """Test normalizing coordinates."""
    # Test normalization of coordinates
    assert parser._normalize_coordinate(0.5) == 0.5
    assert parser._normalize_coordinate(2.0) == 1.0
    assert parser._normalize_coordinate(-0.5) == 0.0
    assert parser._normalize_coordinate("0.7") == 0.7

    # Test normalization of radius
    assert parser._normalize_radius(0.2) == 0.2
    assert parser._normalize_radius(0.6) == 0.5
    assert parser._normalize_radius(-0.1) == 0.0
    assert parser._normalize_radius("0.3") == 0.3


def test_convert_to_pixels(parser):
    """Test converting normalized coordinates to pixels."""
    highlights = [
        {"x": 0.5, "y": 0.5, "radius": 0.1, "description": "Center"},
        {"x": 0.0, "y": 0.0, "radius": 0.2, "description": "Top Left"},
    ]

    image_size = (400, 300)
    pixel_highlights = parser.convert_to_pixels(highlights, image_size)

    assert pixel_highlights[0]["x"] == 200
    assert pixel_highlights[0]["y"] == 150
    assert pixel_highlights[0]["radius"] == 30  # min(400, 300) * 0.1
    assert pixel_highlights[0]["description"] == "Center"

    assert pixel_highlights[1]["x"] == 0
    assert pixel_highlights[1]["y"] == 0
    assert pixel_highlights[1]["radius"] == 60  # min(400, 300) * 0.2
    assert pixel_highlights[1]["description"] == "Top Left"


def test_missing_raw_response(parser):
    """Test handling a missing raw_response field."""
    result = parser.parse_response({})
    assert result is None

    result = parser.parse_response(None)
    assert result is None


def test_validate_highlights(parser):
    """Test validating and normalizing highlights."""
    highlights = [
        {"x": 0.3, "y": 0.4, "radius": 0.1, "description": "Valid"},
        {"x": 1.5, "y": -0.5, "radius": 0.8, "description": "Invalid but normalizable"},
        {"y": 0.5, "radius": 0.2, "description": "Missing x"},
        {"x": 0.5, "radius": 0.2, "description": "Missing y"},
        {"x": 0.5, "y": 0.5, "description": "Missing radius"},
    ]

    result = parser._validate_highlights(highlights)

    assert len(result) == 2  # Only the first two are valid after normalization

    assert result[0]["x"] == 0.3
    assert result[0]["y"] == 0.4
    assert result[0]["radius"] == 0.1
    assert result[0]["description"] == "Valid"

    assert result[1]["x"] == 1.0  # Normalized from 1.5
    assert result[1]["y"] == 0.0  # Normalized from -0.5
    assert result[1]["radius"] == 0.5  # Normalized from 0.8
    assert result[1]["description"] == "Invalid but normalizable"
