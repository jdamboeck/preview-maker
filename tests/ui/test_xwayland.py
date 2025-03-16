"""Test for verifying GTK functionality in Xwayland environment.

This test file contains a simple test to verify that GTK is working correctly
in the Xwayland environment.
"""

import os
import time
import subprocess
import pytest

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


@pytest.mark.skipif(not GTK_AVAILABLE, reason="GTK not available")
class TestXwayland(GTKTestBase):
    """Tests for verifying GTK functionality in Xwayland environment."""

    def test_gtk_window_creation(self):
        """Test that a GTK window can be created."""
        # Create an application
        app = Gtk.Application(application_id="com.test.xwayland")

        # Create a window
        window = Gtk.ApplicationWindow(application=app)
        window.set_title("Test Window")
        window.set_default_size(400, 300)

        # Add a label
        label = Gtk.Label(label="Hello, Xwayland!")
        window.set_child(label)

        # Show the window
        window.present()

        # Process events for a short time
        main_loop = GLib.MainLoop()
        GLib.timeout_add(100, lambda: main_loop.quit())  # Quit after 100ms
        main_loop.run()

        # Clean up
        window.destroy()

        # If we got here without errors, the test passes
        assert True
