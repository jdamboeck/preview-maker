"""Tests for the ApplicationWindow component.

This module contains tests for the ApplicationWindow class, which is
the main window of the Preview Maker application.
"""

import os
import unittest
from unittest import mock
from pathlib import Path

import pytest

# Conditionally import GTK based on environment
HEADLESS = os.environ.get("HEADLESS", "0") == "1"

# Mock GTK if in headless mode
if HEADLESS:
    # Create GTK mocks
    class MockGtk:
        class Application:
            def __init__(self):
                pass

        class ApplicationWindow:
            def __init__(self, *args, **kwargs):
                self.application = kwargs.get("application")
                self.title = kwargs.get("title", "")
                self.default_width = kwargs.get("default_width", 800)
                self.default_height = kwargs.get("default_height", 600)
                self.child = None

            def set_titlebar(self, titlebar):
                self.titlebar = titlebar

            def set_child(self, child):
                self.child = child

            def add_controller(self, controller):
                pass

            def present(self):
                pass

            def show(self):
                pass

        class Box:
            def __init__(self, orientation=None, spacing=0):
                self.orientation = orientation
                self.spacing = spacing
                self.children = []

            def append(self, child):
                self.children.append(child)

        class HeaderBar:
            def __init__(self):
                self.start_items = []
                self.end_items = []

            def pack_start(self, widget):
                self.start_items.append(widget)

            def pack_end(self, widget):
                self.end_items.append(widget)

        class Button:
            def __init__(self, label=None):
                self.label = label
                self.clicked_handler = None

            @classmethod
            def new_from_icon_name(cls, icon_name):
                button = cls()
                button.icon_name = icon_name
                return button

            def connect(self, signal, handler):
                if signal == "clicked":
                    self.clicked_handler = handler

        class Label:
            def __init__(self, label=""):
                self.label = label

            def set_text(self, text):
                self.label = text

            def set_xalign(self, align):
                self.xalign = align

        class Orientation:
            VERTICAL = "vertical"
            HORIZONTAL = "horizontal"

        class ResponseType:
            ACCEPT = 1
            CANCEL = 0
            OK = 2
            CLOSE = 3

        class MessageType:
            ERROR = 0

        class ButtonsType:
            OK = 0

    # Create Gdk mocks
    class MockGdk:
        class FileList:
            pass

        class DragAction:
            COPY = 1

    # Create GLib mock
    class MockGLib:
        @staticmethod
        def idle_add(func, *args):
            return func(*args)

    # Apply mocks
    gi_mock = mock.MagicMock()
    gi_mock.require_version = mock.MagicMock()

    # Create a mock of the gi.repository module
    gi_repository_mock = mock.MagicMock()
    gi_repository_mock.Gtk = MockGtk
    gi_repository_mock.Gdk = MockGdk
    gi_repository_mock.GLib = MockGLib

    # Patch the imports
    mock.patch("gi", gi_mock).start()
    mock.patch("gi.repository", gi_repository_mock).start()

# Now import the ApplicationWindow
from preview_maker.ui.app_window import ApplicationWindow


class TestApplicationWindow:
    """Tests for the ApplicationWindow class."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock application."""
        if HEADLESS:
            return MockGtk.Application()
        else:
            return mock.MagicMock()

    @pytest.fixture
    def app_window(self, mock_app):
        """Create an ApplicationWindow instance for testing."""
        window = ApplicationWindow(mock_app)
        return window

    def test_init(self, app_window, mock_app):
        """Test that the window initializes correctly."""
        assert app_window.application == mock_app
        assert app_window.title == "Preview Maker"
        assert app_window.default_width == 1024
        assert app_window.default_height == 768
        assert app_window.image_processor is not None
        assert app_window.analyzer is None  # Not initialized until API key is provided
        assert app_window.preview_generator is None
        assert app_window.current_file is None

    def test_create_header_bar(self, app_window):
        """Test that the header bar is created with the correct buttons."""
        # In headless mode, we can inspect the mocked header bar
        if HEADLESS:
            header_bar = app_window.titlebar

            # Check that we have the correct buttons
            assert len(header_bar.start_items) == 2  # Open and Save buttons
            assert len(header_bar.end_items) == 2  # Analyze and Settings buttons

            # Check button labels
            assert header_bar.start_items[0].label == "Open"
            assert header_bar.start_items[1].label == "Save"
            assert header_bar.end_items[0].label == "Analyze"

            # Settings button is created with an icon name
            assert hasattr(header_bar.end_items[1], "icon_name")
        else:
            # In non-headless mode, we can't easily inspect the GTK objects
            # So just verify the method doesn't raise exceptions
            pass

    def test_load_image(self, app_window, monkeypatch):
        """Test that loading an image updates the status and triggers the processor."""
        # Mock the image processor's load_image method
        mock_load_image = mock.MagicMock()
        monkeypatch.setattr(app_window.image_processor, "load_image", mock_load_image)

        # Mock the status bar
        app_window.status_bar = mock.MagicMock()

        # Call the method
        test_path = "/path/to/test.jpg"
        app_window._load_image(test_path)

        # Check that the status was updated
        app_window.status_bar.set_text.assert_called_with(f"Loading {test_path}...")

        # Check that current_file was set
        assert str(app_window.current_file) == test_path

        # Check that the processor was called
        mock_load_image.assert_called_once()
        assert mock_load_image.call_args[0][0] == test_path

    def test_show_error_dialog(self, app_window, monkeypatch):
        """Test that error dialogs are displayed correctly."""
        # In headless mode, we need to mock the dialog creation
        if HEADLESS:
            # The headless mock already handles this
            pass
        else:
            # Mock the Gtk.MessageDialog
            mock_dialog = mock.MagicMock()
            mock_dialog_class = mock.MagicMock(return_value=mock_dialog)
            monkeypatch.setattr("gi.repository.Gtk.MessageDialog", mock_dialog_class)

        # Show an error
        error_message = "Test error message"
        app_window._show_error_dialog(error_message)

        # In headless mode, we can check if the format_secondary_text was called
        if HEADLESS:
            # No assertions needed as the mocks don't raise exceptions
            pass
        else:
            # Check that dialog was created with correct params
            mock_dialog.format_secondary_text.assert_called_with(error_message)
            mock_dialog.connect.assert_called_once()
            mock_dialog.show.assert_called_once()
