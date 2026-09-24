# Parts list: receiver carrier (ESP32-S3-Zero + CC1101)

Links are search pages, not vetted listings.

| Ref | Qty | Part | Package | What to check | Amazon.it | AliExpress |
|-----|-----|------|---------|---------------|-----------|------------|
| PCB | 1 | This carrier, 2 layers, 1.6 mm, 44.8 x 32 mm | – | Upload `fab/s3zero_cc1101_gerbers.zip` to JLCPCB / PCBWay | – | – |
| U1 | 1 | Waveshare ESP32-S3-Zero | module | Must be the Waveshare "Zero" (18 x 23.5 mm, 2x9 castellated). Not the Super Mini | [search](https://www.amazon.it/s?k=waveshare+esp32-s3-zero) | [search](https://www.aliexpress.com/w/wholesale-waveshare-esp32-s3-zero.html) |
| U2 | 1 | CC1101 868 MHz module, 11 pin | castellated | Same module as the transmitter | [search](https://www.amazon.it/s?k=cc1101+868mhz+modulo) | [search](https://www.aliexpress.com/w/wholesale-cc1101-868mhz-11pin.html) |
| FB1 | 1 | Ferrite bead 600 R @ 100 MHz, >= 0.5 A | 0805 | e.g. BLM21PG601SN1 | [search](https://www.amazon.it/s?k=0805+ferrite+bead+600r) | [search](https://www.aliexpress.com/w/wholesale-0805-ferrite-bead-600r.html) |
| C1 | 1 | 10 uF X5R 10 V | 0805 | | [search](https://www.amazon.it/s?k=0805+10uf+x5r) | [search](https://www.aliexpress.com/w/wholesale-0805-10uf-x5r.html) |
| C2 | 1 | 100 nF X7R | 0805 | | [search](https://www.amazon.it/s?k=0805+capacitor+kit) | [search](https://www.aliexpress.com/w/wholesale-0805-capacitor-kit.html) |
| ANT | 1 | 86 mm solid wire | – | Through the plated ANT hole | – | – |
| – | opt | 2 x 9-pin 2.54 mm header (if not soldering the S3-Zero flat) | THT | | [search](https://www.amazon.it/s?k=pin+header+2.54mm+male) | [search](https://www.aliexpress.com/w/wholesale-2.54mm-pin-header-male-40pin.html) |
| – | 2 | M2.5 screws / standoffs | – | Mounting holes are 2.7 mm | – | – |

Power: the S3-Zero's USB-C (5 V). No other supply parts are needed.
