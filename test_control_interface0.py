import usb.core
import usb.util
import sys
import time
import libusb_package

# Device identification
VID = 0x11FF
PID = 0x1212

# TARGETING HYPOTHESIS 1: Interface 0, Endpoint 3
TARGET_INTERFACE = 0 
TARGET_ENDPOINT = 0x03 # Endpoint 3 (Out)

def create_led_packet():
    # Based on pxn_usb_config_table.md: [100, 65, 224, 2, <30 bytes LED>, 0...] (58 bytes)
    pkt = bytearray(58)
    pkt[0] = 100
    pkt[1] = 65
    pkt[2] = 224
    pkt[3] = 2
    # Fill with Red LED data (RGB triples)
    for i in range(4, 34, 3):
        pkt[i] = 255 # R
        pkt[i+1] = 0   # G
        pkt[i+2] = 0   # B
    return pkt

def main():
    print(f"PXN Control Test - Hypothesis: Interface {TARGET_INTERFACE}, Endpoint {TARGET_ENDPOINT}")
    
    # Corrected function name for libusb-package
    backend = libusb_package.get_libusb1_backend()
    
    print("Searching for device...")
    dev = usb.core.find(idVendor=VID, idProduct=PID, backend=backend)
    
    if dev is None:
        print("Device not found. Check Zadig driver (Interface 0 should be WinUSB).")
        sys.exit(1)

    print("Device found!")

    try:
        # Set configuration
        dev.set_configuration()

        # Claim the interface
        usb.util.claim_interface(dev, TARGET_INTERFACE)
        print(f"Successfully claimed interface {TARGET_INTERFACE}")

        packet = create_led_packet()
        print(f"Sending LED packet ({len(packet)} bytes) to endpoint {TARGET_ENDPOINT}...")
        
        dev.write(TARGET_ENDPOINT, packet, timeout=1000)
        print("Packet sent successfully! Check your wheel LEDs.")

    except usb.core.USBError as e:
        print(f"USB Error: {e}")
        if e.errno == 13:
            print("Access denied. Ensure Interface 0 is set to WinUSB in Zadig.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        try:
            usb.util.release_interface(dev, TARGET_INTERFACE)
            print("Interface released.")
        except:
            pass

if __name__ == "__main__":
    main()
