#!/usr/bin/env python3
"""Generate ezCore V2 (circular, home-etch) MeshTag.kicad_pcb from the netlist +
local footprints.

Plain round board Ø48 mm. XIAO in the centre, Wio-SX1262 at the bottom edge (IPEX
toward the rim, LoRa FPC wraps the inner wall), round NFC coil under the XIAO,
pogo-4P + button + slide switch + battery pads on the back. The attachment point
(keychain) is handled by the enclosure, not the PCB.

Pipeline: `build_pcb.py` places parts, draws the round outline, writes the
NFC-coil keep-out and the GND-net code; `route_pcb.sh` then autoroutes and calls
`build_pcb.py finalize` to add the BLE/GND zones and fill.
"""
import pcbnew, re, os, sys, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRETTY = os.path.join(ROOT, "lib", "MeshTag.pretty")
NET = os.path.join(ROOT, "MeshTag.net")
OUT = os.path.join(ROOT, "MeshTag.kicad_pcb")

MM = pcbnew.FromMM
def VM(x, y): return pcbnew.VECTOR2I(MM(x), MM(y))

# ---- round board ----
DIA = 48.0                 # board diameter
R = DIA / 2.0              # radius
CX, CY = 130.0, 110.0      # board centre in workspace


# ---- component -> footprint ----
REFFP = {
    "U1": "XIAO-nRF52840-SMD", "U2": "Wio-SX1262-Module", "AE1": "NFC_Coil_Round",
    "C1": "C_0402_1005Metric", "C2": "C_0402_1005Metric", "C5": "C_0402_1005Metric",
    "C3": "C_0402_1005Metric", "C4": "C_0402_1005Metric",
    "SW1": "SW_Push_1P1T_NO_CK_KMR2", "SW3": "SW_SPDT_PCM12", "BT1": "Batt_WirePads_2x",
    "J5": "Pogo_4P_2.54mm",
    "D1": "LED_0402", "D2": "LED_0402", "R1": "R_0402", "R2": "R_0402",
    "TP1": "TestPoint_Pad_1.0x1.0mm", "TP2": "TestPoint_Pad_1.0x1.0mm",
    "TP3": "TestPoint_Pad_1.0x1.0mm", "TP4": "TestPoint_Pad_1.0x1.0mm",
    "TP5": "TestPoint_Pad_1.0x1.0mm", "TP6": "TestPoint_Pad_1.0x1.0mm",
}
# UX-first placement, all on the FRONT face. Pogo at the TOP, button + bicolour LED
# on the LEFT (90° from the pogo), SWD/test pads near the button (lower-left),
# ON/OFF slide switch on the RIGHT, XIAO + NFC coil centred, Wio just below. The
# keychain notch is at the BOTTOM of the outline (opposite the pogo); the battery
# (Ø45 + ferrite) sits behind the board.
# Placement by body centre, board-centre-relative mm: (dx, dy, rot, back_side).
# +x right, +y down. Centre of board is (0,0).
PLACE = {
    "U1":  (0, -2, 0, False),         # XIAO, centre (nudged up to free the bottom)
    "AE1": (0, -2, 60, False),        # NFC coil under the XIAO (feed -> NFC pads)
    "U2":  (0, 13, 0, False),         # Wio-SX1262 below the XIAO
    "C5": (14, 13, 0, False),         # Wio VCC decoupling
    "C1": (-12, 10, 0, False), "C2": (12, 10, 0, False),   # 3V3 decoupling
    "C3": (-11, 14, 0, False),  "C4": (11, 14, 0, False),      # NFC tuning
    "J5":  (0, -20, 0, False),        # POGO charge/USB pads, top
    "BT1": (0, -14.5, 0, False),      # LiPo wire pads (battery body is behind)
    "SW1": (-19, -2, 0, False),       # user BUTTON, far left (90° from pogo)
    "D1":  (-14.5, -5, 0, False), "D2": (-14.5, -8, 0, False),   # bicolour LED (R/G)
    "R1":  (-18.5, -5, 0, False), "R2": (-18.5, -8, 0, False),   # LED series resistors
    "TP1": (-20, 3, 0, False), "TP2": (-20, 6, 0, False),       # SWD/RST test pads,
    "TP3": (-18, 9, 0, False), "TP4": (-15, 11, 0, False),    #   near the button
    "TP5": (-6, -18, 0, False), "TP6": (6, -18, 0, False),      # USB D+/D- (by pogo)
    "SW3": (19, -2, 90, False),       # ON/OFF slide switch, right
}


def body_offset(mod):
    """Centroid of the footprint copper bounding box (pads + graphic copper)."""
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
    nets = {}
    def getnet(name):
        if name not in nets:
            n = pcbnew.NETINFO_ITEM(board, name)
            board.Add(n)
            nets[name] = n
        return nets[name]

    for ref, fp in REFFP.items():
        mod = pcbnew.FootprintLoad(PRETTY, fp)
        if mod is None:
            sys.exit("cannot load footprint %s" % fp)
        mod.SetReference(ref)
        dx, dy, rot, flip = PLACE[ref]
        board.Add(mod)
        bx, by = body_offset(mod)
        if flip:
            bx = -bx
        r = math.radians(rot)
        ox = bx * math.cos(r) - by * math.sin(r)
        oy = bx * math.sin(r) + by * math.cos(r)
        mod.SetPosition(VM(CX + dx - ox, CY + dy - oy))
        if flip:
            mod.Flip(mod.GetPosition(), True)
        mod.SetOrientationDegrees(rot)
        for pad in mod.Pads():
            key = (ref, pad.GetNumber())
            if key in node2net:
                pad.SetNet(getnet(node2net[key]))

    draw_outline(board)
    board.GetDesignSettings().SetBoardThickness(MM(1.0))

    gnd_code = getnet("GND").GetNetCode()
    board.Save(OUT)

    # NFC-coil keep-out BEFORE routing (keeps tracks/pour off the coil copper).
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
    """Round board Ø48 with a keychain tab at the BOTTOM and edge registration
    marks for double-sided home etching.

    The main circle is cut by a small bump (tab) at the bottom where the user
    drills the keychain hole themselves; no copper or plated hole is placed there.
    Four short registration ticks on Edge.Cuts (N/E/S/W) let the two photo films be
    aligned without drilled fiducials."""
    import math as _m
    # One CLOSED contour: the main Ø48 circle joined to a keychain tab at the
    # bottom, built from two arcs that meet at the circle/tab intersections.
    tab_r = 3.5
    tab_cy = CY + R + 1.0                       # tab centre below the rim (+Y)
    dc = abs(tab_cy - CY)
    a = (R ** 2 - tab_r ** 2 + dc ** 2) / (2 * dc)
    h = _m.sqrt(R ** 2 - a ** 2)
    py = CY + a
    L = (CX - h, py)                            # left intersection
    Rr = (CX + h, py)                           # right intersection

    def arc(start, mid, end):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_ARC)
        s.SetArcGeometry(VM(*start), VM(*mid), VM(*end))
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1)); board.Add(s)

    # main circle arc: left intersection -> top -> right intersection (the long way)
    arc(L, (CX, CY - R), Rr)
    # tab arc: right intersection -> tab bottom -> left intersection
    arc(Rr, (CX, tab_cy + tab_r), L)

    # silk guide ring where to drill the keychain hole (no copper, no plated hole)
    g = pcbnew.PCB_SHAPE(board)
    g.SetShape(pcbnew.SHAPE_T_CIRCLE)
    g.SetCenter(VM(CX, tab_cy)); g.SetEnd(VM(CX + 1.2, tab_cy))
    g.SetLayer(pcbnew.F_SilkS); g.SetWidth(MM(0.2)); board.Add(g)

    # edge registration ticks on F.Silk at N/E/W (recto-verso alignment, no holes)
    for ang in (90, 0, 180):
        r = _m.radians(ang)
        x0 = CX + (R - 1.5) * _m.cos(r); y0 = CY - (R - 1.5) * _m.sin(r)
        x1 = CX + (R + 0.0) * _m.cos(r); y1 = CY - (R + 0.0) * _m.sin(r)
        for layer in (pcbnew.F_SilkS, pcbnew.B_SilkS):
            t = pcbnew.PCB_SHAPE(board)
            t.SetShape(pcbnew.SHAPE_T_SEGMENT)
            t.SetStart(VM(x0, y0)); t.SetEnd(VM(x1, y1))
            t.SetLayer(layer); t.SetWidth(MM(0.2)); board.Add(t)


def zone_sexpr(name, netcode, netname, layers, pts, keepout=False):
    import uuid
    poly = "\n".join("        (xy %.3f %.3f)" % (x, y) for x, y in pts)
    lay = " ".join('"%s"' % l for l in layers)
    head = ('  (zone\n'
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


def circle_pts(cx, cy, rad, nseg=72):
    return [(cx + rad * math.cos(2 * math.pi * k / nseg),
             cy + rad * math.sin(2 * math.pi * k / nseg)) for k in range(nseg)]


def coil_keepout():
    """Keep the GND pour out of the round NFC coil (Ø ~34 under the XIAO)."""
    return zone_sexpr("NFC_COIL_KEEPOUT", 0, "", ("F.Cu", "B.Cu"),
                      circle_pts(CX, CY, 8.5), keepout=True)


def extra_zones(gnd_code):
    """BLE-antenna keep-out (top of XIAO, ear side) + GND pours (both layers)."""
    z = ""
    # BLE keep-out: a band near the top of the XIAO (its onboard antenna end).
    z += zone_sexpr("BLE_ANT_KEEPOUT", 0, "", ("F.Cu", "B.Cu"),
                    [(CX - 9, CY - 13), (CX + 9, CY - 13),
                     (CX + 9, CY - 8.5), (CX - 9, CY - 8.5)], keepout=True)
    # GND pours: ring between the coil keep-out (r 17) and the rim (r ~23.3).
    ring_out = circle_pts(CX, CY, R - 0.7)
    ring_in = list(reversed(circle_pts(CX, CY, 8.8)))
    for layer in ("F.Cu", "B.Cu"):
        z += zone_sexpr("GND_pour", gnd_code, "GND", (layer,), ring_out)
    return z


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
