#!/usr/bin/env python3
"""
Gemini AI analyzer for kimono textiles.
Identifies interesting patterns in textile images.
"""
import os
import re
from io import BytesIO

# Import configuration
import config

# Try to import Google Generative AI
try:
    import google.generativeai as genai

    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print(
        "WARNING: google-generativeai package not installed. "
        "Run 'pip install google-generativeai' to enable AI features."
    )

# Load Gemini API key from environment variable with help from config module
config.load_environment_variables()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Get Gemini API configuration from config
GEMINI_MODEL = config.get_gemini_api("model_name")
MAX_OUTPUT_TOKENS = config.get_gemini_api("max_output_tokens")
TEMPERATURE = config.get_gemini_api("temperature")
TOP_P = config.get_gemini_api("top_p")
TOP_K = config.get_gemini_api("top_k")

if GENAI_AVAILABLE and GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    # Initialize Gemini
    genai.configure(api_key=GEMINI_API_KEY)
    AI_ENABLED = True
else:
    AI_ENABLED = False

# Use only one fallback warning
_FALLBACK_WARNING_SHOWN = False


def fallback_detection(image):
    """
    Fallback detection when Gemini API is not available.
    Returns a region in the center of the image.

    Args:
        image: PIL Image object

    Returns:
        tuple: (box, None, None) where box is (x1, y1, x2, y2) coordinates
    """
    # If AI is not enabled, just return a default region in the center
    width, height = image.size
    # Create a box that covers the center 50% of the image
    center_box = (width // 4, height // 4, width * 3 // 4, height * 3 // 4)
    return center_box, None, None  # No raw box or description in fallback mode


def identify_interesting_textile(image, custom_prompt=None, target_type=None):
    """
    Use Google Gemini AI to identify the most interesting area of the image.

    Args:
        image: PIL Image object
        custom_prompt: Optional custom prompt to use instead of the default
        target_type: Optional target type to look for (replaces {target_type} in prompt)

    Returns:
        tuple: (coordinates, raw_coordinates, description)
            - coordinates: (x1, y1, x2, y2) of the interesting area
            - raw_coordinates: original coordinates before adjustment or None
            - description: text description of what was detected or None
    """
    global _FALLBACK_WARNING_SHOWN

    if not GENAI_AVAILABLE or not AI_ENABLED:
        if not _FALLBACK_WARNING_SHOWN:
            print("Gemini API not available, using fallback detection")
            _FALLBACK_WARNING_SHOWN = True
        return fallback_detection(image)

    try:
        # Resize image if too large to avoid API limits
        max_dim = 1024
        resized_img = image
        if max(image.size) > max_dim:
            ratio = max_dim / max(image.size)
            new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
            # Use LANCZOS for highest quality resampling
            resized_img = image.resize(new_size, resample=1)  # 1 = LANCZOS

        # Ensure image is in RGB mode (not RGBA) before saving as JPEG
        if resized_img.mode == "RGBA":
            resized_img = resized_img.convert("RGB")

        # Save to buffer for Gemini API with high quality setting
        buffer = BytesIO()
        resized_img.save(buffer, format="JPEG", quality=95)
        buffer.seek(0)

        # Configure the model using settings from config
        model = genai.GenerativeModel(GEMINI_MODEL)

        # Use custom prompt if provided, otherwise use combined prompt from config
        if custom_prompt is None:
            # Use the new combined prompt system
            prompt = config.get_combined_prompt(target_type)
            print(f"Using prompt with target type: {target_type or 'None'}")
        else:
            prompt = custom_prompt
            print(f"Using custom prompt: {prompt}")

        response = model.generate_content(
            [prompt, {"mime_type": "image/jpeg", "data": buffer.getvalue()}],
            generation_config=genai.GenerationConfig(
                max_output_tokens=MAX_OUTPUT_TOKENS,
                temperature=TEMPERATURE,
                top_p=TOP_P,
                top_k=TOP_K,
            ),
        )

        # Parse the response
        response_text = response.text.strip()
        print(f"Raw Gemini response: {response_text}")

        # Extract coordinates
        coords_match = re.search(
            r"COORDS:\s*(\d+\.?\d*),(\d+\.?\d*),(\d+\.?\d*),(\d+\.?\d*)",
            response_text,
            re.IGNORECASE,
        )

        # Extract description (everything after DESCRIPTION:)
        description_match = re.search(
            r"DESCRIPTION:\s*(.*(?:\n.*)*)", response_text, re.IGNORECASE | re.DOTALL
        )

        description = None
        if description_match:
            description = description_match.group(1).strip()
            print(f"Extracted description: {description}")

        # Fall back to the original pattern if the structured response fails
        if not coords_match:
            coords_match = re.search(
                r"(\d+\.?\d*),(\d+\.?\d*),(\d+\.?\d*),(\d+\.?\d*)", response_text
            )
            # If we found coordinates but no structure, try to extract description as any text before/after coords
            if coords_match and not description:
                # Get everything except the coordinates as a potential description
                coords_text = coords_match.group(0)
                potential_description = response_text.replace(coords_text, "").strip()
                if potential_description:
                    description = potential_description
                    print(f"Extracted unstructured description: {description}")

        if coords_match:
            # Parse the coordinates
            x1_pct, y1_pct, x2_pct, y2_pct = map(float, coords_match.groups())

            # Log the raw normalized coordinates exactly as received from Gemini
            print(
                f"Raw normalized coordinates from Gemini: {x1_pct},{y1_pct},{x2_pct},{y2_pct}"
            )

            # Raw pixel coordinates before any adjustments
            width, height = image.size
            raw_x1 = int(x1_pct * width)
            raw_y1 = int(y1_pct * height)
            raw_x2 = int(x2_pct * width)
            raw_y2 = int(y2_pct * height)
            print(
                f"Raw pixel coordinates before adjustments: ({raw_x1}, {raw_y1}, {raw_x2}, {raw_y2})"
            )

            # Store raw coordinates for debugging
            raw_box = (raw_x1, raw_y1, raw_x2, raw_y2)

            # Normalize values to ensure they're between 0 and 1
            x1_pct = max(0.0, min(1.0, x1_pct))
            y1_pct = max(0.0, min(1.0, y1_pct))
            x2_pct = max(0.0, min(1.0, x2_pct))
            y2_pct = max(0.0, min(1.0, y2_pct))

            # Ensure x2 > x1 and y2 > y1
            if x2_pct <= x1_pct:
                x1_pct, x2_pct = max(0.0, x1_pct - 0.1), min(1.0, x1_pct + 0.1)
            if y2_pct <= y1_pct:
                y1_pct, y2_pct = max(0.0, y1_pct - 0.1), min(1.0, y1_pct + 0.1)

            # Convert percentages to actual pixel coordinates
            x1 = int(x1_pct * width)
            y1 = int(y1_pct * height)
            x2 = int(x2_pct * width)
            y2 = int(y2_pct * height)

            print(f"Pixel coordinates after normalization: ({x1}, {y1}, {x2}, {y2})")

            # Ensure minimum size for the region (at least 5% of the image)
            min_width = width // 20
            min_height = height // 20

            if x2 - x1 < min_width:
                # Use floating point division for more accurate center
                center_x = (x1 + x2) / 2
                x1 = max(0, int(center_x - min_width / 2))
                x2 = min(width, x1 + min_width)

            if y2 - y1 < min_height:
                # Use floating point division for more accurate center
                center_y = (y1 + y2) / 2
                y1 = max(0, int(center_y - min_height / 2))
                y2 = min(height, y1 + min_height)

            # Ensure the selected area is not too large (max 15% of image area)
            max_area = width * height * 0.15  # 15% of image area
            area = (x2 - x1) * (y2 - y1)

            if area > max_area:
                # Scale down the box while keeping the center the same
                # Use floating point division for more accurate center
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2

                # Calculate the scale factor to reduce to max area
                scale_factor = (
                    max_area / area
                ) ** 0.5  # square root to apply to both dimensions

                # Calculate new dimensions
                new_width = int((x2 - x1) * scale_factor)
                new_height = int((y2 - y1) * scale_factor)

                # Apply to coordinates with precise centering
                x1 = max(0, int(center_x - new_width / 2))
                y1 = max(0, int(center_y - new_height / 2))
                x2 = min(width, x1 + new_width)
                y2 = min(height, y1 + new_height)

            print(f"Processed coordinates: ({x1}, {y1}, {x2}, {y2})")
            return (x1, y1, x2, y2), raw_box, description

        # If parsing fails, return a default region
        print("Failed to parse coordinates from Gemini response. Using default region.")
        width, height = image.size
        center_box = (width // 4, height // 4, width * 3 // 4, height * 3 // 4)
        return center_box, None, None  # No raw box or description in fallback mode

    except (ValueError, TypeError, IndexError) as e:
        print(f"Error processing Gemini API response: {e}")
        # Return a default region on error
        width, height = image.size
        center_box = (width // 4, height // 4, width * 3 // 4, height * 3 // 4)
        return center_box, None, None  # No raw box or description in fallback mode
    except Exception as e:
        print(f"Unexpected error calling Gemini API: {e}")
        # Return a default region on error
        width, height = image.size
        center_box = (width // 4, height // 4, width * 3 // 4, height * 3 // 4)
        return center_box, None, None  # No raw box or description in fallback mode
