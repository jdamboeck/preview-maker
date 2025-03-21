#!/usr/bin/env python3
"""
Preview Maker - Finds interesting details in images
using Google Gemini AI and creates a zoomed-in circular overlay with magnification.
"""

import os
import sys
import time
import threading
import subprocess
import gi
import toml

# Set required versions before importing
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
gi.require_version("Notify", "0.7")

# Add the src directory to the path if running from the root
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# GTK imports
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Gio, Notify

# Image processing imports
from PIL import Image

# Import our custom modules
import gemini_analyzer
import image_processor
import config

# Check for optional dependencies
try:
    import google.generativeai as genai

    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print(
        "WARNUNG: google-generativeai-Paket nicht installiert. "
        "Führen Sie 'pip install google-generativeai' aus, um KI-Funktionen zu aktivieren."
    )

# Get paths from config
PREVIEWS_DIR = config.get_path("previews_dir")
DEBUG_DIR = config.get_path("debug_dir")
PROMPTS_DIR = config.get_path("prompts_dir")
DEFAULT_PROMPT_FILE = config.get_path("default_prompt_file")
TECHNICAL_PROMPT_FILE = config.get_path("technical_prompt_file")
DEFAULT_TARGET_TYPE = config.get_default_target_type()

# Ensure prompt files exist
config.ensure_prompt_files()


class PreviewMaker(Gtk.Application):
    """Main application class for the Preview Maker."""

    def __init__(self):
        # Use 0 for FLAGS_NONE to avoid attribute error
        super().__init__(
            application_id="com.example.preview-maker",
            flags=0,
        )
        self.connect("activate", self.on_activate)

        # Register application actions
        show_action = Gio.SimpleAction.new("show-main-window", None)
        show_action.connect("activate", self._show_main_window)
        self.add_action(show_action)

        # Initialize libnotify
        Notify.init("Vorschau-Ersteller")

        self.current_image = None
        self.processed_image = None
        self.processed_image_with_debug = (
            None  # For on-screen display with debug overlay
        )
        self.processing = False
        self.image_queue = []
        self.current_image_path = None
        self.current_dir = None
        self.notification = None  # Will hold the current libnotify notification
        # For tracking active notifications
        self.last_notification_id = None
        # For tracking specific notifications to prevent flooding
        self._notification_timestamps = {}
        # Store normalized coordinates (0-1) instead of pixels
        self.selected_magnification_point_norm = None
        self.selected_preview_point_norm = None
        # We'll still keep the pixel values for calculations
        self.selected_magnification_point = None
        self.selected_preview_point = None
        self.window = None
        self.progress_bar = None
        self.spinner = None
        self.circle_area = None
        # Track original image dimensions
        self.original_img_width = 0
        self.original_img_height = 0
        # Configurable parameters for circle sizes
        self.selection_ratio = config.get_image_processing("selection_ratio")
        self.zoom_factor = config.get_image_processing("zoom_factor")

        # Load debug mode from config if it exists
        try:
            import toml

            config_path = config.CONFIG_PATH
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    cfg = toml.load(f)
                # Check if UI section with debug_mode exists
                if "ui" in cfg and "debug_mode" in cfg["ui"]:
                    self.debug_mode = cfg["ui"]["debug_mode"]
                    print(f"Loaded debug mode from config: {self.debug_mode}")
                else:
                    self.debug_mode = False  # Default to debug mode off
        except Exception:
            # Default to debug mode off if can't load from config
            self.debug_mode = False

        # Store the description from Gemini
        self.gemini_description = None

        # Ensure desktop file exists for proper notifications
        self._ensure_desktop_file()

    def debug_print(self, *args, **kwargs):
        """Print debug information only when debug mode is enabled"""
        if self.debug_mode:
            print(*args, **kwargs)

    def on_activate(self, app):
        """Primary method to set up the UI when the application starts."""
        # Create the main window
        self.window = Gtk.ApplicationWindow(application=app)
        self.window.set_title("Preview Maker")
        self.window.set_default_size(800, 600)

        # Initialize libnotify again here to ensure it's ready
        Notify.init("Vorschau-Ersteller")

        # Set up all CSS providers
        self._setup_css_providers()

        # Check if Gemini AI is available and show notification if not
        if not GENAI_AVAILABLE:
            # Don't show initial notification, but keep the code for setting up
            print("Google Generative AI not available - not showing notification")

        # Create the main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.window.set_child(main_box)

        # Create header with title and instructions
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        header_box.set_margin_top(20)
        header_box.set_margin_bottom(20)
        header_box.set_margin_start(20)
        header_box.set_margin_end(20)

        title = Gtk.Label(label="Preview Maker")
        title.add_css_class("heading")
        title.set_halign(Gtk.Align.CENTER)
        title.set_margin_bottom(10)
        header_box.append(title)

        instructions = Gtk.Label()
        instructions.set_markup(
            "Drag and drop image files to create previews.\n"
            "<small>Automatic mode creates previews immediately. "
            "Manual mode allows fine-tuning.</small>"
        )
        instructions.add_css_class("desc-text")
        instructions.set_halign(Gtk.Align.CENTER)
        instructions.set_justify(Gtk.Justification.CENTER)
        header_box.append(instructions)

        main_box.append(header_box)

        # Create a vertical box for the layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)
        vbox.set_vexpand(True)
        main_box.append(vbox)

        # Create a horizontal box for the drop areas
        drop_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        drop_box.set_vexpand(True)
        drop_box.set_hexpand(True)
        # Set fixed size for drop box
        drop_box.set_size_request(350, 250)

        # Automatic mode drop area
        auto_drop_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        auto_drop_area.set_size_request(150, 150)
        auto_drop_area.set_hexpand(True)
        auto_drop_area.set_vexpand(True)
        auto_drop_area.set_halign(Gtk.Align.CENTER)
        auto_drop_area.set_valign(Gtk.Align.CENTER)

        # Center the icon in the auto drop area
        auto_icon_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        auto_icon_box.set_halign(Gtk.Align.CENTER)
        auto_icon_box.set_valign(Gtk.Align.CENTER)
        auto_icon_box.set_vexpand(True)

        auto_icon = Gtk.Image.new_from_icon_name("media-playback-start")
        auto_icon.set_pixel_size(48)  # Larger icon
        auto_label = Gtk.Label(label="Automatischer Modus")
        auto_label.set_margin_top(10)

        auto_icon_box.append(auto_icon)
        auto_icon_box.append(auto_label)
        auto_drop_area.append(auto_icon_box)
        drop_box.append(auto_drop_area)

        # Manual mode drop area
        manual_drop_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        manual_drop_area.set_size_request(150, 150)
        manual_drop_area.set_hexpand(True)
        manual_drop_area.set_vexpand(True)
        manual_drop_area.set_halign(Gtk.Align.CENTER)
        manual_drop_area.set_valign(Gtk.Align.CENTER)

        # Center the icon in the manual drop area
        manual_icon_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        manual_icon_box.set_halign(Gtk.Align.CENTER)
        manual_icon_box.set_valign(Gtk.Align.CENTER)
        manual_icon_box.set_vexpand(True)

        manual_icon = Gtk.Image.new_from_icon_name("preferences-system")
        manual_icon.set_pixel_size(48)  # Larger icon
        manual_label = Gtk.Label(label="Manueller Modus")
        manual_label.set_margin_top(10)

        manual_icon_box.append(manual_icon)
        manual_icon_box.append(manual_label)
        manual_drop_area.append(manual_icon_box)
        drop_box.append(manual_drop_area)

        # Add background color styling
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(
            b"""
        box {
            background-color: #333333;
            border-radius: 8px;
        }
        .mode-label {
            color: white;
            font-weight: bold;
        }
        """
        )

        # Get the style context for the display
        display = Gdk.Display.get_default()
        Gtk.StyleContext.add_provider_for_display(
            display,
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        # Add CSS classes
        auto_label.add_css_class("mode-label")
        manual_label.add_css_class("mode-label")

        # Set up drag and drop functionality for automatic mode
        auto_drop_target = Gtk.DropTarget.new(Gio.File, Gdk.DragAction.COPY)
        auto_drop_target.connect("drop", self.on_auto_drop)
        auto_drop_area.add_controller(auto_drop_target)

        # Set up drag and drop functionality for manual mode
        manual_drop_target = Gtk.DropTarget.new(Gio.File, Gdk.DragAction.COPY)
        manual_drop_target.connect("drop", self.on_manual_drop)
        manual_drop_area.add_controller(manual_drop_target)

        # Add the drop box directly to the main vbox
        vbox.append(drop_box)

        # Add a status bar for fallback notifications
        self.status_bar = Gtk.Label()
        self.status_bar.set_halign(Gtk.Align.START)
        self.status_bar.set_margin_start(10)
        self.status_bar.set_margin_top(5)
        self.status_bar.set_margin_bottom(5)
        vbox.append(self.status_bar)

        # Show the window and fix its size based on content
        self.window.present()

        # Force size calculation
        GLib.timeout_add(100, self._fix_window_size)

        # Add CSS provider for basic styling
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(
            b"""
            .heading {
                font-size: 20px;
                font-weight: bold;
            }
            .desc-text {
                font-size: 14px;
                line-height: 1.3;
            }
            """,
            -1,  # Length parameter, -1 means auto-detect length
        )

        # Apply the CSS provider to the display
        display = Gdk.Display.get_default()
        Gtk.StyleContext.add_provider_for_display(
            display, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _fix_window_size(self):
        """Fix the window size after initial layout."""
        if not self.window:
            return False

        # Get the preferred size based on content
        width, height = self.window.get_default_size()
        if width == 0 or height == 0:
            # Get natural size if default size isn't set
            width = max(350, self.window.get_width())
            height = max(300, self.window.get_height())

        # Fix the window size
        self.window.set_default_size(width, height)
        self.window.set_resizable(False)
        return False  # Don't repeat

    def _ensure_desktop_file(self):
        """Create a desktop file to ensure notifications work properly."""
        try:
            # Create desktop file in ~/.local/share/applications
            app_id = self.get_application_id() + ".desktop"
            user_app_dir = os.path.expanduser("~/.local/share/applications")
            os.makedirs(user_app_dir, exist_ok=True)
            desktop_file_path = os.path.join(user_app_dir, app_id)

            # Only create if it doesn't exist
            if not os.path.exists(desktop_file_path):
                with open(desktop_file_path, "w") as f:
                    f.write(
                        f"""[Desktop Entry]
Name=Preview Maker
Comment=Analyze textile patterns in kimono images
Exec=python {os.path.abspath(sys.argv[0])}
Icon=image-x-generic
Terminal=false
Type=Application
Categories=Graphics;
StartupNotify=true
X-GNOME-UsesNotifications=true
"""
                    )
                # Update desktop database
                try:
                    subprocess.run(
                        ["update-desktop-database", user_app_dir], check=False
                    )
                except FileNotFoundError:
                    pass  # Not critical if update-desktop-database is not available
                print(f"Created desktop file at {desktop_file_path}")
        except Exception as e:
            print(f"Warning: Could not create desktop file: {e}")

    def on_draw_circles(self, widget, cr, width, height):
        """Draw circles on the overlay using Cairo."""
        if not self.current_image:
            return

        # Get the actual image dimensions
        img_width, img_height = self.current_image.size

        self.debug_print(f"Drawing area dimensions: {width}x{height}")
        self.debug_print(f"Image dimensions: {img_width}x{img_height}")
        self.debug_print(
            f"Magnification point (normalized): {self.selected_magnification_point_norm}"
        )
        self.debug_print(
            f"Preview point (normalized): {self.selected_preview_point_norm}"
        )

        # First determine the actual image display size within the drawing area
        # (this accounts for aspect ratio preservation)
        display_ratio = img_width / img_height
        widget_ratio = width / height

        if display_ratio > widget_ratio:
            # Image is wider than widget - width constrained
            image_display_width = width
            image_display_height = width / display_ratio
        else:
            # Image is taller than widget - height constrained
            image_display_height = height
            image_display_width = height * display_ratio

        # Calculate the scaling factor from original image to current display
        scale_x = image_display_width / img_width
        scale_y = image_display_height / img_height

        # Calculate letterboxing/pillarboxing offsets to center the image
        x_offset = (width - image_display_width) / 2
        y_offset = (height - image_display_height) / 2

        self.debug_print(
            f"Image display size: {image_display_width}x{image_display_height}"
        )
        self.debug_print(f"Scale factors: {scale_x}, {scale_y}")
        self.debug_print(f"Offsets: {x_offset}, {y_offset}")

        # Draw the effective image area (for debugging)
        cr.set_source_rgba(0.1, 0.1, 0.1, 0.05)  # Very subtle rectangle
        cr.rectangle(x_offset, y_offset, image_display_width, image_display_height)
        cr.fill()

        # Calculate the selection circle size based on the image dimensions
        shortest_dimension = min(img_width, img_height)
        highlight_diameter = int(shortest_dimension * self.selection_ratio)
        highlight_radius = highlight_diameter / 2

        # Check if we have valid normalized points for the magnification circle
        if (
            self.selected_magnification_point_norm
            and self.selected_magnification_point_norm[0] >= 0
            and self.selected_magnification_point_norm[0] <= 1
            and self.selected_magnification_point_norm[1] >= 0
            and self.selected_magnification_point_norm[1] <= 1
        ):
            # Convert normalized coordinates to viewport coordinates
            norm_x, norm_y = self.selected_magnification_point_norm

            # Additional debug info to troubleshoot coordinate issues
            if hasattr(self, "original_mag_x") and hasattr(self, "original_width"):
                print(
                    f"DEBUG COORDS: Original mag point: ({self.original_mag_x}, {self.original_mag_y})"
                )
                print(
                    f"DEBUG COORDS: Original image dimensions: "
                    f"{self.original_width}x{self.original_height}"
                )
                print(
                    f"DEBUG COORDS: Display image dimensions: {img_width}x{img_height}"
                )
                print(f"DEBUG COORDS: Drawing at normalized: ({norm_x}, {norm_y})")

            # Map from normalized coordinates to pixel positions on displayed image
            draw_x = x_offset + (norm_x * image_display_width)
            draw_y = y_offset + (norm_y * image_display_height)

            self.debug_print(f"Drawing magnification circle at: ({draw_x}, {draw_y})")

            # Draw the magnification circle (green)
            cr.set_source_rgba(0, 1, 0, 0.5)  # Green, semi-transparent

            # Scale the radius based on viewport scale - use the configurable selection size
            circle_radius = highlight_radius * scale_x
            cr.arc(draw_x, draw_y, circle_radius, 0, 2 * 3.14)
            cr.fill()

            # Update pixel coordinates based on current viewport
            pixel_x = int(norm_x * img_width)
            pixel_y = int(norm_y * img_height)
            self.selected_magnification_point = (pixel_x, pixel_y)

        # Check if we have valid normalized preview points
        if (
            self.selected_preview_point_norm
            and self.selected_preview_point_norm[0] >= 0
            and self.selected_preview_point_norm[1] >= 0
        ):
            # Convert normalized coordinates to viewport coordinates
            norm_x, norm_y = self.selected_preview_point_norm

            # Map from normalized coordinates to pixel positions on displayed image
            draw_x = x_offset + (norm_x * image_display_width)
            draw_y = y_offset + (norm_y * image_display_height)

            self.debug_print(f"Drawing preview circle at: ({draw_x}, {draw_y})")

            # Draw the preview circle (blue)
            cr.set_source_rgba(0, 0, 1, 0.5)  # Blue, semi-transparent

            # Scale the radius based on viewport scale - use configurable zoom factor
            # The preview circle radius is the highlight radius times the zoom factor
            circle_radius = highlight_radius * self.zoom_factor * scale_x
            cr.arc(draw_x, draw_y, circle_radius, 0, 2 * 3.14)
            cr.fill()

            # Update pixel coordinates based on current viewport
            pixel_x = int(norm_x * img_width)
            pixel_y = int(norm_y * img_height)
            self.selected_preview_point = (pixel_x, pixel_y)

        # If both circles are visible, draw a line connecting them
        if (
            self.selected_magnification_point_norm
            and self.selected_magnification_point_norm[0] >= 0
            and self.selected_preview_point_norm
            and self.selected_preview_point_norm[0] >= 0
        ):
            # Get the center points of both circles
            mag_norm_x, mag_norm_y = self.selected_magnification_point_norm
            prev_norm_x, prev_norm_y = self.selected_preview_point_norm

            # Map to display coordinates
            mag_draw_x = x_offset + (mag_norm_x * image_display_width)
            mag_draw_y = y_offset + (mag_norm_y * image_display_height)
            prev_draw_x = x_offset + (prev_norm_x * image_display_width)
            prev_draw_y = y_offset + (prev_norm_y * image_display_height)

            # Draw the connecting line
            cr.set_source_rgba(1, 0.5, 0, 0.7)  # Orange, semi-transparent
            cr.set_line_width(2.0)
            cr.move_to(mag_draw_x, mag_draw_y)
            cr.line_to(prev_draw_x, prev_draw_y)
            cr.stroke()

        # If debug mode is enabled, draw the API boundary box only if it's a real API response
        if self.debug_mode and hasattr(self, "gemini_box") and self.gemini_box:
            # Get the original bounding box coordinates from Gemini API
            ox1, oy1, ox2, oy2 = self.gemini_box

            # Print debug info to help diagnose coordinate issues
            print(f"DEBUG: Drawing gemini_box: ({ox1}, {oy1}, {ox2}, {oy2})")
            print(f"DEBUG: Current image dimensions: {img_width}x{img_height}")

            # Check if we need to adjust coordinates for image resizing
            if hasattr(self, "original_width") and img_width != self.original_width:
                # The image might have been resized, adjust coordinates proportionally
                width_ratio = img_width / self.original_width
                height_ratio = img_height / self.original_height
                print(
                    f"DEBUG: Adjusting coordinates with ratios: {width_ratio}, {height_ratio}"
                )

                # Use ratios to adjust the box coordinates to the current image size
                ox1 = int(ox1 * width_ratio)
                oy1 = int(oy1 * height_ratio)
                ox2 = int(ox2 * width_ratio)
                oy2 = int(oy2 * height_ratio)
                print(f"DEBUG: Adjusted gemini_box: ({ox1}, {oy1}, {ox2}, {oy2})")

            # Convert to normalized coordinates
            norm_ox1 = ox1 / img_width
            norm_oy1 = oy1 / img_height
            norm_ox2 = ox2 / img_width
            norm_oy2 = oy2 / img_height
            print(
                f"DEBUG: Normalized gemini_box: ({norm_ox1}, {norm_oy1}, {norm_ox2}, {norm_oy2})"
            )

            # Map to display coordinates
            box_x1 = x_offset + (norm_ox1 * image_display_width)
            box_y1 = y_offset + (norm_oy1 * image_display_height)
            box_x2 = x_offset + (norm_ox2 * image_display_width)
            box_y2 = y_offset + (norm_oy2 * image_display_height)
            print(
                f"DEBUG: Display gemini_box: ({box_x1}, {box_y1}, {box_x2}, {box_y2})"
            )

            # Draw the boundary box
            cr.set_source_rgba(0, 0.5, 1, 0.6)  # Blue, semi-transparent
            cr.set_line_width(2.0)
            cr.rectangle(box_x1, box_y1, box_x2 - box_x1, box_y2 - box_y1)
            cr.stroke()

            # Add a label
            cr.set_source_rgba(0, 0.5, 1, 0.8)  # Brighter blue for text
            cr.rectangle(box_x1, box_y1 - 20, 90, 20)
            cr.fill()

            cr.set_source_rgba(1, 1, 1, 1)  # White text
            cr.select_font_face("Sans", 0, 0)
            cr.set_font_size(12)
            cr.move_to(box_x1 + 5, box_y1 - 5)
            cr.show_text("API-Grenze")
        elif self.debug_mode:
            # Draw an error message when we don't have a valid boundary box but debug mode is on
            cr.select_font_face("Sans", 0, 1)  # 1 = bold
            cr.set_font_size(16)

            # Draw text shadow
            cr.set_source_rgba(0, 0, 0, 0.7)

            # Create a semi-transparent background for the text
            text = "Gemini API failed to provide a valid bounding box"
            text_x = width / 2 - 220  # Approximate center
            text_y = 30

            # Text background
            cr.set_source_rgba(0.8, 0, 0, 0.7)  # Red background
            cr.rectangle(text_x - 5, text_y - 20, 440, 30)
            cr.fill()

            # Text
            cr.set_source_rgba(1, 1, 1, 1)  # White text
            cr.move_to(text_x, text_y)
            cr.show_text(text)

    def on_image_click(self, gesture, n_press, x, y):
        """Handle click on the image."""
        button = gesture.get_current_button()
        state = gesture.get_current_event_state()

        # Get the actual image dimensions
        if self.current_image:
            img_width, img_height = self.current_image.size

            # Get the widget dimensions
            widget = gesture.get_widget()
            widget_width = widget.get_width()
            widget_height = widget.get_height()

            self.debug_print(f"Widget dimensions: {widget_width}x{widget_height}")
            self.debug_print(f"Image dimensions: {img_width}x{img_height}")
            self.debug_print(f"Click at widget coords: ({x}, {y})")

            # Calculate the actual displayed image size (accounting for aspect ratio)
            display_ratio = img_width / img_height
            widget_ratio = widget_width / widget_height

            if display_ratio > widget_ratio:
                # Image is wider than widget - width constrained
                image_display_width = widget_width
                image_display_height = widget_width / display_ratio
            else:
                # Image is taller than widget - height constrained
                image_display_height = widget_height
                image_display_width = widget_height * display_ratio

            # Calculate letterboxing/pillarboxing offsets
            x_offset = (widget_width - image_display_width) / 2
            y_offset = (widget_height - image_display_height) / 2

            self.debug_print(
                f"Display image size: {image_display_width}x{image_display_height}"
            )
            self.debug_print(f"Offsets: {x_offset}, {y_offset}")

            # Check if click is within the actual image area
            if (
                x < x_offset
                or x > (x_offset + image_display_width)
                or y < y_offset
                or y > (y_offset + image_display_height)
            ):
                self.show_notification("Klick außerhalb des Bildbereichs")
                return

            # Adjust coordinates to account for letterboxing/pillarboxing
            image_x = x - x_offset
            image_y = y - y_offset

            # Convert to normalized coordinates (0.0-1.0)
            norm_x = image_x / image_display_width
            norm_y = image_y / image_display_height

            # Convert normalized coordinates to pixel coordinates in original image
            pixel_x = int(norm_x * img_width)
            pixel_y = int(norm_y * img_height)

            self.debug_print(f"Normalized coordinates: ({norm_x:.4f}, {norm_y:.4f})")
            self.debug_print(f"Pixel coordinates: ({pixel_x}, {pixel_y})")

            # Ensure coordinates are within image bounds (redundant check)
            if norm_x < 0 or norm_x > 1 or norm_y < 0 or norm_y > 1:
                self.show_notification("Koordinaten außerhalb des Bildbereichs")
                return

            if (
                button == 1 and state & Gdk.ModifierType.CONTROL_MASK
            ):  # Ctrl + Left click
                # Store both normalized and pixel coordinates
                self.selected_magnification_point_norm = (norm_x, norm_y)
                self.selected_magnification_point = (pixel_x, pixel_y)
                self.show_notification(
                    f"Vorschaupunkt gesetzt bei ({pixel_x}, {pixel_y})"
                )
                self.debug_print(
                    f"Magnification point selected: {self.selected_magnification_point}"
                )
                self.debug_print(
                    f"Normalized: {self.selected_magnification_point_norm}"
                )

            elif button == 1:  # Left click
                # Store both normalized and pixel coordinates
                self.selected_preview_point_norm = (norm_x, norm_y)
                self.selected_preview_point = (pixel_x, pixel_y)
                self.show_notification(
                    f"Vorschaupunkt gesetzt bei ({pixel_x}, {pixel_y})"
                )
                self.debug_print(
                    f"Preview point selected: {self.selected_preview_point}"
                )
                self.debug_print(f"Normalized: {self.selected_preview_point_norm}")
        else:
            # No image loaded
            self.show_notification("Kein Bild geladen")
            return

        # Redraw the circles
        widget = gesture.get_widget()
        widget.queue_draw()

    def _calculate_selection_box(self):
        """Calculate a bounding box for the current magnification point and selection size.
        This is NOT the original API boundary box, but the current selection area.
        """
        if not self.current_image or not self.selected_magnification_point:
            return None

        # Get image dimensions
        width, height = self.current_image.size
        mag_x, mag_y = self.selected_magnification_point

        # Calculate the selection circle radius based on image size
        shortest_dimension = min(width, height)
        selection_diameter = int(shortest_dimension * self.selection_ratio)
        radius = selection_diameter / 2  # Use floating point division

        # Calculate the bounding box coordinates - use precise floating point math
        x1 = max(0, int(mag_x - radius))
        y1 = max(0, int(mag_y - radius))
        x2 = min(width, int(mag_x + radius))
        y2 = min(height, int(mag_y + radius))

        # Ensure the box has the correct dimensions
        if x2 - x1 < selection_diameter:
            # Adjust if we hit the edge - use floating point and convert to int
            if x1 == 0:
                x2 = min(width, int(x1 + selection_diameter))
            else:
                x1 = max(0, int(x2 - selection_diameter))

        if y2 - y1 < selection_diameter:
            # Adjust if we hit the edge - use floating point and convert to int
            if y1 == 0:
                y2 = min(height, int(y1 + selection_diameter))
            else:
                y1 = max(0, int(y2 - selection_diameter))

        return (x1, y1, x2, y2)

    def rerun_detection(self, button):
        """Rerun the detection process with the current settings."""
        if not self.current_image:
            self.show_notification("Kein Bild geladen")
            return

        self.show_notification("Erkennung wird ausgeführt...")

        # Get the custom prompt from the text view
        custom_prompt = None
        if hasattr(self, "prompt_entry_view") and self.prompt_entry_view:
            buffer = self.prompt_entry_view.get_buffer()
            start_iter = buffer.get_start_iter()
            end_iter = buffer.get_end_iter()
            text = buffer.get_text(start_iter, end_iter, True)

            # Only use the custom prompt if it's not the placeholder and not empty
            if text.strip() and not self.is_placeholder_visible:
                custom_prompt = text
            else:
                print("Using default prompt from user_prompt.md")

        # Default target type
        target_type = DEFAULT_TARGET_TYPE

        print(f"Running detection with target type: {target_type}")
        if custom_prompt:
            print(f"Using custom prompt from entry: {custom_prompt[:50]}...")

        # Store the custom prompt for later use
        self.custom_prompt = custom_prompt

        # Create a thread for the detection to avoid blocking the UI
        detection_thread = threading.Thread(
            target=self._run_detection_thread,
            args=(self.current_image, target_type),
        )
        detection_thread.daemon = True
        detection_thread.start()

    def _run_detection_thread(self, image, target_type):
        """Run the detection in a separate thread."""
        try:
            # Get the custom prompt if it exists
            custom_prompt = None
            if hasattr(self, "custom_prompt") and self.custom_prompt:
                custom_prompt = self.custom_prompt
                # Replace {target_type} with the actual value
                custom_prompt = custom_prompt.replace("{target_type}", target_type)

            # Call the gemini detector with the custom prompt
            interesting_area, raw_box, description = (
                gemini_analyzer.identify_interesting_textile(
                    image, custom_prompt, target_type
                )
            )

            # Store the raw boundary from Gemini for debug overlay
            # Only store if we got a real response from the API (not a fallback)
            if raw_box:
                # Store the original raw bounding box to debug inconsistencies
                self.gemini_box = raw_box
                # Print additional debug info to help identify coordinate issues
                x1, y1, x2, y2 = raw_box
                print(f"DEBUG: Raw gemini_box: ({x1}, {y1}, {x2}, {y2})")
                print(f"DEBUG: Image dimensions: {image.size[0]}x{image.size[1]}")
                print("Received valid boundary box from Gemini API")
                # Clear any previous API failure notification state
                self._notification_timestamps.pop(
                    "Gemini API failed to provide a valid bounding box", None
                )
            else:
                # If we didn't get a raw_box, clear any previous box to avoid showing stale data
                if hasattr(self, "gemini_box"):
                    print("No valid boundary from Gemini API, clearing debug overlay")
                    self.gemini_box = None

                # Send a notification if debug mode is on - but only once per detection attempt
                if hasattr(self, "debug_mode") and self.debug_mode:
                    error_message = "Gemini API failed to provide a valid bounding box"
                    print(error_message)
                    # Use idle_add to ensure notification happens in the main thread
                    GLib.idle_add(
                        self.show_notification,
                        error_message,
                        5,  # Show for 5 seconds
                        True,  # Use desktop notification
                    )

            # Update the description in the UI if one was returned
            if description:
                GLib.idle_add(self._update_description_in_ui, description)

            # Update magnification and preview points based on the interesting area
            if interesting_area:
                x1, y1, x2, y2 = interesting_area
                width, height = image.size

                # Validate the coordinates to ensure they're within image bounds
                # and in the correct order (i.e., x1 < x2 and y1 < y2)
                x1 = max(0, min(width - 1, x1))
                y1 = max(0, min(height - 1, y1))
                x2 = max(x1 + 1, min(width, x2))
                y2 = max(y1 + 1, min(height, y2))

                # Set the magnification point to the center of the interesting area
                mag_x = (x1 + x2) / 2
                mag_y = (y1 + y2) / 2

                # Convert to integers at the end of calculation
                mag_x = int(mag_x)
                mag_y = int(mag_y)

                # Set the normalized coordinates
                norm_mag_x = mag_x / width
                norm_mag_y = mag_y / height

                # IMPORTANT: Store these for debugging
                self.original_mag_x = mag_x
                self.original_mag_y = mag_y
                self.original_width = width
                self.original_height = height

                # Store the normalized coordinates for circle drawing
                self.selected_magnification_point_norm = (norm_mag_x, norm_mag_y)

                # Calculate the preview point - fixed point in top left quadrant
                preview_x = int(width * 0.125)
                preview_y = int(height * 0.125)
                norm_preview_x = preview_x / width
                norm_preview_y = preview_y / height
                self.selected_preview_point_norm = (norm_preview_x, norm_preview_y)

                print(f"Gemini API returned boundary box: {interesting_area}")
                print(f"Set magnification point at: ({mag_x}, {mag_y})")
                print(f"Normalized magnification: ({norm_mag_x}, {norm_mag_y})")
                print(f"Set preview point at: ({preview_x}, {preview_y})")
                print(f"Normalized preview: ({norm_preview_x}, {norm_preview_y})")

                # Calculate the area percentage for debugging
                box_width = x2 - x1
                box_height = y2 - y1
                area_percentage = (box_width * box_height) / (width * height) * 100
                self.debug_print(f"Bounding box area: {area_percentage:.2f}% of image")

            # Redraw the circle area
            GLib.idle_add(lambda: self.circle_area and self.circle_area.queue_draw())

            # Show a more informative notification based on detection success
            if raw_box:
                GLib.idle_add(
                    self.show_notification,
                    "Erkennung abgeschlossen: Interessensbereich erfolgreich identifiziert.",
                    2,
                    True,
                )
            else:
                GLib.idle_add(
                    self.show_notification,
                    "Erkennung abgeschlossen: Konnte keinen spezifischen Bereich identifizieren.",
                    2,
                    True,
                )
        except Exception as e:
            print(f"Error in detection thread: {e}")
            GLib.idle_add(
                self.show_notification, f"Fehler bei der Erkennung: {e}", 5, True
            )

    def apply_manual_changes(self, button):
        """Apply changes from manual mode."""
        # Validate that we have valid coordinates
        if not self.current_image:
            self.show_notification("No image loaded")
            return

        if not self.selected_magnification_point or not self.selected_preview_point:
            self.show_notification("Please select magnification and preview points")
            return

        # Validate that the coordinates make sense
        width, height = self.current_image.size
        mag_x, mag_y = self.selected_magnification_point
        preview_x, preview_y = self.selected_preview_point

        if mag_x < 0 or mag_y < 0 or mag_x >= width or mag_y >= height:
            self.show_notification("Magnification point is outside image bounds")
            return

        if preview_x < 0 or preview_y < 0 or preview_x >= width or preview_y >= height:
            self.show_notification("Preview point is outside image bounds")
            return

        # Make sure we have the current directory set
        if not self.current_dir and self.current_image_path:
            self.current_dir = os.path.dirname(self.current_image_path)
            print(f"Setting current directory to: {self.current_dir}")

        # Calculate the selection box based on current point and settings
        interesting_area = self._calculate_selection_box()

        if not interesting_area:
            self._show_error("Failed to calculate selection box from points.")
            return

        # Determine if we have a valid gemini_box for debug overlay
        show_debug_overlay = False
        if self.debug_mode and hasattr(self, "gemini_box") and self.gemini_box:
            show_debug_overlay = True
            print("Using Gemini API boundary box in debug overlay")
        elif self.debug_mode:
            print("Debug mode is on but no valid Gemini API boundary box available")

        # Create the processed image for display (with debug overlay if enabled and available)
        self.processed_image_with_debug = image_processor.create_highlighted_image(
            self.current_image,
            interesting_area,
            preview_center=self.selected_preview_point,
            selection_ratio=self.selection_ratio,
            zoom_factor=self.zoom_factor,
            show_debug_overlay=show_debug_overlay,
        )

        # Create the processed image for saving (never with debug overlay)
        self.processed_image = image_processor.create_highlighted_image(
            self.current_image,
            interesting_area,
            preview_center=self.selected_preview_point,
            selection_ratio=self.selection_ratio,
            zoom_factor=self.zoom_factor,
            show_debug_overlay=False,
        )

        # Update the preview if we have a result
        if self.processed_image_with_debug and hasattr(self, "output_picture"):
            # Convert PIL Image to GdkPixbuf
            # For display, use the version with debug info if available
            display_image = self.processed_image_with_debug
            width, height = display_image.size

            # Create an empty pixbuf of the right size
            pixbuf = GdkPixbuf.Pixbuf.new(
                GdkPixbuf.Colorspace.RGB, True, 8, width, height
            )

            # Convert the PIL image to bytes and load into the pixbuf
            image_bytes = display_image.tobytes()
            pixbuf.read_pixel_bytes().append(image_bytes)

            # Set the pixbuf to the picture widget
            self.output_picture.set_pixbuf(pixbuf)

        self.show_notification("Änderungen angewendet")

    def _show_error(self, error_message):
        """Show an error message notification."""
        self.show_notification(
            f"Error: {error_message}", 5, True
        )  # Use desktop notification for errors
        self.processing = False

        # Continue with next image despite error
        if self.image_queue:
            self.process_next_image()
        else:
            if self.progress_bar:
                self.progress_bar.set_visible(False)

        return False  # Important for GLib.idle_add

    def _show_ai_installation_instructions(self, container=None):
        """Show installation instructions for the AI package."""
        install_info = Gtk.Label()
        install_info.set_markup(
            "<b>Installationsanweisungen:</b>\n"
            "1. Installieren Sie das Gemini API-Paket: <tt>pip install google-generativeai</tt>\n"
            "2. Setzen Sie Ihren API-Schlüssel in der Umgebung: <tt>export GEMINI_API_KEY=your_key_here</tt>\n"
            "   Oder erstellen Sie eine .env-Datei mit: <tt>GEMINI_API_KEY=your_key_here</tt>"
        )
        install_info.set_wrap(True)
        install_info.set_halign(Gtk.Align.START)

        # If container is provided, add to it, otherwise assume it's a standalone dialog
        if container:
            container.append(install_info)
        else:
            # Create a dialog window
            dialog = Gtk.Window()
            dialog.set_title("AI Installation Instructions")
            dialog.set_resizable(True)
            dialog.set_size_request(500, 300)

            # Main box
            main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            main_box.set_margin_top(20)
            main_box.set_margin_bottom(20)
            main_box.set_margin_start(20)
            main_box.set_margin_end(20)
            dialog.set_child(main_box)

            # Add the instructions
            main_box.append(install_info)

            # Close button
            close_button = Gtk.Button.new_with_label("Close")
            close_button.set_halign(Gtk.Align.END)
            close_button.set_margin_top(20)
            close_button.connect("clicked", lambda button: dialog.destroy())
            main_box.append(close_button)

            # Show dialog
            dialog.present()

    def on_debug_toggled(self, checkbox):
        """Handle toggling of the debug checkbox."""
        was_debug_on = self.debug_mode
        self.debug_mode = checkbox.get_active()
        print(f"Debug checkbox toggled - debug mode set to: {self.debug_mode}")

        # Save the debug setting to config
        try:
            config.update_config("ui", "debug_mode", self.debug_mode)
        except Exception as e:
            print(f"Failed to save debug setting: {e}")

        # Just redraw the overlay immediately if we have points set
        if self.circle_area:
            self.circle_area.queue_draw()

        # Reprocess the image with new setting if we have a magnification point set
        if (
            hasattr(self, "selected_magnification_point")
            and self.selected_magnification_point
            and self.selected_magnification_point[0] >= 0
            and self.selected_magnification_point[1] >= 0
        ):
            self.apply_manual_changes(None)

    def on_selection_size_changed(self, scale):
        """Handle changes to the selection size slider."""
        self.selection_ratio = scale.get_value()
        self.debug_print(f"Selection size ratio set to: {self.selection_ratio}")

        # Save the setting to config
        config.update_config(
            "image_processing", "selection_ratio", self.selection_ratio
        )

        # Update the display immediately
        if self.circle_area:
            self.circle_area.queue_draw()

    def on_zoom_factor_changed(self, scale):
        """Handle changes to the zoom factor slider."""
        self.zoom_factor = scale.get_value()
        self.debug_print(f"Zoom factor set to: {self.zoom_factor}")

        # Save the setting to config
        config.update_config("image_processing", "zoom_factor", self.zoom_factor)

        # Update the display immediately
        if self.circle_area:
            self.circle_area.queue_draw()

    def reset_prompt_to_default(self, button):
        """Reset the prompt to the default template."""
        try:
            # Load only the user part of the prompt
            with open(DEFAULT_PROMPT_FILE, "w", encoding="utf-8") as f:
                f.write(config.DEFAULT_USER_PROMPT)

            if hasattr(self, "prompt_entry_view") and self.prompt_entry_view:
                self.prompt_entry_view.get_buffer().set_text(config.DEFAULT_USER_PROMPT)
            self.show_notification("Benutzeraufforderung auf Standard zurückgesetzt")
        except Exception as e:
            self.show_notification(f"Fehler beim Zurücksetzen der Aufforderung: {e}")

    def save_prompt_as_default(self, button):
        """Save the current prompt as the default one."""
        if hasattr(self, "prompt_entry_view") and self.prompt_entry_view:
            buffer = self.prompt_entry_view.get_buffer()
            start_iter = buffer.get_start_iter()
            end_iter = buffer.get_end_iter()
            prompt_text = buffer.get_text(start_iter, end_iter, True)

            # Save only the user part (the instructions, not the COORDS/FORMAT part)
            try:
                with open(DEFAULT_PROMPT_FILE, "w", encoding="utf-8") as f:
                    f.write(prompt_text)
                self.show_notification("Benutzeraufforderung als Standard gespeichert")
            except Exception as e:
                self.show_notification(f"Fehler beim Speichern der Aufforderung: {e}")
                print(f"Error saving prompt: {e}")

    def _update_description_in_ui(self, description):
        """Update the description label in the UI (called from the main thread)."""
        if hasattr(self, "description_label") and self.description_label:
            # Make the description more noticeable by adding a prefix
            if description:
                # Trim excessively long descriptions
                if len(description) > 500:
                    description = description[:497] + "..."

                display_text = f"AI: {description}"
                self.description_label.set_text(display_text)
                self.description_label.set_tooltip_text(description)

                # Log to console for debugging
                print(f"Updated UI with description: {description}")

                # Highlight using a notification too
                if hasattr(self, "show_notification"):
                    self.show_notification("Beschreibung von Gemini KI erhalten", 2)
            else:
                self.description_label.set_text("No description available from AI")
        return False  # For GLib.idle_add

    def show_advanced_settings(self, button):
        """Open a popup window with advanced settings like API debug and custom prompt options."""
        # Create a new dialog window
        dialog = Gtk.Window()
        dialog.set_title("Advanced Settings")
        dialog.set_resizable(True)

        # Set a minimum size but no fixed size, allowing content-based sizing
        dialog.set_size_request(500, 400)

        # Main vertical box for all settings
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        dialog.set_child(main_box)

        # API Debug checkbox
        debug_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        debug_checkbox = Gtk.CheckButton.new_with_label("Debug Mode")
        debug_checkbox.set_active(self.debug_mode)
        debug_checkbox.connect("toggled", self.on_debug_toggled)
        debug_box.append(debug_checkbox)
        main_box.append(debug_box)

        # API Boundary Label
        api_boundary_label = Gtk.Label()
        api_boundary_label.set_markup("<b>API-Einstellungen</b>")
        api_boundary_label.set_halign(Gtk.Align.START)
        api_boundary_label.set_margin_top(10)
        main_box.append(api_boundary_label)

        # API Boundary checkbox
        boundary_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        boundary_checkbox = Gtk.CheckButton.new_with_label("API-Grenzrahmen anzeigen")
        boundary_checkbox.set_tooltip_text(
            "Show the raw bounding box returned by Gemini API"
        )
        boundary_checkbox.set_active(
            self.debug_mode
        )  # Use debug mode value for this too
        boundary_checkbox.connect("toggled", self.on_debug_toggled)
        boundary_box.append(boundary_checkbox)
        main_box.append(boundary_box)

        # Installation instructions
        if not GENAI_AVAILABLE:
            self._show_ai_installation_instructions(main_box)

        # Prompt Editor Section
        prompt_label = Gtk.Label()
        prompt_label.set_markup("<b>Benutzerdefinierte Aufforderung</b>")
        prompt_label.set_halign(Gtk.Align.START)
        prompt_label.set_margin_top(20)
        main_box.append(prompt_label)

        # Prompt description/info
        prompt_info_label = Gtk.Label()
        prompt_info_label.set_markup(
            "Bearbeiten Sie den Benutzeranteil der Aufforderung für die Erkennung. Die technischen "
            "Formatierungsanweisungen werden separat verwaltet.\nVerwenden Sie {target_type} als "
            "Platzhalter für den Zieltyp."
        )
        prompt_info_label.set_wrap(True)
        prompt_info_label.set_halign(Gtk.Align.START)
        prompt_info_label.set_margin_bottom(10)
        main_box.append(prompt_info_label)

        # Text view with scrollbars for custom prompt
        prompt_scroll = Gtk.ScrolledWindow()
        prompt_scroll.set_vexpand(True)
        prompt_scroll.set_hexpand(True)
        prompt_scroll.set_min_content_height(100)  # Increased for better usability

        # Add simple margins to the scroll window
        prompt_scroll.set_margin_top(8)
        prompt_scroll.set_margin_bottom(8)
        prompt_scroll.set_margin_start(8)
        prompt_scroll.set_margin_end(8)

        # Use the helper method to setup the prompt text view
        self._setup_prompt_text_view(prompt_scroll, dialog)

        # Add the scrolled window with the prompt text view to the main box
        main_box.append(prompt_scroll)

        # Add a box for prompt control buttons
        prompt_buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        prompt_buttons_box.set_margin_top(8)
        prompt_buttons_box.set_halign(Gtk.Align.END)

        # Add reset button
        reset_button = Gtk.Button(label="Zurücksetzen")
        reset_button.connect(
            "clicked", lambda btn: self.reset_custom_prompt(btn, self.prompt_entry_view)
        )
        reset_button.set_margin_end(8)
        prompt_buttons_box.append(reset_button)

        # Add save button
        save_button = Gtk.Button(label="Speichern")
        save_button.connect(
            "clicked", lambda btn: self.save_custom_prompt(btn, self.prompt_entry_view)
        )
        save_button.add_css_class("suggested-action")  # Highlight this button
        prompt_buttons_box.append(save_button)

        main_box.append(prompt_buttons_box)

        # Present the dialog
        dialog.present()

    def reset_custom_prompt(self, button, text_view):
        """Reset the prompt to the default template."""
        buffer = text_view.get_buffer()
        buffer.set_text(config.DEFAULT_USER_PROMPT)
        self.show_notification("Prompt reset to default template")

    def save_custom_prompt(self, button, text_view):
        """Save the custom prompt from the text view."""
        buffer = text_view.get_buffer()
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        prompt_text = buffer.get_text(start_iter, end_iter, True)

        if prompt_text.strip():
            try:
                with open(DEFAULT_PROMPT_FILE, "w", encoding="utf-8") as f:
                    f.write(prompt_text)
                self.show_notification("Custom prompt saved")
            except Exception as e:
                self.show_notification(f"Fehler beim Speichern der Aufforderung: {e}")
        else:
            self.show_notification("Prompt is empty, not saving")

    def process_image(self, image_path):
        """Start processing the image in a separate thread."""
        # Mark that we're processing
        self.processing = True
        self.show_notification(f"Processing {os.path.basename(image_path)}...")

        # Load the image in a background thread
        thread = threading.Thread(target=self._process_image_thread, args=(image_path,))
        thread.daemon = True
        thread.start()

    def _process_image_thread(self, image_path):
        """Process an image in a background thread."""
        try:
            GLib.idle_add(
                self.show_notification,
                f"Processing {os.path.basename(image_path)}...",
                2,
            )

            # Store the current image path
            self.current_image_path = image_path
            self.current_dir = os.path.dirname(image_path)

            # Open the image with PIL
            self.current_image = Image.open(image_path)
            print(f"Processing image: {image_path}")
            print(f"Current directory: {self.current_dir}")

            width, height = self.current_image.size
            print(f"Image dimensions: {width}x{height}")

            # Keep RGBA mode when possible - only convert to RGB when sending to Gemini API
            # We'll use a copy for the Gemini API to avoid modifying the original

            # Check if we have manually selected points
            if (
                hasattr(self, "selected_magnification_point")
                and self.selected_magnification_point
                and self.selected_magnification_point[0] >= 0
                and self.selected_magnification_point[1] >= 0
            ):
                # Use manually selected points
                mag_x, mag_y = self.selected_magnification_point
                preview_x, preview_y = (
                    self.selected_preview_point
                    if self.selected_preview_point
                    else (mag_x + 128, mag_y + 128)
                )

                print(f"Magnification point: ({mag_x}, {mag_y})")
                print(f"Preview point: ({preview_x}, {preview_y})")

                # Calculate the selection box based on current point and settings
                interesting_area = self._calculate_selection_box()

                # Calculate radius regardless of whether interesting_area exists
                shortest_dimension = min(width, height)
                selection_diameter = int(shortest_dimension * self.selection_ratio)
                radius = selection_diameter / 2

                # If calculation failed, fallback to something reasonable
                if not interesting_area:
                    # Use the radius calculated above
                    x1 = max(0, mag_x - radius)
                    y1 = max(0, mag_y - radius)
                    x2 = min(width, mag_x + radius)
                    y2 = min(height, mag_y + radius)
                    interesting_area = (x1, y1, x2, y2)

                print(f"Using manually selected area: {interesting_area}")

                # For the debug overlay, we'll use the actual Gemini box if available
                # or the calculated box if not
                debug_box = (
                    self.gemini_box if hasattr(self, "gemini_box") else interesting_area
                )

                # Create a processed image with the highlight, passing the configurable parameters
                # For display, we may want to show debug overlay
                self.processed_image_with_debug = (
                    image_processor.create_highlighted_image(
                        self.current_image,
                        interesting_area,
                        preview_center=(preview_x, preview_y),
                        selection_ratio=self.selection_ratio,
                        zoom_factor=self.zoom_factor,
                        show_debug_overlay=self.debug_mode and debug_box is not None,
                    )
                )

                # For saving, we never want the debug overlay
                self.processed_image = image_processor.create_highlighted_image(
                    self.current_image,
                    interesting_area,
                    preview_center=(preview_x, preview_y),
                    selection_ratio=self.selection_ratio,
                    zoom_factor=self.zoom_factor,
                    show_debug_overlay=False,  # Never show debug overlay in saved image
                )

            else:
                # Use Gemini API to identify interesting textile parts
                print("No valid manual selection, using Gemini API")

                # For Gemini API, we need to make a copy that might need RGB conversion
                gemini_image = self.current_image
                if gemini_image.mode == "RGBA":
                    # Only convert the copy to RGB for the API
                    gemini_image = gemini_image.copy().convert("RGB")

                interesting_area, raw_box, description = (
                    gemini_analyzer.identify_interesting_textile(gemini_image)
                )

                # Store the original Gemini API boundary box for debug overlay
                self.gemini_box = interesting_area

                # Store the raw boundary box
                self.raw_gemini_box = raw_box

                # Store the description
                self.gemini_description = description

                # Update the description in the UI if we're in a manual mode window
                # (needs to be done in the main thread)
                if description:
                    GLib.idle_add(self._update_description_in_ui, description)

                if raw_box:
                    print(f"Raw Gemini box before adjustments: {self.raw_gemini_box}")
                    # Clear any previous API failure notification state
                    self._notification_timestamps.pop(
                        "Gemini API failed to provide a valid bounding box", None
                    )
                else:
                    # Send a notification if debug mode is on and we didn't get a valid bounding box
                    if hasattr(self, "debug_mode") and self.debug_mode:
                        error_message = (
                            "Gemini API failed to provide a valid bounding box"
                        )
                        print(error_message)
                        # Use idle_add to ensure notification happens in the main thread
                        GLib.idle_add(
                            self.show_notification,
                            error_message,
                            5,  # Show for 5 seconds
                            True,  # Use desktop notification
                        )

                if description:
                    print(f"Gemini description: {description}")

                # Determine if we have a valid gemini_box for debug overlay
                show_debug_overlay = False
                if self.debug_mode and raw_box:
                    show_debug_overlay = True
                    print("Using Gemini API boundary box in debug overlay")
                elif self.debug_mode:
                    print(
                        "Debug mode is on but no valid Gemini API boundary box available"
                    )

                # Create a processed image with the highlight - use original image to preserve quality
                # For display, we may want to show debug overlay
                self.processed_image_with_debug = (
                    image_processor.create_highlighted_image(
                        self.current_image,
                        interesting_area,
                        selection_ratio=self.selection_ratio,
                        zoom_factor=self.zoom_factor,
                        show_debug_overlay=show_debug_overlay,
                    )
                )

                # For saving, we never want the debug overlay
                self.processed_image = image_processor.create_highlighted_image(
                    self.current_image,
                    interesting_area,
                    selection_ratio=self.selection_ratio,
                    zoom_factor=self.zoom_factor,
                    show_debug_overlay=False,  # Never show debug overlay in saved image
                )

            # Show notification about AI status
            if not gemini_analyzer.AI_ENABLED:
                # Remove desktop notification but keep console logging
                print(
                    "Using fallback mode (no Gemini AI). Install google-generativeai package for AI features."
                )
                # Comment out or remove the notification
                # GLib.idle_add(
                #     self.show_notification,
                #     "Using fallback mode (no Gemini AI). Install google-generativeai package for AI features.",
                #     5,
                # )

            # Save debug image with red dot at the interesting spot
            debug_path = image_processor.save_debug_image(
                self.current_image,
                interesting_area,
                image_path,
                debug_dir=DEBUG_DIR,
                current_dir=self.current_dir,
            )
            print(f"Debug image saved to: {debug_path}")

            # Save the processed image
            output_path = image_processor.save_processed_image(
                self.processed_image,  # Use the clean version without debug overlay for saving
                image_path,
                output_dir=PREVIEWS_DIR,
                current_dir=self.current_dir,
            )
            print(f"Processed image saved to: {output_path}")

            # Show completion notification with desktop notification and file path for opening
            if output_path:  # Add a check to ensure output_path is not None
                filename = os.path.basename(output_path)
                GLib.idle_add(
                    self.show_notification,
                    f"Image processing complete: {filename}",
                    3,
                    True,  # Use desktop notification for completion
                    output_path,  # Pass the file path for opening
                )
            else:
                GLib.idle_add(
                    self.show_notification,
                    "Image processing complete",
                    3,
                    True,  # Use desktop notification for completion
                )

            # Update the UI on the main thread
            GLib.idle_add(self._processing_complete)

        except Exception as e:
            GLib.idle_add(self._show_error, str(e))

    def _processing_complete(self):
        """Called when processing is complete to update the UI."""
        # Enable any disabled buttons
        if hasattr(self, "buttons"):
            for button in self.buttons:
                button.set_sensitive(True)

        # Update the preview if we have a result
        if self.processed_image and hasattr(self, "output_picture"):
            # For display, use the version with debug info if available
            display_image = (
                self.processed_image_with_debug
                if hasattr(self, "processed_image_with_debug")
                and self.processed_image_with_debug
                else self.processed_image
            )
            width, height = display_image.size

            # Create an empty pixbuf of the right size
            pixbuf = GdkPixbuf.Pixbuf.new(
                GdkPixbuf.Colorspace.RGB, True, 8, width, height
            )

            # Convert the PIL image to bytes
            image_bytes = display_image.tobytes()
            pixbuf.read_pixel_bytes().append(image_bytes)

            # Set the pixbuf to the picture widget
            self.output_picture.set_pixbuf(pixbuf)

        # Reset processing state
        self.processing = False

        # Update progress notification
        if self.image_queue:
            total = len(self.image_queue) + 1  # +1 for the current image
            progress = 1 - (len(self.image_queue) / total)
            percent = int(progress * 100)
            self.show_notification(f"Verarbeite {percent}% der Bilder")

            # Process the next image
            self.process_next_image()
        else:
            # Don't include file path here since it's a summary notification
            self.show_notification("Alle Bilder verarbeitet", 3, True)

        if self.spinner:
            self.spinner.stop()
        return False  # Important for GLib.idle_add

    def process_next_image(self):
        """Process the next image in the queue."""
        if not self.image_queue:
            self.show_notification(
                "Alle Bilder verarbeitet", 3, True
            )  # Use desktop notification for completion
            return

        # Get the next image path
        image_path = self.image_queue.pop(0)
        self.current_image_path = image_path
        self.process_image(image_path)

        # Show progress through notifications instead of progress bar
        total = len(self.image_queue) + 1  # +1 for the current image
        progress = 1 - (len(self.image_queue) / total)
        percent = int(progress * 100)
        self.show_notification(f"Verarbeite {percent}% der Bilder")

    def process_dropped_file(self, file):
        """Process a dropped file or directory."""
        file_path = file.get_path()
        if not file_path:
            self.show_notification("Ungültige Datei")
            return False

        # Remember the directory of the dropped file/folder
        if os.path.isdir(file_path):
            self.current_dir = file_path
        else:
            self.current_dir = os.path.dirname(file_path)

        # Clear any existing image queue
        self.image_queue = []

        # Check if it's a directory or a file
        if os.path.isdir(file_path):
            # Directory dropped, look for image files
            image_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".gif"]

            for root, _, files in os.walk(file_path):
                for file_name in files:
                    ext = os.path.splitext(file_name)[1].lower()
                    if ext in image_extensions:
                        self.image_queue.append(os.path.join(root, file_name))

            if not self.image_queue:
                self.show_notification("Keine Bilder im Verzeichnis gefunden")
                return False

            # Start processing the first image
            count = len(self.image_queue)
            self.show_notification(f"Verarbeite {count} Bilder...")

            # Setup progress bar
            if self.progress_bar:
                self.progress_bar.set_visible(True)
                self.progress_bar.set_fraction(0)

            self.process_next_image()
            return True

        # Single file dropped, check if it's an image
        ext = os.path.splitext(file_path)[1].lower()
        image_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".gif"]

        if ext in image_extensions:
            self.image_queue.append(file_path)
            self.show_notification("Processing image...")
            self.process_next_image()
            return True

        self.show_notification("Die Datei ist kein Bild")
        return False

    def _show_main_window(self, action, parameter):
        """Action to show the main window when notification is clicked."""
        if self.window:
            self.window.present()
        return False

    def do_shutdown(self):
        """Clean up resources when the application is shutting down."""
        # Uninitialize libnotify
        if Notify.is_initted():
            Notify.uninit()

        # Chain up to parent - with self parameter
        Gtk.Application.do_shutdown(self)

    def on_prompt_focus_in(self, controller):
        """Handle focus-in for prompt textview.

        Args:
            controller: The focus controller that triggered the event
        """
        # Get the text view that triggered the event
        text_view = controller.get_widget()
        if not text_view:
            return

        # Get the view ID if set using Python attribute instead of get_data
        view_id = getattr(text_view, "view_id", None)

        # Get the appropriate placeholder state based on view ID
        if view_id:
            is_placeholder_visible = getattr(
                self, f"is_placeholder_visible_{view_id}", False
            )
        else:
            is_placeholder_visible = getattr(self, "is_placeholder_visible", False)

        # When focused, clear the placeholder text
        if is_placeholder_visible:
            buffer = text_view.get_buffer()
            buffer.set_text("")
            text_view.remove_css_class("placeholder")

            # Update the placeholder state
            if view_id:
                setattr(self, f"is_placeholder_visible_{view_id}", False)
            else:
                self.is_placeholder_visible = False

        # Make sure the text view has focus
        text_view.grab_focus()

    def on_prompt_focus_out(self, controller):
        """Handle focus-out for prompt textview.

        Args:
            controller: The focus controller that triggered the event
        """
        # Get the text view that triggered the event
        text_view = controller.get_widget()
        if not text_view:
            return

        # Get the view ID if set using Python attribute
        view_id = getattr(text_view, "view_id", None)

        # Get the buffer text
        buffer = text_view.get_buffer()
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        text = buffer.get_text(start, end, False)

        # Check if empty - if so, restore placeholder
        if not text.strip():
            # Get the appropriate placeholder text
            if view_id:
                placeholder_text = getattr(
                    self, f"placeholder_text_{view_id}", "[Standard]"
                )
                setattr(self, f"is_placeholder_visible_{view_id}", True)
            else:
                placeholder_text = getattr(self, "placeholder_text", "[Standard]")
                self.is_placeholder_visible = True

            buffer.set_text(placeholder_text)
            text_view.add_css_class("placeholder")

    def on_textview_click(self, gesture, n_press, x, y):
        """Handle click directly on the text view.

        Args:
            gesture: The gesture controller that triggered the event
            n_press: Number of presses (clicks)
            x: X coordinate of the click
            y: Y coordinate of the click

        Returns:
            False to allow event propagation
        """
        # Get the text view that was clicked
        text_view = gesture.get_widget()
        if not text_view:
            return False

        # Get the view ID if set using Python attribute
        view_id = getattr(text_view, "view_id", None)

        # Ensure the text view gets focus
        text_view.grab_focus()

        # If placeholder is visible, clear it on first click
        if view_id:
            is_placeholder_visible = getattr(
                self, f"is_placeholder_visible_{view_id}", False
            )
        else:
            is_placeholder_visible = getattr(self, "is_placeholder_visible", False)

        if is_placeholder_visible:
            buffer = text_view.get_buffer()
            buffer.set_text("")
            text_view.remove_css_class("placeholder")

            # Update placeholder state
            if view_id:
                setattr(self, f"is_placeholder_visible_{view_id}", False)
            else:
                self.is_placeholder_visible = False

        return False  # Allow event propagation

    def on_window_click(self, controller, n_press, x, y):
        """
        Handle click events on the window (for dismissing focus).

        Args:
            controller: The GestureClick controller
            n_press: Number of presses
            x: X-coordinate of the click
            y: Y-coordinate of the click
        """
        # This method is primarily used to dismiss focus from other widgets
        if hasattr(self, "window"):
            self.window.grab_focus()

    def _setup_css_providers(self):
        """Set up all CSS providers for the application.

        This centralizes all CSS styling in one place.
        """
        # Create the main CSS provider
        main_css_provider = Gtk.CssProvider()
        main_css_provider.load_from_data(
            b"""
            .heading {
                font-size: 20px;
                font-weight: bold;
            }
            .description-text {
                font-size: 16px;
                line-height: 1.5;
            }
            .prompt-text {
                font-size: 18px;
                line-height: 1.5;
            }
            textview.placeholder {
                color: alpha(#666666, 0.7);
                font-style: italic;
                font-size: 95%;
            }
            .desc-text {
                font-size: 14px;
                line-height: 1.3;
            }
            """,
            -1,  # Length parameter, -1 means auto-detect length
        )

        # Apply the CSS provider to the display
        display = Gdk.Display.get_default()
        Gtk.StyleContext.add_provider_for_display(
            display, main_css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        return main_css_provider

    def on_auto_drop(self, drop_target, value, x, y):
        """Handle automatic mode drop."""
        self.show_notification("Automatischer Modus aktiviert")
        self.process_dropped_file(value)
        return True

    def on_manual_drop(self, drop_target, value, x, y):
        """Handle manual mode drop."""
        self.show_notification("Manueller Modus aktiviert")
        # Extract the file path from the GLocalFile object
        file_path = value.get_path() if hasattr(value, "get_path") else str(value)
        if file_path:
            # Set the current directory to the directory containing the dropped file
            self.current_dir = os.path.dirname(file_path)
            print(f"Manual mode: Setting current directory to {self.current_dir}")
            self.open_manual_mode_window(file_path)
        return True

    def show_notification(
        self,
        message,
        timeout=3,
        use_desktop_notification=False,
        file_path=None,
        is_error=False,
    ):
        """
        Show a notification to the user.

        Args:
            message: The message to show
            timeout: How long to show the message (in seconds)
            use_desktop_notification: Whether to show a desktop notification (only for important events)
            file_path: Optional path to the file that should be opened when the notification is clicked
            is_error: Whether this is an error notification (for styling)

        Returns:
            True if notification was shown, False otherwise
        """
        # Rate limiting based on message content
        current_time = time.time()
        cooldown_period = 1  # Default 1 second cooldown between identical notifications

        # For the Gemini API failure message, use a longer cooldown
        if "Gemini API failed to provide a valid bounding box" in message:
            cooldown_period = 10  # 10 seconds between Gemini API failure notifications

        # For detection completion messages, use longer cooldown
        if "Erkennung abgeschlossen" in message:
            cooldown_period = 5  # 5 seconds between detection completion notifications

        # Check if we've shown this message recently
        if message in self._notification_timestamps:
            last_time = self._notification_timestamps[message]
            if current_time - last_time < cooldown_period:
                return False  # Skip this notification, it's too soon

        # Update timestamp for this message
        self._notification_timestamps[message] = current_time

        # Now show the notification
        error_prefix = "ERROR: " if is_error else ""
        print(f"Notification: {error_prefix}{message}")

        # Update the status bar if we have one
        self._update_status_bar(message)

        return True

    def _update_status_bar(self, message):
        """Update the status bar with a message."""
        if hasattr(self, "status_bar") and self.status_bar:
            self.status_bar.set_text(message)
        return False

    def _clear_status_bar(self):
        """Clear the status bar message."""
        if hasattr(self, "status_bar") and self.status_bar:
            self.status_bar.set_text("")
        return False

    def open_manual_mode_window(self, file_path):
        """Open a window for manual mode editing."""
        # Load the image
        try:
            image = Image.open(file_path)
            self.current_image = image
            self.current_image_path = file_path

            # Get image dimensions and store them
            img_width, img_height = image.size
            self.original_img_width = img_width
            self.original_img_height = img_height
            print(f"Loaded image with dimensions: {img_width}x{img_height}")

            # Create a new window for manual mode with the updated title format
            manual_window = Gtk.Window(title="Preview Maker - Manual")

            # Make the window automatically fit content with a reasonable max size
            display = Gdk.Display.get_default()
            monitor = display.get_monitors().get_item(0)
            if monitor:
                geometry = monitor.get_geometry()
                screen_width = geometry.width
                screen_height = geometry.height
                max_width = int(screen_width * 0.8)
                max_height = int(screen_height * 0.8)
                window_width = min(max_width, img_width + 400)  # Add space for controls
                window_height = min(max_height, img_height + 100)
                manual_window.set_default_size(window_width, window_height)
            else:
                # Default size if we can't get screen dimensions
                manual_window.set_default_size(1000, 600)

            # Create the two-panel layout
            image_container, controls_box = self._create_ui_layout(manual_window)

            try:
                # Create the image section with overlay
                overlay, circle_area = self._create_image_section(
                    image_container, image, manual_window
                )

                # Create all controls sections
                self._create_description_section(controls_box)
                rerun_button = self._create_prompt_section(controls_box, manual_window)
                self._create_debug_section(controls_box)
                self._add_help_and_buttons(controls_box)

                # Show the window
                manual_window.present()

                # Automatically run detection once when the window is shown
                # Use a short delay to ensure the window is fully rendered
                # Using a source ID that we can store to avoid multiple timers
                self._auto_detection_timer = GLib.timeout_add(
                    500, self._run_initial_detection, rerun_button
                )
            except Exception as inner_e:
                print(f"Error setting up UI components: {inner_e}")
                # Still show the window with an error message
                error_label = Gtk.Label(label=f"Error setting up UI: {inner_e}")
                error_label.set_margin_top(20)
                error_label.set_margin_bottom(20)
                error_label.set_margin_start(20)
                error_label.set_margin_end(20)
                manual_window.set_child(error_label)
                manual_window.present()
                self.show_notification(f"Error setting up UI: {inner_e}", is_error=True)

        except Exception as e:
            print(f"Error opening image: {e}")
            self.show_notification(f"Error opening image: {e}", is_error=True)

    def _run_initial_detection(self, button):
        """Run the initial detection once after window setup and then remove the timer."""
        # Run the detection
        if button and hasattr(self, "rerun_detection"):
            self.rerun_detection(button)

        # Remove the timer so it doesn't run again
        if hasattr(self, "_auto_detection_timer"):
            self._auto_detection_timer = None

        # Return False to ensure the timeout doesn't repeat
        return False

    def _create_ui_layout(self, manual_window):
        """
        Create the two-panel layout structure for the manual mode window.

        Args:
            manual_window: The window to add the layout to

        Returns:
            tuple: (image_container, controls_box) - The two main panels
        """
        # Create main layout as horizontal box
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        hbox.set_margin_top(20)
        hbox.set_margin_bottom(20)
        hbox.set_margin_start(20)
        hbox.set_margin_end(20)

        # Create a container for the image with padding - LEFT SIDE
        image_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        image_container.set_hexpand(True)
        image_container.set_vexpand(True)
        image_container.set_margin_start(12)
        image_container.set_margin_end(12)
        image_container.set_margin_top(12)
        image_container.set_margin_bottom(12)

        hbox.append(image_container)

        # Create a container for the controls with padding - RIGHT SIDE
        controls_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        controls_container.set_margin_start(12)
        controls_container.set_margin_end(12)
        controls_container.set_margin_top(12)
        controls_container.set_margin_bottom(12)

        # Create a vertical box for all UI controls
        controls_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        controls_box.set_size_request(350, -1)  # Set minimum width for controls
        controls_box.set_vexpand(True)  # Make sure it uses full height
        controls_box.set_margin_start(8)
        controls_box.set_margin_end(8)
        controls_box.set_margin_top(8)
        controls_box.set_margin_bottom(8)

        controls_container.append(controls_box)
        hbox.append(controls_container)

        # Set the main horizontal box as the child of the window
        manual_window.set_child(hbox)

        return image_container, controls_box

    def _create_image_section(self, image_container, image, manual_window):
        """
        Create the image display section with overlay for circle drawing.

        Args:
            image_container: The container to add the image section to
            image: The PIL image to display
            manual_window: The parent window

        Returns:
            tuple: (overlay, circle_area) - References to key UI components
        """
        # Get image dimensions
        img_width, img_height = image.size

        # Get screen dimensions
        display = Gdk.Display.get_default()
        monitor = display.get_monitors().get_item(0)
        if monitor:
            geometry = monitor.get_geometry()
            screen_width = geometry.width
            screen_height = geometry.height
        else:
            # Fallback values if we can't get screen dimensions
            screen_width = 1920
            screen_height = 1080

        # Calculate appropriate window size (80% of screen size maximum)
        max_width = int(screen_width * 0.8)
        max_height = int(screen_height * 0.8)

        # Determine if we need to scale the image
        scale_factor = 1.0
        if img_width > max_width or img_height > max_height:
            # Scale down while preserving aspect ratio
            width_ratio = max_width / img_width
            height_ratio = max_height / img_height
            scale_factor = min(width_ratio, height_ratio)

        # Create a picture widget with keep-aspect-ratio enabled
        picture = Gtk.Picture()
        picture.set_content_fit(Gtk.ContentFit.CONTAIN)  # Preserve aspect ratio
        picture.set_can_shrink(True)  # Allow image to shrink when window resizes

        # Load the image
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.current_image_path)
        texture = Gdk.Texture.new_for_pixbuf(pixbuf)
        picture.set_paintable(texture)

        # Make the picture expand to fill available space
        picture.set_hexpand(True)
        picture.set_vexpand(True)

        # Initialize normalized points to offscreen
        self.selected_magnification_point_norm = (-1.0, -1.0)  # Offscreen
        self.selected_preview_point_norm = (-1.0, -1.0)  # Offscreen

        # Initialize pixel points (we'll still need these for some calculations)
        self.selected_magnification_point = (-200, -200)
        self.selected_preview_point = (-600, -600)

        # Store the original image dimensions for coordinate mapping
        self.display_width = img_width
        self.display_height = img_height
        self.display_scale = scale_factor

        self.debug_print(
            f"Display size: {img_width}x{img_height}, Scale: {scale_factor}"
        )

        # Create an overlay to draw circles on the image
        overlay = Gtk.Overlay()
        overlay.set_child(picture)

        # Create a drawing area for circles
        circle_area = Gtk.DrawingArea()

        # Make the drawing area fill the entire overlay
        circle_area.set_hexpand(True)
        circle_area.set_vexpand(True)

        # Set the drawing function
        circle_area.set_draw_func(self.on_draw_circles)

        # Store a reference to the circle_area for redrawing
        self.circle_area = circle_area

        # Add click gesture for mouse interaction
        click_gesture = Gtk.GestureClick()
        click_gesture.connect("pressed", self.on_image_click)
        circle_area.add_controller(click_gesture)

        overlay.add_overlay(circle_area)

        # Add spinner for Gemini detection
        spinner = Gtk.Spinner()
        spinner.set_size_request(48, 48)
        spinner.set_halign(Gtk.Align.CENTER)
        spinner.set_valign(Gtk.Align.CENTER)
        self.spinner = spinner
        overlay.add_overlay(spinner)

        # Add a frame around the image overlay for better visual separation
        image_frame = Gtk.Frame()
        image_frame.set_child(overlay)
        image_frame.set_hexpand(True)  # Let the image expand horizontally
        image_frame.set_vexpand(True)  # Let the image expand vertically

        image_container.append(image_frame)

        return overlay, circle_area

    def _create_description_section(self, controls_box):
        """
        Create the AI description section for the manual mode window.

        Args:
            controls_box: The container to add the description section to

        Returns:
            Gtk.Frame: The description section frame
        """
        # Create description section
        description_frame = Gtk.Frame()
        description_frame.set_label("AI Description")

        # Use ScrolledWindow for description to allow auto-sizing
        description_scroll = Gtk.ScrolledWindow()
        description_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        description_scroll.set_min_content_height(100)
        description_scroll.set_propagate_natural_height(True)

        self.description_label = Gtk.Label()
        self.description_label.set_valign(Gtk.Align.START)
        self.description_label.set_halign(Gtk.Align.START)
        self.description_label.set_margin_start(12)
        self.description_label.set_margin_end(12)
        self.description_label.set_margin_top(12)
        self.description_label.set_margin_bottom(12)
        self.description_label.set_selectable(True)
        self.description_label.set_wrap(True)
        self.description_label.set_text("Run detection to see Gemini's description")
        self.description_label.add_css_class("description-text")  # Modern GTK4 method
        description_scroll.set_child(self.description_label)
        description_frame.set_child(description_scroll)

        controls_box.append(description_frame)

        return description_frame

    def _create_prompt_section(self, controls_box, window):
        """
        Create the prompt section for customizing detection prompts.

        Args:
            controls_box: The container to add the prompt section to
            window: The parent window for event handling

        Returns:
            Gtk.Button: The rerun detection button
        """
        # Add prompt section with a large text area for customization
        prompt_section = Gtk.Frame()
        prompt_section.set_label("Detection Prompt")
        prompt_section.set_margin_top(16)

        # Create box for prompt controls
        prompt_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        prompt_box.set_margin_start(12)
        prompt_box.set_margin_end(12)
        prompt_box.set_margin_top(12)
        prompt_box.set_margin_bottom(12)

        # Add a section for target type
        target_section = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        target_section.set_margin_bottom(16)

        target_label = Gtk.Label(label="Prompt:")
        target_label.set_halign(Gtk.Align.START)
        target_label.set_margin_end(10)
        # Hide the label since the section is already called prompt
        target_label.set_visible(False)
        target_section.append(target_label)

        # Create a scrollable container for the prompt text view
        prompt_scroll = Gtk.ScrolledWindow()
        prompt_scroll.set_vexpand(True)
        prompt_scroll.set_hexpand(True)
        prompt_scroll.set_min_content_height(100)  # Increased for better usability

        # Add simple margins to the scroll window
        prompt_scroll.set_margin_top(8)
        prompt_scroll.set_margin_bottom(8)
        prompt_scroll.set_margin_start(8)
        prompt_scroll.set_margin_end(8)

        # Use the helper method to setup the prompt text view
        self._setup_prompt_text_view(prompt_scroll, window)

        target_section.append(prompt_scroll)

        # Add the Rerun Detection button next to target type
        rerun_button = Gtk.Button(label="Erkennung erneut ausführen")
        rerun_button.connect("clicked", self.rerun_detection)
        rerun_button.set_margin_start(8)
        target_section.append(rerun_button)

        prompt_box.append(target_section)

        # Add an advanced settings button for API debug and custom prompt
        advanced_button = Gtk.Button.new_with_label("Erweiterte Einstellungen")
        advanced_button.set_halign(Gtk.Align.END)
        advanced_button.connect("clicked", self.show_advanced_settings)
        advanced_button.set_margin_top(8)
        prompt_box.append(advanced_button)

        # Add a note about targeting precision
        targeting_note = Gtk.Label()
        targeting_note.set_markup(
            "<small><i>Für beste Ergebnisse, geben Sie ein einzelnes, eindeutiges Objekt im 'Zieltyp' an, "
            "anstatt allgemeine Kategorien</i></small>"
        )
        targeting_note.set_halign(Gtk.Align.START)
        targeting_note.set_margin_top(4)
        prompt_box.append(targeting_note)

        # Set the prompt box as the child of the prompt section
        prompt_section.set_child(prompt_box)
        controls_box.append(prompt_section)

        # Load the default prompt from file for use in detection
        try:
            with open(DEFAULT_PROMPT_FILE, "r", encoding="utf-8") as f:
                self.default_prompt = f.read()
        except FileNotFoundError:
            # Fallback to a basic prompt if file doesn't exist
            self.default_prompt = (
                "Please analyze this image and identify the most interesting {target_type} area. "
                "Return coordinates of a bounding box as normalized values between 0 and 1 "
                "in the format: x1,y1,x2,y2 where x1,y1 is the top-left corner."
            )

        return rerun_button

    def _create_debug_section(self, controls_box):
        """
        Create the debug controls section for the manual mode window.

        Args:
            controls_box: The container to add the debug section to

        Returns:
            Gtk.Box: The debug section
        """
        # Add debug options section
        debug_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        debug_section.set_margin_bottom(16)  # Increased margin

        # Add a horizontal box for size controls
        size_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # Size label
        size_label = Gtk.Label(label="Auswahlgröße:")
        size_label.set_halign(Gtk.Align.START)
        size_label.set_size_request(100, -1)  # Fixed width for label
        size_box.append(size_label)

        # Add a scale for adjusting the selection circle size
        size_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 0.05, 0.3, 0.01
        )
        size_scale.set_value(self.selection_ratio)
        size_scale.set_hexpand(True)
        size_scale.set_tooltip_text("Adjust the size of the selection circle")
        size_scale.connect("value-changed", self.on_selection_size_changed)
        size_box.append(size_scale)

        debug_section.append(size_box)

        # Add a horizontal box for zoom controls
        zoom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # Zoom label
        zoom_label = Gtk.Label(label="Vergrößerung:")
        zoom_label.set_halign(Gtk.Align.START)
        zoom_label.set_size_request(100, -1)  # Fixed width for label
        zoom_box.append(zoom_label)

        # Add a scale for adjusting the zoom factor
        zoom_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1.5, 5.0, 0.1)
        zoom_scale.set_value(self.zoom_factor)
        zoom_scale.set_hexpand(True)
        zoom_scale.set_tooltip_text("Adjust the zoom factor")
        zoom_scale.connect("value-changed", self.on_zoom_factor_changed)
        zoom_box.append(zoom_scale)

        debug_section.append(zoom_box)

        controls_box.append(debug_section)

        return debug_section

    def _add_help_and_buttons(self, controls_box):
        """
        Add help text and action buttons to the controls panel.

        Args:
            controls_box: The container to add the help text and buttons to

        Returns:
            Gtk.Button: The apply button
        """
        # Add buttons with improved styling
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(8)

        # Add explanatory text on the left side of the button box
        help_text = Gtk.Label()
        help_text.set_markup(
            "<small>Linksklick: Vorschaupunkt setzen (blauer Kreis)\n"
            "Strg+Linksklick: Vergrößerungspunkt setzen (grüner Kreis)</small>"
        )
        help_text.set_halign(Gtk.Align.START)
        help_text.set_hexpand(True)
        button_box.append(help_text)

        # Create styled buttons
        apply_button = Gtk.Button(label="Änderungen anwenden")
        apply_button.connect("clicked", self.apply_manual_changes)
        apply_button.add_css_class("suggested-action")  # Highlight this button

        button_box.append(apply_button)

        controls_box.append(button_box)

        return apply_button

    def _setup_prompt_text_view(self, prompt_scroll, window, view_id=None):
        """Setup a text view for prompt editing with placeholder functionality.

        Args:
            prompt_scroll: The ScrolledWindow that will contain the text view
            window: The parent window for adding the click controller
            view_id: Optional identifier for this text view (for multiple text views)

        Returns:
            The configured TextView widget
        """
        # Create a text view for the prompt with placeholder functionality
        text_view = Gtk.TextView()
        text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        text_view.set_top_margin(8)
        text_view.set_bottom_margin(8)
        text_view.set_left_margin(8)
        text_view.set_right_margin(8)

        # Ensure text view is focusable
        text_view.set_focusable(True)

        # Set appropriate dimensions
        text_view.set_size_request(500, 100)

        # Get the default user prompt
        try:
            with open(DEFAULT_PROMPT_FILE, "r", encoding="utf-8") as f:
                default_user_prompt = f.read()
        except FileNotFoundError:
            default_user_prompt = "Please analyze this image and identify the most interesting {target_type} area."

        # Set up placeholder text and handling
        buffer = text_view.get_buffer()

        # Store references either in specific attributes or instance variables
        if view_id:
            setattr(self, f"prompt_entry_view_{view_id}", text_view)
            setattr(self, f"prompt_buffer_{view_id}", buffer)
            setattr(self, f"is_placeholder_visible_{view_id}", True)
        else:
            self.prompt_entry_view = text_view
            self.prompt_buffer = buffer
            self.is_placeholder_visible = True

        # Use the same shortened placeholder format for consistency
        first_sentence = default_user_prompt.split(".")[0]
        if len(first_sentence) > 50:
            short_placeholder = first_sentence[:50] + "..."
        else:
            short_placeholder = first_sentence

        placeholder_text = f"[Standard] {short_placeholder}"

        # Store the placeholder text
        if view_id:
            setattr(self, f"placeholder_text_{view_id}", placeholder_text)
        else:
            self.placeholder_text = placeholder_text

        buffer.set_text(placeholder_text)
        text_view.add_css_class("placeholder")

        # Store a reference to the view ID with the widget using Python attribute instead of set_data
        if view_id:
            # Instead of text_view.set_data("view_id", view_id)
            setattr(text_view, "view_id", view_id)

        # Add a direct click controller to the text view itself
        text_click_controller = Gtk.GestureClick.new()
        text_click_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        text_click_controller.connect("pressed", self.on_textview_click)
        text_view.add_controller(text_click_controller)

        # Handle focus events with a focus controller
        focus_controller = Gtk.EventControllerFocus.new()
        focus_controller.connect("enter", self.on_prompt_focus_in)
        focus_controller.connect("leave", self.on_prompt_focus_out)
        text_view.add_controller(focus_controller)

        # Add a click controller to the main window to handle unfocus
        if window:
            window_click_controller = Gtk.GestureClick.new()
            window_click_controller.set_propagation_phase(Gtk.PropagationPhase.BUBBLE)
            window_click_controller.connect("pressed", self.on_window_click)
            window.add_controller(window_click_controller)

        # Set the text view as the child of the scroll window
        prompt_scroll.set_child(text_view)

        return text_view


def main():
    """Run the application."""
    app = PreviewMaker()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
