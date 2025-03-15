"""Module for analyzing images using Google's Gemini API.

This module provides the ImageAnalyzer class which leverages Google's
Gemini API to identify interesting regions in images. It supports both
direct image analysis and analysis from file paths.
"""

import os
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path

from PIL import Image
import google.generativeai as genai

from preview_maker.ai.parser import ResponseParser


logger = logging.getLogger(__name__)


class ImageAnalyzer:
    """Analyzes images using Google's Gemini API to identify regions of interest.

    This class uses the Gemini API to analyze images and identify interesting
    regions or features. It returns normalized coordinates and descriptions
    for each region, which can be used to create overlays or annotations.

    Attributes:
        _client: The Gemini model client.
        _model_name: Name of the Gemini model to use.
        _parser: ResponseParser instance to parse API responses.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-pro-vision",
        client: Any = None,
    ):
        """Initialize the ImageAnalyzer.

        Args:
            api_key: The Google API key to use. If None, will try to get from
                environment variable GOOGLE_API_KEY.
            model_name: The name of the Gemini model to use.
            client: Optional pre-configured client for testing.
        """
        self._model_name = model_name
        self._parser = ResponseParser()

        if client:
            self._client = client
            return

        # Get API key from param or environment
        if not api_key:
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError(
                    "API key must be provided either as a parameter or "
                    "via GOOGLE_API_KEY environment variable."
                )

        # Configure the Gemini API
        genai.configure(api_key=api_key)
        self._client = genai.GenerativeModel(model_name)

    def analyze_image(self, image: Image.Image) -> Optional[List[Dict[str, Any]]]:
        """Analyze an image to identify interesting regions.

        Args:
            image: The PIL Image to analyze.

        Returns:
            A list of dictionaries, each containing normalized coordinates (x, y),
            radius, and description for an interesting region. Returns None if
            analysis fails.
        """
        try:
            # Build the prompt
            prompt = self._build_prompt(image)

            # Send the request to Gemini
            response = self._client.generate_content([prompt, image])

            # Parse the response
            return self._parser.parse_response({"raw_response": response.text})
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return None

    def analyze_image_from_path(
        self, image_path: Union[str, Path]
    ) -> Optional[List[Dict[str, Any]]]:
        """Analyze an image from a file path.

        Args:
            image_path: Path to the image file.

        Returns:
            A list of dictionaries, each containing normalized coordinates (x, y),
            radius, and description for an interesting region. Returns None if
            analysis fails.
        """
        try:
            # Open the image
            image = Image.open(image_path)
            return self.analyze_image(image)
        except Exception as e:
            logger.error(f"Error opening or analyzing image at {image_path}: {e}")
            return None

    def convert_highlights_to_pixels(
        self, highlights: List[Dict[str, Any]], image_size: Tuple[int, int]
    ) -> List[Dict[str, Any]]:
        """Convert normalized highlight coordinates to pixel coordinates.

        Args:
            highlights: List of highlight dictionaries with normalized coordinates.
            image_size: Tuple of (width, height) in pixels.

        Returns:
            List of highlight dictionaries with pixel coordinates.
        """
        return self._parser.convert_to_pixels(highlights, image_size)

    def _build_prompt(self, image: Image.Image) -> str:
        """Build the prompt for the Gemini API.

        Args:
            image: The image to analyze.

        Returns:
            A string prompt to send to the Gemini API.
        """
        return (
            "Analyze this image and highlight areas of interest. "
            "Identify 2-5 points that would be considered visually significant "
            "or important to the composition. "
            "For each point, provide the following information in JSON format:\n"
            "```json\n"
            "{\n"
            '  "highlights": [\n'
            "    {\n"
            '      "x": <normalized x coordinate (0.0-1.0)>,\n'
            '      "y": <normalized y coordinate (0.0-1.0)>,\n'
            '      "radius": <normalized radius (0.0-0.5)>,\n'
            '      "description": "<brief description of this area>"\n'
            "    },\n"
            "    ...\n"
            "  ]\n"
            "}\n"
            "```\n"
            "The x and y coordinates should be normalized values between 0.0 and 1.0, "
            "where (0,0) is the top-left corner and (1,1) is the bottom-right corner. "
            "The radius should be a normalized value between 0.0 and 0.5."
        )
