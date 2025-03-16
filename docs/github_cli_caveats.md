# GitHub CLI API Caveats and Solutions

This document outlines common issues encountered when using GitHub CLI API for Git operations and provides tested solutions.

## Command Limitations

### Multi-line Commands

Issue: GitHub CLI commands with multiple lines fail with error: "Command contains newline characters. Please write a single command without newlines"

**Example of failing command:**

```bash
content=$(echo -n "# Test content

More content" | base64 -w0)

gh api repos/owner/repo/contents/path -X PUT \
  -f message="commit message" \
  -f content="$content" \
  -f branch="branch-name"
```

**Working solution:**

```bash
content=$(echo -n "# Test\n\nMore content" | base64 -w0) && gh api repos/owner/repo/contents/path -X PUT -f message="commit message" -f content="$content" -f branch="branch-name"
```

### Complex Content with Special Characters

Issue: Content with special characters can cause escaping problems.

**Working solution with temp file:**

```bash
echo -n "# Complex content with 'quotes' and \"double quotes\"" | base64 -w0 > /tmp/content.txt && \
gh api repos/owner/repo/contents/path -X PUT -f message="message" -f content="$(cat /tmp/content.txt)" -f branch="branch"
```

## Helper Script Approach

For complex operations, use a Python helper script that generates commands:

```python
import json

# Create a feature branch with GitHub CLI API
def create_branch(owner, repo, branch, from_branch="develop"):
    """Create a new branch non-interactively."""
    head_sha = f"$(gh api repos/{owner}/{repo}/git/refs/heads/{from_branch} --jq '.object.sha')"
    command = f"gh api repos/{owner}/{repo}/git/refs -f ref='refs/heads/{branch}' -f sha='{head_sha}'"
    print(f"Command to run: {command}")

# Create a file with GitHub CLI API  
def create_file(owner, repo, path, content, branch, message):
    """Create a file non-interactively."""
    content_b64 = "$(echo -n '" + content.replace("'", "'\\'") + "' | base64 -w0)"
    command = f"gh api repos/{owner}/{repo}/contents/{path} -X PUT -f message='{message}' -f content='{content_b64}' -f branch='{branch}'"
    print(f"Command to run: {command}")

# Create a pull request with GitHub CLI API
def create_pr(owner, repo, title, body, head, base="develop"):
    """Create a PR non-interactively."""
    body_escaped = json.dumps(body)
    command = f"gh api repos/{owner}/{repo}/pulls -f title='{title}' -f body={body_escaped} -f head='{head}' -f base='{base}'"
    print(f"Command to run: {command}")
```

## Multiple Files in One Commit

Issue: GitHub CLI API requires separate calls for each file, unlike MCP's `push_files`.

**Working approach:**

1. Create a script that iterates through files and generates commands
2. Use `gh` CLI for a shell script approach (more complex)
3. When possible, always prefer MCP's `push_files` function

## Template Usage

### Pull Request Templates

PR templates work correctly with both MCP functions and GitHub CLI API:

```javascript
// With MCP functions
mcp_github_create_pull_request({
  owner: "jdamboeck",
  repo: "preview-maker",
  title: "feat: Add feature",
  body: "# Pull Request\n\n## Description\nThis is a feature\n\n## Type of Change\n- [x] New feature",
  head: "feature/branch",
  base: "develop"
});
```

```bash
# With GitHub CLI API
gh api repos/jdamboeck/preview-maker/pulls -f title="feat: Add feature" \
  -f body="# Pull Request\n\n## Description\nThis is a feature\n\n## Type of Change\n- [x] New feature" \
  -f head="feature/branch" \
  -f base="develop"
```

### Issue Templates

Issue templates work correctly when manually structured in the body content.

## Recommendations

1. **Use MCP functions** as the first and preferred choice whenever available
2. For GitHub CLI API operations:
   - Use single-line commands with escaped newlines
   - Use temp files for complex content
   - Consider helper scripts for complex operations
3. Always test commands before documenting them
4. When in doubt, use the MCP approach