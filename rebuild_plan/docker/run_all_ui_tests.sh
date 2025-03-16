#!/bin/bash
# Script to run all UI tests for Preview Maker

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../.."

echo "Running all UI tests for Preview Maker"
echo "======================================"

# Run the GTK tests
echo "Running GTK UI tests..."
./rebuild_plan/docker/run_gtk_tests.sh --test tests/ui/

echo ""
echo "All UI tests completed successfully!"