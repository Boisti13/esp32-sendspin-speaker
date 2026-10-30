"""Autoroute a board with Freerouting and pour GND again.

    D:/Programs/KiCad/10.0/bin/python.exe -u hardware/scripts/route.py main [passes]

1. export the board without its pours to Specctra DSN,
2. run Freerouting's jar with a portable Java 25 (~/.local/java, ~/.local/freerouting;
   the 2.5.0 native CLI build crashes while routing),
3. import the session (tracks and vias), pour GND on both layers again, save.
Existing tracks are kept and routed around. KiCad must be closed.
"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
from pcbplace import Board

HW = "D:/dev/esp32-sendspin-speaker/hardware"
BOARDS = {"main": (f"{HW}/main/sendspin-speaker-main.kicad_pcb", 100.0, 100.0, 100.0, 58.0),
          "ui": (f"{HW}/ui/sendspin-speaker-ui.kicad_pcb", 100.0, 100.0, 75.0, 45.0),
          "usb": (f"{HW}/usb/sendspin-speaker-usb.kicad_pcb", 100.0, 100.0, 32.0, 22.0)}
JAVA = os.path.expanduser("~/.local/java/jdk-25.0.5+8-jre/bin/java.exe")
FREEROUTING = os.path.expanduser("~/.local/freerouting/2.5.0/freerouting-2.5.0.jar")

name = sys.argv[1]
passes = sys.argv[2] if len(sys.argv) > 2 else "40"
path, x0, y0, w, h = BOARDS[name]
work = os.path.join(os.environ.get("TEMP", "."), f"route-{name}")
os.makedirs(work, exist_ok=True)
dsn, ses = os.path.join(work, f"{name}.dsn"), os.path.join(work, f"{name}.ses")

b = pcbnew.LoadBoard(path)
keep = [z for z in b.Zones()]
for z in keep:
    b.Remove(z)                       # pours out of the way; kept referenced (removing frees nothing yet)
if not pcbnew.ExportSpecctraDSN(b, dsn):
    sys.exit("DSN export failed")
print("exported", dsn)

r = subprocess.run([JAVA, "-Djava.awt.headless=true", "-jar", FREEROUTING, "-de", dsn, "-do", ses,
                    "-mp", passes, "-l", "en", "--gui.enabled=false"],
                   capture_output=True, text=True, stdin=subprocess.DEVNULL, cwd=work)
print("\n".join(r.stdout.splitlines()[-8:]))
if r.returncode != 0 or not os.path.exists(ses):
    sys.exit(f"freerouting failed ({r.returncode}): {r.stderr[-2000:]}")

B = Board(path, x0, y0, w, h)
if not pcbnew.ImportSpecctraSES(B.b, ses):
    sys.exit("SES import failed")

# Freerouting leaves vias behind that only one track reaches: remove them
tracks = [t for t in B.b.GetTracks() if t.GetClass() == "PCB_TRACK"]
pads = [p for f in B.b.GetFootprints() for p in f.Pads()]
gone = 0
for v in [t for t in B.b.GetTracks() if t.GetClass() == "PCB_VIA"]:
    pos, net, r = v.GetPosition(), v.GetNetCode(), v.GetWidth(pcbnew.F_Cu) / 2
    near = lambda q: (q.x - pos.x) ** 2 + (q.y - pos.y) ** 2 <= r * r
    layers = {t.GetLayer() for t in tracks
              if t.GetNetCode() == net and (near(t.GetStart()) or near(t.GetEnd()))}
    on_pad = any(p.GetNetCode() == net and p.HitTest(pos) for p in pads)
    if len(layers) < 2 and not on_pad:    # reaches one layer only: the via does nothing
        B.trash.append(v); B.b.Remove(v); gone += 1
print("dangling vias removed:", gone)
B.gnd_pour()
B.save()
print("routed and saved", path)
