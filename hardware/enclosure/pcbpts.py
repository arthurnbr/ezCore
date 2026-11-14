"""Dump mesh vertices of every solid of the PCB STEP in the case frame.

Case frame: origin = board centre on board top face, +z toward components.
x = X - 150, y = Y + 100, z = Z - 1.0  (KiCad STEP export units mm).
Writes /tmp/pcbpts.npz with pts (N,3) and sid (N,) solid index, plus per-solid bbox.
"""
import sys
import numpy as np
from OCP.STEPControl import STEPControl_Reader
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID, TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location

r = STEPControl_Reader(); r.ReadFile(sys.argv[1]); r.TransferRoots()
shp = r.OneShape()
BRepMesh_IncrementalMesh(shp, 0.05, False, 0.3)
pts, sid = [], []
es = TopExp_Explorer(shp, TopAbs_SOLID)
k = 0
while es.More():
    ef = TopExp_Explorer(es.Current(), TopAbs_FACE)
    while ef.More():
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(TopoDS.Face(ef.Current()), loc)
        if tri is not None:
            t = loc.Transformation()
            for i in range(1, tri.NbNodes() + 1):
                p = tri.Node(i).Transformed(t)
                pts.append((p.X() - 150.0, p.Y() + 100.0, p.Z() - 1.0)); sid.append(k)
        ef.Next()
    k += 1
    es.Next()
pts = np.array(pts); sid = np.array(sid)
np.savez("/tmp/pcbpts.npz", pts=pts, sid=sid)
print(k, "solids", len(pts), "points", "z range", pts[:, 2].min(), pts[:, 2].max())
