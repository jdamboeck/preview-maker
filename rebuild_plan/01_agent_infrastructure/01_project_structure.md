# Phase 1.1: Agent-Friendly Project Structure

## Overview
This phase establishes the foundational directory structure and documentation that will enable AI assistants to effectively navigate and understand the codebase from the beginning of the rebuild process.

## Goals
- Create a base directory structure that follows component-based design
- Set up AI guidance documentation
- Establish a component mapping system for easy navigation

## Tasks

### Task 1.1.1: Set Up Base Directory Structure
- [ ] Create root-level directories
  ```bash
  mkdir -p app/{config,core,ui/{components,dialogs,handlers},utils}
  mkdir -p prompts resources/{css,icons}
  mkdir -p tests/{unit,integration,mocks}
  ```
- [ ] Create base Python package files
  ```bash
  touch app/__init__.py app/main.py
  touch app/config/__init__.py app/core/__init__.py app/ui/__init__.py app/utils/__init__.py
  ```
- [ ] Create placeholder README.md file with project overview

**Success Criteria**: Directory structure verified with `find app -type d | sort`

### Task 1.1.2: Create AI Guidance Documentation
- [ ] Create `.cursorrules` file with AI interaction guidelines
  ```bash
  touch .cursorrules
  ```
- [ ] Establish `ARCHITECTURE.md` with system overview and design principles
  ```bash
  touch ARCHITECTURE.md
  ```
- [ ] Create `docs/` directory for detailed documentation
  ```bash
  mkdir -p docs
  touch docs/FOR_AI_ASSISTANTS.md
  ```

**Success Criteria**: All documentation files exist and contain basic outlines

### Task 1.1.3: Implement Component Mapping System
- [ ] Create `COMPONENT_INDEX.md` that maps functionality to files
  ```bash
  touch COMPONENT_INDEX.md
  ```
- [ ] Define relationship between components in documentation
- [ ] Create navigation guides for common operations

**Success Criteria**: Component index captures all planned components and their relationships

## AI Entry Point
When entering at this step, you should:

1. First examine the current project structure with `find . -type d | grep -v "__pycache__" | sort`
2. Review the main application file (preview_maker.py) to understand the current monolithic structure
3. Proceed with implementing the directory structure as defined in Task 1.1.1
4. Create initial documentation files from Tasks 1.1.2 and 1.1.3
5. Fill each file with appropriate content based on the application's purpose
6. Verify all success criteria are met
7. Proceed to Phase 1.2: Code Standards and Documentation Templates

## Next Steps
Once this phase is complete, proceed to [Code Standards and Documentation Templates](./02_code_standards.md)