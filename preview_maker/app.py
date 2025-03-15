"""Main application entry point for Preview Maker.

This module initializes and runs the Preview Maker application,
setting up the GTK application structure and logging system.
"""

import sys
import argparse
import logging
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib  # noqa: E402

from preview_maker.core.logging import setup_logging, logger
from preview_maker.ui.app_window import ApplicationWindow


class PreviewMakerApp(Gtk.Application):
    """Main application class for Preview Maker.

    This class handles application lifecycle, including initialization,
    activation, and shutdown.

    Attributes:
        window: The main application window
    """

    def __init__(self) -> None:
        """Initialize the application."""
        super().__init__(
            application_id="com.github.jdamboeck.preview-maker",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self.window = None
        self.register(None)

        logger.info("Application initialized")

    def do_activate(self) -> None:
        """Handle application activation.

        This method is called when the application is activated for the
        first time, or when it's re-activated after being hidden.
        """
        # Create window if it doesn't exist
        if not self.window:
            self.window = ApplicationWindow(self)

        # Show the window and bring it to the front
        self.window.present()
        logger.info("Application activated")

    def do_shutdown(self) -> None:
        """Handle application shutdown."""
        logger.info("Application shutting down")
        super().do_shutdown()


def parse_arguments():
    """Parse command line arguments.

    Returns:
        The parsed arguments object
    """
    parser = argparse.ArgumentParser(
        description="Preview Maker - Image preview generator"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--headless", action="store_true", help="Run in headless mode (for testing)"
    )
    parser.add_argument(
        "--image", type=str, help="Image file to process in headless mode"
    )
    parser.add_argument("--output", type=str, help="Output file path in headless mode")
    parser.add_argument("--api-key", type=str, help="Google Gemini API key")

    return parser.parse_args()


def run_headless(args):
    """Run the application in headless mode.

    Args:
        args: The parsed command line arguments

    Returns:
        0 on success, non-zero on failure
    """
    from preview_maker.ai.integration import AIPreviewGenerator

    logger.info("Running in headless mode")

    # Check required arguments
    if not args.image:
        logger.error("--image argument is required in headless mode")
        return 1

    if not args.output:
        logger.error("--output argument is required in headless mode")
        return 1

    if not args.api_key:
        logger.error("--api-key argument is required in headless mode")
        return 1

    # Create preview generator
    preview_generator = AIPreviewGenerator(api_key=args.api_key)

    # Process image
    try:
        logger.info(f"Processing image: {args.image}")
        image_path = Path(args.image)
        output_path = Path(args.output)

        # Generate preview
        preview = preview_generator.generate_preview(image_path)

        if preview:
            # Save result
            preview.save(output_path)
            logger.info(f"Preview saved to: {output_path}")
            return 0
        else:
            logger.error("Failed to generate preview")
            return 1

    except Exception as e:
        logger.exception(f"Error in headless mode: {e}")
        return 1


def main():
    """Main entry point for the application."""
    # Parse command line arguments
    args = parse_arguments()

    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(level=log_level)

    # Run in headless mode if specified
    if args.headless:
        return run_headless(args)

    # Run GUI application
    app = PreviewMakerApp()
    exit_status = app.run(sys.argv)
    logger.info(f"Application exited with status {exit_status}")
    return exit_status


if __name__ == "__main__":
    sys.exit(main())
