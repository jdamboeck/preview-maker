#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install package in development mode with test dependencies
echo "Installing package in development mode..."
pip install -e ".[dev]"

# Create necessary directories
mkdir -p tests/core
mkdir -p preview_maker/core/tests

echo "Development environment setup complete!"