import hid
import sys

VID = 0x11FF
PID = 0x1212

def enumerate_interfaces():
    try:
        devices = hid.enumerate(VID, PID)
        if not devices:
            print(f"No devices found with VID=0x{VID:04X} PID=0x{PID:04X}")
            return

        print(f"Found {len(devices)} interfaces for device {VID:04X}:{PID:04X}:")
        for i, d in enumerate(devices):
            print(f"\nInterface {i}:")
            for key, value in d.items():
                print(f"  {key}: {value}")

    except Exception as e:
        print(f"Error enumerating: {e}")

if __name__ == "__main__":
    enumerate_interfaces()

