#!/bin/bash
# MOGLabs CEM Application Launcher
# Usage:
#   ./run_cem.sh              - Normal mode (discovers device)
#   ./run_cem.sh --offline    - Offline mode (no device required)
#   ./run_cem.sh --mog        - Internal/debug logging mode

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found. Please install Python 3.8+"
    exit 1
fi

if ! python3 -c "import PySide6" 2>/dev/null && ! python3 -c "import PySide2" 2>/dev/null; then
    echo "PySide not found. Installing dependencies..."
    pip3 install -r requirements.txt
fi

echo "Starting MOGLabs CEM v1.0.1..."
python3 -m cem_app "$@" 2>&1 || python3 __main__.py "$@" 2>&1
