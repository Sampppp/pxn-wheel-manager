#!/usr/bin/env python3
"""
backend/main.py
FastAPI REST backend + PyWebView frameless desktop launcher.
Exposes PXNController settings via REST; launches React frontend in dark frameless window.
"""

import threading
import time
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Optional, Dict

# Import controller from sibling module
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wheel_controller import PXNController

# ------------------------------------------------------------------
# FastAPI setup
# ------------------------------------------------------------------

app = FastAPI(title="PXN Custom Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

controller = PXNController()

class SettingUpdate(BaseModel):
    setting_name: str
    value: Any

# ------------------------------------------------------------------
# REST endpoints
# ------------------------------------------------------------------

@app.get("/api/settings")
def get_settings():
    """Return current state of all PXN settings."""
    return {"status": "ok", "data": controller.get_state(), "connected": controller.is_connected()}

@app.post("/api/settings")
def update_setting(payload: SettingUpdate):
    """Update a single setting and send USB packet."""
    ok = controller.set_parameter(payload.setting_name, payload.value)
    return {"status": "ok" if ok else "error", "sent": ok, "setting": payload.setting_name}

@app.get("/api/read")
def read_wheel():
    """Read live HID data from endpoint 131."""
    data = controller.read_wheel_data()
    return {"status": "ok", "data": data}

@app.post("/api/connect")
def connect_wheel():
    ok = controller.connect()
    return {"status": "ok" if ok else "error", "connected": ok}

@app.post("/api/disconnect")
def disconnect_wheel():
    controller.disconnect()
    return {"status": "ok", "connected": False}

# ------------------------------------------------------------------
# PyWebView launcher (frameless, dark-mode desktop window)
# ------------------------------------------------------------------


# Serve built React frontend (build with: cd frontend && npm install && npm run build)
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_static_dir = os.path.join(_project_root, "frontend", "dist")
app.mount("/", StaticFiles(directory=_static_dir, html=True), name="static")

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8120, log_level="warning")

def launch_desktop():
    import webview
    # Start FastAPI in background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    # Give server time to bind
    time.sleep(2.0)
    # Launch frameless dark window pointing to React frontend
    try:
        window = webview.create_window(
            title="PXN Custom Manager",
            url="http://127.0.0.1:8120",
            width=1200,
            height=800,
            min_size=(900, 600),
            easy_drag=True,
            resizable=True,
            shadow=True,
            transparent=False,
        )
        def on_loaded():
            try:
                window.evaluate_js("document.body.style.backgroundColor = '#0f0f1a';")
            except Exception:
                pass
        window.events.loaded += on_loaded
        webview.start()
    except Exception as exc:
        print("WebView failed to start:", exc)
        print("Ensure frontend is built and server is running at http://127.0.0.1:8120")

if __name__ == "__main__":
    launch_desktop()
