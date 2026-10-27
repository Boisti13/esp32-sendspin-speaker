# Changelog

## Unreleased

### To do

- Port to ESPHome 2026.10's built-in Sendspin: drop the
  `external_components` (the pinned `audio` copy breaks validation) and the
  options the merged `sendspin` no longer has (`kalman_process_error`).
- Set the ES8388 output on the device instead of through Home Assistant
  (the `on_boot` call runs before the API is connected).
- Check the entity the track buttons call (`media_player.speaker_1`).

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
