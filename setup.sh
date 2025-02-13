#!/bin/bash

# Create virtual environment if it doesn't exist
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

echo "Setup complete! Virtual environment is created and packages are installed."
echo "To activate the virtual environment, run: source .venv/bin/activate"
