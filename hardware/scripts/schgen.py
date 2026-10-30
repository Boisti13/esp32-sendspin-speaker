"""Draft generator for KiCad 10 schematic sheets (used for the first draft of each sheet).

A sheet is generated once; after that it is edited in KiCad and never regenerated,
or the hand edits are lost. Usage: see make_mcu.py.
"""
import re, uuid

KICAD = "D:/Programs/KiCad/10.0/share/kicad/symbols"
PROJECT_LIBS = {
    "lcsc": "D:/dev/esp32-sendspin-speaker/hardware/lib/lcsc.kicad_sym",
    "sendspin-speaker": "D:/dev/esp32-sendspin-speaker/hardware/lib/sendspin-speaker.kicad_sym",
}
FONT = "(effects (font (size 1.27 1.27))"
U = lambda: str(uuid.uuid4())
r2 = lambda v: round(v, 2)
g = lambda v: round(round(v / 1.27) * 1.27, 2)  # 50 mil connection grid


def _block(text, start):
    depth = 0
    for j in range(start, len(text)):
        if text[j] == "(":
            depth += 1
        elif text[j] == ")":
            depth -= 1
            if depth == 0:
                return text[start:j + 1]
    raise ValueError("unbalanced")


def _children(blk):
    """Top-level child blocks of an s-expression block, as (start, end) spans."""
    out, depth, start = [], 0, None
    for i, ch in enumerate(blk):
        if ch == "(":
            depth += 1
            if depth == 2:
                start = i
        elif ch == ")":
            if depth == 2:
                out.append((start, i + 1))
            depth -= 1
    return out


def _raw_symbol(lib, name):
    path = PROJECT_LIBS.get(lib, f"{KICAD}/{lib}.kicad_sym")
    t = open(path, encoding="utf-8").read()
    m = re.search(r'\n\s*\(symbol "' + re.escape(name) + r'"', t)
    if not m:
        raise KeyError(f"{lib}:{name}")
    blk = _block(t, m.start() + t[m.start():].index("("))
    ext = re.search(r'\(extends "([^"]+)"\)', blk)
    if not ext:
        return blk
    # derived symbol: parent's graphics and pins, the child's own properties
    parent = _raw_symbol(lib, ext.group(1))
    props = [blk[a:b] for a, b in _children(blk) if blk[a:b].startswith("(property")]
    keep = [parent[a:b] for a, b in _children(parent) if not parent[a:b].startswith("(property")]
    keep = [k.replace(f'(symbol "{ext.group(1)}_', f'(symbol "{name}_') for k in keep]
    return f'(symbol "{name}"\n' + "\n".join(props + keep) + "\n)"


def load_symbol(lib, name):
    blk = _raw_symbol(lib, name)
    blk = blk.replace(f'(symbol "{name}"', f'(symbol "{lib}:{name}"', 1)
    texts = {}
    for k in ("Reference", "Value"):
        i = blk.find(f'(property "{k}"')
        if i < 0:
            continue
        prop = _block(blk, i)
        m = re.search(r'\(at ([-\d.]+) ([-\d.]+) (\d+)\)', prop)
        just = re.search(r'\(justify ([^)]*)\)', prop)
        texts[k] = (float(m.group(1)), float(m.group(2)), int(m.group(3)), just.group(1) if just else "")
    pins = {}  # number -> (x, y, angle, unit); unit 0 = shared by all units
    for m in re.finditer(r'\(symbol "' + re.escape(name) + r'_(\d+)_(\d+)"', blk):
        unit, sub = int(m.group(1)), _block(blk, m.start())
        for px, py, ang, num in re.findall(
                r'\(pin \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+) (\d+)\).*?\(number "([^"]+)"', sub, re.S):
            pins.setdefault(num, (float(px), float(py), int(ang), unit))
    return blk, pins, texts


# rail -> power-library symbol drawn for it (VBUS is a hierarchical signal, not a rail here)
POWER = {"+3V3": "+3V3", "GND": "GND", "VBAT": "+BATT", "VBAT_SW": "+BATT", "+3V3_USB": "+3V3"}

# pin angle -> direction a wire leaves the connection point (screen coords, y down)
AWAY = {0: (-1, 0), 180: (1, 0), 90: (0, 1), 270: (0, -1)}


class Sheet:
    def __init__(self, project, path, pwr_base=0):
        self.project, self.path, self.pwr_base = project, path, pwr_base  # path: "/root/sheet"
        self.libs, self.items, self.pwr = {}, [], 0

    def _lib(self, lib, name):
        key = f"{lib}:{name}"
        if key not in self.libs:
            self.libs[key] = load_symbol(lib, name)
        return self.libs[key][1]

    def _texts(self, lib, name):
        return self.libs[f"{lib}:{name}"][2]

    def part(self, lib, name, ref, value, x, y, footprint="", lcsc="", dnp=False,
             datasheet="~", in_bom=True, hide_ref=False, text_lib=True, texts=None, unit=1):
        x, y = g(x), g(y)
        pins = {n: p[:3] for n, p in self._lib(lib, name).items() if p[3] in (0, unit)}
        is_pwr = ref.startswith("#")
        horizontal = all(a in (0, 180) for _, _, a in pins.values()) and len(pins) == 2
        # R/C: texts beside the part read better than KiCad's value-inside-the-body default
        use_lib = text_lib and not (lib == "Device" and name in ("R", "C"))
        lib_texts = self._texts(lib, name) if use_lib else {}
        just_of, angle_of = {}, {}
        if texts:  # explicit screen offsets: {"Reference": (dx, dy, justify), ...}
            props = []
            for k, v, hide in (("Reference", ref, hide_ref), ("Value", value, False)):
                dx, dy, j = texts[k]
                props.append((k, v, x + dx, y + dy, hide)); just_of[k] = j
        elif lib_texts.get("Reference") and lib_texts.get("Value"):  # where the library puts them
            props = []
            for k, v, hide in (("Reference", ref, hide_ref), ("Value", value, False)):
                tx, ty, ang, j = lib_texts[k]
                props.append((k, v, x + tx, y - ty, hide)); just_of[k] = j; angle_of[k] = ang
        elif horizontal:  # 2-pin part lying flat (LED, button): texts above and below, centred
            props = [("Reference", ref, x, y - 5.08, hide_ref), ("Value", value, x, y + 3.81, False)]
        else:
            props = [("Reference", ref, x + 2.54, y - 1.27, hide_ref),
                     ("Value", value, x + 2.54, y + 1.27, False)]
        props += [("Footprint", footprint, x, y, True), ("Datasheet", datasheet, x, y, True)]
        if lcsc:
            props.append(("LCSC", lcsc, x, y, True))
        if is_pwr:  # GND-like symbols hang down: value below; supplies point up: value above
            down = name in ("GND", "GNDA", "GNDD")
            props = [("Reference", ref, x, y + (6.35 if not down else -6.35), True),
                     ("Value", value, x, y + (3.81 if down else -3.81), down),  # GND text hidden: the symbol says it
                     ("Footprint", "", x, y, True), ("Datasheet", "", x, y, True)]
        s = (f'(symbol (lib_id "{lib}:{name}") (at {r2(x)} {r2(y)} 0) (unit {unit}) (exclude_from_sim no) '
             f'(in_bom {"no" if is_pwr or not in_bom else "yes"}) (on_board {"no" if is_pwr else "yes"}) '
             f'(dnp {"yes" if dnp else "no"}) (uuid "{U()}")\n')
        for k, v, px, py, hide in props:
            if k in just_of:
                just = f" (justify {just_of[k]})" if just_of[k] else ""
            else:
                just = (" (justify left)" if k in ("Reference", "Value") and not is_pwr and not horizontal
                        else "")
            s += (f'  (property "{k}" "{v}" (at {r2(px)} {r2(py)} {angle_of.get(k, 0)}) {FONT}{just}'
                  f'{" (hide yes)" if hide else ""}))\n')
        for num in pins:
            s += f'  (pin "{num}" (uuid "{U()}"))\n'
        s += (f'  (instances (project "{self.project}" (path "{self.path}" '
              f'(reference "{ref}") (unit {unit}))))\n)\n')
        self.items.append(s)
        return {n: (r2(x + px), r2(y - py), a) for n, (px, py, a) in pins.items()}

    def power(self, net, x, y):
        """Power symbol; the net is named by its value (rails KiCad has no symbol for
        borrow +BATT / +3V3 graphics)."""
        self.pwr += 1
        self.part("power", POWER[net], f"#PWR{self.pwr_base + self.pwr:04d}", net, x, y)

    def flag(self, x, y):
        self.pwr += 1
        self.part("power", "PWR_FLAG", f"#FLG{self.pwr_base + self.pwr:04d}", "PWR_FLAG", x, y)

    def wire(self, x1, y1, x2, y2):
        x1, y1, x2, y2 = g(x1), g(y1), g(x2), g(y2)
        self.items.append(f'(wire (pts (xy {r2(x1)} {r2(y1)}) (xy {r2(x2)} {r2(y2)})) '
                          f'(stroke (width 0) (type default)) (uuid "{U()}"))\n')

    def label(self, kind, name, x, y, direction, shape="passive"):
        ang, just = {(-1, 0): (180, "right"), (1, 0): (0, "left"),
                     (0, -1): (90, "left"), (0, 1): (270, "right")}[direction]
        extra = f"(shape {shape}) " if kind == "hierarchical_label" else ""
        self.items.append(f'({kind} "{name}" {extra}(at {r2(x)} {r2(y)} {ang}) {FONT} '
                          f'(justify {just}{"" if kind == "hierarchical_label" else " bottom"})) '
                          f'(uuid "{U()}"))\n')

    def junction(self, x, y):
        self.items.append(f'(junction (at {r2(g(x))} {r2(g(y))}) (diameter 0) (color 0 0 0 0) '
                          f'(uuid "{U()}"))\n')

    def no_connect(self, x, y):
        self.items.append(f'(no_connect (at {r2(x)} {r2(y)}) (uuid "{U()}"))\n')

    def text(self, s, x, y, size=1.27):
        s = s.replace('"', '\\"').replace("\n", "\\n")
        self.items.append(f'(text "{s}" (exclude_from_sim no) (at {r2(x)} {r2(y)} 0) '
                          f'(effects (font (size {size} {size})) (justify left top)) (uuid "{U()}"))\n')

    def attach(self, pin, net, stub=2.54, kind="hierarchical_label", shape="passive", bend=None):
        """Wire a stub off a pin and end it in a label or power symbol.
        bend: optional (dx, dy) second segment, e.g. sideways after a vertical stub."""
        x, y, a = pin
        dx, dy = AWAY[a]
        ex, ey = x + dx * stub, y + dy * stub
        if net in POWER:
            if a in (0, 180):  # side pin: stub out, symbol at its end
                self.wire(x, y, ex, ey)
                self.power(net, ex, ey)
            else:              # top/bottom pin: symbol right on it
                self.power(net, x, y)
            return
        self.wire(x, y, ex, ey)
        d = (dx, dy)
        if bend:
            self.wire(ex, ey, ex + bend[0], ey + bend[1])
            ex, ey = ex + bend[0], ey + bend[1]
            d = (1 if bend[0] > 0 else -1, 0) if bend[0] else (0, 1 if bend[1] > 0 else -1)
        self.label(kind, net, ex, ey, d, shape)

    def write(self, out, file_uuid, title, paper="A4"):
        s = (f'(kicad_sch (version 20250114) (generator "eeschema") (generator_version "9.0")\n'
             f'(uuid "{file_uuid}") (paper "{paper}")\n'
             f'(title_block (title "{title}") (date "2026-10-30") (rev "A"))\n(lib_symbols\n')
        for blk, _, _ in self.libs.values():
            s += blk + "\n"
        s += ")\n" + "".join(self.items) + ")\n"
        open(out, "w", encoding="utf-8", newline="\n").write(s)
