# GitHub CLI Caveats and Solutions

This document outlines common issues encountered when using GitHub CLI for automation and provides tested solutions.

## Key Issues with GitHub CLI Automation

When using GitHub CLI for automation or in non-interactive contexts, you may encounter these challenges:

1. **Multi-line commands don't work as expected**
2. **Content with special characters requires proper escaping**
3. **Auth tokens need proper handling**
4. **Error handling is limited in non-interactive mode**

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

## Solutions for Common Issues

### Working with Multi-line Content

When creating files or PRs with multi-line content, direct commands often fail. Here are effective workarounds:

#### Solution 1: Use Temporary Files

```bash
# Create content in a temporary file
cat > /tmp/content.txt << 'EOF'
# This is a multi-line file
with code examples and special characters like:
* Lists
* "Quotes"
* $Variables
EOF

# Base64 encode the content
base64 -w0 /tmp/content.txt > /tmp/encoded.txt

# Create the file using the encoded content
gh api repos/jdamboeck/preview-maker/contents/path/to/file.md -X PUT \
  -f message="Add documentation file" \
  -f content="$(cat /tmp/encoded.txt)" \
  -f branch="feature/branch-name" | cat
```

#### Solution 2: Echo With Base64 Encoding

```bash
# For smaller content, use echo with new lines escaped
echo -n "# Title\n\nThis is a paragraph.\n\n* List item 1\n* List item 2" | base64 -w0 > /tmp/content.txt
gh api repos/jdamboeck/preview-maker/contents/README.md -X PUT \
  -f message="Update README" \
  -f content="$(cat /tmp/content.txt)" \
  -f branch="feature/branch-name" | cat
```

### Creating Pull Requests with Detailed Descriptions

For PRs with detailed descriptions that include formatting:

```bash
# Write PR description to a file
cat > /tmp/pr_description.txt << 'EOF'
This PR adds the following features:

- Feature 1: Description with details
- Feature 2: Another description

## Testing Done
- Unit tests all pass
- Integration tests completed

Fixes #123
EOF

# Create the PR using the file content
gh api repos/jdamboeck/preview-maker/pulls -f title="feat: Add new feature" \
  -f body="$(cat /tmp/pr_description.txt)" \
  -f head="feature/branch-name" \
  -f base="develop" | cat
```

## Helper Script Approach

For complex operations, you can use either a Bash or Python helper script to generate commands:

### Bash Helper Functions

```bash
#!/bin/bash
# File: scripts/github_cli_workflow_helpers.sh

# Create a branch
create_branch() {
  local owner=$1
  local repo=$2
  local branch=$3
  local base_branch=${4:-"develop"}
  
  head_sha=$(gh api repos/$owner/$repo/git/refs/heads/$base_branch --jq '.object.sha')
  gh api repos/$owner/$repo/git/refs -f ref="refs/heads/$branch" \
    -f sha="$head_sha" | cat
  
  echo "Branch '$branch' created from '$base_branch'"
}

# Create a file with content
create_file() {
  local owner=$1
  local repo=$2
  local path=$3
  local content=$4
  local branch=$5
  local message=${6:-"Add $path"}
  
  echo -n "$content" | base64 -w0 > /tmp/gh_content.txt
  gh api repos/$owner/$repo/contents/$path -X PUT \
    -f message="$message" \
    -f content="$(cat /tmp/gh_content.txt)" \
    -f branch="$branch" | cat
  
  echo "File '$path' created in branch '$branch'"
}

# Create a pull request
create_pr() {
  local owner=$1
  local repo=$2
  local title=$3
  local body=$4
  local head=$5
  local base=${6:-"develop"}
  
  echo "$body" > /tmp/gh_pr_body.txt
  gh api repos/$owner/$repo/pulls -f title="$title" \
    -f body="$(cat /tmp/gh_pr_body.txt)" \
    -f head="$head" \
    -f base="$base" | cat
  
  echo "Pull request created from '$head' to '$base'"
}
```

### Python Helper Script

```python
#!/usr/bin/env python3
# File: scripts/github_cli_helpers.py

import base64
import subprocess
import json
import os
from typing import List, Dict, Optional, Any

def create_branch_command(owner: str, repo: str, branch: str, base_branch: str = "develop") -> str:
    """Generate command to create a new branch."""
    return (
        f"head_sha=$(gh api repos/{owner}/{repo}/git/refs/heads/{base_branch} --jq '.object.sha') && "
        f"gh api repos/{owner}/{repo}/git/refs -f ref=\"refs/heads/{branch}\" -f sha=\"$head_sha\" | cat"
    )

def create_file_command(
    owner: str, 
    repo: str, 
    path: str, 
    content: str, 
    branch: str, 
    message: str = None
) -> str:
    """Generate command to create a file with content."""
    if message is None:
        message = f"Add {path}"
    
    # Create a temporary file name
    tmp_file = f"/tmp/gh_content_{os.path.basename(path)}.b64"
    
    # Create the command with proper escaping
    commands = [
        f"echo -n '{content.replace(\"'\", \"'\\''\")}' | base64 -w0 > {tmp_file}",
        f"gh api repos/{owner}/{repo}/contents/{path} -X PUT "
        f"-f message='{message.replace(\"'\", \"'\\''\")}' "
        f"-f content=\"$(cat {tmp_file})\" "
        f"-f branch='{branch}' | cat",
        f"rm {tmp_file}"
    ]
    
    return " && ".join(commands)

def create_pr_command(
    owner: str, 
    repo: str, 
    title: str, 
    body: str, 
    head: str, 
    base: str = "develop"
) -> str:
    """Generate command to create a pull request."""
    # Create a temporary file name
    tmp_file = f"/tmp/gh_pr_body_{head.replace('/', '_')}.txt"
    
    # Create the command with proper escaping
    commands = [
        f"cat > {tmp_file} << 'EOFGH'\n{body}\nEOFGH",
        f"gh api repos/{owner}/{repo}/pulls "
        f"-f title='{title.replace(\"'\", \"'\\''\")}' "
        f"-f body=\"$(cat {tmp_file})\" "
        f"-f head='{head}' "
        f"-f base='{base}' | cat",
        f"rm {tmp_file}"
    ]
    
    return " && ".join(commands)
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

## Important Recommendations

1. **Always append `| cat` to commands** that might launch a pager
2. **Store complex content in temporary files** rather than passing directly
3. **Use the helper scripts** provided in this document for common operations
4. **Prefer MCP functions over GitHub CLI** whenever available
5. **Test commands in a safe environment** before using in production workflows
6. **For truly complex operations**, consider using the GitHub API directly with proper HTTP clients
7. **Use single-line commands with escaped newlines** when necessary
8. **Consider helper scripts for complex operations** to make commands more maintainable

By following these guidelines, you can reliably automate GitHub operations while avoiding common pitfalls with the GitHub CLI.