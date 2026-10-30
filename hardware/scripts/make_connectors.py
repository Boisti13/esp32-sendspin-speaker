"""Draw the main board's Connectors sheet (connectors.kicad_sch)."""
import os, sys
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(__file__))
from schgen import Sheet, POWER

OUT = "D:/dev/esp32-sendspin-speaker/hardware/main/connectors.kicad_sch"
ROOT, SHEET = "1294b3cd-656f-456e-a4e5-c0aee204737d", "6d38e623-8931-4aa4-bceb-223bb3823fea"
FILE_UUID = "bb425f65-859b-4413-b82d-4aef79876a03"
TITLE = "ESP32 Sendspin Speaker — main board — Connectors"

HIER = {"DISP_SCK": "input", "DISP_MOSI": "bidirectional", "DISP_CS": "input",
        "DISP_DC": "input", "LED": "input"}
for b in ("BTN1", "BTN3", "BTN4", "BTN5", "BTN6"):
    HIER[b] = "output"

s = Sheet("sendspin-speaker-main", f"/{ROOT}/{SHEET}", pwr_base=500)


def net(pin, name, stub=2.54):
    if name in POWER:
        s.attach(pin, name, stub=stub)
    else:
        s.attach(pin, name, stub=stub, shape=HIER.get(name, "passive"),
                 kind="hierarchical_label" if name in HIER else "label")


# J_UI: the front panel. Pin order is the contract with ui/ (hardware/README.md).
J_UI = ["+3V3", "GND", "DISP_SCK", "DISP_MOSI", "DISP_CS", "DISP_DC",
        "BTN1", "BTN3", "BTN4", "BTN5", "BTN6", "LED_EXT"]   # LED through R501: the panel has no parts
j = s.part("Connector_Generic", "Conn_01x12", "J501", "J_UI", 101.6, 88.9,
           footprint="Connector_JST:JST_XH_B12B-XH-A_1x12_P2.50mm_Vertical")
for i, n in enumerate(J_UI, start=1):
    net(j[str(i)], n, stub=20.32 if n == "GND" else 2.54)   # GND hangs below the labels' reach

# J_LED: off-board status LED (plain LED to LED/GND, or an SK6812 on VBAT_SW)
j = s.part("Connector_Generic", "Conn_01x03", "J502", "J_LED", 127.0, 139.7,
           footprint="Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical")
net(j["1"], "VBAT_SW"); net(j["2"], "LED_EXT"); net(j["3"], "GND")
r = s.part("Device", "R", "R501", "330", 76.2, 152.4, footprint="Resistor_SMD:R_0805_2012Metric")
net(r["1"], "LED"); s.attach(r["2"], "LED_EXT", kind="label", bend=(5.08, 0))

s.text("Connectors\n"
       "J_UI (XH 12) to the front panel: SPI display uses SCK/MOSI/CS/DC; an I2C OLED only\n"
       "SCK = SCL and MOSI = SDA (fit R105/R106 on the MCU sheet). Buttons pull to GND on the panel.\n"
       "J_UI pin 12 and J_LED (XH 3) carry the status LED through R501 330R: a plain LED wires\n"
       "straight to LED/GND (panel header or J_LED), or an SK6812 on J_LED (power from VBAT_SW).\n"
       "Pin orders are the contract with the front panel (hardware/README.md).", 38.1, 30.48)

s.write(OUT, FILE_UUID, TITLE)
print("ok")
