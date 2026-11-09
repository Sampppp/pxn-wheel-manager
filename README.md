# PXN Custom Manager

Reverse-engineered desktop manager for PXN wheelbases (V12/V10/Lite/PAN).

## Structure

- `backend/` — FastAPI + PyWebView desktop launcher; `PXNController` HID interface
- `frontend/` — React + Vite + Tailwind dark-mode UI (Pit House aesthetic)
- `test_angle.py` — Minimal HID packet test script
- `pxn_usb_config_table.md` — Reverse-engineered byte structures

## Quick Start

### 1. System dependencies (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y libgtk-3-dev libwebkit2gtk-4.1-dev pkg-config \
  libhidapi-dev libhidapi-libusb0 libhidapi-hidraw0 python3-gi python3-gi-cairo
```

### 2. Python backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
.venv/bin/python backend/main.py
```

The desktop window opens at `http://127.0.0.1:8120` (frameless, dark mode).

### 3. Frontend build (if not using pre-built `dist/`)

```bash
cd frontend
npm install
npm run build
```

The backend serves `frontend/dist/` automatically via `StaticFiles`.

## Key Features

- **USB/HID**: `PXNController` connects to VID `0x11FF` / PID `0x1212`
- **Settings**: Spring, Inertia, Friction, Center Force, Mechanical Damper, Game Force / FFB Gain, Rotation Angle, LED/Map profiles, Calibration
- **Debounced updates**: 200ms delay on slider drag to prevent USB flooding
- **Real-time read**: Endpoint 131 (64 bytes) parses rotation angle, game force, motor data

## Reverse-Engineering Notes

Packet structures derived from `pxn_usb_decompiled.py` and `config_decompiled.py` (extracted from `pxn.exe` PyInstaller bundle). Rotation angle and FFB are read from HID endpoint 131; profile/config writes use endpoint 3 (`[100, 65, 224, ...]`).
