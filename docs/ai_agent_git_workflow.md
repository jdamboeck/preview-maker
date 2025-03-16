# AI Agent Integration with Git Workflow

This document provides guidelines for integrating AI agents with the Preview Maker Git workflow, ensuring consistent and standardized contributions.

## Overview

AI agents, such as Claude or other AI assistants, can help with the Preview Maker project in various ways, including code generation, documentation updates, and issue resolution. This guide ensures that AI agent contributions follow the project's Git workflow and maintain code quality standards.

## GitHub MCP Functions for AI Agents

When working with AI assistants that support MCP functions, prefer these over direct Git commands for GitHub operations:

```javascript
// Create a pull request
mcp_github_create_pull_request({
  owner: "jdamboeck",
  repo: "preview-maker",
  title: "feat: Add new feature",
  body: "Implements...\n\nCloses #123",
  head: "feature/my-feature",
  base: "develop"
});

// Create or update a file
mcp_github_create_or_update_file({
  owner: "jdamboeck",
  repo: "preview-maker",
  path: "path/to/file.md",
  content: "File content here",
  message: "docs: Update documentation",
  branch: "feature/my-feature"
});

// Create an issue
mcp_github_create_issue({
  owner: "jdamboeck",
  repo: "preview-maker",
  title: "bug: Something is broken",
  body: "When I do X, Y happens instead of Z",
  labels: ["bug", "priority-high"]
});
```

## AI Agent Workflow Patterns

### Feature Development

1. **Branch Creation**:
   ```javascript
   // Create feature branch from develop
   mcp_github_create_branch({
     owner: "jdamboeck",
     repo: "preview-maker",
     branch: "feature/ai-generated-feature",
     from_branch: "develop"
   });
   ```

2. **Code Implementation**:
   ```javascript
   // Add or update files
   mcp_github_create_or_update_file({
     owner: "jdamboeck",
     repo: "preview-maker",
     path: "path/to/new/file.py",
     content: "# Generated code\n...",
     message: "feat: Implement feature X",
     branch: "feature/ai-generated-feature"
   });
   ```

3. **Pull Request Creation**:
   ```javascript
   // Create PR
   mcp_github_create_pull_request({
     owner: "jdamboeck",
     repo: "preview-maker",
     title: "feat: Implement feature X",
     body: "This PR adds feature X, which...\n\nCloses #123",
     head: "feature/ai-generated-feature",
     base: "develop"
   });
   ```

### Documentation Updates

1. **Branch Creation**:
   ```javascript
   // Create documentation branch
   mcp_github_create_branch({
     owner: "jdamboeck",
     repo: "preview-maker",
     branch: "docs/update-readme",
     from_branch: "develop"
   });
   ```

2. **Documentation Changes**:
   ```javascript
   // Update documentation file
   mcp_github_create_or_update_file({
     owner: "jdamboeck",
     repo: "preview-maker",
     path: "README.md",
     content: "# Updated content\n...",
     message: "docs: Improve README clarity",
     branch: "docs/update-readme"
   });
   ```

3. **Pull Request Creation**:
   ```javascript
   // Create PR for documentation update
   mcp_github_create_pull_request({
     owner: "jdamboeck",
     repo: "preview-maker",
     title: "docs: Update README",
     body: "This PR improves the README by...\n\nCloses #456",
     head: "docs/update-readme",
     base: "develop"
   });
   ```

### Bug Fixes

1. **Branch Creation**:
   ```javascript
   // Create bugfix branch
   mcp_github_create_branch({
     owner: "jdamboeck",
     repo: "preview-maker",
     branch: "bugfix/fix-issue-789",
     from_branch: "develop"
   });
   ```

2. **Code Fixes**:
   ```javascript
   // Update file with fix
   mcp_github_create_or_update_file({
     owner: "jdamboeck",
     repo: "preview-maker",
     path: "path/to/buggy/file.py",
     content: "# Fixed code\n...",
     message: "fix: Resolve issue with X",
     branch: "bugfix/fix-issue-789"
   });
   ```

3. **Pull Request Creation**:
   ```javascript
   // Create PR for bug fix
   mcp_github_create_pull_request({
     owner: "jdamboeck",
     repo: "preview-maker",
     title: "fix: Resolve issue with X",
     body: "This PR fixes issue #789 by...\n\nFixes #789",
     head: "bugfix/fix-issue-789",
     base: "develop"
   });
   ```

## Commit Message Guidelines for AI Agents

AI agents should follow the same commit message standards as human contributors:

1. **Use the correct prefix**:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Formatting changes
   - `refactor:` - Code refactoring without functional changes
   - `test:` - Adding or updating tests
   - `chore:` - Maintenance tasks

2. **Keep the first line concise** (under 50 characters)

3. **Provide a detailed description** for complex changes

Example:
```
feat: Add circular mask generation

- Implements algorithm for creating circular masks with configurable radius
- Optimizes performance for large images using caching
- Adds type hints and comprehensive documentation
```

## Code Style Compliance

AI agents must follow the project's code style guidelines:

1. **Follow PEP 8** for Python code
2. **Use type annotations** throughout
3. **Include docstrings** for all classes and functions
4. **Follow the import guidelines** (GTK first, then standard library, then app modules)
5. **Use spaces, not tabs** for indentation (4 spaces for Python)

## Testing Requirements for AI-Generated Code

All code generated by AI agents must include appropriate tests:

1. **Unit tests** for specific functions and methods
2. **Integration tests** for component interactions
3. **UI tests** for user interface components, including headless test mode
4. **Ensure tests run in Docker** environment

Example:
```python
def test_circular_mask_generation():
    """Test that the circular mask generator works correctly."""
    processor = ImageProcessor()
    mask = processor.generate_circular_mask(radius=50)

    # Assert mask has correct dimensions
    assert mask.size == (100, 100)

    # Assert mask is circular
    center = mask.size[0] // 2
    assert mask.getpixel((center, center)) == 255  # Center is white
    assert mask.getpixel((0, 0)) == 0  # Corner is black
```

## Documentation Requirements

AI agents should update or create documentation when:

1. **Adding new functionality**
2. **Changing existing behavior**
3. **Updating dependencies**
4. **Fixing bugs with user-visible impact**

Documentation should include:
- Purpose and usage examples
- Parameter descriptions
- Return value explanations
- Exception cases

## Interaction with Human Reviewers

When a human reviews AI-generated PRs:

1. **Respond to feedback** by creating additional commits addressing the feedback
2. **Explain reasoning** behind implementation choices when asked
3. **Suggest alternatives** if the initial approach has issues

## Monitoring and Tracking

AI agents should track their contributions to the project:

1. **Maintain a list of created issues**
2. **Track open pull requests**
3. **Follow up on feedback** and review comments

## AI Agent Responsibility Boundaries

AI agents should:

1. **NOT modify protected branches** directly (main, develop)
2. **NOT modify critical infrastructure** without human review
3. **NOT modify deployment configurations** without explicit approval
4. **NOT create releases** (human approval required)

## Best Practices for AI-Human Collaboration

1. **Clearly label AI contributions** in commit messages or PR descriptions
2. **Document complex logic** with comments explaining the reasoning
3. **Prefer multiple small, focused PRs** over large, monolithic changes
4. **Link PRs to issues** they address

## Troubleshooting Common Issues

### API Rate Limiting

If encountering API rate limits:
- Implement exponential backoff between requests
- Batch changes to minimize API calls
- Use conditional requests where appropriate

### Branch Conflicts

When merge conflicts occur:
1. Fetch latest changes from target branch
2. Resolve conflicts locally
3. Push updated branch
4. Update the PR

### Permission Issues

If lacking permissions for specific operations:
1. Document the intended changes
2. Request assistance from a repository administrator

## Conclusion

Following these guidelines ensures that AI agents contribute effectively to the Preview Maker project while maintaining code quality standards and adhering to the established Git workflow.

For additional details, refer to:
- [GitHub CLI Guide](github_cli_guide.md)
- [Git Workflow](../rebuild_plan/git_workflow.md)
- [Branch Protection Rules](branch_protection_rules.md)