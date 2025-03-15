"""Module for parsing responses from the Gemini API.

This module provides the ResponseParser class which handles the parsing
of responses from the Gemini API, extracting structured data about image
highlights in various formats.
"""

import json
import re
import logging
from typing import Dict, List, Optional, Any, Tuple, Union

logger = logging.getLogger(__name__)


class ResponseParser:
    """Parser for Gemini API responses about image highlights.

    This class provides methods to parse both structured (JSON) and
    unstructured (text) responses from the Gemini API, extracting
    coordinates, radii, and descriptions of image highlights.
    """

    def parse_response(
        self, response: Optional[Dict[str, str]]
    ) -> Optional[List[Dict[str, Any]]]:
        """Parse a response from the Gemini API.

        This method attempts to extract highlight information from the response,
        trying first to parse JSON and falling back to text extraction if needed.

        Args:
            response: A dictionary containing a 'raw_response' key with the
                     text response from the Gemini API.

        Returns:
            A list of dictionaries, each containing normalized coordinates (x, y),
            radius, and description for an interesting region. Returns None if
            parsing fails.
        """
        if not response or "raw_response" not in response:
            logger.warning("Invalid response format: missing 'raw_response'")
            return None

        raw_text = response["raw_response"]

        # Try to extract JSON first
        highlights = self._extract_json(raw_text)

        # Fall back to text extraction if JSON parsing failed
        if not highlights:
            highlights = self._extract_from_text(raw_text)

        if not highlights:
            logger.warning("Failed to extract highlights from response")
            return None

        # Validate and normalize the extracted highlights
        return self._validate_highlights(highlights)

    def _extract_json(self, text: str) -> Optional[List[Dict[str, Any]]]:
        """Extract highlights from JSON in the response.

        Args:
            text: The raw text response.

        Returns:
            A list of highlight dictionaries or None if extraction fails.
        """
        # Look for JSON blocks in the response
        json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if not json_match:
            # Try without the markdown code block format
            json_match = re.search(r"{.*?}", text, re.DOTALL)

        if not json_match:
            return None

        try:
            json_str = json_match.group(1) if "```" in text else json_match.group(0)
            data = json.loads(json_str)

            if "highlights" in data:
                return data["highlights"]
            return None
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from response")
            return None
        except Exception as e:
            logger.warning(f"Error extracting JSON highlights: {e}")
            return None

    def _extract_from_text(self, text: str) -> Optional[List[Dict[str, Any]]]:
        """Extract highlights from unstructured text in the response.

        Args:
            text: The raw text response.

        Returns:
            A list of highlight dictionaries or None if extraction fails.
        """
        highlights = []

        # Pattern to match coordinate information in text
        # Look for patterns like "x: 0.5" or "radius: 0.1"
        coord_pattern = (
            r"(?:highlight|point|area|region).*?"
            r"(?:x\s*[:=]\s*([0-9.]+)).*?"
            r"(?:y\s*[:=]\s*([0-9.]+)).*?"
            r"(?:radius\s*[:=]\s*([0-9.]+)).*?"
            r"(?:description|desc)?\s*[:=]\s*([^\n]+)"
        )

        matches = re.finditer(coord_pattern, text.lower(), re.DOTALL | re.IGNORECASE)

        for match in matches:
            try:
                x = float(match.group(1))
                y = float(match.group(2))
                radius = float(match.group(3))
                description = match.group(4).strip()

                highlights.append(
                    {"x": x, "y": y, "radius": radius, "description": description}
                )
            except (ValueError, IndexError) as e:
                logger.warning(f"Error parsing text highlight: {e}")
                continue

        return highlights if highlights else None

    def _validate_highlights(
        self, highlights: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Validate and normalize the extracted highlights.

        Args:
            highlights: The list of highlight dictionaries.

        Returns:
            A list of validated and normalized highlight dictionaries.
        """
        valid_highlights = []

        for highlight in highlights:
            if (
                "x" not in highlight
                or "y" not in highlight
                or "radius" not in highlight
            ):
                logger.warning(f"Skipping invalid highlight: {highlight}")
                continue

            # Normalize the coordinates and radius
            highlight["x"] = self._normalize_coordinate(highlight["x"])
            highlight["y"] = self._normalize_coordinate(highlight["y"])
            highlight["radius"] = self._normalize_radius(highlight["radius"])

            valid_highlights.append(highlight)

        return valid_highlights

    def _normalize_coordinate(self, value: Union[float, str]) -> float:
        """Normalize a coordinate value to be between 0.0 and 1.0.

        Args:
            value: The coordinate value to normalize.

        Returns:
            The normalized coordinate value.
        """
        try:
            if isinstance(value, str):
                value = float(value)
            return max(0.0, min(1.0, value))
        except ValueError:
            logger.warning(f"Invalid coordinate value: {value}, using 0.5")
            return 0.5

    def _normalize_radius(self, value: Union[float, str]) -> float:
        """Normalize a radius value to be between 0.0 and 0.5.

        Args:
            value: The radius value to normalize.

        Returns:
            The normalized radius value.
        """
        try:
            if isinstance(value, str):
                value = float(value)
            return max(0.0, min(0.5, value))
        except ValueError:
            logger.warning(f"Invalid radius value: {value}, using 0.1")
            return 0.1

    def convert_to_pixels(
        self, highlights: List[Dict[str, Any]], image_size: Tuple[int, int]
    ) -> List[Dict[str, Any]]:
        """Convert normalized highlight coordinates to pixel coordinates.

        Args:
            highlights: List of highlight dictionaries with normalized coordinates.
            image_size: Tuple of (width, height) in pixels.

        Returns:
            List of highlight dictionaries with pixel coordinates.
        """
        width, height = image_size
        min_dimension = min(width, height)
        pixel_highlights = []

        for highlight in highlights:
            pixel_highlight = highlight.copy()
            pixel_highlight["x"] = int(highlight["x"] * width)
            pixel_highlight["y"] = int(highlight["y"] * height)
            pixel_highlight["radius"] = int(highlight["radius"] * min_dimension)
            pixel_highlights.append(pixel_highlight)

        return pixel_highlights
