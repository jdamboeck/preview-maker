# Branch Protection Rules for Preview Maker

This document outlines the branch protection rules for the Preview Maker repository, ensuring code quality and maintaining a clean Git history.

## Overview

Branch protection rules help ensure that changes to important branches meet certain quality criteria before they are merged. This document provides instructions on how to set up these rules through the GitHub interface.

## Protection Rules for `main` Branch

The `main` branch contains production-ready code and must always remain stable.

### Required Rules

1. **Require pull request reviews before merging**
   - Require at least 1 approval before merging
   - Dismiss stale pull request approvals when new commits are pushed
   - Require review from Code Owners

2. **Require status checks to pass before merging**
   - Require branches to be up to date before merging
   - Required status checks:
     - `test` (tests must pass)
     - `lint` (code quality checks must pass)
     - `verify-docs` (documentation must be valid)

3. **Require signed commits**
   - All commits must be signed with GPG keys

4. **Include administrators**
   - Apply these rules to repository administrators

5. **Restrict who can push to matching branches**
   - Allow only specific users or teams to push to the `main` branch

## Protection Rules for `develop` Branch

The `develop` branch is our integration branch and should be protected to ensure high-quality code.

### Required Rules

1. **Require pull request reviews before merging**
   - Require at least 1 approval before merging
   - Dismiss stale pull request approvals when new commits are pushed

2. **Require status checks to pass before merging**
   - Require branches to be up to date before merging
   - Required status checks:
     - `test` (tests must pass)
     - `lint` (code quality checks must pass)

3. **Require linear history**
   - Prevent merge commits
   - Enforce clean, linear history

4. **Include administrators**
   - Apply these rules to repository administrators

## Setting Up Branch Protection Rules

### Instructions for Repository Administrators

1. Navigate to the repository on GitHub
2. Go to Settings > Branches
3. Click "Add rule" next to "Branch protection rules"
4. Enter the branch name pattern (`main` or `develop`)
5. Configure the protection rules as described above
6. Click "Create" or "Save changes"

## Branch Protection Rules with GitHub CLI

You can also set up branch protection rules using GitHub CLI:

```bash
# For main branch
gh api --method PUT repos/:owner/:repo/branches/main/protection \
  -f required_status_checks='{"strict":true,"contexts":["test","lint","verify-docs"]}' \
  -f enforce_admins=true \
  -f required_pull_request_reviews='{"dismissal_restrictions":{},"dismiss_stale_reviews":true,"require_code_owner_reviews":true,"required_approving_review_count":1}' \
  -f restrictions='{"users":[],"teams":[],"apps":[]}' \
  -f required_signatures=true

# For develop branch
gh api --method PUT repos/:owner/:repo/branches/develop/protection \
  -f required_status_checks='{"strict":true,"contexts":["test","lint"]}' \
  -f enforce_admins=true \
  -f required_pull_request_reviews='{"dismissal_restrictions":{},"dismiss_stale_reviews":true,"require_code_owner_reviews":false,"required_approving_review_count":1}' \
  -f required_linear_history=true
```

## Additional Protection Measures

### CODEOWNERS File

Create a `.github/CODEOWNERS` file to automatically assign reviewers:

```
# Default owners for everything in the repo
* @jdamboeck

# Documentation owners
docs/ @documentation-team

# Core code owners
preview_maker/core/ @core-team

# UI code owners
preview_maker/ui/ @ui-team

# AI integration code owners
preview_maker/ai/ @ai-team
```

### Automated Branch Cleanup

We've set up GitHub Actions workflow to automatically delete branches after their PRs are merged:
- The workflow runs when a PR is closed
- It only deletes branches that have been merged
- It does not delete `release/*` branches to preserve release history

## Best Practices

1. **Never Commit Directly to Protected Branches**
   - Always create feature branches and pull requests
   - Even simple changes should follow the PR workflow

2. **Keep PRs Small and Focused**
   - Easier to review
   - Lower chance of introducing bugs
   - Faster integration time

3. **Address All CI Failures**
   - Fix all failing checks before requesting review
   - If a check is failing incorrectly, document it in the PR

4. **Regular Rebasing**
   - Regularly rebase feature branches against develop
   - Helps prevent merge conflicts

## Troubleshooting

### Common Issues

1. **Cannot push to protected branch**
   - Create a pull request instead
   - Ensure you have appropriate permissions

2. **CI checks failing**
   - Run pre-commit hooks locally before pushing
   - Check the CI logs for specific errors

3. **Stale review dismissed**
   - Request a new review after pushing changes
   - Ensure you address all reviewer comments

For more help, contact repository administrators.