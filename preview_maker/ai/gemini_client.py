"""Gemini API client for image analysis.

This module provides a client for Google's Gemini API to analyze images and
identify interesting regions to highlight.
"""

import os
from pathlib import Path
from typing import Dict, Optional, Any, Union
import io

import google.generativeai as genai
from PIL import Image

from preview_maker.core.config import config_manager
from preview_maker.core.logging import logger


class GeminiClient:
    """Client for Google's Gemini API for image analysis."""

    def __init__(self) -> None:
        """Initialize the Gemini client.

        Loads API key from configuration and initializes the Gemini API client.
        Falls back to environment variable if not in config.
        """
        self._config = config_manager.get_config()
        self._model = None
        self._initialized = False
        self._api_key = self._get_api_key()

        # Initialize client if API key is available
        if self._api_key:
            self._initialize_client()

    def _get_api_key(self) -> Optional[str]:
        """Get the Gemini API key from config or environment.

        Returns:
            API key or None if not available
        """
        # First try config
        api_key = self._config.gemini_api_key

        # Fall back to environment variable
        if not api_key:
            api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            logger.warning("No Gemini API key found in config or environment")

        return api_key

    def _initialize_client(self) -> None:
        """Initialize the Gemini API client."""
        try:
            # Configure the Gemini API
            genai.configure(api_key=self._api_key)

            # Get the multimodal model for image analysis
            self._model = genai.GenerativeModel("gemini-pro-vision")
            self._initialized = True
            logger.info("Gemini API client initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Gemini API client: {e}")
            self._initialized = False

    def analyze_image(
        self, image_path: Union[str, Path, Image.Image], prompt: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Analyze an image using Gemini API.

        Args:
            image_path: Path to the image file or PIL Image object
            prompt: Custom prompt to use for analysis (uses default if None)

        Returns:
            Analysis results or None if failed
        """
        if not self._initialized or not self._model:
            logger.error("Gemini API client not initialized")
            return None

        try:
            # Load image if path provided
            if isinstance(image_path, (str, Path)):
                try:
                    image = Image.open(image_path)
                except Exception as e:
                    logger.error(f"Failed to load image {image_path}: {e}")
                    return None
            else:
                image = image_path

            # Use default prompt if none provided
            if not prompt:
                prompt = self._get_default_prompt()

            # Prepare image for API
            img_bytes = io.BytesIO()
            image.save(img_bytes, format="PNG")
            img_bytes.seek(0)

            # Send request to Gemini
            response = self._model.generate_content([prompt, img_bytes])

            # Process response
            return self._process_response(response)

        except Exception as e:
            logger.error(f"Failed to analyze image: {e}")
            return None

    def _get_default_prompt(self) -> str:
        """Get the default prompt for image analysis.

        Returns:
            Default prompt text
        """
        return """
        Analyze this image and identify the most interesting or important regions.
        For each region, provide:
        1. The relative x,y coordinates of the center (values between 0.0 and 1.0)
        2. An appropriate radius for a circular highlight (as a value between 0.0 and 0.5)
        3. A brief description of what makes this region interesting

        Format your response as JSON with the following structure:
        {
          "highlights": [
            {
              "x": 0.5,
              "y": 0.5,
              "radius": 0.1,
              "description": "Description of this region"
            },
            ... more highlights ...
          ]
        }

        Limit your response to the 3 most interesting regions.
        """

    def _process_response(self, response: Any) -> Optional[Dict[str, Any]]:
        """Process the Gemini API response.

        Args:
            response: Response from the Gemini API

        Returns:
            Processed results or None if failed
        """
        try:
            # Extract text from response
            if hasattr(response, "text"):
                raw_text = response.text
            elif hasattr(response, "candidates") and response.candidates:
                raw_text = response.candidates[0].content.parts[0].text
            else:
                logger.error("Unexpected response format from Gemini API")
                return None

            # For now, just return the raw text
            # The parser module will handle converting this to structured data
            return {"raw_response": raw_text}

        except Exception as e:
            logger.error(f"Failed to process Gemini API response: {e}")
            return None

    @property
    def is_initialized(self) -> bool:
        """Check if the client is initialized.

        Returns:
            True if initialized, False otherwise
        """
        return self._initialized
