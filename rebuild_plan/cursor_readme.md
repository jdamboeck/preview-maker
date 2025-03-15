# Cursor IDE Setup for Preview Maker

This directory contains all the necessary setup files and instructions for setting up Cursor IDE and the development environment for the Preview Maker application rebuild.

## Quick Start Guide

1. **Set up the development environment**
   - Follow the detailed instructions in [`cursor_setup.md`](cursor_setup.md)
   - Install required system dependencies for GTK 4.0
   - Create Python virtual environment and install packages
   - **ALTERNATIVE**: Use the Docker environment in the [`docker/`](docker/README.md) directory

2. **Test your GTK environment**
   - Run the GTK overlay test script to verify your setup:
     ```bash
     python rebuild_plan/gtk_overlay_test.py
     ```
   - Or use Docker:
     ```bash
     docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm gtk-test
     ```
   - This test demonstrates the circular overlay capabilities needed for Preview Maker

3. **Set up Cursor IDE**
   - Install Cursor IDE from [https://cursor.sh/](https://cursor.sh/)
   - Open the Preview Maker project folder in Cursor
   - Copy the `.vscode/settings.json` and `.vscode/launch.json` files from the setup instructions
   - Move the `.cursorrules` file to your project root

## What's Included

- **cursor_setup.md**: Comprehensive setup instructions
- **gtk_overlay_test.py**: Test script for GTK 4.0 and image processing capabilities
- **.cursorrules**: Guidelines for AI-assisted development
- **Example configuration files** for VS Code settings compatible with Cursor
- **Docker environment**: Containerized development setup for consistent environments

## Autonomous Debugging

The setup includes autonomous debugging infrastructure:

1. **Diagnostic utilities** for monitoring component health
2. **Structured debugging cycle** for AI assistants to troubleshoot issues
3. **GTK-specific debugging tools** like the GTK Inspector
4. **Automatic test image generation** for consistent testing
5. **Docker-based diagnostics** for environment verification

## Project Structure

The setup creates the following recommended project structure:

```
preview-maker/
├── app/
│   ├── components/         # Core components of the application
│   │   └── ui/             # GTK UI components
│   └── utils/              # Utility modules including diagnostic tools
├── tests/                  # Test files with pytest fixtures
├── resources/              # Static resources and test images
├── .vscode/                # IDE configuration
├── docker/                 # Docker environment configuration
└── rebuild_plan/           # Rebuild documentation
```

## Troubleshooting

If you encounter issues:

1. Verify system dependencies using the diagnostic tool:
   ```bash
   python app/utils/debug_tool.py --system
   ```

2. Check component health:
   ```bash
   python app/utils/debug_tool.py --all
   ```

3. For Docker users, run comprehensive diagnostics:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm diagnostics
   ```

4. Inspect GTK rendering with GTK Inspector (Ctrl+Shift+I during application run)

5. Enable verbose logging by setting the `PREVIEW_MAKER_DEBUG=1` environment variable

## Docker Integration

For consistent development across all environments, you can use the Docker setup:

1. **Build the Docker image**:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml build
   ```

2. **Start development environment**:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker
   ```

3. **Run the GTK test**:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm gtk-test
   ```

4. **Run all tests**:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test
   ```

See the [Docker README](docker/README.md) for more detailed instructions.

## Reference

For more details on the Preview Maker rebuild, refer to:
- [Technical Specifications](architecture/06_technical_specifications.md)
- [Implementation Roadmap](implementation_roadmap.md)
- [GTK Development Guide](00_prerequisites/04_gtk_development_guide.md)
- [Gemini AI Integration](00_prerequisites/05_gemini_ai_integration.md)
- [Docker Environment Guide](docker/README.md)