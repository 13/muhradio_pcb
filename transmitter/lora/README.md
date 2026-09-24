# Arduino Pro Mini + RFM95W (LoRa 868 MHz) carrier PCB

A 17.78 x 60 mm two-layer carrier (v1.1, LoRa) that hard-wires an Arduino Pro Mini to the
HopeRF RFM95W LoRa module (16 x 16 mm, 16 castellations) for the muhradio
LoRa transmitter nodes. Same board size, sensor header and battery circuit as
the CC1101 carrier in `../cc1101/`; only the radio and its wiring differ.

See `docs/DESIGN.md` for the part research, the layout decision and the
assembly notes.

## Files

| File | What it is |
|------|------------|
| `promini_rfm95w.kicad_pro` | KiCad 10 project (open this) |
| `promini_rfm95w.kicad_pcb` | The board (DRC clean, ground pours filled) |
| `promini_rfm95w.kicad_sch` | Schematic (ERC clean, matches the board) |
| `promini_rfm95w.kicad_sym`, `promini_rfm95w.pretty/` | Project symbol and footprint libraries |
| `fab/gerbers/` | Gerber + Excellon drill files for ordering |
| `fab/*.png`, `fab/*.svg`, `fab/*.pdf` | Previews and the schematic PDF |
| `fab/v1.0/` | Previous revision (with the JP1 link) |
| `docs/BOM.md` | Parts list (differences from the CC1101 board) |
| `fab/drc_report.txt`, `fab/erc_report.txt` | KiCad check reports |
| `gen_board.py`, `gen_sch.py` | Scripts that regenerate the board and schematic with KiCad's Python API |

## Wiring

| Pro Mini | RFM95W | muhradio |
|----------|--------|----------|
| VCC (3.3 V) | 3.3V | |
| GND | GND | |
| D13 | SCK | |
| D12 | MISO | |
| D11 | MOSI | |
| D10 | NSS | |
| D9 | RESET | |
| D2 (INT0) | DIO0 | TX-done interrupt |
| D3 | J1 only | sensors |

DIO1..DIO5 are left unconnected (muhradio does not use them).

## Sensor header J1

`RAW  VCC  D3  SCL  SDA  GND` in one 2.54 mm row on the top side, between
the Pro Mini and the module. Matches the muhradio transmitter pinout
(I2C on A4/A5, interrupt sensors and DS18B20 on D3). Optional R1 (4.7 k,
D3 pull-up for DS18B20) and C1 (10 uF) are 0805 parts on the top side.
A4/A5 holes are at the SparkFun positions; other clones: jumper A4/A5 to
J1 SDA/SCL.

## Antenna

The RFM95W's ANT castellation (corner of the far edge) is a plated 1.0 mm
hole on the carrier: push an 86 mm solid wire through it and the castellation
and solder once.

## Battery power

2 x AA or one LiFePO4 cell straight on VCC through J2 (JST PH) and Q1 (reverse-
polarity P-FET).
Remove the Pro Mini's power LED and regulator. Unplug the battery and use a
3.3 V FTDI adapter when programming. R2 (330 R) sits in series with D3;
C2 (100 nF, DNP) is a debounce cap for reed/button nodes only.

## Measuring sleep current

There is no on-board link any more. Put the meter in series with the battery
lead at J2 (a JST PH extension cable with one wire cut is handy). Read the
sleep current there; short the meter with a jumper or clip while the node
wakes and transmits, because a meter's uA range drops volts at the 120 mA LoRa TX burst
and would brown the node out.

Use a **3.3 V / 8 MHz** Pro Mini. The CC1101 is rated 1.8-3.6 V and is not
5 V tolerant.

## Regenerating

```sh
python3 gen_board.py     # writes promini_rfm95w.kicad_pcb and the .pretty library
python3 gen_sch.py       # writes promini_rfm95w.kicad_sch and .kicad_sym
kicad-cli pcb drc --schematic-parity promini_rfm95w.kicad_pcb
```
