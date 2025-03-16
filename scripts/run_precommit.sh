#!/bin/bash

# Script to run pre-commit checks in CI environments
# Usage: ./scripts/run_precommit.sh [options]
#
# Options:
#   --all-files    Run on all files in the repository
#   --staged       Run only on staged files (default)
#   --fix          Attempt to fix issues automatically

set -e

# Default options
CHECK_STAGED=true
FIX_ISSUES=false
ALL_FILES=false

# Parse arguments
for arg in "$@"; do
  case $arg in
    --all-files)
      ALL_FILES=true
      CHECK_STAGED=false
      shift
      ;;
    --staged)
      CHECK_STAGED=true
      ALL_FILES=false
      shift
      ;;
    --fix)
      FIX_ISSUES=true
      shift
      ;;
    *)
      echo "Unknown option: $arg"
      exit 1
      ;;
  esac
done

# Install pre-commit if not already installed
if ! command -v pre-commit &> /dev/null; then
  echo "Installing pre-commit..."
  pip install pre-commit
fi

# Run pre-commit
if [[ "$ALL_FILES" == true ]]; then
  echo "Running pre-commit on all files..."
  if [[ "$FIX_ISSUES" == true ]]; then
    pre-commit run --all-files --fix
  else
    pre-commit run --all-files
  fi
elif [[ "$CHECK_STAGED" == true ]]; then
  echo "Running pre-commit on staged files..."
  if [[ "$FIX_ISSUES" == true ]]; then
    git diff --staged --name-only | xargs pre-commit run --files
  else
    pre-commit run
  fi
fi

echo "Pre-commit checks completed."