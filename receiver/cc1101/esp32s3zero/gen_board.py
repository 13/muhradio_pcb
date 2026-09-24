#!/usr/bin/env python3
"""Generate the ESP32-S3-Zero + CC1101 (11-pin) receiver carrier PCB for
muhradio (receiver/platformio.ini env esp32-s3-zero-cc1101 / -bresser).

Run:  python3 gen_board.py            (writes s3zero_cc1101.kicad_pcb)

Coordinates in mm, origin at the board's top-left corner, y down.  The
ESP32-S3-Zero sits on the top side at the left with its USB-C on the top
edge; the CC1101 module sits on the top side to the right, antenna edge at
the right board edge.  See docs/DESIGN.md.
"""
import os
import sys

import pcbnew
from pcbnew import VECTOR2I, FromMM

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "s3zero_cc1101"
OUT = os.path.join(HERE, NAME + ".kicad_pcb")

# ----------------------------------------------------------------------------
# Geometry (mm)
# ----------------------------------------------------------------------------
BOARD_W = 44.8
BOARD_H = 32.0

# ESP32-S3-Zero (Waveshare): 18.0 x 23.5 mm, 2 x 9 castellated holes,
# rows 15.24 mm apart, 1.38 mm in from the long edges, first hole 1.59 mm
# from the USB end, 2.54 mm pitch.  Pin numbering as a DIP: 1..9 down the
# left (USB end first), 10..18 up the right.
S3_W, S3_H = 18.0, 23.5
S3_POS = (2.5, 2.0)                       # top-left corner of the S3-Zero
S3_ROW_IN = 1.38
S3_PIN0 = 1.59
S3_LEFT = ["5V", "GND", "3V3", "GP1", "GP2", "GP3", "GP4", "GP5", "GP6"]
S3_RIGHT_BOTTOM_UP = ["GP7", "GP8", "GP9", "GP10", "GP11", "GP12", "GP13", "RX44", "TX43"]

S3_PADS = []                              # (number, name, x, y) relative to S3 corner
for i, n in enumerate(S3_LEFT):
    S3_PADS.append((str(i + 1), n, S3_ROW_IN, S3_PIN0 + i * 2.54))
for i, n in enumerate(S3_RIGHT_BOTTOM_UP):
    S3_PADS.append((str(i + 10), n, S3_W - S3_ROW_IN, S3_PIN0 + (8 - i) * 2.54))

# muhradio receiver wiring (receiver/platformio.ini, env esp32-s3-zero-cc1101)
S3_NET = {"GND": "GND", "3V3": "3V3", "GP9": "SCK", "GP7": "MISO", "GP8": "MOSI",
          "GP6": "CSN", "GP2": "GDO0", "GP4": "GDO2"}

# CC1101 11-pin module (same footprint as the transmitter carrier)
MOD_W, MOD_H = 19.3, 17.0
MOD_EDGE = MOD_W / 2
MOD_SIG_PITCH, MOD_ANT_PITCH, MOD_ANT_OFFSET = 2.0, 2.54, 1.0
CAST_OUT, CAST_IN = 1.2, 0.8
MOD_SIG = ["VCC", "GND", "MOSI", "SCLK", "MISO", "GDO2", "GDO0", "CSN"]
MOD_PADS = []
for i, n in enumerate(MOD_SIG):
    MOD_PADS.append((str(i + 1), n, -(MOD_EDGE + (CAST_OUT - CAST_IN) / 2), -7.0 + i * MOD_SIG_PITCH, CAST_OUT + CAST_IN, 1.2))
for i, n in enumerate(["GND", "ANT", "GND"]):
    MOD_PADS.append((str(i + 9), n, MOD_EDGE + (CAST_OUT - CAST_IN) / 2, MOD_ANT_OFFSET + (i - 1) * MOD_ANT_PITCH, CAST_OUT + CAST_IN, 1.8 if n == "ANT" else 1.6))
MOD_NET = {"VCC": "VCC_RF", "GND": "GND", "MOSI": "MOSI", "SCLK": "SCK", "MISO": "MISO",
           "GDO2": "GDO2", "GDO0": "GDO0", "CSN": "CSN", "ANT": "unconnected-(U2-ANT-Pad10)"}

# Module placement: signal edge faces the S3-Zero's right column, SCLK pad
# level with GP9 (SCK).
MOD_LEFT = 24.0
S3_SCK_Y = S3_POS[1] + S3_PIN0 + 6 * 2.54          # GP9 row
MOD_CENTER = (MOD_LEFT + MOD_EDGE, S3_SCK_Y + 1.0)  # SCLK pad is at centre_y - 1.0

# Rules
CLEARANCE, TRACK_SIG, TRACK_PWR = 0.2, 0.3, 0.5
VIA_D, VIA_DRILL, EDGE_CLR = 0.6, 0.3, 0.3


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
except Exception as e:
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


def tht_pad(fp, number, x, y, drill, dia, netname=None, shape=pcbnew.PAD_SHAPE_CIRCLE, size=None, offset=None):
    p = pcbnew.PAD(fp)
    p.SetNumber(number)
    p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    p.SetShape(shape)
    p.SetSize(mm(*(size or (dia, dia))))
    p.SetDrillSize(mm(drill, drill))
    p.SetLayerSet(pcbnew.PAD.PTHMask())
    p.SetPosition(mm(x, y))
    if offset:
        p.SetOffset(mm(*offset))
    if netname:
        p.SetNet(net(netname))
    fp.Add(p)
    return p


def npth(fp, x, y, drill):
    p = pcbnew.PAD(fp)
    p.SetNumber("")
    p.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
    p.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    p.SetSize(mm(drill, drill))
    p.SetDrillSize(mm(drill, drill))
    p.SetLayerSet(pcbnew.PAD.UnplatedHoleMask())
    p.SetPosition(mm(x, y))
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


def new_fp(ref, value, lib, name, smd, board_only=False):
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    attr = pcbnew.FP_SMD if smd else pcbnew.FP_THROUGH_HOLE
    if board_only:
        attr |= pcbnew.FP_BOARD_ONLY | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES
    fp.SetAttributes(attr)
    board.Add(fp)
    return fp


def ref_style(fp, x, y, size=0.8, layer=pcbnew.F_SilkS, visible=True):
    r = fp.Reference()
    r.SetPosition(mm(x, y))
    r.SetTextSize(VECTOR2I(FromMM(size), FromMM(size)))
    r.SetTextThickness(FromMM(0.12))
    r.SetLayer(layer)
    r.SetVisible(visible)
    fp.Value().SetVisible(False)
    fp.Value().SetLayer(pcbnew.F_Fab)


# ----------------------------------------------------------------------------
# U1: ESP32-S3-Zero (top side).  Pads are oval with the hole offset outward so
# the pad ledge reaches past the S3-Zero edge for castellation soldering; the
# same pads take 2.54 mm header pins.
# ----------------------------------------------------------------------------
u1 = new_fp("U1", "ESP32-S3-Zero", "s3zero_cc1101", "Waveshare_ESP32-S3-Zero", smd=False)
for num, name, x, y in S3_PADS:
    n = S3_NET.get(name)
    if n is None:
        n = f"unconnected-(U1-{name}-Pad{num})"
    outward = -0.45 if x < S3_W / 2 else 0.45
    tht_pad(u1, num, x, y, 1.0, 1.7, n, shape=pcbnew.PAD_SHAPE_OVAL, size=(2.6, 1.7), offset=(outward, 0))
fp_rect(u1, 0, 0, S3_W, S3_H, pcbnew.F_Fab, 0.1)
fp_rect(u1, -0.6, -0.6, S3_W + 0.6, S3_H + 0.6, pcbnew.F_CrtYd, 0.05)
fp_line(u1, 3.0, S3_H + 0.3, S3_W - 3.0, S3_H + 0.3, pcbnew.F_SilkS)
fp_text(u1, "USB-C", S3_W / 2, 1.3, pcbnew.F_Fab, 0.8)
fp_text(u1, "ESP32-S3-Zero", S3_W / 2, S3_H / 2, pcbnew.F_Fab, 1.0)
fp_text(u1, "2.4G ant", 3.5, S3_H - 1.5, pcbnew.F_Fab, 0.6)
for num, name, x, y in S3_PADS:            # pin names on the back, readable from below
    lx = x + 2.9 if x < S3_W / 2 else x - 2.9
    t = fp_text(u1, name, lx, y, pcbnew.B_SilkS, 0.8)
    t.SetMirrored(True)
ref_style(u1, S3_W / 2, -1.0, layer=pcbnew.F_Fab)
u1.SetPosition(mm(*S3_POS))

# ----------------------------------------------------------------------------
# U2: CC1101 module (top side, unrotated: signal edge left, VCC at the top)
# ----------------------------------------------------------------------------
u2 = new_fp("U2", "CC1101 868MHz 11-pin", "s3zero_cc1101", "CC1101_11pin_castellated", smd=True)
for num, name, x, y, w, h in MOD_PADS:
    if name == "ANT":
        p = tht_pad(u2, num, x, y, 1.0, 2.0, MOD_NET[name], shape=pcbnew.PAD_SHAPE_OVAL, size=(w, h))
    else:
        smd_pad(u2, num, x, y, w, h, MOD_NET[name])
fp_rect(u2, -MOD_EDGE, -MOD_H / 2, MOD_EDGE, MOD_H / 2, pcbnew.F_Fab, 0.1)
fp_rect(u2, -MOD_EDGE - 0.25, -MOD_H / 2 - 0.25, MOD_EDGE + 0.25, MOD_H / 2 + 0.25, pcbnew.F_CrtYd, 0.05)
fp_line(u2, -MOD_EDGE, -MOD_H / 2 - 0.15, MOD_EDGE, -MOD_H / 2 - 0.15, pcbnew.F_SilkS)
fp_line(u2, -MOD_EDGE, MOD_H / 2 + 0.15, MOD_EDGE, MOD_H / 2 + 0.15, pcbnew.F_SilkS)
for num, name, x, y, w, h in MOD_PADS:
    lx = x + 3.1 if x < 0 else x - 3.1
    fp_text(u2, name, lx, y, pcbnew.F_SilkS, 0.8)
fp_text(u2, "CC1101 868MHz", 0, -3.0, pcbnew.F_Fab, 0.9)
ref_style(u2, 0, -MOD_H / 2 - 1.2)
u2.SetPosition(mm(*MOD_CENTER))

modpad = {}
for p in u2.Pads():
    n = [m for m in MOD_PADS if m[0] == p.GetNumber()][0][1]
    modpad.setdefault(n, []).append((pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)))
mp = {k: v[0] for k, v in modpad.items()}
print("module pads:", {k: [(round(x, 2), round(y, 2)) for x, y in v] for k, v in modpad.items()})

s3 = {name: (S3_POS[0] + x, S3_POS[1] + y) for _, name, x, y in S3_PADS}

# ----------------------------------------------------------------------------
# 3V3 filter for the radio: FB1 (ferrite) -> C1 10uF + C2 100nF -> module VCC
# ----------------------------------------------------------------------------
def passive_0805(ref, value, name, net1, net2, pos, rot=0):
    fp = new_fp(ref, value, "s3zero_cc1101", name, smd=True)
    smd_pad(fp, "1", -0.95, 0, 1.0, 1.3, net1)
    smd_pad(fp, "2", 0.95, 0, 1.0, 1.3, net2)
    fp_rect(fp, -1.0, -0.625, 1.0, 0.625, pcbnew.F_Fab, 0.1)
    fp_rect(fp, -1.7, -0.9, 1.7, 0.9, pcbnew.F_CrtYd, 0.05)
    fp_line(fp, -0.35, -0.95, 0.35, -0.95, pcbnew.F_SilkS)
    fp_line(fp, -0.35, 0.95, 0.35, 0.95, pcbnew.F_SilkS)
    ref_style(fp, 0, -1.6)
    fp.SetPosition(mm(*pos))
    fp.SetOrientationDegrees(rot)
    return fp


FB1_POS = (23.0, 7.5)
C1_POS = (29.5, 7.5)
C2_POS = (33.5, 7.5)
fb1 = passive_0805("FB1", "ferrite 600R@100MHz", "R_0805", "3V3", "VCC_RF", FB1_POS)
c1 = passive_0805("C1", "10uF", "C_0805", "VCC_RF", "GND", C1_POS)
c2 = passive_0805("C2", "100nF", "C_0805", "VCC_RF", "GND", C2_POS)

# ----------------------------------------------------------------------------
# Mounting holes (M2.5), board-only
# ----------------------------------------------------------------------------
for ref, pos in (("H1", (40.0, 3.5)), ("H2", (41.5, 30.3))):
    h = new_fp(ref, "M2.5", "s3zero_cc1101", "MountingHole_2.7mm", smd=False, board_only=True)
    npth(h, 0, 0, 2.7)
    s = pcbnew.PCB_SHAPE(h)
    s.SetShape(pcbnew.SHAPE_T_CIRCLE)
    s.SetStart(mm(0, 0))
    s.SetEnd(mm(1.6, 0))
    s.SetLayer(pcbnew.F_CrtYd)
    s.SetWidth(FromMM(0.05))
    h.Add(s)
    ref_style(h, 0, 0, layer=pcbnew.F_Fab, visible=False)
    h.SetPosition(mm(*pos))

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


def edge_arc(cx, cy, r, a0, a1):
    import math
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_ARC)
    r0, r1 = math.radians(a0), math.radians(a1)
    rm = (r0 + r1) / 2
    s.SetArcGeometry(mm(cx + r * math.cos(r0), cy - r * math.sin(r0)),
                     mm(cx + r * math.cos(rm), cy - r * math.sin(rm)),
                     mm(cx + r * math.cos(r1), cy - r * math.sin(r1)))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(FromMM(0.1))
    board.Add(s)


R = 1.5
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
S3_L, S3_R = S3_POS[0], S3_POS[0] + S3_W           # S3-Zero body edges (x)
S3_BOT = S3_POS[1] + S3_H
S3_PAD_R = S3_R - S3_ROW_IN + 0.45 + 1.3             # right-hand S3 pads reach this x (20.87)
PAD_L = mp["CSN"][0] - (CAST_OUT + CAST_IN) / 2     # module pads' left end (22.8)
CH_F = 1.2                                          # F.Cu channel left of the S3 body (3V3)
CH_B1, CH_B2 = 0.9, 1.55                            # B.Cu channels left of the S3 body (GDO0, GDO2)

# SPI, right column -> module
track("SCK", F, [s3["GP9"], mp["SCLK"]])
track("MISO", F, [s3["GP7"], (21.4, s3["GP7"][1]), (21.4, mp["MISO"][1]), mp["MISO"]])
MOSI_VIA = (21.75, mp["MOSI"][1])
track("MOSI", B, [s3["GP8"], (MOSI_VIA[0], s3["GP8"][1]), MOSI_VIA])
via("MOSI", *MOSI_VIA)
track("MOSI", F, [MOSI_VIA, mp["MOSI"]])

# Left column signals: CSN on top around the S3 bottom; GDO0/GDO2 on the bottom
# layer, up through vias under the module into the inner ends of their pads.
LANE_CSN, LANE_GDO2, LANE_GDO0 = S3_BOT + 2.1, S3_BOT + 0.9, S3_BOT + 1.7
track("CSN", F, [s3["GP6"], (s3["GP6"][0], S3_BOT + 0.9), (mp["CSN"][0] - 0.5, LANE_CSN), (mp["CSN"][0] - 0.5, mp["CSN"][1])])
GDO2_VIA = (MOD_LEFT + 2.0, mp["GDO2"][1])
track("GDO2", B, [s3["GP4"], (CH_B2, s3["GP4"][1] + 0.9), (CH_B2, LANE_GDO2), (GDO2_VIA[0], LANE_GDO2), GDO2_VIA])
via("GDO2", *GDO2_VIA)
track("GDO2", F, [GDO2_VIA, mp["GDO2"]])
GDO0_VIA = (MOD_LEFT + 3.0, mp["GDO0"][1])
track("GDO0", B, [s3["GP2"], (CH_B1, s3["GP2"][1] + 0.9), (CH_B1, LANE_GDO0), (GDO0_VIA[0], LANE_GDO0), GDO0_VIA])
via("GDO0", *GDO0_VIA)
track("GDO0", F, [GDO0_VIA, mp["GDO0"]])

# S3-Zero GND pin: bottom layer, up the left channel and along the top strip into the right pour
track("GND", B, [s3["GND"], (1.0, s3["GND"][1]), (1.0, 0.8), (MOD_LEFT + 1.5, 0.8), (MOD_LEFT + 1.5, 2.0)], TRACK_PWR)

# 3V3: left column pin 3 -> up the left channel -> along the top strip -> FB1.1
TOP_Y = S3_POS[1] - 1.0
FB_IN = (FB1_POS[0] - 0.95, FB1_POS[1])
FB_OUT = (FB1_POS[0] + 0.95, FB1_POS[1])
track("3V3", F, [s3["3V3"], (CH_F, s3["3V3"][1] - 0.9), (CH_F, TOP_Y), (FB_IN[0], TOP_Y), FB_IN], TRACK_PWR)
# VCC_RF: FB1.2 -> module VCC pad, and a bus above the caps to C1.1 / C2.1
BUS_Y = C1_POS[1] - 1.9
track("VCC_RF", F, [FB_OUT, (mp["VCC"][0], FB_OUT[1] + 1.2), mp["VCC"]], TRACK_PWR)
track("VCC_RF", F, [FB_OUT, (FB_OUT[0] + 1.0, BUS_Y), (C2_POS[0] - 0.95, BUS_Y), (C2_POS[0] - 0.95, C2_POS[1])], TRACK_PWR)
track("VCC_RF", F, [(C1_POS[0] - 0.95, BUS_Y), (C1_POS[0] - 0.95, C1_POS[1])], TRACK_PWR)
# capacitor grounds
for pos in (C1_POS, C2_POS):
    track("GND", F, [(pos[0] + 0.95, pos[1]), (pos[0] + 2.0, pos[1])], TRACK_PWR)
    via("GND", pos[0] + 2.0, pos[1])

# GND stitching vias
for (x, y) in [(10.0, 30.2), (20.0, 30.2), (30.0, 30.2), (36.0, 30.2), (41.5, 12.0), (41.5, 26.5),
               (27.0, 3.0), (34.0, 3.0), (24.5, 3.3), (2.0, 30.2), (30.0, 12.5)]:
    via("GND", x, y)

# ----------------------------------------------------------------------------
# Ground pours: everything except the S3-Zero body on the top layer (its
# underside carries exposed pads) and a strip around the antenna pads.
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


# Pours stay clear of the S3-Zero (exposed pads on its underside, and the
# 0.84 mm gaps between its edge pads only produce slivers) and of the
# channel between the two modules.
ZX = MOD_LEFT                          # pour from the module's left edge rightwards
ANT_Y0, ANT_Y1 = mp["ANT"][1] - 4.0, mp["ANT"][1] + 4.0
XN = MOD_LEFT + MOD_W - 0.3               # notch: no pour beside the ANT-side pads
RIGHT = [(ZX, 0), (BOARD_W, 0), (BOARD_W, ANT_Y0), (XN, ANT_Y0), (XN, ANT_Y1), (BOARD_W, ANT_Y1), (BOARD_W, BOARD_H), (ZX, BOARD_H)]
gnd_zone(pcbnew.F_Cu, RIGHT, "GND_F_right")
gnd_zone(pcbnew.B_Cu, RIGHT, "GND_B_right")
zb = gnd_zone(pcbnew.F_Cu, [(0, S3_BOT + 3.0), (ZX + 3.0, S3_BOT + 3.0), (ZX + 3.0, BOARD_H), (0, BOARD_H)], "GND_F_bottom")
zb.SetAssignedPriority(1)
zb = gnd_zone(pcbnew.B_Cu, [(0, S3_BOT + 2.4), (ZX + 3.0, S3_BOT + 2.4), (ZX + 3.0, BOARD_H), (0, BOARD_H)], "GND_B_bottom")
zb.SetAssignedPriority(1)

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


text("muhradio RX", 30.0, 2.2, pcbnew.F_SilkS, 1.0, bold=True)
text("S3Zero+CC1101 v1.0", 30.0, 4.0, pcbnew.F_SilkS, 0.8)
text("ANT", BOARD_W - 1.4, 14.8, pcbnew.F_SilkS, 0.8, rot=90)
text("USB-C", S3_POS[0] + S3_W / 2, 1.0, pcbnew.B_SilkS, 0.8, mirrored=True)
text("SCK9 MISO7 MOSI8 CS6 GDO0=2 GDO2=4", 22.0, 30.8, pcbnew.B_SilkS, 0.8, mirrored=True)

# ----------------------------------------------------------------------------
# Fill zones and save
# ----------------------------------------------------------------------------
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
board.BuildConnectivity()
board.Save(OUT)
print("wrote", OUT)

LIB = os.path.join(HERE, "s3zero_cc1101.pretty")
os.makedirs(LIB, exist_ok=True)
try:
    io = pcbnew.PCB_IO_KICAD_SEXPR()
    for fp in board.Footprints():
        copy = pcbnew.FOOTPRINT(fp)
        copy.SetPosition(VECTOR2I(0, 0))
        copy.SetOrientationDegrees(0)
        for p in copy.Pads():
            p.SetNet(pcbnew.NETINFO_ITEM(board, ""))
        io.FootprintSave(LIB, copy)
    print("footprints saved to", LIB)
except Exception as e:
    print("footprint export skipped:", e)
