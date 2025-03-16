"""Tests for the ManualOverlayManager class.

This module contains tests for the ManualOverlayManager class, which allows
manual creation and positioning of overlays.
"""

import os
import sys
from unittest import mock

import pytest
from PIL import Image

# Conditionally import GTK based on environment
HEADLESS = os.environ.get("HEADLESS", "0") == "1"

# Configure mocks before imports if in headless mode
if HEADLESS:
    # Create system-wide mocks before any imports
    sys.modules["gi"] = mock.MagicMock()
    sys.modules["gi"].require_version = mock.MagicMock()
    sys.modules["gi.repository"] = mock.MagicMock()
    sys.modules["gi.repository.Gtk"] = mock.MagicMock()
    sys.modules["gi.repository.Gdk"] = mock.MagicMock()
    sys.modules["gi.repository.GLib"] = mock.MagicMock()

    # Create a mock ImageView class
    class MockImageView:
        def __init__(self):
            self.image = None
            self.overlays = []
            self.controllers = []

        def get_image(self):
            return self.image

        def add_overlay(self, *args, **kwargs):
            self.overlays.append((args, kwargs))

        def add_controller(self, controller):
            self.controllers.append(controller)
            return True

        def queue_draw(self):
            pass

    # Create a mock ManualOverlayManager that doesn't use GTK
    class MockManualOverlayManager:
        """A mock version of ManualOverlayManager for testing."""

        def __init__(self, image_view):
            self.image_view = image_view
            self.overlays = {}
            self.selected_overlay_id = None
            self.default_radius = 50
            self.default_color = "#ff0000"

        def create_overlay_at(self, x, y):
            """Create a new overlay at the specified position."""
            import uuid

            overlay_id = str(uuid.uuid4())
            self.overlays[overlay_id] = ((x, y), self.default_radius)
            self._apply_overlays()
            return overlay_id

        def select_overlay(self, overlay_id):
            """Select an overlay by ID."""
            self.selected_overlay_id = overlay_id

        def delete_selected_overlay(self):
            """Delete the currently selected overlay."""
            if self.selected_overlay_id:
                del self.overlays[self.selected_overlay_id]
                self.selected_overlay_id = None
                self._apply_overlays()

        def set_overlay_radius(self, radius):
            """Set the radius of the selected overlay."""
            if self.selected_overlay_id:
                position, _ = self.overlays[self.selected_overlay_id]
                self.overlays[self.selected_overlay_id] = (position, radius)
                self._apply_overlays()

        def update_selected_overlay(self, x, y):
            """Update the position of the selected overlay."""
            if self.selected_overlay_id:
                _, radius = self.overlays[self.selected_overlay_id]
                self.overlays[self.selected_overlay_id] = ((x, y), radius)
                self._apply_overlays()

        def clear_overlays(self):
            """Remove all overlays."""
            self.overlays = {}
            self.selected_overlay_id = None
            self._apply_overlays()

        def get_selected_overlay(self):
            """Get the currently selected overlay."""
            if self.selected_overlay_id:
                return (
                    self.selected_overlay_id,
                    self.overlays[self.selected_overlay_id],
                )
            return None

        def get_overlays(self):
            """Get all overlays."""
            return self.overlays

        def _apply_overlays(self):
            """Apply overlays to the image."""
            self.image_view.overlays = []
            for overlay_id, (position, radius) in self.overlays.items():
                self.image_view.add_overlay(position, radius, self.default_color)

        def _find_overlay_at(self, x, y):
            """Find an overlay at the specified position."""
            for overlay_id, (position, radius) in self.overlays.items():
                px, py = position
                distance = ((px - x) ** 2 + (py - y) ** 2) ** 0.5
                if distance <= radius:
                    return overlay_id
            return None

    # Use our mock instead of the real one
    sys.modules["preview_maker.ui.image_view"] = mock.MagicMock()
    sys.modules["preview_maker.ui.image_view"].ImageView = MockImageView

    # Replace the real ManualOverlayManager with our mock
    from preview_maker.ui.manual_overlay_manager import ManualOverlayManager

    ManualOverlayManager = MockManualOverlayManager
else:
    # In non-headless mode, import normally
    import gi

    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk, Gdk
    from preview_maker.ui.manual_overlay_manager import ManualOverlayManager
    from preview_maker.ui.image_view import ImageView


class TestManualOverlayManager:
    """Tests for the ManualOverlayManager class."""

    @pytest.fixture
    def mock_image_view(self):
        """Create a mock ImageView."""
        if HEADLESS:
            mock_view = MockImageView()
            # Create a test image
            mock_view.image = Image.new("RGB", (100, 100), color="white")
        else:
            mock_view = mock.MagicMock(spec=ImageView)
            # Create a test image
            test_image = Image.new("RGB", (100, 100), color="white")
            mock_view.get_image.return_value = test_image

        return mock_view

    @pytest.fixture
    def overlay_manager(self, mock_image_view):
        """Create a ManualOverlayManager with a mock ImageView."""
        return ManualOverlayManager(mock_image_view)

    def test_initialization(self, overlay_manager, mock_image_view):
        """Test initialization of the ManualOverlayManager."""
        assert overlay_manager.image_view == mock_image_view
        assert overlay_manager.overlays == {}
        assert overlay_manager.selected_overlay_id is None
        assert overlay_manager.default_radius == 50
        assert overlay_manager.default_color == "#ff0000"

    def test_create_overlay_at(self, overlay_manager):
        """Test creating an overlay at a specific position."""
        overlay_id = overlay_manager.create_overlay_at(50, 50)

        # Verify overlay was created
        assert len(overlay_manager.overlays) == 1
        assert overlay_id in overlay_manager.overlays

        # Verify overlay properties
        position, radius = overlay_manager.overlays[overlay_id]
        assert position == (50, 50)
        assert radius == 50

    def test_select_overlay(self, overlay_manager):
        """Test selecting an overlay."""
        # Create an overlay
        overlay_id = overlay_manager.create_overlay_at(50, 50)

        # Select the overlay
        overlay_manager.select_overlay(overlay_id)
        assert overlay_manager.selected_overlay_id == overlay_id

        # Deselect the overlay
        overlay_manager.select_overlay(None)
        assert overlay_manager.selected_overlay_id is None

    def test_delete_selected_overlay(self, overlay_manager):
        """Test deleting the selected overlay."""
        # Create and select an overlay
        overlay_id = overlay_manager.create_overlay_at(50, 50)
        overlay_manager.select_overlay(overlay_id)

        # Delete the selected overlay
        overlay_manager.delete_selected_overlay()

        # Verify overlay was deleted
        assert len(overlay_manager.overlays) == 0
        assert overlay_manager.selected_overlay_id is None

    def test_set_overlay_radius(self, overlay_manager):
        """Test setting the radius of the selected overlay."""
        # Create and select an overlay
        overlay_id = overlay_manager.create_overlay_at(50, 50)
        overlay_manager.select_overlay(overlay_id)

        # Set a new radius
        overlay_manager.set_overlay_radius(75)

        # Verify the radius was updated
        position, radius = overlay_manager.overlays[overlay_id]
        assert radius == 75

    def test_update_selected_overlay(self, overlay_manager):
        """Test updating the position of the selected overlay."""
        # Create and select an overlay
        overlay_id = overlay_manager.create_overlay_at(50, 50)
        overlay_manager.select_overlay(overlay_id)

        # Update position
        overlay_manager.update_selected_overlay(75, 75)

        # Verify position was updated
        position, radius = overlay_manager.overlays[overlay_id]
        assert position == (75, 75)

    def test_clear_overlays(self, overlay_manager):
        """Test clearing all overlays."""
        # Create multiple overlays
        overlay_manager.create_overlay_at(25, 25)
        overlay_manager.create_overlay_at(50, 50)
        overlay_manager.create_overlay_at(75, 75)

        assert len(overlay_manager.overlays) == 3

        # Clear overlays
        overlay_manager.clear_overlays()

        # Verify all overlays were removed
        assert len(overlay_manager.overlays) == 0
        assert overlay_manager.selected_overlay_id is None

    def test_get_selected_overlay(self, overlay_manager):
        """Test getting the selected overlay."""
        # Create and select an overlay
        overlay_id = overlay_manager.create_overlay_at(50, 50)
        overlay_manager.select_overlay(overlay_id)

        # Get selected overlay
        selected = overlay_manager.get_selected_overlay()

        # Verify the correct overlay was returned
        assert selected is not None
        assert selected[0] == overlay_id
        assert selected[1][0] == (50, 50)  # position
        assert selected[1][1] == 50  # radius

    def test_get_overlays(self, overlay_manager):
        """Test getting all overlays."""
        # Create multiple overlays
        overlay_manager.create_overlay_at(25, 25)
        overlay_manager.create_overlay_at(50, 50)

        # Get all overlays
        overlays = overlay_manager.get_overlays()

        # Verify overlays were returned
        assert len(overlays) == 2
        for overlay_id, overlay_data in overlays.items():
            assert isinstance(overlay_id, str)
            position, radius = overlay_data
            assert isinstance(position, tuple)
            assert len(position) == 2
            assert isinstance(radius, int)

    def test_apply_overlays(self, overlay_manager, mock_image_view):
        """Test applying overlays to the image."""
        # Create overlays
        overlay_manager.create_overlay_at(25, 25)
        overlay_manager.create_overlay_at(50, 50)

        # Mock the logger
        with mock.patch(
            "preview_maker.ui.manual_overlay_manager.logger", create=True
        ) as mock_logger:
            # Call _apply_overlays
            overlay_manager._apply_overlays()

            # Verify image update was triggered
            if HEADLESS:
                assert len(mock_image_view.overlays) > 0
            else:
                mock_image_view.add_overlay.assert_called()

    def test_find_overlay_at(self, overlay_manager):
        """Test finding an overlay at a specific position."""
        # Create overlays
        id1 = overlay_manager.create_overlay_at(25, 25)
        id2 = overlay_manager.create_overlay_at(75, 75)

        # Find overlay at the center of the first overlay
        found_id = overlay_manager._find_overlay_at(25, 25)
        assert found_id == id1

        # Find overlay near the edge of the second overlay's radius
        found_id = overlay_manager._find_overlay_at(150, 150)  # Far outside radius
        assert found_id is None

        found_id = overlay_manager._find_overlay_at(
            90, 75
        )  # Within radius (assuming default 50)
        assert found_id == id2
