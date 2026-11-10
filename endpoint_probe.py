import ctypes
import time
import os

# Constants
VID = 0x11FF
PID = 0x1212
LIBUSB_PATH = os.path.join(os.getcwd(), "libusb-1.0.dll")

# LibUSB Types
class libusb_device_handle(ctypes.Structure):
    pass

class libusb_context(ctypes.Structure):
    pass

# Load DLL
try:
    lib = ctypes.CDLL(LIBUSB_PATH)
    print(f"Successfully loaded {LIBUSB_PATH}")
except Exception as e:
    print(f"Failed to load DLL: {e}")
    exit(1)

# Define function signatures
lib.libusb_init.argtypes = [ctypes.POINTER(ctypes.POINTER(libusb_context))]
lib.libusb_init.restype = ctypes.c_int

lib.libusb_open_device_with_vid_pid.argtypes = [ctypes.POINTER(libusb_context), ctypes.c_uint16, ctypes.c_uint16]
lib.libusb_open_device_with_vid_pid.restype = ctypes.POINTER(libusb_device_handle)

lib.libusb_claim_interface.argtypes = [ctypes.POINTER(libusb_device_handle), ctypes.c_int]
lib.libusb_claim_interface.restype = ctypes.c_int

lib.libusb_release_interface.argtypes = [ctypes.POINTER(libusb_device_handle), ctypes.c_int]
lib.libusb_release_interface.restype = ctypes.c_int

lib.libusb_bulk_transfer.argtypes = [
    ctypes.POINTER(libusb_device_handle),
    ctypes.c_uint8,
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int),
    ctypes.c_uint32
]
lib.libusb_bulk_transfer.restype = ctypes.c_int

lib.libusb_close.argtypes = [ctypes.POINTER(libusb_device_handle)]
lib.libusb_close.restype = ctypes.c_int

lib.libusb_exit.argtypes = [ctypes.POINTER(libusb_context)]
lib.libusb_exit.restype = ctypes.c_int

def try_write(handle, endpoint, data):
    data_len = len(data)
    buf = (ctypes.c_ubyte * data_len).from_buffer(data)
    transferred = ctypes.c_int()
    res = lib.libusb_bulk_transfer(handle, endpoint, buf, data_len, ctypes.byref(transferred), 1000)
    return res

def main():
    print("PXN V12 Endpoint Probe Tool")
    
    ctx = ctypes.POINTER(libusb_context)()
    if lib.libusb_init(ctypes.byref(ctx)) != 0:
        print("Failed to initialize libusb")
        return

    handle = lib.libusb_open_device_with_vid_pid(ctx, VID, PID)
    if not handle:
        print("Device not found.")
        lib.libusb_exit(ctx)
        return

    # Try claiming different interfaces
    for interface in [0, 1, 2, 3]:
        print(f"\n--- Testing Interface {interface} ---")
        if lib.libusb_claim_interface(handle, interface) != 0:
            print(f"  Could not claim interface {interface}")
            continue
        
        # LED Red packet
        pkt_red = bytearray(64) # Try 64 bytes instead of 58
        pkt_red[0] = 100; pkt_red[1] = 65; pkt_red[2] = 224; pkt_red[3] = 2
        for i in range(0, 30, 3):
            pkt_red[4+i] = 255; pkt_red[5+i] = 0; pkt_red[6+i] = 0
        
        # Try different OUT endpoints
        for ep in [1, 2, 3, 4, 5]:
            res = try_write(handle, ep, pkt_red)
            print(f"  Endpoint {ep}: Result {res}")
            if res == 0:
                print(f"    SUCCESS! Endpoint {ep} accepted the packet.")
        
        lib.libusb_release_interface(handle, interface)

    lib.libusb_close(handle)
    lib.libusb_exit(ctx)

if __name__ == "__main__":
    main()