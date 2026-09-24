# ESP32-S3-Zero + CC1101 receiver carrier: design note

Date: 2026-09-15, v1.0

## Purpose

A carrier for the muhradio **receiver** (gateway) in its CC1101 variant on
the Waveshare ESP32-S3-Zero. It is USB powered and always on, so the design
priorities differ from the transmitter carrier: receive sensitivity and
WiFi-noise isolation matter, battery life does not.

## Parts and geometry

| Part | Size | Pins |
|------|------|------|
| Waveshare ESP32-S3-Zero | 18.0 x 23.5 mm | 2 x 9 castellated holes, 2.54 mm pitch, rows 15.24 mm apart (1.38 mm in from each long edge), first hole 1.59 mm from the USB end. Left row (USB end first): 5V GND 3V3 GP1..GP6. Right row (USB end first): TX43 RX44 GP13..GP7. USB-C on one short end, 2.4 GHz chip antenna at the other end (left corner). Exposed pads on the underside (GP17/18/38..45, GP14..16). |
| CC1101 11-pin module | 19.3 x 17.0 mm | as on the transmitter carrier |

S3-Zero geometry from Waveshare's dimension drawing and the community
KiCad footprint (jtomka/kicad-esp32-s3-zero); pin functions from the
Waveshare pinout diagram.

## Layout decisions

- **Both modules on the top side, side by side.** The S3-Zero on the left
  with USB-C flush with the top board edge; the CC1101 to the right with its
  signal edge facing the S3-Zero's right (SPI) column and its ANT edge at the
  right board edge. That puts the 868 MHz antenna about 40 mm from the
  S3-Zero's 2.4 GHz antenna (bottom-left corner), at right angles to it.
- **S3-Zero pads** are ovals with the hole offset outward, so the pad
  reaches 0.4 mm past the S3-Zero edge: that is the fillet for castellation
  soldering, and the same 1.0 mm hole takes header pins.
- **No copper pour under the S3-Zero** on the top layer: its underside has
  exposed pads and holes. Pours start at the module's left edge and in a
  band below the S3-Zero. Signals from the S3-Zero's left column go around
  its bottom end, never under it.
- **Radio supply filter:** 3V3 from the S3-Zero -> FB1 (600 R @ 100 MHz
  ferrite) -> C1 10 uF + C2 100 nF -> module VCC. WiFi transmit bursts are
  the receiver's main noise source; this keeps them off the CC1101 rail.
- **GDO2 to GP4** as a spare interrupt/status line. The firmware ignores
  it today; it costs one trace.
- **ANT** is a plated 1.0 mm hole aligned with the module's ANT
  castellation, as on the transmitter carrier. An 86 mm wire is the
  quarter-wave antenna; keep it in line with the board's long axis.
- Two M2.5 mounting holes (top right, bottom middle).

## Routing summary

SCK is a straight top-layer trace. MISO steps around the MOSI pad on the top
layer. MOSI runs on the bottom layer to a via in the channel between the
modules. CSN goes down and around the S3-Zero's bottom end on the top layer.
GDO0 and GDO2 use the bottom layer around the S3-Zero's left and bottom
edges, then vias under the module into the inner ends of their pads.
3V3 runs up the left channel and along the top strip to FB1.

## Not included, on purpose

SMA connector (the wire antenna is enough for a gateway inside a plastic
box; an SMA edge connector can be added later at the ANT hole position),
5 V input header (USB-C does the job), status LED (the S3-Zero has an RGB
LED on GP21).
