"""Enclosure layout solver (case frame, mm). Prints every number the FeatureScript uses.

Frame: origin board centre, z=0 board top, +z front. Board R=25, z -1..0.
"""
import json, math
import numpy as np

d = np.load('/tmp/pcbpts.npz'); P = d['pts']
pose = json.load(open('/tmp/pose.json'))

# ---- fixed design choices ----
Ro = 26.85          # outer radius
Ri = 25.25          # cavity radius (board R 25 + 0.25)
tF = 1.4            # front skin
rf = 2.2            # outer front edge fillet
rfi = 0.9           # inner front edge fillet
Rd = 260.0          # dome sphere radius
CLR = 0.30          # min clearance skin <-> component
J5 = pose['J5']


def j5_local(x, y):
    a = math.radians(J5['rot']); c, s = math.cos(-a), math.sin(-a)
    dx, dy = x - J5['x'], y - J5['y']
    return dx * c - dy * s, dx * s + dy * c


def in_obround(lx, ly, half_straight, rad):
    return math.hypot(max(abs(lx) - half_straight, 0.0), ly) <= rad


def outer_z(r, za):
    csz = za - Rd
    # torus centre (Ro-rf, zc) tangent to sphere internally
    cx = Ro - rf
    zc = csz + math.sqrt((Rd - rf) ** 2 - cx ** 2)
    v = np.array([cx, zc - csz]) / (Rd - rf)
    rT = Rd * v[0]
    if r <= rT:
        return csz + math.sqrt(Rd ** 2 - r * r), zc, rT
    if r <= Ro:
        return zc + math.sqrt(max(rf ** 2 - (r - cx) ** 2, 0)), zc, rT
    return None, zc, rT


def inner_z(r, za):
    csz = za - Rd; R2 = Rd - tF
    cx = Ri - rfi
    zci = csz + math.sqrt((R2 - rfi) ** 2 - cx ** 2)
    v = np.array([cx, zci - csz]) / (R2 - rfi)
    rT = R2 * v[0]
    if r <= rT:
        return csz + math.sqrt(R2 ** 2 - r * r), zci, rT
    if r <= Ri:
        return zci + math.sqrt(max(rfi ** 2 - (r - cx) ** 2, 0)), zci, rT
    return None, zci, rT


above = P[P[:, 2] > 0.02]
rr = np.hypot(above[:, 0], above[:, 1])
j5mask = np.array([in_obround(*j5_local(x, y), 10.8, 6.2) for x, y in above[:, :2]])
other = above[~j5mask]; ro_ = rr[~j5mask]


def min_clear(za):
    zi = np.array([inner_z(r, za)[0] for r in ro_])
    c = zi - other[:, 2]
    i = int(np.argmin(c)); return c[i], other[i]

za = 3.0
while min_clear(za)[0] < CLR:
    za += 0.01
za = math.ceil(za * 20) / 20
c, p = min_clear(za)
zo0, zc, rT = outer_z(0, za)
zi0, zci, rTi = inner_z(0, za)
print("APEX za=%.2f  min clr %.3f at %s" % (za, c, np.round(p, 2)))
print("outer: fillet centre zc=%.3f (wall top), sphere->torus r=%.3f, edge z at Ro=%.3f" % (zc, rT, zc))
print("inner: zci=%.3f rTi=%.3f, inner apex %.3f" % (zci, rTi, zi0))

# J5 recess depth over the J5 top obround (+0.25)
deps = []
for a in np.linspace(0, 2 * math.pi, 90):
    for k in (0.0, 0.5, 1.0):
        pass
pts = []
for lx in np.linspace(-10.85, 10.85, 60):
    for ly in np.linspace(-3.68, 3.68, 15):
        if in_obround(lx, ly, 7.17, 3.68):
            a = math.radians(J5['rot']); c_, s_ = math.cos(a), math.sin(a)
            x = J5['x'] + lx * c_ - ly * s_; y = J5['y'] + lx * s_ + ly * c_
            r = math.hypot(x, y)
            z = outer_z(r, za)[0]
            pts.append((r, None if z is None else z - 2.8))
ds = [p[1] for p in pts if p[1] is not None]
print("J5 recess depth over plug outline: min %.2f max %.2f  max r %.2f (Ro %.2f)" % (min(ds), max(ds), max(p[0] for p in pts), Ro))
# skin under J5 recess ring: inner z at J5 r range
for r in (16.5, 20, 23, 24.5):
    print("  r=%.1f outer %.2f inner %.2f" % (r, outer_z(r, za)[0], inner_z(r, za)[0]))

# ---- button SW1 ----
sw = pose['SW1']; R_sw = math.hypot(sw['x'], sw['y'])
m = np.hypot(above[:, 0] - sw['x'], above[:, 1] - sw['y'])
act = above[m < 1.05]; ann = above[(m >= 1.05) & (m < 4.4)]
print("SW1 r=%.2f actuator top %.3f; max z under flange annulus (r<4.4) %.3f; outer %.3f inner %.3f"
      % (R_sw, act[:, 2].max(), ann[:, 2].max(), outer_z(R_sw, za)[0], inner_z(R_sw, za)[0]))
# ---- LEDs ----
lx_, ly_ = (pose['D1']['x'] + pose['D2']['x']) / 2, (pose['D1']['y'] + pose['D2']['y']) / 2
R_led = math.hypot(lx_, ly_)
m = np.hypot(above[:, 0] - lx_, above[:, 1] - ly_)
print("LED mid (%.3f,%.3f) r=%.2f; max z within 1.4 %.3f; outer %.3f inner %.3f" % (lx_, ly_, R_led, above[m < 1.4][:, 2].max(), outer_z(R_led, za)[0], inner_z(R_led, za)[0]))
# ---- locating pin through old keyring hole (-15.2, 15.2) ----
hx, hy = -15.2, 15.2
m = np.hypot(above[:, 0] - hx, above[:, 1] - hy)
print("pin hole r=%.2f, max z of parts within 3.2: %s; inner %.3f" % (math.hypot(hx, hy), (above[m < 3.2][:, 2].max() if (m < 3.2).any() else None), inner_z(math.hypot(hx, hy), za)[0]))
# ---- ledge ring r 24.3..Ri, z>=0: angles with parts ----
m = (rr > 24.0) & (above[:, 2] > 0.02)
angs = sorted(set(int(math.degrees(math.atan2(y, x)) % 360) for x, y in above[m][:, :2]))
print("parts at r>24.0 (angles):", angs)
# ---- slider: SW3 frame ----
s3 = pose['SW3']; a = math.radians(s3['rot'])
rel = above[:, :2] - np.array([s3['x'], s3['y']]); c_, s_ = math.cos(-a), math.sin(-a)
u = rel[:, 0] * c_ - rel[:, 1] * s_; v = rel[:, 0] * s_ + rel[:, 1] * c_
corr = (np.abs(u) < 4.0) & (v < -2.55) & (v > -10)
print("slider corridor |u|<4, v<-2.55: n=%d" % corr.sum(), "zmax", above[corr][:, 2].max() if corr.any() else None)
print("SW3 centre r=%.3f; inner z at r 21.4 %.3f, 24.5 %.3f, 25.25 %.3f" % (math.hypot(s3['x'], s3['y']), inner_z(21.4, za)[0], inner_z(24.5, za)[0], inner_z(25.2, za)[0]))
json.dump(dict(za=za, zc=zc, zci=zci, Ro=Ro, Ri=Ri, tF=tF, rf=rf, rfi=rfi, Rd=Rd), open('/tmp/design.json', 'w'))
