"""Silkscreen labels on the main board: pin names at every connector, what each
connector, switch and LED is for, and the board name on the back.

    D:/Programs/KiCad/10.0/bin/python.exe -u hardware/scripts/silk_main.py
Removes the labels it wrote before (they carry the "silk:" prefix in no field, so they
are recognised by layer + the marker set below) and writes them again. KiCad closed.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
from pcbplace import Board, mm

B = Board("D:/dev/esp32-sendspin-speaker/hardware/main/sendspin-speaker-main.kicad_pcb",
          100.0, 100.0, 100.0, 58.0)
CX, CY = B.x0 + B.w / 2, B.y0 + B.h / 2
MARK = "~"          # every label this script writes ends with a hidden marker: a trailing space

PINS = {   # connector -> pin names, pin 1 first
    "J501": ["3V3", "GND", "SCK", "MOSI", "CS", "DC", "B1", "B3", "B4", "B5", "B6", "LED"],
    "J301": ["5V", "D-", "D+", "CC1", "CC2", "GND"],
    "J502": ["V+", "LED", "GND"],
    "J201": ["+", "-"],
    "J202": ["SW", "SW"],
    "J203": ["V+", "CHG", "FULL"],
    "J401": ["+", "-"],
    "J402": ["+", "-"],
}
WHAT = {   # part -> function label
    "J501": "PANEL", "J301": "USB", "J502": "LED", "J201": "BAT", "J202": "SWITCH",
    "J203": "CHARGE", "J401": "SPK L", "J402": "SPK R", "J403": "PHONES",
    "USB301": "USB-C", "SW201": "ON/OFF", "SW101": "RESET", "SW102": "BOOT",
    "D101": "STATUS", "D201": "CHG", "D202": "FULL", "JP201": "BYPASS",
}

# remove what an earlier run wrote
for d in list(B.b.GetDrawings()):
    if d.GetClass() == "PCB_TEXT" and d.GetText().endswith(" ") and d.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS):
        B.trash.append(d); B.b.Remove(d)


def text(s, x, y, size=0.8, rot=0, just="center", layer=pcbnew.F_SilkS):
    t = pcbnew.PCB_TEXT(B.b)
    t.SetText(s + " ")                                    # trailing space = written by this script
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(0.15))
    t.SetTextAngleDegrees(rot)
    t.SetHorizJustify({"left": pcbnew.GR_TEXT_H_ALIGN_LEFT, "right": pcbnew.GR_TEXT_H_ALIGN_RIGHT,
                       "center": pcbnew.GR_TEXT_H_ALIGN_CENTER}[just])
    t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    if layer == pcbnew.B_SilkS:
        t.SetMirrored(True)
    t.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    B.b.Add(t)


for ref, names in PINS.items():
    x0, y0, w, h = B.bbox(ref)
    pads = {p.GetNumber(): p.GetPosition() for p in B.fp[ref].Pads()}
    xs = [pcbnew.ToMM(pads[str(i + 1)].x) for i in range(len(names))]
    ys = [pcbnew.ToMM(pads[str(i + 1)].y) for i in range(len(names))]
    if max(xs) - min(xs) > max(ys) - min(ys):             # pins in a row: names stand upright
        top = y0 + h / 2 > CY                             # bottom-edge connector: names above it
        for n, x in zip(names, xs):
            if top:
                text(n, x, y0 - 0.5, rot=90, just="left")
            else:
                text(n, x, y0 + h + 0.5, rot=90, just="right")
        if top:
            text(WHAT[ref], x0 + w / 2, y0 - 5.4, size=1.0)
        else:                                             # speakers: label beside the "+ -"
            text(WHAT[ref], x0 + w / 2, y0 + h + 3.3, size=0.9)
    else:                                                 # pins in a column: names beside it
        left = x0 + w / 2 > CX                            # right-edge connector: names to its left
        for n, y in zip(names, ys):
            text(n, x0 - 0.5 if left else x0 + w + 0.5, y, just="right" if left else "left")
        text(WHAT[ref], (x0 - 3.0) if left else (x0 + w + 3.0), y0 - 0.8, size=0.9)

for ref in ("J403", "USB301", "SW201", "SW101", "SW102", "D101", "D201", "D202", "JP201"):
    x0, y0, w, h = B.bbox(ref)
    if ref in ("J403", "USB301"):                         # left edge: label to the right
        text(WHAT[ref], x0 + w + 0.8, y0 + h / 2, size=1.0, just="left")
    elif ref == "SW201":                                  # right edge: label to the left
        text(WHAT[ref], x0 - 0.8, y0 + h / 2, size=1.0, just="right")
    else:                                                 # small parts: label underneath
        text(WHAT[ref], x0 + w / 2, y0 + h + 0.9, size=0.8)

# board name on the back
text("ESP32 Sendspin Speaker", CX, CY - 3.0, size=1.5, layer=pcbnew.B_SilkS)
text("main board  Rev A  2026-10", CX, CY, size=1.0, layer=pcbnew.B_SilkS)
text("CERN-OHL-P-2.0  github.com/Boisti13/esp32-sendspin-speaker", CX, CY + 2.5, size=0.8,
     layer=pcbnew.B_SilkS)

B.save()
print("labels written")
