#!/usr/bin/env python3
"""
Helper functions for GitHub CLI operations.

This module provides utility functions that wrap GitHub CLI API commands,
avoiding common issues with shell escaping and parameter handling.
Each function handles proper escaping and temporary file management.
"""

import base64
import json
import os
import subprocess
import tempfile
from typing import List, Optional


def create_branch(
    owner: str, repo: str, branch: str, base_branch: str = "develop"
) -> str:
    """Generate command to create a new branch."""
    command = [
        "bash",
        "-c",
        (
            f"head_sha=$(gh api repos/{owner}/{repo}/git/refs/heads/{base_branch} "
            f"--jq '.object.sha') && gh api repos/{owner}/{repo}/git/refs "
            f'-f ref="refs/heads/{branch}" -f sha="$head_sha" | cat'
        ),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout


def create_file(
    owner: str,
    repo: str,
    path: str,
    content: str,
    branch: str,
    message: Optional[str] = None,
) -> str:
    """Create a file with content using GitHub CLI API."""
    if message is None:
        message = f"Add {path}"

    # Create temporary files for content and message
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as content_file:
        content_file.write(content)
        content_path = content_file.name

    # Base64 encode the content
    encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as encoded_file:
        encoded_file.write(encoded_content)
        encoded_path = encoded_file.name

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as message_file:
        message_file.write(message)
        message_path = message_file.name

    # Create the command
    command = [
        "bash",
        "-c",
        f"gh api repos/{owner}/{repo}/contents/{path} -X PUT "
        f"-f message=@{message_path} "
        f"-f content=@{encoded_path} "
        f"-f branch={branch} | cat",
    ]

    # Execute command
    result = subprocess.run(command, capture_output=True, text=True)

    # Clean up temp files
    for file_path in [content_path, encoded_path, message_path]:
        if os.path.exists(file_path):
            os.remove(file_path)

    return result.stdout


def create_pr(
    owner: str, repo: str, title: str, body: str, head: str, base: str = "develop"
) -> str:
    """Create a pull request using GitHub CLI API."""
    # Create temporary files for title and body
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as title_file:
        title_file.write(title)
        title_path = title_file.name

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as body_file:
        body_file.write(body)
        body_path = body_file.name

    # Create the command
    command = [
        "bash",
        "-c",
        f"gh api repos/{owner}/{repo}/pulls "
        f"-f title=@{title_path} "
        f"-f body=@{body_path} "
        f"-f head={head} "
        f"-f base={base} | cat",
    ]

    # Execute command
    result = subprocess.run(command, capture_output=True, text=True)

    # Clean up temp files
    for file_path in [title_path, body_path]:
        if os.path.exists(file_path):
            os.remove(file_path)

    return result.stdout


def merge_pr(owner: str, repo: str, pr_number: int, merge_method: str = "merge") -> str:
    """Merge a pull request using GitHub CLI API."""
    command = [
        "bash",
        "-c",
        f"gh api repos/{owner}/{repo}/pulls/{pr_number}/merge -X PUT "
        f"-f merge_method={merge_method} | cat",
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout


def delete_branch(owner: str, repo: str, branch: str) -> str:
    """Delete a branch using GitHub CLI API."""
    command = [
        "bash",
        "-c",
        f"gh api repos/{owner}/{repo}/git/refs/heads/{branch} -X DELETE | cat",
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout


def create_issue(
    owner: str, repo: str, title: str, body: str, labels: Optional[List[str]] = None
) -> str:
    """Create an issue using GitHub CLI API."""
    # Create temporary files for title and body
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as title_file:
        title_file.write(title)
        title_path = title_file.name

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as body_file:
        body_file.write(body)
        body_path = body_file.name

    # Create the base command
    command_parts = [
        "gh api repos/{owner}/{repo}/issues "
        f"-f title=@{title_path} "
        f"-f body=@{body_path} "
    ]

    # Add labels if provided
    if labels and len(labels) > 0:
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as labels_file:
            labels_file.write(json.dumps(labels))
            labels_path = labels_file.name
        command_parts.append(f"-f labels=@{labels_path} ")
        temp_files = [title_path, body_path, labels_path]
    else:
        temp_files = [title_path, body_path]

    command_parts.append("| cat")
    command = ["bash", "-c", "".join(command_parts)]

    # Execute command
    result = subprocess.run(command, capture_output=True, text=True)

    # Clean up temp files
    for file_path in temp_files:
        if os.path.exists(file_path):
            os.remove(file_path)

    return result.stdout
