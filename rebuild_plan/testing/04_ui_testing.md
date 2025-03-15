# UI Testing

This document details the approach to UI testing for the rebuilt Preview Maker application, with a focus on Docker-based testing.

## UI Testing Approach

UI tests verify that the user interface works correctly. They focus on the visual elements, user interactions, and the integration of UI components with the underlying application logic.

### Key UI Testing Areas

1. **Component Rendering**: Verify that UI components render correctly
2. **User Interactions**: Verify that user interactions (clicks, drags, etc.) work correctly
3. **Data Display**: Verify that data is displayed correctly in the UI
4. **Error Handling**: Verify that UI handles errors gracefully

## Docker-Based UI Testing

UI tests are run in the Docker gtk-test container, which provides X11 forwarding for GUI testing:

```bash
# Run all UI tests
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm gtk-test pytest tests/ui/

# Run specific UI tests
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm gtk-test pytest tests/ui/test_main_window.py
```

### Headless UI Testing

For CI/CD pipelines, UI tests can be run in headless mode using Xvfb:

```bash
# Run headless UI tests
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/ui/ --headless
```

## UI Test Structure

UI tests should follow this structure:

1. **Setup**: Create and configure the UI components being tested
2. **Interaction**: Perform user interactions with the UI
3. **Verification**: Verify that the UI responds correctly

Example:

```python
def test_main_window_displays_image():
    """Test that the main window can display an image."""
    # Setup
    window = MainWindow()
    test_image_path = "test_data/test_image.jpg"

    # Interaction
    window.load_image(test_image_path)

    # Verification
    assert window.get_image() is not None
    assert window.get_image_size() == (400, 300)
```

## GTK-Specific Testing

For GTK-specific testing, use the GTK test utilities:

```python
def test_gtk_button_click():
    """Test that a GTK button click works correctly."""
    # Setup
    window = MainWindow()
    button = window.get_button("load_image")

    # Interaction
    button.clicked()

    # Verification
    assert window.get_file_chooser().is_visible()
```

## Event-Based UI Testing

For event-based UI testing, use the GTK event system:

```python
def test_drag_and_drop():
    """Test that drag and drop works correctly."""
    # Setup
    window = MainWindow()
    drop_target = window.get_drop_target()

    # Create a mock file list
    file_list = Gdk.FileList()
    file_list.append(Gio.File.new_for_path("test_data/test_image.jpg"))

    # Simulate a drop event
    drop_target.emit("drop", file_list, 100, 100)

    # Verification
    assert window.get_image() is not None
```

## UI Component Mocking

For UI component mocking, create mock UI components:

```python
class MockFileChooser:
    """Mock file chooser for testing."""

    def __init__(self):
        self.visible = False
        self.selected_file = None

    def show(self):
        """Show the file chooser."""
        self.visible = True

    def hide(self):
        """Hide the file chooser."""
        self.visible = False

    def is_visible(self):
        """Return whether the file chooser is visible."""
        return self.visible

    def select_file(self, file_path):
        """Select a file."""
        self.selected_file = file_path

    def get_selected_file(self):
        """Return the selected file."""
        return self.selected_file

def test_file_chooser():
    """Test that the file chooser works correctly."""
    # Setup
    window = MainWindow()
    window.file_chooser = MockFileChooser()

    # Interaction
    window.show_file_chooser()
    window.file_chooser.select_file("test_data/test_image.jpg")
    window.load_selected_file()

    # Verification
    assert window.get_image() is not None
```

## UI Test Data

Use shared test data for UI tests:

```python
@pytest.fixture
def test_image():
    """Return a test image for UI testing."""
    img = Image.new("RGB", (400, 300), color="white")
    draw = ImageDraw.Draw(img)
    draw.rectangle((50, 50, 150, 150), fill="blue")
    return img

def test_display_image(test_image):
    """Test that an image can be displayed."""
    # Setup
    window = MainWindow()

    # Interaction
    window.display_image(test_image)

    # Verification
    assert window.get_image() is not None
    assert window.get_image_size() == (400, 300)
```

## UI Test Coverage

UI tests should cover all key UI components and interactions:

- **Main Window**: Test that the main window displays correctly
- **Image Display**: Test that images are displayed correctly
- **Highlight Overlay**: Test that highlight overlays are displayed correctly
- **User Interactions**: Test that user interactions work correctly

## CI/CD Integration

Include UI tests in CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run UI tests
  run: |
    Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
    export DISPLAY=:99
    docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm gtk-test pytest tests/ui/
```