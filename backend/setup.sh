#!/bin/bash
# Setup script for Pin-Up AI backend

set -e

echo "Creating virtual environment..."
python3 -m venv .venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

echo "Installing requirements..."
pip install -r requirements.txt

echo "Generating final requirements..."
pip freeze > requirements.txt

echo "✓ Backend setup complete!"
echo "To activate the environment, run: source .venv/bin/activate"
