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

# Install main packages
pip3 install opencv-python ultralytics psutil --break-system-packages

# CRITICAL FIX: Force downgrade NumPy to 1.x AFTER other packages are installed
# This overrides whatever version ultralytics/opencv pulled in.
echo "[INFO] Forcing NumPy 1.26.4 to prevent SIGILL crashes..."
pip3 install "numpy==1.26.4" --force-reinstall --break-system-packages

echo "------------------------------------------------"
echo "   SETUP COMPLETE!                              "
echo "   Run the app with: python3 main_pi.py         "
echo "------------------------------------------------"
echo "   BACKUP PLAN: If it still crashes, run:       "
echo "   pip3 install \"numpy<2.0.0\" --force-reinstall"
echo "------------------------------------------------"
