"""Pytest configuration for Preview Maker tests.

This module contains fixtures and configuration for pytest.
"""

import os
import sys
from pathlib import Path
from unittest import mock

import pytest
from PIL import Image


# Check if we're running in headless mode
HEADLESS = os.environ.get("HEADLESS", "0") == "1"


@pytest.fixture
def test_image():
    """Create a test image for testing."""
    # Create a simple test image
    image = Image.new("RGB", (100, 100), color="white")
    return image


@pytest.fixture
def test_image_path(tmp_path, test_image):
    """Save a test image and return its path."""
    image_path = tmp_path / "test.jpg"
    test_image.save(image_path)
    return image_path


@pytest.fixture
def mock_gemini_response():
    """Create a mock response from the Gemini API."""
    return """
    I've analyzed the image and identified the following interesting regions:

    [
      {
        "x": 150,
        "y": 200,
        "radius": 50,
        "confidence": 0.9,
        "description": "A colorful flower in the foreground"
      },
      {
        "x": 300,
        "y": 150,
        "radius": 40,
        "confidence": 0.8,
        "description": "An interesting architectural detail"
      },
      {
        "x": 100,
        "y": 350,
        "radius": 30,
        "confidence": 0.7,
        "description": "A small animal partially hidden"
      }
    ]

    These regions contain the most visually striking elements in the image.
    """


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

        class ContentFit:
            CONTAIN = 0

        class EventControllerScroll:
            @classmethod
            def new(cls, flags):
                return cls()

            def connect(self, signal, handler):
                pass

        class EventControllerScrollFlags:
            BOTH_AXES = 0

        class GestureDrag:
            @classmethod
            def new(cls):
                return cls()

            def connect(self, signal, handler):
                pass

            def get_offset(self):
                return (0, 0)

        class GestureClick:
            @classmethod
            def new(cls):
                return cls()

            def set_button(self, button):
                pass

            def connect(self, signal, handler):
                pass

        class CssProvider:
            def load_from_data(self, data):
                pass

        class StyleContext:
            @staticmethod
            def add_provider(context, provider, priority):
                pass

        class STYLE_PROVIDER_PRIORITY_APPLICATION:
            pass

    # Create Gdk mocks
    class MockGdk:
        class FileList:
            def get_files(self):
                return []

        class DragAction:
            COPY = 1

        class MemoryTexture:
            @classmethod
            def new(cls, width, height, format, bytes, stride):
                return cls()

        class MemoryFormat:
            R8G8B8A8 = 0

    # Create GLib mock
    class MockGLib:
        @staticmethod
        def idle_add(func, *args):
            return func(*args)

        @staticmethod
        def Bytes(data):
            return data

    # Create Gio mock
    class MockGio:
        class ApplicationFlags:
            FLAGS_NONE = 0

    # Apply mocks
    gi_mock = mock.MagicMock()
    gi_mock.require_version = mock.MagicMock()

    # Create a mock of the gi.repository module
    gi_repository_mock = mock.MagicMock()
    gi_repository_mock.Gtk = MockGtk
    gi_repository_mock.Gdk = MockGdk
    gi_repository_mock.GLib = MockGLib
    gi_repository_mock.Gio = MockGio

    # Patch the imports
    sys.modules["gi"] = gi_mock
    sys.modules["gi.repository"] = gi_repository_mock
    sys.modules["gi.repository.Gtk"] = MockGtk
    sys.modules["gi.repository.Gdk"] = MockGdk
    sys.modules["gi.repository.GLib"] = MockGLib
    sys.modules["gi.repository.Gio"] = MockGio
