# Git Workflow for Preview Maker

This document outlines the Git workflow for the Preview Maker project, providing guidelines for branching, committing, testing, and merging changes.

## Repository Structure

The Preview Maker project uses the following repository:

- **GitHub Repository**: [https://github.com/jdenen/preview-maker](https://github.com/jdenen/preview-maker)
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

```
# Start from the develop branch
git checkout develop
git pull origin develop

# Create a feature branch
git checkout -b feature/image-processor

# Work on your feature with regular commits
# ...make changes...
git add .
git commit -m "Add circular mask generation function"

# Push your branch to the remote repository
git push -u origin feature/image-processor
```

### Code Review Process

1. Create a Pull Request (PR) from your feature branch to the develop branch
2. Ensure all tests pass in the PR
3. Request code review from at least one team member
4. Address review comments with additional commits
5. Once approved, merge the PR

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
git checkout develop
git merge --no-ff feature/image-processor
git push origin develop
```

### Release Process

```bash
# Create a release branch from develop
git checkout develop
git checkout -b release/v1.0.0

# Final testing and bug fixes on the release branch
# ...make changes...
git commit -m "Fix final issues for v1.0.0"

# Merge to main when ready
git checkout main
git merge --no-ff release/v1.0.0
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin main --tags

# Also merge back to develop
git checkout develop
git merge --no-ff release/v1.0.0
git push origin develop
```

### Hotfix Process

```bash
# Create hotfix branch from main
git checkout main
git checkout -b hotfix/critical-bug-fix

# Fix the issue
# ...make changes...
git commit -m "Fix critical bug in production"

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

## Git Hooks

Consider using pre-commit hooks to ensure:
- Code passes linting
- Tests pass before committing
- No debug code is committed
- Commit messages follow guidelines

## Repository Setup for New Contributors

```bash
# Clone the repository
git clone https://github.com/jdenen/preview-maker.git
cd preview-maker

# Set up your environment
docker-compose -f rebuild_plan/docker/docker-compose.yml build
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm verify
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