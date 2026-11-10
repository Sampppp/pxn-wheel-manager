import time
import hid

VID = 0x11FF
PID = 0x1212

def send_packet(dev, pkt):
    try:
        dev.write(pkt)
        return True
    except Exception as e:
        print(f"Write failed: {e}")
        return False

def full_init():
    try:
        devices = hid.enumerate(VID, PID)
        if not devices:
            print("Device not found.")
            return
        
        target = None
        for d in devices:
            if d['usage_page'] == 65280:
                target = d
                break
        
        dev = hid.device()
        if target:
            dev.open_path(target['path'])
        else:
            dev.open(VID, PID)
        
        print("Connected. Executing full initialization sequence...")

        # Base Info Template (from config_decompiled.py)
        # [100, 129, 1, 0, 0, 0, 0, 0, ...]
        base_info = bytearray([100, 129, 1] + [0]*55)
        print("Sending base info template...")
        send_packet(dev, base_info)
        time.sleep(0.01)

        # Profile Info Template (from config_decompiled.py)
        # [100, 129, 224, 0, 0, 0, 0, 0, ...]
        profile_info = bytearray([100, 129, 224] + [0]*55)
        
        # Sequence from pxn_p12_lite_init():
        # pkt[3] = 0, then 2, then 3, then 4, then 1
        for subcmd in [0, 2, 3, 4, 1]:
            print(f"Sending profile info subcmd {subcmd}...")
            pkt = bytearray(profile_info)
            pkt[3] = subcmd
            send_packet(dev, pkt)
            time.sleep(0.01)

        print("Initialization sequence complete. Please check if the wheel is still drifting.")
        dev.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    full_init()