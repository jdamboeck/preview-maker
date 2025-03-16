# April 2025 Documentation Update Release

This release merges our latest documentation and workflow improvements from the develop branch to main.

## Major Enhancements

### Improved Git Workflow Documentation

- Completely rewrote `git_workflow.md` with a focus on:
  - Prioritizing MCP functions as first choice
  - Using non-interactive GitHub CLI API commands as fallback
  - Avoiding direct Git commands entirely when possible
  
- Added new supporting documentation:
  - `mcp_tools_reference.md`: Comprehensive guide to MCP GitHub functions
  - `github_cli_caveats.md`: Detailed guide to GitHub CLI issues and solutions
  
- Added helper scripts:
  - `github_cli_workflow_helpers.sh`: A bash script with helper functions for common GitHub operations
  - `github_cli_helpers.py`: A Python script to generate GitHub CLI commands

### Enhanced Testing Documentation

- Added comprehensive UI testing guidance with Xwayland support
- Created mock-based testing approach for headless environments
- Documented CI/CD pipeline for GTK applications
- Added troubleshooting guides for common testing issues

### Template Improvements

- Implemented GitHub issue templates
- Added comprehensive PR template
- Created workflow test components to validate templates
- Added branch protection documentation

## Key Commits

- d865f5b: docs: Update Git workflow with tested commands
- c753026: feat: Add GitHub CLI helper script
- e2b6587: docs: Add PR template test results
- 3eb6f87: feat: Add template test component
- e75c694: docs: Update progress tracking to reflect completed UI test improvements
- b6d42a5: docs: Add MCP tools reference and GitHub CLI guidance
- 4f1224b: docs: Enhance GitHub workflow with templates, CLI guide, and branch protection
- 3accb10: docs: Enhance UI testing documentation with comprehensive Xwayland guide
- 1f428e9: docs: Add Known Issues section and update mocks
- 7750ca4: feat: Add CI/CD examples for GTK testing

## Verification

- All GitHub workflow improvements have been tested and validated
- Template functionality has been verified with actual usage
- Documentation has been reviewed for accuracy and completeness
- Helper scripts have been tested in various scenarios

## Impact

This release significantly improves the development workflow and documentation for the Preview Maker project, making it easier for contributors to follow best practices and avoid common pitfalls.