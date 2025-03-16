#!/bin/bash
# GitHub CLI Workflow Helper Script
# This script provides helper functions for GitHub operations using the GitHub CLI API

# Create a branch using GitHub CLI API
create_branch() {
  local owner=$1
  local repo=$2
  local branch=$3
  local from_branch=${4:-develop}
  
  local head_sha=$(gh api repos/$owner/$repo/git/refs/heads/$from_branch --jq '.object.sha')
  gh api repos/$owner/$repo/git/refs -f ref="refs/heads/$branch" -f sha="$head_sha" | cat
  echo "Branch '$branch' created from '$from_branch'"
}

# Create or update file using GitHub CLI API
create_file() {
  local owner=$1
  local repo=$2
  local path=$3
  local content=$4
  local branch=$5
  local message=$6
  
  # Write content to temp file and encode
  echo -n "$content" | base64 -w0 > /tmp/gh_content.txt
  
  # Create or update file
  gh api repos/$owner/$repo/contents/$path -X PUT \
    -f message="$message" \
    -f content="$(cat /tmp/gh_content.txt)" \
    -f branch="$branch" | cat
  
  echo "File '$path' created or updated in branch '$branch'"
}

# Create pull request using GitHub CLI API
create_pr() {
  local owner=$1
  local repo=$2
  local title=$3
  local body=$4
  local head=$5
  local base=${6:-develop}
  
  # Write body to temp file
  echo -n "$body" > /tmp/gh_body.txt
  
  # Create PR
  gh api repos/$owner/$repo/pulls \
    -f title="$title" \
    -f body="$(cat /tmp/gh_body.txt)" \
    -f head="$head" \
    -f base="$base" | cat
  
  echo "Pull request created from '$head' to '$base'"
}

# Merge pull request using GitHub CLI API
merge_pr() {
  local owner=$1
  local repo=$2
  local pr_number=$3
  local merge_method=${4:-merge}
  
  gh api repos/$owner/$repo/pulls/$pr_number/merge -X PUT \
    -f merge_method="$merge_method" | cat
  
  echo "Pull request #$pr_number merged using $merge_method method"
}

# Delete branch using GitHub CLI API
delete_branch() {
  local owner=$1
  local repo=$2
  local branch=$3
  
  gh api repos/$owner/$repo/git/refs/heads/$branch -X DELETE | cat
  
  echo "Branch '$branch' deleted"
}

# Example usage
# ./github_cli_workflow_helpers.sh create_branch jdamboeck preview-maker feature/test
# ./github_cli_workflow_helpers.sh create_file jdamboeck preview-maker README.md "# Test" feature/test "Update README"

# If called directly, execute the specified function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  "$@"
fi