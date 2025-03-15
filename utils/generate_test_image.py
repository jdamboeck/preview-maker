#!/usr/bin/env python3
"""
Generates a test pattern image for testing the Preview Maker.
"""
from PIL import Image, ImageDraw, ImageFilter
import os


def generate_test_image():
    """Generate a test image with interesting details."""
    # Image dimensions
    width, height = 800, 1200

    # Create a new image with white background
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    # Draw a pattern background
    # Main body
    draw.rectangle(
        [(width // 4, height // 8), (width * 3 // 4, height * 7 // 8)],
        outline="black",
        width=3,
        fill=(240, 230, 225),
    )

    # Sleeves
    sleeve_width = width // 6
    sleeve_start_y = height // 5
    sleeve_length = height // 3

    # Left sleeve
    draw.rectangle(
        [
            (width // 4 - sleeve_width, sleeve_start_y),
            (width // 4, sleeve_start_y + sleeve_length),
        ],
        outline="black",
        width=3,
        fill=(240, 230, 225),
    )

    # Right sleeve
    draw.rectangle(
        [
            (width * 3 // 4, sleeve_start_y),
            (width * 3 // 4 + sleeve_width, sleeve_start_y + sleeve_length),
        ],
        outline="black",
        width=3,
        fill=(240, 230, 225),
    )

    # Draw some decorative patterns
    # Create a flower pattern area (this will be our "interesting textile part")
    flower_center_x = width // 2
    flower_center_y = height // 3
    flower_radius = 100

    # Draw flower petals
    colors = [
        (255, 50, 50),
        (255, 150, 50),
        (255, 230, 50),
        (50, 200, 50),
        (50, 100, 255),
        (150, 50, 200),
    ]

    for i in range(12):
        angle = i * 30
        x = flower_center_x + int(
            flower_radius
            * 0.6
            * (i % 2 + 1)
            * ((angle % 90) / 45 if angle % 90 < 45 else (90 - angle % 90) / 45)
        )
        y = flower_center_y + int(
            flower_radius
            * 0.6
            * (i % 2 + 1)
            * ((angle % 90) / 45 if angle % 90 >= 45 else (90 - angle % 90) / 45)
        )

        petal_size = 30 + i % 3 * 10
        color = colors[i % len(colors)]

        draw.ellipse(
            (x - petal_size, y - petal_size, x + petal_size, y + petal_size),
            fill=color,
            outline="black",
        )

    # Draw the flower center
    draw.ellipse(
        (
            flower_center_x - 30,
            flower_center_y - 30,
            flower_center_x + 30,
            flower_center_y + 30,
        ),
        fill="gold",
        outline="black",
    )

    # Add some regular geometric patterns in the lower part
    for i in range(10):
        y_pos = height * 1 // 2 + i * 50
        for j in range(8):
            x_pos = width // 4 + 20 + j * 70
            if (i + j) % 2 == 0:
                draw.rectangle(
                    (x_pos, y_pos, x_pos + 40, y_pos + 40),
                    fill=(200, 200, 255),
                    outline="black",
                )
            else:
                draw.ellipse(
                    (x_pos, y_pos, x_pos + 40, y_pos + 40),
                    fill=(255, 200, 200),
                    outline="black",
                )

    # Apply a slight blur to soften the image
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))

    # Create data directory if it doesn't exist
    test_dir = "data"
    os.makedirs(test_dir, exist_ok=True)

    output_path = os.path.join(test_dir, "test_pattern.png")
    img.save(output_path)
    print(f"Test image saved to {output_path}")
    return output_path


if __name__ == "__main__":
    generate_test_image()
