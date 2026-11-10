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

def reset():
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
        
        print("Connected. Attempting reset sequence...")

        # 1. Try to send Calibration Stop (might clear error flags)
        print("Sending Calibration Stop...")
        pkt_stop = bytearray(58)
        pkt_stop[0] = 100; pkt_stop[1] = 253; pkt_stop[2] = 2; pkt_stop[3] = 2
        send_packet(dev, pkt_stop)
        time.sleep(0.5)

        # 2. Try to send a Zero Jizuo packet (reset all FFB params)
        print("Sending Zero Jizuo parameters...")
        pkt_zero = bytearray(58)
        pkt_zero[0] = 100; pkt_zero[1] = 65; pkt_zero[2] = 224; pkt_zero[3] = 1
        # All other bytes are 0
        send_packet(dev, pkt_zero)
        time.sleep(0.5)

        # 3. Try to send a generic "Zero" profile packet
        print("Sending Zero Profile packet...")
        pkt_prof = bytearray(58)
        pkt_prof[0] = 100; pkt_prof[1] = 65; pkt_prof[2] = 224; pkt_prof[3] = 0
        send_packet(dev, pkt_prof)
        time.sleep(0.5)

        print("Reset sequence complete. Please check if the wheel is still drifting.")
        dev.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    reset()