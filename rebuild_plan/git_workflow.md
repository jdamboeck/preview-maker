# Git Workflow for Preview Maker

This document outlines the Git workflow for the Preview Maker project, providing guidelines for branching, committing, testing, and merging changes.

## Repository Structure

The Preview Maker project uses the following repository:

- **GitHub Repository**: [https://github.com/jdamboeck/preview-maker](https://github.com/jdamboeck/preview-maker)
- **Main Branch**: `main` - Contains the stable, production-ready code
- **Development Branch**: `develop` - Integration branch for feature development

## Preferred Tools

For all repository operations, use tools in this priority order:

1. **MCP GitHub Functions**: Always use these as the first choice (see [MCP Tools Reference](../docs/mcp_tools_reference.md))
2. **Non-interactive GitHub CLI API commands**: Use only when MCP functions don't exist for a specific operation
3. **Direct Git commands**: Avoid these entirely when possible

For a comprehensive guide on available tools:
- [MCP Tools Reference](../docs/mcp_tools_reference.md): Complete reference for all MCP functions
- [GitHub CLI Guide](../docs/github_cli_guide.md): Non-interactive GitHub CLI commands
- [GitHub CLI Caveats and Solutions](../docs/github_cli_caveats.md): Common issues and tested solutions

## Branching Strategy

We follow a modified GitFlow workflow with these branch types:

### Core Branches

- **main**: Production-ready code, always stable
- **develop**: Integration branch, contains features ready for testing

### Supporting Branches

- **feature/<feature-name>**: For new features and non-urgent enhancements
- **bugfix/<bug-description>**: For fixes to bugs found in develop
- **hotfix/<hotfix-description>**: For urgent fixes to production issues
- **release/<version>**: For final testing before a release

## Workflow Guidelines

### Feature Development

#### Using MCP Functions (Preferred)

```javascript
// 1. Create a feature branch from develop
mcp_github_create_branch({
  owner: "jdamboeck",
  repo: "preview-maker",
  branch: "feature/image-processor",
  from_branch: "develop"
});

// 2. Create or update multiple files in one commit
mcp_github_push_files({
  owner: "jdamboeck",
  repo: "preview-maker",
  branch: "feature/image-processor",
  message: "feat: Add circular mask generation function",
  files: [
    {
      path: "app/components/image_processor.py",
      content: "# Implementation of image processor\n\nclass ImageProcessor:\n    ..."
    },
    {
      path: "tests/test_image_processor.py",
      content: "# Tests for image processor\n\nimport pytest\n\ndef test_circular_mask():\n    ..."
    }
  ]
});

// 3. Create a pull request to develop
mcp_github_create_pull_request({
  owner: "jdamboeck",
  repo: "preview-maker",
  title: "feat: Add circular mask generation",
  body: "Implements algorithm for creating circular masks with adjustable parameters.",
  head: "feature/image-processor",
  base: "develop"
});
```

#### Using GitHub CLI API (Alternative)

For complex GitHub CLI operations, we provide helper scripts to simplify the process:

**Option 1: Use the bash helper script**
```bash
# Source the helper script
source scripts/github_cli_workflow_helpers.sh

# Create a branch
create_branch jdamboeck preview-maker feature/image-processor develop

# Create files (handles content encoding properly)
create_file jdamboeck preview-maker app/components/image_processor.py "# Implementation of image processor\n\nclass ImageProcessor:\n    ..." feature/image-processor "feat: Add image processor implementation"

# Create PR with proper body formatting
create_pr jdamboeck preview-maker "feat: Add circular mask generation" "Implements algorithm for creating circular masks with adjustable parameters." feature/image-processor develop
```

**Option 2: Manual bash commands (for simpler operations)**
```bash
# 1. Create a feature branch from develop (non-interactive)
head_sha=$(gh api repos/jdamboeck/preview-maker/git/refs/heads/develop --jq '.object.sha')
gh api repos/jdamboeck/preview-maker/git/refs -f ref="refs/heads/feature/image-processor" \
  -f sha="$head_sha"

# 2. Create file with proper content encoding
echo -n "# Implementation of image processor\n\nclass ImageProcessor:\n    ..." | base64 -w0 > /tmp/content.txt
gh api repos/jdamboeck/preview-maker/contents/app/components/image_processor.py -X PUT \
  -f message="feat: Add image processor implementation" \
  -f content="$(cat /tmp/content.txt)" \
  -f branch="feature/image-processor" | cat

# 3. Create a pull request (non-interactive)
gh api repos/jdamboeck/preview-maker/pulls -f title="feat: Add circular mask generation" \
  -f body="Implements algorithm for creating circular masks with adjustable parameters." \
  -f head="feature/image-processor" \
  -f base="develop" | cat
```

**Important Caveats:**
- Multi-line commands must be combined with `&&` or written to a script
- Content with special characters requires proper escaping or temp file approach
- See [GitHub CLI Caveats and Solutions](../docs/github_cli_caveats.md) for detailed solutions

### Code Review Process

#### Using MCP Functions (Preferred)

```javascript
// 1. Create a pull request
mcp_github_create_pull_request({
  owner: "jdamboeck",
  repo: "preview-maker",
  title: "feat: Add image processor",
  body: "Implements circular mask generation functionality",
  head: "feature/image-processor",
  base: "develop"
});

// 2. Add a comment to the PR discussing review comments
mcp_github_add_issue_comment({
  owner: "jdamboeck",
  repo: "preview-maker",
  issue_number: 123, // PR number
  body: "I've addressed the review comments by refactoring the mask generation function."
});
```

#### Using GitHub CLI API (Alternative)

```bash
# 1. Create a pull request (non-interactive)
gh api repos/jdamboeck/preview-maker/pulls -f title="feat: Add image processor" \
  -f body="Implements circular mask generation functionality" \
  -f head="feature/image-processor" \
  -f base="develop" | cat

# 2. Check PR status (non-interactive)
gh api repos/jdamboeck/preview-maker/pulls/123/checks --jq '.check_runs[] | {name, status, conclusion}' | cat

# 3. Add reviewers (non-interactive)
gh api repos/jdamboeck/preview-maker/pulls/123 -X PATCH -f reviewers='["username"]' | cat

# 4. Merge the PR when approved (non-interactive)
gh api repos/jdamboeck/preview-maker/pulls/123/merge -X PUT -f merge_method="merge" | cat

# 5. Delete the branch after merging (non-interactive)
gh api repos/jdamboeck/preview-maker/git/refs/heads/feature/image-processor -X DELETE | cat
```

### Testing Requirements

Before creating a PR, ensure all tests pass in the Docker environment:

```bash
# Run tests in Docker (non-interactive)
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/ -v | cat
```

### Merging Strategy

We use non-fast-forward merges to maintain a clear history:

#### Using MCP Functions

No direct merge function in MCP, use GitHub CLI API instead.

#### Using GitHub CLI API

```bash
# Merge PR non-interactively with merge commit
gh api repos/jdamboeck/preview-maker/pulls/123/merge -X PUT -f merge_method="merge" | cat

# Delete branch after successful merge
gh api repos/jdamboeck/preview-maker/git/refs/heads/feature/image-processor -X DELETE | cat
```

### Release Process

#### Using MCP Functions (Preferred)

```javascript
// 1. Create a release branch from develop
mcp_github_create_branch({
  owner: "jdamboeck",
  repo: "preview-maker",
  branch: "release/v1.0.0",
  from_branch: "develop"
});

// 2. Make final fixes if needed
mcp_github_create_or_update_file({
  owner: "jdamboeck",
  repo: "preview-maker",
  path: "VERSION",
  message: "chore: Update version to 1.0.0",
  content: "1.0.0",
  branch: "release/v1.0.0"
});

// 3. Create PR to main
mcp_github_create_pull_request({
  owner: "jdamboeck",
  repo: "preview-maker",
  title: "release: v1.0.0",
  body: "Release version 1.0.0",
  head: "release/v1.0.0",
  base: "main"
});

// 4. Create PR to sync back to develop after main merge
mcp_github_create_pull_request({
  owner: "jdamboeck",
  repo: "preview-maker",
  title: "chore: Sync release to develop",
  body: "Brings release changes back to develop branch",
  head: "main",
  base: "develop"
});
```

#### Using GitHub CLI API (Alternative)

```bash
# 1. Create a release branch from develop (non-interactive)
head_sha=$(gh api repos/jdamboeck/preview-maker/git/refs/heads/develop --jq '.object.sha')
gh api repos/jdamboeck/preview-maker/git/refs -f ref="refs/heads/release/v1.0.0" \
  -f sha="$head_sha" | cat

# 2. Create PR to main when ready (non-interactive)
gh api repos/jdamboeck/preview-maker/pulls -f title="release: v1.0.0" \
  -f body="Release version 1.0.0" \
  -f head="release/v1.0.0" \
  -f base="main" | cat

# 3. After PR is approved and merged, create the release (non-interactive)
gh api repos/jdamboeck/preview-maker/releases -f tag_name="v1.0.0" \
  -f name="Version 1.0.0" \
  -f body="See CHANGELOG.md for details" \
  -f target_commitish="main" | cat

# 4. Create PR to merge back to develop (non-interactive)
gh api repos/jdamboeck/preview-maker/pulls -f title="chore: Sync release to develop" \
  -f body="Brings release changes back to develop branch" \
  -f head="main" \
  -f base="develop" | cat
```

### Hotfix Process

#### Using MCP Functions (Preferred)

```javascript
// 1. Create hotfix branch from main
mcp_github_create_branch({
  owner: "jdamboeck",
  repo: "preview-maker",
  branch: "hotfix/critical-bug-fix",
  from_branch: "main"
});

// 2. Make the fix
mcp_github_create_or_update_file({
  owner: "jdamboeck",
  repo: "preview-maker",
  path: "app/components/buggy_component.py",
  message: "fix: Critical bug in production",
  content: "# Fixed implementation...",
  branch: "hotfix/critical-bug-fix"
});

// 3. Create PR to main
mcp_github_create_pull_request({
  owner: "jdamboeck",
  repo: "preview-maker",
  title: "fix: Critical production bug",
  body: "Fixes critical issue in production",
  head: "hotfix/critical-bug-fix",
  base: "main"
});
```

#### Using GitHub CLI API (Alternative)

```bash
# 1. Create hotfix branch from main (non-interactive)
head_sha=$(gh api repos/jdamboeck/preview-maker/git/refs/heads/main --jq '.object.sha')
gh api repos/jdamboeck/preview-maker/git/refs -f ref="refs/heads/hotfix/critical-bug-fix" \
  -f sha="$head_sha" | cat

# 2. Create PR to main (non-interactive)
gh api repos/jdamboeck/preview-maker/pulls -f title="fix: Critical production bug" \
  -f body="Fixes critical issue in production" \
  -f head="hotfix/critical-bug-fix" \
  -f base="main" | cat

# 3. After PR is approved and merged, create the patch release (non-interactive)
gh api repos/jdamboeck/preview-maker/releases -f tag_name="v1.0.1" \
  -f name="Hotfix v1.0.1" \
  -f body="Emergency fix for critical issue" \
  -f target_commitish="main" | cat

# 4. Create PR to merge to develop (non-interactive)
gh api repos/jdamboeck/preview-maker/pulls -f title="fix: Sync hotfix to develop" \
  -f body="Brings hotfix from main into develop" \
  -f head="main" \
  -f base="develop" | cat
```

## Commit Message Guidelines

Follow these guidelines for commit messages:

1. Use the imperative mood ("Add feature" not "Added feature")
2. Start with a capital letter
3. Keep the first line under 50 characters
4. Include a detailed description after the first line if needed
5. Use prefixes for clarity:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Formatting, linting, etc. (no code change)
   - `refactor:` - Code refactoring
   - `test:` - Tests
   - `chore:` - Maintenance tasks

Example:
```
feat: Add circular mask generation function

- Implements algorithm for creating circular masks
- Adds unit tests for mask generation
- Optimizes performance for large images
```

## Pre-commit Hooks

We use pre-commit hooks to ensure:
- Code passes linting
- Tests pass before committing
- No debug code is committed
- Commit messages follow guidelines

To set up pre-commit hooks in the development environment:
```bash
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker pip install pre-commit
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker pre-commit install
```

## Helper Scripts

To simplify complex GitHub CLI operations, we provide two helper scripts:

1. **Bash Helper Script** (`scripts/github_cli_workflow_helpers.sh`):
   - Provides functions for common GitHub operations
   - Handles content encoding and special characters
   - Simplifies multi-step processes

2. **Python Helper Script** (`scripts/github_cli_helpers.py`):
   - Generates properly formatted GitHub CLI commands
   - Helps with complex content escaping
   - Useful for programmatic GitHub operations

See [GitHub CLI Caveats and Solutions](../docs/github_cli_caveats.md) for detailed usage examples.

## Common Operations Reference

### Repository Setup for New Contributors

```bash
# Clone the repository using GitHub CLI (non-interactive)
gh repo clone jdamboeck/preview-maker -- -q
cd preview-maker

# Set up your environment (non-interactive)
docker-compose -f rebuild_plan/docker/docker-compose.yml build
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm verify | cat
```

### Common GitHub Operations

#### Using MCP Functions (Preferred)

```javascript
// Get file contents
mcp_github_get_file_contents({
  owner: "jdamboeck",
  repo: "preview-maker",
  path: "README.md",
  branch: "develop"
});

// Create an issue
mcp_github_create_issue({
  owner: "jdamboeck",
  repo: "preview-maker",
  title: "bug: Something is broken",
  body: "When I do X, Y happens instead of Z",
  labels: ["bug", "priority-high"]
});

// Push multiple files in one commit
mcp_github_push_files({
  owner: "jdamboeck",
  repo: "preview-maker",
  branch: "feature/my-feature",
  message: "feat: Implement new feature",
  files: [
    { path: "file1.py", content: "content1" },
    { path: "file2.py", content: "content2" }
  ]
});
```

#### Using GitHub CLI API (Alternative)

```bash
# Get repository info (non-interactive)
gh api repos/jdamboeck/preview-maker --jq '{name, description, default_branch}' | cat

# List branches (non-interactive)
gh api repos/jdamboeck/preview-maker/branches --jq '.[] | {name, protected}' | cat

# List pull requests (non-interactive)
gh api repos/jdamboeck/preview-maker/pulls --jq '.[] | {number, title, state}' | cat

# List issues (non-interactive)
gh api repos/jdamboeck/preview-maker/issues --jq '.[] | {number, title, state}' | cat

# Get file content (non-interactive)
gh api repos/jdamboeck/preview-maker/contents/README.md --jq '.content' | base64 -d | cat
```

## Best Practices

1. **Always use MCP functions first** when available
2. **Only use non-interactive commands** that won't prompt for input
3. **Avoid direct Git commands** entirely when possible
4. **Append `| cat` to any command** that might launch a pager
5. **Prefer atomic operations** that accomplish multiple steps at once
6. **Use descriptive commit messages** that follow the guidelines
7. **Create comprehensive PR descriptions** to facilitate review
8. **Run tests in Docker** before creating PRs
9. **Document all MCP tool usage** in PR descriptions
10. **Use helper scripts for complex operations** instead of writing complex commands directly
11. **For multi-line content in GitHub CLI commands**, write to temp files or use proper escaping techniques (see [GitHub CLI Caveats](../docs/github_cli_caveats.md))