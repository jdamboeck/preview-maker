#!/usr/bin/env python3
"""
Image processing module for kimono textile analyzer.
Creates highlighted images with circular overlay and zoomed previews.
"""
import os
from PIL import Image, ImageDraw, ImageFilter

# Constants for image quality
PNG_COMPRESSION = 4  # Balanced compression (range 0-9, lower is better quality)
# PIL constants for resampling
HIGH_RESAMPLING = 1  # Image.LANCZOS (1) is highest quality resampling filter

# Default circle sizing parameters
DEFAULT_SELECTION_RATIO = (
    0.1  # Selection circle diameter as percentage of image's shortest dimension
)
DEFAULT_ZOOM_FACTOR = 3.0  # How much to zoom the preview


def create_highlighted_image(
    original_image,
    interesting_area,
    preview_center=None,
    selection_ratio=DEFAULT_SELECTION_RATIO,
    zoom_factor=DEFAULT_ZOOM_FACTOR,
    show_debug_overlay=False,
):
    """
    Create an image with a circular highlight and zoomed preview of the interesting area.

    Args:
        original_image: PIL Image object of the original image
        interesting_area: tuple (x1, y1, x2, y2) coordinates of the interesting area
        preview_center: tuple (x, y) coordinates for the center of the preview circle
        (optional)
        selection_ratio: The size of the selection circle as a ratio of the image's
        shortest dimension (default: 0.1 = 10%)
        zoom_factor: How much to zoom the preview (default: 3.0)
        show_debug_overlay: Whether to draw the original bounding box as a debug overlay

    Returns:
        PIL Image: Processed image with highlight and zoomed preview
    """
    # Validate the interesting area coordinates
    x1, y1, x2, y2 = interesting_area
    width, height = original_image.size

    # Store the original coordinates for debug overlay
    original_box = (x1, y1, x2, y2)

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
    # Ensure we're working in RGBA mode to preserve quality during processing
    if original_image.mode != "RGBA":
        result = original_image.copy().convert("RGBA")
    else:
        result = original_image.copy()

    # Get the interesting area coordinates
    x1, y1, x2, y2 = interesting_area

    # Use floating point division for more accurate center calculation
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    # Convert to integers for drawing functions at the end of calculations
    center_x = int(center_x)
    center_y = int(center_y)

    # Calculate the selection circle size based on the image dimensions
    shortest_dimension = min(width, height)
    highlight_diameter = int(shortest_dimension * selection_ratio)
    highlight_radius = highlight_diameter / 2  # Use floating-point division

    # For drawing functions, we'll convert radius to integer where needed
    int_radius = int(highlight_radius)

    # Create a transparent overlay for dark gray with transparency
    overlay = Image.new("RGBA", result.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    # Draw a semi-transparent dark gray circle
    overlay_draw.ellipse(
        [
            (center_x - int_radius, center_y - int_radius),
            (center_x + int_radius, center_y + int_radius),
        ],
        fill=(50, 50, 50, 160),  # Dark gray with increased opacity
        outline=(255, 120, 0, 230),  # Orange outline to match the connecting line
        width=max(
            1, int(highlight_radius * 0.09)
        ),  # Border width proportional to radius
    )

    # If debug overlay is enabled, draw the original bounding box
    if show_debug_overlay:
        # Draw the original bounding box from Gemini in blue
        ox1, oy1, ox2, oy2 = original_box
        outline_width = max(
            1, int(shortest_dimension * 0.003)
        )  # Proportional to image size
        overlay_draw.rectangle(
            [(ox1, oy1), (ox2, oy2)],
            fill=None,
            outline=(0, 100, 255, 220),  # Blue, semi-transparent
            width=outline_width,
        )

        # Add a small label for the debug box
        text_bg_size = (90, 20)
        text_bg = Image.new("RGBA", text_bg_size, (0, 100, 255, 180))
        overlay.paste(text_bg, (ox1, max(0, oy1 - 20)), text_bg)

        # Add text "API Boundary" next to the bounding box
        overlay_draw.text(
            (ox1 + 5, max(0, oy1 - 18)),
            "API Boundary",
            fill=(255, 255, 255, 255),  # White text
        )

    # Print dimensions for debugging
    print(
        f"DEBUG: Circle diameter = {highlight_radius*2} pixels with proportional border"
    )
    print(
        f"DEBUG: Image dimensions = {width}x{height}, selection ratio = {selection_ratio}"
    )
    if show_debug_overlay:
        print(f"DEBUG: Original bounding box = {original_box}")

    # Apply a slight blur to the overlay for smoother edges
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=0.5))

    # Paste the overlay onto the result
    result = Image.alpha_composite(result, overlay)

    # Create a zoomed view of the interesting part
    zoom_radius = highlight_radius * zoom_factor  # Keep as float initially

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
        # We should extract the region around the magnification center
        # (not the preview center)
        crop_region = original_image.crop(
            (
                max(0, center_x - int_radius),
                max(0, center_y - int_radius),
                min(width, center_x + int_radius),
                min(height, center_y + int_radius),
            )
        )

        # The preview center determines where to place the zoomed preview
        # Calculate the position of the zoomed preview based on the preview center
        zoom_size = int(zoom_radius * 2)  # Convert to int for image operations
        zoom_padding = int(
            max(10, shortest_dimension * 0.01)
        )  # Padding from the edge (proportional)

        # Place the zoomed preview centered on the preview point using floating-point math
        zoom_x = max(0, min(width - zoom_size, int(preview_x - zoom_size / 2)))
        zoom_y = max(0, min(height - zoom_size, int(preview_y - zoom_size / 2)))
    else:
        crop_region = original_image.crop(
            (
                max(0, center_x - int_radius),
                max(0, center_y - int_radius),
                min(width, center_x + int_radius),
                min(height, center_y + int_radius),
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
        zoom_size = int(zoom_radius * 2)  # Convert to int for image operations
        zoom_padding = int(
            max(10, shortest_dimension * 0.01)
        )  # Padding from the edge (proportional)

        if "top" in corner_name:
            zoom_y = zoom_padding
        else:
            zoom_y = height - zoom_size - zoom_padding

        if "left" in corner_name:
            zoom_x = zoom_padding
        else:
            zoom_x = width - zoom_size - zoom_padding

    # Resize for the zoom effect (use LANCZOS instead of BICUBIC for highest quality)
    zoomed = crop_region.resize((zoom_size, zoom_size), resample=HIGH_RESAMPLING)

    # Create a larger mask for antialiasing
    mask_size = zoom_size + 4  # Slightly larger for smooth edges

    # First create a larger mask with blur for antialiasing
    big_mask = Image.new("L", (mask_size, mask_size), 0)
    big_mask_draw = ImageDraw.Draw(big_mask)
    big_mask_draw.ellipse((2, 2, mask_size - 2, mask_size - 2), fill=255)

    # Apply a slight blur for antialiasing edges
    smooth_mask = big_mask.filter(ImageFilter.GaussianBlur(radius=1.5))

    # Resize back to the exact size we need
    mask = smooth_mask.resize((zoom_size, zoom_size), resample=HIGH_RESAMPLING)

    # Create a background for the zoomed preview with slightly rounded corners
    zoom_bg = Image.new("RGBA", (zoom_size, zoom_size), (255, 255, 255, 180))

    # Apply the mask to both the zoomed image and background
    if zoomed.mode != "RGBA":
        zoomed = zoomed.convert("RGBA")
    zoomed.putalpha(mask)
    zoom_bg.putalpha(mask)

    # Ensure result is in RGBA for pasting
    if result.mode != "RGBA":
        result = result.convert("RGBA")

    # Paste the background first
    result.paste(zoom_bg, (zoom_x, zoom_y), zoom_bg)

    # Then paste the zoomed image
    result.paste(zoomed, (zoom_x, zoom_y), zoomed)

    # Draw a border around the zoomed preview with antialiasing
    result_draw = ImageDraw.Draw(result)
    border_color = (255, 120, 0, 255)  # ORANGE outline
    border_width = max(
        5, int(zoom_size * 0.05)
    )  # Border width proportional to zoomed size

    # Draw a slightly blurred rectangle for the border to achieve antialiasing
    border_img = Image.new(
        "RGBA",
        (zoom_size + border_width * 2, zoom_size + border_width * 2),
        (0, 0, 0, 0),
    )
    border_draw = ImageDraw.Draw(border_img)

    # Draw the outer and inner circles for the border
    border_draw.ellipse(
        (0, 0, zoom_size + border_width * 2 - 1, zoom_size + border_width * 2 - 1),
        fill=border_color,
    )
    border_draw.ellipse(
        (
            border_width,
            border_width,
            zoom_size + border_width - 1,
            zoom_size + border_width - 1,
        ),
        fill=(0, 0, 0, 0),
    )

    # Apply blur for smoother edges
    border_img = border_img.filter(ImageFilter.GaussianBlur(radius=0.7))

    # Paste the border image
    result.paste(border_img, (zoom_x - border_width, zoom_y - border_width), border_img)

    # Draw a line connecting the interesting area to the zoomed preview
    if preview_center:
        # Draw a line from the magnification point to the zoomed preview
        line_width = max(2, int(shortest_dimension * 0.003))  # Proportional line width
        result_draw.line(
            [
                (center_x, center_y),
                (int(zoom_x + zoom_size / 2), int(zoom_y + zoom_size / 2)),
            ],
            fill=(255, 120, 0, 255),  # ORANGE line
            width=line_width,
        )
    else:
        line_width = max(2, int(shortest_dimension * 0.003))  # Proportional line width
        result_draw.line(
            [
                (center_x, center_y),
                (int(zoom_x + zoom_size / 2), int(zoom_y + zoom_size / 2)),
            ],
            fill=(255, 120, 0, 255),  # ORANGE line
            width=line_width,
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

    # Get the center of the interesting area using floating point division
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    # Convert to integers at the end of calculation
    center_x = int(center_x)
    center_y = int(center_y)

    # Draw a big red dot with smooth edges - size proportional to image
    shortest_dimension = min(width, height)
    dot_radius = int(shortest_dimension * 0.02)  # 2% of image's shortest dimension

    # Create a separate image for the dot with antialiasing
    dot_img = Image.new("RGBA", (dot_radius * 2 + 4, dot_radius * 2 + 4), (0, 0, 0, 0))
    dot_draw = ImageDraw.Draw(dot_img)
    dot_draw.ellipse(
        [2, 2, dot_radius * 2 + 2, dot_radius * 2 + 2], fill=(255, 0, 0, 255)  # Red
    )
    # Apply blur for antialiasing
    dot_img = dot_img.filter(ImageFilter.GaussianBlur(radius=1.0))

    # Ensure the debug image is in RGBA mode for compositing
    if debug_image.mode != "RGBA":
        debug_image = debug_image.convert("RGBA")

    # Paste the dot onto the debug image
    debug_image.paste(
        dot_img, (center_x - dot_radius - 2, center_y - dot_radius - 2), dot_img
    )

    # Create output paths relative to the input directory
    base_filename = os.path.splitext(os.path.basename(original_path))[0] + ".png"

    # Save in local debug directory
    os.makedirs(debug_dir, exist_ok=True)
    debug_path = os.path.join(debug_dir, f"debug_{base_filename}")
    debug_image.save(debug_path, format="PNG", compress_level=PNG_COMPRESSION)

    # If current_dir exists, also save relative to input
    if current_dir:
        rel_debug_dir = os.path.join(current_dir, "previews", "debug")
        os.makedirs(rel_debug_dir, exist_ok=True)
        rel_debug_path = os.path.join(rel_debug_dir, f"debug_{base_filename}")
        debug_image.save(rel_debug_path, format="PNG", compress_level=PNG_COMPRESSION)
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
    processed_image.save(output_path, format="PNG", compress_level=PNG_COMPRESSION)

    # If current_dir exists, also save relative to input
    if current_dir:
        rel_preview_dir = os.path.join(current_dir, "previews")
        os.makedirs(rel_preview_dir, exist_ok=True)
        rel_output_path = os.path.join(rel_preview_dir, base_filename)
        processed_image.save(
            rel_output_path, format="PNG", compress_level=PNG_COMPRESSION
        )
        return rel_output_path

    return output_path
