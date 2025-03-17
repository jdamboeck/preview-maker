"""Mock classes for GTK UI testing.

This module provides mock implementations of GTK UI components for testing,
allowing tests to run in both headless and GUI environments.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from unittest import mock
from PIL import Image
import uuid

# Determine if we can import GTK
try:
    import gi

    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk as RealGtk
    from gi.repository import Gdk as RealGdk
    from gi.repository import GLib as RealGLib

    GTK_AVAILABLE = True
except (ImportError, ValueError, AttributeError):
    RealGtk = None
    RealGdk = None
    RealGLib = None
    GTK_AVAILABLE = False
    print("GTK not available, using mock implementations")


# Mock GTK classes for headless testing
class MockGtk:
    """Mock Gtk namespace for testing."""

    class Orientation:
        """Mock for Gtk.Orientation enumeration."""

        HORIZONTAL = 0
        VERTICAL = 1

    class StyleContext:
        """Mock for Gtk.StyleContext."""

        @staticmethod
        def add_provider(context, provider, priority):
            """Mock for add_provider method."""
            pass

    class STYLE_PROVIDER_PRIORITY_APPLICATION:
        """Mock for Gtk style priority constant."""

        pass

    class ContentFit:
        """Mock for Gtk.ContentFit enumeration."""

        FILL = 0
        CONTAIN = 1
        COVER = 2
        SCALE_DOWN = 3

    class Box:
        """Mock for Gtk.Box."""

        def __init__(self, orientation=None, spacing=0):
            self.orientation = orientation
            self.spacing = spacing
            self.children = []
            self.parent = None
            self.css_classes = []
            self.props = mock.MagicMock()

        def append(self, child):
            """Mock for append method."""
            self.children.append(child)
            child.parent = self

        def remove(self, child):
            """Mock for remove method."""
            if child in self.children:
                self.children.remove(child)
                child.parent = None

        def set_orientation(self, orientation):
            """Mock for set_orientation method."""
            self.orientation = orientation

        def get_orientation(self):
            """Mock for get_orientation method."""
            return self.orientation

        def __iter__(self):
            """Make iterable."""
            return iter(self.children)

        def add_css_class(self, css_class):
            """Mock for add_css_class method."""
            if css_class not in self.css_classes:
                self.css_classes.append(css_class)

        def remove_css_class(self, css_class):
            """Mock for remove_css_class method."""
            if css_class in self.css_classes:
                self.css_classes.remove(css_class)

        def get_children(self):
            """Get all children widgets."""
            return self.children

    class Button:
        """Mock for Gtk.Button."""

        def __init__(self, label=None):
            """Initialize Button with optional label."""
            self.label = label
            self.handlers = {}
            self.parent = None
            self.css_classes = []

        def set_label(self, label):
            """Set button label."""
            self.label = label

        def get_label(self):
            """Get button label."""
            return self.label

        def connect(self, signal, handler):
            """Connect signal to handler."""
            self.handlers[signal] = handler
            return id(handler)

        def emit(self, signal, *args):
            """Emit signal and call handler."""
            if signal in self.handlers:
                self.handlers[signal](*args)

        def clicked(self):
            """Simulate click on the button."""
            self.emit("clicked", self)

        def add_css_class(self, css_class):
            """Add CSS class to the button."""
            if css_class not in self.css_classes:
                self.css_classes.append(css_class)

        def remove_css_class(self, css_class):
            """Remove CSS class from the button."""
            if css_class in self.css_classes:
                self.css_classes.remove(css_class)

        def set_sensitive(self, sensitive):
            """Set whether the button is sensitive (enabled)."""
            self.sensitive = sensitive

        def get_sensitive(self):
            """Get whether the button is sensitive (enabled)."""
            return getattr(self, "sensitive", True)

    class Scale:
        """Mock for Gtk.Scale."""

        def __init__(self, orientation=None, adjustment=None):
            """Initialize Scale with optional orientation and adjustment."""
            self.orientation = orientation
            self.adjustment = adjustment
            self.value = 0.0
            self.handlers = {}
            self.parent = None
            self.sensitive = True

        def set_value(self, value):
            """Set the scale value."""
            self.value = value
            self.emit("value-changed")

        def get_value(self):
            """Get the scale value."""
            return self.value

        def connect(self, signal, handler):
            """Connect a signal handler."""
            self.handlers[signal] = handler
            return id(handler)

        def emit(self, signal, *args):
            """Emit a signal and call handler."""
            if signal in self.handlers:
                if args:
                    self.handlers[signal](*args)
                else:
                    self.handlers[signal](self)

        def set_sensitive(self, sensitive):
            """Set whether the scale is sensitive (enabled)."""
            self.sensitive = sensitive

        def get_sensitive(self):
            """Get whether the scale is sensitive (enabled)."""
            return self.sensitive

        def list_signal_handlers(self, signal_name):
            """List signal handlers for a given signal."""
            if signal_name in self.handlers:
                return [id(self.handlers[signal_name])]
            return []

        def disconnect(self, handler_id):
            """Disconnect a signal handler by ID."""
            for signal, handler in list(self.handlers.items()):
                if id(handler) == handler_id:
                    old_handler = self.handlers[signal]
                    del self.handlers[signal]
                    return old_handler
            return None

    class CssProvider:
        """Mock for Gtk.CssProvider."""

        def __init__(self):
            self.css_data = None

        def load_from_data(self, data):
            """Mock for load_from_data method."""
            self.css_data = data

    class ApplicationWindow:
        """Mock for Gtk.ApplicationWindow."""

        def __init__(self, application=None):
            self.application = application
            self.child = None
            self.title = ""
            self.default_width = 800
            self.default_height = 600

        def set_child(self, child):
            """Mock for set_child method."""
            self.child = child

        def get_child(self):
            """Mock for get_child method."""
            return self.child

        def set_title(self, title):
            """Mock for set_title method."""
            self.title = title

        def get_title(self):
            """Mock for get_title method."""
            return self.title

        def set_default_size(self, width, height):
            """Mock for set_default_size method."""
            self.default_width = width
            self.default_height = height

        def show(self):
            """Mock for show method."""
            pass

        def present(self):
            """Mock for present method."""
            pass

        def destroy(self):
            """Mock for destroy method."""
            self.child = None

    class Application:
        """Mock for Gtk.Application."""

        def __init__(self, application_id=None):
            self.application_id = application_id
            self.windows = []

        def get_windows(self):
            """Mock for get_windows method."""
            return self.windows

        def add_window(self, window):
            """Mock for add_window method."""
            self.windows.append(window)

        def remove_window(self, window):
            """Mock for remove_window method."""
            if window in self.windows:
                self.windows.remove(window)

        def quit(self):
            """Mock for quit method."""
            for window in self.windows[:]:
                window.destroy()
            self.windows.clear()

    class Picture:
        """Mock for Gtk.Picture."""

        def __init__(self):
            self.paintable = None
            self.can_shrink = False
            self.content_fit = None
            self.controllers = []
            self.parent = None
            self.style_context = mock.MagicMock()

        def set_paintable(self, paintable):
            """Mock for set_paintable method."""
            self.paintable = paintable

        def get_paintable(self):
            """Mock for get_paintable method."""
            return self.paintable

        def set_can_shrink(self, can_shrink):
            """Mock for set_can_shrink method."""
            self.can_shrink = can_shrink

        def get_can_shrink(self):
            """Mock for get_can_shrink method."""
            return self.can_shrink

        def set_content_fit(self, content_fit):
            """Mock for set_content_fit method."""
            self.content_fit = content_fit

        def get_content_fit(self):
            """Mock for get_content_fit method."""
            return self.content_fit

        def add_controller(self, controller):
            """Mock for add_controller method."""
            self.controllers.append(controller)

        def remove_controller(self, controller):
            """Mock for remove_controller method."""
            if controller in self.controllers:
                self.controllers.remove(controller)

        def get_style_context(self):
            """Mock for get_style_context method."""
            return self.style_context

        def queue_draw(self):
            """Mock for queue_draw method."""
            pass

    class EventControllerScroll:
        """Mock for Gtk.EventControllerScroll."""

        @staticmethod
        def new(flags):
            """Mock for new method."""
            controller = mock.MagicMock()
            controller.handlers = {}
            controller.connect = lambda signal, handler: controller.handlers.update(
                {signal: handler}
            )
            return controller

    class EventControllerScrollFlags:
        """Mock for Gtk.EventControllerScrollFlags."""

        NONE = 0
        HORIZONTAL = 1
        VERTICAL = 2
        BOTH_AXES = 3

    class GestureDrag:
        """Mock for Gtk.GestureDrag."""

        @staticmethod
        def new():
            """Mock for new method."""
            controller = mock.MagicMock()
            controller.handlers = {}
            controller.connect = lambda signal, handler: controller.handlers.update(
                {signal: handler}
            )
            controller.get_offset = lambda: (0, 0)
            return controller

    class GestureClick:
        """Mock for Gtk.GestureClick."""

        @staticmethod
        def new():
            """Mock for new method."""
            controller = mock.MagicMock()
            controller.handlers = {}
            controller.connect = lambda signal, handler: controller.handlers.update(
                {signal: handler}
            )
            controller.set_button = lambda button: None
            return controller

    @staticmethod
    def init():
        """Mock for Gtk.init function."""
        print("Mock GTK initialized")
        return True

    @staticmethod
    def events_pending():
        """Mock for Gtk.events_pending function."""
        return False

    @staticmethod
    def main_iteration_do(blocking):
        """Mock for Gtk.main_iteration_do function."""
        return False


class MockGdk:
    """Mock Gdk namespace for testing."""

    class MemoryFormat:
        """Mock for Gdk.MemoryFormat enumeration."""

        R8G8B8 = 0
        R8G8B8A8 = 1

    class MemoryTexture:
        """Mock for Gdk.MemoryTexture."""

        @staticmethod
        def new(width, height, format, bytes_data, stride):
            """Mock for new method."""
            return mock.MagicMock()

    class ContentFit:
        """Mock for Gdk.ContentFit enumeration."""

        FILL = 0
        CONTAIN = 1
        COVER = 2
        SCALE_DOWN = 3


class MockGLib:
    """Mock GLib namespace for testing."""

    @staticmethod
    def Bytes(data):
        """Mock for GLib.Bytes constructor."""
        return mock.MagicMock()

    @staticmethod
    def idle_add(function, *args):
        """Mock for GLib.idle_add function."""
        function(*args)
        return 0


# Mock image view class for testing
class MockImageView(MockGtk.Box):
    """Mock implementation of ImageView class."""

    def __init__(self):
        """Initialize a mock image view."""
        super().__init__(orientation=MockGtk.Orientation.VERTICAL)
        self._image = None
        self._scale = 1.0
        self._original_size = None
        self._content_fit = MockGtk.ContentFit.CONTAIN

    def set_image(self, image):
        """Set the image to display."""
        self._image = image
        if image:
            self._original_size = image.size

    def get_image(self):
        """Get the current image."""
        return self._image

    def set_scale(self, scale):
        """Set the zoom scale."""
        self._scale = scale

    def get_scale(self):
        """Get the current zoom scale."""
        return self._scale

    def set_can_shrink(self, can_shrink):
        """Set whether the widget can shrink."""
        pass  # Mock implementation does nothing

    def set_content_fit(self, content_fit):
        """Set how content fits in the widget."""
        self._content_fit = content_fit

    def get_content_fit(self):
        """Get the current content fit mode."""
        return self._content_fit

    def _setup_controllers(self):
        """Set up gesture controllers."""
        pass  # Mock implementation does nothing


# Mock ManualOverlayManager for testing
class MockManualOverlayManager:
    """Mock for ManualOverlayManager class."""

    def __init__(self, image_view):
        """Initialize MockManualOverlayManager."""
        self.image_view = image_view
        self.overlays = {}  # Format: {id: (x, y, radius)}
        self.selected_overlay_id = None
        self.default_radius = 50
        self.default_color = "#ff0000"
        self.on_overlay_selected = None

    def create_overlay_at(self, x: int, y: int, radius: Optional[int] = None) -> str:
        """Create a new overlay at the specified coordinates."""
        if radius is None:
            radius = self.default_radius

        # Generate a unique ID for the overlay
        overlay_id = str(uuid.uuid4())

        # Store the overlay properties
        self.overlays[overlay_id] = (x, y, radius)

        # Add the overlay to the image view
        if hasattr(self.image_view, "add_overlay"):
            self.image_view.add_overlay(overlay_id)

        # Select the new overlay
        self.select_overlay(overlay_id)

        return overlay_id

    def select_overlay(self, overlay_id: str) -> None:
        """Select an overlay by ID.

        Args:
            overlay_id: ID of the overlay to select, or None to deselect
        """
        # Update selected overlay ID
        self.selected_overlay_id = overlay_id

        # Notify callback if exists
        if self.on_overlay_selected is not None:
            self.on_overlay_selected(overlay_id)

    def delete_selected_overlay(self) -> None:
        """Delete the currently selected overlay."""
        if self.selected_overlay_id:
            self.delete_overlay(self.selected_overlay_id)

    def delete_overlay(self, overlay_id: str) -> None:
        """Delete the specified overlay."""
        if overlay_id in self.overlays:
            # Remove from our internal tracking
            del self.overlays[overlay_id]

            # Remove from image view
            if hasattr(self.image_view, "remove_overlay"):
                self.image_view.remove_overlay(overlay_id)

            # Clear selection if this was the selected overlay
            if self.selected_overlay_id == overlay_id:
                self.selected_overlay_id = None

    def update_selected_overlay(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        radius: Optional[int] = None,
    ) -> None:
        """Update the properties of the selected overlay."""
        if not self.selected_overlay_id:
            return

        overlay_id = self.selected_overlay_id
        current_x, current_y, current_radius = self.overlays[overlay_id]

        # Update only the provided values
        new_x = x if x is not None else current_x
        new_y = y if y is not None else current_y
        new_radius = radius if radius is not None else current_radius

        # Store the updated values
        self.overlays[overlay_id] = (new_x, new_y, new_radius)

        # Update the display
        if hasattr(self.image_view, "update_overlay"):
            self.image_view.update_overlay(overlay_id)

    def get_overlay_count(self) -> int:
        """Get the number of overlays."""
        return len(self.overlays)

    def get_selected_overlay(self) -> Optional[Tuple[str, Tuple[int, int, int]]]:
        """Get the currently selected overlay.

        Returns:
            Tuple of (overlay_id, (x, y, radius)) or None if no overlay is selected
        """
        if (
            not self.selected_overlay_id
            or self.selected_overlay_id not in self.overlays
        ):
            return None

        return (self.selected_overlay_id, self.overlays[self.selected_overlay_id])


# Mock SettingsDialog for testing
class MockSettingsDialog:
    """Mock implementation of the SettingsDialog for headless testing."""

    def __init__(self, parent_window):
        """Initialize the dialog."""
        self.parent = parent_window
        self.config = None
        self.visible = False

        # Main container
        self.content_area = MockGtk.Box(orientation=MockGtk.Orientation.VERTICAL)

        # Create notebook for tabs
        self.notebook = ExtendedMockGtk.Notebook()
        self.notebook.set_name("settings-notebook")

        # Create tabs
        self._general_tab = self._create_general_tab()
        self._api_tab = self._create_api_tab()
        self._overlay_tab = self._create_overlay_tab()
        self._export_tab = self._create_export_tab()

        # Add tabs to notebook
        self.notebook.append_page(
            self._general_tab, ExtendedMockGtk.Label(label="General")
        )
        self.notebook.append_page(self._api_tab, ExtendedMockGtk.Label(label="API"))
        self.notebook.append_page(
            self._overlay_tab, ExtendedMockGtk.Label(label="Overlays")
        )
        self.notebook.append_page(
            self._export_tab, ExtendedMockGtk.Label(label="Export")
        )

        self.content_area.append(self.notebook)

        # Button area
        self.action_area = MockGtk.Box(orientation=MockGtk.Orientation.HORIZONTAL)

        # Create buttons
        self.cancel_button = ExtendedMockGtk.Button(label="Cancel")
        self.apply_button = ExtendedMockGtk.Button(label="Apply")
        self.ok_button = ExtendedMockGtk.Button(label="OK")

        self.cancel_button.set_name("cancel-button")
        self.apply_button.set_name("apply-button")
        self.ok_button.set_name("ok-button")

        # Add buttons to action area
        self.action_area.append(self.cancel_button)
        self.action_area.append(self.apply_button)
        self.action_area.append(self.ok_button)

        self.content_area.append(self.action_area)

        # Set up button callbacks
        self.apply_callback = None
        self.cancel_callback = None
        self.ok_callback = None

    def _create_general_tab(self):
        """Create the general settings tab."""
        tab = MockGtk.Box(orientation=MockGtk.Orientation.VERTICAL)

        # Debug mode checkbox
        self._debug_checkbox = ExtendedMockGtk.CheckButton()
        self._debug_checkbox.set_label("Debug Mode")
        tab.append(self._debug_checkbox)

        # Window size settings
        size_box = MockGtk.Box(orientation=MockGtk.Orientation.HORIZONTAL)
        width_label = ExtendedMockGtk.Label(label="Window Width:")
        self._width_entry = ExtendedMockGtk.Entry()
        self._width_entry.set_name("window-width-entry")

        height_label = ExtendedMockGtk.Label(label="Window Height:")
        self._height_entry = ExtendedMockGtk.Entry()
        self._height_entry.set_name("window-height-entry")

        size_box.append(width_label)
        size_box.append(self._width_entry)
        size_box.append(height_label)
        size_box.append(self._height_entry)

        tab.append(size_box)
        return tab

    def _create_api_tab(self):
        """Create the API settings tab."""
        tab = MockGtk.Box(orientation=MockGtk.Orientation.VERTICAL)

        # API key entry
        api_key_box = MockGtk.Box(orientation=MockGtk.Orientation.HORIZONTAL)
        api_key_label = ExtendedMockGtk.Label(label="API Key:")
        self._api_key_entry = ExtendedMockGtk.Entry()
        self._api_key_entry.set_name("api-key-entry")
        self._api_key_entry.set_visibility(False)  # Hide API key

        api_key_box.append(api_key_label)
        api_key_box.append(self._api_key_entry)
        tab.append(api_key_box)

        # Model selection combobox
        model_box = MockGtk.Box(orientation=MockGtk.Orientation.HORIZONTAL)
        model_label = ExtendedMockGtk.Label(label="Model:")
        self._model_combo = ExtendedMockGtk.ComboBoxText()
        self._model_combo.set_name("model-combo")

        # Add models
        self._model_combo.append_text("gemini-1.5-flash")
        self._model_combo.append_text("gemini-1.5-pro")
        self._model_combo.append_text("gemini-1.0-pro-vision")

        model_box.append(model_label)
        model_box.append(self._model_combo)
        tab.append(model_box)

        # Temperature setting
        temp_box = MockGtk.Box(orientation=MockGtk.Orientation.HORIZONTAL)
        temp_label = ExtendedMockGtk.Label(label="Temperature:")
        self._temp_scale = ExtendedMockGtk.Scale(
            orientation=MockGtk.Orientation.HORIZONTAL
        )
        self._temp_scale.set_name("temperature-scale")

        temp_box.append(temp_label)
        temp_box.append(self._temp_scale)
        tab.append(temp_box)

        return tab

    def _create_overlay_tab(self):
        """Create the overlay settings tab."""
        tab = MockGtk.Box(orientation=MockGtk.Orientation.VERTICAL)

        # Selection ratio scale
        ratio_box = MockGtk.Box(orientation=MockGtk.Orientation.HORIZONTAL)
        ratio_label = ExtendedMockGtk.Label(label="Selection Ratio:")
        self._ratio_scale = ExtendedMockGtk.Scale(
            orientation=MockGtk.Orientation.HORIZONTAL
        )
        self._ratio_scale.set_name("selection-ratio-scale")

        ratio_box.append(ratio_label)
        ratio_box.append(self._ratio_scale)
        tab.append(ratio_box)

        # Zoom factor scale
        zoom_box = MockGtk.Box(orientation=MockGtk.Orientation.HORIZONTAL)
        zoom_label = ExtendedMockGtk.Label(label="Zoom Factor:")
        self._zoom_scale = ExtendedMockGtk.Scale(
            orientation=MockGtk.Orientation.HORIZONTAL
        )
        self._zoom_scale.set_name("zoom-factor-scale")

        zoom_box.append(zoom_label)
        zoom_box.append(self._zoom_scale)
        tab.append(zoom_box)

        # Overlay color
        color_box = MockGtk.Box(orientation=MockGtk.Orientation.HORIZONTAL)
        color_label = ExtendedMockGtk.Label(label="Overlay Color:")
        self._color_button = ExtendedMockGtk.ColorButton()
        self._color_button.set_name("overlay-color-button")

        color_box.append(color_label)
        color_box.append(self._color_button)
        tab.append(color_box)

        # Overlay opacity
        opacity_box = MockGtk.Box(orientation=MockGtk.Orientation.HORIZONTAL)
        opacity_label = ExtendedMockGtk.Label(label="Overlay Opacity:")
        self._opacity_scale = ExtendedMockGtk.Scale(
            orientation=MockGtk.Orientation.HORIZONTAL
        )
        self._opacity_scale.set_name("overlay-opacity-scale")

        opacity_box.append(opacity_label)
        opacity_box.append(self._opacity_scale)
        tab.append(opacity_box)

        return tab

    def _create_export_tab(self):
        """Create the export settings tab."""
        tab = MockGtk.Box(orientation=MockGtk.Orientation.VERTICAL)

        # PNG compression scale
        png_box = MockGtk.Box(orientation=MockGtk.Orientation.HORIZONTAL)
        png_label = ExtendedMockGtk.Label(label="PNG Compression:")
        self._png_scale = ExtendedMockGtk.Scale(
            orientation=MockGtk.Orientation.HORIZONTAL
        )
        self._png_scale.set_name("png-compression-scale")

        png_box.append(png_label)
        png_box.append(self._png_scale)
        tab.append(png_box)

        # High quality resampling checkbox
        self._high_quality_checkbox = ExtendedMockGtk.CheckButton()
        self._high_quality_checkbox.set_label("High Quality Resampling")
        tab.append(self._high_quality_checkbox)

        return tab

    def show(self):
        """Show the dialog."""
        self.visible = True
        # Load current settings
        from preview_maker.core.config import config_manager

        config = config_manager.get_config()

        # General tab
        self._debug_checkbox.set_active(config.debug_mode)
        self._width_entry.set_text(str(config.window_width))
        self._height_entry.set_text(str(config.window_height))

        # API tab
        self._api_key_entry.set_text("")  # Don't show actual API key

        model_index = 0
        for i in range(self._model_combo.get_model().iter_n_children(None)):
            if self._model_combo.get_model().get_value(i, 0) == config.model_name:
                model_index = i
                break
        self._model_combo.set_active(model_index)

        self._temp_scale.set_value(config.temperature)

        # Overlay tab
        self._ratio_scale.set_value(config.selection_ratio)
        self._zoom_scale.set_value(config.zoom_factor)
        self._opacity_scale.set_value(config.overlay_opacity)

        # Export tab
        self._png_scale.set_value(config.png_compression)
        self._high_quality_checkbox.set_active(config.high_resampling == 1)

        # Store original settings for cancel
        self._current_settings = {
            "debug_mode": config.debug_mode,
            "window_width": config.window_width,
            "window_height": config.window_height,
            "model_name": config.model_name,
            "temperature": config.temperature,
            "selection_ratio": config.selection_ratio,
            "zoom_factor": config.zoom_factor,
            "overlay_opacity": config.overlay_opacity,
            "png_compression": config.png_compression,
            "high_resampling": config.high_resampling,
        }

    def _on_apply_clicked(self, button):
        """Handle apply button click."""
        self._apply_settings()

    def _on_cancel_clicked(self, button):
        """Handle cancel button click."""
        self.visible = False
        for handler_id, handler in self._response_handlers:
            handler(self, -6)  # Gtk.ResponseType.CANCEL

    def _on_ok_clicked(self, button):
        """Handle OK button click."""
        self._apply_settings()
        self.visible = False
        for handler_id, handler in self._response_handlers:
            handler(self, -5)  # Gtk.ResponseType.OK

    def _apply_settings(self):
        """Apply the current settings."""
        from preview_maker.core.config import config_manager

        # Collect settings from UI
        updates = {
            "debug_mode": self._debug_checkbox.get_active(),
            "window_width": int(self._width_entry.get_text()),
            "window_height": int(self._height_entry.get_text()),
            "model_name": self._model_combo.get_active_text(),
            "temperature": self._temp_scale.get_value(),
            "selection_ratio": self._ratio_scale.get_value(),
            "zoom_factor": self._zoom_scale.get_value(),
            "overlay_opacity": self._opacity_scale.get_value(),
            "png_compression": int(self._png_scale.get_value()),
            "high_resampling": 1 if self._high_quality_checkbox.get_active() else 0,
        }

        # Update API key if provided (non-empty)
        api_key = self._api_key_entry.get_text()
        if api_key:
            updates["gemini_api_key"] = api_key

        # Apply updates
        config_manager.update_config(updates)

    def connect(self, signal, handler):
        """Connect a signal handler.

        Args:
            signal: The signal name
            handler: The handler function

        Returns:
            Handler ID
        """
        handler_id = len(self._response_handlers) + 1
        self._response_handlers.append((handler_id, handler))
        return handler_id

    def get_content_area(self):
        """Return the dialog's content area."""
        return self.content_area

    def get_action_area(self):
        """Get the action area of the dialog.

        Returns:
            The action area box
        """
        return self.action_area

    def get_transient_for(self):
        """Get the parent window.

        Returns:
            The parent window
        """
        return self.parent

    def is_visible(self):
        """Check if the dialog is visible.

        Returns:
            True if visible, False otherwise
        """
        return self.visible

    def destroy(self):
        """Destroy the dialog."""
        self.visible = False


class MockAnalysisResultsDisplay(MockGtk.Box):
    """Mock implementation of the AnalysisResultsDisplay for headless testing."""

    def __init__(self, parent_window):
        """Initialize a mock analysis results display.

        Args:
            parent_window: The parent window
        """
        super().__init__(orientation=MockGtk.Orientation.VERTICAL, spacing=12)
        self.parent_window = parent_window

        # Result storage
        self._result = None
        self._error = None

        # UI components
        self._scroll_window = MockGtk.Box()
        self._text_view = MockGtk.Box()
        self._buttons_box = MockGtk.Box(
            orientation=MockGtk.Orientation.HORIZONTAL, spacing=6
        )

        # Action buttons
        self._copy_button = MockGtk.Button(label="Copy to Clipboard")
        self._save_button = MockGtk.Button(label="Save to File")
        self._expand_all_button = MockGtk.Button(label="Expand All")
        self._collapse_all_button = MockGtk.Button(label="Collapse All")

        self._buttons_box.append(self._copy_button)
        self._buttons_box.append(self._save_button)
        self._buttons_box.append(self._expand_all_button)
        self._buttons_box.append(self._collapse_all_button)

        # Section containers (expandable)
        self._sections = {
            "description": {
                "container": MockGtk.Box(),
                "expander": MockGtk.Button(label="Description"),
                "content": MockGtk.Box(),
                "expanded": True,
            },
            "key_points": {
                "container": MockGtk.Box(),
                "expander": MockGtk.Button(label="Key Points"),
                "content": MockGtk.Box(),
                "expanded": True,
            },
            "technical_details": {
                "container": MockGtk.Box(),
                "expander": MockGtk.Button(label="Technical Details"),
                "content": MockGtk.Box(),
                "expanded": True,
            },
            "metadata": {
                "container": MockGtk.Box(),
                "expander": MockGtk.Button(label="Metadata"),
                "content": MockGtk.Box(),
                "expanded": True,
            },
        }

        # Main container
        self._main_container = MockGtk.Box(
            orientation=MockGtk.Orientation.VERTICAL, spacing=12
        )

        # Append everything
        self.append(self._main_container)
        self._main_container.append(self._text_view)
        self._main_container.append(self._buttons_box)

    def display_result(self, result):
        """Display an analysis result.

        Args:
            result: The analysis result dictionary
        """
        self._result = result
        self._error = None

        # Clear existing content
        for section in self._sections.values():
            section["content"].remove_css_class("content-visible")
            section["content"].add_css_class("content-hidden")

        # In a real implementation, we would populate the text view
        # For the mock, we just store the result

    def clear(self):
        """Clear the display."""
        self._result = None
        self._error = None

    def has_result(self):
        """Check if there is a result to display.

        Returns:
            bool: True if there is a result, False otherwise
        """
        return self._result is not None

    def get_result(self):
        """Get the current result.

        Returns:
            dict: The current result or None
        """
        return self._result

    def display_error(self, error_message):
        """Display an error message.

        Args:
            error_message: The error message to display
        """
        self._error = error_message
        self._result = None

    def has_error(self):
        """Check if there is an error message.

        Returns:
            bool: True if there is an error, False otherwise
        """
        return self._error is not None

    def get_error(self):
        """Get the current error message.

        Returns:
            str: The current error message or None
        """
        return self._error

    def copy_to_clipboard(self):
        """Copy the result to the clipboard."""
        # In a real implementation, this would copy to the clipboard
        # For the mock, we get a mock clipboard and set the text
        clipboard = self._get_clipboard()

        if self._result:
            formatted_text = str(self._result)
            clipboard.set_text(formatted_text, -1)

    def save_to_file(self, filepath=None):
        """Save the result to a file.

        Args:
            filepath: Optional filepath to save to. If None, a dialog will be shown.

        Returns:
            bool: True if saved successfully, False otherwise
        """
        if not self._result:
            return False

        if not filepath:
            filepath = self._show_save_dialog()

        if not filepath:
            return False

        # In a real implementation, this would write to a file
        # For the mock, we create an empty file
        with open(filepath, "w") as f:
            f.write(str(self._result))

        return True

    def _show_save_dialog(self):
        """Show a file save dialog.

        Returns:
            str: The selected filepath or None
        """
        # Mock implementation returns a dummy path
        return "/tmp/analysis_results.txt"

    def _get_clipboard(self):
        """Get the system clipboard.

        Returns:
            A mock clipboard
        """
        # Return a mock clipboard
        return MockClipboard()

    def is_section_expanded(self, section_name):
        """Check if a section is expanded.

        Args:
            section_name: The name of the section

        Returns:
            bool: True if expanded, False otherwise
        """
        if section_name not in self._sections:
            return False

        return self._sections[section_name]["expanded"]

    def set_section_expanded(self, section_name, expanded):
        """Set whether a section is expanded.

        Args:
            section_name: The name of the section
            expanded: True to expand, False to collapse
        """
        if section_name not in self._sections:
            return

        self._sections[section_name]["expanded"] = expanded

        # Update CSS classes for visibility
        if expanded:
            self._sections[section_name]["content"].remove_css_class("content-hidden")
            self._sections[section_name]["content"].add_css_class("content-visible")
        else:
            self._sections[section_name]["content"].remove_css_class("content-visible")
            self._sections[section_name]["content"].add_css_class("content-hidden")


class MockClipboard:
    """Mock implementation of the clipboard."""

    def __init__(self):
        """Initialize a mock clipboard."""
        self.text = None

    def set_text(self, text, length=-1):
        """Set text on the clipboard.

        Args:
            text: The text to set
            length: The length of the text, or -1 for all
        """
        self.text = text

    def get_text(self):
        """Get text from the clipboard.

        Returns:
            str: The clipboard text
        """
        return self.text


class ExtendedMockGtk(MockGtk):
    """Extended mock Gtk with additional widget classes."""

    class Label:
        """Mock for Gtk.Label."""

        def __init__(self, label=""):
            self.label_text = label
            self.props = mock.MagicMock()
            self.props.label = label
            self.style_context = mock.MagicMock()
            self.name = ""

        def set_text(self, text):
            self.label_text = text
            self.props.label = text

        def get_text(self):
            return self.label_text

        def set_name(self, name):
            self.name = name

    class Button:
        """Mock for Gtk.Button."""

        def __init__(self, label=""):
            self.label_text = label
            self.name = ""
            self.props = mock.MagicMock()

        def set_label(self, label):
            self.label_text = label

        def get_label(self):
            return self.label_text

        def set_name(self, name):
            self.name = name

    class Entry:
        """Mock for Gtk.Entry."""

        def __init__(self):
            self.text = ""
            self.visible = True
            self.name = ""
            self.props = mock.MagicMock()

        def get_text(self):
            return self.text

        def set_text(self, text):
            self.text = text

        def set_visibility(self, visible):
            self.visible = visible

        def set_name(self, name):
            self.name = name

    class CheckButton:
        """Mock for Gtk.CheckButton."""

        def __init__(self, label=""):
            """Initialize the check button."""
            self.label_text = label
            self.active = False
            self.name = ""
            self.props = mock.MagicMock()
            self.props.active = self.active

        def get_active(self):
            """Get the active state."""
            return self.active

        def set_active(self, active):
            """Set the active state."""
            self.active = active
            self.props.active = active

        def set_label(self, label):
            """Set the label text."""
            self.label_text = label

        def get_label(self):
            """Get the label text."""
            return self.label_text

        def set_name(self, name):
            """Set the name of the check button."""
            self.name = name

    class ComboBoxText:
        """Mock for Gtk.ComboBoxText."""

        def __init__(self):
            """Initialize the combo box."""
            self.items = []
            self.active = -1
            self.name = ""
            self.props = mock.MagicMock()

        def append_text(self, text):
            """Add an item to the combo box."""
            self.items.append(text)

        def get_active(self):
            """Get the active item index."""
            return self.active

        def set_active(self, index):
            """Set the active item by index."""
            if 0 <= index < len(self.items):
                self.active = index

        def get_active_text(self):
            """Get the text of the active item."""
            if 0 <= self.active < len(self.items):
                return self.items[self.active]
            return None

        def set_name(self, name):
            """Set the name of the combo box."""
            self.name = name

    class Notebook:
        """Mock for Gtk.Notebook."""

        def __init__(self):
            """Initialize the notebook."""
            self.pages = []
            self.tabs = []
            self.current_page = 0
            self.name = ""
            self.props = mock.MagicMock()

        def append_page(self, widget, tab_label):
            """Add a page to the notebook."""
            self.pages.append(widget)
            self.tabs.append(tab_label)
            return len(self.pages) - 1

        def get_current_page(self):
            """Get the current page index."""
            return self.current_page

        def set_current_page(self, page_num):
            """Set the current page index."""
            if 0 <= page_num < len(self.pages):
                self.current_page = page_num

        def get_nth_page(self, page_num):
            """Get the page at the given index."""
            if 0 <= page_num < len(self.pages):
                return self.pages[page_num]
            return None

        def set_name(self, name):
            """Set the name of the notebook."""
            self.name = name

    class Scale:
        """Mock for Gtk.Scale."""

        def __init__(self, orientation=None, adjustment=None):
            """Initialize Scale with optional orientation and adjustment."""
            self.value = 0.0
            self.orientation = orientation
            self.adjustment = adjustment
            self.name = ""
            self.props = mock.MagicMock()
            self.props.value = self.value

        def get_value(self):
            """Get the scale value."""
            return self.value

        def set_value(self, value):
            """Set the scale value."""
            self.value = value
            self.props.value = value

        def set_range(self, min_value, max_value):
            """Set the range of the scale."""
            self.min_value = min_value
            self.max_value = max_value

        def set_name(self, name):
            """Set the name of the scale."""
            self.name = name

    class ColorButton:
        """Mock for Gtk.ColorButton."""

        def __init__(self):
            """Initialize the color button."""
            self.rgba = None
            self.name = ""
            self.props = mock.MagicMock()

        def get_rgba(self):
            """Get the RGBA color."""
            return self.rgba

        def set_rgba(self, rgba):
            """Set the RGBA color."""
            self.rgba = rgba

        def set_name(self, name):
            """Set the name of the color button."""
            self.name = name


class MockNotebookPage:
    """Mock for a notebook page."""

    def __init__(self, page, label):
        """Initialize the notebook page."""
        self.page = page
        self.label = label

    def get_child(self):
        """Get the page content."""
        return self.page

    def get_tab_label(self):
        """Get the tab label."""
        return self.label


class MockTreeModel:
    """Mock for Gtk.TreeModel."""

    def __init__(self, items):
        """Initialize the tree model."""
        self.items = items

    def iter_n_children(self, iter_):
        """Get the number of children."""
        return len(self.items)

    def get_value(self, index, column):
        """Get the value at the given index and column."""
        if 0 <= index < len(self.items):
            return self.items[index]
        return None


class MockRGBA:
    """Mock for Gdk.RGBA."""

    def __init__(self, red, green, blue, alpha):
        """Initialize the RGBA color."""
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

    def to_string(self):
        """Convert to string representation."""
        return f"rgba({self.red:.1f},{self.green:.1f},{self.blue:.1f},{self.alpha:.1f})"


def process_events():
    """Process pending GTK events."""
    # In a real GTK application, this would process pending events
    # For our mock, we do nothing
    pass


# Determine which classes to export based on GTK availability
if GTK_AVAILABLE and RealGtk is not None:
    # Use real GTK classes but export our mocks too
    Gtk = RealGtk
    Gdk = RealGdk
    GLib = RealGLib
else:
    # Use mock GTK classes
    Gtk = ExtendedMockGtk
    Gdk = MockGdk
    GLib = MockGLib
