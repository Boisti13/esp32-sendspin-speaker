# ESP32 Sendspin Speaker

[![Release](https://img.shields.io/github/v/release/Boisti13/esp32-sendspin-speaker?include_prereleases)](https://github.com/Boisti13/esp32-sendspin-speaker/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Version](https://img.shields.io/badge/version-0.2.0-orange)
![ESPHome](https://img.shields.io/badge/ESPHome-2026.10.0-black)

A network speaker for Home Assistant and Music Assistant on an ESP32-A1S
audio board. It plays [Sendspin](https://www.sendspin-audio.com/) streams
(Music Assistant's synchronised multi-room audio), shows what's playing on a
small colour screen and has hardware buttons for play/pause, volume and
tracks. Built with ESPHome.

> Since v0.2.0 it uses the Sendspin components built into ESPHome 2026.10;
> no pull requests or external components any more.

## Highlights

- **Sendspin player**: shows up in Music Assistant as a player and plays in
  sync with other Sendspin speakers.
- **ES8388 codec** on the A1S board, stereo, 48 kHz / 32-bit I²S; output
  set to both outputs (speaker and headphone) at boot, on the device itself.
- **Amplifier switched with playback**: on 150 ms after playback starts
  (no pop while the codec settles), off 300 ms after it stops or pauses (no
  click on the last audio).
- **1.47" screen** (320 × 172 landscape, ST7789V): play/pause icon, volume,
  IP address, title and artist. Long names end in "...", accented letters
  (ä, ö, ü, ß, é) are in the font. Redrawn only when something changes.
- **Six buttons that work without Home Assistant**: previous, next, volume
  down/up, play/pause go straight to the player and on to Music Assistant
  through Sendspin. Headphone jack detection.

## Hardware

| Part | |
|---|---|
| Board | ESP32-A1S audio kit (ESP32-WROVER with PSRAM, ES8388 codec) |
| Codec | ES8388, I²C SDA 33 / SCL 32; I²S LRCLK 25, BCLK 27, DOUT 26, MCLK 0 |
| Amplifier enable | GPIO21 |
| Screen | Waveshare 1.47" 172 × 320, ST7789V; SPI CLK 14, MOSI 13, CS 15, DC 22, RST 12 |
| Headphone jack detect | GPIO39 |

### Buttons

| Key | Pin | Does |
|---|---|---|
| Key 1 | GPIO36 | previous track |
| Key 2 | — | its pin (GPIO13) is the screen's MOSI |
| Key 3 | GPIO19 | next track |
| Key 4 | GPIO23 | volume down |
| Key 5 | GPIO18 | volume up |
| Key 6 | GPIO5 | play / pause (toggle) |

GPIO12 (screen reset) is a strapping pin: if it is high at power-on the
ESP32 picks 1.8 V flash and doesn't boot. Worth moving if boot is flaky.

## Install

| Step | |
|---|---|
| 1 | Copy `secrets.example.yaml` to `secrets.yaml` and fill in Wi-Fi, a new API key (`openssl rand -base64 32`) and an OTA password. In Home Assistant's ESPHome app the shared `secrets.yaml` gets `speaker_1_key` and `speaker_1_ota_password`. |
| 2 | Put `speaker.yaml` and `fonts/` into the ESPHome folder. |
| 3 | Flash once over USB: `esphome run speaker.yaml`. After that, over Wi-Fi. |
| 4 | Add the device in Home Assistant with the API key. It needs no Home Assistant actions. |
| 5 | In Music Assistant, enable the Sendspin provider; the speaker appears as a player. |

## Example: playing an album

Start an album in Music Assistant on *Sendspin Media Player*. The board
switches to *playing*, waits 150 ms, turns the amplifier on and two seconds
later draws the screen once: pause icon, `VOL 65%`, the title in large type
and the artist below (*Die Ärzte* shows with its umlaut; a long title ends
in "..."). Press Key 5 and the volume goes up a step; the screen redraws
with the new value. Press Key 3 and Music Assistant skips to the next track.
Press Key 6 to pause: the icon changes to play and the amplifier turns off
300 ms later.

## Layout

```
speaker.yaml           the whole device: board, codec, Sendspin, screen, buttons
requirements.txt       the ESPHome version it is tested with
fonts/                 Ubuntu Medium and Material Design Icons for the screen
secrets.example.yaml   the secrets the config expects
```

## Development

- Check a change: `esphome config speaker.yaml`, then
  `esphome compile speaker.yaml`.
- ESPHome **2026.10.0** (`requirements.txt`), the version of Home
  Assistant's ESPHome app. Sendspin, `speaker_source` and `media_source`
  are built in since then; older versions don't have them.
- The screen has `update_interval: never`: every change that shows on it
  calls `component.update: tft_display`.

## License

MIT, see [LICENSE](LICENSE). Fonts: see
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
