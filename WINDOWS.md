# Windows Build & Run Guide

## 1. Python environment

- Install Python 3.11+ from https://python.org (check "Add to PATH")
- Create venv: `python -m venv .venv`
- Activate: `.venv\Scripts\activate`
- Install backend: `pip install -r backend/requirements.txt`

## 2. HID / USB dependencies (Windows)

The `hid` package needs `hidapi` DLLs. On Windows:

- Download `hidapi` release from https://github.com/libusb/hidapi/releases
- Place `hidapi.dll` (or `libhidapi-0.dll`) in `.venv\Lib\site-packages\hid\` or in `C:\Windows\System32`
- Alternatively install via `pip install hid` after ensuring `hidapi.dll` is in PATH

## 3. PyWebView (desktop window)

- `pywebview` on Windows uses Edge WebView2 (built into Windows 10/11) or Qt
- If Qt backend needed: `pip install PyQt6 PyQt6-WebEngine`
- If Edge/WebView2 missing, install from https://developer.microsoft.com/en-us/microsoft-edge/webview2/

## 4. Frontend (React + Vite)

- Install Node.js LTS from https://nodejs.org
- `cd frontend`
- `npm install`
- `npm run build` (creates `dist/`)

## 5. Run

```cmd
.venv\Scripts\python backend\main.py
```

The frameless dark window opens at `http://127.0.0.1:8120`. The backend serves `frontend/dist/` automatically.

## 6. USB / Wheelbase

- Connect PXN wheelbase via USB
- VID `0x11FF` (4607), PID `0x1212` (4626)
- If device busy, retry after 1-2 seconds

## No hid / No PyQt6 needed

- `wheel_controller.py` now uses `pyusb` (not `hid`). Install with `pip install pyusb`.
- `pywebview` uses Windows Edge WebView2 by default; no Qt needed.
- If `pywebview` still fails, install `PyQt6-WebEngine` via pip (`pip install PyQt6-WebEngine`) as fallback.

## Building frontend without npm in PowerShell

If `npm` is unavailable:
1. Build on Linux/Mac: `cd frontend && npm install && npm run build`
2. Copy the resulting `frontend/dist/` folder to Windows (`scp`, USB, etc.)
3. Place it next to `backend/` so `main.py` finds `/home/spak/wb/pxn-wheel-manager/frontend/dist/` (adjust path in `main.py` if needed)
