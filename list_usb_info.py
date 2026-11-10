import usb.core
import usb.util
import sys

VID = 0x11FF
PID = 0x1212

def list_device_info():
    dev = usb.core.find(idVendor=VID, idProduct=PID)
    if dev is None:
        print(f"Device {VID:04X}:{PID:04X} not found")
        return

    print(f"Device: {VID:04X}:{PID:04X}")
    print(f"Manufacturer: {dev.manufacturer}")
    print(f"Product: {dev.product}")

    for cfg in dev:
        print(f"\nConfiguration {cfg.index}:")
        for intf in cfg.interfaces:
            print(f"  Interface {intf.bInterfaceNumber}:")
            for alt in intf.altsettings:
                print(f"    Alternate Setting {alt.bAlternateSetting}:")
                print(f"      Class: {alt.bInterfaceClass}, Subclass: {alt.bInterfaceSubClass}, Protocol: {alt.bInterfaceProtocol}")
                for ep in alt.endpoints:
                    print(f"        Endpoint {ep.bEndpointAddress}:")
                    print(f"          Address: {ep.bEndpointAddress}, Attributes: {ep.bmAttributes}, MaxPacketSize: {ep.wMaxPacketSize}")

if __name__ == "__main__":
    list_device_info()
