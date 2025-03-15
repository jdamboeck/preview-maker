#!/usr/bin/env python3
"""
Image Processing Tests for Preview Maker

This test verifies that the image processing functionality works as expected.
"""
import os
import tempfile
import pytest
from PIL import Image, ImageDraw


def create_test_image(size=(400, 300), color="white"):
    """Create a test image for testing purposes."""
    img = Image.new("RGB", size, color=color)
    draw = ImageDraw.Draw(img)
    # Draw some shapes to make it interesting
    draw.rectangle((50, 50, 150, 150), fill="blue")
    draw.ellipse((200, 100, 300, 200), fill="red")
    return img


def test_create_circular_highlight():
    """Test that we can create a circular highlight overlay."""
    # Create a test image
    original = create_test_image()
    assert original.size == (400, 300)

    # Create a circular highlight
    center = (200, 150)  # Center of the image
    radius = 50

    # Create mask for circular highlight (mask must be the same size as the zoomed area)
    mask = Image.new("L", (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, radius * 2 - 1, radius * 2 - 1), fill=255)

    # Create zoomed version of the selected area
    zoom_factor = 2.0
    x, y = center
    box = (
        int(x - radius / zoom_factor),
        int(y - radius / zoom_factor),
        int(x + radius / zoom_factor),
        int(y + radius / zoom_factor),
    )
    zoomed_area = original.crop(box).resize((radius * 2, radius * 2))

    # Composite the images
    result = original.copy()
    result.paste(zoomed_area, (center[0] - radius, center[1] - radius), mask)

    # Save to a temporary file for visual inspection if needed
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        result.save(tmp.name)
        assert os.path.exists(tmp.name)
        # Clean up
        os.unlink(tmp.name)

    # Verify the result is the same size as the original
    assert result.size == original.size


def test_image_resize():
    """Test that we can resize images."""
    original = create_test_image(size=(800, 600))
    assert original.size == (800, 600)

    # Resize to half size - use simple resize without specifying filter
    # This is compatible with all Pillow versions
    resized = original.resize((400, 300))
    assert resized.size == (400, 300)


def test_image_format_conversion():
    """Test that we can convert between image formats."""
    original = create_test_image()

    # Save as different formats and verify
    formats = ["JPEG", "PNG", "BMP"]
    for fmt in formats:
        with tempfile.NamedTemporaryFile(suffix=f".{fmt.lower()}", delete=False) as tmp:
            original.save(tmp.name, format=fmt)
            assert os.path.exists(tmp.name)

            # Reload and verify
            reloaded = Image.open(tmp.name)
            assert reloaded.format == fmt

            # Clean up
            os.unlink(tmp.name)


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
