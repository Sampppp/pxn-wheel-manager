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

# Use pyusb (same library imported by pxn_usb_decompiled.py)
try:
    import usb.core
    import usb.util
except ImportError as exc:
    print("ERROR: pyusb not installed. Install with: pip install pyusb")
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
def connect_device(max_retries=3, delay=0.5):
    for attempt in range(1, max_retries + 1):
        try:
            dev = usb.core.find(idVendor=VID, idProduct=PID)
            if dev is None:
                raise usb.core.USBError("Device not found (VID=0x%04X PID=0x%04X)" % (VID, PID))
            # Set configuration (required for HID devices)
            dev.set_configuration()
            # Claim interface 0 (standard for this wheelbase)
            usb.util.claim_interface(dev, 0)
            return dev
        except usb.core.USBError as exc:
            msg = str(exc)
            if "busy" in msg.lower() or "resource" in msg.lower() or "timeout" in msg.lower():
                print("Device busy (attempt %d/%d): %s" % (attempt, max_retries, msg))
                if attempt < max_retries:
                    time.sleep(delay * attempt)
                    continue
            print("USB error (attempt %d/%d): %s" % (attempt, max_retries, msg))
            raise
    raise usb.core.USBError("Failed to connect after %d attempts" % max_retries)

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
        print("Device connected; interface claimed.")

        # Try sending via endpoint 1 (upgrade/command endpoint) first,
        # then endpoint 131 (read endpoint) if needed.
        # Note: pyusb write endpoint is the endpoint address (e.g., 0x01 for EP1 OUT).
        # We attempt endpoint 1 (0x01) because profile writes use endpoint 3 (0x03),
        # but angle is unverified; endpoint 1 is the safest speculative target.
        try:
            # Endpoint 1 OUT (address 0x01)
            dev.write(0x01, packet, timeout=1000)
            print("Packet sent to endpoint 0x01 (report 131).")
        except usb.core.USBError as exc:
            print("Endpoint 0x01 failed: %s" % exc)
            # Fallback: try endpoint 3 (profile/config endpoint)
            try:
                dev.write(0x03, packet, timeout=1000)
                print("Packet sent to endpoint 0x03 (profile/config).")
            except usb.core.USBError as exc2:
                print("Endpoint 0x03 also failed: %s" % exc2)
                raise

        # Small delay then attempt a read to verify device is responsive
        time.sleep(0.2)
        try:
            # Read from endpoint 131 (0x83 IN) — 64 bytes, 1000ms timeout
            data = dev.read(0x83, 64, timeout=1000)
            print("Read back %d bytes from endpoint 0x83." % len(data))
            if len(data) >= 3:
                read_angle = data[1] + data[2] * 256
                print("Current reported angle (bytes 1-2): 0x%04X (%d / 65535)" % (read_angle, read_angle))
        except usb.core.USBError as exc:
            print("Read back failed (device may not respond to this packet): %s" % exc)

    except Exception as exc:
        print("ERROR: %s" % exc)
        sys.exit(1)
    finally:
        if dev is not None:
            try:
                usb.util.release_interface(dev, 0)
                usb.util.dispose_resources(dev)
                print("Device released.")
            except Exception as exc:
                print("Cleanup warning: %s" % exc)

if __name__ == "__main__":
    main()
