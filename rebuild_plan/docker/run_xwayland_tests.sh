#!/bin/bash
# Script to run GTK tests using Xwayland in Docker environment
# This provides improved GTK UI testing with a complete X11 server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../.."

HEADLESS="false"
TEST_PATH="tests/ui/"
DOCKER_COMPOSE_FILE="rebuild_plan/docker/docker-compose.yml"

# Process arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --headless)
      HEADLESS="true"
      shift
      ;;
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
      echo "Usage: $0 [--headless] [--test test_path]"
      exit 1
      ;;
  esac
done

echo "Running Xwayland GTK tests with settings:"
echo "  Headless mode: $HEADLESS"
echo "  Test path: $TEST_PATH"

# Build the Docker image if needed
docker-compose -f "$DOCKER_COMPOSE_FILE" build xwayland-test

# Run the tests using the xwayland service
docker-compose -f "$DOCKER_COMPOSE_FILE" run --rm \
  -e HEADLESS=$HEADLESS \
  -e TEST_PATH="$TEST_PATH" \
  xwayland-test pytest "$TEST_PATH" -v

echo "Xwayland GTK tests completed"