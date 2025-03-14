#!/usr/bin/env python3
"""
Kimono Textile Analyzer - Finds interesting textile patterns in kimono images
using Google Gemini AI and creates a zoomed-in circular overlay.
"""

import os
import sys
import threading

# GTK imports first
import gi

# Image processing imports
from PIL import Image

# Import our custom modules
import gemini_analyzer
import image_processor

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Gio

# Check for optional dependencies
try:
    import google.generativeai as genai

    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print(
        "WARNING: google-generativeai package not installed. "
        "Run 'pip install google-generativeai' to enable AI features."
    )


# Create previews directory if it doesn't exist
PREVIEWS_DIR = "previews"
DEBUG_DIR = os.path.join(PREVIEWS_DIR, "debug")
PROMPTS_DIR = "prompts"
DEFAULT_PROMPT_FILE = os.path.join(PROMPTS_DIR, "gemini_detection.txt")
DEFAULT_TARGET_TYPE = "textile pattern or detail"

os.makedirs(PREVIEWS_DIR, exist_ok=True)
os.makedirs(DEBUG_DIR, exist_ok=True)
os.makedirs(PROMPTS_DIR, exist_ok=True)

# Create default prompt file if it doesn't exist
if not os.path.exists(DEFAULT_PROMPT_FILE):
    with open(DEFAULT_PROMPT_FILE, "w", encoding="utf-8") as f:
        f.write(
            "Please analyze this image and identify the most interesting {target_type} area.\n\n"
            "Look for areas with these characteristics:\n"
            "- Clear visual focal points or points of interest\n"
            "- Detailed patterns or textures\n"
            "- Areas with high contrast or distinctive colors\n"
            "- Unusual or unique elements\n"
            "- Rich details that would benefit from magnification\n\n"
            "Respond with TWO PARTS:\n"
            "1. COORDS: Coordinates as normalized values between 0 and 1 in the format x1,y1,x2,y2\n"
            "   where (x1,y1) is the top-left corner and (x2,y2) is the bottom-right corner.\n"
            "2. DESCRIPTION: A brief description (1-2 sentences) of what you identified and why it's interesting.\n\n"
            "Format your response EXACTLY as:\n"
            "COORDS: x1,y1,x2,y2\n"
            "DESCRIPTION: Your description here."
        )


class KimonoAnalyzer(Gtk.Application):
    """Main application class for the Kimono Textile Analyzer."""

    def __init__(self):
        # Use 0 for FLAGS_NONE to avoid attribute error
        super().__init__(
            application_id="org.example.kimonoanalyzer",
            flags=0,
        )
        self.connect("activate", self.on_activate)
        self.current_image = None
        self.processed_image = None
        self.processing = False
        self.image_queue = []
        self.current_image_path = None
        self.current_dir = None
        self.notification = None
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
        self.selection_ratio = 0.1  # 10% of shortest dimension
        self.zoom_factor = 3.0  # 3x zoom factor
        # Debug mode flag
        self.debug_mode = False
        # Store the description from Gemini
        self.gemini_description = None

    def on_activate(self, app):
        """Initialize the application window and UI components."""
        # Create the main window with updated title
        self.window = Gtk.ApplicationWindow(
            application=app, title="Kimono Textile Analyzer - Dropper"
        )
        self.window.set_default_size(400, 300)  # Better default size

        # Check if Gemini AI is available and show notification if not
        if not GENAI_AVAILABLE:
            # Schedule notification to show after window is displayed
            GLib.timeout_add(1000, self._show_ai_installation_instructions)

        # Create a vertical box for the layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)
        vbox.set_vexpand(True)
        self.window.set_child(vbox)

        # Create a horizontal box for the drop areas
        drop_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        drop_box.set_vexpand(True)
        drop_box.set_hexpand(True)

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
        auto_label = Gtk.Label(label="Auto Mode")
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
        manual_label = Gtk.Label(label="Manual Mode")
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

        # Create notification label (hidden by default)
        self.notification = Gtk.Label(label="")
        self.notification.set_visible(False)
        self.notification.add_css_class("notification")
        vbox.append(self.notification)

        # Notification styling
        notification_css = Gtk.CssProvider()
        notification_css.load_from_data(
            b"""
        .notification {
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 8px;
            border-radius: 4px;
        }
        """
        )
        Gtk.StyleContext.add_provider_for_display(
            display,
            notification_css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        # Create a hidden progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_visible(False)
        vbox.append(self.progress_bar)

        # Show the window
        self.window.present()

    def show_notification(self, message, timeout=3):
        """Show a notification message."""
        if self.notification:
            self.notification.set_text(message)
            self.notification.set_visible(True)

        # Hide notification after timeout
        GLib.timeout_add_seconds(timeout, self._hide_notification)

    def _hide_notification(self):
        """Hide the notification."""
        if self.notification:
            self.notification.set_visible(False)
        return False  # Don't repeat

    def on_auto_drop(self, drop_target, value, x, y):
        """Handle automatic mode drop."""
        self.show_notification("Automatic mode activated")
        self.process_dropped_file(value)
        return True

    def on_manual_drop(self, drop_target, value, x, y):
        """Handle manual mode drop."""
        self.show_notification("Manual mode activated")
        file_path = value.get_path()
        if file_path:
            # Set the current directory to the directory containing the dropped file
            self.current_dir = os.path.dirname(file_path)
            print(f"Manual mode: Setting current directory to {self.current_dir}")
            self.open_manual_mode_window(file_path)
        return True

    def open_manual_mode_window(self, file_path):
        """Open a window for manual mode editing."""
        # Load the image
        image = Image.open(file_path)
        self.current_image = image
        self.current_image_path = file_path

        # Get image dimensions and store them
        img_width, img_height = image.size
        self.original_img_width = img_width
        self.original_img_height = img_height
        print(f"Loaded image with dimensions: {img_width}x{img_height}")

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
        window_width = img_width
        window_height = img_height

        if img_width > max_width or img_height > max_height:
            # Scale down while preserving aspect ratio
            width_ratio = max_width / img_width
            height_ratio = max_height / img_height
            scale_factor = min(width_ratio, height_ratio)

            window_width = int(img_width * scale_factor)
            window_height = int(img_height * scale_factor)

        # Create a new window for manual mode with the updated title format
        manual_window = Gtk.Window(title="Kimono Textile Analyzer - Manual")
        manual_window.set_default_size(window_width, window_height)

        # Initialize normalized points to offscreen
        self.selected_magnification_point_norm = (-1.0, -1.0)  # Offscreen
        self.selected_preview_point_norm = (-1.0, -1.0)  # Offscreen

        # Initialize pixel points (we'll still need these for some calculations)
        self.selected_magnification_point = (-200, -200)
        self.selected_preview_point = (-600, -600)

        # Create a picture widget with keep-aspect-ratio enabled
        picture = Gtk.Picture()
        picture.set_keep_aspect_ratio(True)  # This is crucial for proper scaling
        picture.set_can_shrink(True)  # Allow image to shrink when window resizes

        # Load the image
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(file_path)
        texture = Gdk.Texture.new_for_pixbuf(pixbuf)
        picture.set_paintable(texture)

        # Make the picture expand to fill available space
        picture.set_hexpand(True)
        picture.set_vexpand(True)

        # Store the original image dimensions for coordinate mapping
        self.display_width = img_width
        self.display_height = img_height
        self.display_scale = scale_factor

        print(f"Display size: {img_width}x{img_height}, Scale: {scale_factor}")

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
        self.spinner = Gtk.Spinner()
        self.spinner.set_size_request(48, 48)
        self.spinner.set_halign(Gtk.Align.CENTER)
        self.spinner.set_valign(Gtk.Align.CENTER)
        overlay.add_overlay(self.spinner)

        # Create main layout with increased spacing and margins
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        vbox.set_margin_top(20)
        vbox.set_margin_bottom(20)
        vbox.set_margin_start(20)
        vbox.set_margin_end(20)

        # Add a frame around the image overlay for better visual separation
        image_frame = Gtk.Frame()
        image_frame.set_child(overlay)
        image_frame.set_margin_bottom(12)
        vbox.append(image_frame)

        # Add a description display area
        description_frame = Gtk.Frame()
        description_frame.set_label("AI Description")

        description_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        description_box.set_margin_top(8)
        description_box.set_margin_bottom(8)
        description_box.set_margin_start(8)
        description_box.set_margin_end(8)

        self.description_label = Gtk.Label()
        self.description_label.set_wrap(True)
        self.description_label.set_selectable(True)
        self.description_label.set_xalign(0)  # Left align text
        self.description_label.set_text("Run detection to see Gemini's description")
        self.description_label.add_css_class("description-text")

        description_box.append(self.description_label)
        description_frame.set_child(description_box)
        description_frame.set_margin_bottom(12)
        vbox.append(description_frame)

        # Get the default prompt from file
        try:
            with open(DEFAULT_PROMPT_FILE, "r", encoding="utf-8") as f:
                default_prompt = f.read()
        except FileNotFoundError:
            # Fallback to a basic prompt if file doesn't exist
            default_prompt = (
                "Please analyze this image and identify the most interesting {target_type} area. "
                "Return only the coordinates of a bounding box around this area as normalized values "
                "between 0 and 1 in the format: x1,y1,x2,y2 where x1,y1 is the top-left corner and "
                "x2,y2 is the bottom-right corner."
            )

        # Create prompt customization section with improved styling
        prompt_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        prompt_section.set_margin_bottom(16)

        # Add a section for target type
        target_section = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        target_section.set_margin_bottom(8)

        target_label = Gtk.Label(label="Target Type:")
        target_label.set_halign(Gtk.Align.START)
        target_label.set_margin_end(10)
        target_section.append(target_label)

        # Create an entry for target type with better styling
        self.target_entry = Gtk.Entry()
        self.target_entry.set_text(DEFAULT_TARGET_TYPE)
        self.target_entry.set_placeholder_text(
            "e.g. flower, button, specific symbol, small detail"
        )
        self.target_entry.set_tooltip_text(
            "Enter a specific object or detail to look for - be as precise as possible.\n"
            "Examples: 'floral emblem', 'geometric pattern', 'character', 'specific symbol'"
        )
        self.target_entry.set_hexpand(True)
        target_section.append(self.target_entry)

        prompt_section.append(target_section)

        prompt_header = Gtk.Label(label="Custom Gemini Prompt Template:")
        prompt_header.set_halign(Gtk.Align.START)
        prompt_header.set_margin_bottom(4)
        prompt_header.add_css_class("heading")
        prompt_section.append(prompt_header)

        # Create a text entry for the prompt with better styling
        self.prompt_entry = Gtk.TextView()
        self.prompt_entry.set_wrap_mode(Gtk.WrapMode.WORD)
        self.prompt_entry.get_buffer().set_text(default_prompt)
        self.prompt_entry.set_top_margin(8)
        self.prompt_entry.set_bottom_margin(8)
        self.prompt_entry.set_left_margin(8)
        self.prompt_entry.set_right_margin(8)

        # Add scrolling for the text entry with improved styling
        prompt_scroll = Gtk.ScrolledWindow()
        prompt_scroll.set_min_content_height(100)  # Taller text area
        prompt_scroll.set_child(self.prompt_entry)
        prompt_scroll.set_margin_bottom(4)
        prompt_section.append(prompt_scroll)

        # Add buttons to save or reset prompt
        prompt_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        prompt_button_box.set_halign(Gtk.Align.END)
        prompt_button_box.set_margin_top(4)

        reset_prompt_button = Gtk.Button(label="Reset to Default")
        reset_prompt_button.connect("clicked", self.reset_prompt_to_default)

        save_prompt_button = Gtk.Button(label="Save as Default")
        save_prompt_button.connect("clicked", self.save_prompt_as_default)

        prompt_button_box.append(reset_prompt_button)
        prompt_button_box.append(save_prompt_button)
        prompt_section.append(prompt_button_box)

        # Add a note about the required format with improved styling
        note_label = Gtk.Label()
        note_label.set_markup(
            "<small>Note: Response must include coordinates in format: x1,y1,x2,y2</small>"
        )
        note_label.set_halign(Gtk.Align.START)
        note_label.set_margin_top(4)
        prompt_section.append(note_label)

        # Add a note about targeting precision
        targeting_note = Gtk.Label()
        targeting_note.set_markup(
            "<small><i>For best results, specify a single, distinct object in 'Target Type' "
            "rather than general categories</i></small>"
        )
        targeting_note.set_halign(Gtk.Align.START)
        targeting_note.set_margin_top(2)
        prompt_section.append(targeting_note)

        vbox.append(prompt_section)

        # Add debug options section
        debug_section = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        debug_section.set_margin_bottom(12)

        # Add debug checkbox for showing the API boundary
        self.debug_checkbox = Gtk.CheckButton()
        self.debug_checkbox.set_label("Show API Boundary")
        self.debug_checkbox.set_tooltip_text(
            "Show the original boundary box returned by Gemini API"
        )
        self.debug_checkbox.set_active(self.debug_mode)
        self.debug_checkbox.connect("toggled", self.on_debug_toggled)
        debug_section.append(self.debug_checkbox)

        # Add sizing controls
        size_label = Gtk.Label(label="Selection Size:")
        size_label.set_margin_start(20)
        debug_section.append(size_label)

        # Add a scale for adjusting the selection circle size
        size_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 0.05, 0.3, 0.01
        )
        size_scale.set_value(self.selection_ratio)
        size_scale.set_size_request(150, -1)
        size_scale.set_tooltip_text("Adjust the size of the selection circle")
        size_scale.connect("value-changed", self.on_selection_size_changed)
        debug_section.append(size_scale)

        # Add zoom factor control
        zoom_label = Gtk.Label(label="Zoom:")
        zoom_label.set_margin_start(20)
        debug_section.append(zoom_label)

        # Add a scale for adjusting the zoom factor
        zoom_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1.5, 5.0, 0.1)
        zoom_scale.set_value(self.zoom_factor)
        zoom_scale.set_size_request(150, -1)
        zoom_scale.set_tooltip_text("Adjust the zoom factor")
        zoom_scale.connect("value-changed", self.on_zoom_factor_changed)
        debug_section.append(zoom_scale)

        vbox.append(debug_section)

        # Add buttons with improved styling
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(8)

        # Add explanatory text on the left side of the button box
        help_text = Gtk.Label()
        help_text.set_markup(
            "<small>Left click: Set preview point (blue circle)\n"
            "Ctrl+Left click: Set magnification point (green circle)</small>"
        )
        help_text.set_halign(Gtk.Align.START)
        help_text.set_hexpand(True)
        button_box.append(help_text)

        # Create styled buttons
        rerun_button = Gtk.Button(label="Rerun Detection")
        rerun_button.connect("clicked", self.rerun_detection)
        rerun_button.set_margin_end(8)

        apply_button = Gtk.Button(label="Apply Changes")
        apply_button.connect("clicked", self.apply_manual_changes)
        apply_button.add_css_class("suggested-action")  # Highlight this button

        button_box.append(rerun_button)
        button_box.append(apply_button)

        vbox.append(button_box)

        # Add CSS styling
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(
            b"""
            .heading {
                font-weight: bold;
                font-size: 15px;
            }
            .description-text {
                font-size: 14px;
                padding: 4px;
            }
            """
        )

        # Apply the CSS provider
        display = Gdk.Display.get_default()
        Gtk.StyleContext.add_provider_for_display(
            display, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        manual_window.set_child(vbox)

        # Show the window
        manual_window.present()

        # Automatically run detection when the window is shown
        # Use a short delay to ensure the window is fully rendered
        GLib.timeout_add(500, lambda: self.rerun_detection(rerun_button))

    def on_draw_circles(self, widget, cr, width, height):
        """Draw circles on the overlay using Cairo."""
        if not self.current_image:
            return

        # Get the actual image dimensions
        img_width, img_height = self.current_image.size

        print(f"Drawing area dimensions: {width}x{height}")
        print(f"Image dimensions: {img_width}x{img_height}")
        print(
            f"Magnification point (normalized): {self.selected_magnification_point_norm}"
        )
        print(f"Preview point (normalized): {self.selected_preview_point_norm}")

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

        print(f"Image display size: {image_display_width}x{image_display_height}")
        print(f"Scale factors: {scale_x}, {scale_y}")
        print(f"Offsets: {x_offset}, {y_offset}")

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

            # Map from normalized coordinates to pixel positions on displayed image
            draw_x = x_offset + (norm_x * image_display_width)
            draw_y = y_offset + (norm_y * image_display_height)

            print(f"Drawing magnification circle at: ({draw_x}, {draw_y})")

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
            and self.selected_preview_point_norm[0] <= 1
            and self.selected_preview_point_norm[1] >= 0
            and self.selected_preview_point_norm[1] <= 1
        ):
            # Convert normalized coordinates to viewport coordinates
            norm_x, norm_y = self.selected_preview_point_norm

            # Map from normalized coordinates to pixel positions on displayed image
            draw_x = x_offset + (norm_x * image_display_width)
            draw_y = y_offset + (norm_y * image_display_height)

            print(f"Drawing preview circle at: ({draw_x}, {draw_y})")

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

        # If debug mode is enabled, draw the API boundary box
        if self.debug_mode and hasattr(self, "gemini_box") and self.gemini_box:
            # Get the original bounding box coordinates from Gemini API
            ox1, oy1, ox2, oy2 = self.gemini_box

            # Convert to normalized coordinates
            norm_ox1 = ox1 / img_width
            norm_oy1 = oy1 / img_height
            norm_ox2 = ox2 / img_width
            norm_oy2 = oy2 / img_height

            # Map to display coordinates
            box_x1 = x_offset + (norm_ox1 * image_display_width)
            box_y1 = y_offset + (norm_oy1 * image_display_height)
            box_x2 = x_offset + (norm_ox2 * image_display_width)
            box_y2 = y_offset + (norm_oy2 * image_display_height)

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
            cr.show_text("API Boundary")

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

            print(f"Widget dimensions: {widget_width}x{widget_height}")
            print(f"Image dimensions: {img_width}x{img_height}")
            print(f"Click at widget coords: ({x}, {y})")

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

            print(f"Display image size: {image_display_width}x{image_display_height}")
            print(f"Offsets: {x_offset}, {y_offset}")

            # Check if click is within the actual image area
            if (
                x < x_offset
                or x > (x_offset + image_display_width)
                or y < y_offset
                or y > (y_offset + image_display_height)
            ):
                self.show_notification("Click outside image area")
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

            print(f"Normalized coordinates: ({norm_x:.4f}, {norm_y:.4f})")
            print(f"Pixel coordinates: ({pixel_x}, {pixel_y})")

            # Ensure coordinates are within image bounds (redundant check)
            if norm_x < 0 or norm_x > 1 or norm_y < 0 or norm_y > 1:
                self.show_notification("Coordinates out of bounds")
                return

            if (
                button == 1 and state & Gdk.ModifierType.CONTROL_MASK
            ):  # Ctrl + Left click
                # Store both normalized and pixel coordinates
                self.selected_magnification_point_norm = (norm_x, norm_y)
                self.selected_magnification_point = (pixel_x, pixel_y)
                self.show_notification(
                    f"Magnification point set at ({pixel_x}, {pixel_y})"
                )
                print(
                    f"Magnification point selected: {self.selected_magnification_point}"
                )
                print(f"Normalized: {self.selected_magnification_point_norm}")

            elif button == 1:  # Left click
                # Store both normalized and pixel coordinates
                self.selected_preview_point_norm = (norm_x, norm_y)
                self.selected_preview_point = (pixel_x, pixel_y)
                self.show_notification(f"Preview point set at ({pixel_x}, {pixel_y})")
                print(f"Preview point selected: {self.selected_preview_point}")
                print(f"Normalized: {self.selected_preview_point_norm}")
        else:
            # No image loaded
            self.show_notification("No image loaded")
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
        """Rerun Gemini detection."""
        self.show_notification("Rerunning detection...")
        if self.spinner:
            self.spinner.start()

        # Make sure we have an image and it's in RGB mode if it's RGBA
        if self.current_image:
            # Store the original mode to restore it later
            original_mode = self.current_image.mode

            # Create a copy for Gemini processing that may need to be RGB
            image_for_gemini = self.current_image.copy()
            if image_for_gemini.mode == "RGBA":
                image_for_gemini = image_for_gemini.convert("RGB")

            # Get the prompt template from the text entry
            prompt_template = None
            target_type = DEFAULT_TARGET_TYPE

            if hasattr(self, "prompt_entry") and self.prompt_entry:
                buffer = self.prompt_entry.get_buffer()
                start_iter = buffer.get_start_iter()
                end_iter = buffer.get_end_iter()
                prompt_template = buffer.get_text(start_iter, end_iter, True)
                if prompt_template.strip() == "":
                    prompt_template = None

            # Get the target type
            if hasattr(self, "target_entry") and self.target_entry:
                target_text = self.target_entry.get_text()
                if target_text.strip():
                    target_type = target_text.strip()

            # Format the prompt with the target type
            custom_prompt = None
            if prompt_template:
                try:
                    custom_prompt = prompt_template.format(target_type=target_type)
                    print(f"Formatted prompt with target type: {target_type}")
                except KeyError:
                    # If formatting fails, use the template as is
                    custom_prompt = prompt_template
                    print(
                        "Warning: Prompt template doesn't contain {target_type} placeholder"
                    )

            print(f"Using prompt: {custom_prompt}")

            # Call the Gemini analyzer with the custom prompt
            interesting_area, raw_box, description = (
                gemini_analyzer.identify_interesting_textile(
                    image_for_gemini, custom_prompt
                )
            )

            # Store the ORIGINAL Gemini API boundary box for debug overlay
            # This is different from the working bounding box used for the selection
            self.gemini_box = interesting_area

            # Also store the raw unprocessed box for more detailed debugging
            self.raw_gemini_box = raw_box

            # Store the description from Gemini
            self.gemini_description = description

            # Update the description label if we have a description
            if hasattr(self, "description_label") and self.description_label:
                if description:
                    self.description_label.set_text(description)
                    self.description_label.set_tooltip_text(description)
                else:
                    self.description_label.set_text("No description available")

            print(f"Gemini API returned boundary box: {self.gemini_box}")
            if raw_box:
                print(f"Raw Gemini box before adjustments: {self.raw_gemini_box}")
            if description:
                print(f"Gemini description: {description}")

            # Show notification about AI status
            if not gemini_analyzer.AI_ENABLED:
                self.show_notification(
                    "Using fallback mode (no Gemini AI). Install google-generativeai package for AI features.",
                    5,
                )

            # Get image dimensions
            img_width, img_height = self.current_image.size

            # Calculate the area of the bounding box as a percentage of the image
            box_width = interesting_area[2] - interesting_area[0]
            box_height = interesting_area[3] - interesting_area[1]
            box_area = box_width * box_height
            image_area = img_width * img_height
            area_percentage = (box_area / image_area) * 100

            print(f"Bounding box area: {area_percentage:.2f}% of image")

            # Set the magnification point (green circle) at the center of the interesting area
            # Use floating point division to get the exact center point
            mag_x = (interesting_area[0] + interesting_area[2]) / 2
            mag_y = (interesting_area[1] + interesting_area[3]) / 2

            # Convert to int after all calculations to prevent accumulated rounding errors
            mag_x = int(mag_x)
            mag_y = int(mag_y)

            # Calculate padding based on current selection size instead of using a fixed value
            shortest_dimension = min(img_width, img_height)
            selection_diameter = int(shortest_dimension * self.selection_ratio)
            mag_radius = (
                selection_diameter / 2
            )  # Use the actual radius from selection size

            # Ensure magnification point is not too close to any edge based on its actual size
            mag_x = max(int(mag_radius), min(img_width - int(mag_radius), mag_x))
            mag_y = max(int(mag_radius), min(img_height - int(mag_radius), mag_y))

            # Store both pixel coordinates and normalized coordinates
            self.selected_magnification_point = (mag_x, mag_y)

            # Calculate normalized coordinates (0.0-1.0) for the magnification point
            norm_mag_x = mag_x / img_width
            norm_mag_y = mag_y / img_height
            self.selected_magnification_point_norm = (norm_mag_x, norm_mag_y)

            # For the preview point (blue circle), we need more padding since its radius is larger
            # Calculate preview circle radius based on the selection size and zoom factor
            preview_diameter = selection_diameter * self.zoom_factor
            preview_radius = preview_diameter / 2  # Use floating point division

            # Calculate safe areas for the preview point
            safe_left = int(preview_radius)
            safe_right = img_width - int(preview_radius)
            safe_top = int(preview_radius)
            safe_bottom = img_height - int(preview_radius)

            # If the image is too small to fit the preview circle, adjust the radius
            if safe_right <= safe_left or safe_bottom <= safe_top:
                # Image is too small, use a smaller radius
                preview_radius = (
                    min(img_width, img_height) / 3
                )  # Use floating point division
                safe_left = int(preview_radius)
                safe_right = img_width - int(preview_radius)
                safe_top = int(preview_radius)
                safe_bottom = img_height - int(preview_radius)

            # Define potential preview points in the four corners within the safe area
            corners = [
                (safe_left, safe_top),  # Top-left
                (safe_right, safe_top),  # Top-right
                (safe_left, safe_bottom),  # Bottom-left
                (safe_right, safe_bottom),  # Bottom-right
            ]

            # Find the corner farthest from the magnification point
            max_distance = 0
            farthest_corner = corners[0]

            for corner in corners:
                corner_x, corner_y = corner
                # Calculate squared distance (no need for square root)
                distance = (corner_x - mag_x) ** 2 + (corner_y - mag_y) ** 2
                if distance > max_distance:
                    max_distance = distance
                    farthest_corner = corner

            # Set the preview point (blue circle) in the farthest corner
            preview_x, preview_y = farthest_corner
            self.selected_preview_point = (preview_x, preview_y)

            # Calculate normalized coordinates for the preview point
            norm_preview_x = preview_x / img_width
            norm_preview_y = preview_y / img_height
            self.selected_preview_point_norm = (norm_preview_x, norm_preview_y)

            print(f"Image dimensions: {img_width}x{img_height}")
            print(f"Set magnification point at: {self.selected_magnification_point}")
            print(f"Normalized magnification: {self.selected_magnification_point_norm}")
            print(f"Set preview point at: {self.selected_preview_point}")
            print(f"Normalized preview: {self.selected_preview_point_norm}")

            # Update the UI to show the new points
            if hasattr(self, "spinner") and self.spinner:
                self.spinner.stop()

            # Use the stored reference to the circle_area to force a redraw
            if hasattr(self, "circle_area") and self.circle_area:
                print("Redrawing circle area")
                self.circle_area.queue_draw()
            else:
                print("Warning: No circle_area reference found for redrawing")

            self.show_notification("Detection complete.")

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

        self.show_notification("Applying changes...")
        # Process the image with the selected points
        self.process_image(self.current_image_path)

    def process_dropped_file(self, file):
        """Process a dropped file or directory."""
        file_path = file.get_path()
        if not file_path:
            self.show_notification("Invalid file")
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
                self.show_notification("No images found in directory")
                return False

            # Start processing the first image
            count = len(self.image_queue)
            self.show_notification(f"Processing {count} images...")

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

        self.show_notification("The file is not an image")
        return False

    def process_next_image(self):
        """Process the next image in the queue."""
        if not self.image_queue:
            self.show_notification("All images processed")
            if self.progress_bar:
                self.progress_bar.set_visible(False)
            return

        # Get the next image path
        image_path = self.image_queue.pop(0)
        self.current_image_path = image_path
        self.process_image(image_path)

        # Update progress bar
        total = len(self.image_queue) + 1  # +1 for the current image
        progress = 1 - (len(self.image_queue) / total)
        if self.progress_bar:
            self.progress_bar.set_fraction(progress)

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
        """Background thread for image processing."""
        try:
            # Load the image
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
                # If calculation failed, fallback to something reasonable
                if not interesting_area:
                    # Calculate a reasonable bounding box
                    shortest_dimension = min(width, height)
                    selection_diameter = int(shortest_dimension * self.selection_ratio)
                    radius = selection_diameter / 2
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
                self.processed_image = image_processor.create_highlighted_image(
                    self.current_image,
                    interesting_area,
                    preview_center=(preview_x, preview_y),
                    selection_ratio=self.selection_ratio,
                    zoom_factor=self.zoom_factor,
                    show_debug_overlay=self.debug_mode and debug_box is not None,
                )
            else:
                # Use Gemini AI to identify interesting textile parts
                print("No valid manual selection, using Gemini API")

                # For Gemini API, we need to make a copy that might need RGB conversion
                gemini_image = self.current_image
                if gemini_image.mode == "RGBA":
                    # Only convert the copy to RGB for the API
                    gemini_image = gemini_image.copy().convert("RGB")

                interesting_area, raw_box, description = (
                    gemini_analyzer.identify_interesting_textile(gemini_image)
                )

                # Store the ORIGINAL Gemini API boundary box for debug overlay
                self.gemini_box = interesting_area

                # Also store the raw unprocessed box for more detailed debugging
                self.raw_gemini_box = raw_box

                # Store the description
                self.gemini_description = description

                # Update the description in the UI if we're in a manual mode window
                # (needs to be done in the main thread)
                if description:
                    GLib.idle_add(self._update_description_in_ui, description)

                if raw_box:
                    print(f"Raw Gemini box before adjustments: {self.raw_gemini_box}")
                if description:
                    print(f"Gemini description: {description}")

                # Create a processed image with the highlight - use original image to preserve quality
                # Pass the configurable parameters
                self.processed_image = image_processor.create_highlighted_image(
                    self.current_image,
                    interesting_area,
                    selection_ratio=self.selection_ratio,
                    zoom_factor=self.zoom_factor,
                    show_debug_overlay=self.debug_mode,
                )

            # Show notification about AI status
            if not gemini_analyzer.AI_ENABLED:
                GLib.idle_add(
                    self.show_notification,
                    "Using fallback mode (no Gemini AI). Install google-generativeai package for AI features.",
                    5,
                )

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
                self.processed_image,
                image_path,
                output_dir=PREVIEWS_DIR,
                current_dir=self.current_dir,
            )
            print(f"Processed image saved to: {output_path}")

            # Update the UI on the main thread
            GLib.idle_add(self._processing_complete)

        except Exception as e:
            GLib.idle_add(self._show_error, str(e))

    def _processing_complete(self):
        """Called when image processing is complete."""
        # Reset processing state
        self.processing = False

        # Update progress bar
        if self.image_queue:
            total = len(self.image_queue) + 1  # +1 for the current image
            progress = 1 - (len(self.image_queue) / total)
            if self.progress_bar:
                self.progress_bar.set_fraction(progress)

            # Process the next image
            self.process_next_image()
        else:
            if self.progress_bar:
                self.progress_bar.set_visible(False)
            self.show_notification("All images processed")

        if self.spinner:
            self.spinner.stop()
        return False  # Important for GLib.idle_add

    def _show_error(self, error_message):
        """Show an error message notification."""
        self.show_notification(f"Error: {error_message}")
        self.processing = False

        # Continue with next image despite error
        if self.image_queue:
            self.process_next_image()
        else:
            if self.progress_bar:
                self.progress_bar.set_visible(False)

        return False  # Important for GLib.idle_add

    def _show_ai_installation_instructions(self):
        """Show instructions for installing the google-generativeai package."""
        self.show_notification(
            "To enable AI features, run: pip install google-generativeai", 10
        )
        return False  # Don't repeat

    def on_debug_toggled(self, checkbox):
        """Handle toggling of the debug checkbox."""
        self.debug_mode = checkbox.get_active()
        print(f"Debug checkbox toggled - debug mode set to: {self.debug_mode}")

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
        print(f"Selection size ratio set to: {self.selection_ratio}")
        # Update the display immediately
        if self.circle_area:
            self.circle_area.queue_draw()

    def on_zoom_factor_changed(self, scale):
        """Handle changes to the zoom factor slider."""
        self.zoom_factor = scale.get_value()
        print(f"Zoom factor set to: {self.zoom_factor}")
        # Update the display immediately
        if self.circle_area:
            self.circle_area.queue_draw()

    def reset_prompt_to_default(self, button):
        """Reset the prompt to the default one from file."""
        try:
            with open(DEFAULT_PROMPT_FILE, "r", encoding="utf-8") as f:
                default_prompt = f.read()
                if self.prompt_entry:
                    self.prompt_entry.get_buffer().set_text(default_prompt)
            self.show_notification("Prompt reset to default")
        except FileNotFoundError:
            self.show_notification("Default prompt file not found")

    def save_prompt_as_default(self, button):
        """Save the current prompt as the default one."""
        if hasattr(self, "prompt_entry") and self.prompt_entry:
            buffer = self.prompt_entry.get_buffer()
            start_iter = buffer.get_start_iter()
            end_iter = buffer.get_end_iter()
            prompt_text = buffer.get_text(start_iter, end_iter, True)

            if prompt_text.strip():
                try:
                    with open(DEFAULT_PROMPT_FILE, "w", encoding="utf-8") as f:
                        f.write(prompt_text)
                    self.show_notification("Prompt saved as default")
                except Exception as e:
                    self.show_notification(f"Error saving prompt: {e}")
            else:
                self.show_notification("Prompt is empty, not saving")

    def _update_description_in_ui(self, description):
        """Update the description label in the UI (called from the main thread)."""
        if hasattr(self, "description_label") and self.description_label:
            self.description_label.set_text(description)
            self.description_label.set_tooltip_text(description)
        return False  # For GLib.idle_add


def main():
    """Run the application."""
    app = KimonoAnalyzer()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
