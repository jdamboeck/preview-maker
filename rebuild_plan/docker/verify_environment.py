#!/usr/bin/env python3
"""
Docker Environment Verification Script for Preview Maker

This script verifies that all necessary components for Preview Maker
are available in the Docker environment.
"""
import sys
import os
import importlib
import platform
from pathlib import Path
import tempfile


def print_header(text):
    """Print a header with the given text."""
    print("\n" + "=" * 80)
    print(f" {text}")
    print("=" * 80)


def print_result(name, status, message=""):
    """Print a result with the given name, status, and message."""
    status_str = "✓ PASS" if status else "✗ FAIL"
    print(f"{status_str.ljust(8)} | {name.ljust(20)} | {message}")


def check_module(module_name, import_statement=None):
    """Check if a module is available."""
    try:
        if import_statement:
            exec(import_statement)
        else:
            importlib.import_module(module_name)
        return True, ""
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error: {str(e)}"


def check_gtk():
    """Check if GTK 4.0 is available."""
    try:
        import gi

        gi.require_version("Gtk", "4.0")
        from gi.repository import Gtk

        return True, f"GTK version: {Gtk._version}"
    except ImportError as e:
        return False, f"ImportError: {str(e)}"
    except ValueError as e:
        return False, f"ValueError: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def check_cairo():
    """Check if Cairo is available."""
    try:
        import cairo

        return True, f"Cairo version: {cairo.version}"
    except ImportError as e:
        return False, f"ImportError: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def check_pillow():
    """Check if Pillow is available."""
    try:
        from PIL import Image

        return True, f"Pillow version: {Image.__version__}"
    except ImportError as e:
        return False, f"ImportError: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def check_gemini_ai():
    """Check if Google Generative AI is available."""
    try:
        import google.generativeai as genai

        return True, "Google Generative AI is available"
    except ImportError as e:
        return False, f"ImportError: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def check_image_processing():
    """Check if image processing with Pillow works."""
    try:
        from PIL import Image, ImageDraw

        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test.png"

            # Create a test image
            img = Image.new("RGB", (100, 100), color="white")
            draw = ImageDraw.Draw(img)
            draw.rectangle((10, 10, 90, 90), fill="blue")
            img.save(test_file)

            # Verify the image was created
            if not test_file.exists():
                return False, "Failed to create test image"

            # Try to open and process the image
            img = Image.open(test_file)
            img = img.resize((50, 50))

            return True, "Image processing with Pillow works"
    except Exception as e:
        return False, f"Error: {str(e)}"


def check_cairo_drawing():
    """Check if Cairo drawing works."""
    try:
        import cairo

        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test.png"

            # Create a Cairo surface
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
            ctx = cairo.Context(surface)

            # Draw something
            ctx.set_source_rgb(1, 1, 1)
            ctx.paint()
            ctx.set_source_rgb(0, 0, 1)
            ctx.rectangle(10, 10, 80, 80)
            ctx.fill()

            # Save to file
            surface.write_to_png(str(test_file))

            # Verify the image was created
            if not test_file.exists():
                return False, "Failed to create test image with Cairo"

            return True, "Cairo drawing works"
    except Exception as e:
        return False, f"Error: {str(e)}"


def check_docker():
    """Check if running in Docker."""
    in_docker = os.path.exists("/.dockerenv") or os.path.exists("/run/.containerenv")

    if not in_docker:
        # Check cgroup
        try:
            with open("/proc/1/cgroup", "r") as f:
                in_docker = "docker" in f.read()
        except Exception:
            pass

    return in_docker, "Running in Docker" if in_docker else "Not running in Docker"


def check_display():
    """Check if DISPLAY is set."""
    display = os.environ.get("DISPLAY")
    if not display:
        return False, "DISPLAY environment variable is not set"

    try:
        import subprocess

        subprocess.check_output(["xdpyinfo"], stderr=subprocess.STDOUT, text=True)
        return True, f"X11 display is available: {display}"
    except Exception:
        # X11 forwarding might not work in all environments, so this is not critical
        return (
            True,
            f"DISPLAY is set to {display}, but X11 connection failed (not critical)",
        )


def main():
    """Run all checks and print results."""
    print_header("Preview Maker Docker Environment Verification")

    # System information
    print(f"Python version: {platform.python_version()}")
    print(f"Platform: {platform.platform()}")
    print(f"User: {os.getenv('USER', 'unknown')}")
    print(f"Working directory: {os.getcwd()}")

    # Run checks
    checks = [
        ("GTK 4.0", check_gtk()),
        ("Cairo", check_cairo()),
        ("Pillow", check_pillow()),
        ("Google Generative AI", check_gemini_ai()),
        ("Image Processing", check_image_processing()),
        ("Cairo Drawing", check_cairo_drawing()),
        ("Docker Environment", check_docker()),
        ("X11 Display", check_display()),
    ]

    print_header("Component Checks")

    all_passed = True
    for name, (status, message) in checks:
        print_result(name, status, message)
        if not status and name != "X11 Display":  # X11 Display is not critical
            all_passed = False

    # Print summary
    print_header("Summary")
    if all_passed:
        print(
            "All checks passed! The Docker environment is ready for Preview Maker development."
        )
    else:
        print("Some checks failed. Please review the results and fix any issues.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
