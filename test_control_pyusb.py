import usb.core
import usb.util
import sys
import time

# Device identification
VID = 0x11FF
PID = 0x1212

# Target Interface and Endpoint (based on RE analysis)
# The user identified Interface 3 as the control path.
# In pyusb, interfaces are 0-indexed.
TARGET_INTERFACE = 3 
TARGET_ENDPOINT = 0x03 # Endpoint 3 (Out)

# Speculative packet from pxn_usb_config_table.md
# Example: LED Color Profile [100, 65, 224, 2, <30 bytes LED>, 0...] (58 bytes)
def create_led_packet():
    pkt = bytearray(58)
    pkt[0] = 100
    pkt[1] = 65
    pkt[2] = 224
    pkt[3] = 2
    # Fill with some dummy LED data (RGB triples)
    for i in range(4, 34, 3):
        pkt[i] = 255 # Red
        pkt[i+1] = 0   # Green
        pkt[i+2] = 0   # Blue
    return pkt

def main():
    print(f"PXN Control Test (pyusb)")
    print(f"Searching for device {VID:04X}:{PID:04X}...")
    
    dev = usb.core.find(idVendor=VID, idProduct=PID)
    if dev is None:
        print("Device not found. Make sure it's connected and Zadig driver is installed.")
        sys.exit(1)

    print("Device found!")

    try:
        # Detach kernel driver if necessary (mostly for Linux, but good practice)
        try:
            if dev.is_kernel_driver_active(TARGET_INTERFACE):
                dev.detach_kernel_driver(TARGET_INTERFACE)
                print(f"Detached kernel driver from interface {TARGET_INTERFACE}")
        except NotImplementedError:
            pass

        # Set configuration
        dev.set_configuration()

        # Claim the interface
        usb.util.claim_interface(dev, TARGET_INTERFACE)
        print(f"Claimed interface {TARGET_INTERFACE}")

        # Create a test packet
        packet = create_led_packet()
        print(f"Sending LED packet ({len(packet)} bytes)...")
        
        # Write to the endpoint
        # write(endpoint, data, timeout)
        dev.write(TARGET_ENDPOINT, packet, timeout=1000)
        print("Packet sent successfully!")

    except usb.core.USBError as e:
        print(f"USB Error: {e}")
        if e.errno == 13: # Access denied
            print("Access denied. Try running as Administrator or check Zadig driver.")
        elif e.errno == 19: # Device not found / Interface not found
            print(f"Interface {TARGET_INTERFACE} or Endpoint {TARGET_ENDPOINT} not found.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        usb.util.release_interface(dev, TARGET_INTERFACE)
        print("Interface released.")

if __name__ == "__main__":
    main()
