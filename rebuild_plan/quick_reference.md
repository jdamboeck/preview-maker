# Preview Maker Quick Reference Guide

This document provides quick reference for common operations when working with the Preview Maker project.

## Environment Commands

### Docker Environment

| Action | Command |
|--------|---------|
| Build Docker environment | `docker-compose -f rebuild_plan/docker/docker-compose.yml build` |
| Verify environment | `docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm verify` |
| Start development shell | `docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker dev` |
| Run the application | `docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker run` |
| Run GTK overlay test | `docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm gtk-test` |
| Run diagnostics | `docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm diagnostics` |
| Clean up environment | `docker-compose -f rebuild_plan/docker/docker-compose.yml down` |

### Testing

| Action | Command |
|--------|---------|
| Run all tests | `docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test` |
| Run unit tests | `docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/unit/` |
| Run integration tests | `docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/integration/` |
| Run UI tests | `docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/ui/ --headless` |
| Run with X11 | `docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm gtk-test pytest tests/ui/` |
| Generate coverage | `docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest --cov=preview_maker --cov-report=html` |

## Code Structure Reference

### Core Components

| Component | Purpose | Key Files |
|-----------|---------|-----------|
| Configuration | Manage app settings | `core/config.py` |
| Image Processor | Process images | `image/processor.py` |
| AI Integration | Gemini API client | `ai/gemini_client.py` |
| UI Components | GTK user interface | `ui/main_window.py` |
| Event System | Component communication | `core/events.py` |

### Common Imports

```python
# GTK imports
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GLib

# Image processing
from PIL import Image, ImageDraw, ImageFilter

# Gemini AI
import google.generativeai as genai

# Project imports
from preview_maker.core.config import Config
from preview_maker.image.processor import ImageProcessor
from preview_maker.ai.gemini_client import GeminiClient
```

## UI Component Guidelines

### GTK Controllers (not Signal Handlers)

```python
# Add a click controller to a button
button = Gtk.Button(label="Click Me")
click_controller = Gtk.GestureClick.new()
click_controller.connect("pressed", self._on_button_pressed)
button.add_controller(click_controller)

# Add drag-and-drop support
drop_controller = Gtk.DropTarget.new(Gdk.ContentFormats.new_for_gtype(Gdk.FileList), Gdk.DragAction.COPY)
drop_controller.connect("drop", self._on_drop)
widget.add_controller(drop_controller)
```

### Threading and UI Updates

```python
def process_image_async(self, file_path):
    # Start background thread
    thread = threading.Thread(target=self._process_image_thread, args=(file_path,))
    thread.daemon = True
    thread.start()

def _process_image_thread(self, file_path):
    # Process in background
    result = self.image_processor.process(file_path)

    # Update UI in main thread
    GLib.idle_add(self._update_ui_with_result, result)
```

## Image Processing Reference

### Creating Circular Masks

```python
def create_circular_mask(image, center, radius):
    """Create a circular mask for highlighting."""
    # Create blank mask image
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)

    # Draw white circle on black background
    draw.ellipse((
        center[0] - radius, center[1] - radius,
        center[0] + radius, center[1] + radius
    ), fill=255)

    return mask
```

### Applying Zoom Effect

```python
def create_zoomed_overlay(image, center, radius, zoom_factor=2.0):
    """Create a zoomed circular overlay."""
    # Calculate crop box
    crop_radius = radius / zoom_factor
    crop_box = (
        center[0] - crop_radius, center[1] - crop_radius,
        center[0] + crop_radius, center[1] + crop_radius
    )

    # Crop, resize, and create circular mask
    zoomed = image.crop(crop_box).resize((radius * 2, radius * 2))
    mask = create_circular_mask(image, center, radius)

    # Create result image and paste zoomed portion
    result = image.copy()
    result.paste(zoomed, (center[0] - radius, center[1] - radius), mask)

    return result
```

## Gemini AI Integration

### Basic API Call

```python
def analyze_image(image_path):
    """Analyze image with Gemini Vision API."""
    # Initialize Gemini
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-pro-vision')

    # Load image
    with open(image_path, 'rb') as f:
        image_data = f.read()

    # Create prompt
    prompt = """
    Analyze this image and identify the most interesting or distinctive detail.
    Return a JSON object with:
    1. A description of the detail
    2. The approximate x,y coordinates (as percentages of width/height)
    3. A suggested zoom level (1.5-4.0)
    """

    # Generate response
    response = model.generate_content([prompt, image_data])

    return response.text
```

## Common Testing Patterns

### Basic Component Test

```python
def test_image_processor():
    """Test the image processor component."""
    # Arrange
    processor = ImageProcessor()
    test_image = "tests/data/sample.jpg"

    # Act
    result = processor.process(test_image)

    # Assert
    assert result is not None
    assert result.size == (800, 600)  # Expected dimensions
```

### Mock-Based Testing

```python
def test_ui_with_mocks(mocker):
    """Test UI component with mocks."""
    # Mock dependencies
    mock_processor = mocker.Mock()
    mock_processor.process.return_value = "processed_result"

    # Create component with mock
    ui = UIComponent(image_processor=mock_processor)

    # Act
    ui.process_button_clicked()

    # Assert
    mock_processor.process.assert_called_once()
    # Additional assertions...
```

## Documentation Guidelines

### Docstring Format (Google Style)

```python
def create_overlay(image_path, center, radius, zoom_factor=2.0):
    """Create a circular zoom overlay on the image.

    Args:
        image_path (str): Path to the source image
        center (tuple): (x, y) coordinates of the center point
        radius (int): Radius of the circular overlay
        zoom_factor (float, optional): Amount of zoom. Defaults to
            2.0.

    Returns:
        PIL.Image: The image with overlay applied

    Raises:
        FileNotFoundError: If the image path is invalid
        ValueError: If parameters are out of valid ranges

    Example:
        >>> result = create_overlay("image.jpg", (400, 300), 100)
        >>> result.save("result.jpg")
    """
```

## Debugging Tips

1. Use `print()` statements strategically
2. Run with diagnostic flags: `preview-maker dev --debug`
3. Check log files in Docker container
4. Use pytest's `-v` flag for verbose output
5. Run tests with specific markers: `pytest -m "not slow"`
6. Run failing tests with `--pdb` to drop into debugger

## Key Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `GEMINI_API_KEY` | Google Gemini API authentication | `export GEMINI_API_KEY=your_key_here` |
| `DISPLAY` | X11 display server | `export DISPLAY=:0` |
| `PYTHONPATH` | Python module search path | `export PYTHONPATH=/app` |
| `DEBUG` | Enable debug logging | `export DEBUG=1` |