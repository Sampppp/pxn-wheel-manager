import usb.core
import usb.util
import sys
import time
import libusb_package

VID = 0x11FF
PID = 0x1212
TARGET_INTERFACE = 2 
TARGET_ENDPOINT = 0x03 

def create_base_packet():
    return bytearray(58)

def send_raw_param(dev, offset, value, is_uint16=False):
    pkt = create_base_packet()
    pkt[0] = 100
    pkt[1] = 65
    pkt[2] = 224
    pkt[3] = 1 # Command ID for jizuo_param_set
    
    if is_uint16:
        pkt[offset] = value & 0xFF
        pkt[offset+1] = (value >> 8) & 0xFF
    else:
        pkt[offset] = value & 0xFF
        
    return pkt

def main():
    if len(sys.argv) < 3:
        print("Usage: python pxn_param_scanner.py <offset> <value> [is_uint16]")
        print("Example (Byte): python pxn_param_scanner.py 7 255")
        print("Example (uint16): python pxn_param_scanner.py 4 65535 1")
        sys.exit(1)

    try:
        offset = int(sys.argv[1])
        value = int(sys.argv[2])
        is_uint16 = int(sys.argv[3]) == 1 if len(sys.argv) > 3 else False
    except ValueError:
        print("Error: Offset and Value must be integers.")
        sys.exit(1)

    print(f"Targeting Offset {offset} with Value {value} (uint16={is_uint16})")
    
    backend = libusb_package.get_libusb1_backend()
    dev = usb.core.find(idVendor=VID, idProduct=PID, backend=backend)
    
    if dev is None:
        print("Device not found. Ensure Interface 2 is WinUSB.")
        sys.exit(1)

    try:
        # Removed set_configuration() to avoid device resets
        usb.util.claim_interface(dev, TARGET_INTERFACE)
        
        # --- CONNECTION CHECK ---
        print("Checking connection (reading angle)...", end="", flush=True)
        try:
            # Read from the telemetry endpoint (Interface 0, Endpoint 0x81 / Report 131)
            # We try to read from the device to see if it is alive.
            dev.read(0x81, 64, timeout=500) 
            print(" ALIVE")
        except:
            print(" UNKNOWN (Read failed, but we will try writing anyway)")

        # --- UNLOCK FIRMWARE ---
        print("Unlocking firmware...", end="", flush=True)
        dev.write(TARGET_ENDPOINT, bytearray([100, 129, 1] + [0]*55), timeout=1000)
        time.sleep(0.1) # Increased delay
        for subcmd in [0, 2, 3, 4, 1]:
            dev.write(TARGET_ENDPOINT, bytearray([100, 129, 224, subcmd] + [0]*54), timeout=1000)
            time.sleep(0.1) # Increased delay
        print(" DONE")

        # --- SEND PARAMETER ---
        pkt = send_raw_param(dev, offset, value, is_uint16)
        print(f"Sending packet...", end="", flush=True)
        dev.write(TARGET_ENDPOINT, pkt, timeout=1000)
        print(" SENT")
        
        print("\nPacket delivered. Test the wheel feel now.")

    except usb.core.USBError as e:
        print(f"USB Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        try:
            usb.util.release_interface(dev, TARGET_INTERFACE)
        except:
            pass

if __name__ == "__main__":
    main()
