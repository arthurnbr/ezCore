#!/usr/bin/env python3
"""Export JLCPCB PCBA files into fab/jlc/: gerbers+drill zip, BOM, CPL.

Usage (from anywhere):  python3 tools/export_jlc.py

- BOM: one line per LCSC part, columns Comment / Designator / Footprint / LCSC Part #.
  Parts without an LCSC field (XIAO, Wio, test pads, coil, battery pads) are left out:
  they are hand-soldered or are bare copper.
- CPL: Designator / Mid X / Mid Y / Layer / Rotation, for the same parts, in mm,
  relative to the drill/place origin. JLC_ROT corrects the few footprints whose
  KiCad zero orientation differs from JLC's reel orientation (verify in the JLC
  3D preview before ordering).
"""
import csv, os, re, subprocess, sys, zipfile, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(ROOT, "MeshTag.kicad_pcb")
OUT = os.path.join(ROOT, "fab", "jlc")

# Extra rotation (deg) to add for JLC, per footprint name.
JLC_ROT = {
    "SW_SPDT_PCM12": 0,
    "SW_Push_1P1T-SH_NO_CK_KMR2xxG": 0,
    "MagPogo_4P_P2.50mm_YZT0675": 0,
}


def run(*cmd):
    env = dict(os.environ, KIPRJMOD=ROOT)
    subprocess.run(cmd, check=True, env=env, stdout=subprocess.DEVNULL)


def gerbers():
    gdir = os.path.join(OUT, "gerbers")
    os.makedirs(gdir, exist_ok=True)
    for f in glob.glob(os.path.join(gdir, "*")):
        os.remove(f)
    run("kicad-cli", "pcb", "export", "gerbers", "--output", gdir + "/",
        "--layers", "F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts",
        "--subtract-soldermask", "--no-x2", "--use-drill-file-origin", PCB)
    run("kicad-cli", "pcb", "export", "drill", "--output", gdir + "/", "--format", "excellon",
        "--drill-origin", "plot", "--excellon-units", "mm", "--excellon-separate-th",
        "--generate-map", "--map-format", "gerberx2", PCB)
    zpath = os.path.join(OUT, "MeshTag_gerbers.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(glob.glob(os.path.join(gdir, "*"))):
            z.write(f, os.path.basename(f))
    return zpath


def parts():
    import pcbnew
    board = pcbnew.LoadBoard(PCB)
    origin = board.GetDesignSettings().GetAuxOrigin()
    rows = []
    for fp in board.GetFootprints():
        if fp.IsDNP() or not fp.HasField("LCSC"):
            continue
        name = str(fp.GetFPID().GetLibItemName())
        pos = fp.GetPosition()
        back = fp.GetLayer() == pcbnew.B_Cu
        rot = (fp.GetOrientationDegrees() + JLC_ROT.get(name, 0)) % 360
        rows.append(dict(ref=fp.GetReference(), value=fp.GetValue(), fp=name,
                         lcsc=fp.GetFieldText("LCSC"),
                         x=pcbnew.ToMM(pos.x - origin.x), y=-pcbnew.ToMM(pos.y - origin.y),
                         layer="Bottom" if back else "Top", rot=rot))
    return sorted(rows, key=lambda r: (re.sub(r"\d", "", r["ref"]), int(re.sub(r"\D", "", r["ref"]) or 0)))


def write_bom(rows):
    groups = {}
    for r in rows:
        groups.setdefault((r["lcsc"], r["value"], r["fp"]), []).append(r["ref"])
    path = os.path.join(OUT, "MeshTag_BOM_JLC.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for (lcsc, value, fp), refs in sorted(groups.items(), key=lambda kv: kv[1][0]):
            w.writerow([value, ",".join(refs), fp, lcsc])
    return path


def write_cpl(rows):
    path = os.path.join(OUT, "MeshTag_CPL_JLC.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        for r in rows:
            w.writerow([r["ref"], "%.4fmm" % r["x"], "%.4fmm" % r["y"], r["layer"], "%g" % r["rot"]])
    return path


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    rows = parts()
    print("gerbers:", gerbers())
    print("bom:", write_bom(rows))
    print("cpl:", write_cpl(rows))
    print(len(rows), "placed parts")
    sys.exit(0)
