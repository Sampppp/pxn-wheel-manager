#!/usr/bin/env .venv/bin/python3
"""Parse PXN v12 USB pcapng files and diff rotation payloads."""
from scapy.all import rdpcap
from scapy.layers.usb import USBpcap
from scapy.packet import Raw
from collections import Counter

def parse_file(path):
    pkts = rdpcap(path)
    host_dev = []  # endpoint 0, dataLength > 0
    dev_host = []  # endpoint 129, dataLength > 0
    for p in pkts:
        if not p.haslayer(USBpcap):
            continue
        u = p[USBpcap]
        raw = p[Raw].load if p.haslayer(Raw) else b''
        if u.endpoint == 0 and u.dataLength > 0:
            host_dev.append(raw)
        elif u.endpoint == 129 and u.dataLength > 0:
            dev_host.append(raw)
    return host_dev, dev_host

def diff_payloads(a, b, label_a="1-rotation", label_b="2-rotation"):
    ca = Counter(a)
    cb = Counter(b)
    print(f"\n=== Payload diff: {label_a} vs {label_b} (device->host endpoint 129) ===")
    all_hex = set(ca) | set(cb)
    for h in sorted(all_hex, key=lambda x: (-ca.get(x,0)-cb.get(x,0), x)):
        print(f"  {label_a}:{ca.get(h,0):4d}  {label_b}:{cb.get(h,0):4d}  {h}")

if __name__ == "__main__":
    for fname in ["1-rotation.pcapng", "2-rotation.pcapng"]:
        hd, dh = parse_file(fname)
        print(f"\n{fname}: host->dev packets={len(hd)} dev->host packets={len(dh)}")
        if hd:
            print(f"  host->dev unique payloads={len(set(hd))} example={hd[0].hex()}")
    hd1, dh1 = parse_file("1-rotation.pcapng")
    hd2, dh2 = parse_file("2-rotation.pcapng")
    diff_payloads(dh1, dh2)
