# GTK UI Testing Guide

This guide provides comprehensive information about the various approaches available for testing GTK UI components in the Preview Maker project.

## Testing Approaches

The project supports three approaches for UI testing:

1. **Mock-based Testing**: Fast, lightweight tests using mock GTK components
2. **X11 Forwarding**: Testing with real GTK components using host X11 server
3. **Xwayland Testing**: Self-contained testing with a complete Xwayland environment

### When to Use Each Approach

| Approach | When to Use | Pros | Cons |
|----------|-------------|------|------|
| Mock-based | Unit testing UI components, CI/CD pipelines | Fast, no display needed, simple | Limited testing of actual UI rendering |
| X11 Forwarding | Local development, integration testing | Easier debugging, actual UI rendering | Requires X11 on host, potential permission issues |
| Xwayland | CI/CD pipelines, consistent environments | Self-contained, reliable, no host dependencies | Larger container size, more complex setup |

## Common Testing Patterns

### 1. Test Component Initialization

```python
def test_initialization(self, component):
    """Test that the component initializes correctly."""
    assert isinstance(component, Gtk.Widget)
    # Check properties
    assert component.property_name == expected_value
```

### 2. Test Signal Handling

```python
def test_signal_handling(self, component, monkeypatch):
    """Test that signals are handled correctly."""
    # Mock signal handler
    mock_handler = mock.MagicMock()
    monkeypatch.setattr(component, "_on_signal", mock_handler)
    
    # Emit signal
    component.emit("signal-name")
    
    # Check handler was called
    mock_handler.assert_called_once()
```

### 3. Test UI Integration

```python
def test_ui_integration(self, window, component):
    """Test integration with other UI components."""
    # Add component to window
    window.set_child(component)
    
    # Trigger UI updates
    component.update_ui()
    
    # Process events
    while Gtk.events_pending():
        Gtk.main_iteration_do(False)
    
    # Check UI state
    assert component.is_updated
```

## Running UI Tests

### Mock-based Tests

```bash
# Run all UI tests with mocks
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/ui/ --headless

# Run specific UI test file
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/ui/test_specific_component.py --headless
```

### X11 Forwarding Tests

```bash
# Run all UI tests with X11 forwarding (displays actual windows)
./rebuild_plan/docker/run_gtk_tests.sh

# Run specific UI test with X11 forwarding
./rebuild_plan/docker/run_gtk_tests.sh --test tests/ui/test_specific_component.py

# Run in headless mode with Xvfb
./rebuild_plan/docker/run_gtk_tests.sh --headless
```

### Xwayland Tests

```bash
# Run all UI tests with Xwayland
./rebuild_plan/docker/run_xwayland_tests.sh

# Run specific UI test with Xwayland
./rebuild_plan/docker/run_xwayland_tests.sh --test tests/ui/test_specific_component.py

# Run in headless mode
./rebuild_plan/docker/run_xwayland_tests.sh --headless
```

## Debugging Common GTK Testing Issues

### 1. GTK Initialization Failures

**Symptoms:**
- `Gtk.init()` fails
- "Display cannot be opened" errors
- AttributeError: 'NoneType' has no attribute 'X'

**Solutions:**
- Check `DISPLAY` environment variable is set correctly
- Ensure X11 socket is correctly mounted in Docker
- Verify `.Xauthority` permissions
- Use the Xwayland approach for more reliable initialization

```bash
# Verify X11 environment
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm xwayland-verify
```

### 2. Mock Implementation Issues

**Symptoms:**
- Tests pass but application fails
- Unexpected behavior in real GTK environment

**Solutions:**
- Enhance mock implementations to better match real GTK behavior
- Test critical components with both mocks and real GTK
- Use integration tests to verify component interactions

### 3. Event Processing Issues

**Symptoms:**
- UI doesn't update during tests
- Signals not processed

**Solutions:**
- Add explicit event processing in tests:
  ```python
  # Process events
  while Gtk.events_pending():
      Gtk.main_iteration_do(False)
  ```
- Add small time delays if necessary: `time.sleep(0.1)`

### 4. X11 Permission Issues

**Symptoms:**
- "Cannot open display" errors
- X11 connection rejected

**Solutions:**
- Set correct permissions: `xhost +local:docker`
- Check volume mounts for X11 socket
- Try the Xwayland approach which is self-contained

## Writing Testable GTK Components

1. **Separate UI and Logic**: Keep business logic separate from UI rendering
2. **Use Dependency Injection**: Pass dependencies to components rather than creating them internally
3. **Implement Observable Properties**: Make UI state observable for testing
4. **Write Interface Contracts**: Define clear interfaces that mocks can implement
5. **Provide Testing Hooks**: Add methods that facilitate testing

## CI/CD Integration

An example GitHub Actions workflow is provided in `rebuild_plan/ci_cd_examples/.github/workflows/ui-tests.yml` that demonstrates how to run both headless mock-based tests and Xwayland tests in CI pipelines.

Key points for CI/CD integration:
- Always use headless mode in CI/CD
- Run both mock-based and Xwayland tests for comprehensive coverage
- Test performance-critical components with Xwayland
- Use the smallest sufficient testing approach for non-critical components

## Extending the Testing Framework

To add support for testing a new GTK component:

1. **Create Mock Implementation**: Add a mock class to `tests/ui/mocks.py`
2. **Write Test Cases**: Create a test file in `tests/ui/`
3. **Handle Both Environments**: Support both real GTK and mock components
4. **Add New Test Patterns**: Document any new testing patterns

Example of adding a new mock:

```python
# In tests/ui/mocks.py
class MockNewComponent(MockGtk.Widget):
    """Mock implementation of NewComponent."""
    
    def __init__(self, param1, param2):
        self.param1 = param1
        self.param2 = param2
        self.signals = {}
    
    def do_action(self):
        """Mock implementation of do_action."""
        return "mocked result"
        
    def connect(self, signal, handler):
        """Handle signal connections."""
        self.signals[signal] = handler
        return 1
        
    def emit(self, signal, *args):
        """Emit a signal."""
        if signal in self.signals:
            return self.signals[signal](self, *args)
```

## References

- [GTK 4.0 Documentation](https://docs.gtk.org/gtk4/)
- [PyGObject Testing](https://pygobject.readthedocs.io/en/latest/testing.html)
- [pytest Documentation](https://docs.pytest.org/)
- [Xvfb Documentation](https://www.x.org/releases/X11R7.6/doc/man/man1/Xvfb.1.xhtml)
- [Xwayland Documentation](https://wayland.freedesktop.org/xserver.html)