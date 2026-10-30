# Changelog

## Unreleased

### Under the hood

- `hardware/`: empty KiCad 10 project for a custom battery-powered PCB
  (Rev A), with project-local libraries, the parts list and pin plan in
  `hardware/README.md`, and CERN-OHL-P-2.0 for the hardware.
- `hardware/` split into three boards — main (`main/`), front panel with
  OLED and buttons (`ui/`), USB-C (`usb/`) — with a JST connector plan for
  the panel, USB-C (or USB-C on the main board), LiPo, speakers and
  status LED. SMD passives and LEDs in 0805 wherever possible.
- Main board block diagram: hierarchical sheets USB, Power, MCU, Audio
  and Connectors with their signals, each sheet listing what goes in it.
- Footprints for every part (`hardware/README.md`): KiCad's libraries,
  plus ESP32-A1S, NS4150B, FS8205A, MSK12C02 and PJ-320D imported from LCSC
  into `hardware/lib/lcsc` (A1S with an antenna keepout).
- Pin plan reworked to the A1S's real pads (the codec's I²C/I²S are inside
  the module): display on the ST7789's pins 14/13/15/22, SPI or I²C;
  status LED on 12, CHRG/STDBY on 4/2 through diodes. On/off switch and
  charge LEDs can go off-board (J_SW, J_CHG).
- MCU sheet drawn: ESP32-A1S with all pads wired (unused mic/line-in pads
  marked), 22 µF + 100 nF, EN 10k/1 µF with Reset, Boot, pull-ups on
  GPIO36/39 and display CS, optional I²C pull-ups (not fitted), status LED
  on GPIO12 with its strap pull-down. The A1S symbol got real pin types.
  Draft generator in `hardware/scripts/`.
- Power sheet drawn: TP4056 (2.4k, ~500 mA) with on-board or J_CHG charge
  LEDs and BAT54W read-back to GPIO4/2, J_BAT + DW01A/FS8205A, load
  sharing (SS34, AO3401A), MSK12C02 / J_SW / solder-jumper bypass,
  AP2112K-3.3, battery divider on the cell (2 × 470k: on VBAT_SW it would
  read USB's 4.6 V while charging).
- Power sheet tidied: part texts placed where each symbol expects them,
  crowded labels and rail symbols moved apart (netlist unchanged).
- USB sheet: USB-C (or J_USB) with CC resistors and USBLC6-2SC6, CH340C on
  its own XC6206 3.3 V, TX/RX 470 Ω, UMH3N auto-reset. CH340C symbol copy
  with V3 as power input (tied to VCC).
- Audio sheet: 2 × NS4150B with 100n/100k inputs, bypass, supply caps,
  470 µF bulk, AMP_EN pull-down, speaker connectors, PJ-320D on 47 µF.
- Connectors sheet: J_UI (XH 12) and J_LED (through 330 Ω).
- Front panel and USB-C board schematics. ERC clean on all three projects.
- KiCad 10's local history folder (`.history/`) is ignored.

## v0.7.0 — 2026-10-29

### Changed

- The chime plays when Wi-Fi first connects after boot instead of at
  power-on, so it also says "online". Not on later reconnects, and not
  while something plays.
- Button 1: when nothing is playing it sends Sendspin's *play* to Music
  Assistant, which resumes the speaker's queue with the last track. Before,
  it did nothing after boot (the player had nothing loaded) and replayed
  the chime in v0.6.0.

## v0.6.1 — 2026-10-29

### Fixed

- Play/pause with no music played since boot replayed the boot chime (it
  stayed in the player's playlist). The player is stopped once the chime
  has ended, which empties the playlist; play/pause then does nothing until
  music has played, as before v0.6.0.

## v0.6.0 — 2026-10-29

### Added

- Boot chime: three rising notes at power-on, played through the player
  from a file built into the firmware (`sounds/boot.wav`, made by
  `scripts/make-boot-sound.py`). Switch *Boot Sound* (config, on by
  default, remembered) turns it off.
- `sounds/` must now be next to `speaker.yaml` in the ESPHome folder.

## v0.5.0 — 2026-10-27

### Added

- Diagnostic sensors: *Wi-Fi Signal*, *Uptime*, *Free PSRAM*, *Free Heap*.

### Fixed

- Music stopped after a Wi-Fi stall of ~25 s: the Sendspin buffer (1 MB by
  default) ran dry. It is 2.5 MB now. Much longer gaps still stop the
  music; the signal sensor shows whether the Wi-Fi is the cause.

## v0.4.0 — 2026-10-27

### Changed

- New button layout: 1 play/pause, 3 previous track, 4 next track,
  5 volume down, 6 volume up. The entities are renamed to match
  (*Button 1 Play/Pause* …), so their entity IDs change again.

## v0.3.0 — 2026-10-27

### Changed

- The buttons are named after what they do: *Button 1 Previous Track*,
  *Button 3 Next Track*, *Button 4 Volume Down*, *Button 5 Volume Up*,
  *Button 6 Play/Pause* (were *Key 1* … *Key 6*). **New entity IDs**
  (`binary_sensor.speaker_1_button_1_previous_track` …): the old
  `binary_sensor.speaker_1_key_*` entities stay behind unavailable and can
  be removed.

### Under the hood

- `CLAUDE.md`: Home Assistant now has the v0.2.0 copy and the OTA secret.

## v0.2.0 — 2026-10-27

Needs ESPHome 2026.10 or later.

### Changed

- Uses the Sendspin, `speaker_source` and `media_source` components built
  into ESPHome 2026.10 instead of pull-request copies (v0.1.0 no longer
  validated). The player's speaker and source moved into `media_pipeline:`;
  `kalman_process_error` is gone (the built-in Sendspin has no such option).
- Previous, next and play/pause keys go straight to the player, which
  passes them on to Music Assistant through Sendspin: they work without
  Home Assistant, and the device no longer needs Home Assistant actions.
- Log level INFO instead of DEBUG.

### Fixed

- The DAC output wasn't set to *BOTH* at boot: the Home Assistant call ran
  before the API was connected. It is set on the device now.
- Previous/next called `media_player.speaker_1`, an entity that doesn't
  exist.
- Every volume change while playing restarted the start-up sequence
  (amplifier on, two seconds without redraws): `on_state` also fires on
  volume changes. Only real starts and stops count now.
- The amplifier switched off immediately when playback stopped or paused,
  clipping the last audio with a click; it now waits 300 ms.
- The volume on the screen was right-aligned to x = 164 (the portrait
  width), mid-screen in landscape. It uses the screen width now.
- Long titles and artists are shortened with "..." instead of being cut
  off at the edge; ä, ö, ü, ß and other accented letters are in the font
  (`GF_Latin_Core`).

### Under the hood

- Volume redraws come from `on_volume` instead of a template sensor
  polling every 2 s.
- Unused globals and the Wi-Fi SSID sensor removed; key pins written
  `GPIO23` / `GPIO18`; Key 3 gets the internal pull-up.
- `requirements.txt` with the tested ESPHome version.

## v0.1.0 — 2026-10-27

First version in git: the config as it ran from Home Assistant's ESPHome
folder (`speaker-test.yaml`), built against ESPHome pull requests from late
2025.

### Added

- Sendspin player on an ESP32-A1S (ES8388 codec), amplifier switched with
  playback.
- 1.47" ST7789V screen with play state, volume, IP, title and artist.
- Buttons for previous/next track, volume and play/pause; headphone jack
  sensor.

### Under the hood

- OTA password moved to `secrets.yaml` (`speaker_1_ota_password`); unused
  `ha_base_url` / `ha_token` substitutions removed.
- `project:` name and version added.
