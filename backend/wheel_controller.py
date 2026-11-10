#!/usr/bin/env python3
"""
backend/wheel_controller.py
PXNController - object-oriented USB controller for PXN wheelbase.
Updated to use pyusb and the verified Control Gate (Interface 2, EP 3).
"""

import threading
import time
import struct
import usb.core
import usb.util
import libusb_package
from typing import Optional, Dict, Any, List

class PXNController:
    """Robust USB controller for PXN V12/V10/Lite/PAN wheelbases."""

    VID = 0x11FF
    PID = 0x1212
    
    # USB Topology
    INTF_TELEMETRY = 0
    EP_TELEMETRY_IN = 0x81
    
    INTF_CONTROL = 2
    EP_CONTROL_OUT = 0x03
    EP_CONTROL_IN = 0x83
    
    PACKET_LEN = 58
    READ_REPORT_LEN = 64

    # Parameter Mapping (Based on RE and Physical Testing)
    # Offset is the byte position in the 58-byte packet
    PARAM_MAP = {
        "Angle": {"offset": 4, "type": "uint16"},
        "Rotation_Angle": {"offset": 4, "type": "uint16"},
        "Force_Feedback": {"offset": 6, "type": "byte"},
        "FFB_Gain": {"offset": 6, "type": "byte"},
        "Elasticity": {"offset": 7, "type": "byte"},
        "Damping_Force": {"offset": 8, "type": "byte"},
        "Sine_Force": {"offset": 9, "type": "byte"},
        "Inertial_Force": {"offset": 10, "type": "byte"},
        "Max_Torque": {"offset": 11, "type": "byte"},
        "Max_Rotational_Speed": {"offset": 12, "type": "byte"},
        "Mechanical_Centering_Force": {"offset": 13, "type": "byte"},
        "Mechanical_Damping_Force": {"offset": 14, "type": "byte"},
        "Road_Sensation_Perception": {"offset": 15, "type": "byte"},
        "Mystery_Param": {"offset": 18, "type": "byte"},
    }

    def __init__(self):
        self.device = None
        self._connected = False
        self._lock = threading.RLock()
        self.backend = libusb_package.get_libusb1_backend()

        # Current state of all configurable settings
        self.state: Dict[str, Any] = {
            "Angle": 540,
            "Force_Feedback": 50,
            "Elasticity": 50,
            "Damping_Force": 50,
            "Sine_Force": 50,
            "Inertial_Force": 50,
            "Max_Torque": 50,
            "Max_Rotational_Speed": 50,
            "Mechanical_Centering_Force": 50,
            "Mechanical_Damping_Force": 50,
            "Road_Sensation_Perception": 50,
            "Mystery_Param": 0,
        }

    def connect(self) -> bool:
        """Connect to the device and perform the unlock sequence."""
        with self._lock:
            try:
                self.device = usb.core.find(idVendor=self.VID, idProduct=self.PID, backend=self.backend)
                if self.device is None:
                    print("Device not found.")
                    return False

                # Set configuration
                self.device.set_configuration()

                # Claim both interfaces
                usb.util.claim_interface(self.device, self.INTF_TELEMETRY)
                usb.util.claim_interface(self.device, self.INTF_CONTROL)

                # Perform the mandatory unlock sequence
                if self._initialize_device():
                    self._connected = True
                    print("PXN Wheelbase connected and unlocked.")
                    return True
                
                return False
            except Exception as e:
                print(f"Connection error: {e}")
                self._connected = False
                return False

    def _initialize_device(self) -> bool:
        """Executes the verified unlock sequence to enable control."""
        try:
            # 1. Base Info Handshake
            pkt = bytearray(self.PACKET_LEN)
            pkt[0]=100; pkt[1]=129; pkt[2]=1
            self.device.write(self.EP_CONTROL_OUT, pkt, timeout=1000)
            time.sleep(0.1)

            # 2. Profile Sequence [0, 2, 3, 4, 1]
            for subcmd in [0, 2, 3, 4, 1]:
                pkt = bytearray(self.PACKET_LEN)
                pkt[0]=100; pkt[1]=129; pkt[2]=224; pkt[3]=subcmd
                self.device.write(self.EP_CONTROL_OUT, pkt, timeout=1000)
                time.sleep(0.1)
            
            return True
        except Exception as e:
            print(f"Initialization failed: {e}")
            return False

    def disconnect(self):
        with self._lock:
            try:
                if self.device:
                    usb.util.release_interface(self.device, self.INTF_TELEMETRY)
                    usb.util.release_interface(self.device, self.INTF_CONTROL)
                self.device = None
            except:
                pass
            self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def set_parameter(self, name: str, value: Any) -> bool:
        """Set a specific wheelbase parameter by name."""
        if name not in self.PARAM_MAP:
            print(f"Unknown parameter: {name}")
            return False

        with self._lock:
            if not self._connected:
                if not self.connect(): return False

            try:
                param_info = self.PARAM_MAP[name]
                offset = param_info["offset"]
                p_type = param_info["type"]

                pkt = bytearray(self.PACKET_LEN)
                pkt[0] = 100
                pkt[1] = 65
                pkt[2] = 224
                pkt[3] = 1 # Command ID for jizuo_param_set

                if p_type == "uint16":
                    pkt[offset] = int(value) & 0xFF
                    pkt[offset+1] = (int(value) >> 8) & 0xFF
                else:
                    pkt[offset] = int(value) & 0xFF

                self.device.write(self.EP_CONTROL_OUT, pkt, timeout=1000)
                self.state[name] = value
                return True
            except Exception as e:
                print(f"Error setting {name}: {e}")
                return False

    def read_wheel_data(self) -> Optional[Dict[str, Any]]:
        """Read telemetry from Interface 0, Endpoint 0x81."""
        if not self._connected:
            return None
        try:
            data = self.device.read(self.EP_TELEMETRY_IN, self.READ_REPORT_LEN, timeout=100)
            if not data or len(data) < 26:
                return None
            
            angle_raw = data[0] + data[1] * 256
            angle_norm = round(angle_raw / 65535.0, 3)
            
            game_force_raw = struct.unpack("i", bytes(data[22:26]))[0]
            game_force = game_force_raw * 20.141601
            
            return {
                "rotation_angle_raw": angle_raw,
                "rotation_angle_norm": angle_norm,
                "game_force": game_force,
                "raw": bytes(data),
            }
        except Exception:
            return None

    def get_state(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self.state)

    def set_state(self, state_dict: Dict[str, Any]) -> bool:
        """Update multiple parameters from a dictionary."""
        success = True
        for name, value in state_dict.items():
            if not self.set_parameter(name, value):
                success = False
        return success
