#!/bin/bash
# GitHub CLI Workflow Helper Functions
# Usage: source github_cli_workflow_helpers.sh

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

# Get file contents
get_file_contents() {
  local owner=$1
  local repo=$2
  local path=$3
  local branch=${4:-"develop"}
  
  gh api repos/$owner/$repo/contents/$path?ref=$branch --jq '.content' | base64 -d | cat
}

# List branches
list_branches() {
  local owner=$1
  local repo=$2
  
  gh api repos/$owner/$repo/branches --jq '.[] | {name, protected}' | cat
}

# List pull requests
list_prs() {
  local owner=$1
  local repo=$2
  local state=${3:-"open"}
  
  gh api repos/$owner/$repo/pulls?state=$state --jq '.[] | {number, title, state}' | cat
}

# Merge pull request
merge_pr() {
  local owner=$1
  local repo=$2
  local pr_number=$3
  local merge_method=${4:-"merge"}
  
  gh api repos/$owner/$repo/pulls/$pr_number/merge -X PUT -f merge_method="$merge_method" | cat
  
  echo "Pull request #$pr_number merged using $merge_method method"
}

# Delete branch
delete_branch() {
  local owner=$1
  local repo=$2
  local branch=$3
  
  gh api repos/$owner/$repo/git/refs/heads/$branch -X DELETE | cat
  
  echo "Branch '$branch' deleted"
}

# Create an issue
create_issue() {
  local owner=$1
  local repo=$2
  local title=$3
  local body=$4
  local labels=${5:-""}
  
  echo "$body" > /tmp/gh_issue_body.txt
  
  if [ -z "$labels" ]; then
    gh api repos/$owner/$repo/issues -f title="$title" \
      -f body="$(cat /tmp/gh_issue_body.txt)" | cat
  else
    gh api repos/$owner/$repo/issues -f title="$title" \
      -f body="$(cat /tmp/gh_issue_body.txt)" \
      -f labels="$labels" | cat
  fi
  
  echo "Issue created: $title"
}

# Example usage:
# source github_cli_workflow_helpers.sh
# create_branch jdamboeck preview-maker feature/new-feature
# create_file jdamboeck preview-maker README.md "# New README" feature/new-feature "docs: Update README"
# create_pr jdamboeck preview-maker "feat: New feature" "Description of the PR" feature/new-feature develop