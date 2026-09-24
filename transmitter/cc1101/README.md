# Arduino Pro Mini + CC1101 (11-pin, 868 MHz) carrier PCB

A 17.78 x 60 mm two-layer carrier (v1.5) that hard-wires an Arduino Pro Mini to the
common green 11-pin CC1101 868 MHz module (19.3 x 17 mm, castellated pads).
The Pro Mini sits on the top side, the CC1101 module on the bottom side at
the far end, so the board is exactly as wide as the Pro Mini and as long as
the two modules end to end.

See `docs/DESIGN.md` for the part research, the layout decision and the
assembly notes.

## Files

| File | What it is |
|------|------------|
| `promini_cc1101.kicad_pro` | KiCad 10 project (open this) |
| `promini_cc1101.kicad_pcb` | The board (DRC clean, ground pours filled) |
| `promini_cc1101.kicad_sch` | Schematic (ERC clean, matches the board) |
| `promini_cc1101.kicad_sym`, `promini_cc1101.pretty/` | Project symbol and footprint libraries |
| `fab/gerbers/` | Gerber + Excellon drill files for ordering |
| `fab/*.png`, `fab/*.svg`, `fab/*.pdf` | Previews and the schematic PDF |
| `fab/v1.0/` ... `fab/v1.4/` | Previous revisions |
| `docs/BOM.md` | Parts list with shop search links |
| `fab/drc_report.txt`, `fab/erc_report.txt` | KiCad check reports |
| `gen_board.py`, `gen_sch.py` | Scripts that regenerate the board and schematic with KiCad's Python API |

## Wiring

| Pro Mini | CC1101 |
|----------|--------|
| VCC (3.3 V) | VCC |
| GND | GND |
| D13 | SCLK |
| D12 | MISO |
| D11 | MOSI |
| D10 | CSN |
| D2 (INT0) | GDO0 |
| D3 | J1 only (GDO2 not connected) |

## Sensor header J1 (v1.1)

`RAW  VCC  D3  SCL  SDA  GND` in one 2.54 mm row on the top side, between
the Pro Mini and the module. Matches the muhradio transmitter pinout
(I2C on A4/A5, interrupt sensors and DS18B20 on D3). Optional R1 (4.7 k,
D3 pull-up for DS18B20) and C1 (10 uF) are 0805 parts on the top side.
A4/A5 holes are at the SparkFun positions; other clones: jumper A4/A5 to
J1 SDA/SCL.

## Antenna

Push an 86 mm solid wire (or the module's spring leg) through the plated ANT
hole at the far end of the board, through the module's castellation, and
solder once.

## Battery power (v1.3)

2 x AA or one LiFePO4 cell straight on VCC through J2 (JST PH) and Q1 (reverse-
polarity P-FET).
Remove the Pro Mini's power LED and regulator. Unplug the battery and use a
3.3 V FTDI adapter when programming. R2 (330 R) sits in series with D3;
C2 (100 nF, DNP) is a debounce cap for reed/button nodes only.

## Measuring sleep current (v1.5)

There is no on-board link any more. Put the meter in series with the battery
lead at J2 (a JST PH extension cable with one wire cut is handy). Read the
sleep current there; short the meter with a jumper or clip while the node
wakes and transmits, because a meter's uA range drops volts at 34 mA and
would brown the node out.

Use a **3.3 V / 8 MHz** Pro Mini. The CC1101 is rated 1.8-3.6 V and is not
5 V tolerant.

## Regenerating

```sh
python3 gen_board.py     # writes promini_cc1101.kicad_pcb and the .pretty library
python3 gen_sch.py       # writes promini_cc1101.kicad_sch and .kicad_sym
kicad-cli pcb drc --schematic-parity promini_cc1101.kicad_pcb
```
