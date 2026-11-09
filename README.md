# PXN Custom Manager

Reverse-engineered desktop manager for PXN wheelbases (V12/V10/Lite/PAN).

## Structure

- `backend/` — FastAPI + PyWebView desktop launcher; `PXNController` HID interface
- `frontend/` — React + Vite + Tailwind dark-mode UI (Pit House aesthetic)
- `test_angle.py` — Minimal HID packet test script
- `pxn_usb_config_table.md` — Reverse-engineered byte structures

## Dependencies

### All platforms

- Python 3.11+
- Node.js LTS (for frontend build) — install from https://nodejs.org
- `npm` comes with Node.js; on Windows make sure it is in PATH

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y libgtk-3-dev libwebkit2gtk-4.1-dev pkg-config \
  libhidapi-dev libhidapi-libusb0 libhidapi-hidraw0 python3-gi python3-gi-cairo
```

### Windows

- Install Python 3.11+ from https://python.org (check "Add to PATH")
- Install Node.js LTS from https://nodejs.org (includes `npm`)
- The `hid` package needs `hidapi` DLLs. On Windows:
  - Download `hidapi` release from https://github.com/libusb/hidapi/releases
  - Place `hidapi.dll` (or `libhidapi-0.dll`) in `.venv\Lib\site-packages\hid\` or in `C:\Windows\System32`
  - Alternatively install via `pip install hid` after ensuring `hidapi.dll` is in PATH
- `pywebview` on Windows uses Edge WebView2 (built into Windows 10/11) or Qt
  - If Qt backend needed: `pip install PyQt6 PyQt6-WebEngine`
  - If Edge/WebView2 missing, install from https://developer.microsoft.com/en-us/microsoft-edge/webview2/
- `wheel_controller.py` uses `pyusb` (not `hid`). Install with `pip install pyusb`.
- `pywebview` uses Windows Edge WebView2 by default; no Qt needed.
- If `pywebview` still fails, install `PyQt6-WebEngine` via pip (`pip install PyQt6-WebEngine`) as fallback.

## Build & Run (as simple as possible)

1. Install Python backend dependencies:

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install -r backend/requirements.txt
```

2. Build the frontend (only needed once, or after frontend changes):

```bash
cd frontend
npm install
npm run build
cd ..
```

3. Run the app:

```bash
# Linux/macOS
.venv/bin/python backend/main.py
# Windows
.venv\Scripts\python backend\main.py
```

The desktop window opens at `http://127.0.0.1:8120` (frameless, dark mode). The backend serves `frontend/dist/` automatically via `StaticFiles` using a dynamic path relative to the project root.

## Key Features

- **USB/HID**: `PXNController` connects to VID `0x11FF` / PID `0x1212`
- **Settings**: Spring, Inertia, Friction, Center Force, Mechanical Damper, Game Force / FFB Gain, Rotation Angle, LED/Map profiles, Calibration
- **Debounced updates**: 200ms delay on slider drag to prevent USB flooding
- **Real-time read**: Endpoint 131 (64 bytes) parses rotation angle, game force, motor data

## Reverse-Engineering Notes

Packet structures derived from `pxn_usb_decompiled.py` and `config_decompiled.py` (extracted from `pxn.exe` PyInstaller bundle). Rotation angle and FFB are read from HID endpoint 131; profile/config writes use endpoint 3 (`[100, 65, 224, ...]`).

## USB / Wheelbase

- Connect PXN wheelbase via USB
- VID `0x11FF` (4607), PID `0x1212` (4626)
- If device busy, retry after 1-2 seconds
