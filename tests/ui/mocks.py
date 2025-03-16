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

    class Button:
        """Mock for Gtk.Button."""

        def __init__(self, label=None):
            self.label = label
            self.parent = None
            self.css_classes = []
            self.handlers = {}

        def set_label(self, label):
            """Mock for set_label method."""
            self.label = label

        def get_label(self):
            """Mock for get_label method."""
            return self.label

        def connect(self, signal, handler):
            """Mock for connect method."""
            self.handlers[signal] = handler
            return 1  # Handler ID

        def emit(self, signal, *args):
            """Mock for emit method."""
            if signal in self.handlers:
                handler = self.handlers[signal]
                return handler(self, *args)
            return None

        def add_css_class(self, css_class):
            """Mock for add_css_class method."""
            if css_class not in self.css_classes:
                self.css_classes.append(css_class)

        def remove_css_class(self, css_class):
            """Mock for remove_css_class method."""
            if css_class in self.css_classes:
                self.css_classes.remove(css_class)

    class Scale:
        """Mock for Gtk.Scale."""

        def __init__(self, orientation=None, adjustment=None):
            self.orientation = orientation
            self.adjustment = adjustment
            self.parent = None
            self.value = 0
            self.handlers = {}

        def set_value(self, value):
            """Mock for set_value method."""
            self.value = value
            self.emit("value-changed")

        def get_value(self):
            """Mock for get_value method."""
            return self.value

        def connect(self, signal, handler):
            """Mock for connect method."""
            self.handlers[signal] = handler
            return 1  # Handler ID

        def emit(self, signal, *args):
            """Mock for emit method."""
            if signal in self.handlers:
                handler = self.handlers[signal]
                return handler(self, *args)
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
    """Mock implementation of ManualOverlayManager for testing."""

    def __init__(self, image_view):
        """Initialize the ManualOverlayManager with the provided image view."""
        self.image_view = image_view
        self.overlays = {}  # Dictionary of overlay_id -> (x, y, radius)
        self.selected_overlay_id = None
        self.default_radius = 50

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
        """Select the specified overlay."""
        if overlay_id in self.overlays:
            self.selected_overlay_id = overlay_id

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


# Determine which classes to export based on GTK availability
if GTK_AVAILABLE and RealGtk is not None:
    # Use real GTK classes but export our mocks too
    Gtk = RealGtk
    Gdk = RealGdk
    GLib = RealGLib
else:
    # Use mock GTK classes
    Gtk = MockGtk
    Gdk = MockGdk
    GLib = MockGLib
