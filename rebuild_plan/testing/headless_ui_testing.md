# Headless UI Testing for GTK Applications

This document outlines approaches for testing GTK UI components in a headless environment, which is particularly important for CI/CD pipelines and automated testing.

## Challenges with GTK Testing

Testing GTK applications presents several challenges in headless environments:

1. **Display Requirements**: GTK requires a display server (X11 or Wayland)
2. **Initialization Issues**: GTK must be properly initialized before creating UI components
3. **Event Loop**: Some tests may require a running GTK event loop

## Approaches to Headless UI Testing

### 1. Using Xvfb (X Virtual Framebuffer)

Xvfb provides a virtual X11 display server that runs in memory without the need for a physical display.

```bash
# Start Xvfb
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99

# Run tests
pytest tests/ui/
```

In Docker, this can be automated within your test script:

```python
import os
import subprocess
import time

# Start Xvfb if DISPLAY is not set
if os.environ.get('DISPLAY') is None:
    subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1024x768x24'])
    time.sleep(1)  # Give it a moment to start
    os.environ['DISPLAY'] = ':99'

# Now import GTK and run your tests
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
```

### 2. Mock-Based Testing (Preferred Approach)

A more reliable approach is to use mocks for UI components, which doesn't require an X server at all.

```python
# Mock UI component
class MockWindow:
    def __init__(self, title="Test Window"):
        self.title = title
        self.button_clicked = False

    def get_title(self):
        return self.title

    def click_button(self):
        self.button_clicked = True

    def was_button_clicked(self):
        return self.button_clicked

# Test with the mock
def test_button_click():
    window = MockWindow()
    window.click_button()
    assert window.was_button_clicked()
```

### 3. Hybrid Approach

You can use a hybrid approach that tries to use real GTK components but falls back to mocks in a headless environment:

```python
try:
    import gi
    gi.require_version('Gtk', '4.0')
    from gi.repository import Gtk
    HAS_GTK = True
except (ValueError, ImportError, RuntimeError):
    HAS_GTK = False

if HAS_GTK:
    # Real GTK implementation
    class UIWindow:
        # ... actual GTK implementation ...
else:
    # Mock implementation
    class UIWindow:
        # ... mock implementation ...

# Tests use UIWindow regardless of which implementation is active
def test_window():
    window = UIWindow()
    # ... test implementation ...
```

## Docker Configuration for UI Testing

In Docker, there are two main approaches:

### 1. Mount the X11 Socket (for interactive testing)

```yaml
services:
  gtk-test:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    image: preview-maker:dev
    volumes:
      - ../..:/app
      - /tmp/.X11-unix:/tmp/.X11-unix  # Mount X11 socket
      - ~/.Xauthority:/home/developer/.Xauthority:ro  # X11 auth
    environment:
      - DISPLAY=${DISPLAY:-:0}  # X11 display
    network_mode: host  # Simplifies X11 forwarding
```

### 2. Use Xvfb in CI/CD Pipelines

```yaml
# GitHub Actions example
- name: Run UI tests
  run: |
    Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
    export DISPLAY=:99
    docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/ui/
```

## Demo: Headless UI Testing in Preview Maker

We've implemented a headless UI testing example in `rebuild_plan/testing/headless_ui_test.py`, which uses the mock-based approach:

1. It defines mock UI components that simulate GTK functionality
2. Tests interact with these mocks just as they would with real GTK components
3. No display server is needed, making it perfect for CI/CD environments

Run the example with:

```bash
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test python rebuild_plan/testing/headless_ui_test.py
```

## Best Practices for Headless UI Testing

1. **Separation of Logic**: Keep UI logic separate from business logic to make testing easier
2. **Interface-Based Design**: Design UI components with clear interfaces that can be mocked
3. **Event-Based Testing**: Test that UI events trigger the correct business logic
4. **Defensive Coding**: Handle GTK initialization failures gracefully
5. **CI/CD Integration**: Include headless UI tests in CI/CD pipelines

## Tools and Libraries

- **Xvfb**: Virtual framebuffer for X11
- **pytest-xvfb**: pytest plugin that handles Xvfb automatically
- **pytest-gtk**: pytest plugin for GTK testing (Note: May not be fully compatible with GTK 4.0)
- **pyvirtualdisplay**: Python wrapper for Xvfb

## Conclusion

Headless UI testing for GTK applications is challenging but achievable using the approaches outlined in this document. For most cases, the mock-based approach offers the best reliability and performance, especially in CI/CD environments.