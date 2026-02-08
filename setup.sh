#!/bin/bash

echo "------------------------------------------------"
echo "   RASPBERRY PI 5 / 4 / ZERO 2 W SETUP          "
echo "   (Python 3.13 Compatible - venv method)       "
echo "------------------------------------------------"

# Ensure we are in the script's directory
cd "$(dirname "$0")"

# 1. Update System
echo "[INFO] Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install System Dependencies
echo "[INFO] Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-opencv \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libhdf5-dev \
    libopenblas-dev \
    libatlas-base-dev \
    libjasper-dev \
    libqtgui4 \
    libqt4-test

# 3. Create Virtual Environment (Critical for Python 3.13+)
# We use --system-site-packages to inherit python3-opencv from apt, 
# which is much faster and more stable than pip wheels on RPi.
echo "[INFO] Setting up Virtual Environment (venv)..."
if [ ! -d "venv" ]; then
    python3 -m venv venv --system-site-packages
    echo "[INFO] venv created."
else
    echo "[INFO] venv already exists."
fi

# 4. Install Python Libraries inside venv
echo "[INFO] Installing Python libraries into venv..."
# 4. Install Python Libraries inside venv
echo "[INFO] Installing Python libraries into venv..."
# source venv/bin/activate # Optional now, we use explicit paths

# Upgrade pip inside venv
./venv/bin/pip install --upgrade pip

# Install dependencies
# Note: We do NOT install opencv-python here because we inherit it from system
./venv/bin/pip install -r requirements.txt

# CRITICAL FIX FOR RPi:
# Ultralytics puts 'opencv-python' back. We MUST remove it to use the system one.
# Otherwise: "Illegal Instruction" (Exit Code -4)
echo "[INFO] Removing conflicting pip-installed OpenCV..."
./venv/bin/pip uninstall -y opencv-python opencv-python-headless

echo "------------------------------------------------"
echo "   SETUP COMPLETE!                              "
echo "------------------------------------------------"
echo "To run the application, use the new launch script:"
echo "   ./run.sh"
echo "------------------------------------------------"
