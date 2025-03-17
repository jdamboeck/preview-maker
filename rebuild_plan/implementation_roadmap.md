# Preview Maker Implementation Roadmap

This technical roadmap outlines the implementation sequence for the Preview Maker rebuild, focusing on the core functionality and technical requirements.

## Implementation Timeline

| Phase             | Target Date       | Components                                                        | Status      |
| ----------------- | ----------------- | ----------------------------------------------------------------- | ----------- |
| Foundation Layer  | March 15, 2025    | Configuration Manager, Logging System, Event Communication System | Completed   |
| Image Processing  | March 15, 2025    | Image Processor, Image Cache, Circular Overlay Generation         | Completed   |
| AI Integration    | March 15-16, 2025 | Gemini API Client, Image Analyzer, Response Parser                | In Progress |
| GTK UI Framework  | March 16-30, 2025 | Application Window, Image Viewer, Overlay Management              | In Progress |
| Integration Layer | April 1-20, 2025  | Component Integration, Event-based Communication                  | Not Started |
| Diagnostic System | April 21-30, 2025 | Performance Monitoring, Error Detection                           | Not Started |
| Final Release     | June 15, 2025     | Final Testing, Documentation, Release                             | Not Started |

## Core Components and Implementation Order

### 1. Foundation Layer

```python
# Configuration System Example
class ConfigurationManager:
    def __init__(self, config_path: Path = None):
        self.config_path = config_path or Path("~/.config/preview-maker/config.toml").expanduser()
        self.config = self._load_config()

    def get_ai_api_key(self) -> Optional[str]:
        return self.config.get("ai", {}).get("api_key")

    def get_max_retries(self, default: int = 3) -> int:
        return self.config.get("network", {}).get("max_retries", default)
```

**Implementation Priorities:**

- Configuration system with TOML support
- Error handling with custom exception types
- Logging infrastructure with context tracking

**Success Criteria:**

- Configuration loads in < 50ms
- Test coverage > 80%

### 2. Image Processing Engine

```python
# Image Processor Example
def process_image(image_path: Path) -> ProcessedImage:
    # Load image
    with Image.open(image_path) as img:
        # Process image
        return ProcessedImage(
            original=img.copy(),
            thumbnail=create_thumbnail(img),
            format=img.format,
            size=img.size
        )
```

**Implementation Priorities:**

- Efficient image loading with validation
- Caching layer for processed images
- Thumbnail generation
- Memory management for large images

**Success Criteria:**

- Load images < 200ms for 12MP images
- Memory usage < 100MB during processing

### 3. Gemini AI Service

```python
# Gemini AI Service Example
def analyze_image(image_path: Path, context: str = "") -> List[Dict]:
    # Check cache first
    if result := check_cache(image_path, context):
        return result

    # Call Gemini API with retries
    for attempt in range(MAX_RETRIES):
        try:
            response = gemini_client.generate_content([prompt, Image.open(image_path)])
            result = parse_response(response)
            add_to_cache(image_path, context, result)
            return result
        except Exception as e:
            log_error(f"API call failed: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff

    # Fallback to offline analysis
    return fallback_analysis(image_path)
```

**Implementation Priorities:**

- API integration with error handling
- Response caching and validation
- Fallback mechanism using basic CV techniques
- Prompt engineering for optimal results

**Success Criteria:**

- Success rate > 90% for suitable images
- Graceful degradation when API unavailable

### 4. GTK UI Framework

```python
# UI Framework Example
def initialize_ui():
    # Main window setup
    window = Gtk.ApplicationWindow()

    # Controllers (not signal handlers)
    drop_target = Gtk.DropTarget.new(Gdk.FileList, Gdk.DragAction.COPY)
    drop_target.connect("drop", on_drop)

    # Background processing
    def on_drop(target, value, x, y):
        # Get first file
        file_path = value.get_files()[0].get_path()
        # Process in background
        threading.Thread(target=process_file, args=(file_path,)).start()
```

**Implementation Priorities:**

- Modern GTK 4.0 widget architecture
- Event controllers instead of signal handlers
- Background thread processing
- GTK-specific drawing for overlays

**Success Criteria:**

- UI maintains > 30fps during operations
- Drag-and-drop works with single images and folders

### 5. Integration Layer

```python
# Component Integration Example
class PreviewMakerApp:
    def __init__(self):
        self.config = ConfigurationManager()
        self.image_processor = ImageProcessor(self.config)
        self.ai_service = GeminiAIService(self.config)

        # Connect components via events
        self.image_processor.on_image_loaded.connect(self.ai_service.analyze_image)
        self.ai_service.on_analysis_complete.connect(self.ui.display_results)
```

**Implementation Priorities:**

- Event-based communication between components
- Proper dependency injection
- Feature integration with error propagation
- User feedback mechanisms

**Success Criteria:**

- Complete functionality with < 1s response time
- Zero crashes in extended testing

### 6. Diagnostic & Monitoring System

```python
# Diagnostic System Example
class DiagnosticSystem:
    def __init__(self, app: PreviewMakerApp):
        self.app = app
        self.logs = []

    def diagnose_component(self, component_name: str) -> Dict[str, Any]:
        """Run diagnostic checks on a specific component."""
        if component_name == "image_processor":
            return self._diagnose_image_processor()
        elif component_name == "ai_service":
            return self._diagnose_ai_service()
        elif component_name == "ui":
            return self._diagnose_ui()
        else:
            return {"error": f"Unknown component: {component_name}"}

    def _diagnose_image_processor(self) -> Dict[str, Any]:
        """Run diagnostics on the image processor component."""
        processor = self.app.image_processor
        results = {
            "cache_size": len(processor._cache),
            "cache_hit_ratio": processor.cache_hits / (processor.cache_hits + processor.cache_misses) if (processor.cache_hits + processor.cache_misses) > 0 else 0,
            "avg_processing_time_ms": processor.total_processing_time / processor.processed_count if processor.processed_count > 0 else 0,
            "memory_usage_mb": self._get_memory_usage()
        }
        return results

    def _get_memory_usage(self) -> float:
        """Get current memory usage of the process."""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)  # Convert to MB
```

**Implementation Priorities:**

- Component-specific diagnostic tools
- Performance monitoring
- Memory usage tracking
- Automated error detection

**Success Criteria:**

- Can identify >90% of common issues
- Provides actionable diagnostics data
- Minimal performance impact when enabled

## Automated Testing & Debugging

```python
# Automated test example with debugging capability
def test_process_large_image_with_diagnostics():
    # Setup
    test_file = get_test_image("large_12mp.jpg")
    processor = ImageProcessor(MockConfig())
    diagnostic = DiagnosticSystem(MockApp(processor=processor))

    # Enable detailed logging
    import logging
    original_level = logging.getLogger("preview_maker").level
    logging.getLogger("preview_maker").setLevel(logging.DEBUG)

    try:
        # Act
        start_time = time.time()
        result = processor.process_image(test_file)
        duration = time.time() - start_time

        # Get diagnostics
        diag_results = diagnostic.diagnose_component("image_processor")

        # Assert with diagnostic info
        assert result is not None, f"Failed to process image. Diagnostics: {diag_results}"
        assert duration < 0.2, f"Processing took {duration:.3f}s (>200ms). Diagnostics: {diag_results}"
        assert diag_results["memory_usage_mb"] < 250, f"Memory usage too high: {diag_results['memory_usage_mb']:.2f}MB"
    finally:
        # Restore logging level
        logging.getLogger("preview_maker").setLevel(original_level)
```

- Unit tests with built-in diagnostics
- Automated test cases for component interfaces
- End-to-end validation with monitoring enabled
- Performance regression detection

## Technical Dependencies

| Component       | Depends On                     | Notes                       |
| --------------- | ------------------------------ | --------------------------- |
| Configuration   | None                           | Foundation component        |
| Image Processor | Configuration                  | Needs config for cache size |
| AI Service      | Configuration, Image Processor | Needs processed images      |
| UI Components   | Configuration                  | For user preferences        |
| Integration     | All components                 | Final integration step      |
| Diagnostics     | All components                 | Monitors all components     |

## Performance Requirements

- Image loading: < 200ms for 12MP images
- UI responsiveness: > 30fps during processing
- Memory usage: < 250MB peak
- API response handling: < 500ms

## Code Standards

- Type hints throughout codebase
- Dataclasses for component interfaces
- Exception handling with specific types
- Background processing with main thread UI updates
- Self-diagnosing components with debugging hooks

## Autonomous Debugging Infrastructure

Each component should implement a diagnostic interface for automated debugging:

```python
@dataclass
class ComponentDiagnostics:
    """Base class for component diagnostics."""
    component_name: str
    status: str  # "healthy", "degraded", "failed"
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert diagnostics to a dictionary."""
        return {
            "component": self.component_name,
            "status": self.status,
            "metrics": self.metrics,
            "errors": self.errors,
            "timestamp": time.time()
        }

# Example implementation for the ImageProcessor
def get_diagnostics(self) -> ComponentDiagnostics:
    """Return diagnostic information about this component."""
    status = "healthy"
    errors = []

    # Check cache health
    if len(self._cache) >= self.cache_size * 0.9:
        status = "degraded"
        errors.append("Cache nearly full")

    # Check processing performance
    if self.avg_processing_time > 0.2:  # More than 200ms avg
        status = "degraded"
        errors.append(f"Slow image processing: {self.avg_processing_time*1000:.1f}ms avg")

    return ComponentDiagnostics(
        component_name="image_processor",
        status=status,
        metrics={
            "cache_size": len(self._cache),
            "cache_capacity": self.cache_size,
            "cache_hit_ratio": self.cache_hit_ratio,
            "avg_processing_time_ms": self.avg_processing_time * 1000,
            "images_processed": self.processed_count
        },
        errors=errors
    )
```

This roadmap provides the technical implementation details for rebuilding Preview Maker with a component-based architecture, focusing on the core functionality and technical requirements.