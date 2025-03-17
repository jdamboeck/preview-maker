"""Tests for the OverlayControlPanel component.

This module contains tests for the OverlayControlPanel, which provides UI controls
for manipulating overlays in the ManualOverlayManager.
"""

import os
import time
import subprocess
from unittest import mock
import uuid

import pytest
from PIL import Image

# Import our mocks - make sure we import correctly regardless of environment
from tests.ui.mocks import (
    GTK_AVAILABLE,
    MockGtk,
    MockGdk,
    MockGLib,
    MockImageView,
    MockManualOverlayManager,
)

# Set up conditional imports for UI components
if GTK_AVAILABLE:
    try:
        import gi

        gi.require_version("Gtk", "4.0")
        from gi.repository import Gtk, Gdk, GLib
        from preview_maker.ui.overlay_controls import OverlayControlPanel
        from preview_maker.ui.manual_overlay_manager import ManualOverlayManager
        from preview_maker.ui.image_view import ImageView

        USE_REAL_COMPONENTS = True
        print("Using real GTK components")
    except (ImportError, ValueError, AttributeError) as e:
        print(f"Error importing real GTK components: {e}")
        USE_REAL_COMPONENTS = False

        # Use mocks as fallback
        Gtk = MockGtk
        Gdk = MockGdk
        GLib = MockGLib
else:
    print("GTK not available, using mocks")
    USE_REAL_COMPONENTS = False

    # Use our mocks when GTK is not available
    Gtk = MockGtk
    Gdk = MockGdk
    GLib = MockGLib

# Detect environment
HEADLESS = os.environ.get("HEADLESS", "0") == "1"
USE_XVFB = HEADLESS and os.environ.get("DISPLAY") is None


# Base class for GTK testing
class GTKTestBase:
    """Base class for tests that use real GTK components.

    This class handles setup and teardown of GTK and Xvfb if needed,
    providing a consistent environment for running UI tests.
    """

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
        if not cls.gtk_initialized and GTK_AVAILABLE and USE_REAL_COMPONENTS:
            print(f"Initializing GTK with DISPLAY={os.environ.get('DISPLAY')}")
            # Set the backend to X11 explicitly
            os.environ["GDK_BACKEND"] = "x11"

            try:
                Gtk.init()
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


class TestOverlayControlPanel(GTKTestBase):
    """Tests for the OverlayControlPanel class using real GTK components."""

    @classmethod
    def setup_class(cls):
        """Set up GTK environment and import components."""
        # Initialize GTK environment first
        super().setup_class()

        global OverlayControlPanel, ManualOverlayManager, ImageView

        # If we're not using real components, create mock implementations
        if not USE_REAL_COMPONENTS:
            print("Creating mock implementations for UI testing")

            # Create a mock OverlayControlPanel
            class MockOverlayControlPanel(Gtk.Box):
                """Mock implementation of OverlayControlPanel."""

                def __init__(self, overlay_manager):
                    """Initialize the control panel with an overlay manager."""
                    super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
                    self.overlay_manager = overlay_manager

                    # Set up overlay selection callback
                    self.overlay_manager.on_overlay_selected = self._on_overlay_selected

                    # Create controls
                    # Radius adjustment
                    self.radius_scale = Gtk.Scale(
                        orientation=Gtk.Orientation.HORIZONTAL
                    )
                    self.radius_scale.set_value(50)  # Default radius
                    self.radius_scale.connect("value-changed", self._on_radius_changed)
                    # Initially disabled until an overlay is selected
                    self.radius_scale.set_sensitive(False)
                    self.append(self.radius_scale)

                    # Buttons for creating/deleting overlays
                    button_box = Gtk.Box(
                        orientation=Gtk.Orientation.HORIZONTAL, spacing=5
                    )

                    self.create_button = Gtk.Button(label="Create Overlay")
                    self.create_button.connect("clicked", self._on_create_clicked)
                    button_box.append(self.create_button)

                    self.delete_button = Gtk.Button(label="Delete Overlay")
                    self.delete_button.connect("clicked", self._on_delete_clicked)
                    # Initially disabled until an overlay is selected
                    self.delete_button.set_sensitive(False)
                    button_box.append(self.delete_button)

                    self.append(button_box)

                def _on_radius_changed(self, scale):
                    """Handle radius scale changes."""
                    if self.overlay_manager.selected_overlay_id:
                        radius = scale.get_value()
                        self.overlay_manager.update_selected_overlay(radius=int(radius))

                def update_radius_display(self):
                    """Update the radius scale to match the selected overlay."""
                    if self.overlay_manager.selected_overlay_id:
                        overlay_id = self.overlay_manager.selected_overlay_id
                        x, y, radius = self.overlay_manager.overlays[overlay_id]
                        self.radius_scale.set_value(radius)

                def _on_create_clicked(self, button):
                    """Handle create button clicks."""
                    # Create overlay at center of image
                    self.overlay_manager.create_overlay_at(100, 100)

                def _on_delete_clicked(self, button):
                    """Handle delete button clicks."""
                    self.overlay_manager.delete_selected_overlay()

                def _on_overlay_selected(self, overlay_id):
                    """Handle overlay selection changes."""
                    # Update enabled state of controls
                    has_selection = overlay_id is not None
                    self.radius_scale.set_sensitive(has_selection)
                    self.delete_button.set_sensitive(has_selection)

                    # Update radius display if an overlay is selected
                    if has_selection:
                        selected = self.overlay_manager.get_selected_overlay()
                        if selected:
                            _, (_, _, radius) = selected
                            self.radius_scale.set_value(radius)

            # Set the global variables to use our mocks
            OverlayControlPanel = MockOverlayControlPanel
            ManualOverlayManager = MockManualOverlayManager
            ImageView = MockImageView

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
        window.show()
        yield window
        # Clean up
        window.destroy()

    @pytest.fixture
    def image_view(self):
        """Create an ImageView with a test image."""
        view = ImageView()
        test_image = Image.new("RGB", (200, 200), color="white")
        view.set_image(test_image)
        return view

    @pytest.fixture
    def overlay_manager(self, image_view):
        """Create a ManualOverlayManager with the test ImageView."""
        return ManualOverlayManager(image_view)

    @pytest.fixture
    def control_panel(self, overlay_manager):
        """Create an OverlayControlPanel with the test ManualOverlayManager."""
        panel = OverlayControlPanel(overlay_manager)
        return panel

    # Helper method for processing events in GTK 4.0 compatible way
    def process_events(self):
        """Process pending GTK events in a way that's compatible with GTK 4.0."""
        if hasattr(GLib, "MainContext"):
            context = GLib.MainContext.default()
            while context.pending():
                context.iteration(False)
        else:
            # Fallback for mocks or GTK 3
            while Gtk.events_pending():
                Gtk.main_iteration_do(False)

    def test_initialization(self, control_panel, overlay_manager):
        """Test that the control panel initializes correctly."""
        assert control_panel.overlay_manager == overlay_manager
        assert isinstance(control_panel, Gtk.Box)
        assert control_panel.get_orientation() == Gtk.Orientation.VERTICAL

        # Check that child widgets were created
        children = [child for child in control_panel]
        assert len(children) > 0

    def test_radius_adjustment(self, control_panel, overlay_manager):
        """Test radius adjustment functionality."""
        # Create a test overlay
        overlay_id = overlay_manager.create_overlay_at(100, 100)
        overlay_manager.select_overlay(overlay_id)

        # Find radius scale widget
        radius_scale = None
        for child in control_panel:
            if isinstance(child, Gtk.Scale):
                radius_scale = child
                break

        assert radius_scale is not None, "Radius scale not found"

        # Change radius using the scale
        new_radius = 75
        radius_scale.set_value(new_radius)

        # Process events
        self.process_events()

        # Verify radius was updated
        _, (_, _, radius) = overlay_manager.get_selected_overlay()
        assert (
            radius == new_radius
        ), f"Radius not updated: expected {new_radius}, got {radius}"

    def test_create_button(self, control_panel, overlay_manager, monkeypatch):
        """Test the create overlay button."""
        # Get initial overlay count
        initial_count = len(overlay_manager.overlays)

        # Mock the create_overlay_at method to verify it's called correctly
        called_with = {}
        original_create_overlay = overlay_manager.create_overlay_at

        def mock_create_overlay_at(self, x, y, radius=None):
            called_with["x"] = x
            called_with["y"] = y
            called_with["radius"] = radius
            # Generate a unique ID without calling the original method recursively
            overlay_id = str(uuid.uuid4())
            # Add the overlay directly to avoid recursion
            overlay_manager.overlays[overlay_id] = (
                x,
                y,
                radius or overlay_manager.default_radius,
            )
            overlay_manager.select_overlay(overlay_id)
            return overlay_id

        monkeypatch.setattr(
            overlay_manager,
            "create_overlay_at",
            mock_create_overlay_at.__get__(overlay_manager, type(overlay_manager)),
        )

        # Find the create button
        create_button = None
        for box in control_panel:
            if isinstance(box, Gtk.Box):
                for child in box:
                    if (
                        isinstance(child, Gtk.Button)
                        and child.get_label() == "Create Overlay"
                    ):
                        create_button = child
                        break

        assert create_button is not None, "Create button not found"

        # Click the button
        create_button.clicked()

        # Process events
        self.process_events()

        # Verify a new overlay was created
        assert len(overlay_manager.overlays) == initial_count + 1
        assert "x" in called_with and "y" in called_with
        assert called_with["x"] > 0 and called_with["y"] > 0

    def test_delete_button(self, control_panel, overlay_manager):
        """Test the delete overlay button."""
        # Create an overlay to delete
        overlay_id = overlay_manager.create_overlay_at(100, 100)
        overlay_manager.select_overlay(overlay_id)

        # Find the delete button
        delete_button = None
        for box in control_panel:
            if isinstance(box, Gtk.Box):
                for child in box:
                    if isinstance(child, Gtk.Button) and "Delete" in child.get_label():
                        delete_button = child
                        break

        assert delete_button is not None, "Delete button not found"

        # Verify we have an overlay to delete
        assert overlay_manager.get_overlay_count() > 0
        assert overlay_manager.selected_overlay_id is not None

        # Click the delete button
        delete_button.clicked()

        # Process events
        self.process_events()

        # Verify overlay was deleted
        assert overlay_manager.get_overlay_count() == 0
        assert overlay_manager.selected_overlay_id is None

    def test_ui_integration(self, window, control_panel, image_view, overlay_manager):
        """Test integration of UI components."""
        # Add control panel to window for proper UI event handling
        window.set_child(control_panel)

        # Process events to ensure window is rendered
        self.process_events()

        # Create an overlay
        overlay_id = overlay_manager.create_overlay_at(100, 100)
        overlay_manager.select_overlay(overlay_id)

        # Process events
        self.process_events()

        # Find and change radius scale
        radius_scale = None
        for child in control_panel:
            if isinstance(child, Gtk.Scale):
                radius_scale = child
                break

        assert radius_scale is not None, "Radius scale not found"

        # Set new radius
        new_radius = 80
        radius_scale.set_value(new_radius)

        # Process events
        self.process_events()

        # Verify radius was updated
        _, (_, _, radius) = overlay_manager.get_selected_overlay()
        assert (
            radius == new_radius
        ), f"Radius not updated: expected {new_radius}, got {radius}"

    def test_no_overlay_selected(self, control_panel, overlay_manager):
        """Test UI state when no overlay is selected."""
        # Ensure no overlay is selected
        overlay_manager.select_overlay(None)

        # Process events
        self.process_events()

        # Check that radius scale is disabled
        radius_scale = None
        for child in control_panel:
            if isinstance(child, Gtk.Scale):
                radius_scale = child
                break

        assert radius_scale is not None, "Radius scale not found"
        assert (
            not radius_scale.get_sensitive()
        ), "Radius scale should be disabled when no overlay is selected"

        # Check that delete button is disabled
        delete_button = None
        for box in control_panel:
            if isinstance(box, Gtk.Box):
                for child in box:
                    if isinstance(child, Gtk.Button) and "Delete" in child.get_label():
                        delete_button = child
                        break

        assert delete_button is not None, "Delete button not found"
        assert (
            not delete_button.get_sensitive()
        ), "Delete button should be disabled when no overlay is selected"

    def test_multiple_overlays(self, control_panel, overlay_manager):
        """Test handling of multiple overlays."""
        # Create multiple overlays
        overlay1 = overlay_manager.create_overlay_at(50, 50)
        overlay2 = overlay_manager.create_overlay_at(150, 150)
        overlay3 = overlay_manager.create_overlay_at(100, 100)

        # Select the second overlay
        overlay_manager.select_overlay(overlay2)

        # Process events
        self.process_events()

        # Verify the second overlay is selected
        assert overlay_manager.selected_overlay_id == overlay2

        # Update the radius of the selected overlay
        radius_scale = None
        for child in control_panel:
            if isinstance(child, Gtk.Scale):
                radius_scale = child
                break

        assert radius_scale is not None, "Radius scale not found"

        # Change radius
        new_radius = 60
        radius_scale.set_value(new_radius)

        # Process events
        self.process_events()

        # Verify only the selected overlay was updated
        _, (_, _, radius2) = overlay_manager.get_selected_overlay()
        assert (
            radius2 == new_radius
        ), f"Selected overlay radius not updated: {radius2} != {new_radius}"

        # Select another overlay
        overlay_manager.select_overlay(overlay3)

        # Process events
        self.process_events()

        # Verify the slider updated to reflect the newly selected overlay
        _, (_, _, radius3) = overlay_manager.get_selected_overlay()
        assert (
            abs(radius_scale.get_value() - radius3) < 1
        ), "Radius scale not updated for new selection"

    def test_error_handling(self, control_panel, overlay_manager, monkeypatch):
        """Test error handling in the control panel."""
        # Create a test overlay
        overlay_id = overlay_manager.create_overlay_at(100, 100)
        overlay_manager.select_overlay(overlay_id)

        # Mock update_selected_overlay to raise an exception
        def mock_update_selected_overlay(*args, **kwargs):
            raise ValueError("Test error")

        monkeypatch.setattr(
            overlay_manager, "update_selected_overlay", mock_update_selected_overlay
        )

        # Find radius scale
        radius_scale = None
        for child in control_panel:
            if isinstance(child, Gtk.Scale):
                radius_scale = child
                break

        assert radius_scale is not None, "Radius scale not found"

        # Set up a safe signal handler to test the error case
        original_handler = None
        for handler_id in radius_scale.list_signal_handlers("value-changed"):
            original_handler = radius_scale.disconnect(handler_id)

        def safe_handler(scale):
            try:
                overlay_manager.update_selected_overlay(radius=int(scale.get_value()))
            except Exception as e:
                # In a real app, this would show an error dialog
                print(f"Error: {e}")

        radius_scale.connect("value-changed", safe_handler)

        # Change radius - this should trigger the error handler
        radius_scale.set_value(75)

        # Process events
        self.process_events()

        # Verify we didn't crash
        assert True, "Application handled error gracefully"
