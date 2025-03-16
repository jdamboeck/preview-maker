# UI Testing

This document details the approach to UI testing for the rebuilt Preview Maker application, with a focus on Docker-based testing.

## UI Testing Approach

UI tests verify that the user interface works correctly. They focus on the visual elements, user interactions, and the integration of UI components with the underlying application logic.

### Key UI Testing Areas

1. **Component Rendering**: Verify that UI components render correctly
2. **User Interactions**: Verify that user interactions (clicks, drags, etc.) work correctly
3. **Data Display**: Verify that data is displayed correctly in the UI
4. **Error Handling**: Verify that UI handles errors gracefully

## Testing Approaches

The Preview Maker project supports three approaches for UI testing:

1. **Mock-based Testing**: Uses mock implementations of GTK components for unit testing
2. **X11 Forwarding**: Uses the host's X11 server for interactive testing
3. **Xwayland Testing**: Uses a self-contained Xwayland environment for CI/CD pipelines

### When to Use Each Approach

| Approach | When to Use | Pros | Cons |
|----------|-------------|------|------|
| Mock-based | Unit testing UI components, CI/CD pipelines | Fast, no display needed, simple | Limited testing of actual UI rendering |
| X11 Forwarding | Local development, integration testing | Easier debugging, actual UI rendering | Requires X11 on host, potential permission issues |
| Xwayland | CI/CD pipelines, consistent environments | Self-contained, reliable, no host dependencies | Larger container size, more complex setup |

### Example Test Files

- **Mock-based**: `tests/ui/test_manual_overlay_manager.py`
- **Xwayland**: `tests/ui/test_xwayland.py` and `tests/ui/test_xwayland_overlay.py`

## Docker-Based UI Testing

### Mock-based Testing

Run mock-based UI tests using the standard test service:

```bash
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/ui/ --headless -v
```

### X11 Forwarding Testing

For interactive testing with UI components:

```bash
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm gtk-test
```

### Xwayland Testing

For self-contained UI testing:

```bash
./rebuild_plan/docker/run_gtk_tests.sh --test tests/ui/test_xwayland.py
```

Or run all UI tests:

```bash
./rebuild_plan/docker/run_all_ui_tests.sh
```

## Test Organization

UI tests are organized into several categories:

1. **Component Tests**: Test individual UI components (e.g., `test_manual_overlay_manager.py`)
2. **Integration Tests**: Test interactions between components (e.g., `test_xwayland_overlay.py`)
3. **Workflow Tests**: Test end-to-end workflows (e.g., image loading, overlay creation, saving)

## Best Practices

1. **Use the GTKTestBase class**: For Xwayland testing, extend the `GTKTestBase` class to handle X11 setup
2. **Use fixtures**: Create fixtures for common UI components to reduce code duplication
3. **Test both happy and error paths**: Ensure UI components handle errors gracefully
4. **Clean up resources**: Always destroy GTK windows and terminate Xvfb processes
5. **Use descriptive test names**: Test names should describe what they're testing

## CI/CD Integration

UI tests are integrated into CI/CD pipelines using GitHub Actions. See `rebuild_plan/ci_cd_examples/.github/workflows/ui-tests.yml` for an example workflow.

## Further Reading

- [Xwayland Testing Guide](xwayland_testing.md): Detailed guide for Xwayland testing
- [UI Testing Guide](ui_testing_guide.md): Comprehensive guide for all UI testing approaches
- [Headless UI Testing](headless_ui_testing.md): Guide for headless UI testing with mocks