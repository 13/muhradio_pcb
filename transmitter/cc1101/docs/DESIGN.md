# Pro Mini + CC1101 (11-pin, 868 MHz) carrier board — design note

Date: 2026-09-14, revised 2026-09-15 (v1.1 sensor header, v1.2/v1.3 battery power, v1.4 antenna hole), 2026-09-24 (v1.5 JP1 removed)

## Goal

A minimal two-layer carrier PCB that hard-wires an Arduino Pro Mini to the
common 11-pin CC1101 868 MHz module (green 19.3 x 17 mm module with
castellated half-hole pads: VCC GND MOSI SCLK MISO GDO2 GDO0 CSN on one
edge, GND ANT GND on the opposite edge). The PCB footprint must not exceed
the combined footprint of the two modules.

## Parts (as researched)

| Part | Size | Pins |
|------|------|------|
| Arduino Pro Mini (SparkFun v14 geometry, clones identical) | 17.78 x 33.02 mm | 2 x 12 side pins at 2.54 mm pitch, rows 15.24 mm apart, first pin 1.27 mm from each edge; 6-pin FTDI row on one end |
| CC1101 11-pin module | 19.3 x 17.0 mm | 8 signal castellations at 2.0 mm pitch on one 17 mm edge (centred); GND/ANT/GND at 2.54 mm pitch on the opposite edge, ANT offset about 1 mm toward the CSN end |

Pro Mini coordinates were taken from SparkFun's Eagle board file
(`Arduino-Pro-Mini.brd`). Module dimensions come from vendor listings
(androegg.de: 11 pins, 2 mm pitch; vipitec.de: 19.3 x 17 x 5.3 mm) and
were cross-checked by measuring product photos. The ANT-side pads are
drawn 1.6 mm wide to absorb roughly +/-0.4 mm of uncertainty.

## Layout decision

Two layouts were considered:

1. **Stacked** (module under the Pro Mini). Rejected: the module is 19.3 mm
   wide, wider than the Pro Mini, and the Pro Mini's 24 header pins poke
   through the carrier exactly where the module body must sit. It only
   works if every pin is clipped flush, and the module would then rest on
   solder bumps.
2. **Full length** (module beyond the D10 end of the Pro Mini). Chosen.
   The module goes on the **bottom** side of the carrier so that its pin
   order, seen from the top, matches the Pro Mini's SPI pin order. This
   makes the routing nearly crossing-free and keeps the board only as wide
   as the Pro Mini.

Resulting board: **17.78 x 60.0 mm** (v1.1 onward; v1.0 was 56 mm), two layers,
ground pour on both sides.

## Connections

| Pro Mini | CC1101 module | Note |
|----------|---------------|------|
| VCC (3.3 V) | VCC | module is 1.8-3.6 V, **use a 3.3 V/8 MHz Pro Mini** |
| GND | GND (x4) | via ground pour |
| D13 / SCK | SCLK | |
| D12 / MISO | MISO (SO) | |
| D11 / MOSI | MOSI (SI) | |
| D10 / SS | CSN | |
| D2 / INT0 | GDO0 | packet interrupt (muhradio TX-done) |
| D3 | (not connected to the module) | free for sensors, see J1 |

GDO2 is deliberately left unconnected (v1.1). The muhradio firmware puts its
DS18B20 / button / switch / PIR / radar sensors on D3, and GDO2 is a driven
output of the CC1101, so wiring them together would fight.

## v1.1: sensor header J1

A 1x6 through-hole row (2.54 mm) on the top side between the Pro Mini and
the module, so every muhradio sensor type has one place to solder to:

| J1 pin | Signal | Source |
|--------|--------|--------|
| 1 (square) | RAW | Pro Mini RAW (battery in) |
| 2 | VCC | Pro Mini 3.3 V |
| 3 | D3 | interrupt sensors, DS18B20 |
| 4 | SCL | Pro Mini A5 (inner pin) |
| 5 | SDA | Pro Mini A4 (inner pin) |
| 6 | GND | |

The carrier has holes for A4/A5 at the SparkFun positions (inner row next
to the A2/A3 side). Clones that place A4/A5 elsewhere: leave those holes
empty and run two short wires from the Pro Mini's A4/A5 to J1 SDA/SCL.

Optional parts, both 0805, populate only when needed:

- C1 10 uF across VCC/GND next to the module (TX current bursts).
- R1 4.7 k from D3 to VCC: the DS18B20 1-Wire pull-up. Leave off for
  button/PIR/radar nodes.

Ground: the Pro Mini interior pour and the module-area pour are separate
zones (the header strip between them carries no copper fill); they are
bridged through the J1 GND pin on both layers plus stitching vias.

## v1.2/v1.3: battery power for a years-long, near-zero-sleep node

The muhradio transmitter sleeps with BOD and ADC off, puts the CC1101 into
SPWD (~0.2 uA) and reports VCC measured against the internal bandgap, with a
low-battery flag below 2.7 V. That only makes sense when the battery sits
directly on VCC, so the board puts the **battery straight on VCC with no
regulator in the path**. The user runs 1S LiPo (102050, 1000 mAh) and
NCR18650B cells this way and reports it working; note that a full Li-ion
cell is 4.2 V while the CC1101 is rated to 3.6 V (3.9 V absolute maximum),
so the radio runs above its rating until the cell drops below ~3.6 V. An LDO
was considered and rejected by the user (v1.3). 2 x AA / LiFePO4 work the
same way and stay in spec.

Silkscreen next to J2 carries a large + and - beside the two pads, placed
left of the connector body so they stay visible once it is soldered.
Capacitors draw nothing in sleep: all of them are ceramic, whose leakage is
in the nanoamp range.

Power path, all top side over the module area:

| Part | Function |
|------|----------|
| J2 (JST PH 2-pin, side-entry SMD) | battery in (+ upper pad, - lower pad), cable exits over the right edge; the pads are big enough for bare wires |
| Q1 (AO3401A / DMG2305UX, SOT-23) | reverse-polarity guard on the high side; zero quiescent current, a few mV drop |
| ~~JP1~~ | v1.2-v1.4 had a cuttable solder link in series with VCC for current measurement; removed in v1.5, see below |
| C1 22 uF 0805 | bulk for the 34 mA TX bursts; alkaline cells have real internal resistance |

Sensor-side protection on D3 (under the Pro Mini):

| Part | Function |
|------|----------|
| R2 330 R | series resistor between the MCU pin and the J1 D3 pin; limits ESD/short current from the one wire that leaves the box |
| C2 100 nF (DNP) | debounce for reed switches and buttons; leave OFF for DS18B20, it would break the 1-Wire timing |
| R1 4.7 k (DNP) | DS18B20 pull-up on the sensor side |

Expected currents: sleep is the Pro Mini's own ~4-6 uA with the watchdog
running (~0.3 uA for interrupt-only nodes) plus ~0.2 uA for the radio, once
the Pro Mini's power LED and regulator are removed. A 60 s Si7021 node
averages roughly 30-50 uA, dominated by the wake/TX burst, so 2 x AA lasts
years; interrupt-only nodes are limited by cell shelf life.

Things that are deliberately not on the board: a switched sensor rail
(PIR/radar modules need 5 V and milliamps, they do not belong on a 2 x AA
node), an LDO (Li-ion would need one and would lose the VCC telemetry), and
mounting holes (the only free end is the antenna end).

Assembly cautions for v1.2:

- Remove the Pro Mini's power LED and, ideally, its regulator. Leave RAW
  unconnected.
- Unplug the battery before connecting an FTDI adapter, and set the adapter
  to 3.3 V. 5 V on VCC destroys the CC1101.
- Use protected Li-ion cells (or a 1S PCM on bare NCR18650B): the node keeps
  running with BOD off and will over-discharge an unprotected cell.
- The J2 land pattern follows the JST ePH drawing (contacts 1.0 x 3.5 mm at
  2.0 mm pitch; tab pads 1.5 x 3.4 mm, 6.7 mm apart, 5.75 mm behind the
  contact centres), verified against KiCad's official
  JST_PH_S2B-PH-SM4-TB footprint on 2026-09-15.

## v1.4: antenna hole

The carrier's ANT pad (the one that meets the module's ANT castellation) is a
plated 1.0 mm hole with a 2.0 x 1.8 mm oval ring, centred on the module's
edge line so it lines up with the castellation half-hole. An 86 mm solid wire
(quarter wave at 868 MHz) or the spring antenna's leg goes through carrier
and castellation together and is soldered once; that joint has real strain
relief, which a wire tacked onto the castellation alone does not. The board
length stays 60 mm; the ring sits exactly at the 0.3 mm copper-to-edge
clearance. The wire should leave the board in line with its long axis, away
from the battery. See `docs/BOM.md` for the full parts list.

## v1.5: JP1 removed

The cuttable current-measurement link was redundant: the battery already
enters through a plug, so an ammeter goes in series with the JST cable at J2
and reads the same thing. Removing it takes one solder-and-cut step out of
every board and one 0.3 mm neck out of the VCC path. Q1's source now runs
straight to C1. Nothing else changed; the board stays 17.78 x 60 mm.

Measurement note that was equally true with JP1: a DMM's uA range has a
shunt of hundreds of ohms, so the 34 mA TX burst would drop volts across it
and brown the node out. Short the meter with a jumper while the node is
awake, or use a burden-free instrument, and read the sleep value between
transmissions.

A review of the muhradio firmware on 2026-09-24 confirmed the board is at
its floor: timed nodes sleep at roughly 5 uA (ATmega watchdog 4.5 uA, radio
in SPWD 0.2 uA), interrupt nodes below 0.5 uA, both under the self-discharge
of any battery this board takes. The remaining consumer is firmware: the
BME680 gas heater (320 C for 150 ms per reading, about 2 mAs). No further
hardware changes are planned for battery life.

## Assembly

- Solder the Pro Mini on the top side with straight male headers (or
  female sockets). Its pins are soldered on the bottom side, in the
  region that stays clear of the module.
- Solder the CC1101 module on the bottom side, at the far end, onto the
  castellated pads. Silkscreen on the bottom shows the outline and pin
  names. The antenna solders to the ANT castellation and points off the
  end of the board.
- The carrier has plated but unconnected holes for the Pro Mini's 6-pin
  FTDI row, so a straight or right-angle programming header both fit.
- A6/A7 are not broken out. A4/A5 are (SparkFun positions), see J1 above.
- Sensors: solder a 6-pin header, wires or a JST cable to J1.

## Files

- `promini_cc1101.kicad_pro` / `.kicad_pcb` / `.kicad_sch` — KiCad 10 project
- `gen_board.py` — script that regenerates the PCB from the numbers above
  using KiCad's `pcbnew` Python API
- `fab/` — Gerber/drill files, and preview renders
