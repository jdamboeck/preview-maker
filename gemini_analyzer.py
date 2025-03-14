#!/usr/bin/env python3
"""
Gemini AI analyzer for kimono textiles.
Identifies interesting patterns in textile images.
"""
import os
import re
from io import BytesIO

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

# Load Gemini API key from environment variable
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    # Try to load from .env file
    try:
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    GEMINI_API_KEY = line.strip().split("=")[1].strip()
                    break
    except FileNotFoundError:
        pass

if GENAI_AVAILABLE and GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    # Initialize Gemini
    genai.configure(api_key=GEMINI_API_KEY)
    AI_ENABLED = True
else:
    AI_ENABLED = False
    if GENAI_AVAILABLE and not GEMINI_API_KEY:
        print(
            "WARNING: No Gemini API key found. "
            "Please set the GEMINI_API_KEY environment variable or add it to a .env file."
        )
    elif GENAI_AVAILABLE and GEMINI_API_KEY == "your_gemini_api_key_here":
        print("WARNING: Please replace the placeholder API key in the .env file.")


def identify_interesting_textile(image, custom_prompt=None):
    """
    Use Google Gemini AI to identify the most interesting textile part of the image.

    Args:
        image: PIL Image object
        custom_prompt: Optional custom prompt to use instead of the default

    Returns:
        tuple: Coordinates (x1, y1, x2, y2) of the interesting area
    """
    if not AI_ENABLED:
        # If AI is not enabled, just return a default region in the center
        width, height = image.size
        return (width // 4, height // 4, width * 3 // 4, height * 3 // 4)

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

        # Configure the model - update to use the newer recommended model
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Use custom prompt if provided, otherwise use default
        if custom_prompt is None:
            prompt = (
                "Please analyze this kimono image and identify the most interesting "
                "textile pattern or detail. Return only the coordinates of a bounding "
                "box around this area as normalized values between 0 and 1 in the format: "
                "x1,y1,x2,y2 where x1,y1 is the top-left corner and x2,y2 is the "
                "bottom-right corner."
            )
        else:
            prompt = custom_prompt
            print(f"Using custom prompt: {prompt}")

        response = model.generate_content(
            [prompt, {"mime_type": "image/jpeg", "data": buffer.getvalue()}]
        )

        # Parse the coordinates from the response
        coords_text = response.text.strip()
        print(f"Raw Gemini response: {coords_text}")

        # Extract just the coordinates if there's additional text
        coords_match = re.search(
            r"(\d+\.?\d*),(\d+\.?\d*),(\d+\.?\d*),(\d+\.?\d*)", coords_text
        )

        if coords_match:
            # Parse the coordinates
            x1_pct, y1_pct, x2_pct, y2_pct = map(float, coords_match.groups())

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
            width, height = image.size
            x1 = int(x1_pct * width)
            y1 = int(y1_pct * height)
            x2 = int(x2_pct * width)
            y2 = int(y2_pct * height)

            # Ensure minimum size for the region (at least 10% of the image)
            min_width = width // 10
            min_height = height // 10

            if x2 - x1 < min_width:
                center_x = (x1 + x2) // 2
                x1 = max(0, center_x - min_width // 2)
                x2 = min(width, x1 + min_width)

            if y2 - y1 < min_height:
                center_y = (y1 + y2) // 2
                y1 = max(0, center_y - min_height // 2)
                y2 = min(height, y1 + min_height)

            print(f"Processed coordinates: ({x1}, {y1}, {x2}, {y2})")
            return (x1, y1, x2, y2)

        # If parsing fails, return a default region
        print("Failed to parse coordinates from Gemini response. Using default region.")
        width, height = image.size
        return (width // 4, height // 4, width * 3 // 4, height * 3 // 4)

    except (ValueError, TypeError, IndexError) as e:
        print(f"Error processing Gemini API response: {e}")
        # Return a default region on error
        width, height = image.size
        return (width // 4, height // 4, width * 3 // 4, height * 3 // 4)
    except Exception as e:
        print(f"Unexpected error calling Gemini API: {e}")
        # Return a default region on error
        width, height = image.size
        return (width // 4, height // 4, width * 3 // 4, height * 3 // 4)
