# Branch Protection Rules for Preview Maker

This document outlines the branch protection rules implemented for the Preview Maker repository to ensure code quality and maintain a stable codebase.

## Protected Branches

The following branches are protected:

- **main**: Production-ready code
- **develop**: Integration branch for feature development

## Protection Rules

### For `main` Branch

1. **Require Pull Request Reviews**
   - At least 1 approval required before merging
   - Dismiss stale pull request approvals when new commits are pushed
   - Require review from Code Owners (defined in `.github/CODEOWNERS`)

2. **Require Status Checks to Pass**
   - Required checks:
     - Unit tests
     - Integration tests
     - Docker tests
     - UI tests (headless)
     - Code quality (linting)
   - Require branches to be up to date before merging

3. **Merge Restrictions**
   - No direct commits to `main` (all changes must come through pull requests)
   - No force pushes allowed
   - No deletion of the branch

4. **Include Administrators**
   - These restrictions apply to everyone, including repository administrators

### For `develop` Branch

1. **Require Pull Request Reviews**
   - At least 1 approval required before merging
   - Dismiss stale pull request approvals when new commits are pushed

2. **Require Status Checks to Pass**
   - Required checks:
     - Unit tests
     - Integration tests
     - Docker tests
     - UI tests (headless)
     - Code quality (linting)
   - Require branches to be up to date before merging

3. **Merge Restrictions**
   - No direct commits to `develop` (all changes must come through pull requests)
   - No force pushes allowed
   - No deletion of the branch

## Implementation with GitHub CLI

Branch protection rules can be applied using GitHub CLI:

```bash
# For main branch
gh api repos/jdamboeck/preview-maker/branches/main/protection \
  --method PUT \
  -f required_status_checks.strict=true \
  -f required_status_checks.contexts='["unit-tests", "integration-tests", "docker-tests", "ui-tests", "linting"]' \
  -f enforce_admins=true \
  -f required_pull_request_reviews.required_approving_review_count=1 \
  -f required_pull_request_reviews.dismiss_stale_reviews=true \
  -f required_pull_request_reviews.require_code_owner_reviews=true \
  -f restrictions=null

# For develop branch
gh api repos/jdamboeck/preview-maker/branches/develop/protection \
  --method PUT \
  -f required_status_checks.strict=true \
  -f required_status_checks.contexts='["unit-tests", "integration-tests", "docker-tests", "ui-tests", "linting"]' \
  -f enforce_admins=true \
  -f required_pull_request_reviews.required_approving_review_count=1 \
  -f required_pull_request_reviews.dismiss_stale_reviews=true \
  -f restrictions=null
```

## MCP Function Implementation

For systems with MCP functions, branch protection can be applied programmatically (note: this is a conceptual example as direct MCP functions for branch protection may not be available):

```javascript
// Conceptual example - actual implementation would use GitHub API directly
function setBranchProtection(branch, settings) {
  const url = `https://api.github.com/repos/jdamboeck/preview-maker/branches/${branch}/protection`;

  // Would need to use an HTTP request function or GitHub API wrapper
  // This is a placeholder for the concept
  console.log(`Setting protection for ${branch} with settings:`, settings);
}

// Main branch protection
setBranchProtection("main", {
  required_status_checks: {
    strict: true,
    contexts: ["unit-tests", "integration-tests", "docker-tests", "ui-tests", "linting"]
  },
  enforce_admins: true,
  required_pull_request_reviews: {
    required_approving_review_count: 1,
    dismiss_stale_reviews: true,
    require_code_owner_reviews: true
  },
  restrictions: null
});

// Develop branch protection
setBranchProtection("develop", {
  required_status_checks: {
    strict: true,
    contexts: ["unit-tests", "integration-tests", "docker-tests", "ui-tests", "linting"]
  },
  enforce_admins: true,
  required_pull_request_reviews: {
    required_approving_review_count: 1,
    dismiss_stale_reviews: true
  },
  restrictions: null
});
```

## Verification

To verify that branch protection rules are correctly applied, use:

```bash
gh api repos/jdamboeck/preview-maker/branches/main/protection | jq .
gh api repos/jdamboeck/preview-maker/branches/develop/protection | jq .
```

## Code Owners Definition

Code owners are defined in the `.github/CODEOWNERS` file and determine who must review changes to specific files:

```
# Example CODEOWNERS file
# Global owners for the entire repository
*       @jdamboeck

# Core infrastructure owners
/preview_maker/core/  @core-team-member

# UI component owners
/preview_maker/ui/    @ui-team-member

# Testing infrastructure owners
/tests/               @qa-team-member
```

## Branch Protection Exceptions

In rare cases, branch protection may need to be temporarily disabled for emergency fixes. This should be documented and requires administrator access:

```bash
# Temporarily disable branch protection (EMERGENCY USE ONLY)
gh api repos/jdamboeck/preview-maker/branches/main/protection \
  --method DELETE

# Re-enable protection after emergency fix
# (Run the branch protection setup commands from above)
```

**Important**: Any temporary disabling of branch protection must be:
1. Documented with justification
2. Communicated to the team
3. Re-enabled as soon as possible
4. Followed by a post-mortem if applicable