#!/bin/bash
# Quick launcher for the Magical Story Generator

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Running 'uv sync'..."
    uv sync
fi

echo "Starting Magical Story Generator..."
echo ""

.venv/bin/python main.py

