# Docker Integration Plan for Preview Maker Rebuild

This document outlines how Docker will be integrated into the Preview Maker rebuild project, providing a consistent development and testing environment across all platforms.

## 1. Docker Environment Overview

The Docker environment for Preview Maker consists of the following components:

- **Base Image**: Ubuntu 22.04 with GTK 4.0, Cairo, and Python 3.10
- **Development Container**: For active development with X11 forwarding
- **Test Container**: For running automated tests in CI/CD pipelines
- **GTK Test Container**: For testing GTK-specific functionality
- **Diagnostics Container**: For running diagnostic checks
- **Verification Container**: For verifying the environment setup

## 2. Development Workflow

### 2.1 Setting Up the Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/preview-maker.git
cd preview-maker

# Build the Docker image
docker-compose -f rebuild_plan/docker/docker-compose.yml build

# Verify the environment
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm verify
```

### 2.2 Development Cycle

```bash
# Start a development shell
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker dev

# Run the application
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker run

# Run tests
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test
```

## 3. Testing Strategy

### 3.1 Unit Testing

Unit tests are run in the test container, which provides a consistent environment for testing individual components:

```bash
# Run all unit tests
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest

# Run specific tests
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest path/to/test_file.py
```

### 3.2 Integration Testing

Integration tests verify that components work together correctly:

```bash
# Run integration tests
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/integration/
```

### 3.3 GTK UI Testing

GTK UI tests are run in the gtk-test container, which provides X11 forwarding for GUI testing:

```bash
# Run GTK tests
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm gtk-test
```

### 3.4 Headless Testing

For CI/CD pipelines, tests can be run in headless mode:

```bash
# Run headless tests
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest --headless
```

## 4. Component-Specific Docker Integration

### 4.1 Image Processing Component

The Image Processing component can be tested in the Docker environment using the following approach:

```python
# Example test for image processing
def test_image_processing():
    processor = ImageProcessor()
    result = processor.process_image("test_image.jpg")
    assert result is not None
```

### 4.2 Gemini AI Service

The Gemini AI Service can be tested in the Docker environment using mocks:

```python
# Example test for Gemini AI Service
def test_gemini_ai_service():
    service = GeminiAIService(MockConfig())
    result = service.analyze_image("test_image.jpg")
    assert result is not None
```

### 4.3 GTK UI Framework

The GTK UI Framework can be tested in the Docker environment using the gtk-test container:

```python
# Example test for GTK UI
def test_gtk_ui():
    window = MainWindow()
    assert window.get_title() == "Preview Maker"
```

## 5. CI/CD Integration

### 5.1 GitHub Actions

```yaml
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

### 5.2 GitLab CI

```yaml
stages:
  - build
  - test

build:
  stage: build
  script:
    - docker-compose -f rebuild_plan/docker/docker-compose.yml build

test:
  stage: test
  script:
    - docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test
```

## 6. Debugging in Docker

### 6.1 Interactive Debugging

```bash
# Start a development shell
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker dev

# Run Python with debugger
python -m debugpy --listen 0.0.0.0:5678 --wait-for-client app.py
```

### 6.2 Diagnostic Tools

```bash
# Run diagnostics
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm diagnostics

# Check specific component
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm diagnostics --component=image_processor
```

## 7. Best Practices

1. **Use Volume Mounts**: Mount the source code as a volume to avoid rebuilding the image for code changes
2. **Persistent Python Environment**: Use a named volume for the Python virtual environment to avoid reinstalling packages
3. **X11 Forwarding**: Configure X11 forwarding for GUI applications
4. **Environment Variables**: Use environment variables for configuration
5. **Entrypoint Script**: Use an entrypoint script for common tasks

## 8. Known Limitations

1. **X11 Forwarding**: X11 forwarding may not work in all environments, especially in CI/CD pipelines
2. **Performance**: Docker may have slightly lower performance than native development
3. **GPU Access**: GPU acceleration may not be available in all environments

## 9. Conclusion

Docker provides a consistent environment for developing and testing the Preview Maker application. By following this integration plan, developers can ensure that their code works consistently across all platforms and in CI/CD pipelines.