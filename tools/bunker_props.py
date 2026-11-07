"""Survival props for the safehouse: sandbags, jerrycans, generator, cot, gear.

Everything is authored in Blender space (X right, Y into the room, Z up). Prop
functions take a centre point and apply their own local rotation so the set module
can place them without fighting matrices.
"""

import math
import random
from math import pi, sin, cos, tau, radians

from mathutils import Vector, Euler

import cabin_prims as P


def rnd(a, b):
    return random.uniform(a, b)


def xf(center, rot, local):
    return Vector(center) + Euler(rot, "XYZ").to_matrix() @ Vector(local)


def _xform(gs, fn, center, rot):
    """Run fn() (authored around the local origin), then rotate and place it.

    `gs` is the Groups dict: fn() may add verts to several material groups,
    so every group's new verts get the same rigid transform.
    """
    def _placement(v):
        R = Euler(rot, "XYZ").to_matrix()
        C = Vector(center)
        flat = tuple(rot) == (0.0, 0.0, 0.0)
        v.co = C + (v.co if flat else R @ v.co)

    if hasattr(gs, "bm"):
        bm = gs.bm
        before = set(bm.verts)
        fn()
        for v in bm.verts:
            if v not in before:
                _placement(v)
        return

    before = {}
    for grp in list(gs.values()):
        if hasattr(grp, "bm"):
            before[id(grp)] = set(grp.bm.verts)
    fn()
    for grp in list(gs.values()):
        if not hasattr(grp, "bm"):
            continue
        seen = before.get(id(grp), set())
        for v in grp.bm.verts:
            if v not in seen:
                _placement(v)


# ---------------------------------------------------------------------------------------
# soft goods
# ---------------------------------------------------------------------------------------

def sandbag(gs, center, rot=(0, 0, 0), scale=1.0, fill="burlap", seed=0):
    s = scale
    rng = random.Random(seed)
    P.sphere(gs[fill], center, (0.30 * s, 0.175 * s, 0.115 * s), rot=rot, subdiv=3,
             tile=0.62, jitter=0.045 * s, smooth=False)
    # stitched seam and a tied neck at one end
    for sy in (-0.055, 0.055):
        pts = [xf(center, rot, (x * s, sy * s, 0.085 * s))
               for x in (-0.22, -0.08, 0.06, 0.20)]
        P.tube(gs["canvas_grey"], pts, 0.006 * s, sides=4, tile=0.15)
    P.sphere(gs[fill], xf(center, rot, (0.285 * s, 0.0, 0.0)),
             (0.045 * s, 0.055 * s, 0.050 * s), rot=rot, subdiv=1, tile=0.3)
    P.torus(gs["cord"], xf(center, rot, (0.255 * s, 0.0, 0.0)), 0.042 * s, 0.006 * s,
            rot=(0, pi * 0.5, 0), major_seg=10, minor_seg=4, tile=0.1)
    # a couple of patches and a stencil mark
    if rng.random() < 0.7:
        P.box(gs["canvas_grey"], xf(center, rot, (rng.uniform(-0.1, 0.1) * s,
                                                  -0.16 * s, 0.02 * s)),
              (0.10 * s, 0.004, 0.07 * s), rot=rot, tile=0.3)


def sandbag_wall(gs, x0, y0, cols, rows, fill_a="burlap", fill_b="canvas", seed=0):
    rng = random.Random(seed)
    for row in range(rows):
        for col in range(cols):
            bx = x0 + col * 0.34 + (0.17 if row % 2 else 0.0)
            by = y0 + rng.uniform(-0.02, 0.02)
            bz = 0.10 + row * 0.115
            fill = fill_a if (row + col) % 3 else fill_b
            sandbag(gs, (bx, by, bz), rot=(0, 0, radians(rng.uniform(-8, 8))),
                    scale=rng.uniform(0.92, 1.05), fill=fill, seed=seed + row * 31 + col)


def tarp(gs, center, size, rot=(0, 0, 0), color="canvas", folds=1.0, seed=0,
         drape=0.0, uv=(0.03, 0.03, 0.97, 0.97)):
    """A wrinkled sheet, optionally with cloth hanging off the two long edges."""
    rng = random.Random(seed)
    w, d = size
    phase = rng.uniform(0, tau)

    def height(u, v):
        e = min(u, 1.0 - u, v, 1.0 - v)
        wr = (0.013 * sin(u * 17.0 + phase) + 0.010 * sin(v * 13.0 - phase * 0.7)
              + 0.006 * sin((u + v) * 29.0))
        return (0.006 + wr * folds) * (0.35 + 0.65 * min(1.0, e / 0.12))

    def run():
        P.cloth(gs[color], (-w * 0.5, -d * 0.5, 0.0),
                (w, 0, 0), (0, d, 0), (0, 0, 1), 18, 18, 0.006, height, uv_rect=uv)
        if drape > 0.0:
            for side in (-1, 1):
                def drop(u, v):
                    return (0.004 + 0.012 * sin(u * 15.0 + phase)
                            + 0.030 * v * v)
                P.cloth(gs[color], (-w * 0.5, side * d * 0.5, 0.0),
                        (w, 0, 0), (0, 0, -drape), (0, -side, 0), 16, 6, 0.006, drop,
                        uv_rect=uv)

    _xform(gs, run, center, rot)


def sleeping_bag(gs, center, rot=(0, 0, 0), color="wool", opened=True, seed=0):
    cx, cy, cz = center
    if opened:
        def body(u, v):
            return (0.014 * sin(u * 8.0 + v * 3.0) + 0.020 * v * (1.0 - v)) * 0.8
        P.cloth(gs[color], (cx - 0.36, cy - 0.92, cz + 0.05),
                (0.72, 0, 0), (0, 1.84, 0), (0, 0, 1), 14, 30, 0.055, body,
                uv_rect=(0.02, 0.02, 0.98, 0.98))
        # rolled hood at the head end
        P.cylinder(gs[color], (cx, cy - 0.80, cz + 0.13), 0.115, 0.72,
                   rot=(0, pi * 0.5, 0), segments=18, tile=0.6)
        P.cylinder(gs["canvas_grey"], (cx, cy - 0.42, cz + 0.10), 0.090, 0.74,
                   rot=(0, pi * 0.5, 0), segments=16, tile=0.6)
    else:
        P.cylinder(gs[color], center, 0.115, 0.66, rot=(0, pi * 0.5, 0),
                   segments=18, tile=0.6)
        for i in range(3):
            P.torus(gs["cord"], xf(center, (0, pi * 0.5, 0), (0, 0, 0)),
                    0.118, 0.006, rot=(0, 0, 0), major_seg=14, minor_seg=4, tile=0.1)


def cot(gs, center, rot=(0, 0, 0), scale=1.0):
    s = scale
    steel = gs["steel_dark"]
    canvas = gs["canvas"]

    def build():
        x, y, z = 0.0, 0.0, 0.0
        # side rails
        for sx in (-1, 1):
            P.cylinder(steel, (sx * 0.44, 0.0, 0.46), 0.022, 1.94,
                       rot=(pi * 0.5, 0, 0), segments=10, tile=0.3)
            for ly in (-0.82, 0.82):
                P.cylinder(steel, (sx * 0.44, ly, 0.23), 0.022, 0.46,
                           segments=10, tile=0.3)
                P.box(gs["rubber"], (sx * 0.44, ly, 0.015), (0.06, 0.10, 0.03), tile=0.2)
        # end frames
        for ly in (-0.94, 0.94):
            P.cylinder(steel, (0.0, ly, 0.55), 0.020, 0.92,
                       rot=(0, pi * 0.5, 0), segments=10, tile=0.3)
            P.cylinder(steel, (0.0, ly, 0.72), 0.018, 0.86,
                       rot=(0, pi * 0.5, 0), segments=10, tile=0.3)
        # sagging canvas bunk
        def bed(u, v):
            return 0.055 * sin(pi * u) * sin(pi * v) + 0.010 * sin(u * 7.0)
        P.cloth(canvas, (-0.44, -0.94, 0.50), (0.88, 0, 0), (0, 1.88, 0),
                (0, 0, 1), 12, 24, 0.012, bed, uv_rect=(0.05, 0.05, 0.95, 0.95))
        # blanket folded at the foot
        P.box(gs["wool"], (0.0, 0.58, 0.55), (0.80, 0.62, 0.10),
              bevel=0.02, tile=0.7)
        P.box(gs["wool"], (0.0, 0.58, 0.64), (0.72, 0.50, 0.08),
              bevel=0.02, tile=0.7)
        # pillow
        P.sphere(gs["canvas_grey"], (0.0, -0.70, 0.57), (0.32, 0.19, 0.08),
                 subdiv=2, tile=0.6)
        # a rifle propped against the frame
        # (kept out of the cot function: the set module places it)

    _xform(gs, build, center, rot)


# ---------------------------------------------------------------------------------------
# containers
# ---------------------------------------------------------------------------------------

def jerrycan(gs, center, rot=(0, 0, 0), scale=1.0, body="olive", cap="red"):
    s = scale

    def build():
        P.box(gs[body], (0, 0, 0.235), (0.34, 0.16, 0.45), bevel=0.018, seg=2,
              tile=0.45, grain="Z")
        # pressed X on both broad faces
        for sx in (-1, 1):
            for ang in (32.0, -32.0):
                P.box(gs[body], (sx * 0.081, 0, 0.235), (0.006, 0.030, 0.34),
                      rot=(radians(ang), 0, 0), tile=0.3)
            for zz in (0.10, 0.37):
                P.box(gs[body], (sx * 0.081, 0, zz), (0.005, 0.10, 0.028), tile=0.3)
        # top shoulder, neck and cap
        P.box(gs[body], (0, 0, 0.462), (0.30, 0.14, 0.035), bevel=0.008, tile=0.4)
        P.cylinder(gs[body], (0.10, 0, 0.495), 0.038, 0.055, segments=12, tile=0.2)
        P.cylinder(gs[cap], (0.10, 0, 0.525), 0.040, 0.035, segments=12, tile=0.2)
        P.cylinder(gs[body], (0.10, 0, 0.545), 0.012, 0.02, segments=8, tile=0.1)
        # triple handle
        for sy in (-0.055, 0.055):
            P.box(gs[body], (0.0, sy, 0.505), (0.22, 0.022, 0.030), bevel=0.004, tile=0.2)
        P.box(gs[body], (-0.06, 0, 0.520), (0.022, 0.13, 0.028), bevel=0.004, tile=0.2)
        # side vent + label
        P.box(gs["black"], (0.0, -0.081, 0.40), (0.06, 0.004, 0.05), tile=0.1)
        P.box(gs["white_paint"], (0.0, -0.083, 0.30), (0.15, 0.004, 0.10), tile=0.2)
        P.box(gs["red"], (0.0, -0.085, 0.30), (0.10, 0.004, 0.020),
              rot=(0, 0, radians(-18)), tile=0.1)
        P.box(gs["black"], (0.0, -0.086, 0.345), (0.11, 0.003, 0.012), tile=0.1)
        P.box(gs["black"], (0.0, -0.086, 0.255), (0.13, 0.003, 0.012), tile=0.1)
        # grime at the foot
        P.box(gs["rust_dark"], (0.02, -0.079, 0.045), (0.26, 0.006, 0.06), tile=0.3)

    _xform(gs, build, center, rot)


def ammo_box(gs, center, rot=(0, 0, 0), size=(0.42, 0.25, 0.26), color="olive",
             stencil="white"):
    w, d, h = size

    def build():
        P.box(gs[color], (0, 0, h * 0.5), (w, d, h), bevel=0.008, seg=2, tile=0.45, grain="X")
        P.box(gs[color], (0, 0, h + 0.016), (w + 0.02, d + 0.02, 0.032), bevel=0.005, tile=0.4)
        # pressed ribs and corner plates
        for sx in (-1, 1):
            for zz in (h * 0.30, h * 0.72):
                P.box(gs[color], (sx * (w * 0.5 + 0.003), 0, zz), (0.006, d * 0.8, 0.020), tile=0.2)
            P.box(gs["steel_dark"], (sx * (w * 0.5 - 0.012), d * 0.5 - 0.008, h * 0.5),
                  (0.035, 0.020, h * 0.85), tile=0.2)
        # latches
        for sx in (-0.30, 0.30):
            P.box(gs["steel"], (sx * w, -d * 0.5 - 0.012, h * 0.78), (0.035, 0.018, 0.075),
                  bevel=0.003, tile=0.15)
            P.cylinder(gs["chrome"], (sx * w, -d * 0.5 - 0.022, h * 0.78), 0.010, 0.012,
                       rot=(pi * 0.5, 0, 0), segments=6, tile=0.05)
        # handles
        for sx in (-1, 1):
            P.tube(gs["steel_dark"],
                   [(sx * (w * 0.5 - 0.05), -d * 0.5 - 0.030, h * 0.62),
                    (sx * (w * 0.5 - 0.05), -d * 0.5 - 0.055, h * 0.72),
                    (sx * (w * 0.5 + 0.05), -d * 0.5 - 0.055, h * 0.72),
                    (sx * (w * 0.5 + 0.05), -d * 0.5 - 0.030, h * 0.62)],
                   0.009, sides=5, tile=0.15)
        # stencil: three bars + caliber stripe
        if stencil:
            for i, (yy, ln) in enumerate(((-0.075, 0.20), (-0.035, 0.26), (0.005, 0.18))):
                P.box(gs[stencil], (0.0, -d * 0.5 - 0.004, h * 0.42 + i * 0.035),
                      (ln, 0.003, 0.018), tile=0.15)
            P.box(gs["yellow"], (0.0, -d * 0.5 - 0.005, h * 0.24), (w * 0.70, 0.003, 0.020), tile=0.2)
        # rust creeping from the seams
        for i in range(4):
            P.box(gs["rust_dark"],
                  (rnd(-w * 0.4, w * 0.4), -d * 0.5 - 0.003, rnd(0.03, h * 0.85)),
                  (rnd(0.03, 0.10), 0.003, rnd(0.02, 0.05)), tile=0.25)

    _xform(gs, build, center, rot)


def footlocker(gs, center, rot=(0, 0, 0), size=(0.92, 0.52, 0.42), color="olive"):
    w, d, h = size

    def build():
        P.box(gs[color], (0, 0, h * 0.5), (w, d, h), bevel=0.012, seg=2, tile=0.6, grain="X")
        P.box(gs[color], (0, 0, h + 0.030), (w + 0.02, d + 0.02, 0.060), bevel=0.008, tile=0.5)
        for sx in (-1, 1):
            P.box(gs["steel_dark"], (sx * (w * 0.5 - 0.02), 0, h * 0.5),
                  (0.05, d * 0.96, h * 0.92), tile=0.35)
            P.tube(gs["steel_dark"],
                   [(sx * (w * 0.5 + 0.004), -0.12, h * 0.52),
                    (sx * (w * 0.5 + 0.045), -0.12, h * 0.58),
                    (sx * (w * 0.5 + 0.045), 0.12, h * 0.58),
                    (sx * (w * 0.5 + 0.004), 0.12, h * 0.52)], 0.011, sides=5, tile=0.2)
            P.box(gs["yellow"], (sx * (w * 0.5 - 0.02), -d * 0.5 - 0.003, h * 0.24),
                  (0.10, 0.003, 0.09), rot=(0, 0, radians(45 * sx)), tile=0.2)
        for sx in (-0.30, 0.30):
            P.box(gs["steel"], (sx * w, -d * 0.5 - 0.010, h + 0.010), (0.05, 0.020, 0.11),
                  bevel=0.004, tile=0.2)
        P.box(gs["white_paint"], (0.0, -d * 0.5 - 0.004, h * 0.70), (0.34, 0.003, 0.09), tile=0.3)
        P.box(gs["black"], (0.0, -d * 0.5 - 0.006, h * 0.70), (0.24, 0.003, 0.016), tile=0.2)
        P.box(gs["rust_dark"], (rnd(-0.2, 0.2), -d * 0.5 - 0.003, 0.07), (0.18, 0.004, 0.05), tile=0.3)

    _xform(gs, build, center, rot)


def toolbox(gs, center, rot=(0, 0, 0), scale=1.0):
    s = scale

    def build():
        P.box(gs["red"], (0, 0, 0.10), (0.40, 0.20, 0.20), bevel=0.012, seg=2, tile=0.4)
        P.box(gs["red_dark"], (0, 0, 0.205), (0.40, 0.20, 0.035), bevel=0.008, tile=0.3)
        P.tube(gs["steel"], [(-0.10, 0, 0.245), (-0.10, 0, 0.30), (0.10, 0, 0.30),
                             (0.10, 0, 0.245)], 0.010, sides=5, tile=0.15)
        for sx in (-0.12, 0.12):
            P.box(gs["steel"], (sx, -0.103, 0.185), (0.045, 0.010, 0.050), bevel=0.003, tile=0.1)
        P.box(gs["white_paint"], (0.0, -0.101, 0.10), (0.14, 0.002, 0.04), tile=0.15)

    _xform(gs, build, center, rot)


def water_barrel(gs, center, rot=(0, 0, 0), scale=1.0):
    s = scale

    def build():
        P.lathe(gs["plastic_blue"] if "plastic_blue" in gs else gs["label_blue"],
                [(0.0, 0.0), (0.27, 0.0), (0.29, 0.035), (0.30, 0.10),
                 (0.295, 0.40), (0.30, 0.46), (0.285, 0.55), (0.24, 0.58), (0.0, 0.585)],
                center=(0, 0, 0), segments=26, tile=0.8)
        for zz in (0.14, 0.28, 0.42):
            P.torus(gs["label_blue"], (0, 0, zz), 0.297, 0.012,
                    major_seg=26, minor_seg=5, tile=0.3)
        P.cylinder(gs["label_blue"], (0, 0, 0.60), 0.085, 0.05, segments=16, tile=0.3)
        P.cylinder(gs["black"], (0, 0, 0.63), 0.090, 0.02, segments=16, tile=0.2)
        # tap
        P.cylinder(gs["brass"], (0.0, -0.30, 0.14), 0.020, 0.10,
                   rot=(pi * 0.5, 0, 0), segments=10, tile=0.2)
        P.box(gs["brass"], (0.0, -0.36, 0.13), (0.05, 0.05, 0.05), bevel=0.006, tile=0.15)
        # white stencilled water mark
        P.box(gs["white_paint"], (0.0, -0.295, 0.38), (0.15, 0.003, 0.12), tile=0.2)
        P.box(gs["label_blue"], (0.0, -0.297, 0.38), (0.11, 0.003, 0.018), tile=0.1)

    _xform(gs, build, center, rot)


def bucket(gs, center, rot=(0, 0, 0), fill=True):
    def build():
        P.lathe(gs["galv"], [(0.0, 0.0), (0.10, 0.0), (0.125, 0.015), (0.140, 0.28),
                             (0.145, 0.30)], center=(0, 0, 0), segments=20, tile=0.4)
        P.torus(gs["galv"], (0, 0, 0.29), 0.143, 0.008, major_seg=20, minor_seg=5, tile=0.2)
        P.torus(gs["galv"], (0, 0, 0.06), 0.128, 0.007, major_seg=20, minor_seg=5, tile=0.2)
        # bail handle
        pts = []
        for i in range(13):
            a = pi * i / 12.0
            pts.append((0.15 * cos(a), 0.0, 0.30 + 0.16 * sin(a)))
        P.tube(gs["iron"], pts, 0.006, sides=4, tile=0.2)
        if fill:
            P.disk(gs["water"], (0, 0, 0.22), 0.128, segments=20, tile=0.3)
        P.box(gs["rust_dark"], (0.0, -0.135, 0.17), (0.09, 0.005, 0.14), tile=0.2)

    _xform(gs, build, center, rot)


# ---------------------------------------------------------------------------------------
# machines and gear
# ---------------------------------------------------------------------------------------

def generator(gs, center, rot=(0, 0, 0), scale=1.0):
    s = scale

    def build():
        steel = gs["steel_dark"]
        # skid frame
        for sx in (-1, 1):
            P.box(steel, (sx * 0.38, 0.02, 0.045), (0.06, 0.72, 0.050), tile=0.4)
            for sy in (-1, 1):
                P.cylinder(steel, (sx * 0.38, sy * 0.30, 0.10), 0.028, 0.16,
                           segments=8, tile=0.2)
        for sy in (-1, 1):
            for sx in (-1, 1):
                P.cylinder(steel, (sx * 0.36, sy * 0.30, 0.30), 0.024, 0.55,
                           segments=8, tile=0.3)
        P.box(steel, (0.0, 0.02, 0.62), (0.80, 0.60, 0.030), tile=0.4)
        # yellow power body
        P.box(gs["yellow"], (0.0, -0.01, 0.40), (0.64, 0.44, 0.34),
              bevel=0.020, seg=2, tile=0.5)
        for i in range(6):
            P.box(gs["black"], (0.0, -0.235, 0.27 + i * 0.047), (0.30, 0.008, 0.028), tile=0.2)
        # black fuel tank
        P.box(gs["black"], (0.0, 0.01, 0.73), (0.55, 0.40, 0.17), bevel=0.020, seg=2, tile=0.5)
        P.cylinder(gs["yellow"], (0.20, 0.01, 0.825), 0.040, 0.035, segments=12, tile=0.2)
        # control panel
        P.box(gs["olive_dark"], (0.0, -0.24, 0.51), (0.44, 0.035, 0.16), bevel=0.005, tile=0.3)
        for gx in (-0.13, 0.0):
            P.cylinder(gs["chrome"], (gx, -0.262, 0.52), 0.045, 0.012,
                       rot=(pi * 0.5, 0, 0), segments=14, tile=0.2)
            P.disk(gs["white_paint"], (gx, -0.269, 0.52), 0.037,
                   rot=(pi * 0.5, 0, 0), segments=14, tile=0.2)
            P.box(gs["red"], (gx + 0.010, -0.271, 0.527), (0.045, 0.002, 0.004),
                  rot=(0, 0, radians(35)), tile=0.1)
        P.box(gs["led_green"], (0.14, -0.262, 0.55), (0.022, 0.006, 0.022), tile=0.1)
        P.box(gs["led_red"], (0.18, -0.262, 0.47), (0.022, 0.006, 0.022), tile=0.1)
        # exhaust
        P.tube(gs["rust"], [(-0.24, 0.06, 0.79), (-0.30, 0.12, 0.92),
                            (-0.28, 0.22, 1.10), (-0.24, 0.26, 1.22)],
               0.030, sides=8, tile=0.4)
        P.tube(gs["rust"], [(-0.24, 0.26, 1.22), (-0.19, 0.28, 1.27)], 0.034, sides=8, tile=0.2)
        # wheels and pull handle
        for sx in (-1, 1):
            P.cylinder(gs["rubber"], (sx * 0.42, 0.26, 0.13), 0.125, 0.075,
                       rot=(0, pi * 0.5, 0), segments=18, tile=0.3)
            P.cylinder(gs["steel"], (sx * 0.42, 0.26, 0.13), 0.055, 0.078,
                       rot=(0, pi * 0.5, 0), segments=12, tile=0.2)
        P.tube(gs["steel_dark"], [(-0.30, -0.34, 0.55), (-0.34, -0.44, 0.62),
                                  (0.34, -0.44, 0.62), (0.30, -0.34, 0.55)],
               0.016, sides=6, tile=0.3)
        # coiled output cable
        for i in range(4):
            P.torus(gs["cord"], (0.26, -0.30 + i * 0.012, 0.58), 0.09, 0.012,
                    rot=(pi * 0.5, 0, 0), major_seg=16, minor_seg=5, tile=0.2)

    _xform(gs, build, center, rot)


def reloading_press(gs, center, rot=(0, 0, 0), scale=1.0):
    s = scale

    def build():
        P.box(gs["steel_dark"], (0, 0, 0.020), (0.18, 0.14, 0.040), bevel=0.005, tile=0.2)
        P.cylinder(gs["steel"], (0, 0.02, 0.17), 0.030, 0.30, segments=12, tile=0.3)
        P.box(gs["red"], (0, 0.02, 0.34), (0.10, 0.10, 0.075), bevel=0.008, tile=0.2)
        P.cylinder(gs["steel"], (0, 0.02, 0.40), 0.020, 0.07, segments=10, tile=0.2)
        P.box(gs["steel"], (0, 0.02, 0.445), (0.16, 0.09, 0.025), bevel=0.004, tile=0.2)
        # lever arm and handle
        P.box(gs["red"], (0.06, 0.02, 0.50), (0.30, 0.035, 0.030),
              rot=(0, radians(-12), 0), bevel=0.005, tile=0.2)
        P.sphere(gs["black"], (0.21, 0.02, 0.47), (0.032, 0.032, 0.032), subdiv=2, tile=0.1)
        # die and a case in the shell holder
        P.cylinder(gs["brass"], (0, -0.02, 0.115), 0.014, 0.060, segments=10, tile=0.1)
        P.cylinder(gs["steel"], (0, -0.02, 0.075), 0.020, 0.020, segments=10, tile=0.1)
        for i in range(5):
            P.cylinder(gs["brass"], (0.07 + (i % 3) * 0.018, -0.04 + (i // 3) * 0.02, 0.045),
                       0.007, 0.030, rot=(pi * 0.5, 0, rnd(0, tau)), segments=6, tile=0.05)
        # a small plastic bin of cases
        P.box(gs["label_blue"], (0.16, -0.02, 0.035), (0.10, 0.09, 0.045), bevel=0.006, tile=0.2)

    _xform(gs, build, center, rot)


def medkit(gs, center, rot=(0, 0, 0), scale=1.0):
    s = scale

    def build():
        P.box(gs["white_paint"], (0, 0, 0.085), (0.34, 0.24, 0.17), bevel=0.010, seg=2, tile=0.35)
        P.box(gs["white_paint"], (0, 0, 0.185), (0.35, 0.25, 0.04), bevel=0.006, tile=0.3)
        for sx in (-0.12, 0.12):
            P.box(gs["steel"], (sx, -0.128, 0.165), (0.045, 0.010, 0.050), bevel=0.003, tile=0.1)
        P.tube(gs["steel"], [(-0.09, 0, 0.215), (-0.09, 0, 0.265), (0.09, 0, 0.265),
                             (0.09, 0, 0.215)], 0.010, sides=5, tile=0.1)
        # red cross on the lid, slightly worn
        P.box(gs["red"], (0.0, 0.0, 0.209), (0.20, 0.055, 0.008), tile=0.1)
        P.box(gs["red"], (0.0, 0.0, 0.209), (0.055, 0.20, 0.008), tile=0.1)
        P.box(gs["white_paint"], (0.0, -0.104, 0.209), (0.02, 0.05, 0.008), tile=0.05)
        # a scuffed corner and a taped label
        P.box(gs["rust_dark"], (-0.15, -0.110, 0.035), (0.06, 0.03, 0.05), tile=0.15)
        P.box(gs["paper"], (0.10, -0.122, 0.11), (0.10, 0.003, 0.055), tile=0.2)

    _xform(gs, build, center, rot)


def gas_mask(gs, center, rot=(0, 0, 0), scale=1.0):
    s = scale

    def build():
        P.sphere(gs["rubber"], (0, 0, 0), (0.105, 0.125, 0.140), subdiv=3, tile=0.4, jitter=0.006)
        for sx in (-1, 1):
            P.cylinder(gs["iron_dark"], (sx * 0.055, -0.095, 0.025), 0.038, 0.035,
                       rot=(radians(78), 0, 0), segments=14, tile=0.2)
            P.disk(gs["glass"], (sx * 0.055, -0.113, 0.025), 0.030,
                   rot=(radians(78), 0, 0), segments=14, tile=0.2)
        P.cylinder(gs["olive"], (0, -0.115, -0.065), 0.052, 0.075,
                   rot=(radians(72), 0, 0), segments=16, tile=0.3)
        P.cylinder(gs["iron_dark"], (0, -0.145, -0.085), 0.055, 0.020,
                   rot=(radians(72), 0, 0), segments=16, tile=0.2)
        # straps flying loose
        for sx in (-1, 1):
            P.tube(gs["canvas_grey"], [(sx * 0.10, 0.02, 0.02), (sx * 0.20, 0.10, 0.02),
                                       (sx * 0.16, 0.22, -0.05)], 0.012, sides=4, tile=0.3)
        P.box(gs["canvas_grey"], (0, 0.02, 0.145), (0.10, 0.13, 0.02), tile=0.3)

    _xform(gs, build, center, rot)


def flashlight(gs, center, rot=(0, 0, 0), scale=1.0, lit=False):
    s = scale

    def build():
        P.cylinder(gs["yellow"], (0, 0.0, 0.0), 0.026, 0.17,
                   rot=(pi * 0.5, 0, 0), segments=12, tile=0.3)
        for i in range(3):
            P.torus(gs["yellow"], (0, -0.06 + i * 0.06, 0.0), 0.026, 0.004,
                    rot=(pi * 0.5, 0, 0), major_seg=12, minor_seg=4, tile=0.1)
        P.cylinder(gs["steel"], (0, 0.10, 0.0), 0.038, 0.06,
                   rot=(pi * 0.5, 0, 0), segments=14, tile=0.2, taper=1.25)
        P.disk(gs["lamp_glow"] if lit else gs["glass"], (0, 0.133, 0.0), 0.032,
               rot=(-pi * 0.5, 0, 0), segments=14, tile=0.2)
        P.box(gs["black"], (0, 0.01, 0.027), (0.018, 0.050, 0.012), tile=0.1)
        P.cylinder(gs["black"], (0, -0.09, 0.0), 0.024, 0.015,
                   rot=(pi * 0.5, 0, 0), segments=10, tile=0.1)

    _xform(gs, build, center, rot)


def battery(gs, center, rot=(0, 0, 0)):
    def build():
        P.cylinder(gs["black"], (0, 0, 0.045), 0.026, 0.09, segments=14, tile=0.2)
        P.cylinder(gs["copper"], (0, 0, 0.088), 0.014, 0.012, segments=10, tile=0.1)
        P.cylinder(gs["label_green"], (0, 0, 0.048), 0.0265, 0.030, segments=14, tile=0.2)
        P.cylinder(gs["label_red"], (0, 0, 0.072), 0.0265, 0.008, segments=14, tile=0.1)

    _xform(gs, build, center, rot)


def cable_spool(gs, center, rot=(0, 0, 0), radius=0.22, width=0.24):
    def build():
        for sy in (-1, 1):
            P.disk(gs["wood_dark"], (0, sy * width * 0.5, radius), radius,
                   rot=(pi * 0.5, 0, 0), segments=22, tile=0.5)
            P.cylinder(gs["wood_dark"], (0, sy * width * 0.5, radius), radius * 0.96, 0.018,
                       rot=(pi * 0.5, 0, 0), segments=22, tile=0.4)
        P.cylinder(gs["wood_dark"], (0, 0, radius), radius * 0.30, width,
                   rot=(pi * 0.5, 0, 0), segments=14, tile=0.3)
        for i in range(5):
            P.torus(gs["cord"], (0, -width * 0.28 + i * width * 0.14, radius),
                    radius * 0.72, 0.022, rot=(0, 0, 0), major_seg=22, minor_seg=5, tile=0.2)
        # a loose tail
        P.tube(gs["cord"], [(radius * 0.7, width * 0.3, radius), (radius * 0.9, width * 0.55, 0.10),
                            (radius * 1.1, width * 0.65, 0.02)], 0.010, sides=4, tile=0.2)
        # steel stand
        for sy in (-1, 1):
            P.cylinder(gs["steel_dark"], (0, sy * width * 0.62, radius), 0.012, 0.24,
                       rot=(0, pi * 0.5, 0), segments=8, tile=0.2)

    _xform(gs, build, center, rot)


def tyre(gs, center, rot=(0, 0, 0), radius=0.30):
    def build():
        P.torus(gs["rubber"], (0, 0, radius), radius * 0.72, radius * 0.30,
                rot=(pi * 0.5, 0, 0), major_seg=24, minor_seg=10, tile=0.5)
        P.cylinder(gs["steel"], (0, 0, radius), radius * 0.42, 0.16,
                   rot=(pi * 0.5, 0, 0), segments=18, tile=0.3)
        P.cylinder(gs["iron_dark"], (0, 0, radius), radius * 0.20, 0.17,
                   rot=(pi * 0.5, 0, 0), segments=12, tile=0.2)
        for i in range(18):
            a = tau * i / 18.0
            P.box(gs["rubber"], (cos(a) * radius * 0.98, 0, radius + sin(a) * radius * 0.98),
                  (radius * 0.16, 0.10, radius * 0.07), rot=(0, -a, 0), tile=0.2)

    _xform(gs, build, center, rot)


def folding_chair(gs, center, rot=(0, 0, 0), color="canvas"):
    def build():
        steel = gs["steel_dark"]
        # legs, front and back, crossing slightly
        for sy in (-1, 1):
            P.cylinder(steel, (-0.16, sy * 0.20, 0.24), 0.012, 0.48,
                       rot=(0, radians(10), 0), segments=8, tile=0.2)
            P.cylinder(steel, (0.16, sy * 0.20, 0.24), 0.012, 0.48,
                       rot=(0, radians(-10), 0), segments=8, tile=0.2)
        for sy in (-1, 1):
            P.cylinder(steel, (0.0, sy * 0.20, 0.30), 0.010, 0.34,
                       rot=(0, pi * 0.5, 0), segments=8, tile=0.2)
        # seat and back canvas
        P.cloth(gs[color], (-0.19, -0.19, 0.46), (0.38, 0, 0), (0, 0.38, 0), (0, 0, 1),
                8, 8, 0.008, lambda u, v: 0.006 - 0.012 * sin(pi * u) * sin(pi * v),
                uv_rect=(0.05, 0.05, 0.95, 0.95))
        P.cloth(gs[color], (-0.19, 0.20, 0.47), (0.38, 0, 0), (0, 0, 0.42), (0, -1, 0),
                8, 8, 0.008, lambda u, v: 0.006 + 0.010 * sin(pi * u) * v,
                uv_rect=(0.05, 0.05, 0.95, 0.95))
        for sx in (-1, 1):
            P.cylinder(steel, (sx * 0.18, 0.20, 0.66), 0.011, 0.38,
                       rot=(radians(-8), 0, 0), segments=8, tile=0.2)
        P.box(gs["steel"], (0.0, -0.04, 0.30), (0.30, 0.020, 0.018), tile=0.2)

    _xform(gs, build, center, rot)


# ---------------------------------------------------------------------------------------
# wall furniture
# ---------------------------------------------------------------------------------------

def pegboard(gs, center, size, rot=(0, 0, 0), holes=True):
    w, h = size

    def build():
        P.box(gs["wood_dark"], (0, 0, 0), (w, h, 0.016), bevel=0.004, tile=0.8, grain="X")
        P.box(gs["steel_dark"], (0, 0.011, 0), (w + 0.04, 0.008, h + 0.04), tile=0.5)
        P.box(gs["wood_dark"], (0, -0.009, 0), (w, h, 0.004), tile=0.8)
        if holes:
            nx = int(w / 0.048)
            nz = int(h / 0.048)
            for ix in range(nx):
                for iz in range(nz):
                    px = -w * 0.5 + 0.026 + ix * 0.048
                    pz = -h * 0.5 + 0.026 + iz * 0.048
                    P.cylinder(gs["black"], (px, -0.013, pz), 0.0075, 0.006,
                               rot=(pi * 0.5, 0, 0), segments=6, tile=0.05)

    _xform(gs, build, center, rot)


def warning_sign(gs, center, rot=(0, 0, 0), size=0.26):
    def build():
        d = size
        P.box(gs["black"], (0, 0.008, 0), (d * 1.10, 0.012, d * 1.10),
              rot=(0, radians(45), 0), tile=0.2)
        P.box(gs["yellow"], (0, 0.0, 0), (d, 0.012, d),
              rot=(0, radians(45), 0), tile=0.4)
        P.box(gs["black"], (0, -0.008, 0.02), (d * 0.16, 0.004, d * 0.46), tile=0.1)
        P.box(gs["black"], (0, -0.008, -0.19), (d * 0.16, 0.004, d * 0.12), tile=0.1)
        for sx in (-1, 1):
            for sz in (-1, 1):
                P.cylinder(gs["steel"], (sx * d * 0.30, -0.010, sz * d * 0.30), 0.012, 0.010,
                           rot=(pi * 0.5, 0, 0), segments=6, tile=0.05)

    _xform(gs, build, center, rot)


def map_board(gs, center, rot=(0, 0, 0), size=(0.86, 0.60), seed=0):
    w, h = size
    rng = random.Random(seed)

    def build():
        P.box(gs["brick"], (0, 0.02, 0), (w, 0.030, h), bevel=0.005, tile=0.7)
        P.box(gs["wood_dark"], (0, 0.005, h * 0.5), (w + 0.06, 0.035, 0.045), tile=0.3)
        P.box(gs["wood_dark"], (0, 0.005, -h * 0.5), (w + 0.06, 0.035, 0.045), tile=0.3)
        P.box(gs["wood_dark"], (0, 0.005, 0), (0.035, 0.035, h), tile=0.3)
        # map paper, slightly askew
        P.quad(gs["map"], [(-w * 0.46, 0.001, -h * 0.44), (w * 0.44, 0.001, -h * 0.41),
                           (w * 0.46, 0.001, h * 0.43), (-w * 0.44, 0.001, h * 0.40)],
               uv_rect=(0.02, 0.02, 0.98, 0.98))
        # grid lines and a contaminated zone scribble
        for i in range(6):
            pz = -h * 0.35 + i * h * 0.14
            P.box(gs["ink"], (0, -0.002, pz), (w * 0.86, 0.002, 0.0035), tile=0.1)
        for i in range(5):
            px = -w * 0.38 + i * w * 0.19
            P.box(gs["ink"], (px, -0.002, 0), (0.0035, 0.002, h * 0.80), tile=0.1)
        # red string between pins
        pins = [(-w * 0.28, h * 0.15), (w * 0.05, h * 0.28), (w * 0.30, h * 0.02),
                (w * 0.10, -h * 0.26), (-w * 0.20, -h * 0.10)]
        for i in range(len(pins) - 1):
            a, b = pins[i], pins[i + 1]
            mid = ((a[0] + b[0]) * 0.5, -0.006, (a[1] + b[1]) * 0.5 - 0.03)
            P.tube(gs["thread_red"] if "thread_red" in gs else gs["red"],
                   [(a[0], -0.004, a[1]), mid, (b[0], -0.004, b[1])],
                   0.0025, sides=3, tile=0.1)
        for (px, pz) in pins:
            P.sphere(gs["red"], (px, -0.010, pz), (0.012, 0.008, 0.012), subdiv=1, tile=0.05)
        # photos and sticky notes
        for i in range(4):
            px = -w * 0.34 + rng.uniform(0, w * 0.58)
            pz = h * 0.10 + rng.uniform(-h * 0.30, h * 0.30)
            P.box(gs["paper_old"], (px, -0.006, pz), (0.10, 0.002, 0.13),
                  rot=(0, 0, radians(rng.uniform(-8, 8))), tile=0.2)
            P.box(gs["ink"], (px, -0.008, pz + 0.03), (0.07, 0.001, 0.05), tile=0.1)
        P.box(gs["yellow"], (w * 0.30, -0.007, -h * 0.34), (0.08, 0.002, 0.08),
              rot=(0, 0, radians(6)), tile=0.15)
        P.box(gs["paper"], (-w * 0.31, -0.007, -h * 0.34), (0.09, 0.002, 0.06), tile=0.15)
        # marker pen hanging on a string
        P.tube(gs["cord"], [(w * 0.36, 0.0, -h * 0.30), (w * 0.40, -0.01, -h * 0.42)],
               0.002, sides=3, tile=0.1)
        P.cylinder(gs["black"], (w * 0.40, -0.012, -h * 0.46), 0.008, 0.10,
                   rot=(0, 0, radians(15)), segments=6, tile=0.1)

    _xform(gs, build, center, rot)


def shelf_unit(gs, center, rot=(0, 0, 0), width=1.20, depth=0.42, height=1.90):
    w, d, h = width, depth, height
    steel = gs["steel_dark"]
    planks = [0.12, 0.62, 1.12, 1.62]

    def build():
        for sx in (-1, 1):
            for sy in (-1, 1):
                P.box(steel, (sx * w * 0.5, sy * d * 0.5, h * 0.5),
                      (0.035, 0.035, h), tile=0.4)
                for pz in (0.28, 0.90, 1.52):
                    P.box(steel, (sx * w * 0.5, sy * d * 0.5, pz),
                          (0.045, 0.045, 0.030), tile=0.2)
        for pz in planks:
            P.box(gs["wood"], (0, 0, pz), (w + 0.04, d, 0.035),
                  bevel=0.004, tile=1.0, grain="X")
            P.box(steel, (0, -d * 0.5 - 0.005, pz), (w + 0.02, 0.012, 0.045), tile=0.3)
        # brace across the back
        for pz in (0.90, 1.52):
            P.box(steel, (0, d * 0.5 - 0.01, pz), (w, 0.020, 0.025), tile=0.3)

    _xform(gs, build, center, rot)


def locker(gs, center, rot=(0, 0, 0), width=0.56, depth=0.48, height=1.92):
    w, d, h = width, depth, height
    steel = gs["steel_dark"]
    rng = random.Random(17)

    def build():
        # open carcass: back, two sides, top and bottom, no front so the shelves read
        P.box(steel, (0, d * 0.5 - 0.015, h * 0.5), (w, 0.030, h), tile=0.8, grain="Z")
        for sx in (-1, 1):
            P.box(steel, (sx * (w * 0.5 - 0.015), 0, h * 0.5), (0.030, d, h),
                  tile=0.8, grain="Z")
        P.box(steel, (0, 0, h - 0.015), (w, d, 0.030), tile=0.7)
        P.box(gs["iron_dark"], (0, 0, 0.025), (w + 0.02, d + 0.02, 0.05), tile=0.4)
        # shelves
        for pz in (0.22, 0.74, 1.26):
            P.box(gs["steel"], (0, 0, pz), (w - 0.06, d - 0.05, 0.022), tile=0.4)
            P.box(gs["iron_dark"], (0, -d * 0.5 + 0.02, pz - 0.014), (w - 0.06, 0.020, 0.020),
                  tile=0.2)
        # door, hinged on the front-left edge and swung open toward the room
        ang = radians(-74.0)
        hx, hy = -w * 0.5, -d * 0.5
        ca, sa = cos(ang), sin(ang)

        def door_pt(lx, ly, lz):
            return (hx + lx * ca - ly * sa, hy + lx * sa + ly * ca, lz)

        dc = door_pt(w * 0.5, 0.0, h * 0.5)
        P.box(gs["iron_dark"], dc, (w, 0.026, h * 0.94), rot=(0, 0, ang),
              bevel=0.004, tile=0.7, grain="Z")
        # stiffening ribs on the outside of the door
        for lz in (0.35, 1.30):
            P.box(steel, door_pt(w * 0.5, -0.014, lz), (w * 0.92, 0.012, 0.045),
                  rot=(0, 0, ang), tile=0.3)
        # handle
        hp = door_pt(w * 0.82, -0.030, 1.02)
        P.cylinder(gs["chrome"], hp, 0.013, 0.15, rot=(0, 0, ang), segments=8, tile=0.2)
        P.box(gs["black"], door_pt(w * 0.78, -0.020, 1.02), (0.06, 0.020, 0.10),
              rot=(0, 0, ang), tile=0.2)
        # vents low on the door
        for i in range(4):
            P.box(gs["black"], door_pt(w * 0.5, -0.016, 0.55 + i * 0.045),
                  (0.22, 0.008, 0.016), rot=(0, 0, ang), tile=0.15)
        # hinges
        for hz in (0.26, h - 0.26):
            P.cylinder(gs["chrome"], (hx, hy, hz), 0.020, 0.12,
                       rot=(pi * 0.5, 0, 0), segments=8, tile=0.15)
        # contents: cans, jars, cardboard, toolbox, a mask
        for i in range(5):
            px = -w * 0.26 + i * 0.075
            P.cylinder(gs["label_green"] if i % 2 else gs["label_cream"],
                       (px, -0.06, 0.80), 0.032, 0.11, rot=(pi * 0.5, 0, 0),
                       segments=10, tile=0.2)
        for i in range(3):
            px = -w * 0.22 + i * 0.09
            P.cylinder(gs["glass_amber"], (px, 0.02, 1.32), 0.036, 0.19,
                       segments=12, tile=0.25)
        P.box(gs["cardboard"], (w * 0.10, -0.02, 0.85), (0.22, 0.24, 0.16),
              bevel=0.006, tile=0.4)
        P.box(gs["paper_old"], (w * 0.08, -0.04, 0.94), (0.16, 0.18, 0.02), tile=0.2)
        P.box(gs["red"], (-w * 0.14, -0.02, 0.35), (0.24, 0.20, 0.14),
              bevel=0.008, tile=0.3)
        P.tube(gs["steel"], [(-0.20, -0.02, 0.42), (-0.20, -0.02, 0.48),
                             (-0.08, -0.02, 0.48), (-0.08, -0.02, 0.42)],
               0.008, sides=4, tile=0.1)
        P.sphere(gs["rubber"], (w * 0.16, 0.02, 1.34), (0.10, 0.11, 0.13),
                 subdiv=2, tile=0.4)
        for sx in (-1, 1):
            P.disk(gs["glass"], (w * 0.16 + sx * 0.045, -0.085, 1.37), 0.028,
                   rot=(radians(80), 0, 0), segments=12, tile=0.2)
        # label plate on the side
        P.box(gs["white_paint"], (-w * 0.5 - 0.004, -0.12, 1.58), (0.003, 0.16, 0.06), tile=0.2)
        P.box(gs["black"], (-w * 0.506, -0.12, 1.58), (0.004, 0.12, 0.012), tile=0.1)

    _xform(gs, build, center, rot)


# ---------------------------------------------------------------------------------------
# stove and chimney
# ---------------------------------------------------------------------------------------

def stove(gs, center, rot=(0, 0, 0), scale=1.0):
    s = scale

    def build():
        iron = gs["iron_dark"]
        P.lathe(iron, [(0.0, 0.0), (0.20, 0.0), (0.22, 0.02), (0.24, 0.08),
                       (0.25, 0.36), (0.235, 0.50), (0.20, 0.55), (0.09, 0.58), (0.0, 0.58)],
                center=(0, 0, 0), segments=24, tile=0.7)
        for i in range(3):
            a = tau * i / 3.0 + 0.3
            P.cylinder(iron, (cos(a) * 0.17, sin(a) * 0.17, 0.05), 0.020, 0.10,
                       segments=6, tile=0.2)
        # firebox door with a glowing seam
        P.box(gs["iron"], (0, -0.235, 0.26), (0.26, 0.030, 0.24), bevel=0.008, tile=0.4)
        P.box(gs["ember"], (0, -0.252, 0.20), (0.20, 0.006, 0.020), tile=0.2)
        P.cylinder(gs["steel"], (0.10, -0.255, 0.26), 0.012, 0.09,
                   rot=(0, 0, radians(90)), segments=8, tile=0.1)
        for sx in (-1, 1):
            P.cylinder(gs["iron"], (sx * 0.13, -0.245, 0.16), 0.012, 0.04,
                       rot=(pi * 0.5, 0, 0), segments=6, tile=0.1)
        # top plate and kettle
        P.cylinder(gs["iron"], (0, 0, 0.585), 0.215, 0.025, segments=24, tile=0.4)
        P.lathe(gs["steel_dark"], [(0.0, 0.0), (0.12, 0.0), (0.15, 0.03), (0.14, 0.14),
                                   (0.08, 0.19), (0.03, 0.20)],
                center=(0.0, 0.0, 0.60), segments=20, tile=0.4)
        P.tube(gs["steel_dark"], [(0.0, 0.0, 0.74), (0.0, 0.02, 0.80),
                                  (0.14, 0.02, 0.78), (0.18, 0.02, 0.72)],
               0.010, sides=5, tile=0.2)
        # chimney to the ceiling
        P.cylinder(gs["rust"], (0, 0.06, 0.58 + (2.94 - 0.58) * 0.5), 0.075,
                   2.94 - 0.58, segments=16, tile=0.8)
        for pz in (1.10, 1.80, 2.50):
            P.cylinder(gs["iron"], (0, 0.06, pz), 0.090, 0.045, segments=16, tile=0.3)
        # a small coal scuttle
        P.lathe(gs["galv"], [(0.0, 0.0), (0.10, 0.0), (0.12, 0.02), (0.13, 0.16),
                             (0.125, 0.17)], center=(0.34, -0.10, 0.0), segments=16, tile=0.4)
        P.tube(gs["iron"], [(0.24, -0.10, 0.17), (0.20, -0.12, 0.28),
                            (0.30, -0.12, 0.28), (0.34, -0.10, 0.18)],
               0.006, sides=4, tile=0.1)

    _xform(gs, build, center, rot)


# ---------------------------------------------------------------------------------------
# clutter
# ---------------------------------------------------------------------------------------

def papers(gs, center, rot=(0, 0, 0), count=5, spread=(0.5, 0.35), seed=0):
    rng = random.Random(seed)
    cx, cy, cz = center
    for i in range(count):
        P.box(gs["paper"] if i % 2 else gs["paper_old"],
              (cx + rng.uniform(-spread[0], spread[0]), cy + rng.uniform(-spread[1], spread[1]),
               cz + 0.002 + i * 0.0012),
              (0.16, 0.22, 0.0015), rot=(0, 0, radians(rng.uniform(0, 180))), tile=0.35)


def can_cluster(gs, center, rot=(0, 0, 0), count=4, seed=0):
    rng = random.Random(seed)
    cx, cy, cz = center
    labels = ["label_green", "label_red", "label_cream", "label_blue"]
    for i in range(count):
        px = cx + rng.uniform(-0.12, 0.12)
        py = cy + rng.uniform(-0.10, 0.10)
        rad = rng.uniform(0.028, 0.036)
        hh = rng.uniform(0.075, 0.10)
        P.cylinder(gs["steel"], (px, py, cz + hh * 0.5), rad, hh, segments=14, tile=0.2)
        P.cylinder(gs[labels[i % 4]], (px, py, cz + hh * 0.52), rad * 1.012, hh * 0.55,
                   segments=14, tile=0.2)
        P.cylinder(gs["steel"], (px, py, cz + hh), rad * 1.03, 0.006, segments=14, tile=0.1)
        P.cylinder(gs["steel"], (px, py, cz + 0.004), rad * 1.02, 0.006, segments=14, tile=0.1)


def bottles(gs, center, rot=(0, 0, 0), seed=0):
    rng = random.Random(seed)
    cx, cy, cz = center
    for i in range(3):
        px = cx + rng.uniform(-0.15, 0.15)
        py = cy + rng.uniform(-0.10, 0.10)
        hh = rng.uniform(0.18, 0.26)
        P.cylinder(gs["glass_green"] if i % 2 else gs["glass_amber"],
                   (px, py, cz + hh * 0.5), 0.033, hh, segments=12, tile=0.3)
        P.cylinder(gs["glass_green"] if i % 2 else gs["glass_amber"],
                   (px, py, cz + hh + 0.04), 0.014, 0.08, segments=10, tile=0.2)
        P.cylinder(gs["label_cream"], (px, py, cz + hh * 0.45), 0.034, hh * 0.35,
                   segments=12, tile=0.2)


def rag(gs, center, rot=(0, 0, 0), color="canvas_grey", size=(0.26, 0.20)):
    w, d = size

    def fold(u, v):
        return 0.004 + 0.008 * sin(u * 7.0 + v * 3.0) + 0.004 * sin(v * 9.0)

    P.cloth(gs[color], (center[0] - w * 0.5, center[1] - d * 0.5, center[2]),
            (w, 0, 0), (0, d, 0), (0, 0, 1), 8, 8, 0.004, fold,
            uv_rect=(0.05, 0.05, 0.95, 0.95))


def wall_cable(gs, start, end=None, sag=0.12, radius=0.007, seed=0):
    """Sagging cable. Either start/end points, or a polyline of points in `start`."""
    if end is None:
        pts = [Vector(p) for p in start]
        P.tube(gs["cord"], pts, radius, sides=4, tile=0.3)
        return
    a = Vector(start)
    b = Vector(end)
    pts = []
    for i in range(9):
        t = i / 8.0
        p = a.lerp(b, t)
        p.z -= sag * sin(pi * t)
        pts.append(p)
    P.tube(gs["cord"], pts, radius, sides=4, tile=0.3)


def hanging_cans(gs, center, count=3, seed=0):
    """Noisemakers: a string of tin cans hung by the door."""
    rng = random.Random(seed)
    cx, cy, cz = center
    P.tube(gs["cord"], [(cx, cy, cz), (cx + 0.01, cy, cz - 0.34)], 0.002, sides=3, tile=0.1)
    for i in range(count):
        px = cx + rng.uniform(-0.03, 0.03)
        pz = cz - 0.10 - i * 0.14
        P.cylinder(gs["steel"], (px, cy, pz), 0.030, 0.085, segments=10, tile=0.2)
        P.cylinder(gs["label_green"] if i % 2 else gs["label_red"],
                   (px, cy, pz), 0.0308, 0.040, segments=10, tile=0.2)
        P.tube(gs["cord"], [(cx, cy, pz + 0.10), (px, cy, pz + 0.045)], 0.0018, sides=3, tile=0.1)
