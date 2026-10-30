"""JLCPCB production files for one board: Gerber/drill ZIP, BOM and CPL in JLC's formats.

    python -I hardware/scripts/jlc.py main
Writes hardware/production/<board>/ (git-ignored; files go on a GitHub release).
Only parts with an LCSC number go into BOM and CPL; the rest (ESP32-A1S, JST connectors)
are hand-soldered.
"""
import csv, os, re, subprocess, sys, zipfile

CLI = "D:/Programs/KiCad/10.0/bin/kicad-cli.exe"
HW = "D:/dev/esp32-sendspin-speaker/hardware"
HAND = {"C277945"}                   # ESP32-A1S: JLC doesn't stock it
name = sys.argv[1]
proj = {"main": "main/sendspin-speaker-main", "ui": "ui/sendspin-speaker-ui",
        "usb": "usb/sendspin-speaker-usb"}[name]
pcb, sch = f"{HW}/{proj}.kicad_pcb", f"{HW}/{proj}.kicad_sch"
out = f"{HW}/production/{name}"
gdir = f"{out}/gerber"
os.makedirs(gdir, exist_ok=True)
for f in os.listdir(gdir):
    os.remove(os.path.join(gdir, f))


def run(*args):
    r = subprocess.run([CLI, *args], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"{' '.join(args[:3])} failed: {r.stdout[-800:]}{r.stderr[-800:]}")
    return r.stdout


# Gerbers + drill
run("pcb", "export", "gerbers", "--layers",
    "F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts",
    "--subtract-soldermask", "--no-x2", "-o", gdir + "/", pcb)
run("pcb", "export", "drill", "--format", "excellon", "--excellon-units", "mm", "-o", gdir + "/", pcb)
zpath = f"{out}/sendspin-speaker-{name}-gerber.zip"
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(os.listdir(gdir)):
        z.write(os.path.join(gdir, f), f)

# BOM from the schematic, grouped, only parts JLC places
tmp = f"{out}/bom-kicad.csv"
run("sch", "export", "bom", "--fields", "Value,Reference,Footprint,LCSC,${QUANTITY}",
    "--labels", "Value,Reference,Footprint,LCSC,Qty", "--group-by", "Value,Footprint,LCSC",
    "--exclude-dnp", "-o", tmp, sch)
placed, rows = set(), []
for r in csv.DictReader(open(tmp, encoding="utf-8-sig")):
    code = r["LCSC"].strip()
    if not code or code in HAND:
        continue
    refs = []
    for x in r["Reference"].split(","):                  # KiCad writes ranges (R101-R104): JLC wants each
        x = x.strip()
        m = re.fullmatch(r"([A-Z]+)(\d+)-[A-Z]*(\d+)", x)
        refs += [f"{m.group(1)}{i}" for i in range(int(m.group(2)), int(m.group(3)) + 1)] if m else [x]
    placed.update(refs)
    rows.append([r["Value"], ",".join(refs), r["Footprint"].split(":")[-1], code])
os.remove(tmp)
with open(f"{out}/sendspin-speaker-{name}-bom.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"]); w.writerows(rows)

# CPL from the board, same parts
tmp = f"{out}/pos-kicad.csv"
run("pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both",
    "--exclude-dnp", "-o", tmp, pcb)
cpl = []
for r in csv.DictReader(open(tmp, encoding="utf-8-sig")):
    if r["Ref"] in placed:
        cpl.append([r["Ref"], f'{float(r["PosX"]):.3f}mm', f'{float(r["PosY"]):.3f}mm',
                    "Top" if r["Side"].lower().startswith("top") else "Bottom",
                    f'{float(r["Rot"]):.1f}'])
os.remove(tmp)
with open(f"{out}/sendspin-speaker-{name}-cpl.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"]); w.writerows(cpl)

missing = placed - {c[0] for c in cpl}
print(f"{zpath}\nBOM: {len(rows)} lines, {len(placed)} parts; CPL: {len(cpl)} parts"
      + (f"; NOT ON BOARD: {sorted(missing)}" if missing else ""))
