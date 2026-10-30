"""Draw the main board's USB sheet (usb.kicad_sch)."""
import os, sys
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(__file__))
from schgen import Sheet, POWER

OUT = "D:/dev/esp32-sendspin-speaker/hardware/main/usb.kicad_sch"
ROOT, SHEET = "1294b3cd-656f-456e-a4e5-c0aee204737d", "b9affbcc-9f38-4a2c-914f-0b930952d8a7"
FILE_UUID = "cfc7eebe-a734-41a2-8d5b-6a2f56122061"
TITLE = "ESP32 Sendspin Speaker — main board — USB"

R0805, C0805 = "Resistor_SMD:R_0805_2012Metric", "Capacitor_SMD:C_0805_2012Metric"
HIER = {"VBUS": "output", "U0RXD": "output", "U0TXD": "input", "EN": "output", "IO0": "output"}

s = Sheet("sendspin-speaker-main", f"/{ROOT}/{SHEET}", pwr_base=300)


def net(pin, name, bend=None, stub=2.54):
    if name in POWER:
        s.attach(pin, name, stub=stub)
    elif name in HIER:
        s.attach(pin, name, stub=stub, shape=HIER[name], bend=bend)
    else:
        s.attach(pin, name, stub=stub, kind="label", bend=bend)


def two(lib, name, ref, value, x, y, top, bottom, fp, **kw):
    p = s.part(lib, name, ref, value, x, y, footprint=fp, **kw)
    net(p["1"], top, bend=(5.08, 0)); net(p["2"], bottom, bend=(5.08, 0))
    return p


# --- USB-C on the board (fit this or J_USB) ------------------------------------
u = s.part("Connector", "USB_C_Receptacle_USB2.0_16P", "USB301", "USB-C", 60.96, 88.9,
           footprint="Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12")
USB_NETS = {"A4": "VBUS", "A5": "CC1", "B5": "CC2", "A6": "USB_DP", "B6": "USB_DP",
            "A7": "USB_DN", "B7": "USB_DN", "A1": "GND", "SH": "GND", "A8": None, "B8": None}
for pad, n in USB_NETS.items():   # stacked pins (VBUS x4, GND x4) share one end: wired once
    if n is None:
        s.no_connect(*u[pad][:2])
    else:
        net(u[pad], n, stub=5.08)
two("Device", "R", "R301", "5.1k", 101.6, 109.22, "CC1", "GND", R0805)
two("Device", "R", "R302", "5.1k", 119.38, 109.22, "CC2", "GND", R0805)

# --- or any USB-C receptacle on a cable (bare breakout): CC goes through the cable too ----
j = s.part("Connector_Generic", "Conn_01x06", "J301", "J_USB", 60.96, 149.86,
           footprint="Connector_JST:JST_XH_B6B-XH-A_1x06_P2.50mm_Vertical")
for i, n in enumerate(("VBUS", "USB_DN", "USB_DP", "CC1", "CC2", "GND"), start=1):
    net(j[str(i)], n, stub=5.08 if n == "GND" else 2.54)

# --- ESD ---------------------------------------------------------------------------
e = s.part("Power_Protection", "USBLC6-2SC6", "U301", "USBLC6-2SC6", 147.32, 88.9,
           footprint="Package_TO_SOT_SMD:SOT-23-6")
net(e["1"], "USB_DP"); net(e["6"], "USB_DP"); net(e["3"], "USB_DN"); net(e["4"], "USB_DN")
net(e["5"], "VBUS", bend=(5.08, 0)); net(e["2"], "GND")

# --- CH340C's own 3.3 V from VBUS (no battery drain) --------------------------------
r = s.part("Regulator_Linear", "XC6206PxxxMR", "U303", "XC6206P332MR", 147.32, 147.32,
           footprint="Package_TO_SOT_SMD:SOT-23-3")
net(r["3"], "VBUS"); net(r["2"], "+3V3_USB"); net(r["1"], "GND")
two("Device", "C", "C301", "1u", 127.0, 162.56, "VBUS", "GND", C0805)
two("Device", "C", "C302", "1u", 170.18, 162.56, "+3V3_USB", "GND", C0805)

# --- CH340C ------------------------------------------------------------------------------
c = s.part("sendspin-speaker", "CH340C", "U302", "CH340C", 228.6, 101.6,
           footprint="Package_SO:SOIC-16_3.9x9.9mm_P1.27mm")
net(c["16"], "+3V3_USB")                                       # VCC
s.wire(*c["4"][:2], c["4"][0], c["4"][1] - 2.54)               # V3 tied to VCC (3.3 V supply)
s.wire(c["4"][0], c["4"][1] - 2.54, c["16"][0], c["4"][1] - 2.54)
s.wire(c["16"][0], c["4"][1] - 2.54, *c["16"][:2])
net(c["1"], "GND"); net(c["15"], "GND")                        # R232 off
net(c["5"], "USB_DP", stub=5.08); net(c["6"], "USB_DN", stub=5.08)
for p in ("7", "8", "9", "10", "11", "12"):                     # NC, CTS/DSR/RI/DCD unused
    s.no_connect(*c[p][:2])
net(c["2"], "CH_TXD", stub=5.08); net(c["3"], "CH_RXD", stub=5.08)
net(c["13"], "DTR", stub=5.08); net(c["14"], "RTS", stub=5.08)
two("Device", "C", "C303", "100n", 200.66, 73.66, "+3V3_USB", "GND", C0805)
two("Device", "R", "R303", "470", 271.78, 88.9, "CH_TXD", "U0RXD", R0805)
two("Device", "R", "R304", "470", 271.78, 111.76, "U0TXD", "CH_RXD", R0805)

# --- auto-reset: DTR/RTS -> EN/IO0 (UMH3N, base resistors built in) -----------------
q = s.part("Transistor_BJT", "UMH3N", "Q301", "UMH3N", 330.2, 88.9,
           footprint="Package_TO_SOT_SMD:SOT-363_SC-70-6", unit=1)
net(q["2"], "DTR"); net(q["1"], "RTS", bend=(5.08, 0)); net(q["6"], "EN", bend=(5.08, 0))
q = s.part("Transistor_BJT", "UMH3N", "Q301", "UMH3N", 330.2, 124.46,
           footprint="Package_TO_SOT_SMD:SOT-363_SC-70-6", unit=2)
net(q["5"], "RTS"); net(q["4"], "DTR", bend=(5.08, 0)); net(q["3"], "IO0", bend=(5.08, 0))

# --- VBUS comes in through a passive connector: flag it as a supply --------------
s.flag(38.1, 63.5); s.wire(38.1, 63.5, 38.1, 68.58)
s.label("hierarchical_label", "VBUS", 38.1, 68.58, (1, 0), "output")

s.text("USB\n"
       "Fit USB301 (on board) or J301 + an off-board USB-C receptacle, not both. J301 carries\n"
       "VBUS, D-, D+, CC1, CC2, GND: the off-board part is a bare connector (our usb/ board or any\n"
       "breakout). R301/R302 (5.1k) and U301 (ESD) here serve both; leave R301/R302 off if the\n"
       "breakout already has its own 5.1k.\n"
       "CH340C runs from its own XC6206 (3.3 V from VBUS): no battery drain without USB.\n"
       "V3 tied to VCC (3.3 V supply); R232 low; CTS/DSR/RI/DCD unused (internal pull-ups).\n"
       "TX/RX through 470R. Auto-reset: DTR/RTS both low or both high = idle; the usual\n"
       "esptool sequence pulls EN or IO0 low (GPIO0 is also the codec's MCLK, as on the Audio Kit).",
       38.1, 190.5)

s.write(OUT, FILE_UUID, TITLE, paper="A3")
print("ok")
