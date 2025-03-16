#!/bin/bash
# Docker entrypoint script

# Set environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Function to run tests
run_tests() {
    echo "Running tests with pytest..."
    python -m pytest "$@"
}

# Function to run Xvfb if needed
run_xvfb() {
    if [ "${HEADLESS:-0}" = "1" ] && [ -z "${DISPLAY}" ]; then
        echo "Starting Xvfb for headless testing..."
        Xvfb :99 -screen 0 1280x1024x24 -ac &
        export DISPLAY=:99
        export GDK_BACKEND=x11
        sleep 1  # Give Xvfb time to start
    fi

    # Ensure we're using X11 backend for GTK
    export GDK_BACKEND=x11
}

# Function to run GTK tests
run_gtk_tests() {
    echo "Setting up environment for GTK tests..."
    run_xvfb

    # Run the tests
    if [ -n "$1" ]; then
        python -m pytest "$@" -v
    else
        python -m pytest tests/ui/ -v
    fi
}

# Function to run diagnostics
run_diagnostics() {
    echo "Running diagnostics..."
    echo "Python version:"
    python --version

    echo "Pip packages:"
    pip list

    echo "GTK version:"
    python -c "import gi; gi.require_version('Gtk', '4.0'); from gi.repository import Gtk; print(f'GTK version: {Gtk.get_major_version()}.{Gtk.get_minor_version()}.{Gtk.get_micro_version()}')" || echo "GTK not available"

    echo "Display settings:"
    echo "DISPLAY=$DISPLAY"
    echo "GDK_BACKEND=$GDK_BACKEND"

    echo "System packages:"
    apt list --installed | grep -E 'gtk|glib|gobject|cairo'
}

# Function to verify environment
verify_environment() {
    echo "Verifying environment..."
    run_diagnostics

    # Try importing GTK
    python -c "import gi; gi.require_version('Gtk', '4.0'); from gi.repository import Gtk; print('GTK import successful')" || echo "GTK import failed"

    # Check if we can run a simple GTK application
    if [ -z "${HEADLESS}" ] || [ "${HEADLESS}" != "1" ]; then
        echo "Testing GTK window creation..."
        python -c "
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
import sys

def on_activate(app):
    win = Gtk.ApplicationWindow(application=app)
    win.set_default_size(300, 200)
    win.set_title('Environment Test')
    win.present()
    # Close after 1 second
    GLib.timeout_add(1000, app.quit)

app = Gtk.Application(application_id='com.example.GtkTest')
app.connect('activate', on_activate)
sys.exit(app.run(None))
" || echo "Failed to create GTK window"
    else
        echo "Skipping GTK window test in headless mode"
    fi
}

# Process commands
case "$1" in
    test)
        shift
        run_tests "$@"
        ;;
    gtk-test)
        shift
        run_gtk_tests "$@"
        ;;
    diagnostics)
        run_diagnostics
        ;;
    verify)
        verify_environment
        ;;
    *)
        # If command starts with "pytest", run tests
        if [[ "$1" == "pytest"* ]]; then
            run_tests "$@"
        else
            # Otherwise execute the command
            exec "$@"
        fi
        ;;
esac