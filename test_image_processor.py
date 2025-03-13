#!/usr/bin/env python3
"""
Test script for the image_processor.py module.
"""
import os
import sys
from PIL import Image
import image_processor


def main():
    """Test the image_processor.py module."""
    # Find a JPG image in the current directory
    image_files = [
        f
        for f in os.listdir(".")
        if f.endswith(".jpg") or f.endswith(".jpeg") or f.endswith(".png")
    ]

    if not image_files:
        print("No image files found in the current directory.")
        return 1

    image_path = image_files[0]
    print(f"Using image: {image_path}")

    # Load the image
    image = Image.open(image_path)
    width, height = image.size
    print(f"Image dimensions: {width}x{height}")

    # Define test points
    mag_x, mag_y = width // 3, height // 3
    preview_x, preview_y = width * 2 // 3, height * 2 // 3

    # Create a bounding box around the magnification point
    radius = 128
    x1 = max(0, mag_x - radius)
    y1 = max(0, mag_y - radius)
    x2 = min(width, mag_x + radius)
    y2 = min(height, mag_y + radius)
    interesting_area = (x1, y1, x2, y2)

    print(f"Magnification point: ({mag_x}, {mag_y})")
    print(f"Preview point: ({preview_x}, {preview_y})")
    print(f"Interesting area: {interesting_area}")

    # Test with preview center
    print("\nTesting with preview center...")
    result1 = image_processor.create_highlighted_image(
        image, interesting_area, preview_center=(preview_x, preview_y)
    )
    result1.save("test_with_preview.png")
    print("Saved to test_with_preview.png")

    # Test without preview center
    print("\nTesting without preview center...")
    result2 = image_processor.create_highlighted_image(image, interesting_area)
    result2.save("test_without_preview.png")
    print("Saved to test_without_preview.png")

    return 0


if __name__ == "__main__":
    sys.exit(main())
