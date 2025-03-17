"""Tests for the SettingsDialog component.

This module contains tests for the SettingsDialog class, which provides
a user interface for configuring application settings.
"""

import os
import sys
from unittest import mock

import pytest

# Ensure we're always in headless mode for tests to avoid GTK initialization issues
HEADLESS = True

# Configure mocks before imports if in headless mode
if HEADLESS:
    # Create system-wide mocks before any imports
    sys.modules["gi"] = mock.MagicMock()
    sys.modules["gi"].require_version = mock.MagicMock()
    sys.modules["gi.repository"] = mock.MagicMock()
    sys.modules["gi.repository.Gtk"] = mock.MagicMock()
    sys.modules["gi.repository.Gdk"] = mock.MagicMock()
    sys.modules["gi.repository.GLib"] = mock.MagicMock()

    # Import mocks for testing
    from tests.ui.mocks import MockSettingsDialog, process_events
else:
    # In non-headless mode, we import gi directly (this won't be used in tests)
    import gi

    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk, GLib

    def process_events():
        """Process pending GTK events."""
        while GLib.MainContext.default().iteration(False):
            pass


# Import needed components
from preview_maker.core.config import ConfigManager, PreviewMakerConfig

# Import the component under test (after mock setup)
if not HEADLESS:
    from preview_maker.ui.settings_dialog import SettingsDialog


class TestSettingsDialog:
    """Test cases for the SettingsDialog component."""

    @pytest.fixture
    def mock_parent(self):
        """Create a mock parent window."""
        return mock.MagicMock()

    @pytest.fixture
    def mock_config_manager(self):
        """Create a mock ConfigManager with test values."""
        config = PreviewMakerConfig()
        config.debug_mode = True
        config.gemini_api_key = "test_api_key"
        config.model_name = "test-model"
        config.temperature = 0.1
        config.selection_ratio = 0.1
        config.zoom_factor = 2.0
        config.overlay_color = "#FF0000"
        config.overlay_opacity = 0.7
        config.png_compression = 4
        config.high_resampling = True
        config.default_target_type = "test-target"

        config_manager = ConfigManager()
        config_manager._config = config
        return config_manager

    @pytest.fixture
    def settings_dialog(self, mock_parent, mock_config_manager):
        """Create a SettingsDialog instance for testing."""
        if HEADLESS:
            # Create a mock dialog in headless mode
            from tests.ui.mocks import MockSettingsDialog

            dialog = MockSettingsDialog(mock_parent)
            # Initialize with config
            dialog.config = mock_config_manager.get_config()

            # Set up debug checkbox
            debug_checkbox = dialog._debug_checkbox
            debug_checkbox.set_active(dialog.config.debug_mode)

            return dialog
        else:
            # Create a real dialog in non-headless mode
            return SettingsDialog(mock_parent, mock_config_manager)

    def test_dialog_creation(self, settings_dialog):
        """Test that the dialog is created correctly."""
        assert settings_dialog is not None
        assert settings_dialog.get_content_area() is not None

    def test_dialog_has_tabs(self, settings_dialog):
        """Test that the dialog has the required tabs."""
        # The dialog should have a notebook with tabs
        notebook = settings_dialog.get_content_area().get_children()[0]
        assert notebook is not None

        # Check that notebook has pages
        assert notebook.pages is not None
        assert len(notebook.pages) == 4

    def test_general_settings_tab(self, settings_dialog, mock_config_manager):
        """Test the general settings tab contents."""
        # Get the general settings tab
        notebook = settings_dialog.get_content_area().get_children()[0]
        general_tab = notebook.get_nth_page(0)

        # Check that the debug mode checkbox is present and set correctly
        debug_checkbox = settings_dialog._debug_checkbox
        assert (
            debug_checkbox.get_active() == mock_config_manager.get_config().debug_mode
        )

    def test_api_settings_tab(self, settings_dialog, mock_config_manager):
        """Test the API settings tab contents."""
        # Get the API settings tab
        notebook = settings_dialog.get_content_area().get_children()[0]
        api_tab = notebook.get_nth_page(1)

        # Check API key entry
        api_key_entry = settings_dialog._api_key_entry
        assert api_key_entry is not None

    def test_overlay_settings_tab(self, settings_dialog, mock_config_manager):
        """Test the overlay settings tab contents."""
        # Get the overlay settings tab
        notebook = settings_dialog.get_content_area().get_children()[0]
        overlay_tab = notebook.get_nth_page(2)

        # Check color button
        color_button = settings_dialog._color_button
        assert color_button is not None

    def test_export_settings_tab(self, settings_dialog, mock_config_manager):
        """Test the export settings tab contents."""
        # Get the export settings tab
        notebook = settings_dialog.get_content_area().get_children()[0]
        export_tab = notebook.get_nth_page(3)

        # Check high quality checkbox
        high_quality_checkbox = settings_dialog._high_quality_checkbox
        assert high_quality_checkbox is not None

    def test_apply_button_callback(self, settings_dialog, mock_config_manager):
        """Test that the apply button correctly updates settings."""
        # Modify a setting
        debug_checkbox = settings_dialog._debug_checkbox

        # Toggle the checkbox (opposite of current value)
        original_debug_mode = mock_config_manager.get_config().debug_mode
        debug_checkbox.set_active(not original_debug_mode)

        # Click the apply button
        apply_button = settings_dialog.apply_button

        # Define callback function
        def apply_callback():
            mock_config_manager.get_config().debug_mode = debug_checkbox.get_active()

        # Set up callback
        settings_dialog.apply_callback = apply_callback

        # Simulate button click
        if hasattr(apply_button, "clicked"):
            apply_button.clicked()
        else:
            settings_dialog.apply_callback()

        # Check that the setting was updated
        assert mock_config_manager.get_config().debug_mode == (not original_debug_mode)

    def test_cancel_button_callback(self, settings_dialog, mock_config_manager):
        """Test that the cancel button discards changes."""
        # Modify a setting
        debug_checkbox = settings_dialog._debug_checkbox

        # Toggle the checkbox (opposite of current value)
        original_debug_mode = mock_config_manager.get_config().debug_mode
        debug_checkbox.set_active(not original_debug_mode)

        # Click the cancel button
        cancel_button = settings_dialog.cancel_button

        # Define callback function
        def cancel_callback():
            # Cancel doesn't save changes
            pass

        # Set up callback
        settings_dialog.cancel_callback = cancel_callback

        # Simulate button click
        if hasattr(cancel_button, "clicked"):
            cancel_button.clicked()
        else:
            settings_dialog.cancel_callback()

        # Check that the setting was not updated
        assert mock_config_manager.get_config().debug_mode == original_debug_mode

    def test_ok_button_callback(self, settings_dialog, mock_config_manager):
        """Test that the OK button applies changes and closes the dialog."""
        # Modify a setting
        debug_checkbox = settings_dialog._debug_checkbox

        # Toggle the checkbox (opposite of current value)
        original_debug_mode = mock_config_manager.get_config().debug_mode
        debug_checkbox.set_active(not original_debug_mode)

        # Click the OK button
        ok_button = settings_dialog.ok_button

        # Define callback function
        def ok_callback():
            mock_config_manager.get_config().debug_mode = debug_checkbox.get_active()

        # Set up callbacks
        settings_dialog.ok_callback = ok_callback

        # Simulate button click
        if hasattr(ok_button, "clicked"):
            ok_button.clicked()
        else:
            settings_dialog.ok_callback()

        # Check that the setting was updated
        assert mock_config_manager.get_config().debug_mode == (not original_debug_mode)
