#!/usr/bin/env python3
"""Generate MeshTag.kicad_pcb from the netlist + local footprints.
Run: kicad-cli python / plain python3 with pcbnew available.
Idempotent: regenerates the board from scratch each run."""
import pcbnew, re, os, sys, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRETTY = os.path.join(ROOT, "lib", "MeshTag.pretty")
NET = os.path.join(ROOT, "MeshTag.net")
OUT = os.path.join(ROOT, "MeshTag.kicad_pcb")

MM = pcbnew.FromMM
def VM(x, y): return pcbnew.VECTOR2I(MM(x), MM(y))

# ---- board dimensions (mm) ----
BW, BH = 26.0, 52.0           # board width / height
OX, OY = 100.0, 80.0          # workspace offset for the top-left board corner

# ---- component -> footprint ----
REFFP = {
    "U1": "XIAO-nRF52840-SMD", "U2": "Wio-SX1262-Module", "AE1": "NFC_Coil_5T_2L",
    "C1": "C_0603_1608Metric", "C2": "C_0603_1608Metric",
    "C3": "C_0402_1005Metric", "C4": "C_0402_1005Metric",
    "SW1": "SW_Push_1P1T_NO_CK_KMR2", "SW3": "SW_SPDT_PCM12", "BT1": "Batt_WirePads_2x",
    "TP1": "TestPoint_Pad_1.0x1.0mm", "TP2": "TestPoint_Pad_1.0x1.0mm",
    "TP3": "TestPoint_Pad_1.0x1.0mm", "TP4": "TestPoint_Pad_1.0x1.0mm",
}

# placement by BODY CENTRE relative to board top-left: (cx, cy, rot_deg, back_side).
# The footprint origin is computed from the pad bounding box so parts stay inside
# the outline regardless of where the library put the origin.
PLACE = {
    "U2": (13, 7, 0, False),     # Wio-SX1262 module, top edge
    "U1": (13, 24, 0, False),    # XIAO nRF52840, centre (front)
    "AE1": (13, 43, 0, False),   # NFC coil (front + back copper), lower-middle
    "C1": (9, 14, 0, True),        # 3V3 decoupling (back, under XIAO)
    "C2": (17, 14, 0, True),
    "C3": (6, 31.5, 0, True),        # NFC tuning caps (back, near coil feed)
    "C4": (20, 31.5, 0, True),
    "SW1": (13, 28, 0, True),      # user button (back, case hole)
    "SW3": (16, 35, 0, True),      # battery slide switch (back, bottom-right)
    "BT1": (7, 35, 0, True),       # LiPo wire pads (back, bottom-left)
    "TP1": (4, 19, 0, True),       # RST_MCU   (back SWD/RST/GND test pads)
    "TP2": (4, 22, 0, True),       # SWDIO
    "TP3": (22, 19, 0, True),      # SWCLK
    "TP4": (22, 22, 0, True),      # GND
}


def body_offset(mod):
    """Centroid of the footprint copper bounding box (pads + graphic copper such
    as the NFC coil spiral), in footprint-local mm, so every part centres on its
    real outline regardless of where the library put the origin."""
    xs, ys = [], []
    for pad in mod.Pads():
        bb = pad.GetBoundingBox()
        xs += [pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetRight())]
        ys += [pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetBottom())]
    for g in mod.GraphicalItems():
        if g.GetLayerName() in ("F.Cu", "B.Cu"):
            bb = g.GetBoundingBox()
            xs += [pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetRight())]
            ys += [pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetBottom())]
    ox = pcbnew.ToMM(mod.GetPosition().x)
    oy = pcbnew.ToMM(mod.GetPosition().y)
    return (min(xs) + max(xs)) / 2 - ox, (min(ys) + max(ys)) / 2 - oy


def parse_nodes(path):
    txt = open(path).read()
    node2net = {}
    for nm, body in re.findall(
        r'\(net \(code[^)]*\) \(name "([^"]+)"\)(.*?)(?=\(net |\s*\)\s*\Z)', txt, re.S):
        for ref, pin in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"', body):
            node2net[(ref, pin)] = nm
    return node2net


def main():
    node2net = parse_nodes(NET)
    board = pcbnew.BOARD()

    # net registry
    nets = {}
    def getnet(name):
        if name not in nets:
            n = pcbnew.NETINFO_ITEM(board, name)
            board.Add(n)
            nets[name] = n
        return nets[name]

    # place footprints by body centre
    for ref, fp in REFFP.items():
        mod = pcbnew.FootprintLoad(PRETTY, fp)
        if mod is None:
            sys.exit("cannot load footprint %s" % fp)
        mod.SetReference(ref)
        cx, cy, rot, flip = PLACE[ref]
        board.Add(mod)
        # origin so that the rotated/flipped body centre lands on (cx, cy)
        bx, by = body_offset(mod)
        if flip:
            bx = -bx
        r = math.radians(rot)
        ox = bx * math.cos(r) - by * math.sin(r)
        oy = bx * math.sin(r) + by * math.cos(r)
        mod.SetPosition(VM(OX + cx - ox, OY + cy - oy))
        if flip:
            mod.Flip(mod.GetPosition(), True)
        mod.SetOrientationDegrees(rot)
        for pad in mod.Pads():
            key = (ref, pad.GetNumber())
            if key in node2net:
                pad.SetNet(getnet(node2net[key]))

    # board outline on Edge.Cuts with rounded corners + keychain hole
    draw_outline(board)

    # stackup 1.0 mm
    board.GetDesignSettings().SetBoardThickness(MM(1.0))

    gnd_code = getnet("GND").GetNetCode()
    board.Save(OUT)

    # The NFC-coil keep-out is added NOW (before routing) so the autorouter and the
    # GND pour stay out of the coil's netless spiral. The BLE keep-out and the GND
    # pours are added later by finalize(), after routing, so the router can reach
    # pads under those areas. Record the GND net code for that step.
    with open(OUT) as fh:
        txt = fh.read()
    idx = txt.rstrip().rfind(")")
    txt = txt[:idx] + coil_keepout() + ")\n"
    with open(OUT, "w") as fh:
        fh.write(txt)
    with open(OUT.replace(".kicad_pcb", ".zoneinfo"), "w") as fh:
        fh.write(str(gnd_code))

    print("wrote", OUT, "with", len(REFFP), "footprints and", len(nets), "nets")


def draw_outline(board):
    r = 2.0  # corner radius
    pts = [(0, 0), (BW, 0), (BW, BH), (0, BH)]
    # straight edges with rounded corners via arcs
    def seg(x1, y1, x2, y2):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(VM(OX + x1, OY + y1)); s.SetEnd(VM(OX + x2, OY + y2))
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1)); board.Add(s)
    def arc(cx, cy, x1, y1, x2, y2):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_ARC)
        s.SetCenter(VM(OX + cx, OY + cy))
        s.SetStart(VM(OX + x1, OY + y1)); s.SetEnd(VM(OX + x2, OY + y2))
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1)); board.Add(s)
    # top edge
    seg(r, 0, BW - r, 0)
    arc(BW - r, r, BW - r, 0, BW, r)
    seg(BW, r, BW, BH - r)
    arc(BW - r, BH - r, BW, BH - r, BW - r, BH)
    seg(BW - r, BH, r, BH)
    arc(r, BH - r, r, BH, 0, BH - r)
    seg(0, BH - r, 0, r)
    arc(r, r, 0, r, r, 0)
    # keychain hole near top
    hole = pcbnew.PCB_SHAPE(board)
    hole.SetShape(pcbnew.SHAPE_T_CIRCLE)
    hole.SetCenter(VM(OX + BW / 2, OY + 3.6))
    hole.SetEnd(VM(OX + BW / 2 + 1.6, OY + 3.6))
    hole.SetLayer(pcbnew.Edge_Cuts); hole.SetWidth(MM(0.1)); board.Add(hole)


def zone_sexpr(name, netcode, netname, layers, pts, keepout=False):
    """One copper/keep-out zone as board s-expr text (pcbnew Save() segfaults on
    in-process rule-area zones, so every zone is appended textually)."""
    import uuid
    poly = "\n".join("        (xy %.3f %.3f)" % (OX + x, OY + y) for x, y in pts)
    lay = " ".join('"%s"' % l for l in layers)
    head = (
        '  (zone\n'
        '    (net %d) (net_name "%s") (layers %s)\n' % (netcode, netname, lay) +
        '    (uuid "%s")\n' % uuid.uuid4() +
        '    (name "%s") (hatch edge 0.5)\n' % name +
        '    (connect_pads (clearance 0.2))\n'
        '    (min_thickness 0.2)\n')
    if keepout:
        body = ('    (keepout (tracks allowed) (vias allowed) (pads allowed)\n'
                '             (copperpour not_allowed) (footprints allowed))\n'
                '    (fill (thermal_gap 0.5) (thermal_bridge_width 0.5))\n')
    else:
        body = '    (fill yes (thermal_gap 0.3) (thermal_bridge_width 0.4))\n'
    return head + body + '    (polygon (pts\n' + poly + '\n    ))\n  )\n'


def coil_keepout():
    """NFC-coil keep-out, added BEFORE routing so the autorouter keeps tracks and
    the GND pour out of the coil's netless spiral copper (which would otherwise be
    flagged as shorts). Only the coil and its feed/tuning pads sit inside it."""
    return zone_sexpr("NFC_COIL_KEEPOUT", 0, "", ("F.Cu", "B.Cu"),
                      [(3, 38.3), (23, 38.3), (23, 48), (3, 48)], keepout=True)


def extra_zones(gnd_code):
    """BLE-antenna keep-out and GND copper pours, added AFTER routing.

    - XIAO mounted with USB toward the board bottom: its onboard 2.4 GHz antenna
      sits at the bottom of the module (~y 32.5-36). Keep copper away.
    - GND pours fill the mid board (y 11.6-32.2) on both layers; the coil band is
      already protected by the NFC keep-out placed before routing.
    """
    z = ""
    z += zone_sexpr("BLE_ANT_KEEPOUT", 0, "", ("F.Cu", "B.Cu"),
                    [(3, 32.5), (23, 32.5), (23, 36), (3, 36)], keepout=True)
    for layer in ("F.Cu", "B.Cu"):
        z += zone_sexpr("GND_pour", gnd_code, "GND", (layer,),
                        [(0.4, 11.6), (25.6, 11.6), (25.6, 32.2), (0.4, 32.2)])
    return z



def lay_coil_tracks(board):
    """Lay the 5-turn 2-layer NFC spiral as real copper tracks.

    The coil footprint is a net tie (pads 1=NFC1 feed on F, 2=NFC2 feed on B, and a
    shared centre via as pad 1). Top copper spirals from the F feed pad to the via
    on NFC1; bottom copper spirals from the via to the B feed pad on NFC2. Using
    real tracks (not footprint graphics) gives the coil true connectivity so DRC
    sees the winding as connected."""
    ae = next(m for m in board.GetFootprints() if m.GetReference() == "AE1")
    cx = pcbnew.ToMM(ae.GetPosition().x)
    cy = pcbnew.ToMM(ae.GetPosition().y)
    nfc1 = board.FindNet("NFC1").GetNetCode()
    nfc2 = board.FindNet("NFC2").GetNetCode()
    A, Bb, n, p, w = 8.5, 3.5, 5, 0.5, 0.25

    def spiral(y_feed):
        a = [A - k * p for k in range(n + 1)]
        b = [Bb - k * p for k in range(n + 1)]
        pts = [(a[0], y_feed)]
        for k in range(n):
            pts += [(a[k], -b[k]), (-a[k], -b[k]), (-a[k], b[k]), (a[k + 1], b[k])]
        pts += [(a[n], 0.0)]            # ends at the centre via (x = A - n*p)
        return pts

    def add(pts, layer, netcode):
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(VM(cx + x1, cy + y1))
            t.SetEnd(VM(cx + x2, cy + y2))
            t.SetWidth(MM(w)); t.SetLayer(layer); t.SetNetCode(netcode)
            board.Add(t)

    add(spiral(1.0), pcbnew.F_Cu, nfc1)                      # F feed -> via
    add([(x, -y) for (x, y) in spiral(-1.0)], pcbnew.B_Cu, nfc2)  # via -> B feed


def finalize():
    """Append keep-outs + GND pours to the routed board, then fill zones.

    The NFC coil is a net-tie footprint whose spiral is footprint copper, so no
    extra tracks are laid here."""
    with open(OUT.replace(".kicad_pcb", ".zoneinfo")) as fh:
        gnd_code = int(fh.read().strip())
    with open(OUT) as fh:
        txt = fh.read()
    idx = txt.rstrip().rfind(")")
    txt = txt[:idx] + extra_zones(gnd_code) + ")\n"
    with open(OUT, "w") as fh:
        fh.write(txt)
    board = pcbnew.LoadBoard(OUT)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.Save(OUT)
    print("finalized: zones", board.GetAreaCount(),
          "tracks", len(list(board.GetTracks())))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "finalize":
        finalize()
    else:
        main()
