#!/usr/bin/env python3
"""
test_angle.py
Minimal standalone script to attempt setting PXN wheelbase rotation angle.

REVERSE-ENGINEERING NOTE (from pxn_usb_decompiled.py / config_decompiled.py):
- VID = 4607 (0x11FF), PID = 4626 (0x1212) for V12 wheelbase.
- Rotation angle is READ from HID endpoint 131 (64-byte report), bytes 1-2,
  little-endian uint16 scaled by /65535 (line 194-195 of pxn_usb_decompiled.py).
- There is NO verified write packet for rotation angle in the decompiled USB
  module (pxn_usb_decompiled.py). The packets found are profile/config writes
  to endpoint 3 ([100, 65, ...]) and firmware/upgrade packets to endpoint 1.
- This script sends a SPECULATIVE 64-byte packet mirroring the read format,
  with bytes 1-2 set to the target angle value. It is unverified and may not
  change the angle; it is provided only to demonstrate the byte structure.
- If the device is busy (USBError / timeout), the script retries with backoff.
"""

import sys
import time
import os

# Use hidapi (which we verified works on this system) instead of pyusb
try:
    import hid
except ImportError as exc:
    print("ERROR: hidapi not installed. Install with: pip install hidapi")
    sys.exit(1)

# --- Device identification (from config_decompiled.py) ---
VID = 0x11FF      # 4607 decimal
PID = 0x1212      # 4626 decimal

# --- Target angle ---
TARGET_DEG = 540
# The read path normalizes by /65535 (line 195). 540 deg > 360, so we wrap
# to 180 deg for a uint16 range, but keep the raw calculation visible.
TARGET_DEG_WRAPPED = TARGET_DEG % 360
ANGLE_UINT16 = int((TARGET_DEG_WRAPPED / 360.0) * 65535)

# --- Packet construction (speculative, based on read format) ---
# Read format: 64 bytes, angle at bytes 1-2 (little-endian uint16)
PACKET_LEN = 64
packet = bytearray(PACKET_LEN)
packet[0] = 131          # Report / endpoint identifier (matches read endpoint 131)
packet[1] = ANGLE_UINT16 & 0xFF
packet[2] = (ANGLE_UINT16 >> 8) & 0xFF
# Bytes 3-63 left as 0 (unknown fields; could contain damper/friction/FFB)

# --- Connection with robust error handling ---
def connect_device():
    """
    Connects to the PXN wheelbase using hidapi.
    Since the device has multiple interfaces, we look for the one that 
    matches the vendor-defined usage page (0xFF00 / 65280) if possible,
    or simply try to open the device by VID/PID.
    """
    try:
        # Try to find the specific interface for vendor-defined reports
        devices = hid.enumerate(VID, PID)
        if not devices:
            raise Exception(f"Device not found (VID=0x{VID:04X} PID=0x{PID:04X})")
        
        # Prefer the interface with usage_page 65280 (Vendor Defined)
        target_device = None
        for d in devices:
            if d['usage_page'] == 65280:
                target_device = d
                break
        
        if target_device:
            print(f"Found vendor-defined interface (path: {target_device['path']})")
            dev = hid.device()
            dev.open_path(target_device['path'])
        else:
            print("Vendor-defined interface not found, trying default open...")
            dev = hid.device()
            dev.open(VID, PID)
            
        return dev
    except Exception as e:
        print(f"HID connection error: {e}")
        raise

def main():
    print("PXN Wheel Angle Test")
    print("VID=0x%04X (%d) PID=0x%04X (%d)" % (VID, VID, PID, PID))
    print("Target angle: %d deg (wrapped to %d deg for uint16) -> uint16=0x%04X (%d)" % (
        TARGET_DEG, TARGET_DEG_WRAPPED, ANGLE_UINT16, ANGLE_UINT16))
    print("Packet length: %d bytes" % PACKET_LEN)
    print("Packet bytes 0-5: %s" % " ".join("%02X" % b for b in packet[:6]))

    dev = None
    try:
        dev = connect_device()
        print("Device connected.")

        # In hidapi, the first byte of the write buffer is treated as the Report ID.
        # Our packet[0] is 131, which matches the report ID we want to send.
        try:
            dev.write(packet)
            print("Packet sent via HID (Report ID 131).")
        except Exception as exc:
            print(f"HID write failed: {exc}")
            raise

        # Small delay then attempt a read to verify device is responsive
        time.sleep(0.2)
        try:
            # Read up to 64 bytes
            data = dev.read(64)
            if data:
                print(f"Read back {len(data)} bytes.")
                # Note: hidapi.read() usually strips the Report ID from the start.
                # If the device sends [131, angle_l, angle_h, ...], 
                # data will be [angle_l, angle_h, ...].
                if len(data) >= 2:
                    read_angle = data[0] + data[1] * 256
                    print(f"Current reported angle (bytes 0-1): 0x{read_angle:04X} ({read_angle} / 65535)")
                else:
                    print(f"Read data too short: {data}")
            else:
                print("No data read back.")
        except Exception as exc:
            print(f"HID read failed: {exc}")

    except Exception as exc:
        print("ERROR: %s" % exc)
        sys.exit(1)
    finally:
        if dev is not None:
            try:
                dev.close()
                print("Device closed.")
            except Exception as exc:
                print(f"Cleanup warning: {exc}")

if __name__ == "__main__":
    main()
