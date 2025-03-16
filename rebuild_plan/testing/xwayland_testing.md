# Xwayland Testing for Preview Maker

This document summarizes the findings and recommendations for testing GTK applications in Xwayland environments.

## Overview

The Preview Maker application uses GTK 4 for its user interface. Testing GTK applications in containerized environments can be challenging, especially when dealing with display servers. This document outlines our approach to testing GTK applications in Xwayland environments.

## Testing Approaches

We have implemented two main approaches for testing GTK applications:

1. **Headless Testing with Mocks**: This approach uses mock implementations of GTK components to test the application logic without requiring a display server. This is useful for CI/CD environments where a display server may not be available.

2. **Xwayland Testing**: This approach uses Xwayland to provide a display server for testing GTK applications in a containerized environment. This allows for more comprehensive testing of the UI components.

## Xwayland Testing Setup

The Xwayland testing setup consists of the following components:

1. **Docker Container**: A Docker container with GTK 4 and Xvfb installed.
2. **Xvfb**: A virtual framebuffer X server that allows running X applications without a display.
3. **Test Runner**: A script that sets up the environment and runs the tests.

## Implementation Details

### Docker Container

The Docker container is defined in `rebuild_plan/docker/Dockerfile.gtk-test`. It includes:

- Ubuntu 22.04 as the base image
- GTK 4 and related dependencies
- Python 3 and required packages (pytest, pillow, google-generativeai)
- Xvfb for headless testing

### Test Runner

The test runner script is defined in `rebuild_plan/docker/run_gtk_tests.sh`. It:

1. Builds the Docker image
2. Starts Xvfb in the container
3. Runs the specified tests

### Test Files

We have created several test files to verify GTK functionality in Xwayland environments:

1. **test_xwayland.py**: A simple test that verifies basic GTK functionality.
2. **test_xwayland_overlay.py**: A more comprehensive test that verifies overlay functionality.

## Key Findings

1. **GTK 4 API Changes**: GTK 4 has significant API changes compared to GTK 3. For example, `events_pending` and `main_iteration_do` methods are no longer available. Instead, use `GLib.MainLoop` for event processing.

2. **Display Environment**: The `DISPLAY` environment variable must be set correctly for GTK applications to work. In our setup, we use `:99` for Xvfb.

3. **Backend Selection**: Setting `GDK_BACKEND=x11` explicitly helps ensure compatibility with Xvfb.

4. **Initialization**: GTK 4 doesn't require explicit initialization with `Gtk.init()`.

5. **Window Management**: In GTK 4, windows should be created using `Gtk.ApplicationWindow` with an associated `Gtk.Application`.

6. **Event Processing**: Use `GLib.MainLoop` and `GLib.timeout_add` for event processing instead of the older `Gtk.events_pending` and `Gtk.main_iteration_do` methods.

## Recommendations for Future Development

1. **Use Mock-Based Testing for CI/CD**: For continuous integration and deployment, use mock-based testing to avoid display server dependencies.

2. **Use Xwayland Testing for UI Components**: For comprehensive testing of UI components, use Xwayland testing with Xvfb.

3. **Keep Tests Simple**: Keep tests focused on specific functionality to make them more maintainable.

4. **Handle GTK Version Differences**: Be aware of API differences between GTK versions and use conditional code if necessary.

5. **Use Fixtures**: Use pytest fixtures to set up and tear down test environments.

6. **Separate UI Logic from Business Logic**: Design the application to separate UI logic from business logic to make testing easier.

## Example: Running GTK Tests

To run GTK tests, use the following command:

```bash
./rebuild_plan/docker/run_gtk_tests.sh --test tests/ui/test_xwayland.py
```

This will build the Docker image, start Xvfb, and run the specified test.

## Troubleshooting

If you encounter issues with GTK tests, check the following:

1. **Display Environment**: Make sure the `DISPLAY` environment variable is set correctly.
2. **X11 Socket**: Make sure the X11 socket is accessible to the container.
3. **GTK Version**: Make sure the GTK version in the container matches the version expected by the application.
4. **Dependencies**: Make sure all required dependencies are installed in the container.

## Conclusion

Xwayland testing provides a robust approach to testing GTK applications in containerized environments. By following the recommendations in this document, you can ensure that your GTK applications are thoroughly tested and work correctly in various environments.