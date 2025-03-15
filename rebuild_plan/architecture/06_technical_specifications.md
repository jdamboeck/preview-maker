# Technical Specifications

This document provides specific technical specifications and implementation patterns for key components of the Preview Maker rebuild.

## Image Processing Implementation

### Technical Approach

- Use Pillow's ImageDraw module with transparent masks for circular overlays
- Implement a caching layer for processed images using LRU cache with size limits based on memory constraints
- Set standard thumbnail size of 256×256 pixels for previews, with configurable options
- Use Cairo for custom drawing in GTK DrawingArea for complex overlays
- Background thread processing with main thread UI updates through GLib.idle_add

### Sample Implementation Patterns

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Tuple, Optional
from PIL import Image, ImageDraw
from functools import lru_cache

@dataclass
class ImageProcessor:
    config: "ConfigurationManager"
    cache_size: int = 50
    _cache: Dict[str, "ProcessedImage"] = field(default_factory=dict)

    def process_image(self, image_path: Path) -> "ProcessedImage":
        """Process an image to generate highlights based on detected areas."""
        cache_key = str(image_path)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Load and process image
        with Image.open(image_path) as img:
            # Process image logic
            processed = self._process_image_internal(img)

        # Update cache with LRU eviction
        if len(self._cache) >= self.cache_size:
            # Remove oldest item
            self._cache.pop(next(iter(self._cache)))
        self._cache[cache_key] = processed

        return processed

    def _create_circular_highlight(self,
                                  image: Image.Image,
                                  center: Tuple[int, int],
                                  radius: int,
                                  zoom_factor: float = 2.0) -> Image.Image:
        """Create a circular highlight overlay with zoom effect."""
        # Create mask for circular overlay
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((center[0] - radius, center[1] - radius,
                     center[0] + radius, center[1] + radius), fill=255)

        # Create zoomed version of the selected area
        x, y = center
        box = (x - radius/zoom_factor, y - radius/zoom_factor,
              x + radius/zoom_factor, y + radius/zoom_factor)
        zoomed_area = image.crop(box).resize((radius*2, radius*2))

        # Composite the images
        result = image.copy()
        result.paste(zoomed_area, (center[0] - radius, center[1] - radius), mask)

        return result
```

## Gemini AI Integration

### Technical Approach

- Create a dedicated GeminiAIService class with:
  - Configurable API key management
  - Automatic retry logic (exponential backoff)
  - Response caching to reduce API calls
  - Timeouts and fallback mechanisms
- Implement a deterministic fallback analyzer for when AI is unavailable
- Use a specific prompt template with sections for:
  - Image context and purpose
  - Expected output format
  - Analysis criteria
- Parse and validate responses to ensure expected format

### Sample Implementation Pattern

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import time
import google.generativeai as genai
from PIL import Image

@dataclass
class GeminiAIService:
    config: "ConfigurationManager"
    response_cache: Dict[str, Dict] = field(default_factory=dict)
    _model: Optional[any] = None

    def initialize(self) -> bool:
        """Initialize the Gemini AI service."""
        try:
            api_key = self.config.get_ai_api_key()
            if not api_key:
                return False

            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel('gemini-pro-vision')
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini AI: {e}")
            return False

    def analyze_image(self, image_path: Path,
                     context: str = "") -> List[Dict[str, any]]:
        """Analyze an image to find interesting areas."""
        # Check cache first
        cache_key = f"{image_path}:{hash(context)}"
        if cache_key in self.response_cache:
            return self.response_cache[cache_key]

        # Try AI analysis with retries
        result = None
        retry_count = 0
        max_retries = self.config.get_max_retries(default=3)

        while retry_count < max_retries and not result:
            try:
                if not self._model:
                    if not self.initialize():
                        return self._fallback_analysis(image_path)

                # Prepare the image
                img = Image.open(image_path)

                # Prepare the prompt
                prompt = self._build_prompt(context)

                # Call the AI
                response = self._model.generate_content([prompt, img])

                # Parse the response
                result = self._parse_response(response)

                # Cache the result
                self.response_cache[cache_key] = result
                return result
            except Exception as e:
                retry_count += 1
                self.logger.warning(f"AI analysis retry {retry_count}: {e}")
                time.sleep(2 ** retry_count)  # Exponential backoff

        # Fallback if all retries failed
        return self._fallback_analysis(image_path)

    def _build_prompt(self, context: str) -> str:
        """Build the prompt for the AI."""
        base_prompt = """
        Analyze this image and identify the most interesting or notable details that would be worth highlighting.
        For each area of interest, provide:
        1. X and Y coordinates (as percentages of image width/height)
        2. A radius (as percentage of image width) for the circular highlight
        3. A brief description of why this area is interesting

        Format your response as a list of JSON objects:
        [
          {"x": float, "y": float, "radius": float, "description": "text"},
          ...
        ]

        Include between 1 and 5 highlights, focusing on the most visually interesting or important elements.
        """

        if context:
            return f"{base_prompt}\n\nAdditional context: {context}"
        return base_prompt

    def _fallback_analysis(self, image_path: Path) -> List[Dict[str, any]]:
        """Perform fallback analysis when AI is unavailable."""
        # Implementation of deterministic fallback using classic CV techniques
        # Example: Use a simple edge detection + contour analysis approach
        img = Image.open(image_path)
        width, height = img.size

        # Very simple fallback - just highlight the center of the image
        # In a real implementation, use classic CV techniques
        return [
            {
                "x": 0.5,  # Center X (50%)
                "y": 0.5,  # Center Y (50%)
                "radius": 0.1,  # 10% of image width
                "description": "Automatically detected area of interest (fallback mode)"
            }
        ]
```

## UI Component Implementation

### Technical Approach

- Implement UI following GTK 4.0 best practices:
  - Use controllers instead of signal handlers
  - Proper event propagation model
  - Background thread processing with UI updates via GLib.idle_add
- Use DrawingArea with cairo for custom rendering:
  - Double-buffering for smooth performance
  - Custom draw function for overlay rendering
- Implement modern drag and drop using GTK 4.0 APIs:
  - GtkDropTarget for receiving images
  - Proper file type filtering

### Sample Implementation Pattern

```python
from dataclasses import dataclass, field
from typing import Callable, Optional
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GLib
import threading

@dataclass
class ImagePreviewPanel:
    config: "ConfigurationManager"
    processor: "ImageProcessor"
    on_image_selected: Callable[[str], None] = None

    # UI components
    drawing_area: Optional[Gtk.DrawingArea] = None
    container: Optional[Gtk.Box] = None

    def initialize(self) -> Gtk.Widget:
        """Initialize the image preview panel."""
        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Setup drawing area
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(500, 400)
        self.drawing_area.set_draw_func(self._draw_cb)

        # Add drop target for drag and drop
        drop_target = Gtk.DropTarget.new(Gdk.FileList, Gdk.DragAction.COPY)
        drop_target.connect("drop", self._on_drop)
        self.drawing_area.add_controller(drop_target)

        # Add click gesture for selection
        click_gesture = Gtk.GestureClick.new()
        click_gesture.connect("pressed", self._on_click)
        self.drawing_area.add_controller(click_gesture)

        # Pack widgets
        self.container.append(self.drawing_area)

        return self.container

    def load_image(self, file_path: str) -> None:
        """Load an image in a background thread."""
        def run_processing():
            try:
                # Process the image
                result = self.processor.process_image(file_path)

                # Update UI in main thread
                GLib.idle_add(self._on_image_processed, result)
            except Exception as e:
                GLib.idle_add(self._on_error, str(e))

        # Start background thread
        thread = threading.Thread(target=run_processing)
        thread.daemon = True
        thread.start()

    def _draw_cb(self, area, cr, width, height):
        """Draw callback for the drawing area."""
        # Clear background
        cr.set_source_rgb(0.95, 0.95, 0.95)
        cr.paint()

        # Draw image if available
        if hasattr(self, 'current_image'):
            # Implementation of drawing logic
            pass

    def _on_drop(self, drop_target, value, x, y):
        """Handle drop events for files."""
        if isinstance(value, Gdk.FileList):
            files = value.get_files()
            if files:
                # Take first file only
                file_path = files[0].get_path()
                supported_types = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
                if any(file_path.lower().endswith(ext) for ext in supported_types):
                    self.load_image(file_path)
                    return True
        return False
```

## Event-Based Communication Pattern

### Technical Approach

- Implement a lightweight event system for component communication
- Use a publisher-subscriber pattern for loose coupling
- Allow multiple subscribers to listen to events

### Sample Implementation Pattern

```python
from dataclasses import dataclass, field
from typing import Callable, List, TypeVar, Generic, Any

T = TypeVar('T')

class EventEmitter(Generic[T]):
    """Event emitter for type-safe events."""

    def __init__(self):
        self._handlers: List[Callable[[T], None]] = []

    def connect(self, handler: Callable[[T], None]) -> None:
        """Connect a handler to this event."""
        self._handlers.append(handler)

    def disconnect(self, handler: Callable[[T], None]) -> None:
        """Disconnect a handler from this event."""
        if handler in self._handlers:
            self._handlers.remove(handler)

    def emit(self, event_data: T) -> None:
        """Emit an event to all connected handlers."""
        for handler in self._handlers:
            handler(event_data)


@dataclass
class ImageAnalyzer:
    ai_service: "GeminiAIService"
    on_analysis_complete: EventEmitter["AnalysisResult"] = field(default_factory=EventEmitter)
    on_analysis_started: EventEmitter[str] = field(default_factory=EventEmitter)
    on_analysis_error: EventEmitter[str] = field(default_factory=EventEmitter)

    def analyze_image(self, image_path: str) -> None:
        """Analyze an image and emit events for results."""
        self.on_analysis_started.emit(image_path)

        try:
            # Perform analysis
            result = self.ai_service.analyze_image(image_path)

            # Emit the result event
            analysis_result = AnalysisResult(image_path, result)
            self.on_analysis_complete.emit(analysis_result)
        except Exception as e:
            self.on_analysis_error.emit(str(e))


# Example usage in a UI component:
@dataclass
class AnalysisPanel:
    analyzer: ImageAnalyzer

    def initialize(self) -> None:
        """Initialize the panel and connect to events."""
        self.analyzer.on_analysis_started.connect(self._show_loading)
        self.analyzer.on_analysis_complete.connect(self._show_results)
        self.analyzer.on_analysis_error.connect(self._show_error)

    def _show_loading(self, image_path: str) -> None:
        """Show loading indicator when analysis starts."""
        # Implementation...

    def _show_results(self, result: "AnalysisResult") -> None:
        """Show results when analysis completes."""
        # Implementation...

    def _show_error(self, error_message: str) -> None:
        """Show error when analysis fails."""
        # Implementation...
```

## Success Metrics and Validation

### Performance Metrics

- **Image Loading**:
  - Target: < 200ms for images up to 12MP
  - Measurement: Timing logs for load operations

- **UI Responsiveness**:
  - Target: Frame rate > 30fps during processing
  - Measurement: GTK frame counter during operations

- **Memory Usage**:
  - Target: < 250MB during normal operation
  - Measurement: Memory profiling during typical workflows

### Quality Metrics

- **Stability**:
  - Target: Zero crashes in 24 hours of normal operation
  - Measurement: Extended testing with automated workflows

- **Test Coverage**:
  - Target: > 80% code coverage for core modules
  - Measurement: Pytest coverage reports

- **Processing Success Rate**:
  - Target: > 90% success for highlight generation on suitable images
  - Measurement: Automated test suite with diverse image set

These technical specifications provide concrete guidance for implementing the Preview Maker rebuild, including specific patterns, approaches, and metrics for success.