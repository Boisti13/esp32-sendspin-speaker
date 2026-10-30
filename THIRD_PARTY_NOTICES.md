# Third-Party Notices

The project's own files are under the MIT License, except the hardware
design in `hardware/`, which is under CERN-OHL-P-2.0
([hardware/LICENSE](hardware/LICENSE)). These parts come from others and
keep their own licenses.

## Ubuntu Font

`fonts/Ubuntu-Medium.ttf` is from the [Ubuntu Font Family](https://design.ubuntu.com/font)
(Canonical). Ubuntu Font Licence 1.0.

## Material Design Icons

`fonts/MaterialDesignIconsDesktop.ttf` is the desktop font of
[Material Design Icons](https://pictogrammers.com/library/mdi/)
(Pictogrammers), Apache License 2.0.

## LCSC / EasyEDA parts

`hardware/lib/lcsc.kicad_sym`, `hardware/lib/lcsc.pretty/` and
`hardware/lib/lcsc.3dshapes/` hold symbols, footprints and 3D models for
ESP32-A1S (C277945), NS4150B (C189961), FS8205A (C2830320), MSK12C02
(C431540) and PJ-320D (C431535), converted from LCSC's EasyEDA component
library with [easyeda2kicad](https://github.com/uPesy/easyeda2kicad.py)
and adjusted (3D paths, non-plated pegs, antenna keepout, courtyard).
They come from LCSC/EasyEDA's library, which publishes no explicit
licence; they are not covered by this project's licences.

## ESPHome and build libraries

The firmware is built with ESPHome; the build downloads ESP-IDF and other
libraries. They are not part of this repository and keep their own
licenses.
