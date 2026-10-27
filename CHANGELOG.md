# Changelog

## Unreleased

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
