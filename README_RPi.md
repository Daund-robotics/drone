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
    *(This now forcefully installs compatible versions)*
  - **Fix 2 (Manual)**:
    ```bash
    pip3 install "numpy<2.0.0" "opencv-python<=4.10.0.84" --break-system-packages
    ```

- **"Camera not found"**: 
  - Check ribbon cable.
  - Run `libcamera-hello` to test.
