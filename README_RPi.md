# Raspberry Pi Drone Detection (Python 3.13+)

## 🚀 Setup & Installation

This project is optimized for Raspberry Pi 4 / 5 / Zero 2 W running the latest Raspberry Pi OS (Bookworm/Python 3.13).
It uses a **Virtual Environment (venv)** to ensure stability and prevent "Illegal Instruction" errors common with mixed OpenCV versions.

### 1. Run the Setup Script
Open a terminal in the project folder and run:

```bash
chmod +x setup.sh run.sh
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
