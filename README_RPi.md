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
  - Cause: Incompatible `numpy` version (2.x).
  - Fix: Run `./setup.sh` again.
- **"Camera not found"**: 
  - Check ribbon cable.
  - Run `libcamera-hello` to test.
