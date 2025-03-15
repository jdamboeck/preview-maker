"""Tests for the ImageProcessor component.

This module contains tests for the ImageProcessor class, which is
responsible for loading, transforming, and creating overlays for images.
"""

import os
import unittest
from unittest import mock
from pathlib import Path
import tempfile

import pytest
from PIL import Image

from preview_maker.image.processor import ImageProcessor


class TestImageProcessor:
    """Tests for the ImageProcessor class."""

    @pytest.fixture
    def processor(self):
        """Create an ImageProcessor instance for testing."""
        return ImageProcessor()

    @pytest.fixture
    def test_image(self):
        """Create a test image for testing."""
        # Create a simple test image
        image = Image.new("RGB", (100, 100), color="white")
        return image

    @pytest.fixture
    def temp_image_path(self):
        """Create a temporary image file for testing."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            # Create a simple test image and save it
            image = Image.new("RGB", (100, 100), color="white")
            image.save(tmp.name)
            tmp_path = tmp.name

        # Return the path and ensure cleanup after the test
        yield tmp_path
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    def test_init(self, processor):
        """Test that the processor initializes correctly."""
        assert processor is not None

    def test_load_image_sync(self, processor, temp_image_path):
        """Test synchronous image loading."""
        # Load the image
        image = processor.load_image_sync(temp_image_path)

        # Check that we got an image back
        assert image is not None
        assert isinstance(image, Image.Image)
        assert image.size == (100, 100)

    def test_load_image_async(self, processor, temp_image_path):
        """Test asynchronous image loading."""
        # Create a mock callback
        mock_callback = mock.MagicMock()

        # Load the image
        processor.load_image(temp_image_path, mock_callback)

        # Wait a bit for the thread to complete
        import time

        time.sleep(0.1)

        # Check that the callback was called with an image
        mock_callback.assert_called_once()
        image = mock_callback.call_args[0][0]
        assert image is not None
        assert isinstance(image, Image.Image)
        assert image.size == (100, 100)

    def test_create_circular_overlay(self, processor):
        """Test creating a circular overlay."""
        # Create an overlay
        width, height = 200, 200
        x, y, radius = 100, 100, 50
        color = "#ff0000"  # Red

        overlay = processor.create_circular_overlay(width, height, x, y, radius, color)

        # Check that we got an image back
        assert overlay is not None
        assert isinstance(overlay, Image.Image)
        assert overlay.size == (width, height)
        assert overlay.mode == "RGBA"  # Should be transparent

        # Check that the center pixel is the right color
        center_pixel = overlay.getpixel((x, y))
        assert center_pixel[0] > 200  # Red component should be high
        assert center_pixel[3] > 0  # Alpha should be non-zero

        # Check that a corner pixel is transparent
        corner_pixel = overlay.getpixel((0, 0))
        assert corner_pixel[3] == 0  # Alpha should be zero (transparent)

    def test_resize_image(self, processor, test_image):
        """Test resizing an image."""
        # Resize the image
        new_size = (50, 50)
        resized = processor.resize_image(test_image, new_size)

        # Check that we got an image back with the right size
        assert resized is not None
        assert isinstance(resized, Image.Image)
        assert resized.size == new_size

    def test_crop_image(self, processor, test_image):
        """Test cropping an image."""
        # Crop the image
        box = (25, 25, 75, 75)  # left, top, right, bottom
        cropped = processor.crop_image(test_image, box)

        # Check that we got an image back with the right size
        assert cropped is not None
        assert isinstance(cropped, Image.Image)
        assert cropped.size == (50, 50)  # 75-25 = 50
