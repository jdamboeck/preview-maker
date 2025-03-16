# Git Workflow for Preview Maker

This document outlines the Git workflow for the Preview Maker project, providing guidelines for branching, committing, testing, and merging changes.

## Repository Structure

The Preview Maker project uses the following repository:

- **GitHub Repository**: [https://github.com/jdamboeck/preview-maker](https://github.com/jdamboeck/preview-maker)
- **Main Branch**: `main` - Contains the stable, production-ready code
- **Development Branch**: `develop` - Integration branch for feature development

## Preferred Tools

For all Git operations, we recommend using GitHub CLI (`gh`) or GitHub MCP functions over direct Git commands:

- **GitHub CLI**: Command-line tool that brings GitHub to your terminal
- **GitHub MCP Functions**: Functions for GitHub operations in supported environments
- **Direct Git**: Use only for local operations when GitHub CLI is unavailable

For a comprehensive guide on GitHub CLI usage, see [docs/github_cli_guide.md](../docs/github_cli_guide.md).

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

```bash
# Start from the develop branch
gh api repos/jdamboeck/preview-maker/git/refs/heads/develop --jq '.object.sha'

# Create a feature branch
gh api repos/jdamboeck/preview-maker/git/refs -f ref="refs/heads/feature/image-processor" \
  -f sha="$(gh api repos/jdamboeck/preview-maker/git/refs/heads/develop --jq '.object.sha')"
git fetch
git checkout feature/image-processor

# Work on your feature with regular commits
# ...make changes...
git add .
git commit -m "feat: Add circular mask generation function"

# Push your branch to the remote repository
gh pr create --base develop --title "feat: Add circular mask generation" \
  --body "Implements algorithm for creating circular masks with adjustable parameters."
```

### Code Review Process

1. Create a Pull Request (PR) from your feature branch to the develop branch:
   ```bash
   gh pr create --base develop --title "feat: Add image processor" \
     --body "Implements circular mask generation functionality"
   ```

2. Ensure all tests pass in the PR:
   ```bash
   gh pr checks
   ```

3. Request code review from at least one team member:
   ```bash
   gh pr edit --add-reviewer username
   ```

4. Address review comments with additional commits
5. Once approved, merge the PR:
   ```bash
   gh pr merge --merge --delete-branch
   ```

### Testing Requirements

Before merging to develop:
- All unit tests must pass
- Integration tests must pass
- Docker-based tests must run successfully

```bash
# Run tests before creating PR
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test
```

### Merging Strategy

We use non-fast-forward merges to maintain a clear history:

```bash
# For merging feature branches into develop
gh pr merge --merge --delete-branch
```

### Release Process

```bash
# Create a release branch from develop
gh api repos/jdamboeck/preview-maker/git/refs -f ref="refs/heads/release/v1.0.0" \
  -f sha="$(gh api repos/jdamboeck/preview-maker/git/refs/heads/develop --jq '.object.sha')"
git fetch
git checkout release/v1.0.0

# Final testing and bug fixes on the release branch
# ...make changes...
git commit -m "fix: Final issues for v1.0.0"

# Create PR to main when ready
gh pr create --base main --title "release: v1.0.0" \
  --body "Release version 1.0.0"

# After PR is approved and merged, create the release
gh release create v1.0.0 --title "Version 1.0.0" \
  --notes "See CHANGELOG.md for details" --target main

# Also create PR to merge back to develop
gh pr create --base develop --head main --title "chore: Sync release to develop" \
  --body "Brings release changes back to develop branch"
```

### Hotfix Process

```bash
# Create hotfix branch from main
gh api repos/jdamboeck/preview-maker/git/refs -f ref="refs/heads/hotfix/critical-bug-fix" \
  -f sha="$(gh api repos/jdamboeck/preview-maker/git/refs/heads/main --jq '.object.sha')"
git fetch
git checkout hotfix/critical-bug-fix

# Fix the issue
# ...make changes...
git commit -m "fix: Critical bug in production"

# Create PR to main
gh pr create --base main --title "fix: Critical production bug" \
  --body "Fixes critical issue in production"

# After PR is approved and merged, create the patch release
gh release create v1.0.1 --title "Hotfix v1.0.1" \
  --notes "Emergency fix for critical issue" --target main

# Also create PR to merge to develop
gh pr create --base develop --head main --title "fix: Sync hotfix to develop" \
  --body "Brings hotfix from main into develop"
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

To set up pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

## GitHub MCP Functions

When working in environments that support MCP functions, use them for GitHub operations:

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

// Create a new issue
mcp_github_create_issue({
  owner: "jdamboeck",
  repo: "preview-maker",
  title: "bug: Something is broken",
  body: "When I do X, Y happens instead of Z",
  labels: ["bug", "priority-high"]
});
```

## Repository Setup for New Contributors

```bash
# Clone the repository using GitHub CLI
gh repo clone jdamboeck/preview-maker
cd preview-maker

# Set up your environment
docker-compose -f rebuild_plan/docker/docker-compose.yml build
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm verify
```

## Common GitHub CLI Commands

### Check Repository Status
```bash
gh repo view
```

### Create Branch
```bash
gh api repos/jdamboeck/preview-maker/git/refs -f ref="refs/heads/feature/my-feature" \
  -f sha="$(gh api repos/jdamboeck/preview-maker/git/refs/heads/develop --jq '.object.sha')"
```

### List Pull Requests
```bash
gh pr list
```

### View Issues
```bash
gh issue list
```

### View Commit History
```bash
gh api repos/jdamboeck/preview-maker/commits --jq '.[] | [.sha[0:7], .commit.message] | join(" ")'
```

## Branch Protection Rules

We enforce branch protection rules for the `main` and `develop` branches:

1. Require pull request reviews before merging
2. Require status checks to pass before merging
3. Require branches to be up to date before merging
4. Prohibit force pushes and deletion of protected branches
5. Include administrators in these restrictions

For more information, see [docs/branch_protection_rules.md](../docs/branch_protection_rules.md).