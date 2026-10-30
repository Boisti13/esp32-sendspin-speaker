# Custom PCB — Rev A (in design)

A battery-powered board set for the Sendspin speaker, replacing the
ESP32-Audio-Kit. It keeps the Audio Kit's pins wherever it can, so the
firmware carries over as `speaker-diy.yaml` with only the display, battery
and LED parts changed. KiCad 10 projects; the hardware is licensed under
CERN-OHL-P-2.0 ([LICENSE](LICENSE)), the firmware in the repo root under MIT.

> Status: projects created, schematics not started. Nothing here has been
> built or tested yet.

## Highlights

- **Three boards**: the main board with module, audio and power; a front
  panel with the OLED and the five buttons; a small USB-C board. Everything
  that sits in the enclosure wall — panel, USB-C, battery, speakers,
  status LED — connects by JST cable, so the main board can go anywhere in
  the case.
- **USB-C either way**: on the main board directly, or on the USB-C board
  through a cable. Both footprints are on the main board; fit one.
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
- **0805 wherever possible** for resistors, capacitors and LEDs, so
  everything can be hand-soldered and reworked.

## Boards

| Board | KiCad project | Carries |
|---|---|---|
| Main | [`main/`](main/) | ESP32-A1S, amps, charger and protection, regulators, CH340C, Boot/Reset, on/off switch, headphone jack, all connectors below |
| Front panel | [`ui/`](ui/) | OLED header (SSD1306/SH1106), buttons 1, 3, 4, 5, 6 |
| USB-C | [`usb/`](usb/) | USB-C receptacle, CC resistors, USBLC6-2SC6 |

## Connectors (main board)

JST XH (2.5 mm) unless noted. Pin 1 first.

| Ref | To | Pins | Signals |
|---|---|---|---|
| J_UI | front panel | XH 10 | 3V3, GND, SDA (33), SCL (32), BTN1 (36), BTN3 (19), BTN4 (23), BTN5 (18), BTN6 (5), LED (22) |
| J_USB | USB-C board | XH 4 | VBUS, D−, D+, GND |
| USB1 | — | USB-C 16-pin | the on-board option, in parallel with J_USB |
| J_BAT | LiPo cell | **PH 2.0, 2** | BAT+, BAT− |
| J_LED | status LED | XH 3 | VBAT_SW, LED (22), GND |
| J_SPK_L | left speaker | XH 2 | OUTP, OUTN |
| J_SPK_R | right speaker | XH 2 | OUTP, OUTN |

- **Speakers are bridged (BTL)**: neither wire is ground. Never tie a
  speaker wire to GND or share a return between the two speakers.
- **Battery on JST PH**, since that is what most LiPo cells come with —
  but cells differ in polarity: check before plugging in. Silkscreen
  `+`/`−` at the connector.
- **J_UI**: I²C pull-ups (4.7 kΩ) and GPIO36's 10 kΩ pull-up sit on the
  main board, so the panel only has the display header, buttons to GND and
  a 100 nF at the header. The codec shares the bus, so keep the cable short
  (≤ 20 cm) and the bus at 100–400 kHz. Small series resistors (~100 Ω) on
  the button lines are optional ESD protection. The LED pin is there so a
  panel can carry the status LED instead of J_LED.
- **J_USB / USB1**: the CC resistors and the USBLC6-2SC6 belong next to the
  receptacle, so both the main board (for USB1) and the USB-C board carry
  them. Fit either USB1 or J_USB, not both. The cable carries charge and
  load current (amps on battery through load sharing), so XH's 3 A per pin
  is plenty; keep it short (≤ 15 cm) for USB full speed.
- **J_LED**: a plain LED with its resistor on the main board can be wired
  straight to LED/GND; VBAT_SW is there for an SK6812-type LED (needs
  > 3.7 V, hence not 3V3). The on-board LED footprint stays as an option.

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
| Display | 4-pin header on the panel | SSD1306/SH1106 at 0x3C, codec at 0x10 |
| Battery sense | 2 × 100 kΩ + 100 nF | switched VBAT → GPIO34 |

Flashing over USB needs the slide switch on.

**Footprints**: resistors, capacitors and LEDs in **0805** wherever the part
exists in it. Exceptions: the 220–470 µF bulk capacitor (electrolytic or
polymer), and values that don't come in 0805 at the needed voltage (check
22 µF for ≥ 10 V rating and DC-bias derating).

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
main/sendspin-speaker-main.kicad_*   main board
ui/sendspin-speaker-ui.kicad_*       front panel
usb/sendspin-speaker-usb.kicad_*     USB-C board
*/sym-lib-table, */fp-lib-table      each project points at ../lib/ only
lib/sendspin-speaker.kicad_sym       shared project symbols
lib/sendspin-speaker.pretty/         shared project footprints
lib/3dmodels/                        STEP models
```

Libraries are shared by the three projects and kept in the repo, so they
open on any PC with KiCad 10. Only parts we draw ourselves or that come
with a compatible licence go in `lib/` (the repo is public).

## Manufacturing

Gerbers, BOM and pick-and-place files are generated per board revision and
attached to that revision's GitHub release (tag `hw-rev-a`, …), not
committed. The revision is also printed on the silkscreen. Connector pin
orders above are the contract between the boards: a change goes into both
schematics and this table in the same commit.
