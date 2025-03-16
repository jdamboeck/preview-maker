# GitHub CLI Guide for Preview Maker

This guide provides an overview of how to use GitHub CLI (gh) to improve your workflow when contributing to Preview Maker.

## Installation

### Install GitHub CLI

Follow the [official installation instructions](https://github.com/cli/cli#installation) for your platform:

**Ubuntu/Debian:**
```bash
type -p curl >/dev/null || (sudo apt update && sudo apt install curl -y)
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
&& sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
&& sudo apt update \
&& sudo apt install gh -y
```

**macOS:**
```bash
brew install gh
```

**Windows:**
```powershell
winget install --id GitHub.cli
```

### Authenticate with GitHub

```bash
gh auth login
```

Follow the prompts to authenticate using your preferred method (HTTPS/SSH and browser/token).

## Common Workflows

### Starting a New Feature

```bash
# Switch to develop branch and update
git checkout develop
git pull origin develop

# Create a new feature branch
git checkout -b feature/my-feature

# Work on your changes...
# Make commits...

# Push your branch to GitHub
git push -u origin feature/my-feature

# Create a pull request
gh pr create --base develop --title "feat: My new feature" --body "Description of my feature"
```

### Managing Pull Requests

```bash
# List open PRs
gh pr list

# View a specific PR
gh pr view 123

# Check out a PR locally for testing
gh pr checkout 123

# Review a PR
gh pr review 123 --approve  # Approve
gh pr review 123 --comment  # Comment without approval
gh pr review 123 --request-changes  # Request changes

# Merge a PR
gh pr merge 123 --merge  # Standard merge
gh pr merge 123 --squash  # Squash and merge
gh pr merge 123 --rebase  # Rebase and merge
```

### Working with Issues

```bash
# List open issues
gh issue list

# Create a new issue
gh issue create --title "Bug: Something is broken" --body "Description of the issue"

# View an issue
gh issue view 123

# Close an issue
gh issue close 123

# Assign an issue
gh issue edit 123 --add-assignee username
```

### Creating Releases

```bash
# Create a release from a tag
gh release create v1.0.0 --title "Version 1.0.0" --notes "Release notes for version 1.0.0"

# Upload assets to a release
gh release upload v1.0.0 ./path/to/asset.zip
```

## Advanced Use Cases

### CI Status Checks

```bash
# Check status of checks for current PR
gh pr checks

# View workflow runs for the repository
gh run list
```

### Repository Management

```bash
# View repository details
gh repo view

# Clone a repository
gh repo clone jdamboeck/preview-maker

# Create a fork
gh repo fork jdamboeck/preview-maker
```

### Automating Workflows

GitHub CLI can be used in scripts to automate common workflows:

```bash
#!/bin/bash
# Example: Create a feature branch and PR

BRANCH_NAME="feature/automated-task"
PR_TITLE="feat: Automated task implementation"
PR_BODY="This PR implements automated task functionality."

# Create branch
git checkout develop
git pull origin develop
git checkout -b $BRANCH_NAME

# Make changes
# ...

# Commit and push
git add .
git commit -m "$PR_TITLE"
git push -u origin $BRANCH_NAME

# Create PR
gh pr create --base develop --title "$PR_TITLE" --body "$PR_BODY"
```

## Integration with Docker Workflow

When using Docker for development, you can run GitHub CLI from within Docker containers:

```bash
# Run GitHub CLI in Docker container
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm preview-maker gh pr list
```

## Best Practices

1. **Always authenticate before starting work**
   ```bash
   gh auth status  # Check authentication status
   ```

2. **Use meaningful PR titles and descriptions**
   - Follow the project commit message conventions
   - Include context and reasoning

3. **Link PRs to issues when applicable**
   ```bash
   gh pr create --title "feat: New feature" --body "Fixes #123"
   ```

4. **Check PR status before merging**
   ```bash
   gh pr checks
   gh pr view
   ```

5. **Keep your fork synchronized**
   ```bash
   gh repo sync
   ```

## Troubleshooting

### Authentication Issues

If you encounter authentication issues:

```bash
# Verify authentication status
gh auth status

# Re-authenticate if needed
gh auth login

# Check token scopes
gh auth token
```

### API Rate Limiting

If you encounter rate limiting issues:

1. Ensure you're authenticated
2. Consider using a personal access token with appropriate scopes
3. Space out API calls in scripts

### Command Help

Get help with any command:

```bash
gh help pr
gh help issue
gh pr create --help
```

## Additional Resources

- [GitHub CLI Official Documentation](https://cli.github.com/manual/)
- [GitHub CLI Repository](https://github.com/cli/cli)
- [Preview Maker Git Workflow](../rebuild_plan/git_workflow.md)