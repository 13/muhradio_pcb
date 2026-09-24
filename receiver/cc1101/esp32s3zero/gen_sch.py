#!/usr/bin/env python3
"""Schematic + symbol library for the ESP32-S3-Zero + CC1101 receiver carrier.
Matches gen_board.py; connections are global labels on pin ends."""
import os
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = "s3zero_cc1101"
ROOT_UUID = "7a1f0c2e-5d3b-4e8a-9c21-3b6f0e9d4a55"


def u():
    return str(uuid.uuid4())


def f(v):
    return ("%.4f" % v).rstrip("0").rstrip(".")


S3_LEFT = ["5V", "GND", "3V3", "GP1", "GP2", "GP3", "GP4", "GP5", "GP6"]
S3_RIGHT_BOTTOM_UP = ["GP7", "GP8", "GP9", "GP10", "GP11", "GP12", "GP13", "RX44", "TX43"]
s3_pins = [(str(i + 1), n, "L", i) for i, n in enumerate(S3_LEFT)]
s3_pins += [(str(i + 10), n, "R", 8 - i) for i, n in enumerate(S3_RIGHT_BOTTOM_UP)]

MOD_SIG = ["VCC", "GND", "MOSI", "SCLK", "MISO", "GDO2", "GDO0", "CSN"]
mod_pins = [(str(i + 1), n, "L", i) for i, n in enumerate(MOD_SIG)]
mod_pins += [(str(i + 9), n, "R", i + 2) for i, n in enumerate(["GND", "ANT", "GND"])]
c_pins = [("1", "", "L", 0), ("2", "", "R", 0)]

SYMBOLS = {
    "ESP32-S3-Zero": dict(prefix="U", fp="s3zero_cc1101:Waveshare_ESP32-S3-Zero", hw=12.7, hh=13.97, pins=s3_pins,
                          desc="Waveshare ESP32-S3-Zero, 2x9 castellated"),
    "CC1101_11pin": dict(prefix="U", fp="s3zero_cc1101:CC1101_11pin_castellated", hw=10.16, hh=11.43, pins=mod_pins,
                         desc="CC1101 868 MHz module, 11 castellated pins"),
    "C": dict(prefix="C", fp="s3zero_cc1101:C_0805", hw=1.27, hh=2.54, pins=c_pins, desc="Capacitor"),
    "FerriteBead": dict(prefix="FB", fp="s3zero_cc1101:R_0805", hw=2.54, hh=1.016, pins=c_pins, desc="Ferrite bead"),
}
PIN_LEN, PITCH = 2.54, 2.54


def pin_geometry(sym, pin):
    num, name, side, idx = pin
    hw, hh = sym["hw"], sym["hh"]
    n_side = len([p for p in sym["pins"] if p[2] == side])
    y = (n_side - 1) * PITCH / 2 - idx * PITCH if n_side > 1 else 0
    if sym["prefix"] in ("C", "FB"):
        x = -3.81 if side == "L" else 3.81
    else:
        x = -(hw + PIN_LEN) if side == "L" else (hw + PIN_LEN)
    return x, y, (0 if side == "L" else 180)


def symbol_sexpr(name, sym, lib_prefix=True):
    full = f"{PROJECT}:{name}" if lib_prefix else name
    out = [f'  (symbol "{full}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)']
    out.append(f'    (property "Reference" "{sym["prefix"]}" (at 0 {f(sym["hh"] + 2.54)} 0) (effects (font (size 1.27 1.27))))')
    out.append(f'    (property "Value" "{name}" (at 0 {f(-sym["hh"] - 2.54)} 0) (effects (font (size 1.27 1.27))))')
    out.append(f'    (property "Footprint" "{sym["fp"]}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    out.append('    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    out.append(f'    (property "Description" "{sym["desc"]}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    out.append(f'    (symbol "{name}_0_1"')
    if name == "C":
        out.append('      (polyline (pts (xy -0.762 -2.032) (xy -0.762 2.032)) (stroke (width 0.508) (type default)) (fill (type none)))')
        out.append('      (polyline (pts (xy 0.762 -2.032) (xy 0.762 2.032)) (stroke (width 0.508) (type default)) (fill (type none)))')
        out.append('      (polyline (pts (xy -2.54 0) (xy -0.762 0)) (stroke (width 0) (type default)) (fill (type none)))')
        out.append('      (polyline (pts (xy 0.762 0) (xy 2.54 0)) (stroke (width 0) (type default)) (fill (type none)))')
    elif name == "FerriteBead":
        out.append('      (rectangle (start -2.54 -1.016) (end 2.54 1.016) (stroke (width 0.254) (type default)) (fill (type none)))')
    else:
        out.append(f'      (rectangle (start {f(-sym["hw"])} {f(sym["hh"])}) (end {f(sym["hw"])} {f(-sym["hh"])}) (stroke (width 0.254) (type default)) (fill (type background)))')
    out.append('    )')
    out.append(f'    (symbol "{name}_1_1"')
    for pin in sym["pins"]:
        x, y, ang = pin_geometry(sym, pin)
        length = PIN_LEN if sym["prefix"] not in ("C", "FB") else 3.048
        pname = pin[1] if pin[1] else "~"
        out.append(f'      (pin passive line (at {f(x)} {f(y)} {ang}) (length {f(length)}) '
                   f'(name "{pname}" (effects (font (size 1.27 1.27)))) (number "{pin[0]}" (effects (font (size 1.27 1.27)))))')
    out.append('    )')
    out.append('  )')
    return "\n".join(out)


lib = ['(kicad_symbol_lib (version 20231120) (generator "gen_sch") (generator_version "8.0")']
for name, sym in SYMBOLS.items():
    lib.append(symbol_sexpr(name, sym, lib_prefix=False))
lib.append(')')
open(os.path.join(HERE, PROJECT + ".kicad_sym"), "w").write("\n".join(lib) + "\n")

INSTANCES = [
    ("U1", "ESP32-S3-Zero", "ESP32-S3-Zero", 63.5, 76.2),
    ("U2", "CC1101_11pin", "CC1101 868MHz 11-pin", 139.7, 66.04),
    ("FB1", "FerriteBead", "ferrite 600R@100MHz", 139.7, 101.6),
    ("C1", "C", "10uF", 177.8, 101.6),
    ("C2", "C", "100nF", 177.8, 116.84),
]
NETS = {
    ("U1", "2"): "GND", ("U1", "3"): "3V3", ("U1", "5"): "GDO0", ("U1", "7"): "GDO2", ("U1", "9"): "CSN",
    ("U1", "10"): "MISO", ("U1", "11"): "MOSI", ("U1", "12"): "SCK",
    ("U2", "1"): "VCC_RF", ("U2", "2"): "GND", ("U2", "3"): "MOSI", ("U2", "4"): "SCK", ("U2", "5"): "MISO",
    ("U2", "6"): "GDO2", ("U2", "7"): "GDO0", ("U2", "8"): "CSN", ("U2", "9"): "GND", ("U2", "11"): "GND",
    ("FB1", "1"): "3V3", ("FB1", "2"): "VCC_RF",
    ("C1", "1"): "VCC_RF", ("C1", "2"): "GND", ("C2", "1"): "VCC_RF", ("C2", "2"): "GND",
}

sch = [f'(kicad_sch (version 20231120) (generator "gen_sch") (generator_version "8.0") (uuid "{ROOT_UUID}") (paper "A4")',
       '  (title_block (title "muhradio receiver: ESP32-S3-Zero + CC1101 868 MHz") (date "2026-09-15") (rev "1.0"))',
       '  (lib_symbols']
for name, sym in SYMBOLS.items():
    sch.append(symbol_sexpr(name, sym, lib_prefix=True))
sch.append('  )')
for ref, name, value, X, Y in INSTANCES:
    sym = SYMBOLS[name]
    sch.append(f'  (symbol (lib_id "{PROJECT}:{name}") (at {f(X)} {f(Y)} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{u()}")')
    sch.append(f'    (property "Reference" "{ref}" (at {f(X)} {f(Y - sym["hh"] - 3.0)} 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'    (property "Value" "{value}" (at {f(X)} {f(Y + sym["hh"] + 5.5)} 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'    (property "Footprint" "{sym["fp"]}" (at {f(X)} {f(Y)} 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'    (property "Datasheet" "" (at {f(X)} {f(Y)} 0) (effects (font (size 1.27 1.27)) hide))')
    for pin in sym["pins"]:
        sch.append(f'    (pin "{pin[0]}" (uuid "{u()}"))')
    sch.append(f'    (instances (project "{PROJECT}" (path "/{ROOT_UUID}" (reference "{ref}") (unit 1))))')
    sch.append('  )')
    for pin in sym["pins"]:
        px, py, ang = pin_geometry(sym, pin)
        x, y = X + px, Y - py
        netname = NETS.get((ref, pin[0]))
        if netname is None:
            sch.append(f'  (no_connect (at {f(x)} {f(y)}) (uuid "{u()}"))')
            continue
        lab_ang = 180 if ang == 0 else 0
        justify = "right" if lab_ang == 180 else "left"
        sch.append(f'  (global_label "{netname}" (shape bidirectional) (at {f(x)} {f(y)} {lab_ang}) (fields_autoplaced yes) '
                   f'(effects (font (size 1.27 1.27)) (justify {justify})) (uuid "{u()}")')
        sch.append(f'    (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {f(x)} {f(y)} 0) (effects (font (size 1.27 1.27)) hide))')
        sch.append('  )')

notes = [
    "muhradio receiver (env esp32-s3-zero-cc1101 / -bresser): SCK=GP9 MISO=GP7 MOSI=GP8 SS=GP6 GDO0=GP2.",
    "GDO2 is wired to GP4 as a spare (firmware does not use it yet).",
    "Radio 3.3 V comes from the S3-Zero's 3V3 pin through FB1 + C1/C2 to keep WiFi TX noise off the receiver.",
    "Board is powered by the S3-Zero's USB-C. ANT pad is a plated hole for an 86 mm wire (quarter wave at 868 MHz).",
    "Both modules on the top side; the CC1101 sits about 40 mm from the S3-Zero's 2.4 GHz antenna.",
]
for i, n in enumerate(notes):
    sch.append(f'  (text "{n}" (exclude_from_sim no) (at 25.4 {f(139.7 + i * 5.08)} 0) (effects (font (size 1.778 1.778)) (justify left bottom)) (uuid "{u()}"))')
sch.append('  (sheet_instances (path "/" (page "1")))')
sch.append(')')
open(os.path.join(HERE, PROJECT + ".kicad_sch"), "w").write("\n".join(sch) + "\n")
print("wrote", PROJECT + ".kicad_sch and .kicad_sym")
