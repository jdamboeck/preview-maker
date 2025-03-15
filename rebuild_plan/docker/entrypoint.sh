#!/bin/bash
set -e

# Set up environment
export PYTHONPATH="/app:${PYTHONPATH}"

# Helper functions
function run_tests() {
    echo "Running tests with pytest..."
    cd /app
    python -m pytest $@
}

function run_xvfb() {
    echo "Setting up Xvfb display server..."

    # Check if Xvfb is already running and kill it
    if pgrep -x "Xvfb" > /dev/null; then
        echo "Existing Xvfb process found, stopping it..."
        pkill -x Xvfb || true
        sleep 1
    fi

    # Make sure the display is free
    rm -f /tmp/.X0-lock || true

    # Start Xvfb with more options for better compatibility
    Xvfb :0 -screen 0 1280x1024x24 -ac +extension GLX +render -noreset &
    export DISPLAY=:0
    echo "Waiting for Xvfb to start..."
    sleep 2

    # Verify display is working
    echo "Testing X11 connection..."
    xdpyinfo -display :0 >/dev/null 2>&1 || echo "WARNING: X11 display setup failed"
}

function run_gtk_test() {
    echo "Running GTK overlay test..."
    cd /app

    # Set GDK backend explicitly
    export GDK_BACKEND=x11

    # Initialize GTK before running the application
    python -c "import gi; gi.require_version('Gtk', '4.0'); from gi.repository import Gtk; Gtk.init()"

    python rebuild_plan/gtk_overlay_test.py
}

function run_diagnostics() {
    echo "Running diagnostic checks..."
    cd /app

    # Check GTK installation
    python -c "import gi; gi.require_version('Gtk', '4.0'); from gi.repository import Gtk; print('GTK 4.0 is available')"

    # Check Pillow installation
    python -c "from PIL import Image, ImageDraw; print('Pillow is available')"

    # Check Cairo installation
    python -c "import cairo; print('Cairo is available')"

    # Check system resources
    echo "System Resources:"
    free -h
    df -h

    # Print Python environment
    echo "Python Environment:"
    pip list

    # Run more comprehensive diagnostics if docker_diagnostics.py exists
    if [ -f /app/rebuild_plan/docker/docker_diagnostics.py ]; then
        echo ""
        echo "Running comprehensive diagnostics..."
        python /app/rebuild_plan/docker/docker_diagnostics.py
    fi
}

function run_verification() {
    echo "Running environment verification..."
    cd /app

    if [ -f /app/rebuild_plan/docker/verify_environment.py ]; then
        python /app/rebuild_plan/docker/verify_environment.py
    else
        echo "Verification script not found at /app/rebuild_plan/docker/verify_environment.py"
        exit 1
    fi
}

# If no command is provided, show the help message
if [ $# -eq 0 ]; then
    echo "Preview Maker Docker Environment"
    echo "================================"
    echo "Available commands:"
    echo "  bash                - Start a bash shell"
    echo "  test [args]         - Run pytest with optional arguments"
    echo "  gtk-test            - Run the GTK overlay test"
    echo "  diag                - Run diagnostic checks"
    echo "  verify              - Run environment verification"
    echo "  dev                 - Start development environment with Xvfb"
    echo "  help                - Show this help message"
    echo ""
    echo "Example: docker-compose run --rm preview-maker test -v"
    exit 0
fi

# Process the command
case "$1" in
    test)
        shift
        run_xvfb
        run_tests $@
        ;;
    gtk-test)
        run_xvfb
        run_gtk_test
        ;;
    diag)
        run_diagnostics
        ;;
    verify)
        run_verification
        ;;
    dev)
        run_xvfb
        exec bash
        ;;
    help)
        exec $0
        ;;
    *)
        # Execute the provided command
        exec "$@"
        ;;
esac