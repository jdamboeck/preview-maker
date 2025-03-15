#!/usr/bin/env python3
"""
Test script for the image_processor.py module.
"""
import os
import sys

# Add src directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from PIL import Image
import image_processor


def main():
    """Test the image_processor.py module."""
    # Find a test image in the data directory
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

    if not os.path.exists(data_dir):
        print(f"Data directory not found: {data_dir}")
        return 1

    image_files = [
        f for f in os.listdir(data_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    if not image_files:
        print(f"No image files found in {data_dir}")
        return 1

    image_path = os.path.join(data_dir, image_files[0])
    print(f"Using image: {image_path}")

    # Load the image
    image = Image.open(image_path)
    width, height = image.size
    print(f"Image dimensions: {width}x{height}")

    # Define a test area (middle 25% of the image)
    x1 = width // 4
    y1 = height // 4
    x2 = width * 3 // 4
    y2 = height * 3 // 4
    test_area = (x1, y1, x2, y2)

    # Process with the image processor
    processed = image_processor.create_highlighted_image(
        image, test_area, selection_ratio=0.12, zoom_factor=3, show_debug_overlay=True
    )

    # Save the processed image to a test output
    test_output_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "tests", "test_data"
    )
    os.makedirs(test_output_dir, exist_ok=True)

    output_path = os.path.join(test_output_dir, "test_output.png")
    processed.save(output_path)
    print(f"Saved test output to: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
