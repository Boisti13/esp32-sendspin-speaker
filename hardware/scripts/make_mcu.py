"""Draw the main board's MCU sheet (mcu.kicad_sch)."""
import sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
from schgen import Sheet

OUT = "D:/dev/esp32-sendspin-speaker/hardware/main/mcu.kicad_sch"
ROOT, SHEET = "1294b3cd-656f-456e-a4e5-c0aee204737d", "314e3d3e-7960-4540-b960-f2a0c4541ea0"
FILE_UUID = "892d340b-2040-41ea-b8fb-889fe8777068"
TITLE = "ESP32 Sendspin Speaker — main board — MCU"

R0805, C0805, LED0805 = ("Resistor_SMD:R_0805_2012Metric", "Capacitor_SMD:C_0805_2012Metric",
                         "LED_SMD:LED_0805_2012Metric")
BUTTON = "Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A"

SHAPE = {"U0RXD": "input", "U0TXD": "output", "EN": "input", "IO0": "bidirectional",
         "CHRG": "input", "STDBY": "input", "VBAT_SENSE": "input", "AMP_EN": "output",
         "DISP_SCK": "output", "DISP_MOSI": "bidirectional",
         "DISP_CS": "output", "DISP_DC": "output", "LED": "output"}
for n in ("SPOLP", "SPOLN", "SPORP", "SPORN"):
    SHAPE[n] = "output"
for n in ("BTN1", "BTN3", "BTN4", "BTN5", "BTN6"):
    SHAPE[n] = "input"

# ESP32-A1S pad -> net (None = not connected)
PADS = {1: "GND", 2: "+3V3", 3: "GPIO39", 4: "BTN1", 5: "VBAT_SENSE", 6: "IO0",
        7: "DISP_SCK", 8: "LED", 9: "DISP_MOSI", 10: "DISP_CS", 11: "STDBY", 12: "CHRG",
        13: None, 14: None, 15: None, 16: None, 17: None, 18: None, 19: "GND", 20: "GND",
        21: None, 22: None, 23: "SPORP", 24: "SPORN", 25: "SPOLP", 26: "SPOLN",
        27: None, 28: None, 29: "BTN6", 30: "BTN5", 31: "BTN4", 32: "BTN3",
        33: "DISP_DC", 34: "AMP_EN", 35: "EN", 36: "U0TXD", 37: "U0RXD", 38: "GND"}

s = Sheet("sendspin-speaker-main", f"/{ROOT}/{SHEET}", pwr_base=100)


def hl(pin, net, **kw):
    kind = "hierarchical_label" if net in SHAPE else "label"   # GPIO39: local, spare
    s.attach(pin, net, shape=SHAPE.get(net, "passive"), kind=kind, **kw)


# --- module -----------------------------------------------------------------
u = s.part("lcsc", "ESP32-A1S", "U101", "ESP32-A1S", 80, 100,
           footprint="lcsc:WIRELM-SMD_ESP32-A1S", lcsc="C277945",
           datasheet="https://docs.ai-thinker.com/_media/esp32-a1s_specification.pdf")
for pad, net in PADS.items():
    pin = u[str(pad)]
    if net is None:
        s.no_connect(pin[0], pin[1])
    else:
        # pads 1 and 38 sit next to other pins: longer stubs keep their GND clear of them
        hl(pin, net, stub={1: 10.16, 38: 20.32}.get(pad, 5.08))

# --- supply decoupling (close to pad 2) ---------------------------------------
for i, (ref, val) in enumerate((("C101", "22u"), ("C102", "100n"))):
    c = s.part("Device", "C", ref, val, 150 + 12.7 * i, 45, footprint=C0805)
    hl(c["1"], "+3V3"); hl(c["2"], "GND")

# --- EN: pull-up, RC delay, Reset button ---------------------------------------
r = s.part("Device", "R", "R101", "10k", 190, 45, footprint=R0805)
hl(r["1"], "+3V3"); hl(r["2"], "EN", bend=(5.08, 0))
c = s.part("Device", "C", "C103", "1u", 215, 45, footprint=C0805)
hl(c["1"], "EN", bend=(5.08, 0)); hl(c["2"], "GND")
sw = s.part("Switch", "SW_Push", "SW101", "Reset", 250, 45, footprint=BUTTON)
hl(sw["1"], "EN"); hl(sw["2"], "GND")

# --- pull-ups: input-only GPIO36/39, display CS (strap 15 high), I2C option -----
for i, (ref, val, net, dnp) in enumerate((
        ("R102", "10k", "BTN1", False), ("R103", "10k", "GPIO39", False),
        ("R104", "10k", "DISP_CS", False), ("R105", "4.7k", "DISP_SCK", True),
        ("R106", "4.7k", "DISP_MOSI", True))):
    r = s.part("Device", "R", ref, val, 150 + 22 * i, 90, footprint=R0805, dnp=dnp)
    hl(r["1"], "+3V3"); hl(r["2"], net, bend=(5.08, 0))

# --- Boot button ------------------------------------------------------------
sw = s.part("Switch", "SW_Push", "SW102", "Boot", 160, 135, footprint=BUTTON)
hl(sw["1"], "IO0"); hl(sw["2"], "GND")

# --- status LED on GPIO12 (pull-down keeps the strap low at reset) -------------
r = s.part("Device", "R", "R107", "10k", 195, 135, footprint=R0805)
hl(r["1"], "LED", bend=(5.08, 0)); hl(r["2"], "GND")
r = s.part("Device", "R", "R108", "1k", 220, 135, footprint=R0805)
hl(r["1"], "LED", bend=(5.08, 0))
# LED left of R108: the wire reaches the anode (right pin) without passing the cathode
x, y, _ = r["2"]
d = s.part("Device", "LED", "D101", "green", x - 10.16, y + 7.62, footprint=LED0805)
ax, ay, _ = d["2"]
s.wire(x, y, x, ay); s.wire(x, ay, ax, ay)
hl(d["1"], "GND")

s.text("MCU\n"
       "ESP32-A1S: the codec's I2C (GPIO32/33) and I2S (25/26/27/35, MCLK 0) are inside\n"
       "the module. MIC/LINEIN/HBIAS/MBIAS pads unused.\n"
       "Straps: GPIO12 low at reset (R107), GPIO15 high (R104), GPIO2 low/floating\n"
       "(STDBY via diode on the Power sheet), GPIO0 Boot / auto-reset.\n"
       "R105/R106: fit 4.7k only for an I2C OLED (SCL 14 / SDA 13), leave off for SPI.\n"
       "CHRG (4) / STDBY (2): internal pull-ups in the firmware.\n"
       "C101/C102 next to pad 2 (3V3).", 140, 160)

s.write(OUT, FILE_UUID, TITLE)
print("ok")
