"""Oriented-box proxies per footprint from the PCB STEP point cloud (case frame).

Prints FeatureScript map literals: {ref, cx, cy, rot, lx0, lx1, ly0, ly1, z0, z1}.
Points are assigned to the footprint whose local box contains them (smallest first).
Only points above the board top (z > 0.02) or below the board bottom (z < -1.02).
"""
import json, math
import numpy as np

d = np.load('/tmp/pcbpts.npz'); P = d['pts']
pose = json.load(open('/tmp/pose.json'))
fpbb = json.load(open('/tmp/fpbb.json'))

refs = sorted(pose, key=lambda r: (fpbb[r][2] - fpbb[r][0]) * (fpbb[r][3] - fpbb[r][1]))
taken = np.zeros(len(P), bool)
out = []
for ref in refs:
    if ref in ("AE1",) or ref.startswith("TP"):
        continue                        # copper only
    p = pose[ref]; a = math.radians(p['rot'])
    rel = P[:, :2] - np.array([p['x'], p['y']])
    c, s = math.cos(-a), math.sin(-a)
    lx = rel[:, 0] * c - rel[:, 1] * s; ly = rel[:, 0] * s + rel[:, 1] * c
    # local search window from KiCad bbox size (axis-aligned bbox is >= local size)
    hx = (fpbb[ref][2] - fpbb[ref][0]) / 2 + 1.5; hy = (fpbb[ref][3] - fpbb[ref][1]) / 2 + 1.5
    win = (np.abs(lx) < hx) & (np.abs(ly) < hy) & ~taken
    for side, zm in (("top", P[:, 2] > 0.02), ("bot", P[:, 2] < -1.02)):
        m = win & zm
        if m.sum() < 4:
            continue
        taken |= m
        out.append(dict(ref=ref + ("" if side == "top" else "_b"), cx=p['x'], cy=p['y'], rot=p['rot'],
                        lx0=lx[m].min(), lx1=lx[m].max(), ly0=ly[m].min(), ly1=ly[m].max(),
                        z0=P[m, 2].min(), z1=P[m, 2].max()))
left = (~taken) & ((P[:, 2] > 0.02) | (P[:, 2] < -1.02))
print("// unassigned points:", int(left.sum()))
for o in out:
    print('        { "ref" : "%s", "cx" : %.3f, "cy" : %.3f, "rot" : %.2f, "lx0" : %.3f, "lx1" : %.3f, "ly0" : %.3f, "ly1" : %.3f, "z0" : %.3f, "z1" : %.3f },'
          % (o['ref'], o['cx'], o['cy'], o['rot'], o['lx0'], o['lx1'], o['ly0'], o['ly1'], o['z0'], o['z1']))
json.dump(out, open('/tmp/proxies.json', 'w'))
