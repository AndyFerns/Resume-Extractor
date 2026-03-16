#!/bin/bash
# ===========================================================================
#  run.sh — Quick launcher for the Resume Extractor application (Linux/macOS)
#  Usage:   ./run.sh              (starts server on default port 5000)
#           ./run.sh --port 8080  (starts server on custom port)
# ===========================================================================

set -e

echo "============================================"
echo "  Resume Extractor - Quick Start"
echo "============================================"
echo

# --- Check if virtual environment exists ---
if [ ! -f ".venv/bin/python" ]; then
    echo "[1/3] Creating virtual environment..."
    python3 -m venv .venv
    echo "      Done."
else
    echo "[1/3] Virtual environment already exists."
fi

# --- Install / update dependencies ---
echo "[2/3] Installing dependencies..."
.venv/bin/pip install -q -r requirements.txt

# --- Start the application ---
echo "[3/3] Starting Resume Extractor server..."
echo
echo "      Open http://localhost:5000 in your browser."
echo "      Press Ctrl+C to stop."
echo
.venv/bin/python app.py "$@"
