# Testing Strategy

This document outlines the overall testing approach for the rebuilt Preview Maker application, with a focus on Docker-based testing.

## Testing Philosophy

The Preview Maker testing strategy follows these key principles:

1. **Consistency**: All tests should run in a consistent environment provided by Docker
2. **Automation**: Tests should be automated and run as part of CI/CD pipelines
3. **Isolation**: Components should be tested in isolation with appropriate mocks
4. **Coverage**: Tests should cover all critical functionality with a target of >80% code coverage
5. **Performance**: Performance tests should verify that the application meets performance requirements

## Test Coverage Goals

- **Unit Tests**: >80% code coverage for core components
- **Integration Tests**: Key component interactions tested
- **UI Tests**: Critical user flows tested
- **Performance Tests**: Key performance metrics verified

## Testing Tools and Frameworks

- **pytest**: Primary testing framework
- **pytest-cov**: Code coverage reporting
- **pytest-mock**: Mocking framework
- **pytest-benchmark**: Performance testing
- **Docker**: Consistent testing environment

## Docker-Based Testing

All tests are run in Docker containers to ensure a consistent environment:

```bash
# Run all tests
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test

# Run specific tests
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest path/to/test_file.py

# Run tests with coverage
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest --cov=preview_maker
```

### Test Container Configuration

The test container is configured with all necessary dependencies:

- Python 3.10
- GTK 4.0
- Cairo
- Pillow
- pytest and plugins

### Headless Testing

For CI/CD pipelines, tests are run in headless mode:

```bash
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest --headless
```

## Continuous Integration Approach

Tests are automatically run on:

1. **Pull Requests**: All tests must pass before merging
2. **Main Branch**: All tests run after each merge
3. **Nightly Builds**: Full test suite with extended performance tests

## Test Environment Setup

### Local Development

```bash
# Build the Docker image
docker-compose -f rebuild_plan/docker/docker-compose.yml build

# Verify the environment
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm verify

# Run tests
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test
```

### CI/CD Pipeline

```yaml
# GitHub Actions example
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Build Docker image
      run: docker-compose -f rebuild_plan/docker/docker-compose.yml build
    - name: Run tests
      run: docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test
```

## Testing Roles and Responsibilities

- **Developers**: Write unit tests for their code
- **QA Team**: Write integration and UI tests
- **DevOps**: Maintain the Docker testing environment
- **CI/CD Pipeline**: Automatically run tests on code changes

## Test Categories

### Unit Tests

Test individual components in isolation:

```python
# Example unit test
def test_image_processor():
    processor = ImageProcessor()
    result = processor.process_image("test_image.jpg")
    assert result is not None
```

### Integration Tests

Test component interactions:

```python
# Example integration test
def test_ai_service_with_image_processor():
    processor = ImageProcessor()
    ai_service = GeminiAIService()

    processed_image = processor.process_image("test_image.jpg")
    result = ai_service.analyze_image(processed_image)

    assert result is not None
```

### UI Tests

Test the user interface:

```python
# Example UI test
def test_main_window():
    window = MainWindow()
    assert window.get_title() == "Preview Maker"
```

### Performance Tests

Test performance metrics:

```python
# Example performance test
def test_image_loading_performance(benchmark):
    processor = ImageProcessor()

    # Benchmark image loading
    result = benchmark(processor.process_image, "test_image.jpg")

    # Verify performance
    assert benchmark.stats.stats.mean < 0.2  # Less than 200ms
```

*This document will be expanded as the project progresses.*