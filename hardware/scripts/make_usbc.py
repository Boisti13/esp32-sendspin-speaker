"""Draw the USB-C board (usb/sendspin-speaker-usb.kicad_sch)."""
import os, sys
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(__file__))
from schgen import Sheet, POWER

OUT = "D:/dev/esp32-sendspin-speaker/hardware/usb/sendspin-speaker-usb.kicad_sch"
ROOT = "96d16dac-4b7a-4a9a-9844-1abd0c616560"
TITLE = "ESP32 Sendspin Speaker — USB-C board"
R0805 = "Resistor_SMD:R_0805_2012Metric"

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
for k, (ref, cc) in enumerate((("R701", "CC1"), ("R702", "CC2"))):
    r = s.part("Device", "R", ref, "5.1k", 91.44 + 17.78 * k, 109.22, footprint=R0805)
    net(r["1"], cc, bend=(5.08, 0)); net(r["2"], "GND")

e = s.part("Power_Protection", "USBLC6-2SC6", "U701", "USBLC6-2SC6", 137.16, 88.9,
           footprint="Package_TO_SOT_SMD:SOT-23-6")
net(e["1"], "USB_DP"); net(e["6"], "USB_DP"); net(e["3"], "USB_DN"); net(e["4"], "USB_DN")
net(e["5"], "VBUS", bend=(5.08, 0)); net(e["2"], "GND")

# J_USB to the main board (same pin order as main J301)
j = s.part("Connector_Generic", "Conn_01x04", "J701", "J_USB", 190.5, 88.9,
           footprint="Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical")
net(j["1"], "VBUS"); net(j["2"], "USB_DN"); net(j["3"], "USB_DP"); net(j["4"], "GND", stub=5.08)

for x, n in ((25.4, "VBUS"), (38.1, "GND")):      # supplies that only pass through connectors
    s.flag(x, 38.1); s.wire(x, 38.1, x, 43.18)
    if n in POWER:
        s.power(n, x, 43.18)
    else:
        s.label("label", n, x, 43.18, (1, 0))

s.text("USB-C board\n"
       "Receptacle, 5.1k on CC1 and CC2 separately (5 V sink), USBLC6-2SC6 next to the receptacle.\n"
       "J701 to the main board's J_USB (XH 4: VBUS, D-, D+, GND). Cable <= 15 cm for USB full speed.\n"
       "Fit this board or USB301 on the main board, not both.", 38.1, 152.4)

s.write(OUT, ROOT, TITLE, paper="A4")
print("ok")
