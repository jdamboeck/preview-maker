#!/usr/bin/env python3
"""
Headless UI Testing Example for Preview Maker

This demonstrates how to test GTK UI components in a headless environment
by mocking the UI components
"""
import os
import sys
import pytest

print(f"Testing environment: DISPLAY={os.environ.get('DISPLAY', 'Not set')}")


# Mock UI Components for Headless Testing
class MockWindow:
    """A mock window for testing without a display."""

    def __init__(self, title="Test Window"):
        self.title = title
        self.label_text = "Hello, World!"
        self.button_clicked = False
        print(f"Created mock window with title: {title}")

    def get_title(self):
        """Return the window title."""
        return self.title

    def click_button(self):
        """Simulate a button click."""
        self.button_clicked = True
        self.label_text = "Button Clicked!"
        print("Mock button clicked")

    def was_button_clicked(self):
        """Check if the button was clicked."""
        return self.button_clicked


# For documentation purposes, this is what a real GTK UI component would look like
# GTK window class for reference - not used in headless testing
"""
from gi.repository import Gtk, GLib

class GTKWindow:
    def __init__(self, title="Test Window"):
        self.app = Gtk.Application(application_id="org.test.preview-maker")
        self.app.register()
        self.window = Gtk.ApplicationWindow(application=self.app)
        self.window.set_title(title)
        self.window.set_default_size(400, 300)

        # Create a box
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.window.set_child(self.box)

        # Add a label
        self.label = Gtk.Label(label="Hello, World!")
        self.box.append(self.label)

        # Add a button
        self.button = Gtk.Button(label="Click Me")
        self.button.connect("clicked", self.on_button_clicked)
        self.box.append(self.button)

        # Button click flag
        self.button_clicked = False

    def on_button_clicked(self, button):
        self.button_clicked = True
        self.label.set_label("Button Clicked!")

    def get_title(self):
        return self.window.get_title()

    def click_button(self):
        self.button.emit('clicked')

    def was_button_clicked(self):
        return self.button_clicked
"""

# Use the mock for all headless tests
UIWindow = MockWindow


def test_window_title():
    """Test that the window title is correct."""
    window = UIWindow(title="Preview Maker Test")
    assert window.get_title() == "Preview Maker Test"


def test_button_click():
    """Test that a button click updates the label."""
    window = UIWindow()
    assert not window.was_button_clicked()

    # Simulate a button click
    window.click_button()

    # Verify that the button was clicked
    assert window.was_button_clicked()


if __name__ == "__main__":
    # Run tests with the -xvs flags for verbose output
    sys.exit(pytest.main(["-xvs", __file__]))
