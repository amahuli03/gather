#!/bin/bash
# Install all dependencies from requirements.txt

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate the virtual environment
source "$SCRIPT_DIR/.venv/bin/activate"

# Install all dependencies
pip install -r requirements.txt

echo "✅ All dependencies installed!"

