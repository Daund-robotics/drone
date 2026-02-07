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
pip3 uninstall -y numpy opencv-python ultralytics

echo "[INFO] Installing Python libraries..."
pip3 install --upgrade pip

# CRITICAL FIX: 
# opencv-python 4.13+ requires numpy 2.x, which crashes RPi.
# We MUST pin opencv-python to an older version that supports numpy 1.x.
# We also implicitly pin numpy<2.0.0
echo "[INFO] Installing specific compatible versions (OpenCV 4.10, NumPy 1.26)..."

# Install strict versions known to work on RPi Bullseye/Bookworm
pip3 install "numpy<2.0.0" "opencv-python<=4.10.0.84" ultralytics psutil --break-system-packages

echo "------------------------------------------------"
echo "   SETUP COMPLETE!                              "
echo "   Run the app with: python3 main_pi.py         "
echo "------------------------------------------------"
echo "   BACKUP PLAN: If it still crashes, run:       "
echo "   pip3 install \"numpy<2.0.0\" --force-reinstall"
echo "------------------------------------------------"
