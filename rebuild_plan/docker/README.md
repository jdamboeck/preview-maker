# Docker Environment for Preview Maker

This directory contains files needed to set up a consistent Docker environment for developing, testing, and debugging the Preview Maker application. The Docker environment ensures that all developers have the same dependencies and tools, regardless of their host operating system.

## Quick Start

### 1. Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (version 20.10 or later)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 2.0 or later)
- X11 server (for GUI applications):
  - **Linux**: Already installed
  - **macOS**: Install [XQuartz](https://www.xquartz.org/)
  - **Windows**: Install [VcXsrv](https://sourceforge.net/projects/vcxsrv/) or [Xming](https://sourceforge.net/projects/xming/)

### 2. Build the Docker Image

From the project root directory:

```bash
cd /path/to/preview-maker
docker-compose -f rebuild_plan/docker/docker-compose.yml build
```

### 3. Start the Development Environment

```bash
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker
```

This will start a bash session in the container with X11 forwarding enabled.

## Usage Guide

### Running the Application

Inside the Docker container, you can run the Preview Maker application:

```bash
cd /app
python app/main.py
```

### Running Diagnostic Checks

To verify your Docker environment setup:

```bash
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm diagnostics
```

For more detailed diagnostics:

```bash
# Inside the container
python rebuild_plan/docker/docker_diagnostics.py --output /app/diagnostic_report.json
```

### Running Tests

To run all tests:

```bash
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test
```

To run specific tests with pytest arguments:

```bash
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker test -v tests/test_image_processor.py
```

## Debugging in Docker

### Command Line Debugging

The Docker environment includes several debugging tools:

- `gdb`: GNU Debugger for low-level debugging
- `ipdb`: Enhanced Python debugger
- `strace`/`ltrace`: System call tracing
- `valgrind`: Memory leak detection
- `heaptrack`: Heap memory profiling

Example:

```bash
python -m ipdb app/main.py
```

### Remote Debugging with VS Code or Cursor IDE

The Docker container is configured to support remote debugging:

1. In your application code, add:

```python
import debugpy
debugpy.listen(("0.0.0.0", 5678))
debugpy.wait_for_client()
```

2. Uncomment the port mapping in `docker-compose.yml`:

```yaml
ports:
  - "5678:5678"  # For debugpy
```

3. In VS Code/Cursor, create a launch configuration:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Remote Attach",
      "type": "python",
      "request": "attach",
      "connect": {
        "host": "localhost",
        "port": 5678
      },
      "pathMappings": [
        {
          "localRoot": "${workspaceFolder}",
          "remoteRoot": "/app"
        }
      ]
    }
  ]
}
```

## Integrated Debugging Cycle

The Docker environment integrates into the Preview Maker debugging cycle:

### 1. Automated Diagnostics

Before reporting an issue, run:

```bash
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker python rebuild_plan/docker/docker_diagnostics.py
```

This checks the environment, libraries, and system configuration.

### 2. Component Testing

When having issues with a specific component:

```bash
# Inside the container
python -m pytest tests/components/test_component_name.py -v
```

### 3. Headless Testing

For UI-related tests in a CI environment, the container uses Xvfb to provide a virtual display. This allows GTK applications to run without a physical display.

### 4. Known Limitations

- **X11 Forwarding**: The container is configured for X11 forwarding, but this requires proper setup on the host system. If you're having issues with GUI applications, use the diagnostic tool to check X11 forwarding status.
- **OpenGL Support**: OpenGL support may be limited in the container, which can affect some GTK rendering features.

### 5. Export Diagnostic Reports

For AI-assisted debugging:

```bash
# Inside the container
python rebuild_plan/docker/docker_diagnostics.py -o diagnostic_report.json
```

This report can be provided to AI assistants for automated troubleshooting.

## Customizing the Environment

### Adding Python Packages

1. Add packages to `docker/requirements.txt`
2. Rebuild the image:

```bash
docker-compose -f rebuild_plan/docker/docker-compose.yml build
```

### Adding System Packages

1. Modify the `Dockerfile`
2. Rebuild the image:

```bash
docker-compose -f rebuild_plan/docker/docker-compose.yml build
```

## Troubleshooting

### X11 Forwarding Issues

1. Check your X11 server is running
2. Verify permissions: `xhost +local:docker`
3. Check environment variables: `echo $DISPLAY`

### Container Permission Issues

If you encounter permission issues:

```bash
# Fix ownership from host system
sudo chown -R $USER:$USER .
```

### Image Building Problems

Clear Docker cache and rebuild:

```bash
docker-compose -f rebuild_plan/docker/docker-compose.yml build --no-cache
```

### GTK/Cairo Issues

If you're having issues with GTK or Cairo:

1. Run the diagnostic tool to check the installation
2. Verify that the system packages are installed correctly
3. Check that the Python environment has access to the system packages

## Best Practices

1. **Use volume mounts for development**: Changes made in the container will be reflected on your host system
2. **Run tests within the container**: Ensures consistent test environment
3. **Use the diagnostic tool before reporting issues**: Helps identify environment problems
4. **Export diagnostic reports for AI assistance**: Provides context for AI troubleshooting

## CI/CD Integration

The Docker environment is compatible with CI/CD systems:

```yaml
# Example GitHub Actions workflow
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests in Docker
        run: docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test
```

## References

- [GTK 4.0 Documentation](https://docs.gtk.org/gtk4/)
- [Docker Documentation](https://docs.docker.com/)
- [Debugging Python Applications](https://docs.python.org/3/library/debug.html)
- [Preview Maker Architecture](../architecture/01_architecture_overview.md)