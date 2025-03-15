"""Integration between AI analysis and image processing.

This module provides a bridge between the AI image analysis components
and the image processing pipeline, allowing the application to generate
previews based on AI-identified regions of interest.
"""

import logging
import threading
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path

from PIL import Image

from preview_maker.image.processor import ImageProcessor
from preview_maker.ai.analyzer import ImageAnalyzer


logger = logging.getLogger(__name__)


class AIPreviewGenerator:
    """Generates image previews based on AI analysis.

    This class combines the AI image analysis and image processing components
    to generate previews that highlight areas of interest identified by the AI.

    Attributes:
        analyzer: The ImageAnalyzer instance for AI analysis.
        processor: The ImageProcessor instance for image processing.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-pro-vision",
        overlay_color: Tuple[int, int, int, int] = (255, 0, 0, 128),
    ):
        """Initialize the AI preview generator.

        Args:
            api_key: Optional API key for the Gemini API. If None, will be read
                from environment variables.
            model_name: The name of the Gemini model to use.
            overlay_color: The RGBA color to use for overlays.
        """
        self.analyzer = ImageAnalyzer(api_key=api_key, model_name=model_name)
        self.processor = ImageProcessor()
        self.overlay_color = overlay_color

    def generate_preview(
        self,
        image_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
    ) -> Optional[Image.Image]:
        """Generate a preview image with AI-identified regions highlighted.

        Args:
            image_path: Path to the input image.
            output_path: Optional path to save the generated preview.
                If None, the preview is only returned but not saved.

        Returns:
            The preview image with highlights, or None if generation failed.
        """
        try:
            # Convert to Path object
            image_path = Path(image_path)

            # Ensure the path exists
            if not image_path.exists():
                logger.error(f"Image path does not exist: {image_path}")
                return None

            # Load the original image synchronously
            image = self._load_image_sync(image_path)
            if not image:
                logger.error(f"Failed to load image: {image_path}")
                return None

            # Analyze the image
            highlights = self.analyzer.analyze_image(image)
            if not highlights:
                logger.warning(f"No highlights found in image: {image_path}")
                return None

            # Convert normalized coordinates to pixels
            pixel_highlights = self.analyzer.convert_highlights_to_pixels(
                highlights, image.size
            )

            # Create preview with overlays
            preview = self._create_preview_with_overlays(image, pixel_highlights)

            # Save the preview if output path is provided
            if output_path:
                output_path = Path(output_path)
                preview.save(output_path)
                logger.info(f"Saved preview to: {output_path}")

            return preview

        except Exception as e:
            logger.error(f"Error generating preview: {e}")
            return None

    def _load_image_sync(self, image_path: Path) -> Optional[Image.Image]:
        """Load an image synchronously.

        Args:
            image_path: Path to the image file.

        Returns:
            The loaded PIL Image or None if loading failed.
        """
        result: Dict[str, Optional[Image.Image]] = {"image": None}
        event = threading.Event()

        def callback(img: Optional[Image.Image]) -> None:
            result["image"] = img
            event.set()

        self.processor.load_image(str(image_path), callback)
        event.wait()
        return result["image"]

    def _create_preview_with_overlays(
        self, image: Image.Image, highlights: List[Dict[str, Any]]
    ) -> Image.Image:
        """Create a preview image with overlays for the highlights.

        Args:
            image: The original image.
            highlights: List of highlights with pixel coordinates.

        Returns:
            A new image with overlays.
        """
        # Create a copy of the original image to avoid modifying it
        preview = image.copy()

        # Create overlays for each highlight
        for highlight in highlights:
            x = int(highlight["x"])
            y = int(highlight["y"])
            radius = int(highlight["radius"])

            # Create a circular overlay using the correct API
            # The API expects (image, position, radius)
            overlay = self.processor.create_circular_overlay(preview, (x, y), radius)

            if overlay:
                # Since the overlay is the same size as the image,
                # we can just paste it directly onto the preview
                preview = Image.alpha_composite(preview.convert("RGBA"), overlay)

        # Convert back to the original mode if needed
        if image.mode != "RGBA":
            preview = preview.convert(image.mode)

        return preview
