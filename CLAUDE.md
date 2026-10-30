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
- **Push and copy to Home Assistant without asking once the compile
  check passes** (owner, 2026-10-29): push `dev`, then copy to HA as in
  *Home Assistant copy* below. Still ask before anything else with side
  effects: flashing, merging to `main`, other changes in Home Assistant.
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
`speaker-1`), with the fonts from `/homeassistant/esphome/fonts/` and
the boot chime from `/homeassistant/esphome/sounds/boot.wav` (v0.6.0 on): a plain
copy of `speaker.yaml` (v0.7.0 since 2026-10-29). The shared `secrets.yaml`
there has `speaker_1_key` and `speaker_1_ota_password`. Copy every new version
whose compile check passed (no need to ask): back up the old file to
`/config/project-backups/esphome/esp32-sendspin-speaker/` first, copy with
`git show <commit>:speaker.yaml` (and `sounds/` if it changed), check the
files match.

## Hardware (`hardware/`)

Three KiCad 10 projects for the custom PCB: `main/` (module, audio,
power), `ui/` (front panel: OLED + buttons) and `usb/` (USB-C board),
sharing `hardware/lib/`. Boards, connectors, parts and pin plan in
[hardware/README.md](hardware/README.md), kept current with every change.

- **Off-board parts connect by JST** (owner, 2026-10-30): front panel,
  USB-C board, LiPo, speakers and status LED. USB-C can also sit on the
  main board (both footprints, fit one). The connector table in
  `hardware/README.md` is the contract: a pin-order change goes into both
  schematics and the table in the same commit.
- **0805 wherever possible** for SMD resistors, capacitors and LEDs
  (owner, 2026-10-30); exceptions only where the part doesn't exist in
  0805, noted in the README.

- **KiCad runs on HX99G-BKG only** (KiCad 10 and the `kicad` MCP are
  there), not on the dev box. Push a `wip/` branch before switching PCs.
- **Pins are shared with the firmware.** A pin change goes into the
  schematic, `hardware/README.md` and `speaker-diy.yaml` in the same
  commit. GPIO12, 16, 17 and 35 stay unused.
- **Right footprint right away** (owner, 2026-10-30): every symbol gets its
  final footprint (and `LCSC` field where known) the moment it is placed,
  as listed in `hardware/README.md` → *Parts and footprints*. A part
  KiCad 10 doesn't have is imported from LCSC with easyeda2kicad
  (`~/.venvs/easyeda2kicad` on HX99G-BKG) into a scratch folder, checked,
  then merged into `hardware/lib/lcsc.*` with the fixes listed in the
  README (3D path, NPTH pegs, keepouts); add it to `THIRD_PARTY_NOTICES.md`.
- **Libraries are project-local** (`hardware/lib/`, tables use
  `${KIPRJMOD}/../lib`). Only our own parts or ones with a compatible
  licence; note any third-party part in `THIRD_PARTY_NOTICES.md`.
- **The A1S has no GPIO32/33/25/26/27/35 pads** (codec I²C/I²S are inside
  the module) and every other pad is used: a new signal means giving up
  one. Mind the straps (12 low, 2 low/floating, 15 high).
- **Don't commit production files** (Gerbers, BOM, CPL; `hardware/production/`
  is ignored). They go on a GitHub release tagged `hw-rev-a`, … — the owner
  says when. The revision is also on the silkscreen and in the title block.
- **Don't use the MCP's `vcs_commit_checkpoint`**: commits are made by
  hand, one per change, like the firmware.
- Check before committing: `kicad-cli sch erc` and `kicad-cli pcb drc`
  (`D:\Programs\KiCad\10.0\bin\kicad-cli.exe`). Hardware-only changes need
  no ESPHome check and no firmware version bump; they go into
  `## Unreleased` → *Under the hood* until a board revision is released.
- Hardware licence CERN-OHL-P-2.0 (`hardware/LICENSE`); the firmware stays
  MIT.

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
