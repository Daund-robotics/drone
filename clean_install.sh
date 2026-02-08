#!/bin/bash

# Ensure we are in the script's directory
cd "$(dirname "$0")"

echo "------------------------------------------------"
echo "   FRESH INSTALL: DRONE DETECTION (Picamzero)   "
echo "------------------------------------------------"

# 1. WIPE OLD ENV
if [ -d "venv" ]; then
    echo "[INFO] Wiping old virtual environment..."
    rm -rf venv
fi

# 2. SYSTEM DEPENDENCIES
echo "[INFO] Installing System Dependencies..."
sudo apt-get update
# libcamera and opencv system deps
sudo apt-get install -y \
    python3-opencv \
    libcamera-apps \
    libatlas-base-dev \
    libopenblas-dev \
    libgl1-mesa-glx

# 3. CREATE VENV
echo "[INFO] Creating fresh Virtual Environment..."
# --system-site-packages is CRITICAL to use python3-opencv from apt
python3 -m venv venv --system-site-packages

# 4. INSTALL PYTHON LIBS
echo "[INFO] Installing Python Libraries into venv..."
./venv/bin/pip install --upgrade pip

# Install specific deps for RPi (Picamzero + Ultralytics)
# We exclude opencv-python from requirements.txt via grep to be safe, 
# or we just install explicitly here.
./venv/bin/pip install picamzero ultralytics psutil "numpy<2.0.0"

# 5. CLEANUP CONFLICTS
echo "[INFO] Removing conflicting OpenCV versions..."
./venv/bin/pip uninstall -y opencv-python opencv-python-headless

echo "------------------------------------------------"
echo "   INSTALL COMPLETE                             "
echo "------------------------------------------------"
echo "1. Run: ./run.sh"
