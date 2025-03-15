"""
Module for image processing operations.

This module handles loading, transforming, and creating circular overlays
for images using Pillow and Cairo.
"""

import os
import sys
import threading
import logging
from typing import Callable, Optional, Tuple, Union

from PIL import Image, ImageDraw

# Check if we're running in a headless environment (no display)
# or if we're running tests
HEADLESS_MODE = "DISPLAY" not in os.environ or "pytest" in sys.modules

# Only import GTK/Cairo if not in headless mode
if not HEADLESS_MODE:
    import gi

    gi.require_version("Gtk", "4.0")
    from gi.repository import GLib
    import cairo
else:
    # Create dummy modules for headless mode
    class DummyGLib:
        @staticmethod
        def idle_add(func, *args):
            func(*args)

    class DummyCairo:
        class ImageSurface:
            @staticmethod
            def create_for_data(data, format_type, width, height, stride):
                return None

        class Context:
            def __init__(self, surface):
                self.surface = surface

            def set_source_rgba(self, r, g, b, a):
                pass

            def arc(self, x, y, radius, start, end):
                pass

            def fill(self):
                pass

    GLib = DummyGLib()
    cairo = DummyCairo()

    FORMAT_ARGB32 = 0  # Dummy value for headless mode

# Set up logging
logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Handles image processing operations.
    """

    def __init__(self):
        """Initialize the ImageProcessor."""
        logger.debug("Initializing ImageProcessor (headless mode: %s)", HEADLESS_MODE)

    def load_image(
        self,
        path: str,
        callback: Callable[[Optional[Image.Image]], None] = None,
    ) -> Optional[Image.Image]:
        """
        Load an image from the given path.

        Args:
            path: Path to the image file
            callback: Optional callback function to receive the loaded image

        Returns:
            The loaded PIL Image or None if loading fails
        """
        if callback:
            # Asynchronous loading
            thread = threading.Thread(
                target=self._load_in_thread, args=(path, callback)
            )
            thread.daemon = True
            thread.start()
            return None
        else:
            # Synchronous loading
            return self._load_image_sync(path)

    def _load_in_thread(
        self, path: str, callback: Callable[[Optional[Image.Image]], None]
    ) -> None:
        """
        Load image in a separate thread and call the callback when done.

        Args:
            path: Path to the image file
            callback: Callback function to receive the loaded image
        """
        try:
            image = self._load_image_sync(path)

            if HEADLESS_MODE:
                # In headless mode or during tests, call callback directly
                logger.debug("Headless mode: calling callback directly")
                callback(image)
            else:
                # Use GLib.idle_add to safely update UI from a thread
                logger.debug("Using GLib.idle_add for callback")
                GLib.idle_add(callback, image)

        except Exception as e:
            logger.error("Error loading image in thread: %s", str(e))
            if HEADLESS_MODE:
                callback(None)
            else:
                GLib.idle_add(callback, None)

    def _load_image_sync(self, path: str) -> Optional[Image.Image]:
        """
        Load an image synchronously.

        Args:
            path: Path to the image file

        Returns:
            The loaded PIL Image or None if loading fails
        """
        try:
            logger.debug("Loading image from: %s", path)
            return Image.open(path).convert("RGBA")
        except Exception as e:
            logger.error("Error loading image: %s", str(e))
            return None

    def resize_image(self, image: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """
        Resize an image to the given size.

        Args:
            image: PIL Image to resize
            size: Target size as (width, height)

        Returns:
            Resized PIL Image
        """
        try:
            return image.resize(size, Image.LANCZOS)
        except Exception as e:
            logger.error("Error resizing image: %s", str(e))
            return image

    def crop_image(
        self, image: Image.Image, box: Tuple[int, int, int, int]
    ) -> Image.Image:
        """
        Crop an image to the given box.

        Args:
            image: PIL Image to crop
            box: Crop box as (left, upper, right, lower)

        Returns:
            Cropped PIL Image
        """
        try:
            return image.crop(box)
        except Exception as e:
            logger.error("Error cropping image: %s", str(e))
            return image

    def create_circular_overlay(
        self,
        size: Tuple[int, int],
        position: Tuple[int, int],
        radius: int,
        color: Tuple[int, int, int, int] = (255, 0, 0, 128),
    ) -> Image.Image:
        """
        Create a circular overlay with the given parameters.

        Args:
            size: Size of the overlay image as (width, height)
            position: Center position of the circle as (x, y)
            radius: Radius of the circle
            color: RGBA color of the circle

        Returns:
            PIL Image with the circular overlay
        """
        try:
            # Create a transparent image
            overlay = Image.new("RGBA", size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            # Draw the circle
            x, y = position
            left = x - radius
            top = y - radius
            right = x + radius
            bottom = y + radius

            # Draw a circle with the specified color
            draw.ellipse((left, top, right, bottom), fill=color)

            return overlay
        except Exception as e:
            logger.error("Error creating circular overlay: %s", str(e))
            # Return a transparent image of the requested size
            return Image.new("RGBA", size, (0, 0, 0, 0))

    def create_cairo_surface(self, image: Image.Image) -> Union[object, None]:
        """
        Convert a PIL Image to a Cairo surface.

        Args:
            image: PIL Image to convert

        Returns:
            Cairo surface or None if in headless mode or conversion fails
        """
        if HEADLESS_MODE:
            logger.debug("Skipping Cairo surface creation in headless mode")
            return None

        try:
            # Convert PIL Image to Cairo surface
            img_data = bytearray(image.tobytes("raw", "BGRA"))
            surface = cairo.ImageSurface.create_for_data(
                img_data,
                cairo.FORMAT_ARGB32,
                image.width,
                image.height,
                image.width * 4,
            )
            return surface
        except Exception as e:
            logger.error("Error creating Cairo surface: %s", str(e))
            return None

    def draw_on_cairo_surface(
        self,
        surface,
        draw_func: Callable,
    ) -> None:
        """
        Draw on a Cairo surface using the provided drawing function.

        Args:
            surface: Cairo surface to draw on
            draw_func: Function that takes a Cairo context
        """
        if HEADLESS_MODE or surface is None:
            logger.debug("Skipping Cairo drawing in headless mode")
            return

        try:
            context = cairo.Context(surface)
            draw_func(context)
        except Exception as e:
            logger.error("Error drawing on Cairo surface: %s", str(e))
