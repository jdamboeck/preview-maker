"""Main application window for Preview Maker.

This module contains the ApplicationWindow class which serves as the main
window for the Preview Maker application.
"""

import logging
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Gdk, GLib  # noqa: E402

from preview_maker.core.logging import logger
from preview_maker.image.processor import ImageProcessor
from preview_maker.ai.analyzer import ImageAnalyzer
from preview_maker.ai.integration import AIPreviewGenerator
from preview_maker.ui.image_view import ImageView
from preview_maker.ui.overlay_manager import OverlayManager


class ApplicationWindow(Gtk.ApplicationWindow):
    """Main application window for the Preview Maker application.

    This class is responsible for the main UI of the application, including
    the menu bar, toolbar, and main content area.

    Attributes:
        application: The Gtk.Application instance
        image_processor: The ImageProcessor instance
        analyzer: The ImageAnalyzer instance
        preview_generator: The AIPreviewGenerator instance
        image_view: The ImageView widget for displaying images
        overlay_manager: The OverlayManager for managing highlight overlays
    """

    def __init__(self, application: Gtk.Application) -> None:
        """Initialize the application window.

        Args:
            application: The Gtk.Application instance
        """
        super().__init__(
            application=application,
            title="Preview Maker",
            default_width=1024,
            default_height=768,
        )

        # Initialize components
        self.image_processor = ImageProcessor()
        self.analyzer = None  # Will be initialized when API key is provided
        self.preview_generator = None

        # Set up UI
        self._create_header_bar()
        self._create_main_layout()
        self._setup_drag_and_drop()

        # Store current file
        self.current_file: Optional[Path] = None
        self.processing_lock = threading.Lock()

        logger.info("Application window initialized")

    def _create_header_bar(self) -> None:
        """Create the header bar with controls."""
        header_bar = Gtk.HeaderBar()
        self.set_titlebar(header_bar)

        # Open button
        open_button = Gtk.Button(label="Open")
        open_button.connect("clicked", self._on_open_clicked)
        header_bar.pack_start(open_button)

        # Save button
        save_button = Gtk.Button(label="Save")
        save_button.connect("clicked", self._on_save_clicked)
        header_bar.pack_start(save_button)

        # Analyze button
        analyze_button = Gtk.Button(label="Analyze")
        analyze_button.connect("clicked", self._on_analyze_clicked)
        header_bar.pack_end(analyze_button)

        # Settings button
        settings_button = Gtk.Button.new_from_icon_name("preferences-system")
        settings_button.connect("clicked", self._on_settings_clicked)
        header_bar.pack_end(settings_button)

    def _create_main_layout(self) -> None:
        """Create the main layout for the window."""
        # Main box
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_child(self.main_box)

        # Create image view
        self.image_view = ImageView()
        self.image_view.set_vexpand(True)
        self.image_view.set_hexpand(True)
        self.main_box.append(self.image_view)

        # Create overlay manager
        self.overlay_manager = OverlayManager(self.image_view)

        # Create status bar
        self.status_bar = Gtk.Label(label="Ready")
        self.status_bar.set_xalign(0)  # Align to the left
        self.main_box.append(self.status_bar)

    def _setup_drag_and_drop(self) -> None:
        """Set up drag and drop support."""
        # Create drop target for files
        drop_target = Gtk.DropTarget.new(Gdk.FileList, Gdk.DragAction.COPY)
        drop_target.connect("drop", self._on_drop)
        self.add_controller(drop_target)

    def _on_open_clicked(self, button: Gtk.Button) -> None:
        """Handle open button click.

        Args:
            button: The button that was clicked
        """
        dialog = Gtk.FileChooserDialog(
            title="Open Image",
            parent=self,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("_Open", Gtk.ResponseType.ACCEPT)

        # Add file filters
        filter_images = Gtk.FileFilter()
        filter_images.set_name("Image files")
        filter_images.add_mime_type("image/jpeg")
        filter_images.add_mime_type("image/png")
        filter_images.add_mime_type("image/bmp")
        filter_images.add_mime_type("image/tiff")
        dialog.add_filter(filter_images)

        dialog.connect("response", self._on_file_chooser_response)
        dialog.show()

    def _on_file_chooser_response(
        self, dialog: Gtk.FileChooserDialog, response: int
    ) -> None:
        """Handle file chooser response.

        Args:
            dialog: The file chooser dialog
            response: The response code
        """
        if response == Gtk.ResponseType.ACCEPT:
            file_path = dialog.get_file().get_path()
            self._load_image(file_path)

        dialog.destroy()

    def _on_save_clicked(self, button: Gtk.Button) -> None:
        """Handle save button click.

        Args:
            button: The button that was clicked
        """
        if not self.image_view.get_image():
            self._show_error_dialog("No image to save")
            return

        dialog = Gtk.FileChooserDialog(
            title="Save Image",
            parent=self,
            action=Gtk.FileChooserAction.SAVE,
        )
        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("_Save", Gtk.ResponseType.ACCEPT)
        dialog.set_do_overwrite_confirmation(True)

        # Add file filters
        filter_images = Gtk.FileFilter()
        filter_images.set_name("Image files")
        filter_images.add_mime_type("image/jpeg")
        filter_images.add_mime_type("image/png")
        dialog.add_filter(filter_images)

        dialog.connect("response", self._on_save_dialog_response)
        dialog.show()

    def _on_save_dialog_response(
        self, dialog: Gtk.FileChooserDialog, response: int
    ) -> None:
        """Handle save dialog response.

        Args:
            dialog: The file chooser dialog
            response: The response code
        """
        if response == Gtk.ResponseType.ACCEPT:
            file_path = dialog.get_file().get_path()
            self.image_view.save_image(file_path)
            self.status_bar.set_text(f"Saved to {file_path}")

        dialog.destroy()

    def _on_analyze_clicked(self, button: Gtk.Button) -> None:
        """Handle analyze button click.

        Args:
            button: The button that was clicked
        """
        if not self.current_file:
            self._show_error_dialog("No image loaded")
            return

        # Check if analyzer is initialized
        if not self.analyzer:
            self._show_api_key_dialog()
            return

        # Start analysis in background thread
        self.status_bar.set_text("Analyzing image...")
        threading.Thread(target=self._analyze_image, daemon=True).start()

    def _on_settings_clicked(self, button: Gtk.Button) -> None:
        """Handle settings button click.

        Args:
            button: The button that was clicked
        """
        # Show settings dialog
        self._show_settings_dialog()

    def _on_drop(
        self, drop_target: Gtk.DropTarget, value: Gdk.FileList, x: float, y: float
    ) -> bool:
        """Handle file drop.

        Args:
            drop_target: The drop target
            value: The dropped data
            x: The x coordinate of the drop
            y: The y coordinate of the drop

        Returns:
            True if the drop was handled, False otherwise
        """
        if not value:
            return False

        files = value.get_files()
        if not files:
            return False

        # Get the first file
        file_path = files[0].get_path()
        self._load_image(file_path)
        return True

    def _load_image(self, file_path: str) -> None:
        """Load an image from file.

        Args:
            file_path: Path to the image file
        """
        # Update status
        self.status_bar.set_text(f"Loading {file_path}...")

        # Store current file
        self.current_file = Path(file_path)

        # Load image in background
        def image_callback(image):
            # Update UI on main thread
            GLib.idle_add(self._update_image, image, file_path)

        self.image_processor.load_image(file_path, image_callback)

    def _update_image(self, image, file_path: str) -> bool:
        """Update the image view with the loaded image.

        Args:
            image: The loaded image
            file_path: Path to the image file

        Returns:
            False to ensure GLib.idle_add doesn't call this function again
        """
        if image:
            self.image_view.set_image(image)
            self.status_bar.set_text(f"Loaded {file_path}")
        else:
            self.status_bar.set_text(f"Failed to load {file_path}")
            self._show_error_dialog(f"Failed to load image: {file_path}")

        return False  # Don't call again

    def _analyze_image(self) -> None:
        """Analyze the current image in a background thread."""
        with self.processing_lock:
            if not self.current_file or not self.preview_generator:
                return

            try:
                # Generate preview
                preview = self.preview_generator.generate_preview(self.current_file)

                if preview:
                    # Update UI on main thread
                    GLib.idle_add(self._update_analyzed_image, preview)
                else:
                    GLib.idle_add(
                        self.status_bar.set_text,
                        "Analysis failed - no highlights found",
                    )

            except Exception as e:
                logger.error(f"Analysis failed: {e}")
                GLib.idle_add(self._show_error_dialog, f"Analysis failed: {str(e)}")
                GLib.idle_add(self.status_bar.set_text, "Analysis failed")

    def _update_analyzed_image(self, preview) -> bool:
        """Update the image view with the analyzed image.

        Args:
            preview: The analyzed image

        Returns:
            False to ensure GLib.idle_add doesn't call this function again
        """
        self.image_view.set_image(preview)
        self.status_bar.set_text("Analysis complete")
        return False

    def _show_api_key_dialog(self) -> None:
        """Show a dialog to enter the Gemini API key."""
        dialog = Gtk.Dialog(
            title="API Key Required",
            parent=self,
            modal=True,
            destroy_with_parent=True,
        )
        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("_OK", Gtk.ResponseType.OK)

        # Create dialog content
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        dialog.get_content_area().append(box)

        label = Gtk.Label(label="Please enter your Google Gemini API key:")
        box.append(label)

        entry = Gtk.Entry()
        entry.set_visibility(False)  # Hide input
        box.append(entry)

        dialog.connect("response", self._on_api_key_dialog_response, entry)
        dialog.show()

    def _on_api_key_dialog_response(
        self, dialog: Gtk.Dialog, response: int, entry: Gtk.Entry
    ) -> None:
        """Handle API key dialog response.

        Args:
            dialog: The dialog
            response: The response code
            entry: The entry widget with the API key
        """
        if response == Gtk.ResponseType.OK:
            api_key = entry.get_text()
            if api_key:
                # Initialize analyzer and preview generator
                self.analyzer = ImageAnalyzer(api_key=api_key)
                self.preview_generator = AIPreviewGenerator(api_key=api_key)
                self.status_bar.set_text("API key set")

                # Trigger analysis
                if self.current_file:
                    threading.Thread(target=self._analyze_image, daemon=True).start()

        dialog.destroy()

    def _show_settings_dialog(self) -> None:
        """Show the settings dialog."""
        dialog = Gtk.Dialog(
            title="Settings",
            parent=self,
            modal=True,
            destroy_with_parent=True,
        )
        dialog.add_button("_Close", Gtk.ResponseType.CLOSE)

        # Create dialog content
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        dialog.get_content_area().append(box)

        # API Key section
        api_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        box.append(api_box)

        api_label = Gtk.Label(label="Gemini API Key:")
        api_box.append(api_label)

        api_button = Gtk.Button(label="Change API Key")
        api_button.connect("clicked", self._on_api_key_button_clicked, dialog)
        api_box.append(api_button)

        # Other settings can be added here

        dialog.connect("response", lambda d, r: d.destroy())
        dialog.show()

    def _on_api_key_button_clicked(
        self, button: Gtk.Button, parent_dialog: Gtk.Dialog
    ) -> None:
        """Handle API key button click.

        Args:
            button: The button that was clicked
            parent_dialog: The parent dialog
        """
        self._show_api_key_dialog()

    def _show_error_dialog(self, message: str) -> None:
        """Show an error dialog.

        Args:
            message: The error message
        """
        dialog = Gtk.MessageDialog(
            parent=self,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error",
        )
        dialog.format_secondary_text(message)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.show()
