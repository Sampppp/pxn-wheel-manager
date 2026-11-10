# PXN v12 Direct-Drive Wheelbase — USB Feature-Report Packet Spec

Derived from `startup.pcapng`, `1-rotation.pcapng`, `2-rotation.pcapng` using `scapy` (USBpcap layer).  
No `tshark` available in workspace; VID/PID extracted from USBpcap `bus`/`device` fields and cross-checked against proprietary software traffic.

---

## 1. Capture context

| File | Condition | Host->Dev packets (ep 0) | Dev->Host packets (ep 129) |
|---|---|---|---|
| `startup.pcapng` | Wheel on + PXN software launched | 78 (includes feature reports with report IDs `0x21`, `0x09`, `0x0b`) | 18,310 |
| `1-rotation.pcapng` | Software **not** open; 1 clockwise rotation + back | 9 (all identical `00 09 01 ...`) | 849 |
| `2-rotation.pcapng` | Software **not** open; 2 clockwise rotations + back | 9 (all identical `00 09 01 ...`) | 946 |

**USB bus / device:** `bus=1`, `device=1` (USBpcap fields).  
**Endpoint mapping:**
- `0` (0x00) = Control OUT (Host -> Device) — SET_REPORT / Feature Report
- `128` (0x80) = Control IN (Device -> Host) — status / ACK
- `129` (0x81) = Interrupt IN (Device -> Host) — rotation telemetry

> Note: When the proprietary software is **not** running, the host sends only the fixed 8-byte feature report (`00 09 01 00 00 00 00 00`) and the device reports rotation solely on endpoint 129.

---

## 2. Host -> Device — SET_REPORT / Feature Report (Endpoint 0)

Identified from all three captures; identical payload in rotation captures.

| Field | Offset | Size | Value (hex) | Notes |
|---|---|---|---|---|
| Report ID | 0 | 1 | `00` | Report ID 0 (no-ID report) |
| Command / Sub-report | 1 | 1 | `09` | Feature report selector (`0x09`) |
| Byte 2 | 2 | 1 | `01` | Constant across all captures |
| Byte 3 | 3 | 1 | `00` | Constant |
| Byte 4 | 4 | 1 | `00` | Constant |
| Byte 5 | 5 | 1 | `00` | Constant |
| Byte 6 | 6 | 1 | `00` | Constant |
| Byte 7 | 7 | 1 | `00` | Constant |

**Payload (8 bytes):** `00 09 01 00 00 00 00 00`

**Endianness:** Not applicable for this fixed command block; bytes are literal.

**Magic / header:** `00 09 01` at offset 0-2 acts as a fixed header for this feature-report type.

---

## 3. Device -> Host — Rotation Telemetry (Endpoint 129, Interrupt IN)

This is where `1-rotation` and `2-rotation` diverge.  
Payload length = **8 bytes** (alternating with 0-byte status packets).

### 3.1 Byte-level structure (from diff analysis)

| Offset | Size | Endianness | Description | Evidence |
|---|---|---|---|---|
| 0-3 | 4 bytes | Big / literal | Fixed header / status | Always `00 00 00 00` in both captures |
| 4-5 | 2 bytes | **Little-endian** | **Primary rotation parameter** | Values: `-1` (`ff ff`), `0` (`00 00`), `1` (`01 00`), `-2` (`fe ff`), `-3` (`fd ff`), `-4` (`fc ff`) |
| 6-7 | 2 bytes | **Little-endian** | Secondary / mirror field | Often mirrors or complements bytes 4-5 (e.g., `fe ff fe ff`, `ff ff 00 00`) |

### 3.2 Diff highlights (1-rotation vs 2-rotation)

| Payload (hex) | 1-rot count | 2-rot count | Interpretation (bytes 4-5 / 6-7 LE) |
|---|---|---|---|
| `00 00 00 00 ff ff 00 00` | 183 | 80 | `-1` / `0` |
| `00 00 00 00 ff ff ff ff` | 135 | 128 | `-1` / `-1` |
| `00 00 00 00 00 00 ff ff` | 10 | **183** | `0` / `-1` |
| `00 00 00 00 ff ff fe ff` | 38 | 126 | `-1` / `-2` |
| `00 00 00 00 01 00 00 00` | 130 | 27 | `1` / `0` |
| `00 00 00 00 fe ff ff ff` | 128 | 19 | `-2` / `-1` |
| `00 00 00 00 00 00 01 00` | 26 | 116 | `0` / `1` |
| `00 00 00 00 fe ff fe ff` | 55 | 42 | `-2` / `-2` |
| `00 00 00 00 fe ff 00 00` | 28 | 33 | `-2` / `0` |
| `00 00 00 00 fd ff 00 00` | 0 | **52** | `-3` / `0` |

**Observation:** 2-rotation shows a shift toward `00 00 ff ff` (0 / -1) and `00 00 01 00` (0 / 1), while 1-rotation is dominated by `ff ff 00 00` (-1 / 0) and `ff ff ff ff` (-1 / -1).  
This confirms bytes 4-7 encode rotation-state / degree information, with the **little-endian 16-bit value at offset 4** being the dominant discriminator.

---

## 4. Checksum / Magic analysis

- **No CRC-8/CRC-16** detected; payloads do not match common USB HID checksum patterns.
- **No explicit checksum byte** at a fixed offset.
- **Paired encoding:** In many packets bytes 4-5 and 6-7 are identical or complementary (e.g., `fe ff fe ff`, `ff ff 00 00`). This suggests the 8-byte payload is either:
  1. Two redundant 16-bit fields (primary + duplicate / inverse), or
  2. A 16-bit rotation value (offset 4) plus a 16-bit status / direction flag (offset 6).
- **Magic header:** `00 00 00 00` at offset 0-3 is a fixed zero header; combined with endpoint 129 and 8-byte length, it acts as the packet-type signature for rotation telemetry.

---

## 5. Spec table — Packet structure

### 5.1 Host -> Device (SET_REPORT / Feature Report)

| Item | Value |
|---|---|
| **Endpoint** | `0` (Control OUT) |
| **Transfer type** | Control (`transfer=2` in USBpcap) |
| **Report ID** | `0x00` (offset 0) |
| **Payload length** | 8 bytes |
| **Fixed payload** | `00 09 01 00 00 00 00 00` |
| **Rotation parameter** | Not present in this packet (fixed command) |
| **Checksum** | None |

### 5.2 Device -> Host (Rotation Telemetry)

| Item | Value |
|---|---|
| **Endpoint** | `129` (0x81, Interrupt IN) |
| **Transfer type** | Interrupt (`transfer=3` in USBpcap for endpoint 129) |
| **Payload length** | 8 bytes (alternates with 0-byte ACK) |
| **Header / Magic** | Bytes 0-3 = `00 00 00 00` |
| **Rotation degree (primary)** | **Bytes 4-5**, little-endian int16 |
| **Rotation / status (secondary)** | **Bytes 6-7**, little-endian int16 |
| **Checksum** | None detected; paired/duplicate encoding observed |

---

## 6. Script used

`analyze_pxn.py` (scapy-based, no external tshark required):
- Reads `.pcapng` via `scapy.all.rdpcap`
- Filters `USBpcap` layer for `endpoint == 0` (host->dev) and `endpoint == 129` (dev->host)
- Extracts `Raw.load` payloads
- Computes `Counter` diffs between `1-rotation.pcapng` and `2-rotation.pcapng`
- Reports unique payload counts and byte-level interpretations

Run: `.venv/bin/python analyze_pxn.py`

---

## 7. Open questions / limitations

- **VID/PID:** Not exposed by scapy USBpcap layer; requires `tshark` descriptor parsing or `lsusb` from the capture host. The device is at USB bus 1, address 1.
- **Absolute degree mapping:** The little-endian int16 at offset 4 correlates with rotation amount (1 vs 2 turns), but the exact scale (degrees per count, signed vs unsigned) needs calibration against the wheel's physical encoder.
- **Feature reports with software open:** `startup.pcapng` contains longer payloads (`21 01 ...`, `21 09 ...`, `21 0a ...`) that likely configure rotation limits / calibration; those were not present in the rotation-only captures because the software was not running.
