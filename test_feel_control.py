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

def send_param(dev, param_index, value, is_uint16=False):
    pkt = create_base_packet()
    pkt[0] = 100
    pkt[1] = 65
    pkt[2] = 224
    pkt[3] = 1 # Command ID for jizuo_param_set
    
    # data[1] is uint16 at pkt[4:6]
    # data[2..11] are bytes at pkt[6:16]
    # data[12] is byte at pkt[18]
    
    if param_index == 1: # Spring (uint16)
        pkt[4] = value & 0xFF
        pkt[5] = (value >> 8) & 0xFF
    elif 2 <= param_index <= 11: # Other bytes
        pkt[param_index + 3] = value & 0xFF # index 2 -> pkt[5]? No.
        # Let's re-read the decompiled code carefully.
        # write_data[4] = data[1] % 256
        # write_data[5] = (data[1] - r) / 256
        # for i in range(2, 12): write_data[i + 4] = data[i]
        # So data[2] -> write_data[6], data[3] -> write_data[7]...
        pkt[param_index + 4] = value & 0xFF
    elif param_index == 12:
        pkt[18] = value & 0xFF
        
    return pkt

def main():
    print(f"PXN FEEL TEST - Interface {TARGET_INTERFACE}, Endpoint {TARGET_ENDPOINT}")
    
    backend = libusb_package.get_libusb1_backend()
    dev = usb.core.find(idVendor=VID, idProduct=PID, backend=backend)
    
    if dev is None:
        print("Device not found.")
        sys.exit(1)

    try:
        dev.set_configuration()
        usb.util.claim_interface(dev, TARGET_INTERFACE)
        
        # --- UNLOCK ---
        print("Unlocking firmware...")
        dev.write(TARGET_ENDPOINT, bytearray([100, 129, 1] + [0]*55), timeout=1000)
        time.sleep(0.05)
        for subcmd in [0, 2, 3, 4, 1]:
            dev.write(TARGET_ENDPOINT, bytearray([100, 129, 224, subcmd] + [0]*54), timeout=1000)
            time.sleep(0.05)
        
        # --- TEST 1: MAX SPRING ---
        print("\nSetting MAX SPRING (Should snap to center)...")
        dev.write(TARGET_ENDPOINT, send_param(dev, 1, 65535), timeout=1000)
        time.sleep(2.0)
        
        # --- TEST 2: MAX FRICTION ---
        print("Setting MAX FRICTION (Should be hard to turn)...")
        dev.write(TARGET_ENDPOINT, send_param(dev, 3, 255), timeout=1000)
        time.sleep(2.0)
        
        # --- TEST 3: MAX DAMPER ---
        print("Setting MAX DAMPER (Should feel sluggish)...")
        dev.write(TARGET_ENDPOINT, send_param(dev, 5, 255), timeout=1000)
        time.sleep(2.0)
        
        # --- RESET ---
        print("\nResetting parameters to 0...")
        dev.write(TARGET_ENDPOINT, send_param(dev, 1, 0), timeout=1000)
        dev.write(TARGET_ENDPOINT, send_param(dev, 3, 0), timeout=1000)
        dev.write(TARGET_ENDPOINT, send_param(dev, 5, 0), timeout=1000)

        print("\nTests complete. Did you feel any change in the shaft's behavior?")

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
