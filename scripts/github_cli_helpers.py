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

# Example usage
if __name__ == "__main__":
    create_branch("jdamboeck", "preview-maker", "feature/test-branch")
    create_file("jdamboeck", "preview-maker", "README.md", "# Test\n\nThis is a test.", "feature/test-branch", "Update README")
    create_pr("jdamboeck", "preview-maker", "Update README", "This PR updates the README.", "feature/test-branch")