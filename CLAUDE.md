# Working on this repository

ESPHome firmware that turns an ESP32-A1S audio board (ES8388 codec) with a
1.47" ST7789V screen into a Sendspin speaker for Music Assistant / Home
Assistant. Layout and how-tos are in [README.md](README.md); this is the
checklist. Infrastructure (Home Assistant, servers) is not in this
repository.

## Ground rules

- **Start with `git pull` on `dev`.** The owner works from more than one
  computer.
- **Work on `dev`, commit and push to `dev`.** `main` gets releases only,
  when the owner asks.
- **Ask before side effects**: pushing, flashing, copying to Home Assistant,
  changing Home Assistant.
- **One change = one commit** with the YAML, the version bump, README and
  CHANGELOG.
- **The owner flashes.** Never upload to the device unasked.
- **No secrets in the repo** (it is public). `secrets.yaml` is ignored;
  passwords and keys only as `!secret`.

## Checking a change

ESPHome checks run on the build server (CT 117 on pve_rptu_dev), never
locally while it is reachable:

```bash
bash ../claude-setup/scripts/esphome-check.sh speaker.yaml config    # every change
bash ../claude-setup/scripts/esphome-check.sh speaker.yaml           # + compile
```

## Home Assistant copy

The ESPHome app builds `/homeassistant/esphome/speaker-test.yaml` (device
`speaker-1`), with the fonts from `/homeassistant/esphome/fonts/`: a plain
copy of `speaker.yaml` (v0.3.0 since 2026-10-27). The shared `secrets.yaml`
there has `speaker_1_key` and `speaker_1_ota_password`. Copy a new version
only when the owner asks: back up the old file to
`/config/project-backups/esphome/esp32-sendspin-speaker/` first, copy with
`git show <commit>:speaker.yaml`, check the files match.

## Versions to bump

| Change | Bump |
|---|---|
| fix | patch: `speaker.yaml` (`esphome.project.version`), README badge, CHANGELOG |
| new feature or setting | minor, same three places |
| breaks setups (new secrets, renamed entities) | major (minor while 0.x) |
| docs only | none; `## Unreleased` → *Under the hood* |

## Conventions

- Files use LF line endings (`.gitattributes`). Writing files from Python on
  Windows: `open(..., newline="\n")`.
- A new icon on the screen must also go into the `glyphs` of `mdi_icons`.
- The screen is `update_interval: never`: anything that changes what it
  shows calls `component.update: tft_display` (and respects
  `playback_starting`, which keeps it quiet while the audio pipeline
  starts).
- The player's `on_state` also fires on volume changes: start/stop logic
  goes through `was_playing` and the `playback_started` /
  `playback_stopped` scripts, never straight into `on_state`.
- Keys call the device's own player (`media_player.next` etc.), not Home
  Assistant: the speaker must keep working without HA.
