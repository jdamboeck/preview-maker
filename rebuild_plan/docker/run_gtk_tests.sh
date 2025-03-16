#!/bin/bash
# Script to run GTK tests in a Docker container with Xvfb

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../.."

TEST_PATH="tests/ui/"

# Process arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --test)
      if [[ -n "$2" && "$2" != --* ]]; then
        TEST_PATH="$2"
        shift 2
      else
        echo "Error: --test requires a path argument"
        exit 1
      fi
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--test test_path]"
      exit 1
      ;;
  esac
done

echo "Running GTK tests with settings:"
echo "  Test path: $TEST_PATH"

# Build the Docker image if needed
docker build -f "$SCRIPT_DIR/Dockerfile.gtk-test" -t preview-maker:gtk-test "$SCRIPT_DIR"

# Run the tests
docker run --rm -v "$(pwd):/app" preview-maker:gtk-test "$TEST_PATH" -v

echo "GTK tests completed"