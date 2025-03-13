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

# Image processing imports
from PIL import Image

# Import our custom modules
import gemini_analyzer
import image_processor

# Create previews directory if it doesn't exist
PREVIEWS_DIR = "previews"
DEBUG_DIR = os.path.join(PREVIEWS_DIR, "debug")
os.makedirs(PREVIEWS_DIR, exist_ok=True)
os.makedirs(DEBUG_DIR, exist_ok=True)


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
        self.selected_magnification_point = None
        self.selected_preview_point = None
        self.window = None
        self.progress_bar = None
        self.spinner = None

    def on_activate(self, app):
        """Initialize the application window and UI components."""
        # Create the main window
        self.window = Gtk.ApplicationWindow(
            application=app, title="Kimono Textile Analyzer"
        )
        self.window.set_default_size(200, 200)

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
        self.window.set_child(vbox)

        # Create a horizontal box for the drop areas
        drop_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)

        # Automatic mode drop area
        auto_drop_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        auto_drop_area.set_size_request(120, 120)
        auto_icon = Gtk.Image.new_from_icon_name("media-playback-start")
        auto_icon.set_pixel_size(32)
        auto_drop_area.append(auto_icon)
        drop_box.append(auto_drop_area)

        # Manual mode drop area
        manual_drop_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        manual_drop_area.set_size_request(120, 120)
        manual_icon = Gtk.Image.new_from_icon_name("preferences-system")
        manual_icon.set_pixel_size(32)
        manual_drop_area.append(manual_icon)
        drop_box.append(manual_drop_area)

        # Add background color styling
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(
            b"""
        box {
            background-color: #333333;
            border-radius: 5px;
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

        # Set up drag and drop functionality for automatic mode
        auto_drop_target = Gtk.DropTarget.new(Gio.File, Gdk.DragAction.COPY)
        auto_drop_target.connect("drop", self.on_auto_drop)
        auto_drop_area.add_controller(auto_drop_target)

        # Set up drag and drop functionality for manual mode
        manual_drop_target = Gtk.DropTarget.new(Gio.File, Gdk.DragAction.COPY)
        manual_drop_target.connect("drop", self.on_manual_drop)
        manual_drop_area.add_controller(manual_drop_target)

        # Center the drop area
        center_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        center_box.set_hexpand(True)
        center_box.set_vexpand(True)
        center_box.set_halign(Gtk.Align.CENTER)
        center_box.set_valign(Gtk.Align.CENTER)
        center_box.append(drop_box)
        vbox.append(center_box)

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
        # Create a new window for manual mode
        manual_window = Gtk.Window(title="Manual Mode")
        manual_window.set_default_size(600, 400)

        # Load the image
        image = Image.open(file_path)
        self.current_image = image
        self.current_image_path = file_path

        print(f"Loaded image with dimensions: {image.width}x{image.height}")

        # Initialize selected points to offscreen positions
        if self.selected_magnification_point is None:
            self.selected_magnification_point = (-200, -200)  # Offscreen
        if self.selected_preview_point is None:
            self.selected_preview_point = (-600, -600)  # Offscreen

        # Create a picture widget
        picture = Gtk.Picture()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(file_path, 600, 400, True)
        texture = Gdk.Texture.new_for_pixbuf(pixbuf)
        picture.set_paintable(texture)

        # Get the actual displayed size of the image
        display_width = texture.get_width()
        display_height = texture.get_height()
        print(f"Display size: {display_width}x{display_height}")

        # Create an overlay to draw circles on the image
        overlay = Gtk.Overlay()
        overlay.set_child(picture)

        # Create a drawing area for circles - use the same size as the displayed image
        circle_area = Gtk.DrawingArea()
        circle_area.set_content_width(display_width)
        circle_area.set_content_height(display_height)
        circle_area.set_draw_func(self.on_draw_circles)

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

        # Get the default prompt from gemini_analyzer
        default_prompt = (
            "Please analyze this kimono image and identify the most interesting "
            "textile pattern or detail. Return only the coordinates of a bounding "
            "box around this area as normalized values between 0 and 1 in the format: "
            "x1,y1,x2,y2 where x1,y1 is the top-left corner and x2,y2 is the bottom-right corner."
        )

        # Create prompt customization field
        prompt_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        prompt_label = Gtk.Label(label="Custom Gemini Prompt:")
        prompt_box.append(prompt_label)

        # Create a text entry for the prompt
        self.prompt_entry = Gtk.TextView()
        self.prompt_entry.set_wrap_mode(Gtk.WrapMode.WORD)
        self.prompt_entry.get_buffer().set_text(default_prompt)

        # Add scrolling for the text entry
        prompt_scroll = Gtk.ScrolledWindow()
        prompt_scroll.set_min_content_height(80)
        prompt_scroll.set_child(self.prompt_entry)
        prompt_box.append(prompt_scroll)

        # Add a note about the required format
        note_label = Gtk.Label()
        note_label.set_markup(
            "<small>Note: Response must include coordinates in format: x1,y1,x2,y2</small>"
        )
        note_label.set_halign(Gtk.Align.START)
        prompt_box.append(note_label)

        # Add buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        rerun_button = Gtk.Button(label="Rerun Detection")
        rerun_button.connect("clicked", self.rerun_detection)
        apply_button = Gtk.Button(label="Apply Changes")
        apply_button.connect("clicked", self.apply_manual_changes)
        button_box.append(rerun_button)
        button_box.append(apply_button)

        # Layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.append(overlay)
        vbox.append(prompt_box)
        vbox.append(button_box)
        manual_window.set_child(vbox)

        # Show the window
        manual_window.present()

    def on_draw_circles(self, widget, cr, width, height):
        """Draw circles on the overlay using Cairo."""
        if not self.current_image:
            return

        # Get the actual image dimensions
        img_width, img_height = self.current_image.size

        print(f"Drawing area dimensions: {width}x{height}")
        print(f"Image dimensions: {img_width}x{img_height}")

        # Find the parent overlay and picture widget
        parent = widget.get_parent()
        picture = None
        if isinstance(parent, Gtk.Overlay):
            picture_widget = parent.get_child()
            if picture_widget and isinstance(picture_widget, Gtk.Picture):
                picture = picture_widget

        # If we found the picture widget, use its dimensions for scaling
        if picture:
            paintable = picture.get_paintable()
            if paintable:
                # Get the actual displayed size of the image
                display_width = paintable.get_intrinsic_width()
                display_height = paintable.get_intrinsic_height()
                print(f"Displayed image size: {display_width}x{display_height}")

                # Calculate the scale factors (image to display)
                scale_x = display_width / img_width if img_width > 0 else 1
                scale_y = display_height / img_height if img_height > 0 else 1

                # Use the same scale for both dimensions to maintain aspect ratio
                scale = min(scale_x, scale_y)

                # Calculate the drawing area scale factors
                draw_scale_x = width / display_width if display_width > 0 else 1
                draw_scale_y = height / display_height if display_height > 0 else 1

                # Calculate any letterboxing/pillarboxing offsets
                display_ratio = display_width / display_height
                widget_ratio = width / height

                x_offset = 0
                y_offset = 0

                if display_ratio > widget_ratio:
                    # Image is wider than widget (letterboxing - black bars on top/bottom)
                    display_scale = width / display_width
                    display_height_scaled = display_height * display_scale
                    y_offset = (height - display_height_scaled) / 2
                else:
                    # Image is taller than widget (pillarboxing - black bars on sides)
                    display_scale = height / display_height
                    display_width_scaled = display_width * display_scale
                    x_offset = (width - display_width_scaled) / 2
            else:
                # Fallback to simple scaling
                scale = (
                    min(width / img_width, height / img_height)
                    if img_width > 0 and img_height > 0
                    else 1
                )
                draw_scale_x = draw_scale_y = 1
                x_offset = y_offset = 0
        else:
            # Fallback to simple scaling
            scale = (
                min(width / img_width, height / img_height)
                if img_width > 0 and img_height > 0
                else 1
            )
            draw_scale_x = draw_scale_y = 1
            x_offset = y_offset = 0

        if (
            self.selected_magnification_point
            and self.selected_magnification_point[0] >= 0
        ):
            # Convert image coordinates to drawing area coordinates
            mag_x, mag_y = self.selected_magnification_point

            # Scale from image coordinates to display coordinates
            display_x = mag_x * scale
            display_y = mag_y * scale

            # Apply any letterboxing/pillarboxing offsets and drawing area scaling
            draw_x = display_x * draw_scale_x + x_offset
            draw_y = display_y * draw_scale_y + y_offset

            print(f"Drawing magnification circle at: ({draw_x}, {draw_y})")

            # Draw the magnification circle (green)
            cr.set_source_rgba(0, 1, 0, 0.5)  # Green, semi-transparent
            circle_radius = (
                128 * scale * draw_scale_x
            )  # Scale the radius based on the display
            cr.arc(draw_x, draw_y, circle_radius, 0, 2 * 3.14)
            cr.fill()

        if self.selected_preview_point and self.selected_preview_point[0] >= 0:
            # Convert image coordinates to drawing area coordinates
            preview_x, preview_y = self.selected_preview_point

            # Scale from image coordinates to display coordinates
            display_x = preview_x * scale
            display_y = preview_y * scale

            # Apply any letterboxing/pillarboxing offsets and drawing area scaling
            draw_x = display_x * draw_scale_x + x_offset
            draw_y = display_y * draw_scale_y + y_offset

            print(f"Drawing preview circle at: ({draw_x}, {draw_y})")

            # Draw the preview circle (blue)
            cr.set_source_rgba(0, 0, 1, 0.5)  # Blue, semi-transparent
            circle_radius = (
                384 * scale * draw_scale_x
            )  # Scale the radius based on the display
            cr.arc(draw_x, draw_y, circle_radius, 0, 2 * 3.14)
            cr.fill()

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

            # Get the picture widget to determine the actual displayed image size
            picture = None
            parent = widget.get_parent()
            if isinstance(parent, Gtk.Overlay):
                picture_widget = parent.get_child()
                if picture_widget and isinstance(picture_widget, Gtk.Picture):
                    picture = picture_widget

            # If we found the picture widget, use its dimensions for scaling
            if picture:
                paintable = picture.get_paintable()
                if paintable:
                    # Get the actual displayed size of the image
                    display_width = paintable.get_intrinsic_width()
                    display_height = paintable.get_intrinsic_height()
                    print(f"Displayed image size: {display_width}x{display_height}")

                    # Calculate the scale factors (display to image)
                    scale_x = img_width / display_width if display_width > 0 else 1
                    scale_y = img_height / display_height if display_height > 0 else 1

                    # Calculate the position within the displayed image
                    # First, determine if there's any letterboxing/pillarboxing
                    # (black bars on sides or top/bottom)
                    display_ratio = display_width / display_height
                    widget_ratio = widget_width / widget_height

                    if display_ratio > widget_ratio:
                        # Image is wider than widget (letterboxing - black bars on top/bottom)
                        display_scale = widget_width / display_width
                        display_height_scaled = display_height * display_scale
                        y_offset = (widget_height - display_height_scaled) / 2

                        # Check if click is within the actual image area
                        if y < y_offset or y > (widget_height - y_offset):
                            self.show_notification("Click outside image area")
                            return

                        # Adjust y coordinate to account for letterboxing
                        y = (y - y_offset) / display_scale
                        x = x / display_scale
                    else:
                        # Image is taller than widget (pillarboxing - black bars on sides)
                        display_scale = widget_height / display_height
                        display_width_scaled = display_width * display_scale
                        x_offset = (widget_width - display_width_scaled) / 2

                        # Check if click is within the actual image area
                        if x < x_offset or x > (widget_width - x_offset):
                            self.show_notification("Click outside image area")
                            return

                        # Adjust x coordinate to account for pillarboxing
                        x = (x - x_offset) / display_scale
                        y = y / display_scale

                    # Convert display coordinates to image coordinates
                    img_x = int(x * scale_x)
                    img_y = int(y * scale_y)
                else:
                    # Fallback to simple scaling if no paintable
                    scale_x = img_width / widget_width if widget_width > 0 else 1
                    scale_y = img_height / widget_height if widget_height > 0 else 1
                    img_x = int(x * scale_x)
                    img_y = int(y * scale_y)
            else:
                # Fallback to simple scaling if no picture widget
                scale_x = img_width / widget_width if widget_width > 0 else 1
                scale_y = img_height / widget_height if widget_height > 0 else 1
                img_x = int(x * scale_x)
                img_y = int(y * scale_y)

            # Ensure coordinates are within image bounds
            img_x = max(0, min(img_x, img_width - 1))
            img_y = max(0, min(img_y, img_height - 1))

            print(
                f"Click at widget coords ({x}, {y}) -> image coords ({img_x}, {img_y})"
            )

            if (
                button == 1 and state & Gdk.ModifierType.CONTROL_MASK
            ):  # Ctrl + Left click
                self.selected_magnification_point = (img_x, img_y)
                self.show_notification(f"Magnification point set at ({img_x}, {img_y})")
                print(
                    f"Magnification point selected: {self.selected_magnification_point}"
                )
            elif button == 1:  # Left click
                self.selected_preview_point = (img_x, img_y)
                self.show_notification(f"Preview point set at ({img_x}, {img_y})")
                print(f"Preview point selected: {self.selected_preview_point}")
        else:
            # No image loaded
            self.show_notification("No image loaded")
            return

        # Redraw the circles
        widget = gesture.get_widget()
        widget.queue_draw()

    def rerun_detection(self, button):
        """Rerun Gemini detection."""
        self.show_notification("Rerunning detection...")
        if self.spinner:
            self.spinner.start()

        # Make sure we have an image and it's in RGB mode if it's RGBA
        if self.current_image:
            if self.current_image.mode == "RGBA":
                self.current_image = self.current_image.convert("RGB")

            # Get the custom prompt from the text entry if available
            custom_prompt = None
            if hasattr(self, "prompt_entry") and self.prompt_entry:
                buffer = self.prompt_entry.get_buffer()
                start_iter = buffer.get_start_iter()
                end_iter = buffer.get_end_iter()
                custom_prompt = buffer.get_text(start_iter, end_iter, True)
                if custom_prompt.strip() == "":
                    custom_prompt = None

            # Call the Gemini analyzer with the custom prompt
            interesting_area = gemini_analyzer.identify_interesting_textile(
                self.current_image, custom_prompt
            )

            # Show notification about AI status
            if not gemini_analyzer.AI_ENABLED:
                self.show_notification(
                    "Using fallback mode (no Gemini AI). Install google-generativeai package for AI features.",
                    5,
                )

            self.selected_magnification_point = (
                (interesting_area[0] + interesting_area[2]) // 2,
                (interesting_area[1] + interesting_area[3]) // 2,
            )
            self.selected_preview_point = (
                self.selected_magnification_point[0] + 128,
                self.selected_magnification_point[1] + 128,
            )

            # Update the UI to show the new points
            if hasattr(self, "spinner") and self.spinner:
                self.spinner.stop()

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

            # Convert to RGB if it's RGBA to avoid JPEG conversion issues
            if self.current_image.mode == "RGBA":
                self.current_image = self.current_image.convert("RGB")

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

                # Create a bounding box around the magnification point
                # Use a 256x256 box centered on the magnification point
                radius = 128

                # Calculate the bounding box coordinates
                x1 = max(0, mag_x - radius)
                y1 = max(0, mag_y - radius)
                x2 = min(width, mag_x + radius)
                y2 = min(height, mag_y + radius)

                # Ensure the box has the correct dimensions
                if x2 - x1 < 2 * radius:
                    # Adjust if we hit the edge
                    if x1 == 0:
                        x2 = min(width, x1 + 2 * radius)
                    else:
                        x1 = max(0, x2 - 2 * radius)

                if y2 - y1 < 2 * radius:
                    # Adjust if we hit the edge
                    if y1 == 0:
                        y2 = min(height, y1 + 2 * radius)
                    else:
                        y1 = max(0, y2 - 2 * radius)

                interesting_area = (x1, y1, x2, y2)
                print(f"Using manually selected area: {interesting_area}")

                # Create a processed image with the highlight
                self.processed_image = image_processor.create_highlighted_image(
                    self.current_image,
                    interesting_area,
                    preview_center=(preview_x, preview_y),
                )
            else:
                # Use Gemini AI to identify interesting textile parts
                print("No valid manual selection, using Gemini AI")
                interesting_area = gemini_analyzer.identify_interesting_textile(
                    self.current_image
                )

                # Create a processed image with the highlight
                self.processed_image = image_processor.create_highlighted_image(
                    self.current_image, interesting_area
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


def main():
    """Run the application."""
    app = KimonoAnalyzer()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
