# Git History Analysis

## Overview
This document outlines the approach for analyzing the Git history of the Preview Maker project to extract valuable information about past issues, debugging efforts, and solutions. This helps preserve knowledge during the rebuild and prevents rediscovering the same issues.

## Purpose
- Identify recurring issues and their solutions
- Document known bugs and fixes
- Preserve debugging techniques used in the original codebase
- Identify areas that have needed frequent modification (potential design issues)

## Analysis Methodology

### 1. Commit Analysis Script

We will create a Python script called `analyze_git_history.py` to extract and analyze the Git history:

```python
#!/usr/bin/env python3
"""
Analyze Git history of Preview Maker to extract debugging information.
"""
import subprocess
import re
import json
import os
from datetime import datetime
from collections import defaultdict, Counter

def get_git_log():
    """Get the git log with detailed information."""
    cmd = [
        "git", "log", "--stat", "--patch",
        "--since=1.year", "--pretty=format:%h|%an|%ad|%s"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def parse_git_log(log_text):
    """Parse the git log into structured data."""
    entries = []
    current_entry = None

    for line in log_text.split('\n'):
        if line.startswith('diff --git'):
            # Start of a new file in the commit
            file_match = re.search(r'a/(.*) b/(.*)', line)
            if file_match and current_entry:
                current_entry["files"].append(file_match.group(2))
        elif '|' in line and len(line.split('|')) == 4:
            # Start of a new commit
            if current_entry:
                entries.append(current_entry)

            hash, author, date, subject = line.split('|', 3)
            current_entry = {
                "hash": hash,
                "author": author,
                "date": date,
                "subject": subject,
                "files": [],
                "bugs": [],
                "fixes": [],
            }

            # Extract bug/fix information from commit message
            if re.search(r'fix(es|ed)?|bug|issue|problem|error', subject, re.I):
                current_entry["fixes"].append(subject)
            if re.search(r'bug|issue|problem|error', subject, re.I):
                current_entry["bugs"].append(subject)

    if current_entry:
        entries.append(current_entry)

    return entries

def analyze_commits(entries):
    """Analyze the commit data to extract patterns."""
    file_changes = defaultdict(int)
    bug_fixes = []
    features = []
    frequent_issues = Counter()

    for entry in entries:
        for file in entry["files"]:
            file_changes[file] += 1

        if entry["fixes"]:
            bug_fixes.extend(entry["fixes"])
            # Extract issue types from fix messages
            for fix in entry["fixes"]:
                for issue_type in ["crash", "display", "error", "performance", "memory", "ui", "ai"]:
                    if issue_type in fix.lower():
                        frequent_issues[issue_type] += 1

        if "feature" in entry["subject"].lower() or "add" in entry["subject"].lower():
            features.append(entry["subject"])

    most_changed_files = sorted(file_changes.items(), key=lambda x: x[1], reverse=True)
    most_frequent_issues = frequent_issues.most_common()

    return {
        "most_changed_files": most_changed_files[:10],  # Top 10 most changed files
        "bug_fixes": bug_fixes,
        "features": features,
        "most_frequent_issues": most_frequent_issues,
    }

def save_analysis(analysis, output_file="git_analysis.json"):
    """Save the analysis to a JSON file."""
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    print(f"Analysis saved to {output_file}")

def generate_report(analysis, output_file="git_analysis_report.md"):
    """Generate a Markdown report from the analysis."""
    report = "# Git History Analysis Report\n\n"
    report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    report += "## Most Frequently Changed Files\n\n"
    report += "These files have had the most changes, indicating potential areas of instability or active development:\n\n"
    report += "| File | Change Count |\n|------|-------------|\n"
    for file, count in analysis["most_changed_files"]:
        report += f"| {file} | {count} |\n"

    report += "\n## Common Issues\n\n"
    report += "These are the most common types of issues fixed in the codebase:\n\n"
    report += "| Issue Type | Occurrence Count |\n|------------|------------------|\n"
    for issue, count in analysis["most_frequent_issues"]:
        report += f"| {issue.capitalize()} | {count} |\n"

    report += "\n## Recent Bug Fixes\n\n"
    report += "These are the recent bug fixes that might need attention during the rebuild:\n\n"
    for fix in analysis["bug_fixes"][-10:]:  # Show 10 most recent
        report += f"- {fix}\n"

    report += "\n## Recent Features\n\n"
    report += "These are the recently added features:\n\n"
    for feature in analysis["features"][-10:]:  # Show 10 most recent
        report += f"- {feature}\n"

    with open(output_file, 'w') as f:
        f.write(report)
    print(f"Report saved to {output_file}")

def main():
    print("Analyzing Git history...")
    log_text = get_git_log()
    entries = parse_git_log(log_text)
    analysis = analyze_commits(entries)
    save_analysis(analysis)
    generate_report(analysis)
    print("Analysis complete!")

if __name__ == "__main__":
    main()
```

### 2. Manual Review of Key Commits

In addition to automated analysis, manually review:

1. Major bug fix commits
2. Commits with detailed comments
3. Commits that touch core functionality

### 3. Issue Tracking Integration

If available, correlate commits with issue tracking systems:

- Link commit messages to issue numbers
- Review issue discussions for context
- Identify resolution patterns

## Expected Outputs

### 1. Git Analysis Report

The script will generate a report (`git_analysis_report.md`) with:

- Most frequently changed files
- Common issue types
- Recent bug fixes
- Recent features added

### 2. Knowledge Base Document

Based on the automated analysis and manual review, we'll create a knowledge base document with:

#### Issue Categories
- UI/GTK Issues
- Image Processing Issues
- AI Integration Issues
- Configuration Issues
- Performance Issues

#### For Each Issue Category
- Common symptoms
- Root causes identified
- Solutions applied
- Areas to handle differently in the rebuild

## Usage in Rebuild Process

### Pre-Implementation
1. Run the analysis script at the beginning of the rebuild
2. Review the report and knowledge base
3. Update component specifications based on findings

### During Implementation
1. Reference the knowledge base when implementing related components
2. Check if a component had frequent changes before finalizing its design
3. Apply known fixes from the original codebase

### Testing Phase
1. Create test cases specifically for previously identified issues
2. Verify the new implementation addresses known problems

## Tool Usage Instructions

To run the Git history analysis:

1. Navigate to the project root
2. Run the analysis script:
   ```bash
   python tools/analyze_git_history.py
   ```
3. Review the generated report in `docs/git_analysis_report.md`
4. Update the knowledge base in `docs/issue_knowledge_base.md` with new findings

## Maintenance

The Git analysis should be re-run:
- At the start of each major development phase
- When encountering issues that might have historical context
- Before finalizing the implementation of frequently-changed components

This ensures that the knowledge from the original codebase is continuously integrated into the rebuild process.

## Conclusion

By systematically analyzing the Git history, we preserve valuable debugging knowledge from the original codebase and avoid rediscovering known issues. This analysis informs both the design and implementation phases of the rebuild, resulting in a more robust application.