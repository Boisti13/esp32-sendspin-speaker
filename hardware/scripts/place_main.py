"""Placement of the main board: outline, M3 holes, fixed parts, passives at their pins, GND pours.

Run with KiCad's Python while KiCad is closed:
    D:/Programs/KiCad/10.0/bin/python.exe -u hardware/scripts/place_main.py
A starting point for hand placement in KiCad, not a finished layout: once the board
has been edited in KiCad, don't run this again.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
from pcbplace import Board, mm, preload

preload("MountingHole", "MountingHole_3.2mm_M3")

X0, Y0, W, H = 100.0, 100.0, 90.0, 58.0
B = Board("D:/dev/esp32-sendspin-speaker/hardware/main/sendspin-speaker-main.kicad_pcb", X0, Y0, W, H)
HOLES = B.corners(4.5)

# --- fixed parts ---------------------------------------------------------------------
# module: antenna hangs over the top edge; the footprint's antenna starts 12.32 mm above its origin
u = B.fp["U101"]
u.SetOrientationDegrees(0)
u.SetPosition(pcbnew.VECTOR2I(mm(150.0), mm(Y0 + 12.32)))

B.place("J401", 161.5, Y0 + 0.5)                          # speakers, top edge right of the module
B.place("J402", 171.0, Y0 + 0.5)                          #   (the amps sit by its speaker outputs)
B.place("SW102", 109.5, Y0 + 1.0)                         # Boot and Reset, top edge left
B.place("SW101", 119.5, Y0 + 1.0)
B.place("J403", X0 - 0.5, 110.0)                          # headphone jack, left edge
B.place("USB301", X0 - 0.8, 128.0, 270)                   # USB-C, left edge, mouth outward
B.place("J301", 109.5, Y0 + H - 7.3)                      # J_USB, bottom edge
B.place("J501", 129.5, Y0 + H - 7.3)                      # J_UI
B.place("J502", 164.5, Y0 + H - 7.3)                      # J_LED
for ref, y in (("J201", 109.5), ("SW201", 119.0), ("J202", 127.5), ("J203", 137.0)):
    w, _ = B.size(ref, 90)
    B.place(ref, X0 + W - w - 0.5, y, 90)                 # battery, switch, J_SW, J_CHG: right edge

FIXED = ["U101", "J401", "J402", "SW101", "SW102", "J403", "USB301", "J301", "J501", "J502",
         "J201", "SW201", "J202", "J203"]
B.taken(FIXED)
for hx, hy in HOLES:                                      # M3 heads: 6 mm plus margin
    B.keepout(hx - 3.6, hy - 3.6, hx + 3.6, hy + 3.6)

# --- ICs near what they talk to --------------------------------------------------------
px, py = B.pad("U101", "25")
B.near("U401", px + 9.0, py - 1.5)                        # amps by the module's SPOL/SPOR pads
px, py = B.pad("U101", "23")
B.near("U402", px + 9.0, py + 4.5)
B.near("C421", 176.0, 121.0)                              # bulk next to the amps
B.near("U302", 122.0, 137.0)                              # CH340C
B.near("U301", 113.5, 135.0)                              # ESD by the receptacle
B.near("U303", 130.0, 134.0)                              # CH340C's 3.3 V
B.near("Q301", 130.0, 141.0)                              # auto-reset
B.near("U201", 146.0, 136.0)                              # TP4056
B.near("U202", 175.0, 112.0, rot=90)                      # DW01A by J_BAT
B.near("Q201", 175.0, 117.0)                              # FS8205A
B.near("D205", 160.0, 136.0)                              # load sharing
B.near("Q202", 167.0, 136.0)
B.near("U203", 152.0, 143.0)                              # AP2112K
B.near("JP201", 178.0, 128.0)                             # switch bypass

# --- passives at the pin they serve (most critical first) ------------------------------
AT = [  # part, anchor, pad, offset from the pad (mm)
    ("C102", "U101", "2", (-4, 0)), ("C101", "U101", "2", (-4, -2)),           # 3V3 decoupling
    ("R101", "U101", "35", (4, 0)), ("C103", "U101", "35", (4, 2)),            # EN RC
    ("R102", "U101", "4", (-4, 0)), ("R103", "U101", "3", (-4, 0)),            # input pull-ups
    ("R207", "U101", "5", (-4, 0)), ("R208", "U101", "5", (-4, 2)),            # battery divider
    ("C207", "U101", "5", (-4, 4)),
    ("R105", "U101", "7", (-4, 0)), ("R106", "U101", "9", (-4, 0)),            # I2C option
    ("R104", "U101", "10", (-4, 0)), ("R107", "U101", "8", (-4, 0)),           # CS pull-up, strap
    ("R108", "U101", "8", (-8, 0)), ("D101", "U101", "8", (-12, 0)),           # status LED
    ("C403", "U401", "2", (-3, 0)), ("C404", "U401", "6", (3, 0)), ("C405", "U401", "6", (3, 2)),
    ("C401", "U401", "3", (-5, 0)), ("R401", "U401", "3", (-9, 0)),
    ("C402", "U401", "4", (-5, 2)), ("R402", "U401", "4", (-9, 2)),
    ("R421", "U401", "1", (-4, -2)),
    ("C413", "U402", "2", (-3, 0)), ("C414", "U402", "6", (3, 0)), ("C415", "U402", "6", (3, 2)),
    ("C411", "U402", "3", (-5, 0)), ("R411", "U402", "3", (-9, 0)),
    ("C412", "U402", "4", (-5, 2)), ("R412", "U402", "4", (-9, 2)),
    ("C422", "J403", "4", (3, 5)), ("C423", "J403", "3", (3, 9)),               # headphone caps
    ("R301", "USB301", "A5", (6, 0)), ("R302", "USB301", "B5", (6, 0)),       # CC
    ("C303", "U302", "16", (0, -3)), ("R303", "U302", "2", (4, 0)), ("R304", "U302", "3", (4, 0)),
    ("C301", "U303", "3", (-3, 0)), ("C302", "U303", "2", (3, 0)),
    ("C201", "U201", "4", (0, -3)), ("C202", "U201", "5", (3, 0)), ("R201", "U201", "2", (3, 0)),
    ("D203", "U201", "7", (-3, 0)), ("R202", "U201", "7", (-3, 3)),
    ("D204", "U201", "6", (-3, 0)), ("R203", "U201", "6", (-3, 3)),
    ("D201", "U201", "7", (-6, 6)), ("D202", "U201", "6", (-3, 7)),
    ("C203", "U202", "5", (0, -3)), ("R204", "U202", "5", (0, -5)), ("R205", "U202", "2", (0, 3)),
    ("R206", "Q202", "1", (-3, 0)), ("C204", "Q202", "2", (3, 0)),
    ("C205", "U203", "1", (-3, 0)), ("C206", "U203", "5", (3, 0)),
    ("R501", "J502", "2", (0, -5)),
]
far = []
for ref, anchor, pad, (dx, dy) in AT:
    px, py = B.pad(anchor, pad)
    d = B.near(ref, px + dx, py + dy)
    if d > 4.0:
        far.append(f"{ref} {d:.1f} mm")
print("further than 4 mm from their spot:", far)

B.outline(radius=3.0)
B.holes("MountingHole_3.2mm_M3", HOLES)                   # 4.5 mm in: a 6 mm screw head stays on the board
B.gnd_pour()
B.save()
print("saved")
