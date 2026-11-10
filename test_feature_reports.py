import time
import hid

VID = 0x11FF
PID = 0x1212

def main():
    print(f"Testing Feature Reports on PXN Wheelbase (VID: {hex(VID)}, PID: {hex(PID)})...")
    devices = hid.enumerate(VID, PID)
    
    target = None
    for d in devices:
        if d['usage_page'] == 65280:
            target = d
            break
    
    if not target:
        print("Vendor-defined interface not found.")
        return

    try:
        dev = hid.device()
        dev.open_path(target['path'])
        print(f"Connected to {target['path']}")

        # LED RED packet: Report ID 100, Subcmd 2, 10 LEDs (255, 0, 0)
        pkt_red = bytearray(58)
        pkt_red[0] = 100
        pkt_red[1] = 65
        pkt_red[2] = 224
        pkt_red[3] = 2
        for i in range(0, 30, 3):
            pkt_red[4+i] = 255
            pkt_red[5+i] = 0
            pkt_red[6+i] = 0

        print("Attempting send_feature_report...")
        try:
            # In hidapi, send_feature_report sends the report ID as the first byte
            dev.send_feature_report(pkt_red)
            print("send_feature_report successful (check LEDs)!")
        except Exception as e:
            print(f"send_feature_report failed: {e}")

        # Try with a leading 0x00 just in case
        print("Attempting send_feature_report with leading 0x00...")
        try:
            pkt_red_prep = bytearray([0]) + pkt_red
            dev.send_feature_report(pkt_red_prep)
            print("Prepended send_feature_report successful (check LEDs)!")
        except Exception as e:
            print(f"Prepended send_feature_report failed: {e}")

        dev.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()