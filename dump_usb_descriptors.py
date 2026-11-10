import usb.core
import usb.util
import sys
import libusb_package

VID = 0x11FF
PID = 0x1212

def dump_descriptors():
    backend = libusb_package.get_libusb1_backend()
    dev = usb.core.find(idVendor=VID, idProduct=PID, backend=backend)
    
    if dev is None:
        print(f"Device {VID:04X}:{PID:04X} not found.")
        return

    print(f"Device: {dev.manufacturer} {dev.product}")
    
    try:
        cfg = dev.get_active_configuration()
        print(f"\nConfiguration {cfg.index}:")
        
        interfaces = cfg.interfaces
        if callable(interfaces):
            interfaces = interfaces()

        for intf in interfaces:
            print(f"  Interface {intf.bInterfaceNumber}:")
            print(f"    Class: {hex(intf.bInterfaceClass)}, Subclass: {hex(intf.bInterfaceSubClass)}, Protocol: {hex(intf.bInterfaceProtocol)}")
            
            endpoints = intf.endpoints
            if callable(endpoints):
                endpoints = endpoints()
                
            for ep in endpoints:
                addr = ep.bEndpointAddress
                dir_ = "IN" if (addr & 0x80) else "OUT"
                attr = ep.bmAttributes
                type_map = {0: "Control", 1: "Isochronous", 2: "Bulk", 3: "Interrupt"}
                ep_type = type_map.get(attr & 0x03, "Unknown")
                
                print(f"    Endpoint {hex(addr)} ({dir_}):")
                print(f"      Type: {ep_type}, MaxPacketSize: {ep.wMaxPacketSize}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    dump_descriptors()

