# Cursor Setup for Preview Maker Development

This guide provides comprehensive setup instructions for using Cursor IDE to develop the Preview Maker application with GTK and Python.

## Prerequisites Installation

### 1. System Dependencies

#### Ubuntu/Debian:
```bash
# Install GTK 4.0 development packages
sudo apt update
sudo apt install -y python3-dev python3-venv python3-pip
sudo apt install -y libgtk-4-dev libcairo2-dev libgirepository1.0-dev
sudo apt install -y gir1.2-gtk-4.0 python3-cairo-dev
```

#### Arch Linux:
```bash
sudo pacman -S python python-pip
sudo pacman -S gtk4 gobject-introspection cairo
sudo pacman -S python-gobject python-cairo
```

#### macOS:
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install GTK 4.0 and dependencies
brew install gtk4 gobject-introspection pygobject3 cairo
brew install python3
```

### 2. Python Environment Setup

```bash
# Create and activate a virtual environment
cd /path/to/preview-maker
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required Python packages
pip install -r requirements.txt
```

Create a `requirements.txt` file with these dependencies:

```
# GTK and Cairo bindings
PyGObject>=3.42.0
pycairo>=1.20.0

# Image processing
Pillow>=9.0.0

# Gemini AI integration
google-generativeai>=0.3.0

# Configuration management
toml>=0.10.2

# Development and testing
pytest>=7.0.0
pytest-cov>=3.0.0
flake8>=4.0.0
mypy>=0.950
black>=22.3.0

# Utilities
psutil>=5.9.0
```

## Cursor IDE Setup

### 1. Install Cursor

Download and install Cursor IDE from [https://cursor.sh/](https://cursor.sh/) if you haven't already.

### 2. Project Configuration

Create a `.vscode/settings.json` file in your project root with these settings:

```json
{
  "python.analysis.typeCheckingMode": "basic",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "88"],
  "editor.formatOnSave": true,
  "editor.rulers": [88],
  "editor.tabSize": 4,
  "editor.insertSpaces": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/*.pyc": true,
    "venv": true,
    ".coverage": true
  },
  "python.analysis.extraPaths": ["${workspaceFolder}"],
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.nosetestsEnabled": false,
  "python.testing.pytestArgs": ["tests"]
}
```

### 3. Copy .cursorrules to Project Root

The `.cursorrules` file should be placed in your project root to guide AI development. You can find the existing file in `rebuild_plan/.cursorrules`.

### 4. Launch Configuration

Create a `.vscode/launch.json` file for debugging:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Preview Maker",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/app/main.py",
      "console": "integratedTerminal",
      "justMyCode": false,
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    },
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "justMyCode": false,
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    },
    {
      "name": "Run Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["tests/"],
      "justMyCode": false,
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  ]
}
```

## Project Structure Initialization

Set up the following directory structure:

```
preview-maker/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── components/
│   │   ├── __init__.py
│   │   ├── image_processor.py
│   │   ├── ai_service.py
│   │   └── ui/
│   │       ├── __init__.py
│   │       ├── app_window.py
│   │       ├── image_view.py
│   │       └── highlight_overlay.py
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── exceptions.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_image_processor.py
│   ├── test_ai_service.py
│   └── test_ui/
│       ├── __init__.py
│       └── test_app_window.py
├── resources/
│   ├── test_images/
│   └── ui/
│       └── app.ui
├── .vscode/
│   ├── settings.json
│   └── launch.json
├── .cursorrules
├── requirements.txt
├── setup.py
├── README.md
└── rebuild_plan/
    └── ... (existing rebuild plan files)
```

## GTK 4.0 Development Environment Verification

Create a basic test script at `app/test_gtk.py`:

```python
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib

class TestWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(600, 400)
        self.set_title("GTK 4.0 Test")

        # Create box for content
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        self.set_child(box)

        # Add a label
        label = Gtk.Label(label="GTK 4.0 is working!")
        label.set_margin_bottom(20)
        box.append(label)

        # Add a button
        button = Gtk.Button(label="Click Me")
        button.connect("clicked", self.on_button_clicked)
        box.append(button)

        # Add an image placeholder
        drawing_area = Gtk.DrawingArea()
        drawing_area.set_size_request(300, 200)
        drawing_area.set_draw_func(self.on_draw)
        box.append(drawing_area)

    def on_button_clicked(self, button):
        print("Button clicked!")

    def on_draw(self, area, cr, width, height):
        # Set background
        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.paint()

        # Draw a circle
        cr.set_source_rgb(0.3, 0.6, 0.8)
        cr.arc(width/2, height/2, min(width, height)/4, 0, 2*3.14159)
        cr.fill()

class TestApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.GtkTest",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        win = TestWindow(application=self)
        win.present()

def main():
    app = TestApp()
    return app.run(None)

if __name__ == "__main__":
    main()
```

Run the test script to verify GTK 4.0 is correctly installed:

```bash
python app/test_gtk.py
```

## Diagnostic Tools Setup

### GTK Inspector

Enable GTK Inspector for debugging:

```bash
# Linux
gsettings set org.gtk.Settings.Debug enable-inspector-keybinding true

# macOS
defaults write org.gtk.gtk-debug enable-inspector-keybinding YES
```

Use Ctrl+Shift+I (or Cmd+Shift+I on macOS) to open the inspector while running a GTK application.

### Cairo Debug

For Cairo drawing issues, create a debugging utility at `app/utils/cairo_debug.py`:

```python
import cairo
import os
from pathlib import Path

def save_surface_to_png(surface, filename):
    """Save a Cairo surface to a PNG file for debugging."""
    debug_dir = Path("debug")
    debug_dir.mkdir(exist_ok=True)
    path = debug_dir / filename
    surface.write_to_png(str(path))
    print(f"Saved debug image to: {path}")
    return path

def debug_draw_function(draw_func):
    """Decorator to debug a drawing function."""
    def wrapper(widget, cr, width, height):
        # Create a surface for debugging
        debug_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        debug_context = cairo.Context(debug_surface)

        # Call the original function with debug context
        result = draw_func(widget, debug_context, width, height)

        # Save the debug output
        save_surface_to_png(debug_surface,
                            f"{draw_func.__name__}_{width}x{height}.png")

        # Also draw to the original context
        result = draw_func(widget, cr, width, height)
        return result
    return wrapper
```

## Automated Debugging Setup

Add a diagnostic utility at `app/utils/diagnostics.py`:

```python
import logging
import time
import psutil
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

@dataclass
class ComponentDiagnostics:
    """Base class for component diagnostics."""
    component_name: str
    status: str  # "healthy", "degraded", "failed"
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert diagnostics to a dictionary."""
        return {
            "component": self.component_name,
            "status": self.status,
            "metrics": self.metrics,
            "errors": self.errors,
            "timestamp": self.timestamp
        }

def diagnose_ui_issues(widget):
    """Diagnose common UI widget issues."""
    results = {
        "widget_type": type(widget).__name__,
        "visible": widget.get_visible() if hasattr(widget, "get_visible") else None,
        "allocated": hasattr(widget, "get_allocated_width") and
                    widget.get_allocated_width() > 0 and
                    widget.get_allocated_height() > 0,
        "parent": widget.get_parent().__class__.__name__
                  if hasattr(widget, "get_parent") and widget.get_parent() else None
    }

    # For drawing areas, check draw function
    if isinstance(widget, Gtk.DrawingArea):
        results["has_draw_func"] = widget.get_draw_func() is not None

    return results

def diagnose_image_issues(image_path: Path):
    """Diagnose image loading and processing issues."""
    from PIL import Image

    results = {
        "exists": image_path.exists(),
        "size_bytes": image_path.stat().st_size if image_path.exists() else 0,
        "errors": []
    }

    if not image_path.exists():
        results["errors"].append(f"File does not exist: {image_path}")
        return results

    try:
        start_time = time.time()
        with Image.open(image_path) as img:
            results["format"] = img.format
            results["mode"] = img.mode
            results["size"] = img.size

            # Check memory impact
            mem_before = psutil.Process().memory_info().rss / (1024 * 1024)
            img_copy = img.copy()  # Test memory allocation
            mem_after = psutil.Process().memory_info().rss / (1024 * 1024)

            results["memory_impact_mb"] = round(mem_after - mem_before, 2)
            results["load_time_ms"] = round((time.time() - start_time) * 1000, 2)

            # Check if image is valid
            img.verify()  # This will raise an exception if image is corrupted
    except Exception as e:
        results["errors"].append(f"Image error: {str(e)}")
        results["traceback"] = traceback.format_exc()

    return results

def add_diagnostic_logging(logger_name: str, level: int = logging.DEBUG) -> Callable:
    """Add diagnostic logging to a logger and return a function to restore level."""
    logger = logging.getLogger(logger_name)
    original_level = logger.level
    logger.setLevel(level)

    def restore_level():
        logger.setLevel(original_level)

    return restore_level
```

## Configuration Template

Create a configuration template at `app/config.toml`:

```toml
[app]
name = "Preview Maker"
version = "1.0.0"
theme = "default"

[performance]
cache_size = 50
image_thumbnail_size = 256
max_memory_mb = 250

[ui]
default_window_width = 1024
default_window_height = 768
zoom_factor = 2.0

[api]
gemini_api_key = ""
max_retries = 3
timeout_seconds = 10
```

## Starter File Creation

Create a basic main.py file to start from:

```python
#!/usr/bin/env python3
import gi
import sys
import logging
from pathlib import Path

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("preview-maker")

def main():
    logger.info("Starting Preview Maker")

    # TODO: Implement the application

    # Placeholder application to verify GTK setup
    app = Gtk.Application(application_id="dev.preview.maker",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
    app.connect("activate", on_activate)
    return app.run(sys.argv)

def on_activate(app):
    win = Gtk.ApplicationWindow(application=app)
    win.set_default_size(1024, 768)
    win.set_title("Preview Maker")

    # Create a simple label
    label = Gtk.Label(label="Preview Maker - Development Setup Complete!")
    win.set_child(label)

    win.present()

if __name__ == "__main__":
    sys.exit(main())
```

## Testing GTK Applications

Create a pytest fixture for testing GTK applications in `tests/conftest.py`:

```python
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
import pytest
import threading
import time

@pytest.fixture
def gtk_app():
    """Fixture for testing GTK applications."""
    app = Gtk.Application(application_id="dev.preview.maker.test")

    # Start the main loop in a separate thread
    def run_app():
        app.run([])

    thread = threading.Thread(target=run_app)
    thread.daemon = True
    thread.start()

    # Wait for app to initialize
    time.sleep(0.1)

    yield app

    # Clean up
    app.quit()
    thread.join(timeout=1.0)

@pytest.fixture
def test_image_path():
    """Fixture that returns a path to a test image."""
    from pathlib import Path
    test_dir = Path(__file__).parent / "data"
    test_dir.mkdir(exist_ok=True)

    # Create a test image if it doesn't exist
    test_image = test_dir / "test_image.png"
    if not test_image.exists():
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (300, 200), color='white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([20, 20, 280, 180], outline='black')
        draw.ellipse([50, 50, 150, 150], fill='blue')
        img.save(test_image)

    return test_image
```

## Docker Development Environment (Optional)

Create a `Dockerfile` for a consistent development environment:

```dockerfile
FROM ubuntu:22.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    libgtk-4-dev \
    libcairo2-dev \
    libgirepository1.0-dev \
    gir1.2-gtk-4.0 \
    python3-cairo-dev \
    git \
    nano \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up a non-root user
RUN useradd -ms /bin/bash developer
USER developer
WORKDIR /home/developer

# Set up Python environment
RUN python3 -m venv /home/developer/venv
ENV PATH="/home/developer/venv/bin:$PATH"

# Copy requirements and install dependencies
COPY --chown=developer:developer requirements.txt /home/developer/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Create project structure
RUN mkdir -p /home/developer/preview-maker/app/components/ui \
    /home/developer/preview-maker/app/utils \
    /home/developer/preview-maker/tests \
    /home/developer/preview-maker/resources

WORKDIR /home/developer/preview-maker

# Set up X11 forwarding for GUI apps
ENV DISPLAY=:0

CMD ["/bin/bash"]
```

Create a `docker-compose.yml` file for easier management:

```yaml
version: '3'

services:
  preview-maker-dev:
    build: .
    volumes:
      - .:/home/developer/preview-maker
      - /tmp/.X11-unix:/tmp/.X11-unix
    environment:
      - DISPLAY=${DISPLAY}
    working_dir: /home/developer/preview-maker
    command: bash
```

## Quick Start Guide

Add these instructions to your project's README.md:

```markdown
## Quick Start for Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/preview-maker.git
   cd preview-maker
   ```

2. **Set up development environment**
   ```bash
   # Create and activate a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Test GTK installation**
   ```bash
   python app/test_gtk.py
   ```

4. **Open in Cursor IDE**
   - Launch Cursor
   - File > Open Folder > select the preview-maker directory
   - Cursor will load the project settings and .cursorrules

5. **Run the application**
   - Press F5 or select Run > Start Debugging
   - Select the "Preview Maker" configuration
```

## Autonomous Debugging Setup

Create a diagnostic utility script at `app/utils/debug_tool.py`:

```python
#!/usr/bin/env python3
"""
Autonomous debugging tool for Preview Maker.

This tool performs component health checks and diagnostics.
"""
import sys
import logging
import argparse
from pathlib import Path
import json
import importlib
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("debug-tool")

def diagnose_component(component_name):
    """Run diagnostics on a specific component."""
    try:
        # Dynamically import component diagnostics
        module_path = f"app.components.{component_name}"
        if component_name.startswith("ui."):
            module_path = f"app.components.{component_name}"

        module = importlib.import_module(module_path)

        # Look for a diagnostic function or class method
        if hasattr(module, "run_diagnostics"):
            diagnostics = module.run_diagnostics()
            return {
                "status": "success",
                "component": component_name,
                "diagnostics": diagnostics
            }
        else:
            return {
                "status": "error",
                "component": component_name,
                "error": "No diagnostic function found"
            }
    except Exception as e:
        return {
            "status": "error",
            "component": component_name,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

def diagnose_all_components():
    """Run diagnostics on all components."""
    components = [
        "image_processor",
        "ai_service",
        "ui.app_window",
        "ui.image_view",
        "ui.highlight_overlay"
    ]

    results = {}
    for component in components:
        results[component] = diagnose_component(component)

    return results

def diagnose_system():
    """Run system-level diagnostics."""
    import psutil

    return {
        "memory": {
            "available": psutil.virtual_memory().available / (1024 * 1024),
            "percent": psutil.virtual_memory().percent
        },
        "cpu": {
            "percent": psutil.cpu_percent(interval=1)
        },
        "disk": {
            "free": psutil.disk_usage('/').free / (1024 * 1024 * 1024),
            "percent": psutil.disk_usage('/').percent
        },
        "python": {
            "version": sys.version
        }
    }

def main():
    parser = argparse.ArgumentParser(description="Preview Maker Diagnostic Tool")
    parser.add_argument("--component", help="Diagnose a specific component")
    parser.add_argument("--all", action="store_true", help="Diagnose all components")
    parser.add_argument("--system", action="store_true", help="Show system diagnostics")
    parser.add_argument("--output", help="Output file for diagnostic results")

    args = parser.parse_args()

    results = {
        "timestamp": __import__("time").time(),
    }

    if args.all:
        results["components"] = diagnose_all_components()
    elif args.component:
        results["components"] = {
            args.component: diagnose_component(args.component)
        }

    if args.system or not (args.all or args.component):
        results["system"] = diagnose_system()

    # Print results
    print(json.dumps(results, indent=2))

    # Save to file if specified
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Diagnostic results saved to {output_path}")

if __name__ == "__main__":
    main()
```

This comprehensive setup provides everything needed to develop the Preview Maker application using Cursor IDE with Python and GTK 4.0, following the technical specifications defined in the rebuild plan.