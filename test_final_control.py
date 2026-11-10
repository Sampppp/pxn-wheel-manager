import usb.core
import usb.util
import sys
import time
import libusb_package

VID = 0x11FF
PID = 0x1212
TARGET_INTERFACE = 2 
TARGET_ENDPOINT = 0x03 

def create_packet(header, length=58):
    pkt = bytearray(length)
    for i, val in enumerate(header):
        pkt[i] = val
    return pkt

def create_led_packet(color='red'):
    payload = bytearray(30)
    if color == 'red':
        for i in range(0, 30, 3):
            payload[i] = 255; payload[i+1] = 0; payload[i+2] = 0
    elif color == 'off':
        for i in range(0, 30, 3):
            payload[i] = 0; payload[i+1] = 0; payload[i+2] = 0
    return create_packet([100, 65, 224, 2] + list(payload))

def main():
    print(f"PXN FINAL CONTROL TEST - Interface {TARGET_INTERFACE}, Endpoint {TARGET_ENDPOINT}")
    
    backend = libusb_package.get_libusb1_backend()
    dev = usb.core.find(idVendor=VID, idProduct=PID, backend=backend)
    
    if dev is None:
        print("Device not found. Ensure Interface 2 is WinUSB.")
        sys.exit(1)

    try:
        dev.set_configuration()
        usb.util.claim_interface(dev, TARGET_INTERFACE)
        print(f"Successfully claimed Interface {TARGET_INTERFACE}")

        # --- STEP 1: UNLOCK FIRMWARE ---
        print("Sending Initialization Sequence to unlock firmware...")
        # Base Info
        dev.write(TARGET_ENDPOINT, create_packet([100, 129, 1]), timeout=1000)
        time.sleep(0.05)
        # Profile Sequence [0, 2, 3, 4, 1]
        for subcmd in [0, 2, 3, 4, 1]:
            dev.write(TARGET_ENDPOINT, create_packet([100, 129, 224, subcmd]), timeout=1000)
            time.sleep(0.05)
        print("Initialization complete.")

        # --- STEP 2: PHYSICAL TEST (Calibration) ---
        print("\nAttempting Calibration Start (Physical Movement)...")
        # [100, 253, 1, 0, 0...]
        dev.write(TARGET_ENDPOINT, create_packet([100, 253, 1, 0, 0]), timeout=1000)
        time.sleep(1.0)

        # --- STEP 3: VISUAL TEST (LEDs) ---
        print("Attempting LED Red...")
        dev.write(TARGET_ENDPOINT, create_led_packet('red'), timeout=1000)
        time.sleep(1.0)
        
        print("Attempting LED Off...")
        dev.write(TARGET_ENDPOINT, create_led_packet('off'), timeout=1000)

        print("\nTests complete. Did the wheelbase move or change LED colors?")

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
