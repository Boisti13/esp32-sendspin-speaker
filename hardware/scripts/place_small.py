"""First placement of the front panel and the USB-C board.

Run with KiCad's Python while KiCad is closed:
    D:/Programs/KiCad/10.0/bin/python.exe hardware/scripts/place_small.py
Don't run it again once a board has been edited in KiCad.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from pcbplace import Board, preload

preload("MountingHole", "MountingHole_3.2mm_M3")
preload("MountingHole", "MountingHole_2.2mm_M2")

HW = "D:/dev/esp32-sendspin-speaker/hardware"

# --- front panel: display header on top, five buttons in a row, J_UI on the back ----
X0, Y0, W, H = 100.0, 100.0, 75.0, 45.0
B = Board(f"{HW}/ui/sendspin-speaker-ui.kicad_pcb", X0, Y0, W, H)
w, _ = B.size("J602", 90)
B.place("J602", X0 + (W - w) / 2, Y0 + 3.0, 90)           # SPI display header, pins in a row
B.place("J603", X0 + (W + w) / 2 + 6.0, Y0 + 3.0, 90)     # I2C OLED header next to it
for k, ref in enumerate(("SW601", "SW603", "SW604", "SW605", "SW606")):
    B.place(ref, X0 + 9.0 + 12.0 * k, Y0 + H - 13.0)       # 12 mm pitch
B.place("J601", X0 + (W - 33.5) / 2, Y0 + 15.0, back=True)  # cable from the main board, back side
left = B.pack(["R601", "C602", "C601", "R602", "D601"], X0 + 7.0, Y0 + 15.0, X0 + 20.0, Y0 + 27.0)
print("front panel, did not fit:", left)
B.outline()
B.holes("MountingHole_3.2mm_M3", ((X0 + 3, Y0 + 3), (X0 + W - 3, Y0 + 3),
                                  (X0 + 3, Y0 + H - 3), (X0 + W - 3, Y0 + H - 3)))
B.gnd_pour()
B.save()

# --- USB-C board: receptacle on the left edge, J_USB on the right ---------------------
X0, Y0, W, H = 100.0, 100.0, 32.0, 20.0
B = Board(f"{HW}/usb/sendspin-speaker-usb.kicad_pcb", X0, Y0, W, H)
B.place("USB701", X0 - 0.8, Y0 + 5.0, 270)
w, _ = B.size("J701", 90)
B.place("J701", X0 + W - w - 0.5, Y0 + 3.3, 90)
left = B.pack(["U701", "R701", "R702"], X0 + 11.5, Y0 + 6.0, X0 + 23.0, Y0 + 14.0)
print("USB-C board, did not fit:", left)
B.outline()
B.holes("MountingHole_2.2mm_M2", ((X0 + 14.5, Y0 + 2.5), (X0 + 14.5, Y0 + H - 2.5)))
B.gnd_pour()
B.save()
print("saved")
