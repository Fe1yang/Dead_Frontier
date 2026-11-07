"""Detailed props for the cabin set. Every function appends to material groups in `gs`."""

import math
import random
from math import pi, sin, cos, tau, radians
from mathutils import Vector, Euler
import cabin_prims as P


def xf(center, rot, local):
    return Vector(center) + Euler(rot, "XYZ").to_matrix() @ Vector(local)


def rnd(a, b):
    return random.uniform(a, b)


def can(gs, center, radius=0.043, height=0.115, label="label_red", rot=(0, 0, 0), ribs=3):
    iron = gs["iron"]
    body = gs["steel"]
    lab = gs[label]
    P.cylinder(body, center, radius, height, rot=rot, segments=24, tile=0.16)
    P.cylinder(lab, center, radius * 1.012, height * 0.58, rot=rot, segments=24, tile=0.16)
    for z in (-height * 0.5 + 0.004, height * 0.5 - 0.004):
        P.torus(iron, xf(center, rot, (0, 0, z)), radius * 1.01, 0.005,
                rot=rot, major_seg=24, minor_seg=6, tile=0.2)
    for i in range(ribs):
        z = -height * 0.22 + i * height * 0.22
        P.torus(iron, xf(center, rot, (0, 0, z)), radius * 1.005, 0.0018,
                rot=rot, major_seg=24, minor_seg=4, tile=0.2)
    # pull tab
    top = xf(center, rot, (0, 0, height * 0.5 + 0.002))
    P.torus(iron, top, radius * 0.30, 0.0035, rot=rot, major_seg=14, minor_seg=4, tile=0.2)
    P.box(iron, xf(center, rot, (0, -radius * 0.45, height * 0.5 + 0.002)),
          (radius * 0.42, radius * 0.20, 0.004), rot=rot, bevel=0.001, tile=0.2)


def jar(gs, center, radius=0.055, height=0.13, fill="paper", rot=(0, 0, 0), lid="iron"):
    glass = gs["glass"]
    profile = [(radius * 0.92, 0), (radius, 0.012), (radius, height * 0.82),
               (radius * 0.94, height * 0.90), (radius * 0.82, height * 0.96),
               (radius * 0.80, height)]
    P.lathe(glass, profile, center=center, segments=28, rot=rot, tile=0.25)
    # contents: a few blobs on the bottom
    for i in range(7):
        a = rnd(0, tau)
        r = rnd(0, radius * 0.62)
        P.sphere(gs[fill], xf(center, rot, (cos(a) * r, sin(a) * r, rnd(0.018, height * 0.55))),
                 (radius * rnd(0.16, 0.30), radius * rnd(0.13, 0.24), radius * rnd(0.12, 0.25)),
                 subdiv=1, tile=0.2, rot=(0, 0, a))
    # lid + knurled rim
    P.cylinder(gs[lid], xf(center, rot, (0, 0, height + 0.012)), radius * 0.86, 0.024,
               rot=rot, segments=28, tile=0.25)
    for i in range(12):
        a = tau * i / 12
        P.box(gs[lid], xf(center, rot, (cos(a) * radius * 0.86, sin(a) * radius * 0.86, height + 0.012)),
              (0.007, 0.007, 0.022), rot=(rot[0], rot[1], rot[2] + a), bevel=0.001, tile=0.2)
    # paper label band
    P.cylinder(gs["paper_old"], xf(center, rot, (0, 0, height * 0.42)), radius * 1.008, height * 0.23,
               rot=rot, segments=28, tile=0.25)


def bottle(gs, center, radius=0.042, height=0.24, glass="glass_green", rot=(0, 0, 0)):
    prof = [(radius * 0.92, 0), (radius, 0.012), (radius, height * 0.48),
            (radius * 0.92, height * 0.60), (radius * 0.48, height * 0.72),
            (radius * 0.30, height * 0.82), (radius * 0.29, height * 0.94),
            (radius * 0.36, height * 0.96), (radius * 0.34, height)]
    P.lathe(gs[glass], prof, center=center, segments=28, rot=rot, tile=0.3)
    P.cylinder(gs["cord"], xf(center, rot, (0, 0, height + 0.012)), radius * 0.30, 0.025,
               rot=rot, segments=16, tile=0.1)
    P.cylinder(gs["paper"], xf(center, rot, (0, 0, height * 0.34)), radius * 1.012, height * 0.22,
               rot=rot, segments=28, tile=0.3)
    # neck band
    P.torus(gs["brass"], xf(center, rot, (0, 0, height * 0.86)), radius * 0.31, 0.003,
            rot=rot, major_seg=18, minor_seg=4, tile=0.2)


def crate(gs, center, size=(0.52, 0.42, 0.34), rot=(0, 0, 0), lidded=False):
    wood = gs["wall"]
    iron = gs["iron_dark"]
    sx, sy, sz = size
    # corner battens and frame
    for ax in (-1, 1):
        for ay in (-1, 1):
            P.box(wood, xf(center, rot, (ax * sx * 0.46, ay * sy * 0.46, 0)),
                  (0.045, 0.045, sz), rot=rot, bevel=0.006, tile=1.0, grain="Z")
    # side boards with gaps
    boards = 5
    for side in (-1, 1):
        for k in range(boards):
            z = -sz * 0.5 + sz * (k + 0.5) / boards
            P.box(wood, xf(center, rot, (0, side * sy * 0.49, z)),
                  (sx * 0.92, 0.025, sz / boards * 0.84), rot=rot,
                  bevel=0.004, tile=1.0, grain="X")
        for k in range(boards):
            z = -sz * 0.5 + sz * (k + 0.5) / boards
            P.box(wood, xf(center, rot, (side * sx * 0.49, 0, z)),
                  (0.025, sy * 0.92, sz / boards * 0.84), rot=rot,
                  bevel=0.004, tile=1.0, grain="Y")
    # top and bottom slats
    for z in (-sz * 0.5, sz * 0.5):
        for k in range(4):
            y = -sy * 0.36 + sy * 0.24 * k
            P.box(wood, xf(center, rot, (0, y, z)),
                  (sx * 0.94, sy * 0.21, 0.022), rot=rot,
                  bevel=0.004, tile=1.0, grain="X")
    # diagonal front brace
    P.box(wood, xf(center, rot, (0, -sy * 0.52, 0)),
          (sx * 0.88, 0.02, 0.045), rot=(rot[0], rot[1], rot[2] + radians(34.0)),
          bevel=0.003, tile=1.0, grain="X")
    # nails
    for ax in (-1, 1):
        for az in (-1, 1):
            P.cylinder(iron, xf(center, rot, (ax * sx * 0.44, -sy * 0.515, az * sz * 0.36)),
                       0.006, 0.008, rot=(pi * 0.5, 0, 0), segments=8, tile=0.1)
    # stencil: a pale stencilled block on the front
    P.quad(gs["paper_old"], [
        xf(center, rot, (-sx * 0.18, -sy * 0.525, -sz * 0.10)),
        xf(center, rot, (sx * 0.18, -sy * 0.525, -sz * 0.10)),
        xf(center, rot, (sx * 0.18, -sy * 0.525, sz * 0.12)),
        xf(center, rot, (-sx * 0.18, -sy * 0.525, sz * 0.12)),
    ], uv_rect=(0, 0, 1, 1))
    for i in range(3):
        P.box(gs["ink"], xf(center, rot, (-sx * 0.10 + i * sx * 0.10, -sy * 0.527, 0)),
              (sx * 0.055, 0.002, sz * 0.10), rot=rot, tile=1.0)


def barrel(gs, center, radius=0.29, height=0.82, rot=(0, 0, 0), bung=True):
    wood = gs["wall"]
    iron = gs["rust"]
    # bulged body
    prof = [(radius * 0.86, 0), (radius * 0.98, height * 0.10),
            (radius, height * 0.50), (radius * 0.98, height * 0.90),
            (radius * 0.86, height)]
    P.lathe(wood, prof, center=center, segments=32, rot=rot, tile=1.0)
    # raised staves
    for i in range(20):
        a = tau * i / 20
        r = radius * 1.005
        P.box(wood, xf(center, rot, (cos(a) * r, sin(a) * r, height * 0.5)),
              (0.016, 0.032, height * 0.93), rot=(rot[0], rot[1], rot[2] + a + pi * 0.5),
              bevel=0.003, tile=1.0, grain="Z")
    # iron hoops
    for z, r in ((height * 0.10, radius * 0.985), (height * 0.50, radius * 1.015),
                 (height * 0.90, radius * 0.985)):
        P.torus(iron, xf(center, rot, (0, 0, z)), r, 0.012,
                rot=rot, major_seg=32, minor_seg=8, tile=0.5)
    # lids + bung
    P.disk(gs["endgrain"], xf(center, rot, (0, 0, height + 0.001)), radius * 0.84,
           rot=rot, segments=32, tile=1.0)
    P.disk(gs["endgrain"], xf(center, rot, (0, 0, -0.001)), radius * 0.84,
           rot=rot, segments=32, tile=1.0)
    if bung:
        P.cylinder(iron, xf(center, rot, (radius * 0.42, 0, height + 0.012)),
                   0.025, 0.018, rot=rot, segments=12, tile=0.2)


def book(gs, center, size=(0.17, 0.24, 0.045), rot=(0, 0, 0), cover="leather"):
    sx, sy, sz = size
    P.box(gs[cover], center, (sx, sy, sz), rot=rot, bevel=0.004, tile=0.25)
    P.box(gs["paper"], xf(center, rot, (0.004, 0, 0)),
          (sx * 0.88, sy * 0.94, sz * 0.72), rot=rot, bevel=0.001, tile=0.4)
    for i in range(3):
        P.box(gs["paper_old"], xf(center, rot, (sx * 0.03, 0, -sz * 0.30 + i * sz * 0.22)),
              (sx * 0.80, sy * 0.92, 0.002), rot=rot, tile=0.4)
    P.box(gs["brass"], xf(center, rot, (0, 0, sz * 0.52)),
          (sx * 0.35, sy * 0.20, 0.003), rot=rot, bevel=0.001, tile=0.2)


def radio(gs, center, rot=(0, 0, 0), scale=1.0):
    s = scale
    w = gs["wall"]
    iron = gs["iron_dark"]
    P.box(w, center, (0.28 * s, 0.13 * s, 0.19 * s), rot=rot, bevel=0.015, seg=2, tile=1.0)
    # speaker grille on the front (-Y)
    front = xf(center, rot, (0, -0.068 * s, 0.012 * s))
    P.box(iron, front, (0.14 * s, 0.008 * s, 0.12 * s), rot=rot, bevel=0.003, tile=0.3)
    for i in range(9):
        z = (i - 4) * 0.011 * s
        P.box(gs["steel"], xf(center, rot, (0, -0.073 * s, 0.012 * s + z)),
              (0.125 * s, 0.004 * s, 0.003 * s), rot=rot, tile=0.2)
    # dial
    dc = xf(center, rot, (0.082 * s, -0.069 * s, 0.038 * s))
    P.cylinder(gs["brass"], dc, 0.032 * s, 0.006 * s, rot=(pi * 0.5, 0, 0) if rot == (0, 0, 0) else rot,
               segments=24, tile=0.2)
    P.cylinder(gs["paper"], xf(center, rot, (0.082 * s, -0.074 * s, 0.038 * s)),
               0.027 * s, 0.002 * s, rot=(pi * 0.5, 0, 0), segments=24, tile=0.2)
    P.box(gs["ink"], xf(center, rot, (0.082 * s, -0.076 * s, 0.048 * s)),
          (0.002 * s, 0.002 * s, 0.023 * s), rot=rot, tile=0.2)
    # knobs
    for kx in (-0.075, 0.0):
        P.cylinder(gs["iron"], xf(center, rot, (kx * s, -0.072 * s, -0.055 * s)),
                   0.018 * s, 0.014 * s, rot=(pi * 0.5, 0, 0), segments=16, tile=0.15)
    # handle and antenna
    P.tube(gs["leather"], [
        xf(center, rot, (-0.10 * s, 0, 0.10 * s)),
        xf(center, rot, (-0.07 * s, 0, 0.16 * s)),
        xf(center, rot, (0.07 * s, 0, 0.16 * s)),
        xf(center, rot, (0.10 * s, 0, 0.10 * s)),
    ], 0.012 * s, sides=6, tile=0.2)
    P.cylinder(gs["steel"], xf(center, rot, (0.12 * s, 0.02 * s, 0.20 * s)),
               0.003 * s, 0.32 * s, rot=(0.22, 0, -0.15), segments=6, tile=0.2)


def lantern(gs, center, scale=1.0, rot=(0, 0, 0), lit=True, hanging=True):
    s = scale
    iron = gs["iron_dark"]
    brass = gs["brass"]
    base = [(0.0, 0.0), (0.10 * s, 0.0), (0.105 * s, 0.02 * s),
            (0.085 * s, 0.055 * s), (0.055 * s, 0.07 * s)]
    P.lathe(iron, base, center=center, segments=24, rot=rot, tile=0.3)
    # glass globe
    globe = [(0.050 * s, 0.07 * s), (0.078 * s, 0.13 * s), (0.082 * s, 0.20 * s),
             (0.070 * s, 0.27 * s), (0.042 * s, 0.32 * s), (0.035 * s, 0.34 * s)]
    P.lathe(gs["glass"], globe, center=center, segments=24, rot=rot, tile=0.3)
    P.cylinder(iron, xf(center, rot, (0, 0, 0.36 * s)), 0.055 * s, 0.035 * s,
               rot=rot, segments=24, tile=0.3)
    P.cylinder(iron, xf(center, rot, (0, 0, 0.385 * s)), 0.022 * s, 0.012 * s,
               rot=rot, segments=16, tile=0.3)
    # guard wires
    for i in range(4):
        a = tau * i / 4
        P.tube(iron, [
            xf(center, rot, (cos(a) * 0.083 * s, sin(a) * 0.083 * s, 0.09 * s)),
            xf(center, rot, (cos(a) * 0.087 * s, sin(a) * 0.087 * s, 0.22 * s)),
            xf(center, rot, (cos(a) * 0.058 * s, sin(a) * 0.058 * s, 0.36 * s)),
        ], 0.004 * s, sides=5, tile=0.2)
    # handle
    P.tube(iron, [
        xf(center, rot, (-0.045 * s, 0, 0.39 * s)),
        xf(center, rot, (-0.06 * s, 0, 0.47 * s)),
        xf(center, rot, (0.0, 0, 0.52 * s)),
        xf(center, rot, (0.06 * s, 0, 0.47 * s)),
        xf(center, rot, (0.045 * s, 0, 0.39 * s)),
    ], 0.008 * s, sides=6, tile=0.2)
    if lit:
        P.sphere(gs["lamp_glow"], xf(center, rot, (0, 0, 0.21 * s)),
                 (0.034 * s, 0.034 * s, 0.065 * s), subdiv=2, tile=0.2)
        P.sphere(gs["flame"], xf(center, rot, (0, 0, 0.17 * s)),
                 (0.016 * s, 0.016 * s, 0.048 * s), subdiv=2, tile=0.2)
    if hanging:
        P.tube(iron, [xf(center, rot, (0, 0, 0.52 * s)), xf(center, rot, (0, 0, 0.75 * s))],
               0.004 * s, sides=5, tile=0.2)


def oil_can(gs, center, scale=1.0, rot=(0, 0, 0)):
    s = scale
    body = [(0.0, 0.0), (0.10 * s, 0.0), (0.105 * s, 0.03 * s), (0.10 * s, 0.22 * s),
            (0.06 * s, 0.28 * s), (0.05 * s, 0.30 * s)]
    P.lathe(gs["rust"], body, center=center, segments=24, rot=rot, tile=0.35)
    P.cylinder(gs["brass"], xf(center, rot, (0, 0, 0.31 * s)), 0.025 * s, 0.04 * s,
               rot=rot, segments=12, tile=0.2)
    P.tube(gs["brass"], [
        xf(center, rot, (0.0, 0, 0.32 * s)),
        xf(center, rot, (0.08 * s, 0, 0.38 * s)),
        xf(center, rot, (0.18 * s, 0, 0.43 * s)),
    ], 0.008 * s, sides=6, tile=0.2)
    P.tube(gs["iron"], [
        xf(center, rot, (-0.09 * s, 0, 0.25 * s)),
        xf(center, rot, (-0.14 * s, 0, 0.18 * s)),
        xf(center, rot, (-0.09 * s, 0, 0.10 * s)),
    ], 0.008 * s, sides=5, tile=0.2)


def mug(gs, center, scale=1.0, rot=(0, 0, 0), enamel="ceramic", liquid=True):
    s = scale
    prof = [(0.0, 0.0), (0.038 * s, 0.0), (0.043 * s, 0.008 * s),
            (0.045 * s, 0.105 * s), (0.043 * s, 0.11 * s)]
    P.lathe(gs[enamel], prof, center=center, segments=24, rot=rot, tile=0.2)
    P.tube(gs["ceramic_blue"] if enamel != "ceramic_blue" else gs["ceramic"], [
        xf(center, rot, (0.042 * s, 0, 0.082 * s)),
        xf(center, rot, (0.070 * s, 0, 0.070 * s)),
        xf(center, rot, (0.072 * s, 0, 0.035 * s)),
        xf(center, rot, (0.042 * s, 0, 0.020 * s)),
    ], 0.006 * s, sides=6, tile=0.15)
    if liquid:
        P.disk(gs["ink"], xf(center, rot, (0, 0, 0.096 * s)), 0.038 * s, rot=rot,
               segments=20, tile=0.2)


def plate(gs, center, scale=1.0, rot=(0, 0, 0)):
    s = scale
    P.lathe(gs["ceramic"], [(0.0, 0.0), (0.085 * s, 0.0), (0.10 * s, 0.012 * s),
                            (0.092 * s, 0.018 * s), (0.075 * s, 0.012 * s)],
            center=center, segments=24, rot=rot, tile=0.2)


def hammer(gs, center, rot=(0, 0, 0), length=0.30, scale=1.0):
    s = scale
    P.cylinder(gs["wall"], xf(center, rot, (0, 0, 0)), 0.014 * s, length,
               rot=(rot[0], rot[1], rot[2] + pi * 0.5), segments=12, tile=0.5)
    P.box(gs["iron"], xf(center, rot, (length * 0.48, 0, 0)), (0.07 * s, 0.035 * s, 0.035 * s),
          rot=rot, bevel=0.004, tile=0.2)
    P.cylinder(gs["iron"], xf(center, rot, (length * 0.48, 0.023 * s, 0)),
               0.018 * s, 0.012 * s, rot=(pi * 0.5, 0, 0), segments=12, tile=0.15)


def screwdriver(gs, center, rot=(0, 0, 0), length=0.20, scale=1.0):
    s = scale
    P.cylinder(gs["label_red"], xf(center, rot, (-0.07 * s, 0, 0)), 0.015 * s, 0.075 * s,
               rot=(rot[0], rot[1], rot[2] + pi * 0.5), segments=12, tile=0.2)
    P.cylinder(gs["steel"], xf(center, rot, (0.06 * s, 0, 0)), 0.004 * s, length,
               rot=(rot[0], rot[1], rot[2] + pi * 0.5), segments=8, tile=0.2)
    P.box(gs["steel"], xf(center, rot, (0.16 * s, 0, 0)), (0.012 * s, 0.002 * s, 0.008 * s),
          rot=rot, tile=0.2)


def wrench(gs, center, rot=(0, 0, 0), length=0.22, scale=1.0):
    s = scale
    P.box(gs["steel"], center, (length, 0.018 * s, 0.028 * s), rot=rot, bevel=0.005, tile=0.2)
    for xx in (-length * 0.5, length * 0.5):
        P.cylinder(gs["steel"], xf(center, rot, (xx, 0, 0)), 0.030 * s, 0.018 * s,
                   rot=(pi * 0.5, 0, 0), segments=16, tile=0.2)
        P.box(gs["wall"], xf(center, rot, (xx, 0, 0)), (0.020 * s, 0.026 * s, 0.040 * s),
              rot=rot, tile=0.5)
    P.box(gs["ink"], xf(center, rot, (-length * 0.50, 0, 0.012 * s)),
          (0.014 * s, 0.021 * s, 0.020 * s), rot=rot, tile=0.2)
    P.box(gs["ink"], xf(center, rot, (length * 0.50, 0, 0.012 * s)),
          (0.014 * s, 0.021 * s, 0.020 * s), rot=rot, tile=0.2)


def saw(gs, center, rot=(0, 0, 0), length=0.48, scale=1.0):
    s = scale
    # blade with teeth
    pts = [(-length * 0.5, 0), (length * 0.5, 0), (length * 0.5, 0.10 * s),
           (-length * 0.44, 0.13 * s), (-length * 0.5, 0.10 * s)]
    P.extrude_xz(gs["steel"], pts, 0.0, 0.006 * s, tile=0.2)
    # teeth
    for i in range(18):
        x = -length * 0.45 + length * 0.90 * i / 17.0
        P.box(gs["steel"], (x, 0, -0.006 * s), (0.012 * s, 0.006 * s, 0.014 * s),
              rot=(0, 0, radians(45)), tile=0.2)
    # handle
    P.box(gs["wall"], (-length * 0.43, 0, 0.13 * s), (0.10 * s, 0.035 * s, 0.10 * s),
          rot=(0, 0, radians(-8)), bevel=0.015, tile=0.5)
    P.box(gs["wall"], (-length * 0.30, 0, 0.17 * s), (0.16 * s, 0.030 * s, 0.055 * s),
          rot=(0, 0, radians(-8)), bevel=0.012, tile=0.5)


def hatchet(gs, center, rot=(0, 0, 0), length=0.34, scale=1.0):
    s = scale
    P.cylinder(gs["wall"], xf(center, rot, (0, 0, -length * 0.5)), 0.012 * s, length,
               rot=rot, segments=12, tile=0.5)
    P.box(gs["iron"], xf(center, rot, (0.05 * s, 0, 0)), (0.09 * s, 0.025 * s, 0.075 * s),
          rot=rot, bevel=0.005, tile=0.2)
    P.box(gs["steel"], xf(center, rot, (0.105 * s, 0, 0)), (0.05 * s, 0.006 * s, 0.09 * s),
          rot=(rot[0], rot[1], rot[2] + radians(8)), tile=0.2)
    P.box(gs["iron"], xf(center, rot, (-0.04 * s, 0, 0)), (0.03 * s, 0.030 * s, 0.045 * s),
          rot=rot, bevel=0.004, tile=0.2)


def boots(gs, center, rot=(0, 0, 0), scale=1.0, spread=0.16):
    s = scale
    for side in (-1, 1):
        base = xf(center, rot, (side * spread * 0.5, 0, 0))
        r2 = (rot[0], rot[1], rot[2] + side * radians(5.0))
        # sole and heel
        P.box(gs["leather"], xf(base, r2, (0, -0.03 * s, 0.028 * s)),
              (0.105 * s, 0.27 * s, 0.035 * s), rot=r2, bevel=0.012, tile=0.4)
        P.box(gs["leather"], xf(base, r2, (0, 0.08 * s, 0.065 * s)),
              (0.10 * s, 0.09 * s, 0.06 * s), rot=r2, bevel=0.01, tile=0.4)
        # upper: shaft + instep + toe
        P.box(gs["leather"], xf(base, r2, (0, 0.07 * s, 0.20 * s)),
              (0.095 * s, 0.11 * s, 0.22 * s), rot=r2, bevel=0.018, seg=2, tile=0.4)
        P.sphere(gs["leather"], xf(base, r2, (0, -0.035 * s, 0.095 * s)),
                 (0.052 * s, 0.11 * s, 0.055 * s), rot=r2, subdiv=2, tile=0.4)
        P.sphere(gs["leather"], xf(base, r2, (0, -0.115 * s, 0.055 * s)),
                 (0.050 * s, 0.07 * s, 0.036 * s), rot=r2, subdiv=2, tile=0.4)
        # cuff
        P.torus(gs["leather"], xf(base, r2, (0, 0.07 * s, 0.31 * s)), 0.055 * s, 0.012 * s,
                rot=(r2[0] + pi * 0.5, r2[1], r2[2]), major_seg=20, minor_seg=6, tile=0.4)
        # laces
        for i in range(4):
            z = 0.15 * s + i * 0.035 * s
            P.tube(gs["cord"], [
                xf(base, r2, (-0.036 * s, 0.012 * s, z)),
                xf(base, r2, (0.0, 0.006 * s, z + 0.008 * s)),
                xf(base, r2, (0.036 * s, 0.012 * s, z)),
            ], 0.0022 * s, sides=4, tile=0.1)
            for sx in (-1, 1):
                P.torus(gs["brass"], xf(base, r2, (sx * 0.038 * s, 0.010 * s, z)),
                        0.004 * s, 0.0015 * s, rot=(r2[0] + pi * 0.5, r2[1], r2[2]),
                        major_seg=8, minor_seg=4, tile=0.1)


def backpack(gs, center, rot=(0, 0, 0), scale=1.0):
    s = scale
    P.sphere(gs["burlap"], center, (0.20 * s, 0.13 * s, 0.30 * s), rot=rot, subdiv=2, tile=0.5)
    P.sphere(gs["burlap"], xf(center, rot, (0, 0.10 * s, -0.06 * s)),
             (0.16 * s, 0.10 * s, 0.18 * s), rot=rot, subdiv=2, tile=0.5)
    # flap
    P.box(gs["leather"], xf(center, rot, (0, -0.10 * s, 0.14 * s)),
          (0.27 * s, 0.10 * s, 0.12 * s), rot=(rot[0] + radians(10), rot[1], rot[2]),
          bevel=0.015, tile=0.4)
    # straps and buckles
    for sx in (-1, 1):
        P.tube(gs["leather"], [
            xf(center, rot, (sx * 0.11 * s, -0.12 * s, 0.12 * s)),
            xf(center, rot, (sx * 0.13 * s, -0.14 * s, -0.04 * s)),
            xf(center, rot, (sx * 0.12 * s, -0.12 * s, -0.20 * s)),
        ], 0.012 * s, sides=5, tile=0.3)
        P.box(gs["brass"], xf(center, rot, (sx * 0.12 * s, -0.15 * s, -0.08 * s)),
              (0.03 * s, 0.015 * s, 0.025 * s), rot=rot, bevel=0.002, tile=0.2)
    # bedroll on top
    P.cylinder(gs["wool"], xf(center, rot, (0, 0, 0.33 * s)), 0.075 * s, 0.46 * s,
               rot=(rot[0], rot[1] + pi * 0.5, rot[2]), segments=16, tile=0.3)
    P.tube(gs["cord"], [
        xf(center, rot, (-0.15 * s, 0, 0.33 * s)),
        xf(center, rot, (-0.15 * s, 0, 0.25 * s)),
        xf(center, rot, (-0.15 * s, 0, 0.41 * s)),
    ], 0.006 * s, sides=4, tile=0.1)


def rifle(gs, center, rot=(0, 0, 0), scale=1.0):
    """Wall-mounted lever rifle in the XZ plane, barrel to the right."""
    s = scale
    # stock silhouette in local XZ
    stock = [(-0.52, -0.05), (-0.55, 0.02), (-0.50, 0.08), (-0.40, 0.11),
             (-0.22, 0.10), (-0.12, 0.06), (-0.05, 0.035), (-0.02, 0.02),
             (0.08, 0.018), (0.18, 0.022), (0.24, 0.040), (0.20, 0.075),
             (-0.03, 0.075), (-0.10, 0.09), (-0.24, 0.13), (-0.38, 0.14),
             (-0.48, 0.12)]
    R = Euler(rot, "XYZ").to_matrix()
    pts = []
    for (x, z) in stock:
        p = Vector(center) + R @ Vector((x * s, 0, z * s))
        pts.append((p.x, p.z))
    P.extrude_xz(gs["wall"], pts, center[1], 0.045 * s, bevel=0.003, tile=0.8)
    # receiver + barrel + tube
    P.box(gs["iron"], xf(center, rot, (0.0, 0, 0.055 * s)), (0.22 * s, 0.05 * s, 0.07 * s),
          rot=rot, bevel=0.005, tile=0.3)
    P.cylinder(gs["steel"], xf(center, rot, (0.42 * s, 0, 0.06 * s)), 0.014 * s, 0.62 * s,
               rot=(0, pi * 0.5, 0), segments=16, tile=0.4)
    P.cylinder(gs["steel"], xf(center, rot, (0.26 * s, 0, 0.035 * s)), 0.020 * s, 0.40 * s,
               rot=(0, pi * 0.5, 0), segments=16, tile=0.4)
    # lever loop
    P.tube(gs["steel"], [
        xf(center, rot, (-0.02 * s, 0, 0.02 * s)),
        xf(center, rot, (0.00 * s, 0, -0.06 * s)),
        xf(center, rot, (0.07 * s, 0, -0.08 * s)),
        xf(center, rot, (0.12 * s, 0, -0.01 * s)),
    ], 0.007 * s, sides=5, tile=0.2)
    # sights and hammer
    P.box(gs["steel"], xf(center, rot, (0.70 * s, 0, 0.085 * s)),
          (0.012 * s, 0.02 * s, 0.018 * s), rot=rot, tile=0.2)
    P.box(gs["steel"], xf(center, rot, (0.16 * s, 0, 0.10 * s)),
          (0.018 * s, 0.02 * s, 0.020 * s), rot=rot, tile=0.2)
    # leather sling, hanging in a loose loop
    P.tube(gs["leather"], [
        xf(center, rot, (-0.40 * s, 0, 0.10 * s)),
        xf(center, rot, (-0.30 * s, 0, 0.27 * s)),
        xf(center, rot, (0.28 * s, 0, 0.28 * s)),
        xf(center, rot, (0.54 * s, 0, 0.08 * s)),
    ], 0.012 * s, sides=5, tile=0.4)


def antlers(gs, center, rot=(0, 0, 0), scale=1.0):
    s = scale
    # plaque
    P.sphere(gs["wall"], xf(center, rot, (0, 0.04 * s, 0)),
             (0.20 * s, 0.025 * s, 0.15 * s), rot=rot, subdiv=2, tile=0.8)
    P.sphere(gs["bone"], xf(center, rot, (0, 0.01 * s, -0.02 * s)),
             (0.10 * s, 0.05 * s, 0.09 * s), rot=rot, subdiv=2, tile=0.5)
    # antler beams
    for side in (-1, 1):
        base = xf(center, rot, (side * 0.04 * s, 0, 0.02 * s))
        main = [
            xf(center, rot, (side * 0.04 * s, 0, 0.03 * s)),
            xf(center, rot, (side * 0.10 * s, 0, 0.14 * s)),
            xf(center, rot, (side * 0.18 * s, 0, 0.26 * s)),
            xf(center, rot, (side * 0.22 * s, 0, 0.40 * s)),
            xf(center, rot, (side * 0.19 * s, 0, 0.52 * s)),
        ]
        P.tube(gs["bone"], main, [0.026 * s, 0.022 * s, 0.018 * s, 0.014 * s, 0.008 * s],
               sides=7, tile=0.3)
        branches = [
            [(side * 0.09, 0, 0.16), (side * 0.16, 0, 0.21), (side * 0.21, 0, 0.30)],
            [(side * 0.15, 0, 0.23), (side * 0.27, 0, 0.27), (side * 0.32, 0, 0.35)],
            [(side * 0.19, 0, 0.33), (side * 0.29, 0, 0.39), (side * 0.33, 0, 0.47)],
        ]
        for br in branches:
            pts = [xf(center, rot, (x, 0, z)) for (x, _y, z) in br]
            P.tube(gs["bone"], pts, [0.012 * s, 0.009 * s, 0.004 * s], sides=6, tile=0.3)
    # a couple of iron nails in the plaque
    for sx in (-1, 1):
        P.cylinder(gs["iron"], xf(center, rot, (sx * 0.16 * s, 0.065 * s, 0)),
                   0.008 * s, 0.01 * s, rot=(pi * 0.5, 0, 0), segments=8, tile=0.1)


def pine(gs, center, height=3.2, radius=1.0, seed=0):
    rng = random.Random(seed)
    trunk_h = height * 0.72
    P.cylinder(gs["bark"], (center[0], center[1], center[2] + trunk_h * 0.5), radius * 0.10, trunk_h,
               segments=12, tile=0.6)
    layers = 4
    for i in range(layers):
        t = i / layers
        z = center[2] + height * (0.18 + 0.66 * t)
        r = radius * (1.0 - t * 0.75)
        h = height * 0.30
        P.cylinder(gs["pine"], (center[0], center[1], z + h * 0.5), r * 0.9, h,
                   segments=18, taper=0.0, tile=0.8)
        P.cylinder(gs["pine_snow"], (center[0], center[1], z + h * 0.72), r * 0.58, h * 0.22,
                   segments=18, taper=0.0, tile=0.4)


def cobweb(gs, corner, edge_a, edge_b, n=7, rings=3, seed=0):
    rng = random.Random(seed)
    c = Vector(corner)
    a = Vector(edge_a)
    b = Vector(edge_b)
    for i in range(n):
        t = i / max(1, n - 1)
        end = a.lerp(b, t)
        P.tube(gs["cord"], [c, c.lerp(end, 0.35) + Vector((0, 0, -0.02)), end],
               0.0012, sides=3, tile=0.2)
    for k in range(1, rings + 1):
        rr_ = k / (rings + 1.0)
        pts = []
        for i in range(n):
            t = i / max(1, n - 1)
            end = a.lerp(b, t)
            p = c.lerp(end, rr_)
            pts.append(p + Vector((0, 0, -0.012 * sin(t * pi))))
        P.tube(gs["cord"], pts, 0.0010, sides=3, tile=0.2)


def rope_coil(gs, center, rot=(0, 0, 0), loops=6, radius=0.12):
    for i in range(loops):
        z = -0.035 + i * 0.012
        P.torus(gs["rope"], xf(center, rot, (0, 0, z)), radius + rnd(-0.006, 0.006), 0.010,
                rot=(rot[0] + rnd(-0.12, 0.12), rot[1], rot[2]),
                major_seg=22, minor_seg=6, tile=0.2)


def chain(gs, points, link=0.035, scale=1.0):
    for k, p in enumerate(points):
        rot = (pi * 0.5 if k % 2 == 0 else 0.0, (k % 3) * 0.35, 0.0)
        P.torus(gs["iron"], p, link * 0.55 * scale, link * 0.11 * scale, rot=rot,
                major_seg=12, minor_seg=6, tile=0.1)
