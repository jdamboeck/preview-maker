# MCP Tools Reference

This document provides a reference for all Model Control Protocol (MCP) tools available for the Preview Maker project. These tools can be used by AI assistants to interact with the development environment, GitHub repository, filesystem, and external resources.

## GitHub MCP Tools

These tools allow interaction with GitHub without using direct Git commands.

### Repository Management

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `mcp_github_create_repository` | Create a new GitHub repository | `name`, `description`, `private` |
| `mcp_github_fork_repository` | Fork a repository to your account | `owner`, `repo`, `organization` (optional) |
| `mcp_github_search_repositories` | Search for GitHub repositories | `query`, `page`, `perPage` |

### Branch and Commit Management

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `mcp_github_create_branch` | Create a new branch | `owner`, `repo`, `branch`, `from_branch` (optional) |
| `mcp_github_list_commits` | List commits on a branch | `owner`, `repo`, `sha` (branch/tag), `page`, `perPage` |

### File Operations

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `mcp_github_create_or_update_file` | Create or update a single file | `owner`, `repo`, `path`, `content`, `message`, `branch`, `sha` (for updates) |
| `mcp_github_get_file_contents` | Get file or directory contents | `owner`, `repo`, `path`, `branch` (optional) |
| `mcp_github_push_files` | Push multiple files in one commit | `owner`, `repo`, `branch`, `files` (array of path/content objects), `message` |

### Issue and PR Management

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `mcp_github_create_issue` | Create a new issue | `owner`, `repo`, `title`, `body`, `labels` (optional) |
| `mcp_github_get_issue` | Get issue details | `owner`, `repo`, `issue_number` |
| `mcp_github_list_issues` | List repository issues | `owner`, `repo`, `state`, `labels`, `sort`, etc. |
| `mcp_github_update_issue` | Update an existing issue | `owner`, `repo`, `issue_number`, plus fields to update |
| `mcp_github_add_issue_comment` | Comment on an issue | `owner`, `repo`, `issue_number`, `body` |
| `mcp_github_create_pull_request` | Create a pull request | `owner`, `repo`, `title`, `head`, `base`, `body` |

### Search Operations

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `mcp_github_search_code` | Search code across repositories | `q` (query), `page`, `per_page`, etc. |
| `mcp_github_search_issues` | Search issues and PRs | `q` (query), `sort`, `order`, etc. |
| `mcp_github_search_users` | Search GitHub users | `q` (query), `sort`, `order`, etc. |

## Docker MCP Tools

These tools allow interaction with Docker containers and services.

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `mcp_docker_create_container` | Create a new Docker container | `image`, `name` (optional), `environment`, `ports` |
| `mcp_docker_deploy_compose` | Deploy a Docker Compose stack | `compose_yaml`, `project_name` |
| `mcp_docker_get_logs` | Get logs from a container | `container_name` |
| `mcp_docker_list_containers` | List all Docker containers | - |

## Filesystem MCP Tools

These tools provide access to the filesystem within allowed directories.

### Basic File Operations

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `mcp_filesystem_read_file` | Read file contents | `path` |
| `mcp_filesystem_write_file` | Create or overwrite a file | `path`, `content` |
| `mcp_filesystem_edit_file` | Make line-based edits to a file | `path`, `edits` (array of oldText/newText pairs), `dryRun` (optional) |
| `mcp_filesystem_move_file` | Move or rename files | `source`, `destination` |
| `mcp_filesystem_read_multiple_files` | Read multiple files at once | `paths` (array of paths) |

### Directory Operations

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `mcp_filesystem_create_directory` | Create a directory | `path` |
| `mcp_filesystem_list_directory` | List directory contents | `path` |
| `mcp_filesystem_directory_tree` | Get recursive directory structure | `path` |
| `mcp_filesystem_list_allowed_directories` | List allowed directories | - |

### Search and Info

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `mcp_filesystem_search_files` | Search for files matching pattern | `path`, `pattern`, `excludePatterns` (optional) |
| `mcp_filesystem_get_file_info` | Get metadata about a file | `path` |

## Web Access Tools

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `mcp_fetch_fetch` | Fetch content from a URL | `url`, `max_length` (optional), `raw` (optional), `start_index` (optional) |

## Usage Examples

### Creating a Branch and Adding Files

```javascript
// Create a new branch
mcp_github_create_branch({
  owner: "jdamboeck",
  repo: "preview-maker",
  branch: "feature/new-component",
  from_branch: "develop"
});

// Add files to the branch
mcp_github_push_files({
  owner: "jdamboeck",
  repo: "preview-maker",
  branch: "feature/new-component",
  message: "feat: Add new component implementation",
  files: [
    {
      path: "app/components/new_component.py",
      content: "# New component implementation\n\nclass NewComponent:\n    def __init__(self):\n        pass"
    },
    {
      path: "tests/components/test_new_component.py",
      content: "# Tests for new component\n\nimport pytest\n\ndef test_new_component():\n    assert True"
    }
  ]
});
```

### Creating a Pull Request

```javascript
mcp_github_create_pull_request({
  owner: "jdamboeck",
  repo: "preview-maker",
  title: "feat: Add new component implementation",
  body: "This PR adds the new component with tests.\n\nCloses #42",
  head: "feature/new-component",
  base: "develop"
});
```

### Working with Docker

```javascript
// List all containers
mcp_docker_list_containers({
  random_string: "any_value"
});

// Get logs from a container
mcp_docker_get_logs({
  container_name: "preview-maker-test-1"
});
```

### File Operations

```javascript
// Create a directory
mcp_filesystem_create_directory({
  path: "/home/jd/dev/projects/preview-maker/app/new_module"
});

// Write a file
mcp_filesystem_write_file({
  path: "/home/jd/dev/projects/preview-maker/app/new_module/component.py",
  content: "# New component implementation\n\nclass NewComponent:\n    def __init__(self):\n        pass"
});

// Search for files
mcp_filesystem_search_files({
  path: "/home/jd/dev/projects/preview-maker",
  pattern: "test_*.py",
  excludePatterns: ["__pycache__"]
});
```

## Best Practices

1. **Prefer MCP Tools**: Use MCP tools instead of direct terminal commands when possible
2. **Error Handling**: Always check for errors in the response
3. **Atomicity**: For GitHub operations, try to use atomic operations (like `push_files` for multiple files)
4. **Permissions**: Be aware of allowed directories for filesystem operations
5. **Documentation**: Document any MCP tool usage in commit messages or PR descriptions

## Limitations

1. MCP tools only work within allowed directories
2. Some advanced Git operations may still require GitHub CLI
3. For complex Docker operations, you may need to use Docker CLI through terminal commands