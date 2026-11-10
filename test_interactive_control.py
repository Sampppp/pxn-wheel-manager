import usb.core
import usb.util
import sys
import time
import libusb_package

VID = 0x11FF
PID = 0x1212
INTF_CONTROL = 2
EP_CONTROL_OUT = 0x03
EP_CONTROL_IN = 0x83

INTF_TELEMETRY = 0
EP_TELEMETRY_IN = 0x81

def main():
    print("PXN Interactive Control Test")
    
    backend = libusb_package.get_libusb1_backend()
    dev = usb.core.find(idVendor=VID, idProduct=PID, backend=backend)
    
    if dev is None:
        print("Device not found. Ensure Interface 0 and 2 are WinUSB.")
        sys.exit(1)

    try:
        # Claim both interfaces
        usb.util.claim_interface(dev, INTF_CONTROL)
        usb.util.claim_interface(dev, INTF_TELEMETRY)
        print("Claimed Interface 0 and 2")

        # --- INTERACTIVE UNLOCK ---
        # We send a packet and wait for ANY response from the device
        unlock_sequence = [
            (bytearray([100, 129, 1] + [0]*55), "Base Info"),
            (bytearray([100, 129, 224, 0] + [0]*54), "Profile 0"),
            (bytearray([100, 129, 224, 2] + [0]*54), "Profile 2"),
            (bytearray([100, 129, 224, 3] + [0]*54), "Profile 3"),
            (bytearray([100, 129, 224, 4] + [0]*54), "Profile 4"),
            (bytearray([100, 129, 224, 1] + [0]*54), "Profile 1"),
        ]

        for pkt, name in unlock_sequence:
            print(f"Sending {name}...", end="", flush=True)
            dev.write(EP_CONTROL_OUT, pkt, timeout=1000)
            
            # Try to read response from either endpoint
            response = None
            try:
                response = dev.read(EP_CONTROL_IN, 64, timeout=200)
            except:
                try:
                    response = dev.read(EP_TELEMETRY_IN, 64, timeout=200)
                except:
                    pass
            
            if response:
                print(f" OK (Recv {len(response)} bytes)")
            else:
                print(" NO RESPONSE")
            time.sleep(0.1)

        # --- TEST PHYSICAL REACTION ---
        print("\nAttempting to set MAX FRICTION (Offset 7)...")
        # [100, 65, 224, 1, 0, 0, 255, ...]
        friction_pkt = bytearray(58)
        friction_pkt[0]=100; friction_pkt[1]=65; friction_pkt[2]=224; friction_pkt[3]=1
        friction_pkt[7] = 255
        
        dev.write(EP_CONTROL_OUT, friction_pkt, timeout=1000)
        print("Packet sent. Check wheel resistance!")

    except usb.core.USBError as e:
        print(f"USB Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        try:
            usb.util.release_interface(dev, INTF_CONTROL)
            usb.util.release_interface(dev, INTF_TELEMETRY)
        except:
            pass

if __name__ == "__main__":
    main()
