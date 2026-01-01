#!/bin/bash
# Script to run the FastAPI service

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate the virtual environment
source "$SCRIPT_DIR/.venv/bin/activate"

# Change to project root directory (important for imports)
cd "$SCRIPT_DIR"

# Run FastAPI with uvicorn
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000


