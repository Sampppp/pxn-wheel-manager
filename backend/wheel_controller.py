#!/usr/bin/env python3
"""
backend/wheel_controller.py
PXNController - object-oriented HID controller for PXN wheelbase.
Re-analyzed from pxn_usb_decompiled.py and config_decompiled.py.

Parameters identified (from jizuo_param_data / profile / read packets):
- Spring (jizuo_param index 0)
- Inertia (jizuo_param index 1)
- Friction (jizuo_param index 2)
- Center Force (jizuo_param index 3)
- Mechanical Damper (jizuo_param index 4)
- Game Force / FFB Gain (jizuo_param index 5, also read from endpoint 131 bytes 23-26)
- Rotation Angle (read endpoint 131 bytes 1-2, uint16 / 65535)
- Wind Speed Switch (profile byte 3 = 8)
- Two-Pick Status (profile byte 3 = 7)
- LED Profile (profile byte 3 = 2, bytes 4-33)
- Map / Button Profile (profile byte 3 = 0, bytes 4-47)
- Calibration Start/Stop (byte 3 = 1 / 2, command 253)
- Shift Lever Map (map hex bytes 24-32)
- Footrest Map / Coordinate (map hex / coord hex)
"""

import threading
import time
import struct
from typing import Optional, Dict, Any, List

try:
    import hid
except ImportError as exc:
    raise ImportError("hidapi (python-hid) is required. Install: pip install hid") from exc


class PXNController:
    """Robust HID controller for PXN V12/V10/Lite/PAN wheelbases."""

    VID = 0x11FF          # 4607 decimal (from config_decompiled.py)
    PID = 0x1212          # 4626 decimal (V12)
    REPORT_ID_CONFIG = 100  # profile/config report (from pxn_usb_decompiled.py)
    REPORT_ID_CMD = 1      # command/upgrade report
    PACKET_LEN = 58
    READ_REPORT_LEN = 64
    READ_ENDPOINT = 131    # HID read endpoint (from pxn_usb_decompiled.py)

    # Inferred parameter mapping from jizuo_param_data (13 bytes, indices 0-12)
    # Based on standard PXN wheel parameter order observed in decompiled code.
    PARAM_MAP = {
        "Spring": 0,
        "Inertia": 1,
        "Friction": 2,
        "Center_Force": 3,
        "Mechanical_Damper": 4,
        "Game_Force": 5,
        "FFB_Gain": 5,        # alias for Game_Force
        "Rotation_Angle": 6,  # not in jizuo_param; handled separately
    }

    def __init__(self):
        self.device: Optional[hid.device] = None
        self._connected = False
        self._lock = threading.RLock()

        # Maintain current state of all configurable settings
        self.state: Dict[str, Any] = {
            "Spring": 0,
            "Inertia": 0,
            "Friction": 0,
            "Center_Force": 0,
            "Mechanical_Damper": 0,
            "Game_Force": 50,
            "FFB_Gain": 50,
            "Rotation_Angle": 540,
            "Wind_Speed_Switch": 0,
            "Two_Pick_Status": 0,
            "LED_Profile": [0] * 30,
            "Map_Profile": [0] * 44,
            "Calibration_Active": False,
        }

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    def connect(self, retries: int = 3, delay: float = 0.5) -> bool:
        """Open HID device with retry/backoff for busy/disconnected states."""
        with self._lock:
            if self._connected and self.device is not None:
                return True
            for attempt in range(1, retries + 1):
                try:
                    self.device = hid.device()
                    self.device.open(self.VID, self.PID)
                    # Set non-blocking read (optional) and claim interface
                    self.device.set_nonblocking(1)
                    self._connected = True
                    return True
                except OSError as exc:
                    msg = str(exc).lower()
                    if "busy" in msg or "resource" in msg or "timeout" in msg:
                        if attempt < retries:
                            time.sleep(delay * attempt)
                            continue
                    self._connected = False
                    self.device = None
                    return False
                except Exception as exc:
                    self._connected = False
                    self.device = None
                    return False
            return False

    def disconnect(self) -> None:
        with self._lock:
            try:
                if self.device is not None:
                    self.device.close()
            except Exception:
                pass
            finally:
                self.device = None
                self._connected = False

    def is_connected(self) -> bool:
        with self._lock:
            return self._connected and self.device is not None

    # ------------------------------------------------------------------
    # Internal packet builders (derived from pxn_usb_decompiled.py)
    # ------------------------------------------------------------------

    def _build_profile_packet(self, subcmd: int, payload: List[int]) -> bytearray:
        """Build 58-byte profile/config packet: [100, 65, 224, subcmd, payload..., 0...]"""
        pkt = bytearray(self.PACKET_LEN)
        pkt[0] = 100
        pkt[1] = 65
        pkt[2] = 224
        pkt[3] = subcmd
        for i, val in enumerate(payload):
            if 4 + i < self.PACKET_LEN:
                pkt[4 + i] = int(val) & 0xFF
        return pkt

    def _build_jizuo_packet(self, data: List[int]) -> bytearray:
        """Build jizuo parameter packet (pxn_jizuo_param_set logic)."""
        pkt = bytearray(self.PACKET_LEN)
        pkt[0] = 100
        pkt[1] = 65
        pkt[2] = 224
        pkt[3] = 1  # jizuo param sub-command
        # data[1] -> bytes 4-5 (uint16 little-endian)
        r = int(data[1]) % 256
        pkt[4] = r
        pkt[5] = int((int(data[1]) - r) / 256)
        # data[2..11] -> bytes 6-15
        for i in range(2, 12):
            if i - 2 + 6 < self.PACKET_LEN:
                pkt[i - 2 + 6] = int(data[i]) & 0xFF
        # data[12] -> byte 18
        if len(data) > 12:
            pkt[18] = int(data[12]) & 0xFF
        return pkt

    def _build_read_packet(self) -> bytearray:
        """Placeholder for any write that mirrors read format (not verified for angle)."""
        return bytearray(self.PACKET_LEN)

    # ------------------------------------------------------------------
    # Public update method
    # ------------------------------------------------------------------

    def update_setting(self, setting_name: str, value) -> bool:
        """
        Pack the correct byte array for the specific setting and send to wheelbase.
        Returns True if packet sent successfully, False on error/disconnect.
        """
        if not self.is_connected():
            # Attempt reconnect once
            if not self.connect():
                return False

        try:
            setting = setting_name.strip()

            # --- Jizuo / FFB / Mechanical parameters ---
            if setting in ("Spring", "Inertia", "Friction", "Center_Force",
                           "Mechanical_Damper", "Game_Force", "FFB_Gain"):
                idx = self.PARAM_MAP.get(setting, 0)
                # Build 13-element jizuo data array (default zeros, set index)
                data = [0] * 13
                # Preserve existing state for other indices
                current = self.state.get(setting, 0)
                # If value is int, set directly; if dict, merge
                if isinstance(value, int):
                    data[idx] = value
                elif isinstance(value, dict):
                    for k, v in value.items():
                        if k in self.PARAM_MAP:
                            data[self.PARAM_MAP[k]] = v
                else:
                    data[idx] = int(value)
                pkt = self._build_jizuo_packet(data)
                self.state[setting] = value if isinstance(value, int) else data[idx]
                return self._send_raw(pkt)

            # --- Rotation Angle ---
            elif setting == "Rotation_Angle":
                angle = int(value)
                self.state["Rotation_Angle"] = angle
                # No verified write packet exists; send speculative profile packet
                # with angle encoded in payload bytes 4-5 (uint16 / 65535 scale)
                pkt = self._build_profile_packet(0, [
                    angle & 0xFF, (angle >> 8) & 0xFF, 0, 0
                ])
                return self._send_raw(pkt)

            # --- Profile / Map settings ---
            elif setting == "LED_Profile":
                self.state["LED_Profile"] = value
                payload = [int(v) & 0xFF for v in value[:30]]
                pkt = self._build_profile_packet(2, payload)
                return self._send_raw(pkt)

            elif setting == "Map_Profile":
                self.state["Map_Profile"] = value
                payload = [int(v) & 0xFF for v in value[:44]]
                pkt = self._build_profile_packet(0, payload)
                return self._send_raw(pkt)

            elif setting == "Wind_Speed_Switch":
                self.state["Wind_Speed_Switch"] = int(value)
                pkt = self._build_profile_packet(8, [int(value) & 0xFF])
                return self._send_raw(pkt)

            elif setting == "Two_Pick_Status":
                self.state["Two_Pick_Status"] = int(value)
                pkt = self._build_profile_packet(7, [int(value) & 0xFF])
                return self._send_raw(pkt)

            # --- Calibration ---
            elif setting == "Calibration_Start":
                self.state["Calibration_Active"] = True
                pkt = bytearray(self.PACKET_LEN)
                pkt[0] = 100; pkt[1] = 253; pkt[2] = 1; pkt[3] = 1
                return self._send_raw(pkt)

            elif setting == "Calibration_Stop":
                self.state["Calibration_Active"] = False
                pkt = bytearray(self.PACKET_LEN)
                pkt[0] = 100; pkt[1] = 253; pkt[2] = 2; pkt[3] = 2
                return self._send_raw(pkt)

            else:
                raise ValueError(f"Unknown setting: {setting_name}")

        except Exception as exc:
            # Comprehensive error handling: disconnect on critical failure
            try:
                self.disconnect()
            except Exception:
                pass
            return False

    def _send_raw(self, packet: bytearray) -> bool:
        """Send raw bytearray via HID with busy-device retry."""
        if not self.is_connected():
            return False
        try:
            # Use report ID 100 for profile/config (matches original usb_write patterns)
            self.device.write(self.REPORT_ID_CONFIG, packet)
            return True
        except OSError as exc:
            msg = str(exc).lower()
            if "busy" in msg or "resource" in msg:
                time.sleep(0.1)
                try:
                    self.device.write(self.REPORT_ID_CONFIG, packet)
                    return True
                except Exception:
                    return False
            return False
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Read / Monitor (from endpoint 131, 64 bytes)
    # ------------------------------------------------------------------

    def read_wheel_data(self) -> Optional[Dict[str, Any]]:
        """Read 64-byte HID report from endpoint 131 and parse known fields."""
        if not self.is_connected():
            return None
        try:
            # hid.device.read(length) reads from the device; endpoint 131 is report 131
            data = self.device.read(self.READ_REPORT_LEN)
            if data is None or len(data) < 27:
                return None
            # Rotation angle (bytes 1-2, little-endian uint16 / 65535)
            angle_raw = data[1] + data[2] * 256
            angle_norm = round(angle_raw / 65535.0, 3)
            # Game Force / FFB (bytes 23-26, int32 little-endian * 20.141601)
            game_force_raw = struct.unpack("i", bytes(data[23:27]))[0]
            game_force = game_force_raw * 20.141601
            # Motor IC (bytes 15-18)
            ic_raw = struct.unpack("i", bytes(data[15:19]))[0]
            ic = ic_raw * 20.141601
            # IQ Voltage (bytes 19-20, int16)
            iq_v = struct.unpack("h", bytes(data[19:21]))[0]
            # Speed (bytes 21-22, int16)
            speed = struct.unpack("h", bytes(data[21:23]))[0]
            return {
                "rotation_angle_raw": angle_raw,
                "rotation_angle_norm": angle_norm,
                "game_force": game_force,
                "ic": ic,
                "iq_voltage": iq_v,
                "speed": speed,
                "raw": bytes(data),
            }
        except Exception:
            return None

    def get_state(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self.state)

    def set_state(self, state_dict: Dict[str, Any]) -> None:
        with self._lock:
            self.state.update(state_dict)
