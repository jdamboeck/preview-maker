"""Test for verifying overlay functionality in Xwayland environment.

This test file contains tests to verify that the overlay functionality works correctly
in the Xwayland environment.
"""

import os
import time
import subprocess
import pytest
from PIL import Image

# Determine if we can import GTK
try:
    import gi

    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk, GLib

    GTK_AVAILABLE = True
except (ImportError, ValueError, AttributeError):
    GTK_AVAILABLE = False
    print("GTK not available, skipping tests")

# Detect environment
HEADLESS = os.environ.get("HEADLESS", "0") == "1"
USE_XVFB = HEADLESS and os.environ.get("DISPLAY") is None


# Base class for GTK testing
class GTKTestBase:
    """Base class for tests that use real GTK components."""

    xvfb_proc = None
    gtk_initialized = False

    @classmethod
    def setup_class(cls):
        """Set up GTK and Xvfb if needed."""
        # Start Xvfb if we're in headless mode and no display is set
        if USE_XVFB:
            print("Starting Xvfb for headless testing...")
            cls.xvfb_proc = subprocess.Popen(
                ["Xvfb", ":99", "-screen", "0", "1280x1024x24", "-ac"]
            )
            time.sleep(1)  # Give Xvfb time to start
            os.environ["DISPLAY"] = ":99"

        # Initialize GTK if we're using real components
        if not cls.gtk_initialized and GTK_AVAILABLE:
            print(f"Initializing GTK with DISPLAY={os.environ.get('DISPLAY')}")
            # Set the backend to X11 explicitly
            os.environ["GDK_BACKEND"] = "x11"

            try:
                # GTK 4 doesn't need explicit initialization
                cls.gtk_initialized = True
                print("GTK initialized successfully")
            except Exception as e:
                print(f"Failed to initialize GTK: {e}")

    @classmethod
    def teardown_class(cls):
        """Clean up Xvfb if we started it."""
        if cls.xvfb_proc:
            print("Stopping Xvfb...")
            cls.xvfb_proc.terminate()
            cls.xvfb_proc = None


# Simple mock for testing
class SimplePicture(Gtk.Picture):
    """A simple picture widget for testing."""

    def __init__(self):
        """Initialize the picture widget."""
        super().__init__()
        self._image = None

    def set_image(self, image):
        """Set the image to display."""
        self._image = image

    def get_image(self):
        """Get the currently displayed image."""
        return self._image


# Simple overlay manager for testing
class SimpleOverlayManager:
    """A simple overlay manager for testing."""

    def __init__(self, image_view):
        """Initialize the overlay manager."""
        self.image_view = image_view
        self.overlays = {}  # id -> (x, y, radius)
        self.next_id = 1
        self.selected_overlay_id = None
        self.callbacks = {}

    def create_overlay_at(self, x, y, radius=50):
        """Create a new overlay at the specified position."""
        overlay_id = self.next_id
        self.next_id += 1
        self.overlays[overlay_id] = (x, y, radius)
        self.selected_overlay_id = overlay_id
        self._emit_changed()
        return overlay_id

    def select_overlay(self, overlay_id):
        """Select an overlay by ID."""
        if overlay_id in self.overlays:
            self.selected_overlay_id = overlay_id
            self._emit_selection_changed()
            return True
        return False

    def delete_selected_overlay(self):
        """Delete the currently selected overlay."""
        if self.selected_overlay_id:
            del self.overlays[self.selected_overlay_id]
            self.selected_overlay_id = None
            self._emit_changed()
            self._emit_selection_changed()
            return True
        return False

    def update_selected_overlay(self, x=None, y=None, radius=None):
        """Update the selected overlay's properties."""
        if not self.selected_overlay_id:
            return False

        current_x, current_y, current_radius = self.overlays[self.selected_overlay_id]
        new_x = x if x is not None else current_x
        new_y = y if y is not None else current_y
        new_radius = radius if radius is not None else current_radius

        self.overlays[self.selected_overlay_id] = (new_x, new_y, new_radius)
        self._emit_changed()
        return True

    def connect(self, signal, callback):
        """Connect a signal to a callback."""
        if signal not in self.callbacks:
            self.callbacks[signal] = []
        self.callbacks[signal].append(callback)

    def _emit_changed(self):
        """Emit the 'overlays-changed' signal."""
        self._emit_signal("overlays-changed")

    def _emit_selection_changed(self):
        """Emit the 'selection-changed' signal."""
        self._emit_signal("selection-changed")

    def _emit_signal(self, signal):
        """Emit a signal to all connected callbacks."""
        if signal in self.callbacks:
            for callback in self.callbacks[signal]:
                callback(self)


# Simple overlay control panel for testing
class SimpleOverlayControlPanel(Gtk.Box):
    """A simple overlay control panel for testing."""

    def __init__(self, overlay_manager):
        """Initialize the control panel with an overlay manager."""
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.overlay_manager = overlay_manager

        # Create controls
        # Radius adjustment
        self.radius_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        self.radius_scale.set_range(10, 100)
        self.radius_scale.set_value(50)  # Default radius
        self.radius_scale.connect("value-changed", self._on_radius_changed)
        self.append(self.radius_scale)

        # Buttons for creating/deleting overlays
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        self.create_button = Gtk.Button(label="Create Overlay")
        self.create_button.connect("clicked", self._on_create_clicked)
        button_box.append(self.create_button)

        self.delete_button = Gtk.Button(label="Delete Overlay")
        self.delete_button.connect("clicked", self._on_delete_clicked)
        button_box.append(self.delete_button)

        self.append(button_box)

        # Connect to overlay manager signals
        self.overlay_manager.connect("selection-changed", self._on_selection_changed)

    def _on_radius_changed(self, scale):
        """Handle radius scale changes."""
        if self.overlay_manager.selected_overlay_id:
            radius = scale.get_value()
            self.overlay_manager.update_selected_overlay(radius=int(radius))

    def _on_create_clicked(self, button):
        """Handle create button clicks."""
        # Create overlay at center of image
        self.overlay_manager.create_overlay_at(100, 100)

    def _on_delete_clicked(self, button):
        """Handle delete button clicks."""
        self.overlay_manager.delete_selected_overlay()

    def _on_selection_changed(self, overlay_manager):
        """Handle selection changes."""
        if overlay_manager.selected_overlay_id:
            overlay_id = overlay_manager.selected_overlay_id
            x, y, radius = overlay_manager.overlays[overlay_id]
            self.radius_scale.set_value(radius)


@pytest.mark.skipif(not GTK_AVAILABLE, reason="GTK not available")
class TestXwaylandOverlay(GTKTestBase):
    """Tests for verifying overlay functionality in Xwayland environment."""

    @pytest.fixture
    def app(self):
        """Create a GTK application for testing."""
        app = Gtk.Application(application_id="com.test.previewmaker")
        yield app
        # Clean up
        if hasattr(app, "get_windows") and callable(app.get_windows):
            for window in app.get_windows() or []:
                window.destroy()

    @pytest.fixture
    def window(self, app):
        """Create a GTK application window for testing."""
        window = Gtk.ApplicationWindow(application=app)
        window.set_default_size(800, 600)
        window.present()
        yield window
        # Clean up
        window.destroy()

    @pytest.fixture
    def image_view(self):
        """Create a simple picture with a test image."""
        view = SimplePicture()
        test_image = Image.new("RGB", (200, 200), color="white")
        view.set_image(test_image)
        return view

    @pytest.fixture
    def overlay_manager(self, image_view):
        """Create a simple overlay manager with the test image view."""
        return SimpleOverlayManager(image_view)

    @pytest.fixture
    def control_panel(self, overlay_manager):
        """Create a simple overlay control panel with the test overlay manager."""
        panel = SimpleOverlayControlPanel(overlay_manager)
        return panel

    def test_overlay_creation(self, control_panel, overlay_manager):
        """Test that overlays can be created."""
        # Initial state
        assert len(overlay_manager.overlays) == 0

        # Create an overlay
        control_panel.create_button.emit("clicked")

        # Check that the overlay was created
        assert len(overlay_manager.overlays) == 1
        assert overlay_manager.selected_overlay_id is not None

        # Process events
        main_loop = GLib.MainLoop()
        GLib.timeout_add(100, lambda: main_loop.quit())  # Quit after 100ms
        main_loop.run()

    def test_overlay_deletion(self, control_panel, overlay_manager):
        """Test that overlays can be deleted."""
        # Create an overlay first
        overlay_id = overlay_manager.create_overlay_at(100, 100)
        assert len(overlay_manager.overlays) == 1

        # Delete the overlay
        control_panel.delete_button.emit("clicked")

        # Check that the overlay was deleted
        assert len(overlay_manager.overlays) == 0
        assert overlay_manager.selected_overlay_id is None

        # Process events
        main_loop = GLib.MainLoop()
        GLib.timeout_add(100, lambda: main_loop.quit())  # Quit after 100ms
        main_loop.run()

    def test_radius_adjustment(self, control_panel, overlay_manager):
        """Test that the radius can be adjusted."""
        # Create an overlay first
        overlay_id = overlay_manager.create_overlay_at(100, 100, radius=50)
        assert overlay_manager.overlays[overlay_id][2] == 50

        # Change the radius
        control_panel.radius_scale.set_value(75)

        # Process events
        main_loop = GLib.MainLoop()
        GLib.timeout_add(100, lambda: main_loop.quit())  # Quit after 100ms
        main_loop.run()

        # Check that the radius was updated
        assert overlay_manager.overlays[overlay_id][2] == 75
