# RPi 4 Drone Detection - Quick Start

## How to Run
1.  **Update Repo**:
    ```bash
    git pull origin main
    ```
2.  **Run Setup (Critical for first run)**:
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```
    *This fixes the "Illegal Instruction" (Exit Code -4) crash by installing compatible NumPy.*

3.  **Run the App**:
    ```bash
    python3 main_pi.py
    ```

## Troubleshooting
- **"Exit Code -4" / "Illegal Instruction"**:
  - **Cause**: Compatible NumPy version was overwritten by a newer one (2.x).
  - **Fix 1 (Recommended)**:
    ```bash
    ./setup.sh
    ```
  - **Fix**:
    ```bash
    # Remove broken pip versions
    pip3 uninstall -y opencv-python opencv-python-headless numpy
    # Install stable system version
    sudo apt-get install -y python3-opencv
    # Reinstall numpy compatible with system
    pip3 install "numpy<2.0.0" --break-system-packages
    ```

- **"Camera not found"**: 
  - Check ribbon cable.
  - Run `libcamera-hello` to test.
