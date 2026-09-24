#!/usr/bin/env python3
"""Generate the schematic (promini_cc1101.kicad_sch) and symbol library
(promini_cc1101.kicad_sym) that match the board produced by gen_board.py.

Connections are made with global labels placed on the pin ends; unused pins
carry no-connect flags so ERC stays clean.
"""
import os
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = "promini_rfm95w"
ROOT_UUID = "9e4b7d21-6f3a-4c58-b1e2-7a0d5c3f8e91"


def u():
    return str(uuid.uuid4())


def f(v):
    return ("%.4f" % v).rstrip("0").rstrip(".")


# ----------------------------------------------------------------------------
# Symbol definitions: (name, ref prefix, footprint, body half-size, pins)
# pin = (number, name, side, index)   side: L, R, B
# ----------------------------------------------------------------------------
PM_LEFT = ["TXO", "RXI", "RST", "GND", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9"]
PM_RIGHT = ["RAW", "GND", "RST", "VCC", "A3", "A2", "A1", "A0", "D13/SCK", "D12/MISO", "D11/MOSI", "D10/SS"]
PM_FTDI = ["GND", "GND", "VCC", "RXI", "TXO", "DTR"]

pm_pins = []
for i, n in enumerate(PM_LEFT):
    pm_pins.append((str(i + 1), n, "L", i))
for i, n in enumerate(PM_RIGHT):
    pm_pins.append((str(i + 13), n, "R", i))
for i, n in enumerate(PM_FTDI):
    pm_pins.append((str(i + 25), "FTDI_" + n, "B", i))
pm_pins.append(("31", "A4/SDA", "R", 12))
pm_pins.append(("32", "A5/SCL", "R", 13))

RFM_LEFT = ["ANT", "GND", "DIO3", "DIO4", "3V3", "DIO0", "DIO1", "DIO2"]
RFM_RIGHT_BOTTOM_UP = ["GND", "DIO5", "RESET", "NSS", "SCK", "MOSI", "MISO", "GND"]
mod_pins = [(str(i + 1), n, "L", i) for i, n in enumerate(RFM_LEFT)]
mod_pins += [(str(i + 9), n, "R", 7 - i) for i, n in enumerate(RFM_RIGHT_BOTTOM_UP)]

c_pins = [("1", "", "L", 0), ("2", "", "R", 0)]
j_pins = [(str(i + 1), n, "L", i) for i, n in enumerate(["RAW", "VCC", "D3", "SCL", "SDA", "GND"])]
j2_pins = [("1", "BAT+", "L", 0), ("2", "BAT-", "L", 1)]
q_pins = [("1", "G", "L", 0), ("3", "D", "R", 0), ("2", "S", "R", 1)]

SYMBOLS = {
    "Arduino_Pro_Mini": dict(prefix="A", fp="promini_rfm95w:Arduino_Pro_Mini", hw=15.24, hh=25.4, pins=pm_pins,
                             desc="Arduino Pro Mini (3.3 V / 8 MHz recommended)"),
    "RFM95W": dict(prefix="U", fp="promini_rfm95w:HOPERF_RFM9XW_castellated", hw=10.16, hh=11.43, pins=mod_pins,
                   desc="HopeRF RFM95W 868 MHz LoRa module, 16 castellations"),
    "C": dict(prefix="C", fp="promini_rfm95w:C_0805", hw=1.27, hh=2.54, pins=c_pins, desc="Capacitor"),
    "R": dict(prefix="R", fp="promini_rfm95w:R_0805", hw=1.016, hh=2.54, pins=c_pins, desc="Resistor"),
    "Conn_01x06": dict(prefix="J", fp="promini_rfm95w:PinHeader_1x06_P2.54mm", hw=2.54, hh=8.89, pins=j_pins, desc="Sensor header"),
    "Conn_01x02": dict(prefix="J", fp="promini_rfm95w:JST_PH_S2B-PH-SM4-TB_SMD", hw=2.54, hh=3.81, pins=j2_pins, desc="Battery connector"),
    "Q_PMOS": dict(prefix="Q", fp="promini_rfm95w:SOT-23", hw=3.81, hh=3.81, pins=q_pins, desc="P-channel MOSFET, reverse-polarity guard"),
}

PIN_LEN = 2.54
PITCH = 2.54


def pin_geometry(sym, pin):
    """Return (x, y, angle) of the pin's connection point in symbol coords (y up)."""
    num, name, side, idx = pin
    hw, hh = sym["hw"], sym["hh"]
    n_side = len([p for p in sym["pins"] if p[2] == side])
    if side in ("L", "R"):
        y = (n_side - 1) * PITCH / 2 - idx * PITCH
        if n_side == 1:
            y = 0
        x = -(hw + PIN_LEN) if side == "L" else (hw + PIN_LEN)
        if sym["prefix"] == "C":
            x = -3.81 if side == "L" else 3.81
        if sym["prefix"] in ("R", "JP"):
            x = -3.81 if side == "L" else 3.81
        ang = 0 if side == "L" else 180
        return x, y, ang
    if side == "B":
        x = -(n_side - 1) * PITCH / 2 + idx * PITCH
        return x, -(hh + PIN_LEN), 90
    if side == "T":
        return 0, 3.81, 270
    raise ValueError(side)


def symbol_sexpr(name, sym, lib_prefix=True):
    full = f"{PROJECT}:{name}" if lib_prefix else name
    out = [f'  (symbol "{full}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)']
    out.append(f'    (property "Reference" "{sym["prefix"]}" (at 0 {f(sym["hh"] + 2.54)} 0) (effects (font (size 1.27 1.27))))')
    out.append(f'    (property "Value" "{name}" (at 0 {f(-sym["hh"] - 2.54)} 0) (effects (font (size 1.27 1.27))))')
    out.append(f'    (property "Footprint" "{sym["fp"]}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    out.append('    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    out.append(f'    (property "Description" "{sym["desc"]}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    out.append(f'    (symbol "{name}_0_1"')
    if name in ("R", "Jumper"):
        out.append('      (rectangle (start -2.54 -1.016) (end 2.54 1.016) (stroke (width 0.254) (type default)) (fill (type none)))')
    elif name == "C":
        out.append('      (polyline (pts (xy -0.762 -2.032) (xy -0.762 2.032)) (stroke (width 0.508) (type default)) (fill (type none)))')
        out.append('      (polyline (pts (xy 0.762 -2.032) (xy 0.762 2.032)) (stroke (width 0.508) (type default)) (fill (type none)))')
        out.append('      (polyline (pts (xy -2.54 0) (xy -0.762 0)) (stroke (width 0) (type default)) (fill (type none)))')
        out.append('      (polyline (pts (xy 0.762 0) (xy 2.54 0)) (stroke (width 0) (type default)) (fill (type none)))')
    else:
        out.append(f'      (rectangle (start {f(-sym["hw"])} {f(sym["hh"])}) (end {f(sym["hw"])} {f(-sym["hh"])}) (stroke (width 0.254) (type default)) (fill (type background)))')
    out.append('    )')
    out.append(f'    (symbol "{name}_1_1"')
    for pin in sym["pins"]:
        x, y, ang = pin_geometry(sym, pin)
        length = PIN_LEN if name not in ("C", "R", "Jumper") else 3.048
        pname = pin[1] if pin[1] else "~"
        out.append(f'      (pin passive line (at {f(x)} {f(y)} {ang}) (length {f(length)}) '
                   f'(name "{pname}" (effects (font (size 1.27 1.27)))) (number "{pin[0]}" (effects (font (size 1.27 1.27)))))')
    out.append('    )')
    out.append('  )')
    return "\n".join(out)


# ----------------------------------------------------------------------------
# Symbol library file
# ----------------------------------------------------------------------------
lib = ['(kicad_symbol_lib (version 20231120) (generator "gen_sch") (generator_version "8.0")']
for name, sym in SYMBOLS.items():
    lib.append(symbol_sexpr(name, sym, lib_prefix=False))
lib.append(')')
with open(os.path.join(HERE, PROJECT + ".kicad_sym"), "w") as fh:
    fh.write("\n".join(lib) + "\n")

# ----------------------------------------------------------------------------
# Schematic
# ----------------------------------------------------------------------------
# Instances: (ref, symbol name, value, x, y)
INSTANCES = [
    ("A1", "Arduino_Pro_Mini", "Arduino Pro Mini 3V3/8MHz", 66.04, 78.74),
    ("U1", "RFM95W", "RFM95W 868MHz LoRa", 152.4, 66.04),
    ("C1", "C", "22uF", 154.94, 106.68),
    ("R1", "R", "4.7k (DS18B20 only)", 154.94, 124.46),
    ("J1", "Conn_01x06", "Sensor header", 106.68, 78.74),
    ("R2", "R", "330R", 106.68, 111.76),
    ("C2", "C", "100nF (DNP)", 106.68, 134.62),
    ("J2", "Conn_01x02", "JST PH battery", 40.64, 119.38),
    ("Q1", "Q_PMOS", "AO3401A", 63.5, 119.38),
]

# Net assignment by (ref, pin number); everything else gets a no-connect.
NETS = {
    ("A1", "4"): "GND", ("A1", "12"): "RST", ("A1", "5"): "DIO0", ("A1", "6"): "D3", ("A1", "13"): "RAW",
    ("R2", "2"): "D3", ("R2", "1"): "D3_S", ("C2", "1"): "D3_S", ("C2", "2"): "GND",
    ("J2", "1"): "BAT+", ("J2", "2"): "GND", ("Q1", "1"): "GND", ("Q1", "3"): "BAT+", ("Q1", "2"): "VCC",
    ("A1", "14"): "GND", ("A1", "16"): "VCC", ("A1", "31"): "SDA", ("A1", "32"): "SCL",
    ("A1", "21"): "SCK", ("A1", "22"): "MISO", ("A1", "23"): "MOSI", ("A1", "24"): "NSS",
    ("U1", "2"): "GND", ("U1", "5"): "VCC", ("U1", "6"): "DIO0", ("U1", "9"): "GND", ("U1", "11"): "RST",
    ("U1", "12"): "NSS", ("U1", "13"): "SCK", ("U1", "14"): "MOSI", ("U1", "15"): "MISO", ("U1", "16"): "GND",
    ("C1", "1"): "VCC", ("C1", "2"): "GND", ("R1", "1"): "D3_S", ("R1", "2"): "VCC",
    ("J1", "1"): "RAW", ("J1", "2"): "VCC", ("J1", "3"): "D3_S", ("J1", "4"): "SCL", ("J1", "5"): "SDA", ("J1", "6"): "GND",
}

sch = [f'(kicad_sch (version 20231120) (generator "gen_sch") (generator_version "8.0") (uuid "{ROOT_UUID}") (paper "A4")',
       '  (title_block (title "Arduino Pro Mini + RFM95W LoRa 868 MHz carrier") (date "2026-09-24") (rev "1.1"))',
       '  (lib_symbols']
for name, sym in SYMBOLS.items():
    sch.append(symbol_sexpr(name, sym, lib_prefix=True))
sch.append('  )')

for ref, name, value, X, Y in INSTANCES:
    sym = SYMBOLS[name]
    sid = u()
    sch.append(f'  (symbol (lib_id "{PROJECT}:{name}") (at {f(X)} {f(Y)} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{sid}")')
    sch.append(f'    (property "Reference" "{ref}" (at {f(X)} {f(Y - sym["hh"] - 3.0)} 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'    (property "Value" "{value}" (at {f(X)} {f(Y + sym["hh"] + 5.5)} 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'    (property "Footprint" "{sym["fp"]}" (at {f(X)} {f(Y)} 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'    (property "Datasheet" "" (at {f(X)} {f(Y)} 0) (effects (font (size 1.27 1.27)) hide))')
    for pin in sym["pins"]:
        sch.append(f'    (pin "{pin[0]}" (uuid "{u()}"))')
    sch.append(f'    (instances (project "{PROJECT}" (path "/{ROOT_UUID}" (reference "{ref}") (unit 1))))')
    sch.append('  )')
    # labels / no-connects at the pin connection points
    for pin in sym["pins"]:
        px, py, ang = pin_geometry(sym, pin)
        x, y = X + px, Y - py
        netname = NETS.get((ref, pin[0]))
        if netname is None:
            sch.append(f'  (no_connect (at {f(x)} {f(y)}) (uuid "{u()}"))')
            continue
        # label points away from the body
        lab_ang = {0: 180, 180: 0, 90: 270, 270: 90}[ang]
        justify = "right" if lab_ang == 180 else "left"
        sch.append(f'  (global_label "{netname}" (shape bidirectional) (at {f(x)} {f(y)} {lab_ang}) (fields_autoplaced yes) '
                   f'(effects (font (size 1.27 1.27)) (justify {justify})) (uuid "{u()}")')
        sch.append(f'    (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {f(x)} {f(y)} 0) (effects (font (size 1.27 1.27)) hide))')
        sch.append('  )')

notes = [
    "Carrier board: Arduino Pro Mini on top, RFM95W LoRa module on the bottom (muhradio LoRa node).",
    "Use a 3.3 V / 8 MHz Pro Mini: the RFM95W is not 5 V tolerant (1.8-3.7 V).",
    "Power: 1S LiPo / 18650 (or 2xAA) straight on VCC via J2 -> Q1 (reverse-polarity P-FET). Measure sleep current in the battery lead at J2.",
    "No regulator by user choice: a full Li-ion cell is 4.2 V, above the CC1101 3.6 V rating. Use protected cells (nothing here stops deep discharge).",
    "Remove the Pro Mini power LED and regulator; unplug the battery while programming (FTDI adapter set to 3.3 V).",
    "C1 22uF bulk for TX bursts. R1 4.7k = DS18B20 pull-up (DS18B20 nodes only). R2 330R series protection on D3.",
    "C2 100nF = reed/button debounce, leave OFF for DS18B20 (1-Wire timing).",
    "J1 sensor header: RAW VCC D3 SCL SDA GND. Radio: D13 SCK, D12 MISO, D11 MOSI, D10 NSS, D9 RST, D2 DIO0 (muhradio LoRa pinout).",
    "A4/A5 holes match the SparkFun layout; on other clones jumper A4/A5 to J1 SDA/SCL.",
    "FTDI row pads are plated but unconnected.",
]
for i, n in enumerate(notes):
    sch.append(f'  (text "{n}" (exclude_from_sim no) (at 25.4 {f(139.7 + i * 5.08)} 0) (effects (font (size 1.778 1.778)) (justify left bottom)) (uuid "{u()}"))')

sch.append('  (sheet_instances (path "/" (page "1")))')
sch.append(')')
with open(os.path.join(HERE, PROJECT + ".kicad_sch"), "w") as fh:
    fh.write("\n".join(sch) + "\n")
print("wrote", PROJECT + ".kicad_sch and .kicad_sym")
