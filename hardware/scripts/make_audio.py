"""Draw the main board's Audio sheet (audio.kicad_sch)."""
import os, sys
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(__file__))
from schgen import Sheet, POWER

OUT = "D:/dev/esp32-sendspin-speaker/hardware/main/audio.kicad_sch"
ROOT, SHEET = "1294b3cd-656f-456e-a4e5-c0aee204737d", "2ec6238e-1f14-4f05-8074-2972fdfd144b"
FILE_UUID = "b9ebad30-a277-4aba-afcb-db365a545c3c"
TITLE = "ESP32 Sendspin Speaker — main board — Audio"

R0805, C0805 = "Resistor_SMD:R_0805_2012Metric", "Capacitor_SMD:C_0805_2012Metric"
XH2 = "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical"
HIER = {n: "input" for n in ("HPOUTL", "HPOUTR", "SPOLP", "SPOLN", "SPORP", "SPORN", "AMP_EN")}
HIER["HP_DET"] = "output"

s = Sheet("sendspin-speaker-main", f"/{ROOT}/{SHEET}", pwr_base=400)


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


def hpart(ref, value, x, y, left, right, fp, lib="Device", name="R"):
    """Series part lying flat: R and C are vertical symbols, so draw them as a short chain."""
    p = s.part(lib, name, ref, value, x, y, footprint=fp,
               texts={"Reference": (2.54, -1.27, "left"), "Value": (2.54, 1.27, "left")})
    net(p["1"], left, bend=(-5.08, 0)); net(p["2"], right, bend=(-5.08, 0))
    return p


# --- two NS4150B, bridged outputs ------------------------------------------------
n = 1
for side, y0, (inp, inn), ref in (("L", 63.5, ("SPOLP", "SPOLN"), 401),
                                  ("R", 137.16, ("SPORP", "SPORN"), 402)):
    u = s.part("lcsc", "NS4150", f"U{ref}", "NS4150B", 165.1, y0,
               footprint="lcsc:MSOP-8_L3.0-W3.0-P0.65-LS5.0-BL", lcsc="C189961")
    net(u["1"], "AMP_EN", stub=7.62)
    net(u["2"], f"BYP_{side}", stub=7.62)
    net(u["3"], f"IN{side}_P", stub=7.62); net(u["4"], f"IN{side}_N", stub=7.62)
    net(u["6"], "VBAT_SW", stub=5.08); net(u["7"], "GND", stub=15.24)
    net(u["8"], f"SPK{side}_P", stub=7.62); net(u["5"], f"SPK{side}_N", stub=7.62)
    # input network: Cin 100n + Rin 100k per leg (gain 240k/Rin = 2.4, -3 dB at 16 Hz)
    b = 400 if side == "L" else 410          # C401..C405 / R401..R402 left, 41x right
    for k, (src, leg) in enumerate(((inp, "P"), (inn, "N"))):
        yy = y0 - 12.7 + 22.86 * k
        hpart(f"C{b + k + 1}", "100n", 63.5, yy, src, f"{side}{leg}_C", C0805)
        hpart(f"R{b + k + 1}", "100k", 101.6, yy, f"{side}{leg}_C", f"IN{side}_{leg}", R0805)
    two("Device", "C", f"C{b + 3}", "1u", 132.08, y0 + 22.86, f"BYP_{side}", "GND", C0805)
    two("Device", "C", f"C{b + 4}", "10u", 215.9, y0 - 15.24, "VBAT_SW", "GND", C0805)
    two("Device", "C", f"C{b + 5}", "1u", 228.6, y0 - 15.24, "VBAT_SW", "GND", C0805)
    j = s.part("Connector_Generic", "Conn_01x02", f"J{ref}", f"J_SPK_{side}", 254.0, y0,
               footprint=XH2)
    net(j["1"], f"SPK{side}_P"); net(j["2"], f"SPK{side}_N")

two("Device", "R", "R421", "100k", 132.08, 101.6, "AMP_EN", "GND", R0805)   # amps off while booting
two("Device", "C_Polarized", "C421", "470u", 241.3, 101.6, "VBAT_SW", "GND",
    "Capacitor_SMD:CP_Elec_8x10")

# --- headphones: PJ-320D on HPOUTL/HPOUTR through 47 uF (the codec's outputs sit at VREF) ---
hpart("C422", "47u", 63.5, 185.42, "HPOUTL", "HPL", C0805)
hpart("C423", "47u", 63.5, 205.74, "HPOUTR", "HPR", C0805)
jk = s.part("lcsc", "PJ-320D", "J403", "PJ-320D", 165.1, 195.58,
            footprint="lcsc:AUDIO-SMD_PJ-320D-1", lcsc="C431535",
            texts={"Reference": (0, -8.89, ""), "Value": (0, 10.16, "")})
net(jk["1"], "GND", stub=12.7)       # sleeve
net(jk["4"], "HPL", stub=5.08)       # tip      } pinout from a third-party page:
net(jk["3"], "HPR", stub=5.08)       # ring     } verify against the datasheet/part
net(jk["2"], "HP_DET", stub=5.08)    # detect   }

s.text("Audio\n"
       "NS4150B x2 from VBAT_SW, outputs bridged (BTL): no speaker wire to GND, no shared return.\n"
       "Inputs: the module's differential speaker outputs (SPOL/SPOR) through 100n + 100k per leg;\n"
       "  gain = 240k / Rin = 2.4 (raise it in the codec, or lower Rin to 47k for 5.1).\n"
       "CTRL = AMP_EN (GPIO21, high = on); R421 keeps the amps off while the ESP32 boots.\n"
       "Supply: 10u + 1u at each amp, C421 470u bulk next to them.\n"
       "Headphones: HPOUTL/R through 47u (the codec's outputs sit at VREF), -3 dB ~ 100 Hz at 32 R.\n"
       "PJ-320D pinout (1 sleeve, 4 tip, 3 ring, 2 detect) is from a third-party listing:\n"
       "  CHECK it against the part before ordering. HP_DET pull-up is on the MCU sheet (R103).",
       38.1, 228.6)

s.write(OUT, FILE_UUID, TITLE, paper="A3")
print("ok")
