"""Image analysis module using Google Gemini API.

This module contains the ImageAnalyzer class, which uses the Google Gemini API
to analyze images and identify interesting regions.
"""

import base64
import io
from typing import List, Dict, Any, Optional, Tuple, Union

import google.generativeai as genai
from PIL import Image

from preview_maker.core.logging import logger
from preview_maker.ai.parser import ResponseParser


class ImageAnalyzer:
    """Analyzes images using the Google Gemini API.

    This class is responsible for sending images to the Gemini API,
    processing the responses, and extracting coordinates of interesting
    regions in the images.

    Attributes:
        api_key: The Google Gemini API key
        model_name: The name of the Gemini model to use
        parser: The ResponseParser for parsing API responses
    """

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-pro-vision") -> None:
        """Initialize the ImageAnalyzer.

        Args:
            api_key: The Google Gemini API key
            model_name: The name of the Gemini model to use
        """
        self.api_key = api_key
        self.model_name = model_name
        self.parser = ResponseParser()

        # Configure the Gemini API
        genai.configure(api_key=api_key)

        logger.info(f"ImageAnalyzer initialized with model: {model_name}")

    def analyze_image(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Analyze an image to find interesting regions.

        Args:
            image: The PIL Image to analyze

        Returns:
            A list of dictionaries containing coordinates and metadata for
            interesting regions in the image
        """
        try:
            # Prepare the image for the API
            image_bytes = self._prepare_image(image)

            # Get the model
            model = genai.GenerativeModel(self.model_name)

            # Create the prompt
            prompt = self._create_prompt(image.width, image.height)

            # Send the request to the API
            response = model.generate_content(
                [prompt, {"mime_type": "image/jpeg", "data": image_bytes}]
            )

            # Parse the response
            highlights = self.parser.parse_response(response.text)

            # Log the results
            logger.info(f"Analysis found {len(highlights)} interesting regions")

            return highlights

        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return []

    def _prepare_image(self, image: Image.Image) -> bytes:
        """Prepare an image for the Gemini API.

        Args:
            image: The PIL Image to prepare

        Returns:
            The image as bytes
        """
        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Convert to JPEG bytes
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        image_bytes = buffer.getvalue()

        return image_bytes

    def _create_prompt(self, width: int, height: int) -> str:
        """Create a prompt for the Gemini API.

        Args:
            width: The width of the image
            height: The height of the image

        Returns:
            The prompt text
        """
        return f"""
        Analyze this image and identify the most interesting or visually striking regions.

        For each interesting region, provide:
        1. The X and Y coordinates of the center of the region
        2. A suggested radius for a circular highlight (in pixels)
        3. A confidence score between 0 and 1

        Format your response as a list of JSON objects, one per region, like this:
        [
          {{
            "x": 123,
            "y": 456,
            "radius": 50,
            "confidence": 0.9,
            "description": "Brief description of what makes this region interesting"
          }}
        ]

        Image dimensions: {width}x{height} pixels.
        Provide coordinates within these bounds.
        Limit your response to the 3 most interesting regions.
        """
