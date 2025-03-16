#!/bin/bash
# File: scripts/github_cli_workflow_helpers.sh
# 
# Helper functions for GitHub CLI workflow operations
# These functions handle common issues with GitHub CLI in automation contexts

# Create a branch from existing branch
create_branch() {
  local owner=$1
  local repo=$2
  local branch=$3
  local base_branch=${4:-"develop"}
  
  echo "Creating branch '$branch' from '$base_branch'..."
  
  # Get the HEAD SHA of the base branch
  head_sha=$(gh api repos/$owner/$repo/git/refs/heads/$base_branch --jq '.object.sha')
  
  if [ -z "$head_sha" ]; then
    echo "Error: Could not get SHA for branch '$base_branch'"
    return 1
  fi
  
  # Create the new branch
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
  
  echo "Creating file '$path' in branch '$branch'..."
  
  # Create temporary file for content
  local tmp_file="/tmp/gh_content_$(basename "$path" | tr '.' '_').txt"
  local tmp_encoded="/tmp/gh_encoded_$(basename "$path" | tr '.' '_').txt"
  
  # Write content to file
  cat > "$tmp_file" << 'EOFCONTENT'
$content
EOFCONTENT
  
  # Replace the content placeholder with actual content
  sed -i "s/\$content/$content/g" "$tmp_file"
  
  # Base64 encode the content
  base64 -w0 "$tmp_file" > "$tmp_encoded"
  
  # Create the file using GitHub API
  gh api repos/$owner/$repo/contents/$path -X PUT \
    -f message="$message" \
    -f content="$(cat "$tmp_encoded")" \
    -f branch="$branch" | cat
  
  # Clean up temporary files
  rm -f "$tmp_file" "$tmp_encoded"
  
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
  
  echo "Creating pull request from '$head' to '$base'..."
  
  # Create temporary file for PR body
  local tmp_file="/tmp/gh_pr_body_$(echo "$head" | tr '/' '_').txt"
  
  # Write PR body to file
  cat > "$tmp_file" << 'EOFPR'
$body
EOFPR
  
  # Replace the body placeholder with actual body
  sed -i "s/\$body/$body/g" "$tmp_file"
  
  # Create the PR using GitHub API
  gh api repos/$owner/$repo/pulls -f title="$title" \
    -f body="$(cat "$tmp_file")" \
    -f head="$head" \
    -f base="$base" | cat
  
  # Clean up temporary file
  rm -f "$tmp_file"
  
  echo "Pull request created from '$head' to '$base'"
}

# Merge a pull request
merge_pr() {
  local owner=$1
  local repo=$2
  local pr_number=$3
  local merge_method=${4:-"merge"} # Options: merge, squash, rebase
  
  echo "Merging pull request #$pr_number..."
  
  # Merge the PR using GitHub API
  gh api repos/$owner/$repo/pulls/$pr_number/merge -X PUT \
    -f merge_method="$merge_method" | cat
  
  echo "Pull request #$pr_number merged using $merge_method method"
}

# Delete a branch
delete_branch() {
  local owner=$1
  local repo=$2
  local branch=$3
  
  echo "Deleting branch '$branch'..."
  
  # Delete the branch using GitHub API
  gh api repos/$owner/$repo/git/refs/heads/$branch -X DELETE | cat
  
  echo "Branch '$branch' deleted"
}

# Create an issue
create_issue() {
  local owner=$1
  local repo=$2
  local title=$3
  local body=$4
  local labels=$5 # Optional: comma-separated list of labels
  
  echo "Creating issue '$title'..."
  
  # Create temporary file for issue body
  local tmp_file="/tmp/gh_issue_body_$(echo "$title" | tr ' ' '_').txt"
  
  # Write issue body to file
  cat > "$tmp_file" << 'EOFISSUE'
$body
EOFISSUE
  
  # Replace the body placeholder with actual body
  sed -i "s/\$body/$body/g" "$tmp_file"
  
  # Create the issue using GitHub API
  if [ -n "$labels" ]; then
    # Convert comma-separated labels to JSON array
    labels_json="[\"$(echo "$labels" | sed 's/,/","/g')\"]"
    gh api repos/$owner/$repo/issues -f title="$title" \
      -f body="$(cat "$tmp_file")" \
      -f labels="$labels_json" | cat
  else
    gh api repos/$owner/$repo/issues -f title="$title" \
      -f body="$(cat "$tmp_file")" | cat
  fi
  
  # Clean up temporary file
  rm -f "$tmp_file"
  
  echo "Issue created: '$title'"
}

# Get file content
get_file_content() {
  local owner=$1
  local repo=$2
  local path=$3
  local branch=${4:-"develop"}
  
  echo "Getting content of file '$path' from branch '$branch'..."
  
  # Get file content using GitHub API
  gh api repos/$owner/$repo/contents/$path?ref=$branch --jq '.content' | cat
  
  echo "Retrieved content for '$path'"
}

# Update file content
update_file() {
  local owner=$1
  local repo=$2
  local path=$3
  local content=$4
  local branch=$5
  local message=${6:-"Update $path"}
  local sha=$7 # Required SHA of the file being replaced
  
  echo "Updating file '$path' in branch '$branch'..."
  
  # Create temporary file for content
  local tmp_file="/tmp/gh_content_$(basename "$path" | tr '.' '_').txt"
  local tmp_encoded="/tmp/gh_encoded_$(basename "$path" | tr '.' '_').txt"
  
  # Write content to file
  cat > "$tmp_file" << 'EOFCONTENT'
$content
EOFCONTENT
  
  # Replace the content placeholder with actual content
  sed -i "s/\$content/$content/g" "$tmp_file"
  
  # Base64 encode the content
  base64 -w0 "$tmp_file" > "$tmp_encoded"
  
  # Update the file using GitHub API
  gh api repos/$owner/$repo/contents/$path -X PUT \
    -f message="$message" \
    -f content="$(cat "$tmp_encoded")" \
    -f branch="$branch" \
    -f sha="$sha" | cat
  
  # Clean up temporary files
  rm -f "$tmp_file" "$tmp_encoded"
  
  echo "File '$path' updated in branch '$branch'"
}

# Usage examples
# --------------
# create_branch "jdamboeck" "preview-maker" "feature/new-branch" "develop"
# create_file "jdamboeck" "preview-maker" "docs/test.md" "# Test\n\nThis is a test" "feature/new-branch" "Add test file"
# create_pr "jdamboeck" "preview-maker" "feat: Add test file" "This PR adds a test file" "feature/new-branch" "develop"
# merge_pr "jdamboeck" "preview-maker" 123 "merge"
# delete_branch "jdamboeck" "preview-maker" "feature/new-branch"
# create_issue "jdamboeck" "preview-maker" "Bug: Something is broken" "## Description\n\nThis is broken" "bug,high-priority"