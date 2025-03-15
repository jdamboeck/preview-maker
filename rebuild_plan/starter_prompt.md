# Preview Maker Rebuild Project - AI Assistant Initialization

Preview Maker is a GTK application that analyzes images using Google's Gemini Vision API to identify interesting details and create zoomed-in circular overlays of those areas. This project involves rebuilding from a monolithic to a component-based architecture.

## Core Functionality

1. **Image Loading & Processing** - Load and process images using Pillow, with caching for performance
2. **Gemini AI Integration** - Detect interesting areas with fallback mechanisms
3. **Highlight Overlay Generation** - Create circular zoomed overlays on detected areas
4. **GTK 4.0 Modern UI** - Implement drag-and-drop interface with proper controllers

## Technical Requirements

- **Python 3.8+** with **Pillow** for image processing
- **GTK 4.0** via PyGObject for UI
- **Google Generative AI** library for Gemini Vision API
- **TOML** for configuration management
- **Event-based architecture** with dependency injection
- **Background thread processing** with GLib.idle_add for UI updates

## Docker Development Environment

This project uses Docker to ensure a consistent development and testing environment:

```bash
# Build the Docker environment
docker-compose -f rebuild_plan/docker/docker-compose.yml build

# Verify the environment
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm verify

# Start a development shell
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker dev

# Run tests
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test
```

For UI testing in headless environments, use mock-based testing approach:

```bash
# Run UI tests with mocked components
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/ui/
```

## Technical Specifications

- **Image Processing**: Use transparent masks with Pillow's ImageDraw
- **Performance Targets**:
  - Image loading < 200ms for images up to 12MP
  - UI responsiveness > 30fps during processing
  - Memory usage < 250MB for normal operation
- **Error Handling**: Implement retry logic with exponential backoff for API calls
- **Component Communication**: Event emitter pattern for loose coupling

## Key Development Resources

- Technical Implementation: `architecture/06_technical_specifications.md`
- Component Dependencies: `00_prerequisites/08_component_dependency_diagram.md`
- AI Integration Guide: `00_prerequisites/05_gemini_ai_integration.md`
- GTK 4.0 Migration Guide: `00_prerequisites/04_gtk_development_guide.md`
- Implementation Roadmap: `implementation_roadmap.md`
- Docker Integration: `docker_integration_plan.md`
- Headless UI Testing: `testing/headless_ui_testing.md`

## Implementation Patterns

The rebuild uses these key implementation patterns:

1. **Background Processing**:
```python
def process_in_background(file_path):
    thread = threading.Thread(target=process_file, args=(file_path,))
    thread.daemon = True
    thread.start()

def process_file(file_path):
    # Process image
    result = process_image(file_path)
    # Update UI in main thread
    GLib.idle_add(update_ui, result)
```

2. **Event-Based Communication**:
```python
# Component emits events that others can subscribe to
image_processor.on_processing_complete.connect(ui_component.update_display)
```

3. **GTK 4.0 Controllers** (not signal handlers):
```python
# Modern event handling with controllers
click_gesture = Gtk.GestureClick.new()
click_gesture.connect("pressed", self._on_click)
widget.add_controller(click_gesture)
```

4. **AI Integration with Fallbacks**:
```python
try:
    # Try AI analysis
    result = gemini_service.analyze_image(image_path)
except Exception:
    # Use fallback analysis when AI unavailable
    result = fallback_analyzer.analyze_image(image_path)
```

5. **Docker-Based Testing**:
```bash
# Run tests in Docker
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/
```

## Autonomous Debugging Cycle

When debugging issues, follow this self-guided cyclic pattern with minimal human intervention:

1. **Problem Identification**
   - Analyze error messages, logs, and unexpected behaviors
   - Categorize issue type: API integration, UI rendering, image processing, threading, etc.
   - Document the exact conditions that trigger the issue
   - **Docker Verification**: Run `docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm verify` to check environment

2. **Hypothesis Generation**
   - Formulate 2-3 likely causes based on available information
   - Rank hypotheses by probability using this pattern:
     ```python
     def rank_hypotheses(error_info):
         hypotheses = [
             {"description": "Possible cause 1", "probability": 0.7, "test": "test_function_1()"},
             {"description": "Possible cause 2", "probability": 0.3, "test": "test_function_2()"}
         ]
         return sorted(hypotheses, key=lambda h: h["probability"], reverse=True)
     ```

3. **Investigation**
   - Examine relevant code, starting with highest probability hypothesis
   - Add targeted logging to gather more information:
     ```python
     def add_diagnostic_logging(module_name):
         logger = logging.getLogger(module_name)
         # Set to DEBUG level temporarily
         original_level = logger.level
         logger.setLevel(logging.DEBUG)
         return original_level  # Return to restore later
     ```
   - **Docker Diagnostics**: Run `docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm diagnostics` for comprehensive diagnostics

4. **Fix Implementation**
   - Implement the fix for the most likely cause
   - Add unit test to verify fix and prevent regression
   - **Docker Testing**: Run tests in isolation with `docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/path/to/test.py`

5. **Verification**
   - Run unit tests to confirm fix works
   - Check for unintended side effects in related components
   - Verify against original requirements and performance metrics
   - **Docker Component Test**: Test specific components with `docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/component/`

6. **Decision Node**
   - If fix resolves issue ✓ → Document and proceed to next task
   - If fix partially resolves issue ↻ → Return to Investigation with new information
   - If fix fails completely ↻ → Test next hypothesis
   - Only if all hypotheses exhausted → Request human intervention

7. **Documentation**
   - Document the issue, investigation process, and solution
   - Update relevant unit tests
   - Commit the changes with clear explanation
   - **Update Documentation**: Ensure Docker usage is documented if relevant to the fix
   - **Follow Documentation Guidelines**: Update all affected documentation as specified in the Documentation Update Guidelines section of `.cursorrules`
   - Update any architecture diagrams or component interfaces that were modified
   - Include docstring updates for any changed functions
   - Ensure README files reflect the current state after changes

## Investigation Tools

Use these techniques for autonomous investigation:

```python
# 1. Diagnose GTK rendering issues
def diagnose_ui_issues(widget):
    # Check widget hierarchy
    print(f"Widget type: {type(widget).__name__}")
    print(f"Parent: {widget.get_parent()}")
    print(f"Visible: {widget.get_visible()}")
    print(f"Size request: {widget.get_size_request()}")
    # For GTK 4.0 drawing issues
    if isinstance(widget, Gtk.DrawingArea):
        print(f"Draw function set: {widget.get_draw_func() is not None}")

# 2. Diagnose image processing issues
def diagnose_image_issues(image_path):
    try:
        with Image.open(image_path) as img:
            print(f"Format: {img.format}")
            print(f"Size: {img.size}")
            print(f"Mode: {img.mode}")
            # Test memory usage
            mem_before = psutil.Process().memory_info().rss / 1024 / 1024
            img_copy = img.copy()
            mem_after = psutil.Process().memory_info().rss / 1024 / 1024
            print(f"Memory impact: {mem_after - mem_before:.2f} MB")
    except Exception as e:
        print(f"Image error: {e}")

# 3. Diagnose API issues
def diagnose_api_issues(service):
    # Check API key configuration
    api_key = service.config.get_ai_api_key()
    print(f"API key configured: {bool(api_key)}")

    # Test connection with minimal request
    try:
        response = service.test_connection()
        print(f"Connection test: {'Success' if response else 'Failed'}")
    except Exception as e:
        print(f"API connection error: {e}")

# 4. Docker Environment Diagnostics
def run_docker_diagnostics():
    """Run comprehensive diagnostics in Docker."""
    import subprocess
    result = subprocess.run(
        ["docker-compose", "-f", "rebuild_plan/docker/docker-compose.yml", "run", "--rm", "diagnostics"],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"Diagnostics failed: {result.stderr}")
    return result.returncode == 0
```

## Docker-Based Testing Approaches

1. **Unit Testing**: Isolated component testing
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/unit/
   ```

2. **Integration Testing**: Component interaction testing
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/integration/
   ```

3. **UI Testing**: Mock-based UI testing for headless environments
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/ui/
   ```

4. **Performance Testing**: Performance metric verification
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/performance/
   ```

## When to Seek Human Intervention

Only request human input when:

1. All reasonable hypotheses have been investigated and ruled out
2. The issue appears to be environment-specific (user's system configuration)
3. The problem requires access to resources outside the codebase (API keys, hardware)
4. The fix would require significant architectural changes
5. Docker environment issues persist after exhausting diagnostic tools

In all other cases, proceed with the debugging cycle autonomously.

## Current Task
[DESCRIBE YOUR SPECIFIC TASK HERE]

Please provide implementation guidance or code that follows these patterns and technical specifications.