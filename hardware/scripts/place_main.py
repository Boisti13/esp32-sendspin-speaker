"""First placement of the main board: outline, M3 holes, parts by function, GND pours.

Run with KiCad's Python while KiCad is closed:
    D:/Programs/KiCad/10.0/bin/python.exe hardware/scripts/place_main.py
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

# module: antenna hangs over the top edge (its keepout stays outside the board);
# the footprint's antenna starts 12.32 mm above its origin
u = B.fp["U101"]
u.SetOrientationDegrees(0)
u.SetPosition(pcbnew.VECTOR2I(mm(150.0), mm(Y0 + 12.32)))

# edge connectors
B.place("J401", 109.5, Y0 + 0.5)                          # speakers, top edge
B.place("J402", 119.5, Y0 + 0.5)
B.place("J403", X0 - 0.5, 110.0)                          # headphone jack, left edge
B.place("USB301", X0 - 0.8, 128.0, 270)                   # USB-C, left edge, mouth outward
B.place("J301", 109.5, Y0 + H - 7.3)                      # J_USB, bottom edge
B.place("J501", 129.5, Y0 + H - 7.3)                      # J_UI, bottom edge
B.place("J502", 164.5, Y0 + H - 7.3)                      # J_LED, bottom edge
B.place("R501", 176.5, Y0 + H - 5.0)                      # its series resistor
for ref, y in (("J201", 109.5), ("SW201", 119.0), ("J202", 127.5), ("J203", 137.0)):
    w, _ = B.size(ref, 90)
    B.place(ref, X0 + W - w - 0.5, y, 90)                 # battery, switch, J_SW, J_CHG: right edge

# functional clusters
left = []
left += B.pack(["U401", "U402", "C421", "C401", "R401", "C402", "R402", "C403", "C404", "C405",
                "C411", "R411", "C412", "R412", "C413", "C414", "C415", "R421"],
               115.5, 108.5, 138.0, 129.0)                                    # audio
left += B.pack(["C422", "C423"], 101.0, 121.0, 114.5, 127.0)                # headphone caps by the jack
left += B.pack(["C101", "C102", "R101", "C103", "SW101", "SW102", "R102", "R103", "R104",
                "R105", "R106", "R107", "R108", "D101"], 162.5, 106.5, 181.0, 129.0)  # MCU
left += B.pack(["U302", "U301", "U303", "Q301", "R301", "R302", "R303", "R304",
                "C301", "C302", "C303"], 112.0, 130.5, 140.0, 149.5)       # USB / CH340C
left += B.pack(["U201", "U202", "Q201", "Q202", "D205", "U203", "D203", "D204", "JP201",
                "R201", "R202", "R203", "R204", "R205", "R206", "R207", "R208",
                "C201", "C202", "C203", "C204", "C205", "C206", "C207", "D201", "D202"],
               141.5, 130.5, 181.0, 149.5)                                    # power
print("did not fit:", left)

B.outline(radius=3.0)                                        # rounded corners
B.holes("MountingHole_3.2mm_M3", B.corners(4.5))   # 4.5 mm in: a 6 mm screw head stays on the board
B.gnd_pour()
B.save()
print("saved")
