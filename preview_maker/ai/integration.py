"""AI integration module for Preview Maker.

This module contains the AIPreviewGenerator class, which integrates
with the Google Gemini API to generate image previews with highlights.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

from PIL import Image

from preview_maker.core.logging import logger
from preview_maker.image.processor import ImageProcessor
from preview_maker.ai.analyzer import ImageAnalyzer


class AIPreviewGenerator:
    """Generates image previews with AI-detected highlights.

    This class integrates the ImageAnalyzer and ImageProcessor to create
    image previews with circular overlays highlighting interesting regions
    detected by the Gemini AI.

    Attributes:
        api_key: The Google Gemini API key
        analyzer: The ImageAnalyzer instance
        image_processor: The ImageProcessor instance
    """

    def __init__(self, api_key: str) -> None:
        """Initialize the AIPreviewGenerator.

        Args:
            api_key: The Google Gemini API key
        """
        self.api_key = api_key
        self.analyzer = ImageAnalyzer(api_key=api_key)
        self.image_processor = ImageProcessor()

        logger.info("AIPreviewGenerator initialized")

    def generate_preview(self, image_path: Union[str, Path]) -> Optional[Image.Image]:
        """Generate a preview with highlights for the given image.

        Args:
            image_path: Path to the image file

        Returns:
            The processed image with highlights, or None if processing failed
        """
        # Load the image
        image = self.image_processor.load_image_sync(str(image_path))
        if not image:
            logger.error(f"Failed to load image: {image_path}")
            return None

        # Analyze the image to find interesting regions
        highlights = self.analyzer.analyze_image(image)
        if not highlights:
            logger.warning(f"No highlights found in image: {image_path}")
            return None

        logger.info(f"Found {len(highlights)} highlights in image: {image_path}")

        # Create a copy of the image to work with
        result_image = image.copy()

        # Ensure the image is in RGBA mode for overlay
        if result_image.mode != "RGBA":
            result_image = result_image.convert("RGBA")

        # Apply overlays for each highlight
        for highlight in highlights:
            # Extract coordinates and radius
            x = highlight.get("x", 0)
            y = highlight.get("y", 0)
            radius = highlight.get("radius", 50)
            confidence = highlight.get("confidence", 0.0)

            # Skip low-confidence highlights
            if confidence < 0.5:
                continue

            # Create overlay with color based on confidence
            # Higher confidence = more red
            red = int(255 * min(1.0, confidence))
            color = f"#{red:02x}4040"  # Red with some transparency

            # Create the overlay
            overlay = self.image_processor.create_circular_overlay(
                result_image.width, result_image.height, x, y, radius, color
            )

            # Composite the overlay onto the result image
            result_image = Image.alpha_composite(result_image, overlay)

        logger.info(f"Generated preview for image: {image_path}")
        return result_image
