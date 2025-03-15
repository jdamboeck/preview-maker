"""Response parser for Gemini API responses.

This module contains the ResponseParser class, which is responsible for
parsing and extracting structured data from Gemini API responses.
"""

import json
import re
from typing import List, Dict, Any, Optional, Tuple, Union

from preview_maker.core.logging import logger


class ResponseParser:
    """Parses responses from the Gemini API.

    This class is responsible for extracting structured data from the
    text responses returned by the Gemini API, particularly for image
    analysis results.
    """

    def __init__(self) -> None:
        """Initialize the ResponseParser."""
        # Regex pattern to extract JSON from text
        self._json_pattern = r"\[[\s\S]*?\]"

        # Regex pattern for coordinates in text format
        self._coords_pattern = (
            r"(?:coordinates|position|location|center|point):\s*"
            r"\(?(\d+)\s*,\s*(\d+)\)?"
        )

        # Regex pattern for radius in text format
        self._radius_pattern = r"radius:\s*(\d+)"

        logger.debug("ResponseParser initialized")

    def parse_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse a response from the Gemini API.

        Args:
            response: The text response from the Gemini API

        Returns:
            A list of dictionaries containing the extracted data
        """
        if not response:
            logger.warning("Empty response received")
            return []

        # Try to extract JSON from the response
        highlights = self._extract_json(response)

        # If JSON extraction failed, try to extract from text
        if not highlights:
            highlights = self._extract_from_text(response)

        # Validate the extracted data
        highlights = self._validate_highlights(highlights)

        logger.debug(f"Parsed {len(highlights)} highlights from response")
        return highlights

    def _extract_json(self, text: str) -> List[Dict[str, Any]]:
        """Extract JSON data from the response text.

        Args:
            text: The response text

        Returns:
            A list of dictionaries containing the extracted data
        """
        try:
            # Look for JSON array in the text
            json_match = re.search(self._json_pattern, text)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)

                # Ensure we have a list of dictionaries
                if isinstance(data, list) and all(
                    isinstance(item, dict) for item in data
                ):
                    return data

            # If we didn't find a JSON array, look for a JSON object with a highlights key
            if '{"highlights":' in text:
                # Extract the JSON object
                json_match = re.search(r"({[\s\S]*?})", text)
                if json_match:
                    json_str = json_match.group(0)
                    data = json.loads(json_str)

                    # Check if it has a highlights key
                    if isinstance(data, dict) and "highlights" in data:
                        return data["highlights"]

            return []

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from response: {e}")
            return []
        except Exception as e:
            logger.error(f"Error extracting JSON: {e}")
            return []

    def _extract_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract data from plain text when JSON parsing fails.

        Args:
            text: The response text

        Returns:
            A list of dictionaries containing the extracted data
        """
        highlights = []

        # Look for coordinates in the text
        coord_matches = re.finditer(self._coords_pattern, text)

        for match in coord_matches:
            try:
                x, y = int(match.group(1)), int(match.group(2))

                # Look for radius near the coordinates
                radius = 50  # Default radius
                radius_text = text[match.start() : match.start() + 200]  # Look ahead
                radius_match = re.search(self._radius_pattern, radius_text)
                if radius_match:
                    radius = int(radius_match.group(1))

                # Extract a description if possible
                description = self._extract_description(text, match.start())

                # Add the highlight
                highlights.append(
                    {
                        "x": x,
                        "y": y,
                        "radius": radius,
                        "confidence": 0.8,  # Default confidence
                        "description": description,
                    }
                )

            except Exception as e:
                logger.warning(f"Error extracting coordinates: {e}")

        return highlights

    def _extract_description(self, text: str, start_pos: int) -> str:
        """Extract a description from the text near the given position.

        Args:
            text: The response text
            start_pos: The starting position to look from

        Returns:
            A description string
        """
        # Look for description patterns
        patterns = [
            r'description:\s*"([^"]+)"',
            r"description:\s*(.+?)(?:\.|$)",
            r"contains:\s*(.+?)(?:\.|$)",
            r"shows:\s*(.+?)(?:\.|$)",
        ]

        # Look ahead from the start position
        search_text = text[start_pos : start_pos + 300]

        for pattern in patterns:
            match = re.search(pattern, search_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return "Interesting region"

    def _validate_highlights(
        self, highlights: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Validate and clean up the extracted highlights.

        Args:
            highlights: The list of extracted highlights

        Returns:
            A cleaned list of valid highlights
        """
        valid_highlights = []

        for highlight in highlights:
            # Ensure required fields are present
            if "x" not in highlight or "y" not in highlight:
                continue

            # Ensure coordinates are integers
            try:
                highlight["x"] = int(highlight["x"])
                highlight["y"] = int(highlight["y"])
            except (ValueError, TypeError):
                continue

            # Ensure radius is an integer and has a reasonable value
            if "radius" not in highlight:
                highlight["radius"] = 50
            else:
                try:
                    highlight["radius"] = int(highlight["radius"])
                    # Ensure radius is positive and reasonable
                    highlight["radius"] = max(10, min(500, highlight["radius"]))
                except (ValueError, TypeError):
                    highlight["radius"] = 50

            # Ensure confidence is a float between 0 and 1
            if "confidence" not in highlight:
                highlight["confidence"] = 0.8
            else:
                try:
                    highlight["confidence"] = float(highlight["confidence"])
                    highlight["confidence"] = max(
                        0.0, min(1.0, highlight["confidence"])
                    )
                except (ValueError, TypeError):
                    highlight["confidence"] = 0.8

            # Ensure description is a string
            if "description" not in highlight or not isinstance(
                highlight["description"], str
            ):
                highlight["description"] = "Interesting region"

            valid_highlights.append(highlight)

        return valid_highlights
