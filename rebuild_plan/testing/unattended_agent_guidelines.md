# Unattended Agent Usage Guidelines for Preview Maker

This document provides guidelines for unattended agent usage in the Preview Maker project, particularly focusing on Docker-based operations and testing in continuous integration environments.

## 1. Principles for Unattended Operation

For any unattended operation (CI/CD, automated testing, scheduled jobs), follow these principles:

1. **Idempotency**: Operations should be idempotent and produce the same result regardless of how many times they're run
2. **Error Handling**: Clearly define exit codes and error states
3. **Logging**: Output sufficient logs for post-run analysis
4. **Environment Independence**: Operations should not rely on specific host configurations
5. **Resource Cleanup**: Containers should clean up after themselves

## 2. Docker Command Structure for Unattended Use

All Docker commands should follow this consistent pattern for unattended usage:

```bash
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm [service] [command]
```

For example:
```bash
# Running tests unattended
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/ --headless

# Running verification unattended
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm verify
```

### Key Command Line Flags

- Always use `--rm` to remove containers after execution
- For UI-based tests, always include `--headless` flag if supported
- For CI environments, include appropriate flags for report generation (e.g., `--cov-report=xml`)

## 3. CI/CD Integration

For CI/CD pipeline integration:

```yaml
# GitHub Actions Example
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
      - uses: actions/checkout@v3
      - name: Build and run tests
        run: |
          docker-compose -f rebuild_plan/docker/docker-compose.yml build
          docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm verify
          docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest --headless --cov=preview_maker --cov-report=xml
```

## 4. Headless UI Testing in Unattended Mode

For running GTK UI tests in unattended environments like CI:

1. **Always use the mock approach** when in completely headless environments:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/ui/ --headless
   ```

2. **Use Xvfb with real GTK** in environments where a virtual display can be initialized:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm gtk-test pytest tests/ui/
   ```

## 5. Environment Variables for Unattended Operation

Set these environment variables for unattended operation:

| Variable | Purpose | Example |
|----------|---------|---------|
| `PREVIEW_MAKER_ENV` | Specifies the environment | `test`, `ci` |
| `PYTHONPATH` | Ensures module imports work | `/app` |
| `DISPLAY` | For X11 forwarding if needed | `:0` |
| `HEADLESS` | Forces headless mode | `true` |

Example Docker command with environment variables:

```bash
docker-compose -f rebuild_plan/docker/docker-compose.yml run -e PREVIEW_MAKER_ENV=ci -e HEADLESS=true --rm test pytest
```

## 6. Diagnostics in Unattended Mode

For diagnostic runs in unattended environments:

```bash
# Run all diagnostics
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm diagnostics > diagnostics_report.txt

# Run component-specific diagnostics
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm diagnostics --component=image_processor > image_processor_diagnostics.txt
```

## 7. Automated Documentation Generation

For documentation generation in unattended environments:

```bash
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker generate-docs
```

## 8. Best Practices for Autonomous Debugging

For autonomous debugging in unattended environments:

1. Follow the debugging cycle in `starter_prompt.md`
2. Use the Docker environment verification as the first step
3. Run comprehensive diagnostics to gather information
4. Use component-specific tests for targeted debugging
5. Generate detailed logs for analysis

## 9. Consistency Requirements

To ensure consistency across all documentation and code:

1. Always refer to Docker commands using the full path (`rebuild_plan/docker/docker-compose.yml`)
2. Use consistent service names:
   - `preview-maker`: Main application
   - `test`: Test environment
   - `verify`: Environment verification
   - `gtk-test`: GTK-specific tests with X11
   - `diagnostics`: Diagnostic tools
3. Use consistent command structures as described in section 2

## 10. Updating This Guide

This guide should be updated whenever:

1. New Docker services are added
2. New command line flags are added for unattended operation
3. CI/CD workflow changes
4. Test execution strategy changes

Keep all documentation in sync with this guide to ensure consistency in unattended agent usage.