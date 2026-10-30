"""Draw the front panel board (ui/sendspin-speaker-ui.kicad_sch)."""
import os, sys
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(__file__))
from schgen import Sheet, POWER

OUT = "D:/dev/esp32-sendspin-speaker/hardware/ui/sendspin-speaker-ui.kicad_sch"
ROOT = "74e7ee0d-6dc4-4bd9-bbf0-04663fc82e38"
TITLE = "ESP32 Sendspin Speaker — front panel (display + buttons)"

R0805, C0805, LED0805 = ("Resistor_SMD:R_0805_2012Metric", "Capacitor_SMD:C_0805_2012Metric",
                         "LED_SMD:LED_0805_2012Metric")
HDR = "Connector_PinHeader_2.54mm:PinHeader_1x{n:02d}_P2.54mm_Vertical"

s = Sheet("sendspin-speaker-ui", f"/{ROOT}", pwr_base=600)


def net(pin, name, stub=2.54, bend=None):
    if name in POWER:
        s.attach(pin, name, stub=stub)
    else:
        s.attach(pin, name, stub=stub, kind="label", bend=bend)


# --- J_UI from the main board (same pin order as main/connectors.kicad_sch) ----
J_UI = ["+3V3", "GND", "DISP_SCK", "DISP_MOSI", "DISP_CS", "DISP_DC",
        "BTN1", "BTN3", "BTN4", "BTN5", "BTN6", "LED"]
j = s.part("Connector_Generic", "Conn_01x12", "J601", "J_UI", 76.2, 88.9,
           footprint="Connector_JST:JST_XH_B12B-XH-A_1x12_P2.50mm_Vertical")
for i, n in enumerate(J_UI, start=1):
    net(j[str(i)], n, stub=20.32 if n == "GND" else 2.54)
c = s.part("Device", "C", "C601", "100n", 38.1, 50.8, footprint=C0805)   # at the connector
net(c["1"], "+3V3"); net(c["2"], "GND")
for x, n in ((25.4, "+3V3"), (12.7, "GND")):       # both arrive through J601 only
    s.flag(x, 38.1); s.wire(x, 38.1, x, 43.18); s.power(n, x, 43.18)

# --- SPI display (ST7789 module, e.g. Waveshare 1.47": VCC GND DIN CLK CS DC RST BL) --
d = s.part("Connector_Generic", "Conn_01x08", "J602", "SPI display", 165.1, 76.2,
           footprint=HDR.format(n=8))
for i, n in enumerate(["+3V3", "GND", "DISP_MOSI", "DISP_SCK", "DISP_CS", "DISP_DC",
                       "DISP_RST", "+3V3"], start=1):
    net(d[str(i)], n, stub=20.32 if n == "GND" else (12.7 if i == 8 else 2.54))
r = s.part("Device", "R", "R601", "10k", 203.2, 66.04, footprint=R0805)   # RC reset at power-up
net(r["1"], "+3V3"); net(r["2"], "DISP_RST", bend=(5.08, 0))
r = s.part("Device", "C", "C602", "1u", 228.6, 71.12, footprint=C0805)
net(r["1"], "DISP_RST", bend=(5.08, 0)); net(r["2"], "GND")

# --- I2C OLED (SSD1306/SH1106 module: GND VCC SCL SDA) -------------------------
o = s.part("Connector_Generic", "Conn_01x04", "J603", "I2C OLED", 165.1, 127.0,
           footprint=HDR.format(n=4))
net(o["1"], "GND", stub=12.7); net(o["2"], "+3V3", stub=12.7)
net(o["3"], "DISP_SCK"); net(o["4"], "DISP_MOSI")

# --- buttons to GND (pull-ups on the main board / in the ESP32) -------------------
for k, (btn, what) in enumerate((("BTN1", "Play/Pause"), ("BTN3", "Prev"), ("BTN4", "Next"),
                                 ("BTN5", "Vol -"), ("BTN6", "Vol +"))):
    sw = s.part("Switch", "SW_Push", f"SW60{btn[-1]}", what, 50.8 + 30.48 * k, 175.26,
                footprint="Button_Switch_THT:SW_PUSH_6mm")
    net(sw["1"], btn); net(sw["2"], "GND")

# --- optional status LED on the panel ---------------------------------------------
r = s.part("Device", "R", "R602", "1k", 203.2, 116.84, footprint=R0805)
net(r["1"], "LED", bend=(5.08, 0)); net(r["2"], "LED_A", bend=(5.08, 0))
led = s.part("Device", "LED", "D601", "status", 236.22, 127.0, footprint=LED0805)
net(led["2"], "LED_A"); net(led["1"], "GND")

s.text("Front panel\n"
       "Fit J602 for the SPI ST7789 (as on the Audio Kit build) or J603 for an I2C OLED\n"
       "(then fit R105/R106 on the main board). Check the module's pin order before soldering:\n"
       "OLED modules come as GND-VCC-SCL-SDA and VCC-GND-SCL-SDA.\n"
       "ST7789 reset: R601/C602 RC at power-up (the firmware has no reset pin). Backlight always on.\n"
       "Buttons pull to GND; BTN1 (GPIO36) has its 10k pull-up on the main board.\n"
       "D601/R602 optional (status LED on the panel instead of J_LED).", 101.6, 22.86)

s.write(OUT, ROOT, TITLE, paper="A4")
print("ok")
