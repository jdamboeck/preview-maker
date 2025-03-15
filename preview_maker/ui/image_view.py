"""Image viewing component for Preview Maker.

This module contains the ImageView class, which is responsible for
displaying images and handling zoom and pan operations.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple, cast

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Gdk, GLib  # noqa: E402

from PIL import Image, ImageDraw
from preview_maker.core.logging import logger


class ImageView(Gtk.Picture):
    """Component for displaying images with zoom and pan capabilities.

    This class extends Gtk.Picture to provide image viewing capabilities
    with additional features like zooming and panning.

    Attributes:
        _image: The currently displayed PIL Image
        _scale: The current zoom scale
        _original_size: The original image dimensions
    """

    def __init__(self) -> None:
        """Initialize the ImageView."""
        super().__init__()

        self._image: Optional[Image.Image] = None
        self._scale: float = 1.0
        self._original_size: Optional[Tuple[int, int]] = None

        # Set up the controllers for zoom and pan
        self._setup_controllers()

        # Set content fit to contain the image while maintaining aspect ratio
        self.set_can_shrink(True)
        self.set_content_fit(Gtk.ContentFit.CONTAIN)

        # Set up CSS styling
        self._setup_css()

        logger.debug("ImageView initialized")

    def _setup_controllers(self) -> None:
        """Set up event controllers for mouse and gesture events."""
        # Zoom controller (mouse wheel)
        scroll_controller = Gtk.EventControllerScroll.new(
            Gtk.EventControllerScrollFlags.BOTH_AXES
        )
        scroll_controller.connect("scroll", self._on_scroll)
        self.add_controller(scroll_controller)

        # Pan controller (drag gesture)
        drag_controller = Gtk.GestureDrag.new()
        drag_controller.connect("drag-begin", self._on_drag_begin)
        drag_controller.connect("drag-update", self._on_drag_update)
        drag_controller.connect("drag-end", self._on_drag_end)
        self.add_controller(drag_controller)

        # Double-click to reset zoom
        click_controller = Gtk.GestureClick.new()
        click_controller.set_button(1)  # Left mouse button
        click_controller.connect("pressed", self._on_click_pressed)
        self.add_controller(click_controller)

    def _setup_css(self) -> None:
        """Set up CSS styling for the image view."""
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(
            b"""
            picture {
                background-color: #333333;
                border: 1px solid #444444;
            }
            """
        )

        style_context = self.get_style_context()
        Gtk.StyleContext.add_provider(
            style_context, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def set_image(self, image: Image.Image) -> None:
        """Set the image to display.

        Args:
            image: The PIL Image to display
        """
        if image is None:
            logger.warning("Attempted to set None image")
            return

        # Store the image
        self._image = image
        self._original_size = image.size
        self._scale = 1.0

        # Convert to Gtk texture and display
        self._update_display()

        logger.debug(f"Set image: {image.size[0]}x{image.size[1]}")

    def get_image(self) -> Optional[Image.Image]:
        """Get the currently displayed image.

        Returns:
            The current PIL Image or None if no image is set
        """
        return self._image

    def save_image(self, path: str) -> bool:
        """Save the current image to a file.

        Args:
            path: Path where the image should be saved

        Returns:
            True if successful, False otherwise
        """
        if not self._image:
            logger.warning("No image to save")
            return False

        try:
            self._image.save(path)
            logger.info(f"Image saved to {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            return False

    def _update_display(self) -> None:
        """Update the display with the current image and scale."""
        if not self._image:
            return

        # Create a copy of the image for display
        display_image = self._image.copy()

        # Convert to format supported by Gtk
        if display_image.mode != "RGBA":
            display_image = display_image.convert("RGBA")

        # Convert PIL image to GdkTexture
        width, height = display_image.size
        bytes_per_pixel = 4  # RGBA
        stride = width * bytes_per_pixel

        # Get image data as bytes
        image_bytes = display_image.tobytes()

        # Create GdkTexture from bytes
        texture = Gdk.MemoryTexture.new(
            width,
            height,
            Gdk.MemoryFormat.R8G8B8A8,
            GLib.Bytes.new(image_bytes),
            stride,
        )

        # Set the texture
        self.set_paintable(texture)

        # Force redraw
        self.queue_draw()

    def _on_scroll(
        self, controller: Gtk.EventControllerScroll, dx: float, dy: float
    ) -> bool:
        """Handle scroll events for zooming.

        Args:
            controller: The scroll controller
            dx: The horizontal scroll delta
            dy: The vertical scroll delta

        Returns:
            True to stop propagation, False otherwise
        """
        if not self._image:
            return False

        # Zoom in/out based on scroll direction
        zoom_factor = 0.1
        if dy < 0:  # Scroll up, zoom in
            self._scale *= 1 + zoom_factor
        else:  # Scroll down, zoom out
            self._scale *= 1 - zoom_factor

        # Limit scale range
        self._scale = max(0.1, min(5.0, self._scale))

        # Update display
        self._update_display()

        return True  # Stop event propagation

    def _on_drag_begin(self, controller: Gtk.GestureDrag, x: float, y: float) -> None:
        """Handle drag begin events for panning.

        Args:
            controller: The drag controller
            x: The x coordinate of the drag start
            y: The y coordinate of the drag start
        """
        # Store drag start position
        self._drag_start_x = x
        self._drag_start_y = y

    def _on_drag_update(self, controller: Gtk.GestureDrag, x: float, y: float) -> None:
        """Handle drag update events for panning.

        Args:
            controller: The drag controller
            x: The current x offset from drag start
            y: The current y offset from drag start
        """
        if not self._image:
            return

        # Calculate the new offset
        offset_x, offset_y = controller.get_offset()

        # Update display with new offset
        # Implementation depends on how panning is handled
        # This is a placeholder for actual implementation

        # Update display
        self._update_display()

    def _on_drag_end(self, controller: Gtk.GestureDrag, x: float, y: float) -> None:
        """Handle drag end events for panning.

        Args:
            controller: The drag controller
            x: The final x offset from drag start
            y: The final y offset from drag start
        """
        # Reset drag state
        pass

    def _on_click_pressed(
        self, controller: Gtk.GestureClick, n_press: int, x: float, y: float
    ) -> None:
        """Handle click events.

        Args:
            controller: The click controller
            n_press: Number of presses (for detecting double-clicks)
            x: The x coordinate of the click
            y: The y coordinate of the click
        """
        if not self._image or n_press != 2:
            return

        # Double-click resets zoom level
        self._scale = 1.0
        self._update_display()

        logger.debug("Reset zoom to 1.0")
