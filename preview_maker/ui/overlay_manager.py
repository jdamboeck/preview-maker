"""Overlay management component for Preview Maker.

This module contains the OverlayManager class, which is responsible for
creating and managing circular overlays on images.
"""

from typing import Dict, List, Optional, Tuple

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from PIL import Image
from preview_maker.core.logging import logger
from preview_maker.image.processor import ImageProcessor


class OverlayManager:
    """Manages overlays for highlighting regions of interest on images.

    This class is responsible for creating and managing circular overlays
    on images, based on coordinates provided by the AI analysis.

    Attributes:
        image_view: The ImageView component this manager works with
        overlays: Dictionary of active overlays with their coordinates
        image_processor: The ImageProcessor for creating overlays
    """

    def __init__(self, image_view) -> None:
        """Initialize the OverlayManager.

        Args:
            image_view: The ImageView component this manager works with
        """
        self.image_view = image_view
        self.overlays: Dict[str, Tuple[int, int, int]] = {}  # id -> (x, y, radius)
        self.image_processor = ImageProcessor()

        logger.debug("OverlayManager initialized")

    def add_overlay(
        self, overlay_id: str, x: int, y: int, radius: int = 50, color: str = "#ff0000"
    ) -> bool:
        """Add a circular overlay to the image.

        Args:
            overlay_id: Unique identifier for the overlay
            x: X-coordinate center of the overlay
            y: Y-coordinate center of the overlay
            radius: Radius of the circular overlay in pixels
            color: Color of the overlay in hex format

        Returns:
            True if the overlay was added successfully, False otherwise
        """
        # Check if we have an image to overlay
        current_image = self.image_view.get_image()
        if not current_image:
            logger.warning("Cannot add overlay: No image loaded")
            return False

        # Store overlay info
        self.overlays[overlay_id] = (x, y, radius)

        # Apply all overlays
        self._apply_overlays(current_image, color)

        logger.debug(f"Added overlay {overlay_id} at ({x}, {y}) with radius {radius}")
        return True

    def remove_overlay(self, overlay_id: str) -> bool:
        """Remove an overlay from the image.

        Args:
            overlay_id: Identifier of the overlay to remove

        Returns:
            True if the overlay was removed, False if not found
        """
        if overlay_id not in self.overlays:
            logger.warning(f"Cannot remove overlay: {overlay_id} not found")
            return False

        # Remove from storage
        del self.overlays[overlay_id]

        # Re-apply remaining overlays
        current_image = self.image_view.get_image()
        if current_image:
            self._apply_overlays(current_image)

        logger.debug(f"Removed overlay {overlay_id}")
        return True

    def clear_overlays(self) -> None:
        """Clear all overlays from the image."""
        # Remove all overlays
        self.overlays.clear()

        # Restore original image
        current_image = self.image_view.get_image()
        if current_image:
            self.image_view.set_image(current_image)

        logger.debug("Cleared all overlays")

    def get_overlays(self) -> Dict[str, Tuple[int, int, int]]:
        """Get all active overlays.

        Returns:
            Dictionary of overlay IDs to coordinates (x, y, radius)
        """
        return self.overlays.copy()

    def _apply_overlays(self, image: Image.Image, color: str = "#ff0000") -> None:
        """Apply all overlays to the image.

        Args:
            image: The base image to apply overlays to
            color: Color of the overlays in hex format
        """
        if not self.overlays:
            # No overlays to apply
            return

        # Make a copy of the image to avoid modifying the original
        result_image = image.copy()

        # Apply each overlay
        for overlay_id, (x, y, radius) in self.overlays.items():
            # Create circular overlay
            overlay = self.image_processor.create_circular_overlay(
                image.size[0], image.size[1], x, y, radius, color
            )

            # Composite the overlay onto the image
            result_image = Image.alpha_composite(result_image.convert("RGBA"), overlay)

        # Update the image view
        self.image_view.set_image(result_image)
