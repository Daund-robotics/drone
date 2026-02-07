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
# Remove PIP versions of OpenCV as they often crash RPi (Illegal Instruction)
pip3 uninstall -y opencv-python opencv-python-headless numpy

echo "[INFO] Installing System Dependencies (Stable OpenCV)..."
# Use the official RPi built OpenCV - it is much more stable than pip wheels
sudo apt-get update
sudo apt-get install -y python3-opencv libhdf5-dev libatlas-base-dev

echo "[INFO] Installing Python libraries..."
pip3 install --upgrade pip

# Install Ultralytics and Utils (Pinning NumPy to <2.0 for best compatibility)
# We do NOT install opencv-python here because we installed python3-opencv via apt
pip3 install "numpy<2.0.0" ultralytics psutil --break-system-packages

echo "------------------------------------------------"
echo "   SETUP COMPLETE!                              "
echo "   Run the app with: python3 main_pi.py         "
echo "------------------------------------------------"
echo "   BACKUP PLAN: If it still crashes, run:       "
echo "   pip3 install \"numpy<2.0.0\" --force-reinstall"
echo "------------------------------------------------"
