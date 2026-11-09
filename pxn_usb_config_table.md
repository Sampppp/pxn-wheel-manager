# PXN USB Config Packet Mapping (from pxn_usb_decompiled.py + config_decompiled.py)

Source files:
- `pxn_usb_decompiled.py` (decompiled `utils/pxn_usb.pyc`)
- `config_decompiled.py` (decompiled `utils/config.pyc`)

## Key constants (config_decompiled.py)
- `PXN_VID = 4607` (0x120F)
- `PXN_V12_PID = 4626` (0x120A)
- Endpoint used for profile/config writes: `usb_write(0, 3, ...)` (device interface 0, endpoint 3)
- HID read endpoint for live data: `handle.read(131, 64, 1000)` (report 131, 64 bytes)

---

## Configuration / Profile Writes (Endpoint 3, report 3)

| Setting Name | Function (line) | Byte Array Structure (first bytes shown) | Endpoint / Report | Value Packing / Notes |
|---|---|---|---|---|
| LED Color Profile | `pxn_led_set` (~1159) | `[100, 65, 224, 2, <30 bytes LED hex>, 0...]` (58 bytes total) | `usb_write(0, 3, ...)` | Byte 3 = `2`; bytes 4-33 = 10 RGB triples (hex parsed from `color_data`); rest zero-padded |
| Map / Button Profile | `pxn_map_set` (~1185) | `[100, 65, 224, 0, <44 bytes map hex>, 0...]` (58 bytes) | `usb_write(0, 3, ...)` | Byte 3 = `0`; bytes 4-47 = `p12_lite_map_hex` (map values); rest zero |
| Wheel + LED Combined | `pxn_wheel_set` (~1206) | First packet: `[100, 65, 224, 2, <30 bytes LED>, ...]`; Second packet: `[100, 65, 224, 0, <44 bytes map>, ...]` | `usb_write(0, 3, ...)` (twice) | Byte 3 = `2` for LED, then `0` for map; same hex packing as above |
| Two-Pick Status | `pxn_wheel_two_pick_set` (~1268) | `[100, 65, 7, <status>, 0...]` (58 bytes) | `usb_write(0, 3, ...)` | Byte 3 = `status` (integer 0/1 directly) |
| Wind Speed Switch | `pxn_wind_speed_switch_set` (~1282) | `[100, 65, 8, <status>, 0...]` (58 bytes) | `usb_write(0, 3, ...)` | Byte 3 = `status` (integer 0/1 directly) |
| Calibration Start | `pxn_wheel_jiaozhun_start` (~1298) | `[100, 253, 1, 0, 0...]` (58 bytes) | `usb_write(0, 3, ...)` | Byte 3 = `1` (start command) |
| Calibration Stop | `pxn_wheel_jiaozhun_stop` (~1314) | `[100, 253, 2, 0, 0...]` (58 bytes) | `usb_write(0, 3, ...)` | Byte 3 = `2` (stop command) |
| Base Info Template | `pxn_p12_lite_init` (~161) | `config.pxn_cmd_tpl_base_info` (template from config) | `usb_write(0, 3, ...)` | Template bytes; exact content defined in `config_decompiled.py` |
| Profile Info Template | `pxn_p12_lite_init` (~164-175) | `config.pxn_cmd_tpl_profile_info` (template) | `usb_write(0, 3, ...)` | Template bytes; sent 5 times during init |
| Shift Lever Map | `pxn_shift_lever_map_set` (~1349) | `[100, 65, 224, 0, <map hex>, ...]` | `usb_write(0, 3, ...)` | Byte 3 = `0`; bytes 4-47 = map hex |
| Footrest Map | `pxn_footrest_map_set` (~1375) | `[100, 65, 224, 0, <map hex>, ...]` | `usb_write(0, 3, ...)` | Byte 3 = `0`; bytes 4-47 = map hex |
| Footrest Coordinate | `pxn_footrest_coordinate_set` (~1425) | `[100, 65, 224, 0, <coord hex>, ...]` | `usb_write(0, 3, ...)` | Byte 3 = `0`; coordinate hex packed in bytes 4+ |
| Jizuo (Base) Param | `pxn_jizuo_param_set` (~167) | `[100, 65, 224, 0, <param hex>, ...]` | `usb_write(0, 3, ...)` | Byte 3 = `0`; parameter hex in payload |

---

## Live Data / Feedback Reads (Endpoint 131, HID report 131, 64 bytes)

These are **read** from the wheelbase, not written by `pxn_usb`. They provide the rotation angle and force feedback values used by the app.

| Setting / Data Point | Function (line) | Byte Range | Endpoint / Report | Packing / Scaling |
|---|---|---|---|---|
| Wheel Rotation Angle | `pxn_p12_lite_read_deal` (~194) | Bytes 1-2 (0-indexed: `data_read[1:3]`) | `handle.read(131, 64, 1000)` | Little-endian uint16: `value = data[1] + data[2]*256`; normalized by `/ 65535` (line 195) |
| Motor / Force Feedback (IA) | `pxn_p12_lite_read_deal` (~500) | Bytes 7-10 (`data_read[7:11]`) | `handle.read(131, 64, 1000)` | Little-endian int32 (`struct.unpack("i", ...)`); scaled by `* 20.141601` |
| Motor / Force Feedback (IB) | `pxn_p12_lite_read_deal` (~504) | Bytes 11-14 (`data_read[11:15]`) | Same | Same int32 little-endian, `* 20.141601` |
| Motor / Force Feedback (IC) | `pxn_p12_lite_read_deal` (~508) | Bytes 15-18 (`data_read[15:19]`) | Same | Same int32 little-endian, `* 20.141601` |
| IQ Voltage | `pxn_p12_lite_read_deal` (~512) | Bytes 19-20 (`data_read[19:21]`) | Same | Little-endian int16 (`struct.unpack("h", ...)`) |
| Speed | `pxn_p12_lite_read_deal` (~516) | Bytes 21-22 (`data_read[21:23]`) | Same | Little-endian int16 (`struct.unpack("h", ...)`) |
| Game Force (FFB) | `pxn_p12_lite_read_deal` (~520) | Bytes 23-26 (`data_read[23:27]`) | Same | Little-endian int32 (`struct.unpack("i", ...)`); scaled by `* 20.141601` |

---

## Firmware / Upgrade Packets (Endpoint 1, report IDs 1 / 100 / 129 / 131 / 160 / 161 / 163 / 169 / 253 / 254)

Not user-config settings, but shown for completeness (they use endpoint 1 with report IDs embedded in byte 1 or byte 2):

| Command | Function | Byte Array (first bytes) | Endpoint / Report | Notes |
|---|---|---|---|---|
| Upgrade Erase | `p12_lite_upgrade_eraze` (~604) | `[1, 129, 0, ...]` | `usb_write(1, 1, ...)` | Byte 1 = 129 (report 129?) |
| Upgrade Erase BLE | `p12_lite_upgrade_eraze_ble` (~621) | `[100, 161, 0, ...]` | `usb_write(0, 1, ...)` | Byte 1 = 161 |
| Upgrade Finish | `p12_lite_upgrade_finish` (~641) | `[1, 131, 0, ...]` | `usb_write(1, 1, ...)` | Byte 1 = 131 |
| Upgrade Finish BLE | `p12_lite_upgrade_finish_ble` (~664) | `[100, 163, 0, ...]` | `usb_write(0, 1, ...)` | Byte 1 = 163 |
| Update Mode | `p12_lite_jizuo_update_mode` (~691) | `[100, 254, 1, 0, ...]` | `usb_write(0, 1, ...)` | Byte 1 = 254, byte 2 = 1 |
| Update Mode BLE | `p12_lite_jizuo_update_mode_ble` (~723) | `[100, 169, 1, 0, ...]` | `usb_write(0, 1, ...)` | Byte 1 = 169 |
| Firmware Data (56 bytes) | `jizuo_upgrade_start` (~775) | `[100, 160, 56, <pkg_low>, <pkg_high>, <data...>]` | `usb_write_retry(0, 1, ...)` | Byte 2 = 56 (length); bytes 3-4 = package number (little-endian uint16) |

---

## Notes on Damper / Friction / FFB Gain
- **No direct write packets for damper or friction** exist inside `pxn_usb_decompiled.py`. Those parameters are likely handled by the game-specific tool modules (`game_dirt_tool`, `game_acc_tool`, `game_wrcg_tool`, etc.) which call `pxn_usb` functions or send data through the same endpoint 3 / endpoint 1 paths.
- **FFB Gain / Force** is delivered to the app via the HID read at endpoint 131 (bytes 23-26, int32 scaled by 20.141601), not by a separate config write.
- **Rotation Angle** is also read from endpoint 131 (bytes 1-2, uint16 / 65535), not written by this module.
