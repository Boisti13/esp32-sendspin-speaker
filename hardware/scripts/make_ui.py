"""Draw the front panel board (ui/sendspin-speaker-ui.kicad_sch): buttons and headers only."""
import os, sys
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(__file__))
from schgen import Sheet, POWER

OUT = "D:/dev/esp32-sendspin-speaker/hardware/ui/sendspin-speaker-ui.kicad_sch"
ROOT = "74e7ee0d-6dc4-4bd9-bbf0-04663fc82e38"
TITLE = "ESP32 Sendspin Speaker — front panel (display + buttons)"

HDR = "Connector_PinHeader_2.54mm:PinHeader_1x{n:02d}_P2.54mm_Vertical"

s = Sheet("sendspin-speaker-ui", f"/{ROOT}", pwr_base=600)


def net(pin, name, stub=2.54, bend=None):
    if name in POWER:
        s.attach(pin, name, stub=stub)
    else:
        s.attach(pin, name, stub=stub, kind="label", bend=bend)


# --- J_UI from the main board (same pin order as main/connectors.kicad_sch) ----
J_UI = ["+3V3", "GND", "DISP_SCK", "DISP_MOSI", "DISP_CS", "DISP_DC",
        "BTN1", "BTN3", "BTN4", "BTN5", "BTN6", "LED"]   # LED: already through 330R on the main board
j = s.part("Connector_Generic", "Conn_01x12", "J601", "J_UI", 76.2, 88.9,
           footprint="Connector_JST:JST_XH_B12B-XH-A_1x12_P2.50mm_Vertical")
for i, n in enumerate(J_UI, start=1):
    net(j[str(i)], n, stub=20.32 if n == "GND" else 2.54)
for x, n in ((25.4, "+3V3"), (12.7, "GND")):       # both arrive through J601 only
    s.flag(x, 38.1); s.wire(x, 38.1, x, 43.18); s.power(n, x, 43.18)

# --- SPI display (ST7789 module, e.g. Waveshare 1.47": VCC GND DIN CLK CS DC RST BL) --
d = s.part("Connector_Generic", "Conn_01x08", "J602", "SPI display", 165.1, 76.2,
           footprint=HDR.format(n=8))
for i, n in enumerate(["+3V3", "GND", "DISP_MOSI", "DISP_SCK", "DISP_CS", "DISP_DC",
                       "+3V3", "+3V3"], start=1):        # RST high (software reset), BL on
    net(d[str(i)], n, stub=20.32 if n == "GND" else (12.7 if i in (7, 8) else 2.54))

# --- I2C OLED (SSD1306/SH1106 module: GND VCC SCL SDA) -------------------------
o = s.part("Connector_Generic", "Conn_01x04", "J603", "I2C OLED", 165.1, 127.0,
           footprint=HDR.format(n=4))
net(o["1"], "GND", stub=12.7); net(o["2"], "+3V3", stub=12.7)
net(o["3"], "DISP_SCK"); net(o["4"], "DISP_MOSI")

# --- status LED header: a panel LED wires straight on (its resistor is on the main board)
led = s.part("Connector_Generic", "Conn_01x02", "J604", "LED", 165.1, 152.4,
             footprint=HDR.format(n=2))
net(led["1"], "LED"); net(led["2"], "GND")

# --- buttons to GND (pull-ups on the main board / in the ESP32) -------------------
for k, (btn, what) in enumerate((("BTN1", "Play/Pause"), ("BTN3", "Prev"), ("BTN4", "Next"),
                                 ("BTN5", "Vol -"), ("BTN6", "Vol +"))):
    sw = s.part("Switch", "SW_Push", f"SW60{btn[-1]}", what, 50.8 + 30.48 * k, 175.26,
                footprint="Button_Switch_THT:SW_PUSH_6mm")
    net(sw["1"], btn); net(sw["2"], "GND")

s.text("Front panel\n"
       "Buttons and headers only, so the panel can be swapped for any wiring.\n"
       "Fit J602 for the SPI ST7789 (as on the Audio Kit build) or J603 for an I2C OLED\n"
       "(then fit R105/R106 on the main board). Check the module's pin order before soldering:\n"
       "OLED modules come as GND-VCC-SCL-SDA and VCC-GND-SCL-SDA.\n"
       "ST7789: RST tied high (the driver sends a software reset), backlight always on.\n"
       "Buttons pull to GND; pull-ups are on the main board / in the ESP32.\n"
       "J604: status LED straight on (its 330R is R501 on the main board).", 101.6, 22.86)

s.write(OUT, ROOT, TITLE, paper="A4")
print("ok")
