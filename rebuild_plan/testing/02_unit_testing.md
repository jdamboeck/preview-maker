# Unit Testing

This document details the approach to unit testing for the rebuilt Preview Maker application, with a focus on Docker-based testing.

## Unit Testing Standards

### Test Structure

All unit tests should follow this structure:

1. **Arrange**: Set up the test environment and create test objects
2. **Act**: Perform the action being tested
3. **Assert**: Verify the expected outcome

Example:

```python
def test_image_processor_loads_image():
    # Arrange
    processor = ImageProcessor()
    test_image_path = "test_data/test_image.jpg"

    # Act
    result = processor.load_image(test_image_path)

    # Assert
    assert result is not None
    assert result.size == (400, 300)
```

### Docker-Based Unit Testing

All unit tests are run in the Docker test container to ensure a consistent environment:

```bash
# Run all unit tests
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/unit/

# Run specific unit tests
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/unit/test_image_processor.py

# Run tests with coverage
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/unit/ --cov=preview_maker
```

## Test Fixture Patterns

### Using pytest Fixtures

Use pytest fixtures for common setup and teardown:

```python
@pytest.fixture
def image_processor():
    """Create an ImageProcessor instance for testing."""
    return ImageProcessor()

@pytest.fixture
def test_image():
    """Create a test image for testing."""
    img = Image.new("RGB", (400, 300), color="white")
    draw = ImageDraw.Draw(img)
    draw.rectangle((50, 50, 150, 150), fill="blue")
    return img

def test_process_image(image_processor, test_image):
    """Test that the image processor can process an image."""
    result = image_processor.process_image(test_image)
    assert result is not None
```

### Docker-Specific Fixtures

For Docker-specific fixtures, use environment variables:

```python
@pytest.fixture
def docker_env():
    """Check if running in Docker environment."""
    return os.environ.get("PREVIEW_MAKER_ENV") == "test"

def test_docker_environment(docker_env):
    """Test that we're running in the Docker environment."""
    assert docker_env is True
```

## Mocking Approach

### Using pytest-mock

Use pytest-mock for mocking dependencies:

```python
def test_gemini_ai_service(mocker):
    """Test that the Gemini AI service can analyze an image."""
    # Mock the API client
    mock_client = mocker.Mock()
    mock_client.generate_content.return_value = {"result": "test"}

    # Create service with mock client
    service = GeminiAIService()
    service._model = mock_client

    # Test the service
    result = service.analyze_image("test_image.jpg")

    # Verify the result
    assert result is not None
    mock_client.generate_content.assert_called_once()
```

### Mocking External Services

For external services, create mock implementations:

```python
class MockGeminiClient:
    """Mock implementation of the Gemini client."""

    def generate_content(self, content):
        """Mock generate_content method."""
        return {
            "result": [
                {"x": 0.5, "y": 0.5, "radius": 0.1, "description": "Test highlight"}
            ]
        }

def test_gemini_ai_service_with_mock():
    """Test that the Gemini AI service can analyze an image with a mock client."""
    # Create service with mock client
    service = GeminiAIService()
    service._model = MockGeminiClient()

    # Test the service
    result = service.analyze_image("test_image.jpg")

    # Verify the result
    assert result is not None
    assert len(result) == 1
    assert result[0]["description"] == "Test highlight"
```

## Component Isolation Techniques

### Dependency Injection

Use dependency injection to isolate components:

```python
def test_preview_maker_app():
    """Test that the Preview Maker app can be initialized with mock components."""
    # Create mock components
    mock_config = MockConfig()
    mock_image_processor = MockImageProcessor()
    mock_ai_service = MockGeminiAIService()

    # Create app with mock components
    app = PreviewMakerApp(
        config=mock_config,
        image_processor=mock_image_processor,
        ai_service=mock_ai_service
    )

    # Verify the app
    assert app is not None
    assert app.config is mock_config
    assert app.image_processor is mock_image_processor
    assert app.ai_service is mock_ai_service
```

### Interface-Based Testing

Test against interfaces rather than concrete implementations:

```python
def test_image_processor_interface():
    """Test that the image processor implements the required interface."""
    processor = ImageProcessor()

    # Verify the interface
    assert hasattr(processor, "process_image")
    assert callable(processor.process_image)
    assert hasattr(processor, "create_thumbnail")
    assert callable(processor.create_thumbnail)
```

## Test Naming Conventions

Use descriptive test names that indicate:

1. The component being tested
2. The action being performed
3. The expected outcome

Examples:

- `test_image_processor_loads_image`
- `test_gemini_ai_service_analyzes_image`
- `test_ui_displays_image`

## Test Coverage Metrics

### Coverage Goals

- **Core Components**: >80% code coverage
- **UI Components**: >70% code coverage
- **Utility Functions**: >90% code coverage

### Measuring Coverage

Use pytest-cov to measure coverage:

```bash
# Run tests with coverage
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest --cov=preview_maker

# Generate HTML coverage report
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest --cov=preview_maker --cov-report=html
```

### Coverage Reports in CI/CD

Include coverage reports in CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run tests with coverage
  run: docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest --cov=preview_maker --cov-report=xml

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v1
  with:
    file: ./coverage.xml
```