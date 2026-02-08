#!/bin/bash

# Ensure we are in the script's directory
cd "$(dirname "$0")"

# Activate the virtual environment
source venv/bin/activate

# Run the main script
# Run the main script using the venv python explicitly
./venv/bin/python3 main_pi.py
