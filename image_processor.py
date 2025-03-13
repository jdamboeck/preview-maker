#!/usr/bin/env python3
"""
Image processing module for kimono textile analyzer.
Creates highlighted images with circular overlay and zoomed previews.
"""
import os
from PIL import Image, ImageDraw


def create_highlighted_image(original_image, interesting_area, preview_center=None):
    """
    Create an image with a circular highlight and zoomed preview of the interesting area.

    Args:
        original_image: PIL Image object of the original image
        interesting_area: tuple (x1, y1, x2, y2) coordinates of the interesting area
        preview_center: tuple (x, y) coordinates for the center of the preview circle (optional)

    Returns:
        PIL Image: Processed image with highlight and zoomed preview
    """
    # Validate the interesting area coordinates
    x1, y1, x2, y2 = interesting_area
    width, height = original_image.size

    # Ensure coordinates are within image bounds
    x1 = max(0, min(x1, width - 1))
    y1 = max(0, min(y1, height - 1))
    x2 = max(0, min(x2, width))
    y2 = max(0, min(y2, height))

    # Ensure right > left and bottom > top
    if x2 <= x1:
        x1, x2 = x2 - 1, x1 + 1
    if y2 <= y1:
        y1, y2 = y2 - 1, y1 + 1

    # Update the interesting area with validated coordinates
    interesting_area = (x1, y1, x2, y2)

    # Make a copy of the original image
    result = original_image.copy()
    draw = ImageDraw.Draw(result)

    # Get the interesting area coordinates
    x1, y1, x2, y2 = interesting_area
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2

    # Set the circle to exactly 256 pixels in diameter
    highlight_radius = 128  # Radius for a 256 pixel diameter circle

    # Create a transparent overlay for dark gray with transparency
    overlay = Image.new("RGBA", result.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    # Draw a semi-transparent dark gray circle
    overlay_draw.ellipse(
        [
            (center_x - highlight_radius, center_y - highlight_radius),
            (center_x + highlight_radius, center_y + highlight_radius),
        ],
        fill=(50, 50, 50, 160),  # Dark gray with increased opacity
        outline=(255, 120, 0, 230),  # Orange outline to match the connecting line
        width=12,  # Increased border width
    )

    # Print dimensions for debugging
    print(f"DEBUG: Circle diameter = {highlight_radius*2} pixels with 10px border")

    # Paste the overlay onto the result
    if result.mode != "RGBA":
        result = result.convert("RGBA")
    result = Image.alpha_composite(result, overlay)

    # Create a zoomed view of the interesting part
    zoom_factor = 3.0  # 3x zoom as requested
    zoom_radius = int(highlight_radius * zoom_factor)

    # Calculate the position for the zoomed preview
    # Place it in the corner that's furthest from the interesting area
    width, height = original_image.size

    # Use the provided preview center if available
    if preview_center:
        preview_x, preview_y = preview_center
        # Ensure preview center is within image bounds
        preview_x = max(0, min(preview_x, width - 1))
        preview_y = max(0, min(preview_y, height - 1))
        print(f"Using provided preview center: ({preview_x}, {preview_y})")

        # Use the preview center for determining the corner
        center_to_use = preview_center
    else:
        # Use the magnification center for determining the corner
        center_to_use = (center_x, center_y)

    # Extract the region to zoom
    if preview_center:
        preview_x, preview_y = preview_center
        # We should extract the region around the magnification center (not the preview center)
        crop_region = original_image.crop(
            (
                max(0, center_x - highlight_radius),
                max(0, center_y - highlight_radius),
                min(width, center_x + highlight_radius),
                min(height, center_y + highlight_radius),
            )
        )

        # The preview center determines where to place the zoomed preview
        # Calculate the position of the zoomed preview based on the preview center
        zoom_size = zoom_radius * 2
        zoom_padding = 10  # Padding from the edge

        # Place the zoomed preview centered on the preview point
        zoom_x = max(0, min(width - zoom_size, preview_x - zoom_size // 2))
        zoom_y = max(0, min(height - zoom_size, preview_y - zoom_size // 2))
    else:
        crop_region = original_image.crop(
            (
                max(0, center_x - highlight_radius),
                max(0, center_y - highlight_radius),
                min(width, center_x + highlight_radius),
                min(height, center_y + highlight_radius),
            )
        )

        # Determine which corner to put the zoomed preview in
        corners = [
            (0, 0, "top-left"),
            (width, 0, "top-right"),
            (0, height, "bottom-left"),
            (width, height, "bottom-right"),
        ]

        # Find the corner furthest from the center point
        furthest_corner = max(
            corners,
            key=lambda c: (c[0] - center_to_use[0]) ** 2
            + (c[1] - center_to_use[1]) ** 2,
        )
        _, _, corner_name = furthest_corner

        # Calculate the position of the zoomed preview
        zoom_size = zoom_radius * 2
        zoom_padding = 10  # Padding from the edge

        if "top" in corner_name:
            zoom_y = zoom_padding
        else:
            zoom_y = height - zoom_size - zoom_padding

        if "left" in corner_name:
            zoom_x = zoom_padding
        else:
            zoom_x = width - zoom_size - zoom_padding

    # Resize for the zoom effect (use BICUBIC instead of LANCZOS)
    zoomed = crop_region.resize((zoom_size, zoom_size), resample=3)  # 3 = BICUBIC

    # Convert result back to RGB if needed for compatibility
    if result.mode == "RGBA":
        rgb_result = Image.new("RGB", result.size, (255, 255, 255))
        rgb_result.paste(result, mask=result.split()[3])  # Use alpha channel as mask
        result = rgb_result

    # Apply a circular mask to the zoomed preview
    mask = Image.new("L", (zoom_size, zoom_size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, zoom_size, zoom_size), fill=255)

    # Create a background for the zoomed preview
    zoom_bg = Image.new("RGBA", (zoom_size, zoom_size), (255, 255, 255, 180))

    # Apply the mask to both the zoomed image and background
    zoomed = zoomed.convert("RGBA")
    zoomed.putalpha(mask)
    zoom_bg.putalpha(mask)

    # Convert result back to RGBA for pasting
    result = result.convert("RGBA")

    # Paste the background first
    result.paste(zoom_bg, (zoom_x, zoom_y), zoom_bg)

    # Then paste the zoomed image
    result.paste(zoomed, (zoom_x, zoom_y), zoomed)

    # Draw a border around the zoomed preview
    draw.rectangle(
        [(zoom_x, zoom_y), (zoom_x + zoom_size, zoom_y + zoom_size)],
        outline=(255, 120, 0, 255),  # ORANGE outline
        width=10,  # 10 pixels width
    )

    # Draw a line connecting the interesting area to the zoomed preview
    if preview_center:
        # Draw a line from the magnification point (center_x, center_y) to the zoomed preview
        draw.line(
            [
                (center_x, center_y),
                (zoom_x + zoom_size // 2, zoom_y + zoom_size // 2),
            ],
            fill=(255, 120, 0, 255),  # ORANGE line
            width=4,  # Thicker line
        )
    else:
        draw.line(
            [(center_x, center_y), (zoom_x + zoom_size // 2, zoom_y + zoom_size // 2)],
            fill=(255, 120, 0, 255),  # ORANGE line
            width=4,  # Thicker line
        )

    return result


def save_debug_image(
    image, interesting_area, original_path, debug_dir="previews/debug", current_dir=None
):
    """
    Save a debug image with a red dot at the most interesting spot.

    Args:
        image: PIL Image object
        interesting_area: tuple (x1, y1, x2, y2) coordinates of the interesting area
        original_path: Path to the original image
        debug_dir: Directory to save debug images
        current_dir: Current working directory

    Returns:
        str: Path to the saved debug image
    """
    debug_image = image.copy()
    draw = ImageDraw.Draw(debug_image)

    # Validate the interesting area coordinates
    x1, y1, x2, y2 = interesting_area
    width, height = image.size

    # Ensure coordinates are within image bounds
    x1 = max(0, min(x1, width - 1))
    y1 = max(0, min(y1, height - 1))
    x2 = max(0, min(x2, width))
    y2 = max(0, min(y2, height))

    # Ensure right > left and bottom > top
    if x2 <= x1:
        x1, x2 = x2 - 1, x1 + 1
    if y2 <= y1:
        y1, y2 = y2 - 1, y1 + 1

    # Update the interesting area with validated coordinates
    interesting_area = (x1, y1, x2, y2)

    # Get the center of the interesting area
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2

    # Draw a big red dot
    dot_radius = 20
    draw.ellipse(
        [
            (center_x - dot_radius, center_y - dot_radius),
            (center_x + dot_radius, center_y + dot_radius),
        ],
        fill="red",
    )

    # Create output paths relative to the input directory
    base_filename = os.path.splitext(os.path.basename(original_path))[0] + ".png"

    # Save in local debug directory
    os.makedirs(debug_dir, exist_ok=True)
    debug_path = os.path.join(debug_dir, f"debug_{base_filename}")
    debug_image.save(debug_path, format="PNG", compress_level=3)

    # If current_dir exists, also save relative to input
    if current_dir:
        rel_debug_dir = os.path.join(current_dir, "previews", "debug")
        os.makedirs(rel_debug_dir, exist_ok=True)
        rel_debug_path = os.path.join(rel_debug_dir, f"debug_{base_filename}")
        debug_image.save(rel_debug_path, format="PNG", compress_level=3)
        return rel_debug_path

    return debug_path


def save_processed_image(
    processed_image, original_path, output_dir="previews", current_dir=None
):
    """
    Save the processed image with the original filename but as PNG.

    Args:
        processed_image: PIL Image object of the processed image
        original_path: Path to the original image
        output_dir: Directory to save processed images
        current_dir: Current working directory

    Returns:
        str: Path to the saved processed image
    """
    if not processed_image:
        return None

    # Get the base filename but change extension to .png
    base_filename = os.path.splitext(os.path.basename(original_path))[0] + ".png"

    # Save in local previews directory
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, base_filename)
    processed_image.save(output_path, format="PNG", compress_level=3)

    # If current_dir exists, also save relative to input
    if current_dir:
        rel_preview_dir = os.path.join(current_dir, "previews")
        os.makedirs(rel_preview_dir, exist_ok=True)
        rel_output_path = os.path.join(rel_preview_dir, base_filename)
        processed_image.save(rel_output_path, format="PNG", compress_level=3)
        return rel_output_path

    return output_path
