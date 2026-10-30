"""Write the LCSC part numbers (checked on lcsc.com, 2026-10-30) into the main board's
schematic symbols, so the JLC BOM comes straight from KiCad.

    python -I hardware/scripts/lcsc_fields.py
KiCad closed. Through-hole JST connectors and the ESP32-A1S get none: hand-soldered.
"""
import glob, re, uuid

BY_VALUE = {  # (footprint contains, value) -> LCSC
    ("R_0805", "10k"): "C17414", ("R_0805", "1k"): "C17513", ("R_0805", "4.7k"): "C17673",
    ("R_0805", "100k"): "C149504", ("R_0805", "5.1k"): "C27834", ("R_0805", "470"): "C17710",
    ("R_0805", "330"): "C17630", ("R_0805", "100"): "C17408", ("R_0805", "470k"): "C17709",
    ("R_0805", "2.4k"): "C17526",
    ("C_0805", "100n"): "C49678", ("C_0805", "1u"): "C28323", ("C_0805", "10u"): "C15850",
    ("C_0805", "22u"): "C45783", ("C_0805", "47u"): "C16780", ("CP_Elec_8x10", "470u"): "C249545",
    ("LED_0805", "red"): "C84256", ("LED_0805", "green"): "C2297",
}
BY_FOOTPRINT = {  # footprint contains -> LCSC (one part per footprint)
    "SOIC-8-1EP": "C16581",            # TP4056-42-ESOP8
    "SOT-23-6_L2.9": "C2830320",       # FS8205A
    "MSOP-8_L3.0": "C189961",          # NS4150B
    "SW-TH_MSK12C02": "C431540",
    "AUDIO-SMD_PJ-320D": "C431535",
    "SOT-23-5": "C51118",              # AP2112K-3.3
    "SOT-23-3": "C5446",               # XC6206P332MR
    "SOIC-16": "C84681",               # CH340C
    "SOT-363": "C123008",              # UMH3N (ROHM UMH3NTN)
    "SOT-323": "C2992467",             # BAT54W
    "D_SMA": "C8678",                  # SS34
    "Package_TO_SOT_SMD:SOT-23\"": "C15127",   # AO3401A (plain SOT-23)
    "HRO_TYPE-C-31-M-12": "C165948",
    "TS-1187A": "C318884",
}
BY_VALUE_EXACT = {"DW01A": "C351410", "USBLC6-2SC6": "C7519"}   # both SOT-23-6


def lcsc_for(fp, value):
    if value in BY_VALUE_EXACT:
        return BY_VALUE_EXACT[value]
    for (f, v), c in BY_VALUE.items():
        if f in fp and v == value:
            return c
    for f, c in BY_FOOTPRINT.items():
        if f in fp + '"':
            return c
    return None


def prop_block(text, name):
    m = re.search(r'\n(\t+)\(property "' + re.escape(name) + r'" "([^"]*)"', text)
    if not m:
        return None
    start, depth = m.start() + 1, 0
    for j in range(start, len(text)):
        if text[j] == "(":
            depth += 1
        elif text[j] == ")":
            depth -= 1
            if depth == 0:
                return start, j + 1, m.group(1), m.group(2)


done, missing = 0, []
for path in glob.glob("D:/dev/esp32-sendspin-speaker/hardware/main/*.kicad_sch"):
    t = open(path, encoding="utf-8").read()
    out, pos = [], 0
    for m in re.finditer(r'\n\t\(symbol\n\t\t\(lib_id "([^"]+)"', t):
        s = m.start() + 1
        depth = 0
        for e in range(s, len(t)):
            if t[e] == "(":
                depth += 1
            elif t[e] == ")":
                depth -= 1
                if depth == 0:
                    break
        blk = t[s:e + 1]
        ref = prop_block(blk, "Reference")[3]
        if ref.startswith("#"):
            continue
        fp, value = prop_block(blk, "Footprint")[3], prop_block(blk, "Value")[3]
        code = lcsc_for(fp, value)
        if not code:
            missing.append(f"{ref} {value} {fp.split(':')[-1]}")
            continue
        old = prop_block(blk, "LCSC")
        if old:
            new = blk[:old[0]] + blk[old[0]:old[1]].replace(f'"LCSC" "{old[3]}"', f'"LCSC" "{code}"', 1) + blk[old[1]:]
        else:
            ds = prop_block(blk, "Datasheet")
            ind = ds[2]
            field = (f'\n{ind}(property "LCSC" "{code}"\n{ind}\t(at 0 0 0)\n{ind}\t(hide yes)\n'
                     f'{ind}\t(effects\n{ind}\t\t(font\n{ind}\t\t\t(size 1.27 1.27)\n{ind}\t\t)\n{ind}\t)\n{ind})')
            new = blk[:ds[1]] + field + blk[ds[1]:]
        out.append(t[pos:s]); out.append(new); pos = e + 1
        done += 1
    out.append(t[pos:])
    open(path, "w", encoding="utf-8", newline="\n").write("".join(out))
print("LCSC set on", done, "symbols; without:", sorted(set(missing)))
