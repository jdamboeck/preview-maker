# GitHub CLI Guide for Preview Maker

This guide provides instructions for using GitHub CLI (`gh`) for the Preview Maker project. Using GitHub CLI is preferred over direct Git commands for better integration with GitHub workflows.

## Installation

### Linux
```bash
# Ubuntu/Debian
sudo apt install gh

# Fedora
sudo dnf install gh

# Arch Linux
sudo pacman -S github-cli
```

### macOS
```bash
brew install gh
```

### Windows
```bash
winget install GitHub.cli
# or
choco install gh
```

## Authentication

Before using GitHub CLI, authenticate with your GitHub account:

```bash
gh auth login
```

Follow the interactive prompts to complete authentication.

## Core Workflows

### Repository Setup

Clone the Preview Maker repository:
```bash
gh repo clone jdamboeck/preview-maker
cd preview-maker
```

### Branch Management

List all branches:
```bash
gh api repos/jdamboeck/preview-maker/branches --jq '.[].name'
```

Create and checkout a new branch:
```bash
# Create feature branch from develop
gh api repos/jdamboeck/preview-maker/git/refs -f ref="refs/heads/feature/new-feature" \
  -f sha="$(gh api repos/jdamboeck/preview-maker/git/refs/heads/develop --jq '.object.sha')"

# Checkout locally
gh repo clone jdamboeck/preview-maker -b feature/new-feature
# or if already cloned
git fetch
git checkout feature/new-feature
```

### Pull Request Workflow

Create a Pull Request:
```bash
gh pr create --base develop --title "feat: Add circular mask generation" \
  --body "Implements algorithm for creating circular masks with adjustable parameters."
```

List open Pull Requests:
```bash
gh pr list
```

Check out a Pull Request to review locally:
```bash
gh pr checkout 123
```

View PR details:
```bash
gh pr view 123
```

Check PR status (CI checks):
```bash
gh pr checks 123
```

Review a PR:
```bash
gh pr review 123 --approve --body "Looks good to me!"
# or
gh pr review 123 --request-changes --body "Please fix these issues..."
```

Merge an approved PR (with non-fast-forward merge):
```bash
gh pr merge 123 --merge --delete-branch
```

### Issue Management

Create an issue:
```bash
gh issue create --title "bug: Overlay not rendering correctly" \
  --body "When using dark mode, the circular overlay becomes invisible."
```

List open issues:
```bash
gh issue list
```

View issue details:
```bash
gh issue view 456
```

Create a branch to work on an issue:
```bash
gh issue develop 456 -b feature/fix-overlay-visibility
```

Close an issue:
```bash
gh issue close 456 --reason completed
```

Add labels to an issue:
```bash
gh issue edit 456 --add-label "priority-high,ui"
```

### Workflow Patterns

#### Feature Development Workflow

```bash
# Start from develop branch
gh api repos/jdamboeck/preview-maker/git/refs/heads/develop --jq '.object.sha'
gh api repos/jdamboeck/preview-maker/git/refs -f ref="refs/heads/feature/my-feature" \
  -f sha="$(gh api repos/jdamboeck/preview-maker/git/refs/heads/develop --jq '.object.sha')"
git fetch
git checkout feature/my-feature

# Develop your feature with regular commits (using standard git for local commits)
# ...

# Create PR when ready
gh pr create --base develop --title "feat: Implement feature" \
  --body "Adds new functionality for...\n\nCloses #123"
```

#### Release Workflow

```bash
# Create release branch from develop
gh api repos/jdamboeck/preview-maker/git/refs -f ref="refs/heads/release/v1.0.0" \
  -f sha="$(gh api repos/jdamboeck/preview-maker/git/refs/heads/develop --jq '.object.sha')"
git fetch
git checkout release/v1.0.0

# Make final release adjustments
# ...

# Create PR to main
gh pr create --base main --title "release: v1.0.0" \
  --body "Release version 1.0.0"

# After PR is approved and merged
# Create the release
gh release create v1.0.0 --title "Release v1.0.0" \
  --notes "See CHANGELOG.md for details" --target main
```

#### Hotfix Workflow

```bash
# Create hotfix branch from main
gh api repos/jdamboeck/preview-maker/git/refs -f ref="refs/heads/hotfix/critical-fix" \
  -f sha="$(gh api repos/jdamboeck/preview-maker/git/refs/heads/main --jq '.object.sha')"
git fetch
git checkout hotfix/critical-fix

# Make hotfix changes
# ...

# Create PR to main
gh pr create --base main --title "fix: Critical production bug" \
  --body "Fixes critical issue in production"

# After PR is approved and merged
# Create the patch release
gh release create v1.0.1 --title "Hotfix v1.0.1" \
  --notes "Emergency fix for..." --target main

# Create PR to merge hotfix into develop
gh pr create --base develop --head main --title "fix: Sync hotfix to develop" \
  --body "Brings hotfix from main into develop"
```

## GitHub MCP Function Usage

For systems with MCP GitHub functions available, these are preferred over direct GitHub CLI commands:

```javascript
// Create or update a file
mcp_github_create_or_update_file({
  owner: "jdamboeck",
  repo: "preview-maker",
  path: "path/to/file.md",
  content: "File content here",
  message: "docs: Update documentation",
  branch: "feature/my-feature"
});

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

## Environment Specific Commands

### Using with Docker Development Environment

When working inside the Docker environment, you can combine GitHub CLI with Docker:

```bash
# Run command in Docker environment
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker \
  gh pr view 123
```

## Best Practices

1. **Always pull before creating branches**:
   ```bash
   git pull origin develop
   ```

2. **Keep commits atomic and well-described**:
   - Use prefix conventions: `feat:`, `fix:`, `docs:`, etc.
   - Keep first line under 50 characters
   - Add detailed description for complex changes

3. **Reference issues in PRs and commits**:
   - Use keywords like "Closes #123" or "Fixes #123" to automatically close issues when merged

4. **Use specialized merge options**:
   ```bash
   gh pr merge 123 --merge --delete-branch
   ```

5. **Regularly sync with develop branch**:
   ```bash
   git fetch origin develop
   git merge origin/develop
   ```

6. **Utilize PR templates**:
   - GitHub CLI will automatically use PR templates from the repository

## Troubleshooting

### Authentication Issues
```bash
gh auth status
gh auth refresh
```

### API Rate Limiting
If you encounter GitHub API rate limits, consider:
```bash
gh auth status
# Check if you're authenticated
```

### Common Error Resolution
```bash
# Force refresh local repository state
git fetch --all
git reset --hard origin/[your-branch-name]
```

## Further Resources

- [GitHub CLI Official Documentation](https://cli.github.com/manual/)
- [GitHub Flow Guide](https://docs.github.com/en/get-started/quickstart/github-flow)
- [GitHub CLI API Documentation](https://cli.github.com/manual/gh_api)
- [Preview Maker Git Workflow](../rebuild_plan/git_workflow.md)