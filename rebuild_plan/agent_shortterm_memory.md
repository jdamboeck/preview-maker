# Agent Short-Term Memory

This document serves as a compact reference for agents working on the Preview Maker project, providing step-by-step guidance through the development cycle and links to detailed resources.

## Project Overview
- **Repository**: [GitHub.com/jdamboeck/preview-maker](https://github.com/jdamboeck/preview-maker)
- **Structure**: Transitioning from monolithic to component-based architecture
- **Key Technologies**: Python 3.8+, GTK 4.0, Pillow, Cairo, Gemini AI, Docker
- **Available Tools**: [MCP Tools Reference](../docs/mcp_tools_reference.md) for GitHub, Docker and filesystem operations

## Development Cycle

### 1. Analyze Task
- Understand requirements and context
- Identify which component is affected
- **Resources**:
  - [Application Analysis](00_prerequisites/01_application_analysis.md)
  - [Component Diagram](00_prerequisites/08_component_dependency_diagram.md)

### 2. Check Technical Documentation
- Review specifications for the component
- Check existing code structure
- **Resources**:
  - [Technical Specifications](architecture/06_technical_specifications.md)
  - [Existing Code Mapping](00_prerequisites/02_existing_code_mapping.md)
  - [GTK Development Guide](00_prerequisites/04_gtk_development_guide.md) (for UI tasks)
  - [Gemini AI Integration](00_prerequisites/05_gemini_ai_integration.md) (for AI features)

### 3. Create Branch Using GitHub CLI
- Work in feature branches branched from `develop`
- Branch naming: `feature/<feature-name>`, `bugfix/<bug-description>`
- **With GitHub CLI**:
  ```bash
  # Create feature branch from develop
  gh api repos/jdamboeck/preview-maker/git/refs -f ref="refs/heads/feature/new-feature" \
    -f sha="$(gh api repos/jdamboeck/preview-maker/git/refs/heads/develop --jq '.object.sha')"
  # Check out the branch locally
  gh repo clone jdamboeck/preview-maker --branch feature/new-feature
  # OR if you've already cloned the repo
  gh repo sync
  gh checkout feature/new-feature
  ```
- **With MCP Functions**:
  ```javascript
  // Create branch from develop
  mcp_github_create_branch({
    owner: "jdamboeck",
    repo: "preview-maker",
    branch: "feature/new-feature",
    from_branch: "develop"
  });
  ```
- **Resources**:
  - [Git Workflow](git_workflow.md)
  - [GitHub CLI Guide](../docs/github_cli_guide.md)
  - [MCP Tools Reference](../docs/mcp_tools_reference.md)

### 4. Formulate Plan
- Define approach based on component architecture
- List specific changes needed
- **Resources**:
  - [Implementation Strategy](06_implementation_strategy/00_starting_point.md)
  - [Quick Reference](quick_reference.md)

### 5. Create Tests
- Write tests before implementation (TDD approach)
- Include unit tests for components
- **Resources**:
  - [Testing Strategy](testing/01_testing_strategy.md)
  - [Unit Testing](testing/02_unit_testing.md)
  - [Integration Testing](testing/03_integration_testing.md) (if needed)
  - [UI Testing](testing/04_ui_testing.md) (for UI components)

### 6. Develop Feature
- Follow code style guidelines
- Implement modular, testable code
- **Docker Commands**:
  ```bash
  # Start development environment
  docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker

  # Run tests as you develop
  docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest path/to/test
  ```
- **Resources**:
  - [Component Patterns](#component-patterns)
  - [Code Style Guidelines](#code-style-guidelines)

### 7. Test
- Run tests in Docker environment
- Fix any regressions
- **Resources**:
  - [Error Recovery Strategies](00_prerequisites/11_error_recovery_strategies.md)

### 8. Update Documentation
- Update docstrings, comments, and README.md files
- Document architectural decisions
- **Resources**: [Documentation Guidelines](#documentation-guidelines)

### 9. Update Progress Tracking
- Mark completed components in progress tracking
- **Resource**: [Progress Tracking](progress_tracking.md)

### 10. Commit Changes
- Follow commit message conventions: `feat:`, `fix:`, `docs:`, etc.
- Keep first line under 50 characters
- **With MCP Functions**:
  ```javascript
  // Update file via MCP
  mcp_github_create_or_update_file({
    owner: "jdamboeck",
    repo: "preview-maker",
    path: "path/to/file.py",
    message: "feat: Add circular mask generation",
    content: "encoded_file_content",
    branch: "feature/circular-mask"
  });

  // For multiple files, use push_files instead
  mcp_github_push_files({
    owner: "jdamboeck",
    repo: "preview-maker",
    branch: "feature/circular-mask",
    message: "feat: Add circular mask generation",
    files: [
      {
        path: "path/to/file1.py",
        content: "file1_content"
      },
      {
        path: "path/to/file2.py",
        content: "file2_content"
      }
    ]
  });
  ```
- **With GitHub CLI** (if local changes need to be committed):
  ```bash
  # Stage and commit changes through GitHub CLI
  gh api --method POST /repos/jdamboeck/preview-maker/git/commits \
    -f message="feat: Add circular mask generation" \
    -f tree="[tree_sha]" \
    -f parent="[parent_sha]"
  # Note: This is simplified and would require additional steps to get tree_sha
  # Consider using gh workflow to run a GitHub Action for file commits instead
  ```

### 11. Create Pull Request
- Use GitHub CLI to create PR to `develop` branch
- Ensure tests pass in CI
- Reference any related issues
- **With GitHub CLI**:
  ```bash
  gh pr create --base develop --title "feat: Add circular mask generation" \
    --body "Implements algorithm for creating circular masks with adjustable parameters. Closes #123"
  ```
- **With MCP Functions**:
  ```javascript
  mcp_github_create_pull_request({
    owner: "jdamboeck",
    repo: "preview-maker",
    title: "feat: Add circular mask generation",
    body: "Implements algorithm for creating circular masks. Closes #123",
    head: "feature/circular-mask",
    base: "develop"
  });
  ```

### 12. Plan Next Task
- Consult progress tracking for next task
- Follow component dependency order

## Quick References

### Component Patterns
- Single responsibility per component
- Dependency injection for core components
- No global state - use explicit parameter passing
- Event-based communication between components
- UI components extend GTK parent classes

### Code Style Guidelines
- PEP 8, type annotations, 88 char line length
- 4 spaces for indentation
- Docstrings for all public functions and classes
- Descriptive names and f-strings

### Documentation Guidelines
- Update after adding/modifying functionality
- Google docstring format
- Keep README.md files current
- Use "docs:" prefix for documentation commits

### GitHub CLI Usage
- Always use GitHub CLI (`gh`) or MCP GitHub functions for repository operations
- Avoid direct Git commands
- Check [GitHub CLI Guide](../docs/github_cli_guide.md) for commands
- See complete [MCP Tools Reference](../docs/mcp_tools_reference.md) for all available MCP functions
- Key operations:
  ```bash
  # List pull requests
  gh pr list

  # Check PR status
  gh pr checks

  # Merge PR with branch deletion
  gh pr merge --merge --delete-branch

  # View repository status
  gh repo view

  # Sync repository
  gh repo sync
  ```

### Docker Tips
- Always use `--rm` flag
- For UI tests in headless environments:
  ```bash
  docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/ui/ --headless
  ```
- Verify environment before starting:
  ```bash
  docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm verify
  ```

## Error Resolution
If you get stuck:
1. Check [Error Recovery Strategies](00_prerequisites/11_error_recovery_strategies.md)
2. Run diagnostics: `docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm diagnostics`
3. Follow the debugging cycle in [Starter Prompt](starter_prompt.md)