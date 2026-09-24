# muhradio hardware carriers

KiCad 10 carrier boards for the [muhradio](https://github.com/13/muhradio)
sensor network, generated from Python scripts with KiCad's `pcbnew` API.

| Folder | Board | Role |
|--------|-------|------|
| `transmitter/cc1101/` | Arduino Pro Mini 3.3 V + CC1101 868 MHz, sensor header, battery direct on VCC | battery-powered sensor node (muhradio transmitter, CC1101) |
| `transmitter/lora/` | same carrier with a HopeRF RFM95W LoRa module (D9 RST, D2 DIO0) | battery-powered sensor node (muhradio transmitter, LoRa) |
| `receiver/cc1101/esp32s3zero/` | Waveshare ESP32-S3-Zero + CC1101 868 MHz, filtered radio supply | USB-powered gateway (muhradio receiver, env `esp32-s3-zero-cc1101`) |

Each folder has its own README, `docs/DESIGN.md`, `docs/BOM.md`, the KiCad
project and `fab/` with Gerbers and previews. Regenerate a board with
`python3 gen_board.py && python3 gen_sch.py` inside its folder, then verify
with `kicad-cli pcb drc --schematic-parity <board>.kicad_pcb`.
