#!/usr/bin/env python3
# File: scripts/github_cli_helpers.py

import base64
import subprocess
import json
import os
from typing import List, Dict, Optional, Any

def create_branch(owner: str, repo: str, branch: str, base_branch: str = "develop") -> str:
    """Generate command to create a new branch."""
    command = (
        f"head_sha=$(gh api repos/{owner}/{repo}/git/refs/heads/{base_branch} --jq '.object.sha') && "
        f"gh api repos/{owner}/{repo}/git/refs -f ref=\"refs/heads/{branch}\" -f sha=\"$head_sha\" | cat"
    )
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

def create_file(
    owner: str, 
    repo: str, 
    path: str, 
    content: str, 
    branch: str, 
    message: str = None
) -> str:
    """Create a file with content using GitHub CLI API."""
    if message is None:
        message = f"Add {path}"
    
    # Create a temporary file for the content
    tmp_file = f"/tmp/gh_content_{os.path.basename(path).replace('.', '_')}.b64"
    
    # Write content to temporary file and encode
    with open(tmp_file, 'w') as f:
        f.write(content)
    
    # Base64 encode the content
    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    # Write encoded content to temp file
    with open(tmp_file, 'w') as f:
        f.write(encoded_content)
    
    # Create the command
    command = (
        f"gh api repos/{owner}/{repo}/contents/{path} -X PUT "
        f"-f message='{message.replace(\"'\", \"'\\''\")}' "
        f"-f content=\"$(cat {tmp_file})\" "
        f"-f branch='{branch}' | cat"
    )
    
    # Execute command
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    # Clean up temp file
    if os.path.exists(tmp_file):
        os.remove(tmp_file)
    
    return result.stdout

def create_pr(
    owner: str, 
    repo: str, 
    title: str, 
    body: str, 
    head: str, 
    base: str = "develop"
) -> str:
    """Create a pull request using GitHub CLI API."""
    # Create a temporary file for the PR body
    tmp_file = f"/tmp/gh_pr_body_{head.replace('/', '_')}.txt"
    
    # Write body to temporary file
    with open(tmp_file, 'w') as f:
        f.write(body)
    
    # Create the command
    command = (
        f"gh api repos/{owner}/{repo}/pulls "
        f"-f title='{title.replace(\"'\", \"'\\''\")}' "
        f"-f body=\"$(cat {tmp_file})\" "
        f"-f head='{head}' "
        f"-f base='{base}' | cat"
    )
    
    # Execute command
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    # Clean up temp file
    if os.path.exists(tmp_file):
        os.remove(tmp_file)
    
    return result.stdout

def merge_pr(
    owner: str,
    repo: str,
    pr_number: int,
    merge_method: str = "merge"
) -> str:
    """Merge a pull request using GitHub CLI API."""
    command = (
        f"gh api repos/{owner}/{repo}/pulls/{pr_number}/merge -X PUT "
        f"-f merge_method='{merge_method}' | cat"
    )
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

def delete_branch(
    owner: str,
    repo: str,
    branch: str
) -> str:
    """Delete a branch using GitHub CLI API."""
    command = f"gh api repos/{owner}/{repo}/git/refs/heads/{branch} -X DELETE | cat"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

def create_issue(
    owner: str,
    repo: str,
    title: str,
    body: str,
    labels: List[str] = None
) -> str:
    """Create an issue using GitHub CLI API."""
    # Create a temporary file for the issue body
    tmp_file = f"/tmp/gh_issue_body_{title.replace(' ', '_')}.txt"
    
    # Write body to temporary file
    with open(tmp_file, 'w') as f:
        f.write(body)
    
    # Create the base command
    command = (
        f"gh api repos/{owner}/{repo}/issues "
        f"-f title='{title.replace(\"'\", \"'\\''\")}' "
        f"-f body=\"$(cat {tmp_file})\" "
    )
    
    # Add labels if provided
    if labels and len(labels) > 0:
        labels_json = json.dumps(labels)
        command += f"-f labels='{labels_json}' "
    
    command += "| cat"
    
    # Execute command
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    # Clean up temp file
    if os.path.exists(tmp_file):
        os.remove(tmp_file)
    
    return result.stdout