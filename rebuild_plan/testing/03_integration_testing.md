# Integration Testing

This document details the approach to integration testing for the rebuilt Preview Maker application, with a focus on Docker-based testing.

## Integration Testing Approach

Integration tests verify that components work together correctly. They focus on the interactions between components rather than the internal implementation details of individual components.

### Key Integration Points

1. **Image Processing → Gemini AI Service**: Verify that processed images can be analyzed by the AI service
2. **Gemini AI Service → UI**: Verify that analysis results can be displayed in the UI
3. **Configuration → Components**: Verify that components are correctly configured

## Docker-Based Integration Testing

All integration tests are run in the Docker test container to ensure a consistent environment:

```bash
# Run all integration tests
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/integration/

# Run specific integration tests
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/integration/test_image_ai_integration.py
```

## Integration Test Structure

Integration tests should follow this structure:

1. **Setup**: Create and configure the components being tested
2. **Integration**: Connect the components and perform the integration action
3. **Verification**: Verify that the integration works as expected

Example:

```python
def test_image_processor_ai_service_integration():
    """Test that the image processor and AI service work together."""
    # Setup
    config = ConfigurationManager()
    image_processor = ImageProcessor(config)
    ai_service = GeminiAIService(config)

    # Integration
    test_image_path = "test_data/test_image.jpg"
    processed_image = image_processor.process_image(test_image_path)
    analysis_result = ai_service.analyze_image(processed_image)

    # Verification
    assert analysis_result is not None
    assert len(analysis_result) > 0
    assert "description" in analysis_result[0]
```

## Component Mocking in Integration Tests

In integration tests, only mock external dependencies that are not part of the integration being tested:

```python
def test_ai_service_ui_integration(mocker):
    """Test that the AI service and UI work together."""
    # Mock the Gemini API client
    mock_client = mocker.Mock()
    mock_client.generate_content.return_value = {
        "result": [
            {"x": 0.5, "y": 0.5, "radius": 0.1, "description": "Test highlight"}
        ]
    }

    # Setup
    config = ConfigurationManager()
    ai_service = GeminiAIService(config)
    ai_service._model = mock_client
    ui = UIManager(config)

    # Integration
    analysis_result = ai_service.analyze_image("test_image.jpg")
    ui.display_results(analysis_result)

    # Verification
    assert ui.get_highlight_count() == 1
    assert ui.get_highlight_description(0) == "Test highlight"
```

## Docker Environment Variables

Use Docker environment variables to configure integration tests:

```python
def test_docker_integration():
    """Test that components can access Docker environment variables."""
    # Verify environment variables
    assert os.environ.get("PREVIEW_MAKER_ENV") == "test"
    assert "/app" in os.environ.get("PYTHONPATH", "")

    # Create components
    config = ConfigurationManager()

    # Verify configuration
    assert config.get_environment() == "test"
```

## Integration Test Data

Use shared test data for integration tests:

```python
@pytest.fixture
def test_data_dir():
    """Return the path to the test data directory."""
    return os.path.join(os.environ.get("PYTHONPATH", "").split(":")[0], "tests", "data")

def test_image_processing_with_test_data(test_data_dir):
    """Test that the image processor can process test data."""
    # Setup
    config = ConfigurationManager()
    image_processor = ImageProcessor(config)

    # Process test image
    test_image_path = os.path.join(test_data_dir, "test_image.jpg")
    result = image_processor.process_image(test_image_path)

    # Verify result
    assert result is not None
    assert result.size == (400, 300)
```

## End-to-End Integration Tests

End-to-end integration tests verify that the entire application works together:

```python
def test_end_to_end_integration():
    """Test that the entire application works together."""
    # Setup
    config = ConfigurationManager()
    app = PreviewMakerApp(config)

    # Integration
    app.load_image("test_data/test_image.jpg")

    # Verification
    assert app.get_image() is not None
    assert app.get_highlights() is not None
    assert len(app.get_highlights()) > 0
```

## Integration Test Coverage

Integration tests should cover all key integration points:

- **Component Interactions**: Test that components can interact with each other
- **Data Flow**: Test that data flows correctly between components
- **Error Handling**: Test that errors are handled correctly at integration points

## CI/CD Integration

Include integration tests in CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run integration tests
  run: docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/integration/
```