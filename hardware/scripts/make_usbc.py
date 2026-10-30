"""Draw the USB-C board (usb/sendspin-speaker-usb.kicad_sch): a bare breakout."""
import os, sys
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(__file__))
from schgen import Sheet, POWER

OUT = "D:/dev/esp32-sendspin-speaker/hardware/usb/sendspin-speaker-usb.kicad_sch"
ROOT = "96d16dac-4b7a-4a9a-9844-1abd0c616560"
TITLE = "ESP32 Sendspin Speaker — USB-C board"

s = Sheet("sendspin-speaker-usb", f"/{ROOT}", pwr_base=700)


def net(pin, name, stub=2.54, bend=None):
    if name in POWER:
        s.attach(pin, name, stub=stub)
    else:
        s.attach(pin, name, stub=stub, kind="label", bend=bend)


u = s.part("Connector", "USB_C_Receptacle_USB2.0_16P", "USB701", "USB-C", 50.8, 88.9,
           footprint="Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12")
for pad, n in {"A4": "VBUS", "A5": "CC1", "B5": "CC2", "A6": "USB_DP", "B6": "USB_DP",
               "A7": "USB_DN", "B7": "USB_DN", "A1": "GND", "SH": "GND"}.items():
    net(u[pad], n, stub=5.08)
for pad in ("A8", "B8"):
    s.no_connect(*u[pad][:2])

# J_USB to the main board (same pin order as main J301). No parts on this board: the
# CC resistors and ESD sit on the main board, so any USB-C breakout can replace it.
j = s.part("Connector_Generic", "Conn_01x06", "J701", "J_USB", 127.0, 88.9,
           footprint="Connector_JST:JST_XH_B6B-XH-A_1x06_P2.50mm_Vertical")
for i, n in enumerate(("VBUS", "USB_DN", "USB_DP", "CC1", "CC2", "GND"), start=1):
    net(j[str(i)], n, stub=5.08 if n == "GND" else 2.54)

for x, n in ((25.4, "VBUS"), (38.1, "GND")):      # supplies that only pass through connectors
    s.flag(x, 38.1); s.wire(x, 38.1, x, 43.18)
    if n in POWER:
        s.power(n, x, 43.18)
    else:
        s.label("label", n, x, 43.18, (1, 0))

s.text("USB-C board\n"
       "Bare breakout: receptacle and J701 only, no parts. The 5.1k CC resistors and the ESD\n"
       "sit on the main board, so any USB-C breakout or panel socket that brings out VBUS, D-,\n"
       "D+, CC1, CC2 and GND can replace this board (without its own 5.1k, or leave R301/R302 off).\n"
       "J701 to the main board's J_USB (XH 6). Cable <= 15 cm for USB full speed.\n"
       "Fit this board or USB301 on the main board, not both.", 38.1, 152.4)

s.write(OUT, ROOT, TITLE, paper="A4")
print("ok")
