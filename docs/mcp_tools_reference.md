# MCP Tools Reference: GitHub Functions

This document provides a comprehensive reference for the MCP GitHub tool functions available for Preview Maker development.

## Introduction

MCP GitHub functions are the preferred method for interacting with GitHub as they provide a clean, programmatic interface that eliminates common issues with command-line tools. These functions handle authentication, content encoding, and other complex aspects automatically.

## Available MCP GitHub Functions

### Repository Management

#### `mcp_github_create_repository`

Creates a new GitHub repository in your account.

```javascript
mcp_github_create_repository({
  name: "my-new-repo",
  description: "A new repository for my project",
  private: true,
  autoInit: true
});
```

#### `mcp_github_fork_repository`

Forks a GitHub repository to your account or specified organization.

```javascript
mcp_github_fork_repository({
  owner: "jdamboeck",
  repo: "preview-maker",
  organization: "my-organization" // Optional
});
```

### Branch Management

#### `mcp_github_create_branch`

Creates a new branch in a GitHub repository.

```javascript
mcp_github_create_branch({
  owner: "jdamboeck",
  repo: "preview-maker",
  branch: "feature/new-feature",
  from_branch: "develop" // Optional, defaults to the repository's default branch
});
```

### File Operations

#### `mcp_github_get_file_contents`

Gets the contents of a file or directory from a GitHub repository.

```javascript
mcp_github_get_file_contents({
  owner: "jdamboeck",
  repo: "preview-maker",
  path: "README.md",
  branch: "develop" // Optional
});
```

#### `mcp_github_create_or_update_file`

Creates or updates a single file in a GitHub repository.

```javascript
mcp_github_create_or_update_file({
  owner: "jdamboeck",
  repo: "preview-maker",
  path: "docs/new-doc.md",
  content: "# New Documentation\n\nThis is a new document.",
  message: "docs: Add new documentation",
  branch: "feature/new-docs",
  sha: "abc123def456" // Required only when updating existing files
});
```

#### `mcp_github_push_files`

Pushes multiple files to a GitHub repository in a single commit.

```javascript
mcp_github_push_files({
  owner: "jdamboeck",
  repo: "preview-maker",
  branch: "feature/new-feature",
  message: "feat: Add new components",
  files: [
    {
      path: "app/components/new_component.py",
      content: "class NewComponent:\n    def __init__(self):\n        pass"
    },
    {
      path: "tests/test_new_component.py",
      content: "import unittest\n\ndef test_new_component():\n    pass"
    }
  ]
});
```

### Pull Request Management

#### `mcp_github_create_pull_request`

Creates a new pull request in a GitHub repository.

```javascript
mcp_github_create_pull_request({
  owner: "jdamboeck",
  repo: "preview-maker",
  title: "feat: Add new feature",
  body: "This PR adds a new feature that does X, Y, and Z.",
  head: "feature/new-feature",
  base: "develop",
  draft: false, // Optional
  maintainer_can_modify: true // Optional
});
```

### Issue Management

#### `mcp_github_create_issue`

Creates a new issue in a GitHub repository.

```javascript
mcp_github_create_issue({
  owner: "jdamboeck",
  repo: "preview-maker",
  title: "bug: Application crashes on startup",
  body: "When starting the application with X configuration, it crashes with error Y.",
  labels: ["bug", "priority-high"],
  assignees: ["username"], // Optional
  milestone: 1 // Optional
});
```

#### `mcp_github_update_issue`

Updates an existing issue in a GitHub repository.

```javascript
mcp_github_update_issue({
  owner: "jdamboeck",
  repo: "preview-maker",
  issue_number: 123,
  title: "Updated issue title", // Optional
  body: "Updated issue description", // Optional
  state: "closed", // Optional: "open" or "closed"
  labels: ["bug", "wontfix"], // Optional
  assignees: ["username"], // Optional
  milestone: 2 // Optional
});
```

#### `mcp_github_add_issue_comment`

Adds a comment to an existing issue.

```javascript
mcp_github_add_issue_comment({
  owner: "jdamboeck",
  repo: "preview-maker",
  issue_number: 123,
  body: "I've investigated this issue and found that it's related to X."
});
```

### Search Functions

#### `mcp_github_search_repositories`

Searches for GitHub repositories.

```javascript
mcp_github_search_repositories({
  query: "language:python preview",
  page: 1, // Optional
  perPage: 30 // Optional
});
```

#### `mcp_github_search_code`

Searches for code across GitHub repositories.

```javascript
mcp_github_search_code({
  q: "class ImageProcessor repo:jdamboeck/preview-maker",
  order: "desc", // Optional: "asc" or "desc"
  page: 1, // Optional
  per_page: 10 // Optional
});
```

#### `mcp_github_search_issues`

Searches for issues and pull requests across GitHub repositories.

```javascript
mcp_github_search_issues({
  q: "is:open is:issue label:bug repo:jdamboeck/preview-maker",
  sort: "created", // Optional
  order: "desc", // Optional: "asc" or "desc"
  page: 1, // Optional
  per_page: 10 // Optional
});
```

#### `mcp_github_search_users`

Searches for users on GitHub.

```javascript
mcp_github_search_users({
  q: "location:berlin",
  sort: "followers", // Optional
  order: "desc", // Optional: "asc" or "desc"
  page: 1, // Optional
  per_page: 10 // Optional
});
```

### Commit Information

#### `mcp_github_list_commits`

Gets list of commits of a branch in a GitHub repository.

```javascript
mcp_github_list_commits({
  owner: "jdamboeck",
  repo: "preview-maker",
  sha: "develop", // Optional: branch name or commit SHA
  page: 1, // Optional
  perPage: 30 // Optional
});
```

## Best Practices for MCP Functions

1. **Always use MCP functions first** when available instead of GitHub CLI commands
2. **Use atomic operations** like `push_files` to update multiple files in one commit
3. **Take advantage of error handling** provided by the MCP environment
4. **Document MCP function usage** in PR descriptions for clarity
5. **Create helper functions** for common sequences of MCP operations

## Common Patterns

### Feature Development Workflow

```javascript
// 1. Create a feature branch
mcp_github_create_branch({
  owner: "jdamboeck",
  repo: "preview-maker",
  branch: "feature/new-feature",
  from_branch: "develop"
});

// 2. Add multiple files in a single commit
mcp_github_push_files({
  owner: "jdamboeck",
  repo: "preview-maker",
  branch: "feature/new-feature",
  message: "feat: Implement new feature",
  files: [
    { path: "file1.py", content: "content1" },
    { path: "file2.py", content: "content2" }
  ]
});

// 3. Create a pull request
mcp_github_create_pull_request({
  owner: "jdamboeck",
  repo: "preview-maker",
  title: "feat: Add new feature",
  body: "This PR implements the new feature as described in issue #123.",
  head: "feature/new-feature",
  base: "develop"
});
```

### Bug Fix Workflow

```javascript
// 1. Create issue for the bug
mcp_github_create_issue({
  owner: "jdamboeck",
  repo: "preview-maker",
  title: "bug: Application crashes when processing large images",
  body: "When processing images larger than 4000x4000 pixels, the application crashes with an out of memory error.",
  labels: ["bug", "priority-high"]
});

// 2. Create bugfix branch
mcp_github_create_branch({
  owner: "jdamboeck",
  repo: "preview-maker",
  branch: "bugfix/large-image-crash",
  from_branch: "develop"
});

// 3. Fix the bug in the relevant file
mcp_github_create_or_update_file({
  owner: "jdamboeck",
  repo: "preview-maker",
  path: "app/components/image_processor.py",
  content: "# Updated implementation with fix",
  message: "fix: Handle large images without crashing",
  branch: "bugfix/large-image-crash"
});

// 4. Create PR that references the issue
mcp_github_create_pull_request({
  owner: "jdamboeck",
  repo: "preview-maker",
  title: "fix: Handle large images without crashing",
  body: "This PR fixes the out of memory error when processing large images.\n\nFixes #123",
  head: "bugfix/large-image-crash",
  base: "develop"
});
```

## Fallback to GitHub CLI

In cases where an MCP function is not available, refer to the [GitHub CLI Guide](github_cli_guide.md) and [GitHub CLI Caveats](github_cli_caveats.md) for alternative approaches using non-interactive GitHub CLI commands.