"""Helpers for first placements with KiCad's Python (pcbnew): place, pack, outline, holes, GND pour."""
import pcbnew

FP_DIR = "D:/Programs/KiCad/10.0/share/kicad/footprints"
mm = pcbnew.FromMM


PRELOADED = {}


def preload(lib, name):
    """Load a library footprint. Call before LoadBoard(): afterwards KiCad 10's SWIG
    bindings hand back bare objects from FootprintLoad()."""
    fp = pcbnew.FootprintLoad(f"{FP_DIR}/{lib}.pretty", name)
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    PRELOADED[name] = fp


class Board:
    def __init__(self, path, x0, y0, w, h):
        self.path, self.x0, self.y0, self.w, self.h = path, x0, y0, w, h
        self.b = pcbnew.LoadBoard(path)
        self.fp = {f.GetReference(): f for f in self.b.GetFootprints()}
        self.trash = []   # removed items stay referenced until saved: deleting them early crashes pcbnew

    def bbox(self, ref):
        r = self.fp[ref].GetBoundingBox(False)
        return (pcbnew.ToMM(r.GetX()), pcbnew.ToMM(r.GetY()),
                pcbnew.ToMM(r.GetWidth()), pcbnew.ToMM(r.GetHeight()))

    def place(self, ref, x, y, rot=0, back=False):
        """Put the footprint's body (without texts) with its top-left corner at x, y."""
        f = self.fp[ref]
        if back != f.IsFlipped():
            f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        f.SetOrientationDegrees(rot)
        bx, by, _, _ = self.bbox(ref)
        p = f.GetPosition()
        f.SetPosition(pcbnew.VECTOR2I(p.x + mm(x - bx), p.y + mm(y - by)))

    def size(self, ref, rot=0):
        self.fp[ref].SetOrientationDegrees(rot)
        return self.bbox(ref)[2:]

    def pack(self, refs, x0, y0, x1, y1, gap=1.0):
        """Row-pack footprints into a rectangle; returns the ones that didn't fit."""
        x, y, row_h, left = x0, y0, 0.0, []
        for ref in refs:
            w, h = self.size(ref)
            if x + w > x1:
                x, y, row_h = x0, y + row_h + gap, 0.0
            if y + h > y1:
                left.append(ref)
                continue
            self.place(ref, x, y)
            x += w + gap
            row_h = max(row_h, h)
        return left

    def outline(self):
        for d in list(self.b.GetDrawings()):
            if d.GetLayer() == pcbnew.Edge_Cuts:
                self.trash.append(d); self.b.Remove(d)
        r = pcbnew.PCB_SHAPE(self.b)
        r.SetShape(pcbnew.SHAPE_T_RECT)
        r.SetStart(pcbnew.VECTOR2I(mm(self.x0), mm(self.y0)))
        r.SetEnd(pcbnew.VECTOR2I(mm(self.x0 + self.w), mm(self.y0 + self.h)))
        r.SetLayer(pcbnew.Edge_Cuts)
        r.SetWidth(mm(0.1))
        self.b.Add(r)

    def holes(self, name, points):
        """Board-only mounting holes (not in the schematic, BOM or position files),
        copied from a footprint preloaded with preload() before the board was opened."""
        for ref in [r for r in self.fp if r.startswith("H")]:
            self.trash.append(self.fp.pop(ref)); self.b.Remove(self.trash[-1])
        for i, (x, y) in enumerate(points, start=1):
            h = pcbnew.FOOTPRINT(PRELOADED[name])
            h.SetParent(self.b)
            h.SetReference(f"H{i}")
            h.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
            h.SetBoardOnly(True); h.SetExcludedFromBOM(True); h.SetExcludedFromPosFiles(True)
            self.b.Add(h)

    def gnd_pour(self):
        for z in list(self.b.Zones()):
            self.trash.append(z); self.b.Remove(z)
        gnd = self.b.FindNet("GND")
        for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
            z = pcbnew.ZONE(self.b)
            z.SetLayer(layer); z.SetNet(gnd); z.SetZoneName("GND")
            ol = z.Outline(); ol.NewOutline()
            for x, y in ((self.x0, self.y0), (self.x0 + self.w, self.y0),
                         (self.x0 + self.w, self.y0 + self.h), (self.x0, self.y0 + self.h)):
                ol.Append(mm(x), mm(y))
            z.SetLocalClearance(mm(0.3)); z.SetMinThickness(mm(0.25))
            z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
            self.b.Add(z)
        pcbnew.ZONE_FILLER(self.b).Fill(self.b.Zones())

    def save(self):
        pcbnew.SaveBoard(self.path, self.b)
