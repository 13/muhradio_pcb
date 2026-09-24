#!/usr/bin/env python3
"""Generate the Pro Mini + CC1101 (11-pin) carrier PCB with KiCad's pcbnew API.

Run:  python3 gen_board.py            (writes promini_cc1101.kicad_pcb)

Coordinate system: millimetres, origin at the board's top-left corner,
y grows downward (KiCad convention).  The Pro Mini sits on the top side
with its FTDI end at y=0; the CC1101 module sits on the bottom side at
the far end.  See docs/DESIGN.md for the reasoning.
"""
import os
import sys

import pcbnew
from pcbnew import VECTOR2I, FromMM

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "promini_cc1101.kicad_pcb")

# ----------------------------------------------------------------------------
# Geometry (mm)
# ----------------------------------------------------------------------------
BOARD_W = 17.78
BOARD_H = 60.0

PM_W, PM_H = 17.78, 33.02          # Pro Mini outline
PM_PITCH = 2.54
PM_LEFT_X, PM_RIGHT_X = 1.27, 16.51
PM_DRILL, PM_PAD = 1.0, 1.7

# Pro Mini pads: (number, name, x, y) with y measured from the FTDI end.
# Derived from SparkFun's Arduino-Pro-Mini.brd (y_kicad = 33.02 - y_eagle).
PM_LEFT = ["TXO", "RXI", "RST", "GND", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9"]
PM_RIGHT = ["RAW", "GND", "RST", "VCC", "A3", "A2", "A1", "A0", "D13", "D12", "D11", "D10"]
PM_FTDI = [("GND", 2.54), ("GND", 5.08), ("VCC", 7.62), ("RXI", 10.16), ("TXO", 12.70), ("DTR", 15.24)]

A4_POS, A5_POS = (13.589, 15.113), (13.589, 12.573)   # SparkFun inner A4/A5 pins
PM_PADS = []
for i, n in enumerate(PM_LEFT):
    PM_PADS.append((str(i + 1), n, PM_LEFT_X, 3.81 + i * PM_PITCH))
for i, n in enumerate(PM_RIGHT):
    PM_PADS.append((str(i + 13), n, PM_RIGHT_X, 3.81 + i * PM_PITCH))
for i, (n, x) in enumerate(PM_FTDI):
    PM_PADS.append((str(i + 25), n, x, 1.27))
PM_PADS.append(("31", "A4", *A4_POS))
PM_PADS.append(("32", "A5", *A5_POS))

# CC1101 11-pin module (top view of the module, origin = module centre).
MOD_W, MOD_H = 19.3, 17.0          # W across the pin edges, H along them
MOD_EDGE = MOD_W / 2               # 9.65
MOD_SIG_PITCH = 2.0
MOD_ANT_PITCH = 2.54
MOD_ANT_OFFSET = 1.0               # ANT pin sits ~1 mm toward the CSN end
CAST_OUT, CAST_IN = 1.2, 0.8       # castellation pad: outside / under module
MOD_SIG = ["VCC", "GND", "MOSI", "SCLK", "MISO", "GDO2", "GDO0", "CSN"]

MOD_PADS = []                      # (number, name, x, y, w, h)
for i, n in enumerate(MOD_SIG):
    y = -7.0 + i * MOD_SIG_PITCH
    MOD_PADS.append((str(i + 1), n, -(MOD_EDGE + (CAST_OUT - CAST_IN) / 2), y, CAST_OUT + CAST_IN, 1.2))
for i, n in enumerate(["GND", "ANT", "GND"]):
    y = MOD_ANT_OFFSET + (i - 1) * MOD_ANT_PITCH
    MOD_PADS.append((str(i + 9), n, MOD_EDGE + (CAST_OUT - CAST_IN) / 2, y, CAST_OUT + CAST_IN, 1.8 if n == "ANT" else 1.6))

# Placement
PM_POS = (0.0, 0.0)                              # Pro Mini top-left corner
MOD_TOP_EDGE = 39.0                              # module signal edge (y)
HDR_Y = 34.9                                     # sensor header row (y)
HDR_X0 = 2.54
HDR_PINS = ["RAW", "VCC", "D3", "SCL", "SDA", "GND"]
MOD_CENTER = (BOARD_W / 2, MOD_TOP_EDGE + MOD_EDGE)

# Rules
CLEARANCE = 0.2
TRACK_SIG = 0.3
TRACK_PWR = 0.4
VIA_D, VIA_DRILL = 0.6, 0.3
EDGE_CLR = 0.3


def mm(x, y):
    return VECTOR2I(FromMM(x), FromMM(y))


# ----------------------------------------------------------------------------
# Board + design rules
# ----------------------------------------------------------------------------
board = pcbnew.BOARD()
ds = board.GetDesignSettings()
ds.m_MinClearance = FromMM(CLEARANCE)
ds.m_TrackMinWidth = FromMM(0.2)
ds.m_ViasMinSize = FromMM(VIA_D)
ds.m_MinThroughDrill = FromMM(VIA_DRILL)
ds.m_CopperEdgeClearance = FromMM(EDGE_CLR)
ds.m_HoleClearance = FromMM(0.25)
ds.m_SolderMaskToCopperClearance = FromMM(0.0)
ds.m_SilkClearance = FromMM(0.0)
ds.m_MinSilkTextHeight = FromMM(0.8)
ds.m_MinSilkTextThickness = FromMM(0.1)
try:
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetClearance(FromMM(CLEARANCE))
    nc.SetTrackWidth(FromMM(TRACK_SIG))
    nc.SetViaDiameter(FromMM(VIA_D))
    nc.SetViaDrill(FromMM(VIA_DRILL))
except Exception as e:  # API differences between versions
    print("netclass setup skipped:", e)

nets = {}


def net(name):
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        nets[name] = n
    return nets[name]


# ----------------------------------------------------------------------------
# Footprint helpers
# ----------------------------------------------------------------------------
def fp_line(fp, x1, y1, x2, y2, layer, w=0.12):
    s = pcbnew.PCB_SHAPE(fp)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(mm(x1, y1))
    s.SetEnd(mm(x2, y2))
    s.SetLayer(layer)
    s.SetWidth(FromMM(w))
    fp.Add(s)


def fp_rect(fp, x1, y1, x2, y2, layer, w=0.12):
    s = pcbnew.PCB_SHAPE(fp)
    s.SetShape(pcbnew.SHAPE_T_RECTANGLE)
    s.SetStart(mm(x1, y1))
    s.SetEnd(mm(x2, y2))
    s.SetLayer(layer)
    s.SetWidth(FromMM(w))
    s.SetFilled(False)
    fp.Add(s)


def fp_poly(fp, pts, layer, w=0.05):
    s = pcbnew.PCB_SHAPE(fp)
    s.SetShape(pcbnew.SHAPE_T_POLY)
    chain = pcbnew.SHAPE_LINE_CHAIN()
    for x, y in pts:
        chain.Append(FromMM(x), FromMM(y))
    chain.SetClosed(True)
    poly = pcbnew.SHAPE_POLY_SET()
    poly.AddOutline(chain)
    s.SetPolyShape(poly)
    s.SetLayer(layer)
    s.SetWidth(FromMM(w))
    s.SetFilled(False)
    fp.Add(s)


def fp_text(fp, text, x, y, layer, size=0.8, rot=0):
    t = pcbnew.PCB_TEXT(fp)
    t.SetText(text)
    t.SetPosition(mm(x, y))
    t.SetLayer(layer)
    t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size)))
    t.SetTextThickness(FromMM(size * 0.15))
    t.SetTextAngleDegrees(rot)
    fp.Add(t)
    return t


def tht_pad(fp, number, x, y, drill, dia, netname=None, shape=pcbnew.PAD_SHAPE_CIRCLE):
    p = pcbnew.PAD(fp)
    p.SetNumber(number)
    p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    p.SetShape(shape)
    p.SetSize(mm(dia, dia))
    p.SetDrillSize(mm(drill, drill))
    p.SetLayerSet(pcbnew.PAD.PTHMask())
    p.SetPosition(mm(x, y))
    if netname:
        p.SetNet(net(netname))
    fp.Add(p)
    return p


def smd_pad(fp, number, x, y, w, h, netname=None):
    p = pcbnew.PAD(fp)
    p.SetNumber(number)
    p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    p.SetShape(pcbnew.PAD_SHAPE_ROUNDRECT)
    p.SetRoundRectRadiusRatio(0.2)
    p.SetSize(mm(w, h))
    p.SetLayerSet(pcbnew.PAD.SMDMask())
    p.SetPosition(mm(x, y))
    if netname:
        p.SetNet(net(netname))
    fp.Add(p)
    return p


def new_fp(ref, value, lib, name, smd):
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    fp.SetAttributes(pcbnew.FP_SMD if smd else pcbnew.FP_THROUGH_HOLE)
    board.Add(fp)
    return fp


# ----------------------------------------------------------------------------
# A1: Arduino Pro Mini (top side)
# ----------------------------------------------------------------------------
PM_NET = {"VCC": "VCC", "GND": "GND", "D2": "GDO0", "D3": "D3", "RAW": "RAW",
          "A4": "SDA", "A5": "SCL",
          "D10": "CSN", "D11": "MOSI", "D12": "MISO", "D13": "SCK"}
SCH_PIN_NAME = {"D13": "D13/SCK", "D12": "D12/MISO", "D11": "D11/MOSI", "D10": "D10/SS"}

a1 = new_fp("A1", "Arduino Pro Mini 3V3/8MHz", "promini_cc1101", "Arduino_Pro_Mini", smd=False)
for num, name, x, y in PM_PADS:
    # FTDI row: plated but unconnected (except GND), so any header style fits
    n = PM_NET.get(name) if y > 3 else None
    if n is None:
        sch_name = SCH_PIN_NAME.get(name, name) if y > 3 else "FTDI_" + name
        n = f"unconnected-(A1-{sch_name}-Pad{num})"
    tht_pad(a1, num, x, y, PM_DRILL, PM_PAD, n)
fp_rect(a1, 0, 0, PM_W, PM_H, pcbnew.F_Fab, 0.1)
# courtyard: U-shape covering the header strips only (interior is free under
# a header-mounted board, which is where C1 sits)
fp_poly(a1, [(-0.25, -0.25), (PM_W + 0.25, -0.25), (PM_W + 0.25, PM_H + 0.25), (PM_W - 2.6, PM_H + 0.25),
             (PM_W - 2.6, 2.6), (2.6, 2.6), (2.6, PM_H + 0.25), (-0.25, PM_H + 0.25)], pcbnew.F_CrtYd, 0.05)
# silkscreen: outline segments that stay inside the board, plus markers
fp_line(a1, 2.6, PM_H + 0.3, PM_W - 2.6, PM_H + 0.3, pcbnew.F_SilkS)
fp_text(a1, "FTDI", PM_W / 2, 1.27, pcbnew.F_Fab, 0.7)
fp_text(a1, "Pro Mini 3V3", PM_W / 2, 8.0, pcbnew.F_Fab, 1.0)
fp_text(a1, "D10", PM_RIGHT_X - 2.6, PM_H - 1.27, pcbnew.F_Fab, 0.6)
fp_text(a1, "D9", PM_LEFT_X + 2.2, PM_H - 1.27, pcbnew.F_Fab, 0.6)
# bottom-side pin names (readable from the back)
for num, name, x, y in PM_PADS:
    if y < 3 or name in ("A4", "A5"):
        continue
    lx = x + 2.7 if x < 5 else x - 2.7
    if x > 5 and 10.5 < y < 17.5:      # clear of the A4/A5 inner holes
        lx = x - 5.7
    t = fp_text(a1, name, lx, y, pcbnew.B_SilkS, 0.8)
    t.SetMirrored(True)
t = fp_text(a1, "FTDI", PM_W / 2, 3.4, pcbnew.B_SilkS, 0.8)
t.SetMirrored(True)
a1.Reference().SetPosition(mm(PM_W / 2, 5.5))
a1.Reference().SetLayer(pcbnew.F_Fab)
a1.Value().SetPosition(mm(PM_W / 2, 10.0))
a1.Value().SetLayer(pcbnew.F_Fab)
a1.Value().SetVisible(False)
a1.SetPosition(mm(*PM_POS))

# ----------------------------------------------------------------------------
# U1: CC1101 11-pin module (bottom side)
# ----------------------------------------------------------------------------
MOD_NET = {"VCC": "VCC", "GND": "GND", "MOSI": "MOSI", "SCLK": "SCK", "MISO": "MISO",
           "GDO2": "unconnected-(U1-GDO2-Pad6)", "GDO0": "GDO0", "CSN": "CSN", "ANT": "unconnected-(U1-ANT-Pad10)"}

u1 = new_fp("U1", "CC1101 868MHz 11-pin", "promini_cc1101", "CC1101_11pin_castellated", smd=True)
for num, name, x, y, w, h in MOD_PADS:
    if name == "ANT":
        # plated 1.0 mm hole aligned with the module's ANT castellation: the wire
        # antenna goes through carrier and castellation and is soldered once
        p = tht_pad(u1, num, x, y, 1.0, 2.0, MOD_NET[name], shape=pcbnew.PAD_SHAPE_OVAL)
        p.SetSize(mm(w, h))
    else:
        smd_pad(u1, num, x, y, w, h, MOD_NET[name])
fp_rect(u1, -MOD_EDGE, -MOD_H / 2, MOD_EDGE, MOD_H / 2, pcbnew.F_Fab, 0.1)
fp_rect(u1, -MOD_EDGE - 0.25, -MOD_H / 2 - 0.25, MOD_EDGE + 0.25, MOD_H / 2 + 0.25, pcbnew.F_CrtYd, 0.05)
# silk outline on the two edges without pads
fp_line(u1, -MOD_EDGE, -MOD_H / 2 - 0.15, MOD_EDGE, -MOD_H / 2 - 0.15, pcbnew.F_SilkS)
fp_line(u1, -MOD_EDGE, MOD_H / 2 + 0.15, MOD_EDGE, MOD_H / 2 + 0.15, pcbnew.F_SilkS)
for num, name, x, y, w, h in MOD_PADS:
    lx = x + 3.1 if x < 0 else x - 3.1
    fp_text(u1, name, lx, y, pcbnew.F_SilkS, 0.8)
fp_text(u1, "CC1101 868MHz", 0, -3.0, pcbnew.F_Fab, 0.9)
fp_text(u1, "component side UP", 0, 3.0, pcbnew.F_Fab, 0.6)
u1.Reference().SetPosition(mm(0, -6.0))
u1.Reference().SetLayer(pcbnew.F_Fab)
u1.Value().SetVisible(False)
u1.Value().SetLayer(pcbnew.F_Fab)

u1.SetPosition(mm(*MOD_CENTER))
u1.Flip(mm(*MOD_CENTER), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
# choose the rotation that puts the signal edge toward the Pro Mini with VCC
# on the left (seen from the top)
vcc_pad = [p for p in u1.Pads() if p.GetNumber() == "1"][0]
for ang in (0, 90, 180, 270):
    u1.SetOrientationDegrees(ang)
    pos = vcc_pad.GetPosition()
    if pcbnew.ToMM(pos.x) < MOD_CENTER[0] and pcbnew.ToMM(pos.y) < MOD_CENTER[1]:
        break
else:
    sys.exit("could not orient module")

modpad = {}
for p in u1.Pads():
    n = [m for m in MOD_PADS if m[0] == p.GetNumber()][0][1]
    modpad.setdefault(n, []).append((pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)))
print("module pads (top view):", {k: [(round(x, 2), round(y, 2)) for x, y in v] for k, v in modpad.items()})
assert abs(modpad["VCC"][0][0] - 1.89) < 0.05 and abs(modpad["CSN"][0][0] - 15.89) < 0.05, "unexpected pad order"

# ----------------------------------------------------------------------------
# C1 (10 uF, optional), R1 (4.7k DS18B20 pull-up, optional), J1 sensor header
# ----------------------------------------------------------------------------
def passive_0805(ref, value, name, net1, net2, pos, rot=0):
    fp = new_fp(ref, value, "promini_cc1101", name, smd=True)
    smd_pad(fp, "1", -0.95, 0, 1.0, 1.3, net1)
    smd_pad(fp, "2", 0.95, 0, 1.0, 1.3, net2)
    fp_rect(fp, -1.0, -0.625, 1.0, 0.625, pcbnew.F_Fab, 0.1)
    fp_rect(fp, -1.7, -0.9, 1.7, 0.9, pcbnew.F_CrtYd, 0.05)
    fp_line(fp, -0.35, -0.95, 0.35, -0.95, pcbnew.F_SilkS)
    fp_line(fp, -0.35, 0.95, 0.35, 0.95, pcbnew.F_SilkS)
    fp.Reference().SetPosition(mm(0, -1.6))
    fp.Reference().SetTextSize(VECTOR2I(FromMM(0.8), FromMM(0.8)))
    fp.Reference().SetTextThickness(FromMM(0.1))
    fp.Value().SetVisible(False)
    fp.Value().SetLayer(pcbnew.F_Fab)
    fp.SetPosition(mm(*pos))
    fp.SetOrientationDegrees(rot)
    return fp


C1_POS = (3.5, 41.0)      # top side, over the module area
R1_POS = (5.6, 30.3)      # top side, under the Pro Mini (header standoff gives room)
c1 = passive_0805("C1", "22uF", "C_0805", "VCC", "GND", C1_POS)
r1 = passive_0805("R1", "4.7k (DS18B20 only)", "R_0805", "D3_S", "VCC", R1_POS)
r1.Reference().SetPosition(mm(R1_POS[0] + 2.7, R1_POS[1]))
# R2: series protection between the MCU D3 and the sensor side (330R, or 0R)
# C2: optional 100 nF debounce on the sensor side (reed/button only, NOT for DS18B20)
D3_X = 3.6
R2_POS = (D3_X, 25.0)
C2_POS = (6.0, 28.0)
r2 = passive_0805("R2", "330R", "R_0805", "D3_S", "D3", R2_POS, rot=90)   # pad2 (upper) = MCU side
c2 = passive_0805("C2", "100nF (DNP)", "C_0805", "D3_S", "GND", C2_POS)
c2.Reference().SetPosition(mm(C2_POS[0] + 2.7, C2_POS[1]))
r2.Reference().SetPosition(mm(R2_POS[0] + 1.8, R2_POS[1]))
r2.Reference().SetTextAngleDegrees(0)

# Battery input: J2 (JST PH side-entry SMD), Q1 reverse-polarity P-FET.
# (v1.5: the JP1 current-measurement link is gone; measure at the battery cable.)
def sot23(ref, value, nets, pos, rot=0):
    fp = new_fp(ref, value, "promini_cc1101", "SOT-23", smd=True)
    for num, (x, y) in zip(("1", "2", "3"), ((-0.95, 1.0), (0.95, 1.0), (0.0, -1.0))):
        smd_pad(fp, num, x, y, 0.9, 1.0, nets[num])
    fp_rect(fp, -0.7, -0.75, 0.7, 0.75, pcbnew.F_Fab, 0.1)
    fp_rect(fp, -1.7, -1.75, 1.7, 1.75, pcbnew.F_CrtYd, 0.05)
    fp_line(fp, -0.7, -0.4, 0.7, -0.4, pcbnew.F_SilkS)
    fp.Reference().SetPosition(mm(0, -2.4))
    fp.Reference().SetTextSize(VECTOR2I(FromMM(0.8), FromMM(0.8)))
    fp.Reference().SetTextThickness(FromMM(0.1))
    fp.Value().SetVisible(False)
    fp.Value().SetLayer(pcbnew.F_Fab)
    fp.SetPosition(mm(*pos))
    fp.SetOrientationDegrees(rot)
    return fp


Q1_POS = (5.95, 44.5)
q1 = sot23("Q1", "AO3401A", {"1": "GND", "2": "VCC", "3": "BAT+"}, Q1_POS, rot=180)

J2_POS = (12.8, 48.5)     # cable exits over the right-hand board edge
# Land pattern per JST ePH drawing (as in KiCad's JST_PH_S2B-PH-SM4-TB footprint):
# contacts 1.0 x 3.5 at 2.0 mm pitch; tab pads 1.5 x 3.4, 6.7 mm apart along the
# pitch axis and 5.75 mm from the contact pad centres along the depth axis.
# Local frame: x = depth axis (cable exits +x), y = pitch axis.
j2 = new_fp("J2", "JST PH battery", "promini_cc1101", "JST_PH_S2B-PH-SM4-TB_SMD", smd=True)
smd_pad(j2, "1", -2.85, -1.0, 3.5, 1.0, "BAT+")
smd_pad(j2, "2", -2.85, 1.0, 3.5, 1.0, "GND")
smd_pad(j2, "MP", 2.9, -3.35, 3.4, 1.5, None)
smd_pad(j2, "MP", 2.9, 3.35, 3.4, 1.5, None)
fp_rect(j2, -3.2, -3.95, 4.4, 3.95, pcbnew.F_Fab, 0.1)
fp_rect(j2, -5.1, -4.6, 5.1, 4.6, pcbnew.F_CrtYd, 0.05)
fp_line(j2, 4.4, -2.0, 4.4, 2.0, pcbnew.F_SilkS)
fp_text(j2, "+", -5.5, -1.0, pcbnew.F_SilkS, 1.0)
fp_text(j2, "-", -5.5, 1.0, pcbnew.F_SilkS, 1.0)
j2.Reference().SetVisible(False)
j2.Reference().SetLayer(pcbnew.F_Fab)
j2.Value().SetVisible(False)
j2.Value().SetLayer(pcbnew.F_Fab)
j2.SetPosition(mm(*J2_POS))

j1 = new_fp("J1", "Sensor header", "promini_cc1101", "PinHeader_1x06_P2.54mm", smd=False)
for i, name in enumerate(HDR_PINS):
    p = tht_pad(j1, str(i + 1), i * 2.54, 0, 1.0, 1.7, {"D3": "D3_S"}.get(name, name),
                shape=pcbnew.PAD_SHAPE_RECT if i == 0 else pcbnew.PAD_SHAPE_CIRCLE)
    t = fp_text(j1, name, i * 2.54, 2.7, pcbnew.F_SilkS, 0.8, rot=90)
fp_rect(j1, -1.27, -1.27, 5 * 2.54 + 1.27, 1.27, pcbnew.F_Fab, 0.1)
fp_rect(j1, -1.52, -1.52, 5 * 2.54 + 1.52, 1.52, pcbnew.F_CrtYd, 0.05)
j1.Reference().SetPosition(mm(5 * 2.54 + 2.6, 0))
j1.Reference().SetTextSize(VECTOR2I(FromMM(0.8), FromMM(0.8)))
j1.Reference().SetTextThickness(FromMM(0.12))
j1.Reference().SetLayer(pcbnew.F_Fab)
j1.Value().SetVisible(False)
j1.Value().SetLayer(pcbnew.F_Fab)
j1.SetPosition(mm(HDR_X0, HDR_Y))
HDR = {name: (HDR_X0 + i * 2.54, HDR_Y) for i, name in enumerate(HDR_PINS)}

# ----------------------------------------------------------------------------
# Board outline
# ----------------------------------------------------------------------------
def edge_line(x1, y1, x2, y2):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(mm(x1, y1))
    s.SetEnd(mm(x2, y2))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(FromMM(0.1))
    board.Add(s)


def edge_arc(cx, cy, r, start_deg, end_deg):
    """Quarter-circle corner: start point at start_deg, sweep to end_deg (CCW on screen)."""
    import math
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_ARC)
    a0 = math.radians(start_deg)
    a1 = math.radians(end_deg)
    am = (a0 + a1) / 2
    s.SetArcGeometry(mm(cx + r * math.cos(a0), cy - r * math.sin(a0)),
                     mm(cx + r * math.cos(am), cy - r * math.sin(am)),
                     mm(cx + r * math.cos(a1), cy - r * math.sin(a1)))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(FromMM(0.1))
    board.Add(s)


R = 1.0
edge_line(R, 0, BOARD_W - R, 0)
edge_line(BOARD_W, R, BOARD_W, BOARD_H - R)
edge_line(BOARD_W - R, BOARD_H, R, BOARD_H)
edge_line(0, BOARD_H - R, 0, R)
edge_arc(R, R, R, 90, 180)
edge_arc(BOARD_W - R, R, R, 0, 90)
edge_arc(BOARD_W - R, BOARD_H - R, R, 270, 360)
edge_arc(R, BOARD_H - R, R, 180, 270)

# ----------------------------------------------------------------------------
# Tracks and vias
# ----------------------------------------------------------------------------
def track(netname, layer, pts, w=TRACK_SIG):
    n = net(netname)
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(mm(x1, y1))
        t.SetEnd(mm(x2, y2))
        t.SetWidth(FromMM(w))
        t.SetLayer(layer)
        t.SetNet(n)
        board.Add(t)


def via(netname, x, y):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(mm(x, y))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetDrill(FromMM(VIA_DRILL))
    try:
        v.SetWidth(FromMM(VIA_D))
    except TypeError:
        v.SetWidth(pcbnew.F_Cu, FromMM(VIA_D))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNet(net(netname))
    board.Add(v)


F, B = pcbnew.F_Cu, pcbnew.B_Cu
pm = {name: (x, y) for _, name, x, y in PM_PADS if y > 3 and name not in ("GND", "RST")}
mp = {k: v[0] for k, v in modpad.items()}
PAD_ENTRY = MOD_TOP_EDGE - 0.2      # castellation pad centre (y)
GND_L = (PM_LEFT_X, 11.43)          # explicit: two side pins are both named GND
GND_R = (PM_RIGHT_X, 6.35)
LANE_Y = 33.4                       # free lane between Pro Mini rings and header rings
CH_R = 15.05                        # right-hand channel between A4/A5 holes and the column

# Header gaps (x) that module signals pass through: between J1 pins
GAP_SCK, GAP_MISO, GAP_MOSI, GAP_GDO0, GAP_CSN = 6.35, 8.89, 11.43, 13.97, 16.8

# --- B.Cu ---------------------------------------------------------------------
# RAW: right column top -> across the top -> down the left edge -> J1 RAW
track("RAW", B, [pm["RAW"], (15.5, 5.2), (3.3, 5.2), (2.6, 5.9), (2.6, 33.0), HDR["RAW"]])
# VCC: right column -> jog above A5 -> left -> down x=3.3 -> J1 VCC -> module VCC pad
track("VCC", B, [pm["VCC"], (15.6, 10.7), (12.4, 10.7), (11.9, 11.43), (3.3, 11.43), (3.3, 33.0), HDR["VCC"]], TRACK_PWR)
track("VCC", B, [HDR["VCC"], (5.08, 36.2), (2.3, 37.4), (mp["VCC"][0], 38.1), (mp["VCC"][0], PAD_ENTRY)], TRACK_PWR)
# GND stub for the right-hand GND pin
track("GND", B, [GND_R, (15.0, 6.35)], TRACK_PWR)
# SPI: diagonals from the right column, straight down through the header gaps
track("SCK", B, [pm["D13"], (GAP_SCK, 33.0), (GAP_SCK, 37.0), (mp["SCLK"][0], 38.0), (mp["SCLK"][0], PAD_ENTRY)])
track("MISO", B, [pm["D12"], (GAP_MISO, 33.0), (GAP_MISO, 37.0), (mp["MISO"][0], 38.0), (mp["MISO"][0], PAD_ENTRY)])
MOSI_VIA1 = (GAP_MOSI, 36.6)
MOSI_VIA2 = (5.5, 37.2)
track("MOSI", B, [pm["D11"], (GAP_MOSI, 33.0), MOSI_VIA1])
via("MOSI", *MOSI_VIA1)
track("MOSI", F, [MOSI_VIA1, (GAP_MOSI, 37.2), MOSI_VIA2])
via("MOSI", *MOSI_VIA2)
track("MOSI", B, [MOSI_VIA2, (mp["MOSI"][0], 38.3), (mp["MOSI"][0], PAD_ENTRY)])
# CSN: D10 -> along the right edge -> module CSN
track("CSN", B, [pm["D10"], (GAP_CSN, 32.6), (GAP_CSN, 36.4), (16.2, 37.7), (mp["CSN"][0], PAD_ENTRY)])

# --- F.Cu ---------------------------------------------------------------------
# GND stub for the left-hand GND pin
track("GND", F, [GND_L, (D3_X + 0.9, 11.43)], TRACK_PWR)
# D3: left column -> down x=3.2 -> R2 (series) -> D3_S -> lane -> J1 D3
track("D3", F, [pm["D3"], (D3_X, 17.2), (D3_X, R2_POS[1] - 0.95)])
track("D3_S", F, [(D3_X, R2_POS[1] + 0.95), (D3_X, 32.6), (3.6, LANE_Y), (6.9, LANE_Y), HDR["D3"]])
# R1 pull-up and C2 debounce hang on the sensor side
track("D3_S", F, [(R1_POS[0] - 0.95, R1_POS[1]), (D3_X, R1_POS[1])])
track("D3_S", F, [(C2_POS[0] - 0.95, C2_POS[1]), (D3_X, C2_POS[1])])
C2_GND_VIA = (7.5, C2_POS[1])
track("GND", F, [(C2_POS[0] + 0.95, C2_POS[1]), C2_GND_VIA])
via("GND", *C2_GND_VIA)
R1_VIA = (7.5, R1_POS[1])
track("VCC", F, [(R1_POS[0] + 0.95, R1_POS[1]), R1_VIA])
via("VCC", *R1_VIA)
track("VCC", B, [R1_VIA, (3.3, R1_POS[1])], TRACK_PWR)
# GDO0: D2 -> along y=13.97 -> up over A5 -> right channel -> down -> gap -> via -> pad
GDO0_VIA = (GAP_GDO0, 36.6)
track("GDO0", F, [pm["D2"], (8.5, 13.97), (9.2, 11.3), (14.8, 11.3), (CH_R, 11.55), (CH_R, 32.8),
                  (GAP_GDO0, 33.7), GDO0_VIA])
via("GDO0", *GDO0_VIA)
track("GDO0", B, [GDO0_VIA, (mp["GDO0"][0], 38.0), (mp["GDO0"][0], PAD_ENTRY)])
# I2C: inner A4/A5 holes -> straight down -> J1
track("SCL", F, [A5_POS, (10.16, 14.0), (10.16, 33.6), HDR["SCL"]])
track("SDA", F, [A4_POS, (12.9, 16.0), (12.9, 33.6), HDR["SDA"]])
# C1: pad1 -> J1 VCC pin (top side), pad2 -> GND via
track("VCC", F, [(C1_POS[0] - 0.95, C1_POS[1]), (2.55, 37.3), (4.2, 36.3), HDR["VCC"]], TRACK_PWR)
# Battery: J2.1 -> Q1 drain; Q1 source -> C1 / VCC
track("BAT+", F, [(J2_POS[0] - 2.75, J2_POS[1] - 1.0), (Q1_POS[0], Q1_POS[1] + 1.0)], 0.5)
track("VCC", F, [(Q1_POS[0] - 0.95, Q1_POS[1] - 1.0), (C1_POS[0] - 0.95 + 1.5, C1_POS[1] + 2.5), (C1_POS[0] - 0.95, C1_POS[1] + 1.0), (C1_POS[0] - 0.95, C1_POS[1])], 0.5)
C1_GND_VIA = (C1_POS[0] + 2.1, C1_POS[1])
track("GND", F, [(C1_POS[0] + 0.95, C1_POS[1]), C1_GND_VIA], TRACK_PWR)
via("GND", *C1_GND_VIA)

# GND stitching vias (both pours)
for (x, y) in [(8.89, 4.2), (6.0, 12.7), (5.0, 21.0), (11.5, 21.0), (14.0, 24.0), (8.89, 27.0),
               (9.3, 31.5), (11.5, 31.9), (13.75, 32.5), (5.5, 32.3), (8.89, 8.0),
               (14.1, 13.85),
               (16.8, 41.5), (3.0, 54.0), (16.8, 54.5), (6.5, 50.5), (9.3, 43.0), (1.2, 50.5)]:
    via("GND", x, y)

# ----------------------------------------------------------------------------
# Ground pours
# ----------------------------------------------------------------------------
def gnd_zone(layer, pts, name):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(net("GND"))
    z.SetAssignedPriority(0)
    z.SetLocalClearance(FromMM(0.3))
    z.SetMinThickness(FromMM(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(FromMM(0.3))
    z.SetThermalReliefSpokeWidth(FromMM(0.4))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_AREA)
    z.SetMinIslandArea(int(FromMM(1.5) * FromMM(1.0)))
    o = z.Outline()
    o.NewOutline()
    for (x, y) in pts:
        o.Append(FromMM(x), FromMM(y))
    z.SetZoneName(name)
    board.Add(z)
    return z


# Two pours per layer: the Pro Mini interior (header strips excluded, they only
# produce slivers) and the module area.  The sensor-header strip in between is
# left without pour; the pours are tied together by the stitching vias.
ZONE_SPLIT = 37.7      # just above the castellation pads; the sensor-header strip has no pour
for layer, tag in ((pcbnew.F_Cu, "F"), (pcbnew.B_Cu, "B")):
    xl = 2.5 if layer == pcbnew.B_Cu else D3_X + 0.5
    gnd_zone(layer, [(xl, 2.7), (BOARD_W - 2.5, 2.7), (BOARD_W - 2.5, PM_H), (xl, PM_H)], "GND_" + tag + "_promini")
    yb = BOARD_H if layer == pcbnew.F_Cu else MOD_TOP_EDGE + MOD_W   # B: stop at the ANT-side pad row (slivers otherwise)
    gnd_zone(layer, [(0, ZONE_SPLIT), (BOARD_W, ZONE_SPLIT), (BOARD_W, yb), (0, yb)], "GND_" + tag + "_module")
# The header GND pin bridges the two pours: F.Cu stub down into the module pour,
# B.Cu stub up into the interior pour (right-hand pocket, which is stitched).
track("GND", F, [HDR["GND"], (HDR["GND"][0], 38.0)], TRACK_PWR)
track("GND", B, [HDR["GND"], (15.0, 33.6), (14.6, 32.9)], TRACK_PWR)

# ----------------------------------------------------------------------------
# Board text
# ----------------------------------------------------------------------------
def text(s, x, y, layer, size=1.0, rot=0, mirrored=False, bold=False):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetPosition(mm(x, y))
    t.SetLayer(layer)
    t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size)))
    t.SetTextThickness(FromMM(size * (0.2 if bold else 0.15)))
    t.SetTextAngleDegrees(rot)
    t.SetMirrored(mirrored)
    board.Add(t)


text("BAT LiPo/18650", 12.3, 40.6, pcbnew.F_SilkS, 0.8)
text("ProMini+CC1101 v1.5", BOARD_W / 2, 54.3, pcbnew.F_SilkS, 0.8, bold=True)
text("3V3 ONLY / FTDI @3V3", BOARD_W / 2, 55.6, pcbnew.F_SilkS, 0.8)
text("CC1101 on back side", BOARD_W / 2, 56.9, pcbnew.F_SilkS, 0.8)
text("ANT >", 5.6, 58.6, pcbnew.F_SilkS, 0.8)

# ----------------------------------------------------------------------------
# Fill zones and save
# ----------------------------------------------------------------------------
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
board.BuildConnectivity()
board.Save(OUT)
print("wrote", OUT)

# Export the three footprints into the project's .pretty library so the
# board's footprint links resolve (see fp-lib-table).
LIB = os.path.join(HERE, "promini_cc1101.pretty")
os.makedirs(LIB, exist_ok=True)
try:
    io = pcbnew.PCB_IO_KICAD_SEXPR()
    for fp in board.Footprints():
        copy = pcbnew.FOOTPRINT(fp)
        copy.SetPosition(VECTOR2I(0, 0))
        copy.SetOrientationDegrees(0)
        if copy.IsFlipped():
            copy.Flip(VECTOR2I(0, 0), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        for p in copy.Pads():
            p.SetNet(pcbnew.NETINFO_ITEM(board, ""))
        io.FootprintSave(LIB, copy)
    print("footprints saved to", LIB)
except Exception as e:
    print("footprint export skipped:", e)
