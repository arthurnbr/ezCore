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
    "C1": "C_0603_1608Metric", "C2": "C_0603_1608Metric", "C5": "C_0402_1005Metric",
    "C3": "C_0402_1005Metric", "C4": "C_0402_1005Metric",
    "SW1": "SW_Push_1P1T_NO_CK_KMR2", "SW3": "SW_SPDT_PCM12", "BT1": "Batt_WirePads_2x",
    "J5": "Pogo_4P_2.54mm",
    "TP1": "TestPoint_Pad_1.0x1.0mm", "TP2": "TestPoint_Pad_1.0x1.0mm",
    "TP3": "TestPoint_Pad_1.0x1.0mm", "TP4": "TestPoint_Pad_1.0x1.0mm",
    "TP5": "TestPoint_Pad_1.0x1.0mm", "TP6": "TestPoint_Pad_1.0x1.0mm",
    "FID1": "Fiducial_Align_1.5mm", "FID2": "Fiducial_Align_1.5mm", "FID3": "Fiducial_Align_1.5mm",
}
# placement by body centre, in board-centre-relative mm: (dx, dy, rot, back_side)
# +x right, +y down. Centre of board is (0,0).
PLACE = {
    "AE1": (0, -1, 60, False),
    "U1": (0, -1, 0, False),
    "U2": (0, 15, 0, False),
    "C5": (5.5, 13, 0, False),
    "C1": (-14.1, -5.13, 0, True),
    "C2": (-14.1, 5.13, 0, True),
    "C3": (-9.83, -6.88, 0, True),
    "C4": (9.83, -6.88, 0, True),
    "SW1": (-18.0, 0.0, 0, True),
    "SW3": (17.5, 0.0, 90, True),
    "J5": (-0.0, -17.0, 0, True),
    "BT1": (0.0, 16.0, 0, True),
    "TP1": (-18.13, -8.45, 0, True),
    "TP2": (-14.14, -14.14, 0, True),
    "TP3": (18.13, -8.45, 0, True),
    "TP4": (14.14, -14.14, 0, True),
    "TP5": (-6.84, -18.79, 0, True),
    "TP6": (6.84, -18.79, 0, True),
    "FID1": (-18.19, 10.5, 0, False),
    "FID2": (18.19, 10.5, 0, False),
    "FID3": (0.0, -21.0, 0, False),
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
    """Plain round board Ø48 as a single Edge.Cuts circle.

    No keychain ear or hole: the attachment point is handled on the enclosure, not
    the PCB (per project decision)."""
    c = pcbnew.PCB_SHAPE(board)
    c.SetShape(pcbnew.SHAPE_T_CIRCLE)
    c.SetCenter(VM(CX, CY))
    c.SetEnd(VM(CX + R, CY))
    c.SetLayer(pcbnew.Edge_Cuts)
    c.SetWidth(MM(0.1))
    board.Add(c)


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
