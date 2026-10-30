# Custom PCB — Rev A (in design)

A battery-powered board for the Sendspin speaker, replacing the
ESP32-Audio-Kit. It keeps the Audio Kit's pins wherever it can, so the
firmware carries over as `speaker-diy.yaml` with only the display, battery
and LED parts changed. KiCad 10 project; the hardware is licensed under
CERN-OHL-P-2.0 ([LICENSE](LICENSE)), the firmware in the repo root under MIT.

> Status: project created, schematic not started. Nothing here has been
> built or tested yet.

## Highlights

- **ESP32-A1S (Ai-Thinker, ES8388 version)**, the same module as the Audio
  Kit, hand-soldered (JLC doesn't stock it). Antenna over the board edge or
  a cutout, no copper under it.
- **Stereo, 2 × 3 W**: two NS4150B in BTL into 4 Ω, powered straight from
  the battery, enabled together on GPIO21.
- **1S LiPo** with TP4056 charging (~500 mA, so any PC port works),
  DW01A + FS8205A protection, load sharing, red/green charge LEDs that the
  firmware can read too.
- **One USB-C port** for charging and flashing (CH340C with auto-reset).
- **On/off slide switch after the charger**: the battery still charges
  while the speaker is off.
- **I²C OLED** (SSD1306/SH1106 128 × 64) on the codec's bus, battery voltage
  on an ADC pin, a status LED, five buttons plus Boot and Reset.

## Parts

| Block | Part | Notes |
|---|---|---|
| Module | ESP32-A1S (ES8388) | 22 µF + 100 nF at the module |
| Amps | 2 × NS4150B | from VBAT, enable GPIO21; 10 µF + 100 nF each; 220–470 µF bulk on VBAT near the amps |
| Headphones (optional) | PJ-320D 3.5 mm | codec LOUT1/ROUT1, detect → GPIO39 |
| Charger | TP4056 | R_PROG 2.4 kΩ (~500 mA); CHRG/STDBY → red/green LEDs and GPIO13/GPIO14 |
| Protection | DW01A + FS8205A | |
| Load sharing | AO3401A + SS34 | |
| Power switch | MSK-12C02 | after charger and load sharing |
| 3.3 V | AP2112K-3.3 or TPS63802 | the buck-boost runs the cell down to 3.0 V |
| USB-C | 16-pin receptacle | 5.1 kΩ on CC1 and CC2 separately; A6/B6 and A7/B7 tied |
| ESD | USBLC6-2SC6 | on D+/D− |
| USB-UART | CH340C | own ME6211/XC6206 3.3 V from VBUS (no battery drain); V3 tied to VCC; TX/RX through 470 Ω |
| Auto-reset | 2 × S8050 or UMH3N | DTR/RTS → EN/GPIO0; EN 10 kΩ pull-up + 1 µF |
| Display | 4-pin header | SSD1306/SH1106 at 0x3C, codec at 0x10 |
| Battery sense | 2 × 100 kΩ + 100 nF | switched VBAT → GPIO34 |

Flashing over USB needs the slide switch on.

## Pin plan

| Function | GPIO | Same as Audio Kit? |
|---|---|---|
| I²C SDA / SCL (codec + OLED) | 33 / 32 | yes |
| I²S MCLK / LRCLK / BCLK / DOUT | 0 / 25 / 27 / 26 | yes |
| Codec data out (keep free) | 35 | yes |
| Amp enable | 21 | yes |
| Buttons 1 play/pause, 3 prev, 4 next, 5 vol −, 6 vol + | 36, 19, 23, 18, 5 | yes; 36 needs an external 10 kΩ pull-up |
| Headphone detect | 39 | yes; external 10 kΩ pull-up (input-only pin) |
| Status LED | 22 | new (was the screen's DC) |
| Battery ADC | 34 | new |
| CHRG / STDBY | 13 / 14 | new, internal pull-ups |
| UART (CH340C) | 1 / 3 | yes |
| Don't use | 12 (flash voltage strap), 16/17 (PSRAM), 35 | |

## Firmware changes (`speaker-diy.yaml`, later)

- ST7789/SPI screen → `ssd1306_i2c` on `bus_a`, monochrome UI; drop `spi:`.
- Battery `adc` on GPIO34 (12 dB, ×2); warn below 3.5 V with the LDO.
- Status LED on GPIO22.
- *Charging* / *Charged* binary sensors on GPIO13/14.

## Layout

```
sendspin-speaker.kicad_pro / .kicad_sch / .kicad_pcb   the KiCad 10 project
sym-lib-table, fp-lib-table                            point at lib/ only
lib/sendspin-speaker.kicad_sym                         project symbols
lib/sendspin-speaker.pretty/                           project footprints
lib/3dmodels/                                          STEP models
```

Libraries are project-local, so the project opens on any PC with KiCad 10.
Only parts we draw ourselves or that come with a compatible licence go in
`lib/` (the repo is public).

## Manufacturing

Gerbers, BOM and pick-and-place files are generated per board revision and
attached to that revision's GitHub release (tag `hw-rev-a`, …), not
committed. The revision is also printed on the silkscreen.
