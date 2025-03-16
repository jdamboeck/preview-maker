# Git Workflow for Preview Maker

This document outlines the Git workflow for the Preview Maker project, providing guidelines for branching, committing, testing, and merging changes.

## Repository Structure

The Preview Maker project uses the following repository:

- **GitHub Repository**: [https://github.com/jdamboeck/preview-maker](https://github.com/jdamboeck/preview-maker)
- **Main Branch**: `main` - Contains the stable, production-ready code
- **Development Branch**: `develop` - Integration branch for feature development

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
git checkout develop
git pull origin develop

# Create a feature branch
git checkout -b feature/image-processor

# Work on your feature with regular commits
# ...make changes...
git add .
git commit -m "feat: Add circular mask generation function"

# Push your branch to the remote repository
git push -u origin feature/image-processor
```

### Code Review Process

1. Create a Pull Request (PR) from your feature branch to the develop branch
2. Ensure all tests pass in the PR
3. Request code review from at least one team member
4. Address review comments with additional commits
5. Once approved, merge the PR

Using GitHub CLI for PR creation:
```bash
# Create PR from current branch to develop
gh pr create --base develop --title "feat: Add circular mask generation" --body "Implements mask creation with Pillow"

# List open PRs
gh pr list

# Check out a PR locally
gh pr checkout 123

# View a specific PR
gh pr view 123

# Add a reviewer to a PR
gh pr edit 123 --add-reviewer username
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
# Using Git CLI
# For merging feature branches into develop
git checkout develop
git merge --no-ff feature/image-processor
git push origin develop

# Using GitHub CLI
# Approve and merge a PR
gh pr review 123 --approve
gh pr merge 123 --merge --delete-branch
```

### Release Process

```bash
# Create a release branch from develop
git checkout develop
git checkout -b release/v1.0.0

# Final testing and bug fixes on the release branch
# ...make changes...
git commit -m "fix: Final issues for v1.0.0"

# Merge to main when ready
git checkout main
git merge --no-ff release/v1.0.0
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin main --tags

# Also merge back to develop
git checkout develop
git merge --no-ff release/v1.0.0
git push origin develop

# Using GitHub CLI to create a release
gh release create v1.0.0 --title "v1.0.0" --notes "Release notes for version 1.0.0"
```

### Hotfix Process

```bash
# Create hotfix branch from main
git checkout main
git checkout -b hotfix/critical-bug-fix

# Fix the issue
# ...make changes...
git commit -m "fix: Critical bug in production"

# Merge to main
git checkout main
git merge --no-ff hotfix/critical-bug-fix
git tag -a v1.0.1 -m "Version 1.0.1"
git push origin main --tags

# Also merge to develop
git checkout develop
git merge --no-ff hotfix/critical-bug-fix
git push origin develop
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

## Issue Management

Using GitHub CLI for issue management:

```bash
# Create a new issue
gh issue create --title "Bug: Overlay not showing in dark mode" --body "The circular overlay is not visible when dark mode is enabled"

# List open issues
gh issue list

# View a specific issue
gh issue view 123

# Close an issue
gh issue close 123 --reason "completed"

# Assign an issue
gh issue edit 123 --add-assignee username
```

## Git Hooks

Consider using pre-commit hooks to ensure:
- Code passes linting
- Tests pass before committing
- No debug code is committed
- Commit messages follow guidelines

Sample `.pre-commit-config.yaml` configuration:
```yaml
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files

-   repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
    -   id: flake8
        args: [--max-line-length=88]

-   repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
    -   id: isort

-   repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
    -   id: black
        args: [--line-length=88]
```

## Repository Setup for New Contributors

```bash
# Clone the repository
git clone https://github.com/jdamboeck/preview-maker.git
cd preview-maker

# Set up your environment
docker-compose -f rebuild_plan/docker/docker-compose.yml build
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm verify

# Set up pre-commit hooks
pip install pre-commit
pre-commit install
```

## Common Git Commands

### Check Status
```bash
git status
```

### Create Branch
```bash
git checkout -b feature/my-feature
```

### Update from Remote
```bash
git pull origin branch-name
```

### Discard Working Changes
```bash
git checkout -- file-name
```

### Show Commit History
```bash
git log --oneline --graph --decorate
```

## Common GitHub CLI Commands

### Authentication
```bash
# Login to GitHub
gh auth login
```

### Repository Management
```bash
# Clone a repository
gh repo clone jdamboeck/preview-maker

# View repository details
gh repo view jdamboeck/preview-maker
```

### Workflow Management
```bash
# Create a branch
gh repo fork --clone=true
gh repo sync

# Check PR status
gh pr status

# List all pending reviews requested from you
gh pr list --search "review-requested:@me"
```

## Templates and Automation

The Preview Maker repository includes:

1. Pull Request Template: `.github/PULL_REQUEST_TEMPLATE.md`
2. Issue Templates:
   - Bug Report: `.github/ISSUE_TEMPLATE/bug_report.md`
   - Feature Request: `.github/ISSUE_TEMPLATE/feature_request.md`
   - Documentation Update: `.github/ISSUE_TEMPLATE/documentation_update.md`

These templates ensure consistent information is provided for all contributions.