# Preview Maker Rebuild Plan

This directory contains the planning and setup materials for the Preview Maker rebuild project, focusing on migrating to GTK 4.0 and improving the overall architecture.

## Repository Information

This project is hosted in a public GitHub repository:

- **Repository URL**: [https://github.com/jdamboeck/preview-maker](https://github.com/jdamboeck/preview-maker)
- **Main Branch**: Contains stable, production-ready code
- **Develop Branch**: Integration branch for feature development

For detailed information on our Git workflow, branching strategy, and contribution guidelines, see [git_workflow.md](git_workflow.md).

## Project Structure

```
rebuild_plan/
├── docker/                  # Docker environment for development
│   ├── Dockerfile           # Base Docker image definition
│   ├── docker-compose.yml   # Docker Compose services configuration
│   ├── entrypoint.sh        # Container entrypoint script
│   ├── requirements.txt     # Python dependencies
│   ├── docker_diagnostics.py # Diagnostic tool for Docker environment
│   ├── verify_environment.py # Verification script for environment
│   └── README.md            # Docker environment documentation
├── gtk_overlay_test.py      # Test script for GTK 4.0 with Pillow and Cairo
├── cursor_readme.md         # Cursor IDE setup instructions
└── README.md                # This file
```

## Docker Environment

We've set up a comprehensive Docker environment for the Preview Maker rebuild project. The environment includes:

1. **Base Docker Image**: Ubuntu 22.04 with GTK 4.0, Cairo, and Python 3.10
2. **Multiple Services**:
   - `preview-maker`: Main development environment
   - `test`: For running tests in CI environment
   - `gtk-test`: For testing GTK overlay functionality
   - `diagnostics`: For running diagnostic checks
   - `verify`: For verifying the environment setup

3. **Verification Tools**:
   - `docker_diagnostics.py`: Comprehensive diagnostic tool
   - `verify_environment.py`: Quick verification script

4. **Commands**:
   - `docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker dev`: Start development environment
   - `docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test`: Run tests
   - `docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm gtk-test`: Run GTK overlay test
   - `docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm diagnostics`: Run diagnostics
   - `docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm verify`: Verify environment

## GTK 4.0 Migration

The `gtk_overlay_test.py` script demonstrates the capabilities of GTK 4.0 with Pillow and Cairo for circular overlays. This script serves as a proof of concept for the Preview Maker rebuild.

Key features demonstrated:
- GTK 4.0 application window setup
- Image loading and display
- Circular overlay creation with both Pillow and Cairo
- Drag-and-drop functionality

## Development Environment

The Docker environment provides a consistent development experience across different platforms. It includes:

1. **X11 Forwarding**: For GUI applications
2. **Persistent Volume**: For Python packages
3. **Development Tools**: Python debugging tools, linters, and test frameworks
4. **Diagnostic Tools**: For troubleshooting environment issues

## Getting Started

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/jdamboeck/preview-maker.git
   cd preview-maker
   ```

2. **Build the Docker Image**:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml build
   ```

3. **Verify the Environment**:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm verify
   ```

4. **Start Development Environment**:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker dev
   ```

5. **Run GTK Overlay Test**:
   ```bash
   docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm gtk-test
   ```

## Next Steps

1. Implement the core components of the Preview Maker application
2. Migrate existing functionality to GTK 4.0
3. Improve the architecture for better maintainability and extensibility
4. Add new features as outlined in the roadmap

## References

- [GTK 4.0 Documentation](https://docs.gtk.org/gtk4/)
- [Cairo Documentation](https://www.cairographics.org/documentation/)
- [Pillow Documentation](https://pillow.readthedocs.io/en/stable/)
- [Docker Documentation](https://docs.docker.com/)

## Documentation

Detailed documentation for the rebuild project:

- Architecture: `architecture/`
- Prerequisites: `00_prerequisites/`
- Implementation Roadmap: `implementation_roadmap.md`
- Docker Integration: `docker_integration_plan.md`
- Testing Strategy: `testing/01_testing_strategy.md`
- Unattended Agent Guidelines: `testing/unattended_agent_guidelines.md`
- Docker Usage: `docker/README.md`
- Git Workflow: `git_workflow.md`

## Cursor IDE Setup

For proper IDE assistance when working with this project:

1. **Place the combined `.cursorrules` file in the project root:**
   ```bash
   # Ensure the .cursorrules file is in the root directory
   cp /home/jd/dev/projects/preview-maker/.cursorrules /path/to/your/workspace/
   ```

   This ensures consistent AI assistance across the entire project, including both old and new code structures.

2. **Cursor loads rules hierarchically:**
   - It prioritizes rules in the current directory
   - Then falls back to parent directories
   - For this project, keep only one `.cursorrules` file in the root directory

3. **IDE assistance helps with:**
   - Docker environment setup and commands
   - Testing standards and patterns
   - Code style and architecture guidelines
   - GTK and image processing best practices

## Working with Old Directory Structure

When working with the old monolithic code structure alongside the rebuild effort:

1. **Code Mapping**
   - Refer to `00_prerequisites/02_existing_code_mapping.md` for how old code maps to new components
   - This helps maintain consistency between both structures

2. **Minimal Changes**
   - Keep changes to old code structure minimal and focused on critical fixes
   - Document any changes made for reference during migration

3. **Transition Strategy**
   - Use adapter patterns to bridge between old and new code during transition
   - Follow the migration sequence in `00_prerequisites/09_refactoring_strategy.md`

4. **Testing**
   - Test changes in both old and new structures where applicable
   - Ensure backward compatibility during the transition

5. **Docker Environment**
   - Use the Docker environment for testing both old and new code structures
   - The verification tools work with both structures

For detailed guidance on working with both structures, see the "Working with Old Directory Structure" section in the `.cursorrules` file.

## Documentation Requirements

All changes during the rebuild project must be properly documented:

1. **Component Documentation**:
   - Document each new component with its purpose and interfaces
   - Update component dependency diagrams when adding connections
   - Include examples of component usage

2. **Migration Documentation**:
   - Document any changes to the existing codebase
   - Record mapping between old and new code structures
   - Note any behavior changes in components

3. **Development Process Documentation**:
   - Document decisions made during implementation
   - Update roadmap progress as components are completed
   - Record any deviations from the original design

Follow the full "Documentation Update Guidelines" in the `.cursorrules` file.

## Implementation Resources

To help with the rebuild implementation, use these additional resources:

1. **Starting Point**: See `06_implementation_strategy/00_starting_point.md` for concrete first steps
2. **Error Recovery**: Refer to `00_prerequisites/11_error_recovery_strategies.md` for solutions to common issues
3. **Quick Reference**: Use `quick_reference.md` for code patterns and common commands
4. **Agent Memory**: For AI agents, `agent_shortterm_memory.md` provides a compact development cycle guide
5. **Status Analysis**: For tracking project progress, `status_analysis_prompt.md` helps analyze and plan next tasks
6. **Progress Tracking**: Update `progress_tracking.md` as components are implemented

These resources provide practical guidance to help implement the rebuild efficiently and consistently.