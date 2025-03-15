#!/usr/bin/env python3
"""
GTK 4.0 Test Script for Preview Maker

This script demonstrates circular overlay capabilities with Pillow and Cairo,
which are essential for the Preview Maker application.
"""
import gi
import sys
import threading
import io
from pathlib import Path
import os

# Try to handle GTK initialization more gracefully
try:
    # Handle headless environment better
    if "DISPLAY" in os.environ and os.environ.get("DISPLAY"):
        print(f"Using display: {os.environ.get('DISPLAY')}")
    else:
        print("No display found. Setting GDK_BACKEND=x11")
        os.environ["GDK_BACKEND"] = "x11"
        os.environ["DISPLAY"] = ":0"

    # Initialize GTK specifically
    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk, Gio, GLib, Gdk

    # Pre-initialize GTK
    Gtk.init()
except Exception as e:
    print(f"Error initializing GTK: {str(e)}")
    sys.exit(1)

try:
    from PIL import Image, ImageDraw
    import cairo
except ImportError:
    print("Error: Required packages not installed. Please run:")
    print("pip install PyGObject pycairo Pillow")
    sys.exit(1)


class OverlayTestWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        try:
            super().__init__(*args, **kwargs)
            self.set_default_size(800, 600)
            self.set_title("Preview Maker - Overlay Test")

            # Create main box
            main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            main_box.set_margin_top(20)
            main_box.set_margin_bottom(20)
            main_box.set_margin_start(20)
            main_box.set_margin_end(20)
            self.set_child(main_box)

            # Add header
            header = Gtk.Label(label="Preview Maker - GTK 4.0 Circular Overlay Test")
            header.add_css_class("title-2")
            main_box.append(header)

            # Create buttons box
            button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            button_box.set_margin_top(10)
            button_box.set_margin_bottom(10)
            main_box.append(button_box)

            # Add Pillow test button
            self.pillow_button = Gtk.Button(label="Test Pillow Overlay")
            self.pillow_button.connect("clicked", self.on_pillow_test_clicked)
            button_box.append(self.pillow_button)

            # Add Cairo test button
            self.cairo_button = Gtk.Button(label="Test Cairo Overlay")
            self.cairo_button.connect("clicked", self.on_cairo_test_clicked)
            button_box.append(self.cairo_button)

            # Add file chooser button
            self.file_button = Gtk.Button(label="Choose Image")
            self.file_button.connect("clicked", self.on_file_button_clicked)
            button_box.append(self.file_button)

            # Create drawing area for image display
            self.drawing_area = Gtk.DrawingArea()
            self.drawing_area.set_size_request(600, 400)
            self.drawing_area.set_draw_func(self.on_draw)

            # Add drop target for drag and drop
            try:
                drop_target = Gtk.DropTarget.new(Gdk.FileList, Gdk.DragAction.COPY)
                drop_target.connect("drop", self.on_drop)
                self.drawing_area.add_controller(drop_target)
            except Exception as e:
                print(f"Warning: Could not set up drag and drop: {str(e)}")

            # Create a scrolled window to contain the drawing area
            scroll = Gtk.ScrolledWindow()
            scroll.set_child(self.drawing_area)
            main_box.append(scroll)

            # Add status bar
            self.status_label = Gtk.Label(
                label="Drag an image or use the buttons above"
            )
            self.status_label.set_margin_top(10)
            main_box.append(self.status_label)

            # Initialize image data
            self.image_surface = None
            self.pillow_image = None
            self.filename = None
            self.use_cairo = False

            # Create a test image on startup
            self._create_test_image()
        except Exception as e:
            print(f"Error initializing window: {str(e)}")
            raise

    def _create_test_image(self):
        """Create a test image if no image is loaded."""
        # Create a simple test image with Pillow
        img = Image.new("RGB", (600, 400), color="#eeeeee")
        draw = ImageDraw.Draw(img)

        # Draw some shapes
        draw.rectangle((50, 50, 550, 350), outline="black")
        draw.ellipse((100, 100, 250, 250), fill="#3584e4")
        draw.ellipse((350, 100, 500, 250), fill="#ff7800")

        # Add some text
        draw.text((300, 300), "Drag an image here", fill="black")

        # Convert to format Cairo can use
        self.pillow_image = img

        # Update status
        self.status_label.set_label(
            "Test image created - Drag a real image or use buttons"
        )

        # Convert Pillow image to Cairo surface
        self._pillow_to_cairo(img)

        # Redraw
        self.drawing_area.queue_draw()

    def _pillow_to_cairo(self, pil_image):
        """Convert a Pillow image to a Cairo surface."""
        # Convert Pillow image to PNG in memory
        png_data = io.BytesIO()
        pil_image.save(png_data, format="PNG")
        png_data.seek(0)

        # Create a Cairo surface from the PNG data
        self.image_surface = cairo.ImageSurface.create_from_png(png_data)

    def on_draw(self, area, cr, width, height):
        """Draw function for the drawing area."""
        # Clear background
        cr.set_source_rgb(0.95, 0.95, 0.95)
        cr.paint()

        # Draw the image if available
        if self.image_surface:
            # Scale to fit while maintaining aspect ratio
            img_width = self.image_surface.get_width()
            img_height = self.image_surface.get_height()

            scale_x = width / img_width
            scale_y = height / img_height
            scale = min(scale_x, scale_y)

            # Center the image
            x = (width - img_width * scale) / 2
            y = (height - img_height * scale) / 2

            # Draw the scaled image
            cr.save()
            cr.translate(x, y)
            cr.scale(scale, scale)
            cr.set_source_surface(self.image_surface, 0, 0)
            cr.paint()
            cr.restore()

    def on_drop(self, drop_target, value, x, y):
        """Handle file drop events."""
        # Process only if we got a file list
        if isinstance(value, Gdk.FileList):
            files = value.get_files()
            if not files:
                return False

            # Get the first file
            file = files[0]
            filename = file.get_path()

            # Check if it's an image file
            if any(
                filename.lower().endswith(ext)
                for ext in [".jpg", ".jpeg", ".png", ".bmp", ".gif"]
            ):
                self.load_image(filename)
                return True

        return False

    def on_file_button_clicked(self, button):
        """Handle file chooser button click."""
        dialog = Gtk.FileDialog()
        dialog.set_title("Open Image")

        # Set up file filter
        filters = Gtk.FileFilter()
        filters.set_name("Images")
        filters.add_mime_type("image/jpeg")
        filters.add_mime_type("image/png")
        filters.add_mime_type("image/bmp")
        filters.add_mime_type("image/gif")

        dialog.open(self, None, self._on_file_selected)

    def _on_file_selected(self, dialog, result):
        """Handle file selection completion."""
        try:
            file = dialog.open_finish(result)
            if file:
                filename = file.get_path()
                self.load_image(filename)
        except GLib.Error as error:
            print(f"Error opening file: {error.message}")

    def load_image(self, filename):
        """Load an image from file in a background thread."""
        self.filename = filename
        self.status_label.set_label(f"Loading {Path(filename).name}...")

        # Use a thread to avoid blocking the UI
        thread = threading.Thread(target=self._load_image_thread, args=(filename,))
        thread.daemon = True
        thread.start()

    def _load_image_thread(self, filename):
        """Background thread to load image."""
        try:
            # Load with Pillow
            self.pillow_image = Image.open(filename).convert("RGBA")

            # Convert to Cairo surface
            self._pillow_to_cairo(self.pillow_image)

            # Update UI in main thread
            GLib.idle_add(self._on_image_loaded, filename)
        except Exception as e:
            GLib.idle_add(self._on_image_error, str(e))

    def _on_image_loaded(self, filename):
        """Called when image is loaded."""
        self.status_label.set_label(f"Loaded: {Path(filename).name}")
        self.drawing_area.queue_draw()

    def _on_image_error(self, error_msg):
        """Called when image loading fails."""
        self.status_label.set_label(f"Error: {error_msg}")

    def on_pillow_test_clicked(self, button):
        """Handle Pillow test button click."""
        if not self.pillow_image:
            self.status_label.set_label("No image loaded to process")
            return

        self.status_label.set_label("Processing with Pillow...")
        self.use_cairo = False

        # Use a thread for processing
        thread = threading.Thread(target=self._process_with_pillow)
        thread.daemon = True
        thread.start()

    def _process_with_pillow(self):
        """Process the image with Pillow to create a circular overlay."""
        try:
            # Create a copy of the original image
            img = self.pillow_image.copy()

            # Get dimensions
            width, height = img.size

            # Create a transparent overlay for the zoom area
            overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            # Define circle location (center of image)
            center_x, center_y = width // 2, height // 2
            radius = min(width, height) // 4

            # Create area to zoom
            zoom_area = img.crop(
                (
                    center_x - radius // 2,
                    center_y - radius // 2,
                    center_x + radius // 2,
                    center_y + radius // 2,
                )
            )

            # Resize to create zoom effect
            zoomed = zoom_area.resize(
                (radius * 2, radius * 2), Image.Resampling.LANCZOS
            )

            # Create circular mask for overlay
            mask = Image.new("L", (radius * 2, radius * 2), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)

            # Paste zoomed area onto overlay using the circular mask
            overlay.paste(zoomed, (center_x - radius, center_y - radius), mask)

            # Draw circle outline
            draw.ellipse(
                (
                    center_x - radius,
                    center_y - radius,
                    center_x + radius,
                    center_y + radius,
                ),
                outline=(255, 255, 255, 255),
                width=2,
            )

            # Compose original with overlay
            result = Image.alpha_composite(img.convert("RGBA"), overlay)

            # Apply the result
            self._pillow_to_cairo(result)

            # Update UI in main thread
            GLib.idle_add(self._on_processing_complete, "Pillow")
        except Exception as e:
            GLib.idle_add(self._on_processing_error, str(e))

    def on_cairo_test_clicked(self, button):
        """Handle Cairo test button click."""
        if not self.image_surface:
            self.status_label.set_label("No image loaded to process")
            return

        self.status_label.set_label("Processing with Cairo...")
        self.use_cairo = True

        # Queue redraw - Cairo processing happens in draw function
        self.drawing_area.queue_draw()

        # Update status
        self.status_label.set_label(
            "Processed with Cairo - Zoom overlay drawn dynamically"
        )

    def _on_processing_complete(self, method):
        """Called when processing is complete."""
        self.status_label.set_label(f"Processing complete using {method}")
        self.drawing_area.queue_draw()

    def _on_processing_error(self, error_msg):
        """Called when processing fails."""
        self.status_label.set_label(f"Processing error: {error_msg}")


class OverlayTestApp(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="dev.preview.maker.test",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )

    def do_activate(self):
        try:
            win = OverlayTestWindow(application=self)
            win.present()
        except Exception as e:
            print(f"Error creating window: {str(e)}")
            sys.exit(1)


def main():
    print("Starting GTK 4.0 Overlay Test Application...")
    print("This test demonstrates circular overlay capabilities for Preview Maker")

    # Check for required libraries
    missing_libs = []
    try:
        import gi

        gi.require_version("Gtk", "4.0")
        from gi.repository import Gtk
    except (ImportError, ValueError) as e:
        missing_libs.append(f"PyGObject/GTK 4.0: {str(e)}")

    try:
        import cairo
    except ImportError as e:
        missing_libs.append(f"PyCairo: {str(e)}")

    try:
        from PIL import Image
    except ImportError as e:
        missing_libs.append(f"Pillow: {str(e)}")

    if missing_libs:
        print("Error: Missing required libraries:")
        for lib in missing_libs:
            print(f" - {lib}")
        print("\nPlease install them following the instructions in cursor_setup.md")
        return 1

    # Run the application with error handling
    try:
        app = OverlayTestApp()
        return app.run(sys.argv)
    except Exception as e:
        print(f"Error running application: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
