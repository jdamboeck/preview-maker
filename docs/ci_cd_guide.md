# Continuous Integration and Deployment Guide

This guide outlines the CI/CD workflows implemented for the Preview Maker project using GitHub Actions.

## Overview

Preview Maker uses GitHub Actions for automating testing, linting, security scanning, and release processes. These workflows help maintain code quality and ensure a smooth development process.

## Implemented Workflows

### PR Validation Workflow

**File**: `.github/workflows/pr-validation.yml`

This workflow runs on pull requests to `develop` and `main` branches, as well as pushes to feature branches.

**Jobs**:
1. **lint**: Runs code quality checks using pre-commit hooks
2. **test**: Runs tests using Docker
3. **verify-docs**: Verifies documentation integrity

**When it runs**:
- When a pull request is opened or updated
- When changes are pushed to feature branches

**Usage for developers**:
- Ensure your code passes all pre-commit checks locally before pushing
- Address any issues flagged by the CI workflow
- Pull requests cannot be merged until all checks pass

### Release Workflow

**File**: `.github/workflows/release.yml`

This workflow automates the release process when a new tag is pushed.

**Jobs**:
1. **build**: Builds the package and creates a GitHub release

**When it runs**:
- When a tag matching the pattern `v*.*.*` is pushed

**Usage for release managers**:
```bash
# Tag the release
git tag -a v1.0.0 -m "Version 1.0.0"

# Push the tag
git push origin v1.0.0
```

### Branch Cleanup Workflow

**File**: `.github/workflows/branch-cleanup.yml`

This workflow automatically deletes branches after their pull requests are merged.

**Jobs**:
1. **delete_branch**: Deletes the branch after PR is merged

**When it runs**:
- When a pull request is closed
- Only if the PR was merged
- Excludes release branches

**Note**: This helps keep the repository clean by automatically removing branches that are no longer needed.

### Security Scan Workflow

**File**: `.github/workflows/security-scan.yml`

This workflow scans dependencies and code for security vulnerabilities.

**Jobs**:
1. **dependency-scan**: Checks dependencies for known vulnerabilities
2. **code-scan**: Analyzes code for security issues

**When it runs**:
- Every Monday at 8:00 UTC
- When dependencies are updated
- Manually when triggered

**Usage for security reviews**:
1. Go to Actions > Security Scan
2. Click "Run workflow"
3. Review the generated artifacts

## Local CI/CD Tools

### Pre-commit Script

We provide a script to run pre-commit checks in various environments:

```bash
# Run on all files
./scripts/run_precommit.sh --all-files

# Run only on staged files
./scripts/run_precommit.sh --staged

# Attempt to fix issues
./scripts/run_precommit.sh --fix
```

### Docker Testing

Run tests in Docker for consistent environments:

```bash
# Run all tests
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest

# Run UI tests in headless mode
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/ui/ --headless -v
```

## Integration with GitHub Checks

The CI/CD workflows integrate with GitHub's Check feature:

1. **Status Checks**: Pull requests show the status of all checks
2. **Required Checks**: Branches can be configured to require specific checks before merging
3. **Detailed Logs**: Each check provides detailed logs for troubleshooting

## Setting Up Branch Protection

1. Go to `Settings > Branches`
2. Click "Add rule" for `develop` and `main` branches
3. Enable "Require status checks to pass before merging"
4. Select all jobs from the pr-validation workflow
5. Save the rule

See [branch_protection_rules.md](branch_protection_rules.md) for detailed guidance.

## Troubleshooting CI/CD Issues

### Common Issues

1. **Tests pass locally but fail in CI**
   - Ensure you're using the same environment (Docker)
   - Check for race conditions or timing issues

2. **Linting errors**
   - Run pre-commit locally: `pre-commit run --all-files`
   - Check specific files: `pre-commit run --files file1.py file2.py`

3. **Security scan failures**
   - Check the security scan artifacts
   - Update dependencies if vulnerabilities are found

### Getting Help

If you encounter persistent CI/CD issues:

1. Check the workflow run logs for detailed error messages
2. Read the job outputs for specific failure points
3. Contact the repository administrators for assistance

## Best Practices

1. **Run checks locally before pushing**
   - Run `./scripts/run_precommit.sh` before commits
   - Run tests in Docker to match CI environment

2. **Keep PRs focused**
   - Smaller PRs are easier to test and review
   - CI runs faster on smaller changes

3. **Address CI failures promptly**
   - Fix issues as soon as they're reported
   - Don't let failing checks accumulate

4. **Review workflow logs**
   - Check logs to understand failures
   - Use this information to improve your development process

## Custom Workflow Development

To create or modify workflows:

1. Create/edit YAML files in `.github/workflows/`
2. Test locally using [act](https://github.com/nektos/act)
3. Submit a PR with workflow changes for review

## Future CI/CD Enhancements

Planned enhancements to our CI/CD pipeline:

1. Automatic version bumping
2. Integration testing with Xwayland in CI
3. Performance benchmarking
4. Code coverage reporting and enforcement