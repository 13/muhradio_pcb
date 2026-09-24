# Pro Mini + RFM95W (LoRa) carrier: design note

Date: 2026-09-15, v1.0; 2026-09-24, v1.1 (JP1 current link removed, as in the CC1101 carrier v1.5). Derived from the CC1101 carrier (`../../cc1101/docs/DESIGN.md`),
which documents the Pro Mini geometry, the sensor header J1, the battery
circuit (J2, Q1, C1), the D3 parts (R1, R2, C2) and the reasoning behind
them. Only the radio differs here.

## Radio

HopeRF RFM95W (SX1276), 16 x 16 mm, 16 castellations at 2.0 mm pitch. Land
pattern per KiCad's `RF_Module:HOPERF_RFM9XW_SMD` (pads 2.0 x 1.0 mm centred
on the module edge). Pins 1-8 down one edge: ANT GND DIO3 DIO4 3.3V DIO0 DIO1
DIO2; pins 9-16 up the other: GND DIO5 RESET NSS SCK MOSI MISO GND.

The module sits on the bottom side with its SPI edge facing the Pro Mini
(top view, left to right: GND DIO5 RESET NSS SCK MOSI MISO GND) and the
other edge at the far end (DIO2 DIO1 DIO0 3V3 DIO4 DIO3 GND ANT). That puts
RESET next to D9, the SPI pads under D10-D13, and the ANT corner at the far
right, where its castellation pad is a plated 1.0 mm hole for the wire antenna.

## Wiring (muhradio docs/PINOUTS.md, Pro Mini -> RFM95W)

| Pro Mini | RFM95W | route |
|----------|--------|-------|
| D13 | SCK | top layer, gap between J1 pins 3/4, via, pad |
| D12 | MISO | top layer, gap 4/5, via, pad |
| D11 | MOSI | top layer, gap 5/6, via, pad |
| D10 | NSS | bottom layer lane above J1, gap 3/4, pad |
| D9 | RESET | top layer lane above J1, gap 2/3, via, pad |
| D2 | DIO0 | top layer: right channel, right board edge, far row via |
| VCC | 3.3V | top layer from the Q1 source node down the left edge, far row via |

The sensor-side D3 net now reaches J1 on the bottom layer (via at the end of
the left channel) to free the top-layer lane for RESET.

## Board

17.78 x 60 mm, same as the CC1101 carrier. RFM95W is rated 1.8-3.7 V; the
same no-regulator caveat for Li-ion applies as on the CC1101 board.
