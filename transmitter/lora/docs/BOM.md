# Parts list: LoRa carrier (differences from the CC1101 board)

The links are **search pages**, not vetted listings: sellers and stock change
weekly. Each row says what to check in the listing before buying.

## Per board

| Ref | Qty | Part | Package | What to check | Amazon.it | AliExpress |
|-----|-----|------|---------|---------------|-----------|------------|
| PCB | 1 | This carrier, 2 layers, 1.6 mm, 17.78 x 60 mm | – | Upload `fab/promini_rfm95w_gerbers.zip`; defaults (HASL, green, 1.6 mm) are fine. 5 pcs ~2 EUR + shipping | – | [JLCPCB](https://jlcpcb.com) / [PCBWay](https://www.pcbway.com) |
| A1 | 1 | Arduino Pro Mini, ATmega328P, **3.3 V / 8 MHz** | module | Must say 3.3 V 8 MHz (not 5 V 16 MHz). Comes with header pins | [search](https://www.amazon.it/s?k=arduino+pro+mini+3.3v+8mhz+atmega328p) | [search](https://www.aliexpress.com/w/wholesale-pro-mini-3.3v-8mhz-atmega328p.html) |
| U1 | 1 | HopeRF **RFM95W-868S2** LoRa module (SX1276, 868 MHz) | castellated 16 x 16 mm | Must be RFM95W (868/915 MHz version), not RFM98W (433). Genuine HopeRF or a known clone | [search](https://www.amazon.it/s?k=rfm95w+868mhz) | [search](https://www.aliexpress.com/w/wholesale-rfm95w-868mhz.html) |
| ANT | 1 | Antenna: 86 mm solid wire (quarter wave), or the module's 868 MHz spring | – | 0.5-0.8 mm solid core wire cut to 86 mm, pushed through the plated ANT hole (it lines up with the RFM95W's ANT corner castellation) and soldered once | – | – |
| J1 | 1 | Pin header 1x6, 2.54 mm, straight or right-angle | THT | Or solder sensor wires straight into the holes | [search](https://www.amazon.it/s?k=pin+header+2.54mm+male) | [search](https://www.aliexpress.com/w/wholesale-2.54mm-pin-header-male-40pin.html) |
| J2 | 1 | JST PH 2.0 mm, 2 pin, **side entry SMD**, S2B-PH-SM4-TB | SMD | Part number S2B-PH-SM4-TB (side/horizontal). Not B2B (vertical), not the through-hole S2B-PH-K | [search](https://www.amazon.it/s?k=jst+ph+2.0+smd+horizontal+2+pin) | [search](https://www.aliexpress.com/w/wholesale-S2B-PH-SM4-TB.html) |
| Q1 | 1 | AO3401A P-channel MOSFET (or DMG2305UX) | SOT-23 | Any P-FET with Vgs(th) < 1 V works; AO3401A is the cheap standard | [search](https://www.amazon.it/s?k=ao3401a+sot-23) | [search](https://www.aliexpress.com/w/wholesale-AO3401A-sot-23.html) |
| C1 | 1 | 22 uF ceramic, X5R/X7R, **10 V** | 0805 | 10 V rating for LiPo (4.2 V) plus DC-bias derating; 6.3 V is marginal | [search](https://www.amazon.it/s?k=0805+22uf+10v+x5r) | [search](https://www.aliexpress.com/w/wholesale-0805-22uf-10v-x5r.html) |
| R2 | 1 | 330 R | 0805 | Series protection on D3. Use 0 R if you prefer | [search](https://www.amazon.it/s?k=0805+resistor+kit) | [search](https://www.aliexpress.com/w/wholesale-0805-resistor-kit.html) |
| R1 | 0-1 | 4.7 k | 0805 | **DS18B20 nodes only** (1-Wire pull-up) | same kit | same kit |
| C2 | 0-1 | 100 nF ceramic | 0805 | **Reed switch / button nodes only** (debounce). Never with DS18B20 | [search](https://www.amazon.it/s?k=0805+capacitor+kit) | [search](https://www.aliexpress.com/w/wholesale-0805-capacitor-kit.html) |

A resistor + capacitor 0805 sample book covers R1, R2, C2 for many boards.

## Power

| Qty | Part | What to check | Amazon.it | AliExpress |
|-----|------|---------------|-----------|------------|
| 1 | LiPo 102050 1000 mAh **with protection (PCM) and JST-PH 2.0 plug** | Listing must say "with protection board". **Check plug polarity against the + mark on J2**: Chinese LiPo plugs are wired both ways. Q1 protects against a swap, but the node will not run until fixed | [search](https://www.amazon.it/s?k=lipo+102050+1000mah+jst+ph+2.0) | [search](https://www.aliexpress.com/w/wholesale-102050-1000mah-lipo-jst-ph.html) |
| or 1 | NCR18650B **protected** + 18650 holder with leads, or a bare cell + 1S protection board (DW01) | Bare NCR18650B has no protection; the node will over-discharge it | [search](https://www.amazon.it/s?k=18650+holder+with+wire+leads) | [search](https://www.aliexpress.com/w/wholesale-1s-18650-protection-board-dw01.html) |
| 1 | JST PH 2.0 2-pin cable (if the cell has bare leads) | 2.0 mm pitch, 2 pin | [search](https://www.amazon.it/s?k=jst+ph+2.0+2+pin+cable) | [search](https://www.aliexpress.com/w/wholesale-jst-ph-2.0-2pin-cable.html) |
| opt | TP4056 charger module with protection | Charge the cell off-board; unplug it from the node while charging | [search](https://www.amazon.it/s?k=tp4056+type+c) | [search](https://www.aliexpress.com/w/wholesale-tp4056-type-c.html) |

## Sensors (per muhradio node type, connect to J1)

| Node | Part | J1 pins | Amazon.it | AliExpress |
|------|------|---------|-----------|------------|
| Temp/humidity | Si7021 breakout (GY-21) or BME280/BMP280 3.3 V | VCC GND SDA SCL | [search](https://www.amazon.it/s?k=si7021+gy-21) | [search](https://www.aliexpress.com/w/wholesale-si7021-gy-21.html) |
| Temp probe | DS18B20 waterproof probe | VCC GND D3 (+R1) | [search](https://www.amazon.it/s?k=ds18b20+waterproof) | [search](https://www.aliexpress.com/w/wholesale-ds18b20-waterproof.html) |
| Door/window | Reed switch, normally open | D3 GND (+C2) | [search](https://www.amazon.it/s?k=reed+switch+magnetic+door+sensor) | [search](https://www.aliexpress.com/w/wholesale-reed-switch-door-sensor.html) |
| Button | Tactile push button | D3 GND (+C2) | [search](https://www.amazon.it/s?k=tactile+push+button) | [search](https://www.aliexpress.com/w/wholesale-tactile-push-button.html) |

PIR (HC-SR501) and radar (RCWL-0516) modules need 5 V and milliamps; they
do not belong on this battery node.

## Tools you need once

| Part | Note | Amazon.it | AliExpress |
|------|------|-----------|------------|
| FTDI USB-serial adapter, **3.3 V switchable** | Set the jumper to 3.3 V. Unplug the battery while programming | [search](https://www.amazon.it/s?k=ftdi+ft232rl+3.3v+5v) | [search](https://www.aliexpress.com/w/wholesale-ft232rl-3.3v-5v-adapter.html) |
| Multimeter with a uA range | To verify sleep current: meter in series with the battery lead at J2, shorted with a clip while the node transmits | – | – |
