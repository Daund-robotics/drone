#!/bin/bash

echo "------------------------------------------------"
echo "   RASPBERRY PI 4 DRONE DETECTION SETUP         "
echo "------------------------------------------------"

# 1. Update System
echo "[INFO] Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install System Dependencies (Crucial for OpenCV on RPi)
echo "[INFO] Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libatlas-base-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libjasper-dev \
    libqtgui4 \
    libqt4-test

# 3. Create Virtual Environment (Optional but recommended, uncomment if needed)
# echo "[INFO] Creating virtual environment..."
# python3 -m venv venv
# source venv/bin/activate

# 4. Install Python Libraries
echo "[INFO] Cleaning up potential conflicting libraries..."
# Remove numpy 2.x if present, as it causes SIGILL (Exit Code -4) on some RPi configs with OpenCV
pip3 uninstall -y numpy opencv-python ultralytics

echo "[INFO] Installing Python libraries (Pinning NumPy < 2.0)..."
pip3 install --upgrade pip
# Force NumPy < 2.0.0 to avoid binary incompatibility ("Illegal Instruction")
pip3 install "numpy<2.0.0"
pip3 install opencv-python ultralytics psutil

echo "------------------------------------------------"
echo "   SETUP COMPLETE!                              "
echo "   Run the app with: python3 main_pi.py         "
echo "------------------------------------------------"
