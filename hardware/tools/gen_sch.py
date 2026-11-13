#!/usr/bin/env python3
"""Generate a human-readable MeshTag.kicad_sch from the component/net definition.

Layout is organised in labelled functional blocks with generous spacing so the
global labels (which carry connectivity) sit clearly outside each symbol and never
overlap it. Text notes annotate every block.

Run: python3 tools/gen_sch.py   (from hardware/ or anywhere)
"""
import uuid, re, os, json, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, "lib", "MeshTag.kicad_sym")
SCH = os.path.join(ROOT, "MeshTag.kicad_sch")
PRO = os.path.join(ROOT, "MeshTag.kicad_pro")


def u():
    return str(uuid.uuid4())


def gs(v):
    return round(round(v / 1.27) * 1.27, 2)


# ---- read symbol pin geometry from the local library ----
SLIB = open(LIB).read()


def _symbol_block(name):
    m = re.search(r'\n\t\(symbol "' + re.escape(name) + r'"', SLIB)
    i = m.start() + 1
    d = 0
    j = i
    while j < len(SLIB):
        if SLIB[j] == '(':
            d += 1
        elif SLIB[j] == ')':
            d -= 1
            if d == 0:
                break
        j += 1
    return SLIB[i:j + 1]


def pin_xy(name, num):
    """Return (dx, dy, angle) of a pin tip in symbol-local coords (schematic Y down)."""
    blk = _symbol_block(name)
    for m in re.finditer(
        r'\(pin \w+ \w+\s*\(at ([\d.-]+) ([\d.-]+) (\d+)\)\s*\(length ([\d.]+)\)\s*\(name "([^"]*)"',
        blk):
        n = re.search(r'\(number "([^"]*)"', blk[m.end():m.end() + 160]).group(1)
        if n == num:
            x, y, ang = float(m.group(1)), float(m.group(2)), int(m.group(3))
            return x, -y, ang  # schematic Y is inverted vs the library
    raise KeyError("%s pin %s" % (name, num))


def grab_lib(name):
    """Return the symbol block re-namespaced to MeshTag: and indented for lib_symbols."""
    blk = re.sub(r'^\t\(symbol "' + re.escape(name) + '"',
                 '\t\t(symbol "MeshTag:%s"' % name, _symbol_block(name), count=1)
    return "\n".join(("\t" + ln if ln.strip() else ln) for ln in blk.split("\n"))


# ---- component placement, block by block ----
# Each entry: (ref, lib, x, y, {pin#: net}, label_side)
# label_side: 'L' labels exit left, 'R' right, 'U' up, 'D' down, or a dict per-pin.
ROWS = [
    # ---- MCU (centre) ----
    ("U1", "XIAO-nRF52840-SMD", 150, 110, {
        "1": "LORA_NSS", "2": "LORA_RST", "3": "SPI_SCK", "4": "SPI_MOSI",
        "5": "SPI_MISO", "6": "LORA_RXEN", "7": "LORA_BUSY", "8": "BTN",
        "9": "LED_G_G", "10": "LED_R_G",
        "11": "LORA_DIO1", "12": "+3V3", "13": "GND", "14": "VBUS",
        "19": "VBATT", "20": "GND", "21": "NFC1", "22": "NFC2",
        "15": "SWDIO", "16": "SWCLK", "17": "RST_MCU", "18": "GND"}),
    # ---- RADIO (right of MCU) ----
    ("U2", "Wio-SX1262", 235, 110, {
        "1": "LORA_RXEN", "2": "SPI_MISO", "3": "SPI_MOSI", "4": "SPI_SCK",
        "5": "LORA_RST", "6": "LORA_NSS", "7": "GND", "8": "+3V3",
        "9": "ANT", "10": "GND", "11": "LORA_BUSY", "12": "LORA_DIO1"}),
    ("C5", "C", 262, 150, {"1": "+3V3", "2": "GND"}),       # Wio VCC decoupling
    # ---- POWER / decoupling (left) ----
    ("C1", "C", 70, 150, {"1": "+3V3", "2": "GND"}),
    ("C2", "C", 85, 150, {"1": "+3V3", "2": "GND"}),
    # ---- NFC (bottom centre) ----
    ("AE1", "NFC_Coil_Round", 150, 175, {"1": "NFC1", "2": "NFC2"}),
    ("C3", "C", 120, 185, {"1": "NFC1", "2": "GND"}),
    ("C4", "C", 180, 185, {"1": "NFC2", "2": "GND"}),
    # ---- BUTTON + user LED (top-left) ----
    ("SW1", "SW_Push", 70, 75, {"1": "BTN", "2": "GND"}),
    ("D1", "LED", 55, 95, {"2": "LED_R_A", "1": "GND"}),    # red: anode(2)->R, cathode(1)->GND
    ("D2", "LED", 70, 95, {"2": "LED_G_A", "1": "GND"}),    # green
    ("R1", "R", 55, 110, {"1": "LED_R_G", "2": "LED_R_A"}), # red series R: GPIO(1)->anode(2)
    ("R2", "R", 70, 110, {"1": "LED_G_G", "2": "LED_G_A"}), # green series R
    # ---- BATTERY + switch (bottom-left) ----
    # Low-side cut: BAT+ stays on VBATT, SW3 opens BAT- from GND.
    ("BT1", "LiPo_1S", 60, 185, {"1": "VBATT", "2": "BAT_N"}),
    ("SW3", "SW_SPDT", 95, 185, {"1": "GND", "3": "BAT_N", "2": "NC_sw"}),
    # ---- CHARGE / USB (right) ----
    ("J5", "Pogo_4P", 290, 160, {"1": "VBUS", "2": "GND", "3": "USB_DP", "4": "USB_DM"}),
    ("TP5", "TestPoint", 315, 165, {"1": "USB_DP"}),
    ("TP6", "TestPoint", 315, 172, {"1": "USB_DM"}),
    # ---- SWD / test (top-right) ----
    ("TP1", "TestPoint", 300, 70, {"1": "RST_MCU"}),
    ("TP2", "TestPoint", 307, 70, {"1": "SWDIO"}),
    ("TP3", "TestPoint", 314, 70, {"1": "SWCLK"}),
    ("TP4", "TestPoint", 321, 70, {"1": "GND"}),
]

# PWR_FLAGs so every supply net is driven (ERC clean).
PWR_FLAGS = [("+3V3", 40, 150), ("GND", 40, 165), ("VBATT", 40, 180),
             ("VBUS", 40, 120), ("BAT_N", 40, 135),
             ("USB_DP", 345, 165), ("USB_DM", 345, 175)]

# Explicit no-connects (pins intentionally unused).
NO_CONNECT = [("U2", "9"), ("SW3", "2")]

# Block annotations: (text, x, y).
NOTES = [
    ("=== MCU (Seeed XIAO nRF52840) ===", 120, 70),
    ("=== RADIO LoRa (Wio-SX1262, EU868) ===", 215, 70),
    ("Decouplage 3V3", 62, 140),
    ("Bobine NFC (appairage par approche) + accord C3/C4", 110, 165),
    ("Bouton utilisateur", 55, 65),
    ("Batterie 1S + interrupteur coupure", 55, 175),
    ("Charge + flash UF2 + serie USB (pogo 4 pts)", 275, 150),
    ("Points de test SWD / RST", 290, 62),
    ("D+/D- vers pads USB du XIAO (USB-C non expose)", 300, 180),
]


def label_dir(ang):
    """All labels horizontal (rotation 0), justified so the text points OUTWARD
    (away from the symbol body), never upside-down.

    KiCad global-label justify is relative to the attach point:
      justify right  -> text sits to the LEFT of the pin
      justify left   -> text sits to the RIGHT of the pin
    Library pin angles (schematic Y-down): 0 exits left, 180 right,
    90 exits downward (bottom), 270 exits upward (top)."""
    return {
        0:   (0, "right"),   # left pin   -> text to the left, horizontal
        180: (0, "left"),    # right pin  -> text to the right, horizontal
        90:  (0, "left"),    # bottom pin -> text to the right, horizontal
        270: (0, "left"),    # top pin    -> text to the right, horizontal
    }.get(ang, (0, "left"))


def main():
    proj_uuid = u()
    pro = json.load(open(PRO))
    pro["sheets"] = [[proj_uuid, "Root"]]
    json.dump(pro, open(PRO, "w"), indent=2)

    used = sorted({lib for _, lib, *_ in ROWS} | {"PWR_FLAG"})
    lib_syms = "\n".join(grab_lib(n) for n in used)

    insts, labels, ncs, wires = [], [], [], []
    # For dense parts (XIAO, Wio) route each pin out with a short stub wire of
    # staggered length so the labels never overlap.
    STUB = 7.62   # base stub length (mm)
    for ref, lib, x, y, nm in ROWS:
        x, y = gs(x), gs(y)
        uid = u()
        insts.append((ref, lib, x, y, uid))
        dense = lib in ("XIAO-nRF52840-SMD", "Wio-SX1262")
        # group pins per side to stagger stubs within a side
        side_idx = {}
        for num, net in nm.items():
            dx, dy, ang = pin_xy(lib, num)
            px, py = round(x + dx, 2), round(y + dy, 2)
            if net in ("ANT", "NC_sw"):
                continue                     # no-connect pins: handled below, no stub
            if not dense:
                labels.append((net, px, py, ang))
                continue
            k = side_idx.get(ang, 0)
            side_idx[ang] = k + 1
            # stub direction = outward along the pin
            ux, uy = {0: (-1, 0), 180: (1, 0), 90: (0, 1), 270: (0, -1)}[ang]
            length = STUB + (k % 2) * 3.81      # alternate 7.62 / 11.43 to fan out
            ex, ey = gs(px + ux * length), gs(py + uy * length)
            wires.append(((px, py), (ex, ey)))
            labels.append((net, ex, ey, ang))

    place = {r[0]: (r[1], gs(r[2]), gs(r[3])) for r in ROWS}
    for ref, num in NO_CONNECT:
        lib, x, y = place[ref]
        dx, dy, _ = pin_xy(lib, num)
        ncs.append((round(x + dx, 2), round(y + dy, 2)))

    P = ['(kicad_sch',
         '\t(version 20250114)',
         '\t(generator "meshtag") (generator_version "9.0")',
         '\t(uuid "%s")' % u(),
         '\t(paper "A3")',
         '\t(lib_symbols\n' + lib_syms + '\n\t)']

    # footprint assigned to each reference (must match build_pcb.py REFFP so the
    # "Update PCB from schematic" step finds a footprint for every symbol)
    FP = {
        "U1": "XIAO-nRF52840-SMD", "U2": "Wio-SX1262-Module", "AE1": "NFC_Coil_Round",
        "C1": "C_0402_1005Metric", "C2": "C_0402_1005Metric", "C3": "C_0402_1005Metric",
        "C4": "C_0402_1005Metric", "C5": "C_0402_1005Metric",
        "SW1": "SW_Push_1P1T_NO_CK_KMR2", "SW3": "SW_SPDT_PCM12",
        "BT1": "Batt_WirePads_2x", "J5": "Pogo_4P_2.54mm",
        "D1": "LED_0402", "D2": "LED_0402", "R1": "R_0402", "R2": "R_0402",
        "TP1": "TestPoint_Pad_1.0x1.0mm", "TP2": "TestPoint_Pad_1.0x1.0mm",
        "TP3": "TestPoint_Pad_1.0x1.0mm", "TP4": "TestPoint_Pad_1.0x1.0mm",
        "TP5": "TestPoint_Pad_1.0x1.0mm", "TP6": "TestPoint_Pad_1.0x1.0mm",
    }
    # symbol instances (Reference above, Value below — never over the pins)
    for ref, lib, x, y, uid in insts:
        fp = "MeshTag:" + FP[ref] if ref in FP else ""
        P.append(
            '\t(symbol\n\t\t(lib_id "MeshTag:%s")\n\t\t(at %s %s 0)\n\t\t(unit 1)\n'
            '\t\t(exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)\n\t\t(uuid "%s")\n'
            '\t\t(property "Reference" "%s" (at %s %s 0) (effects (font (size 1.27 1.27))))\n'
            '\t\t(property "Value" "%s" (at %s %s 0) (effects (font (size 1 1)) (justify bottom)))\n'
            '\t\t(property "Footprint" "%s" (at %s %s 0) (effects (font (size 1.27 1.27)) hide))\n'
            '\t\t(instances (project "MeshTag" (path "/%s" (reference "%s") (unit 1))))\n\t)'
            % (lib, x, y, uid, ref, x, y - 12, lib, x, y + 12, fp, x, y, proj_uuid, ref))

    # stub wires for dense parts
    for (ax, ay), (bx, by) in wires:
        P.append('\t(wire (pts (xy %s %s) (xy %s %s))\n\t\t(stroke (width 0) (type default)) (uuid "%s"))'
                 % (ax, ay, bx, by, u()))
    # global labels (outward)
    for net, x, y, ang in labels:
        if net in ("ANT", "NC_sw"):
            continue
        rot, just = label_dir(ang)
        P.append(
            '\t(global_label "%s" (shape input) (at %s %s %s)\n'
            '\t\t(effects (font (size 1.27 1.27)) (justify %s)) (uuid "%s"))'
            % (net, x, y, rot, just, u()))

    for x, y in ncs:
        P.append('\t(no_connect (at %s %s) (uuid "%s"))' % (x, y, u()))

    # power flags
    for net, x, y in PWR_FLAGS:
        x, y = gs(x), gs(y)
        uid = u()
        P.append(
            '\t(symbol (lib_id "MeshTag:PWR_FLAG") (at %s %s 0) (unit 1)\n'
            '\t\t(exclude_from_sim no)(in_bom no)(on_board yes)(dnp no)(uuid "%s")\n'
            '\t\t(property "Reference" "#FLG%s" (at %s %s 0)(effects (font (size 1.27 1.27)) hide))\n'
            '\t\t(property "Value" "PWR_FLAG" (at %s %s 0)(effects (font (size 1 1))))\n'
            '\t\t(instances (project "MeshTag" (path "/%s" (reference "#FLG%s")(unit 1)))))'
            % (x, y, uid, int(y * 100), x, y - 4, x, y + 4, proj_uuid, int(y * 100)))
        dx, dy, ang = pin_xy("PWR_FLAG", "1")
        P.append(
            '\t(global_label "%s" (shape input) (at %s %s 0)\n'
            '\t\t(effects (font (size 1.27 1.27)) (justify right)) (uuid "%s"))'
            % (net, round(x + dx, 2), round(y + dy, 2), u()))

    # block annotations
    for txt, x, y in NOTES:
        P.append(
            '\t(text "%s" (at %s %s 0)\n\t\t(effects (font (size 1.6 1.6) (thickness 0.3)) (justify left bottom)) (uuid "%s"))'
            % (txt, gs(x), gs(y), u()))

    P += ['\t(sheet_instances (path "/" (page "1")))', ')']
    txt = "\n".join(P) + "\n"
    assert txt.count("(") == txt.count(")"), (txt.count("("), txt.count(")"))
    open(SCH, "w").write(txt)
    print("wrote", SCH)


if __name__ == "__main__":
    main()
