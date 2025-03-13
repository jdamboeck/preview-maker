#!/usr/bin/env python3
"""
Generates a test kimono-like pattern image for testing the Kimono Textile Analyzer.
"""
from PIL import Image, ImageDraw, ImageFilter


def generate_test_image():
    """Generate a kimono-like pattern test image."""
    # Image dimensions
    width, height = 800, 1200

    # Create a new image with white background
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    # Draw a kimono-like outline
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
    img = img.filter(ImageFilter.GaussianBlur(radius=1))

    # Save the image
    output_path = "sample_kimono.jpg"
    img.save(output_path, quality=95)
    print(f"Generated test kimono image at {output_path}")
    return output_path


if __name__ == "__main__":
    SAMPLE_PATH = generate_test_image()
    print("\nYou can now run the Kimono Textile Analyzer with this sample image:")
    print("1. Run the main application: python3 kimono_analyzer.py")
    print("2. Drag and drop the sample image into the application window")
