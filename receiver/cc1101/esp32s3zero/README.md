# muhradio receiver carrier: ESP32-S3-Zero + CC1101 868 MHz

A 44.8 x 31 mm two-layer carrier that wires a Waveshare ESP32-S3-Zero to the
11-pin CC1101 868 MHz module exactly as the muhradio receiver firmware
expects (`receiver/platformio.ini`, env `esp32-s3-zero-cc1101` and
`esp32-s3-zero-bresser`). Both modules sit on the top side; the S3-Zero's
USB-C powers everything.

| S3-Zero | CC1101 | muhradio flag |
|---------|--------|---------------|
| GP9 | SCLK | `CC1101_SCK=9` |
| GP7 | MISO | `CC1101_MISO=7` |
| GP8 | MOSI | `CC1101_MOSI=8` |
| GP6 | CSN | `CC1101_SS=6` |
| GP2 | GDO0 | `CC1101_GDO0=2` |
| GP4 | GDO2 | spare, not used by the firmware |
| 3V3 | VCC via FB1 + C1/C2 | |
| GND | GND | |

## Files

| File | What it is |
|------|------------|
| `s3zero_cc1101.kicad_pro` / `.kicad_pcb` / `.kicad_sch` | KiCad 10 project |
| `s3zero_cc1101.kicad_sym`, `s3zero_cc1101.pretty/` | project libraries |
| `fab/gerbers/`, `fab/s3zero_cc1101_gerbers.zip` | fabrication files |
| `fab/*.png`, `fab/schematic.pdf` | previews |
| `gen_board.py`, `gen_sch.py` | regenerate everything with KiCad's Python API |
| `docs/DESIGN.md` | design decisions and part data |

## Assembly

1. Solder the CC1101 module onto its castellation pads (top side, right).
2. Solder the ESP32-S3-Zero onto its 18 pads, either flat via its castellations
   (the pads have a ledge outside the S3-Zero edge for the fillet) or on
   2.54 mm header pins.
3. FB1 (ferrite bead), C1 10 uF and C2 100 nF (all 0805) above the module.
4. Push an 86 mm solid wire through the plated ANT hole at the right edge and
   solder it; it goes through the module's ANT castellation too.
5. Two M2.5 mounting holes.

Flash with `pio run -e esp32-s3-zero-cc1101 -t upload` from the muhradio
receiver directory; no pin flags need changing.
