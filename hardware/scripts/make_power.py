"""Draw the main board's Power sheet (power.kicad_sch)."""
import os, sys
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(__file__))
from schgen import Sheet, POWER

OUT = "D:/dev/esp32-sendspin-speaker/hardware/main/power.kicad_sch"
ROOT, SHEET = "1294b3cd-656f-456e-a4e5-c0aee204737d", "7a01c100-f9c5-45b7-af6b-1f2f2d3d81d1"
FILE_UUID = "9ff359a6-4225-41a4-bf38-76fa95de203b"
TITLE = "ESP32 Sendspin Speaker — main board — Power"

R0805, C0805, LED0805 = ("Resistor_SMD:R_0805_2012Metric", "Capacitor_SMD:C_0805_2012Metric",
                         "LED_SMD:LED_0805_2012Metric")
XH = "Connector_JST:JST_XH_B{n}B-XH-A_1x{n:02d}_P2.50mm_Vertical"

HIER = {"VBUS": "input", "CHRG": "output", "STDBY": "output", "VBAT_SENSE": "output"}

s = Sheet("sendspin-speaker-main", f"/{ROOT}/{SHEET}", pwr_base=200)


def net(pin, name, bend=None, stub=2.54):
    """End a pin in a power symbol, hierarchical label or local label, whichever fits."""
    if name in POWER:
        s.attach(pin, name, stub=stub)
    elif name in HIER:
        s.attach(pin, name, stub=stub, shape=HIER[name], bend=bend)
    else:
        s.attach(pin, name, stub=stub, kind="label", bend=bend)


def two(lib, name, ref, value, x, y, top, bottom, fp, **kw):
    """Vertical two-pin part between two nets (labels bend right)."""
    p = s.part(lib, name, ref, value, x, y, footprint=fp, **kw)
    net(p["1"], top, bend=(5.08, 0)); net(p["2"], bottom, bend=(5.08, 0))
    return p


# --- charger -------------------------------------------------------------------
u = s.part("Battery_Management", "TP4056-42-ESOP8", "U201", "TP4056", 80.01, 80.01,
           footprint="Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm",
           datasheet="https://www.lcsc.com/datasheet/C16581.pdf")
net(u["4"], "VBUS", stub=5.08)           # VCC
net(u["8"], "VBUS")                      # CE: always enabled
net(u["1"], "GND", stub=12.7)           # TEMP: no NTC (long stub keeps GND clear of PROG)
net(u["2"], "PROG")
net(u["5"], "VBAT")                      # BAT
net(u["3"], "GND"); s.wire(*u["9"][:2], *u["3"][:2])   # GND, exposed pad tied to it
net(u["7"], "CHRG_N", stub=5.08)
net(u["6"], "STDBY_N", stub=5.08)
two("Device", "R", "R201", "2.4k", 110.49, 80.01, "PROG", "GND", R0805)    # ~500 mA
two("Device", "C", "C201", "10u", 50.8, 55.88, "VBUS", "GND", C0805)
two("Device", "C", "C202", "10u", 125.73, 80.01, "VBAT", "GND", C0805)

# --- charge LEDs (on board or via J_CHG) and GPIO read-back --------------------
for i, (sig, colour, led, res, dio) in enumerate((("CHRG", "red", "D201", "R202", "D203"),
                                                  ("STDBY", "green", "D202", "R203", "D204"))):
    y = 125.73 + 25.4 * i
    d = s.part("Device", "LED", led, colour, 40.64, y, footprint=LED0805)
    net(d["2"], "VBUS"); net(d["1"], f"{sig}_K")
    r = s.part("Device", "R", res, "1k", 76.2, y + 3.81, footprint=R0805)
    net(r["1"], f"{sig}_K", bend=(5.08, 0)); net(r["2"], f"{sig}_N", bend=(5.08, 0))
    b = s.part("Diode", "BAT54W", dio, "BAT54W", 116.84, y,
               footprint="Package_TO_SOT_SMD:SOT-323_SC-70")
    net(b["3"], f"{sig}_N"); net(b["1"], sig); s.no_connect(*b["2"][:2])
j = s.part("Connector_Generic", "Conn_01x03", "J203", "J_CHG", 40.64, 185.42,
           footprint=XH.format(n=3))
net(j["1"], "VBUS"); net(j["2"], "CHRG_K"); net(j["3"], "STDBY_K")

# --- battery and protection (DW01A + FS8205A in the negative lead) -------------
j = s.part("Connector_Generic", "Conn_01x02", "J201", "J_BAT", 180.34, 63.5,
           footprint="Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical")
net(j["1"], "VBAT"); net(j["2"], "BAT_N")
u = s.part("Battery_Management", "DW01A", "U202", "DW01A", 220.98, 63.5,
           footprint="Package_TO_SOT_SMD:SOT-23-6")
net(u["5"], "DW_VCC"); net(u["6"], "BAT_N"); net(u["2"], "DW_CS")
net(u["1"], "OD", bend=(-5.08, 0)); net(u["3"], "OC", bend=(5.08, 0)); s.no_connect(*u["4"][:2])
two("Device", "R", "R204", "100", 254.0, 50.8, "VBAT", "DW_VCC", R0805)
two("Device", "C", "C203", "100n", 271.78, 50.8, "DW_VCC", "BAT_N", C0805)
two("Device", "R", "R205", "1k", 254.0, 76.2, "DW_CS", "GND", R0805)
q = s.part("lcsc", "FS8205A_C2830320", "Q201", "FS8205A", 220.98, 101.6,
           footprint="lcsc:SOT-23-6_L2.9-W1.6-P0.95-LS2.8-BR", lcsc="C2830320")
net(q["1"], "BAT_N"); net(q["6"], "OD")      # discharge FET on the cell side
net(q["3"], "GND"); net(q["4"], "OC")        # charge FET on the system side
net(q["2"], "FET_D"); net(q["5"], "FET_D")

# --- load sharing: USB feeds the load through SS34, the cell through AO3401A ---
d = s.part("Diode", "SS34", "D205", "SS34", 190.5, 147.32, footprint="Diode_SMD:D_SMA")
net(d["2"], "VBUS"); net(d["1"], "VBAT_LS")
q = s.part("Transistor_FET", "AO3401A", "Q202", "AO3401A", 190.5, 175.26,
           footprint="Package_TO_SOT_SMD:SOT-23")
net(q["1"], "VBUS")                          # gate: off while USB is present
net(q["3"], "VBAT"); net(q["2"], "VBAT_LS", bend=(5.08, 0))  # drain at the cell, source at the load
two("Device", "R", "R206", "100k", 218.44, 160.02, "VBUS", "GND", R0805)
two("Device", "C", "C204", "10u", 236.22, 160.02, "VBAT_LS", "GND", C0805)

# --- on/off: on-board slide switch, panel switch on J_SW, or bridge JP201 ------
sw = s.part("lcsc", "MSK12C02", "SW201", "MSK12C02", 287.02, 154.94,
            footprint="lcsc:SW-TH_MSK12C02", lcsc="C431540",
            texts={"Reference": (12.7, -2.54, "left"), "Value": (0, 8.89, "")})
net(sw["1"], "VBAT_LS", stub=5.08, bend=(-5.08, 0)); net(sw["2"], "VBAT_SW")
s.no_connect(*sw["3"][:2]); net(sw["4"], "GND")   # shell/mounting pads to GND
j = s.part("Connector_Generic", "Conn_01x02", "J202", "J_SW", 287.02, 180.34,
           footprint=XH.format(n=2))
net(j["1"], "VBAT_LS"); net(j["2"], "VBAT_SW", stub=15.24)  # rail symbol clear of pin 1's label
jp = s.part("Jumper", "SolderJumper_2_Open", "JP201", "SW bypass", 287.02, 200.66,
            footprint="Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm", in_bom=False)
net(jp["1"], "VBAT_LS"); net(jp["2"], "VBAT_SW")

# --- 3.3 V -------------------------------------------------------------------------
u = s.part("Regulator_Linear", "AP2112K-3.3", "U203", "AP2112K-3.3", 345.44, 80.01,
           footprint="Package_TO_SOT_SMD:SOT-23-5",
           texts={"Reference": (0, -8.89, ""), "Value": (0, 10.16, "")})
net(u["1"], "VBAT_SW")                     # VIN
vx, vy, _ = u["1"]; ex, ey, _ = u["3"]      # EN tied to VIN
s.wire(ex, ey, vx - 2.54, ey); s.wire(vx - 2.54, ey, vx - 2.54, vy); s.junction(vx - 2.54, vy)
net(u["2"], "GND"); net(u["5"], "+3V3"); s.no_connect(*u["4"][:2])
two("Device", "C", "C205", "10u", 322.58, 99.06, "VBAT_SW", "GND", C0805)
two("Device", "C", "C206", "10u", 370.84, 99.06, "+3V3", "GND", C0805)

# --- battery voltage: divider on the cell (VBAT_SW reads USB's 4.6 V while charging)
two("Device", "R", "R207", "470k", 330.2, 147.32, "VBAT", "VBAT_SENSE", R0805)
two("Device", "R", "R208", "470k", 330.2, 172.72, "VBAT_SENSE", "GND", R0805)
two("Device", "C", "C207", "100n", 355.6, 172.72, "VBAT_SENSE", "GND", C0805)

# --- power flags: nets fed only through passives or from another sheet ---------
for x, n in ((152.4, "BAT_N"), (172.72, "DW_VCC"), (193.04, "VBAT_SW"), (213.36, "GND")):
    y = 27.94
    s.flag(x, y)
    s.wire(x, y, x, y + 5.08)
    if n in POWER:
        s.power(n, x, y + 5.08)
    else:
        s.label("label", n, x, y + 5.08, (1, 0))

s.text("Power\n"
       "TP4056: R201 2.4k = ~500 mA. CE to VBUS, TEMP to GND (no NTC).\n"
       "Charge LEDs: on board (D201 red, D202 green) or off board on J_CHG; R202/R203 serve both.\n"
       "D203/D204 (BAT54W) let GPIO4/GPIO2 see CHRG/STDBY low without VBUS reaching the pins.\n"
       "  Firmware: charging = CHRG low and STDBY high; full = STDBY low and CHRG high; else no USB.\n"
       "Protection in the negative lead: BAT_N = cell minus, GND = P- (system ground).\n"
       "Load sharing: with USB, Q202 is off and the load runs from VBUS through D205;\n"
       "  without USB, Q202 connects the cell. VBAT_LS = load side before the switch.\n"
       "On/off: fit SW201, or a panel switch on J_SW, or bridge JP201. The cell keeps charging when off.\n"
       "Battery sense on the cell (2x 470k, ~4.5 uA): VBAT_SW would read 4.6 V from USB while charging.\n"
       "J_BAT: check the cell's polarity before plugging in.", 25.4, 228.6)

s.write(OUT, FILE_UUID, TITLE, paper="A3")
print("ok")
