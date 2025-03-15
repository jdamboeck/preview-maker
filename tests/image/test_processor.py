"""Tests for the image processor module."""

import threading

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib
import pytest
from PIL import Image

from preview_maker.image.processor import ImageProcessor


@pytest.fixture
def test_image():
    """Create a test image."""
    image = Image.new("RGB", (100, 100), "red")
    return image


@pytest.fixture
def test_image_path(tmp_path, test_image):
    """Save a test image and return its path."""
    image_path = tmp_path / "test.png"
    test_image.save(image_path)
    return image_path


@pytest.fixture
def image_processor():
    """Create an image processor instance."""
    return ImageProcessor()


def test_load_image(image_processor, test_image_path):
    """Test loading an image."""
    event = threading.Event()
    loaded_image = None

    def callback(image):
        nonlocal loaded_image
        loaded_image = image
        event.set()

    image_processor.load_image(test_image_path, callback)
    event.wait(timeout=5)

    assert loaded_image is not None
    assert loaded_image.size == (100, 100)
    assert loaded_image.mode == "RGB"


def test_create_circular_overlay(image_processor, test_image):
    """Test creating a circular overlay."""
    overlay = image_processor.create_circular_overlay(test_image, (50, 50), 20)

    assert overlay is not None
    assert overlay.size == test_image.size
    assert overlay.mode == "RGBA"


def test_draw_overlay_on_surface(image_processor, test_image):
    """Test drawing an overlay on a surface."""
    # Create overlay
    overlay = image_processor.create_circular_overlay(test_image, (50, 50), 20)

    # Create surface
    surface = image_processor.create_cairo_surface(test_image)

    # Draw overlay
    result = image_processor.draw_overlay_on_surface(surface, overlay, (0, 0))
    assert result is not None


def test_load_nonexistent_image(image_processor, tmp_path):
    """Test loading a nonexistent image."""
    event = threading.Event()
    loaded_image = None

    def callback(image):
        nonlocal loaded_image
        loaded_image = image
        event.set()

    image_processor.load_image(tmp_path / "nonexistent.png", callback)
    event.wait(timeout=5)

    assert loaded_image is None


def test_create_overlay_with_invalid_position(image_processor, test_image):
    """Test creating an overlay with invalid position."""
    # Position outside image bounds
    overlay = image_processor.create_circular_overlay(test_image, (200, 200), 20)
    assert overlay is not None  # Should still create overlay, just clipped


def test_create_overlay_with_invalid_radius(image_processor, test_image):
    """Test creating an overlay with invalid radius."""
    # Negative radius should be handled gracefully
    overlay = image_processor.create_circular_overlay(test_image, (50, 50), -10)
    assert overlay is not None  # Should use absolute value or minimum radius


def test_draw_overlay_with_invalid_surface(image_processor, test_image):
    """Test drawing an overlay with an invalid surface."""
    overlay = image_processor.create_circular_overlay(test_image, (50, 50), 20)
    result = image_processor.draw_overlay_on_surface(None, overlay, (0, 0))
    assert result is None  # Should handle invalid surface gracefully
