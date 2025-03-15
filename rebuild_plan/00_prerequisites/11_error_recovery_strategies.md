# Error Recovery Strategies

This document outlines strategies for recovering from common errors during the Preview Maker rebuild project. It serves as a quick reference for troubleshooting and resolving issues.

## Docker Environment Issues

### Problem: Container fails to build

**Solutions:**
1. Check for network connectivity issues:
   ```bash
   ping -c 3 google.com
   ```

2. Try building with no cache:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml build --no-cache
   ```

3. Check Docker disk space:
   ```bash
   docker system df
   ```
   If needed, clean up:
   ```bash
   docker system prune -a
   ```

### Problem: X11 forwarding not working

**Solutions:**
1. Check the DISPLAY environment variable:
   ```bash
   echo $DISPLAY
   ```

2. Verify X11 socket permissions:
   ```bash
   ls -la /tmp/.X11-unix/
   ```

3. Try running with explicit X11 options:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix gtk-test
   ```

### Problem: Volume mounts not working

**Solutions:**
1. Check file ownership and permissions
2. Try with absolute paths
3. Restart Docker daemon

## GTK Environment Issues

### Problem: GTK initialization fails

**Solutions:**
1. Check for GTK installation in container:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker python -c "import gi; gi.require_version('Gtk', '4.0'); from gi.repository import Gtk; print('GTK available')"
   ```

2. For UI tests in headless environments, use the mock approach:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/ui/ --headless
   ```

### Problem: Cairo drawing issues

**Solutions:**
1. Verify Cairo installation:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker python -c "import cairo; print(cairo.version)"
   ```

2. Check for common drawing issues:
   - Surface dimensions must be positive
   - Drawing operations must be within surface bounds
   - Alpha channel handling issues

## Gemini AI Integration Issues

### Problem: API authentication fails

**Solutions:**
1. Check API key presence:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker python -c "import os; print('API key present' if os.environ.get('GEMINI_API_KEY') else 'API key missing')"
   ```

2. Verify API key format (should be a string of ~40 characters)

3. Ensure network connectivity to Google API endpoints

### Problem: Response parsing failures

**Solutions:**
1. Enable verbose API logging
2. Validate response format matches expected schema
3. Implement more robust error handling around JSON parsing

## Python Environment Issues

### Problem: Import errors

**Solutions:**
1. Check Python path:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker python -c "import sys; print(sys.path)"
   ```

2. Verify package installation:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker pip list
   ```

3. Create proper `__init__.py` files in all module directories

### Problem: Dependency conflicts

**Solutions:**
1. Create a new virtual environment with only required packages
2. Use `pip-compile` to generate pinned requirements
3. Explicitly specify versions for all dependencies

## Database/Storage Issues

### Problem: File permission errors

**Solutions:**
1. Check file ownership in container:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker ls -la /path/to/directory
   ```

2. Ensure volume mounts have correct permissions
3. Use relative paths within the application directory

### Problem: Disk space issues

**Solutions:**
1. Check disk usage in container:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker df -h
   ```

2. Implement cleanup routines for temporary files
3. Use a separate volume for application data

## Testing Issues

### Problem: Tests fail inconsistently

**Solutions:**
1. Check for race conditions in threaded code
2. Ensure tests are isolated from each other
3. Use fixtures to ensure consistent test environment
4. Add more logging to identify intermittent issues

### Problem: Coverage reports show gaps

**Solutions:**
1. Add tests specifically targeting uncovered code
2. Use branch coverage in addition to line coverage
3. Exclude generated code or vendor code from coverage reports

## Real-Time Recovery Actions

1. **Log Analysis**: Always check logs first:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker cat /var/log/app.log
   ```

2. **Diagnostic Mode**: Run the application with diagnostic logging:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker dev --debug
   ```

3. **Component Isolation**: Test components in isolation:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/unit/test_specific_component.py
   ```

4. **Environment Rebuild**: When all else fails, rebuild the environment:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml down
   docker system prune -a --volumes
   docker-compose -f rebuild_plan/docker/docker-compose.yml build --no-cache
   ```

## Prevention Strategies

1. **Regular Testing**: Run tests frequently during development
2. **Incremental Changes**: Make small, focused changes
3. **Version Control**: Commit often with descriptive messages
4. **Documentation**: Document any non-obvious fixes or workarounds
5. **Consistent Environment**: Always use the Docker environment