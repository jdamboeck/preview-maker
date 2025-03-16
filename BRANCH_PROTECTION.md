# Branch Protection Rules

This document outlines the branch protection rules for the Preview Maker repository.

## Main Branch

The `main` branch is protected with the following rules:

1. **Require pull request reviews before merging**
   - At least 1 review is required
   - Dismiss stale pull request approvals when new commits are pushed

2. **Require status checks to pass before merging**
   - Status checks must be passed before merging

3. **Restrict who can push to matching branches**
   - Direct pushes to the main branch are restricted

4. **Do not allow bypassing the above settings**
   - Branch protection applies to everyone, including administrators 

## Develop Branch

The `develop` branch is the integration branch for feature development. All feature branches should be created from and merged back into this branch.

## Feature Branches

Feature branches should follow the naming convention:
- `feature/<feature-name>` for new features
- `bugfix/<bug-description>` for bug fixes
- `hotfix/<issue-description>` for critical fixes that need to go directly to main

All code changes should follow the proper Git workflow as documented in [git_workflow.md](git_workflow.md).