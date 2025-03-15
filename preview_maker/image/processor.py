"""Image processing functionality for Preview Maker.

This module handles loading, transforming, and creating circular overlays
for images using Pillow and Cairo.
"""

import math
import threading
from pathlib import Path
from typing import Callable, Optional, Tuple
import os

import gi
from PIL import Image, ImageDraw

# Check for headless environment
HEADLESS_MODE = os.environ.get("PREVIEW_MAKER_ENV") == "test" or not os.environ.get(
    "DISPLAY"
)

# Only import GTK-related modules if not in headless mode
if not HEADLESS_MODE:
    gi.require_version("Gtk", "4.0")
    from gi.repository import GLib
else:
    # Create a dummy GLib module for headless mode
    class DummyGLib:
        @staticmethod
        def idle_add(callback, *args, **kwargs):
            callback()
            return False

    GLib = DummyGLib

# Import Cairo for drawing - this works in both headless and GUI modes
import cairo

from preview_maker.core.logging import logger
from preview_maker.core.config import config_manager


class ImageProcessor:
    """Handles image processing operations."""

    def __init__(self) -> None:
        """Initialize the image processor."""
        self._config = config_manager.get_config()
        self._current_image: Optional[Image.Image] = None
        self._load_lock = threading.Lock()
        self._headless = HEADLESS_MODE

    def load_image(
        self, path: str | Path, callback: Callable[[Optional[Image.Image]], None]
    ) -> None:
        """Load an image asynchronously.

        Args:
            path: Path to the image file
            callback: Function to call with the loaded image or None on error
        """
        thread = threading.Thread(target=self._load_in_thread, args=(path, callback))
        thread.daemon = True
        thread.start()

    def _load_in_thread(
        self, path: str | Path, callback: Callable[[Optional[Image.Image]], None]
    ) -> None:
        """Load an image in a background thread.

        Args:
            path: Path to the image file
            callback: Function to call with the loaded image or None on error
        """
        try:
            path = str(path)  # Convert Path to string
            image = Image.open(path)
            logger.info(f"Successfully loaded image: {path}")

            with self._load_lock:
                self._current_image = image

            # Call callback directly for tests or use GLib.idle_add if in UI context
            try:
                # Try to use GLib.idle_add if in a GTK context
                if not self._headless:
                    GLib.idle_add(lambda: self._safe_callback(callback, image))
                else:
                    self._safe_callback(callback, image)
            except Exception as e:
                logger.error(f"Error calling callback: {e}")
                # Fall back to direct callback if GLib is not available or fails
                self._safe_callback(callback, image)

        except Exception as e:
            logger.error(f"Failed to load image: {path}", error=e)
            try:
                # Try to use GLib.idle_add if in a GTK context
                if not self._headless:
                    GLib.idle_add(lambda: self._safe_callback(callback, None))
                else:
                    self._safe_callback(callback, None)
            except Exception as ex:
                logger.error(f"Error calling error callback: {ex}")
                # Fall back to direct callback if GLib is not available or fails
                self._safe_callback(callback, None)

    def _safe_callback(
        self,
        callback: Callable[[Optional[Image.Image]], None],
        image: Optional[Image.Image],
    ) -> bool:
        """Safely call the callback function.

        Args:
            callback: Function to call
            image: Image to pass to the callback

        Returns:
            False to ensure GLib.idle_add doesn't call this function again
        """
        try:
            callback(image)
        except Exception as e:
            logger.error(f"Error in callback: {e}")
        return False  # Return False to ensure GLib.idle_add doesn't repeat

    def create_circular_overlay(
        self, image: Image.Image, position: Tuple[int, int], radius: int
    ) -> Optional[Image.Image]:
        """Create a circular overlay for highlighting part of an image.

        Args:
            image: The image to create an overlay for
            position: (x, y) coordinates of the circle center
            radius: Radius of the circle in pixels

        Returns:
            A new image with a circular overlay or None on error
        """
        try:
            # Ensure radius is positive
            radius = abs(radius)

            # Create transparent overlay
            overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))

            # Try using Cairo
            try:
                # Create Cairo surface for drawing
                surface = cairo.ImageSurface(
                    cairo.FORMAT_ARGB32, image.size[0], image.size[1]
                )
                ctx = cairo.Context(surface)

                # Draw circle
                ctx.arc(position[0], position[1], radius, 0, 2 * math.pi)
                ctx.set_source_rgba(1, 0, 0, 0.5)  # Semi-transparent red
                ctx.fill()

                # Convert Cairo surface to PIL image
                surface_data = surface.get_data()
                overlay = Image.frombuffer(
                    "RGBA",
                    (surface.get_width(), surface.get_height()),
                    surface_data,
                    "raw",
                    "BGRA",
                    surface.get_stride(),
                )
            except Exception as e:
                logger.warning(f"Cairo drawing failed, falling back to PIL: {e}")
                # Fallback to PIL if Cairo fails
                draw = ImageDraw.Draw(overlay)
                bounding_box = [
                    position[0] - radius,
                    position[1] - radius,
                    position[0] + radius,
                    position[1] + radius,
                ]
                draw.ellipse(
                    bounding_box, fill=(255, 0, 0, 128)
                )  # Semi-transparent red

            return overlay

        except Exception as e:
            logger.error("Failed to create overlay", error=e)
            return None

    def create_cairo_surface(self, image: Image.Image) -> Optional[cairo.ImageSurface]:
        """Create a Cairo surface from a PIL image.

        Args:
            image: The PIL image to convert

        Returns:
            A Cairo surface or None on error
        """
        if image is None:
            return None

        try:
            # Convert image to RGBA if needed
            if image.mode != "RGBA":
                image = image.convert("RGBA")

            # Create surface
            surface = cairo.ImageSurface(
                cairo.FORMAT_ARGB32, image.size[0], image.size[1]
            )

            # Copy image data to surface
            surface_data = surface.get_data()
            image_data = image.tobytes("raw", "BGRA")
            surface_data[:] = image_data

            return surface

        except Exception as e:
            logger.error(f"Failed to create Cairo surface: {e}")
            return None

    def draw_overlay_on_surface(
        self,
        surface: Optional[cairo.ImageSurface],
        overlay: Optional[Image.Image],
        position: Tuple[int, int],
    ) -> Optional[cairo.ImageSurface]:
        """Draw an overlay on a Cairo surface.

        Args:
            surface: The target surface
            overlay: The overlay image to draw
            position: (x, y) coordinates for drawing

        Returns:
            The modified surface or None on error
        """
        if surface is None or overlay is None:
            return None

        try:
            # Create context for drawing
            ctx = cairo.Context(surface)

            # Convert overlay to Cairo surface
            overlay_surface = self.create_cairo_surface(overlay)
            if overlay_surface is None:
                return None

            # Draw overlay at position
            ctx.set_source_surface(overlay_surface, position[0], position[1])
            ctx.paint()

            return surface

        except Exception as e:
            logger.error(f"Failed to draw overlay: {e}")
            return None

    @property
    def current_image(self) -> Optional[Image.Image]:
        """Get the currently loaded image."""
        return self._current_image
