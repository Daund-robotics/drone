# Raspberry Pi Drone Detection (Python 3.13+)

## 🚀 Quick Start (Fresh Install)

**Recommended for first-time setup or if you are facing issues.**

1.  **Run the Fresh Install Script:**
    This will set up the Virtual Environment, install `picamzero`, `ultralytics`, and remove conflicting libraries automatically.
    ```bash
    chmod +x clean_install.sh
    ./clean_install.sh
    ```

2.  **Run the Application:**
    ```bash
    ./run.sh
    ```

### Legacy Setup (Update only)
If you just want to update dependencies without wiping everything:
```bash
./setup.sh
```

**What this does:**
- Updates system packages
- Installs `python3-opencv` (Stable system version)
- Creates a virtual environment (`venv`)
- Installs `ultralytics` (YOLO) and `psutil` into the `venv`
- Pins `numpy` to a compatible version (<2.0)

### 2. Run the Application
Always use the `run.sh` script to start the detection. This auto-activates the virtual environment.

```bash
./run.sh
```

or manually:

```bash
source venv/bin/activate
python3 main_pi.py
```

## ⚠️ Troubleshooting

**"Illegal Instruction" Error:**
- This means an incompatible version of NumPy or OpenCV was installed.
- **Fix:** Run `./setup.sh` again to rebuild the environment with correct pinning.

**Camera not opening:**
- Ensure you are using the correct mode (CSI vs USB) in `camera_stream.py`.
- For CSI cameras on new OS, you might need to enable Legacy Camera support in `raspi-config` or use `libcamera`.

## 📂 Key Files
- `main_pi.py`: Main logic for RPi.
- `setup.sh`: Installation script (Use this!).
- `run.sh`: Launcher script (Use this!).
- `requirements.txt`: Python dependencies.
