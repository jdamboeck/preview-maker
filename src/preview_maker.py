import os
import sys
import logging
import math
import random
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any, Union, Callable

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Adw, Gio  # noqa

from PIL import Image

from src.config import load_config, update_config
from src.gemini_analyzer import identify_interesting_textile


class PreviewMaker:
    """Main application class to create preview images from user clicks."""

    def __init__(self):
        """Initialize the application UI and connect signal handlers."""
        self.builder = Gtk.Builder()
        self.builder.add_from_file("src/preview_maker.ui")

        # Get config
        self.config = load_config()

        # Initialize debug mode from config
        self.debug_mode = self.config.get("ui", {}).get("debug_mode", False)

        # Connect to the window close event
        self.window = self.builder.get_object("main_window")
        self.window.connect("close-request", self.on_window_close)

    def debug_print(self, message: str) -> None:
        """Print debug information only if debug mode is enabled."""
        if self.debug_mode:
            print(message)

    def on_debug_toggled(self, switch: Gtk.Switch, state: bool) -> None:
        """Handle debug mode toggle switch changes."""
        self.debug_mode = state
        self.debug_print(f"Debug mode: {state}")

        # Save debug mode to config file
        update_config("ui", "debug_mode", state)

        # Update UI elements visibility based on debug mode
        debug_box = self.builder.get_object("debug_box")
        if debug_box:
            debug_box.set_visible(state)

    def on_selection_size_changed(self, scale: Gtk.Scale) -> None:
        """Handle selection size scale changes."""
        value = scale.get_value()
        self.selection_ratio = value / 100.0  # Convert percentage to ratio
        self.debug_print(f"Selection ratio changed to: {self.selection_ratio}")

        # Save selection ratio to config
        update_config("image_processing", "selection_ratio", self.selection_ratio)

        # Redraw circles with new size if there's an image loaded
        self.draw_circles()

    def on_zoom_factor_changed(self, scale: Gtk.Scale) -> None:
        """Handle zoom factor scale changes."""
        value = scale.get_value()
        self.zoom_factor = value
        self.debug_print(f"Zoom factor changed to: {self.zoom_factor}")

        # Save zoom factor to config
        update_config("image_processing", "zoom_factor", self.zoom_factor)

        # Update preview if we have a selection
        if hasattr(self, "preview_image") and self.preview_image is not None:
            self.update_preview()

    def update_display_area(self) -> None:
        """Get the current drawing area dimensions and update display metrics."""
        if not hasattr(self, "drawing_area"):
            return

        # Get drawing area dimensions
        width = self.drawing_area.get_width()
        height = self.drawing_area.get_height()

        self.debug_print(f"Drawing area dimensions: {width}x{height}")

        if hasattr(self, "original_image") and self.original_image is not None:
            # Calculate how much of the original image is visible
            img_width, img_height = self.original_image.size
            self.debug_print(f"Image dimensions: {img_width}x{img_height}")

            # Calculate percentage of the image that is visible in the UI
            if img_width > 0 and img_height > 0:
                area_percentage = (width * height) / (img_width * img_height) * 100
                self.debug_print(f"Visible area: {area_percentage:.1f}% of original")

    def on_image_click(
        self, drawing_area: Gtk.DrawingArea, x: float, y: float, data: object
    ) -> None:
        """Handle clicks on the image to select points for preview."""
        if not hasattr(self, "original_image") or self.original_image is None:
            return

        self.debug_print(f"Click detected at ({x}, {y})")

        # Scale click coordinates to original image dimensions
        img_width, img_height = self.original_image.size
        display_width = drawing_area.get_width()
        display_height = drawing_area.get_height()

        # Calculate the displayed image dimensions (preserving aspect ratio)
        display_ratio = min(display_width / img_width, display_height / img_height)
        disp_img_width = img_width * display_ratio
        disp_img_height = img_height * display_ratio

        # Calculate offsets if the image is centered in the drawing area
        offset_x = (display_width - disp_img_width) / 2
        offset_y = (display_height - disp_img_height) / 2

        # Adjust click coordinates for the offset and scaling
        if (
            x < offset_x
            or y < offset_y
            or x > offset_x + disp_img_width
            or y > offset_y + disp_img_height
        ):
            self.debug_print("Click outside image bounds")
            return

        # Translate to image coordinates
        image_x = (x - offset_x) / display_ratio
        image_y = (y - offset_y) / display_ratio

        self.debug_print(f"Mapped to image coordinates: ({image_x}, {image_y})")
