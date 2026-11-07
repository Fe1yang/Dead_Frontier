"""Assemble the cabin: props, wall furniture, rug, lighting fixtures and the GLB export."""

import json
import math
import os
import random
import struct
from math import pi, sin, cos, tau, radians

import bpy
from mathutils import Vector, Euler

import cabin_prims as P
import cabin_room as R
import cabin_props as Q

BACK = R.BACK
WALL_X = R.WALL_X
CEIL = R.CEIL


class Groups(dict):
    """Lazily create one bmesh accumulator per material actually used."""

    def __missing__(self, key):
        grp = P.Group("Cabin_" + key, P.MAT[key])
        self[key] = grp
        return grp


# ---------------------------------------------------------------------------------------
# rug
# ---------------------------------------------------------------------------------------

RUG_X0, RUG_X1 = -1.02, 1.10
RUG_Y0, RUG_Y1 = -1.28, 0.80


def build_rug(gs):
    width = RUG_X1 - RUG_X0
    depth = RUG_Y1 - RUG_Y0

    def folds(u, v):
        edge = min(u, 1.0 - u, v, 1.0 - v)
        ripple = (0.0055 * sin(u * 19.0 + v * 2.3) + 0.0040 * sin(v * 16.0 - u * 3.1))
        sag = 0.010 * (1.0 - min(1.0, edge / 0.16))
        return 0.006 + ripple * (0.25 + 0.75 * (edge < 0.2)) - sag

    P.cloth(gs["rug"], (RUG_X0, RUG_Y0, 0.012), (width, 0, 0), (0, depth, 0), (0, 0, 1),
            34, 28, 0.008, folds, uv_rect=(0.02, 0.02, 0.98, 0.98))

    # braided border, four strips slightly proud of the pile
    wool = gs["wool"]
    for (cx, cy, sx, sy) in (
            ((RUG_X0 + RUG_X1) * 0.5, RUG_Y0 + 0.05, width - 0.06, 0.045),
            ((RUG_X0 + RUG_X1) * 0.5, RUG_Y1 - 0.05, width - 0.06, 0.045),
            (RUG_X0 + 0.05, (RUG_Y0 + RUG_Y1) * 0.5, 0.045, depth - 0.12),
            (RUG_X1 - 0.05, (RUG_Y0 + RUG_Y1) * 0.5, 0.045, depth - 0.12)):
        P.box(wool, (cx, cy, 0.023), (sx, sy, 0.012), bevel=0.005, seg=1, tile=0.5)

    # fringes at both short ends
    rope = gs["rope"]
    for ey in (RUG_Y0 - 0.001, RUG_Y1 + 0.001):
        for i in range(25):
            fx = RUG_X0 + 0.07 + (width - 0.14) * i / 24.0
            fl = random.uniform(0.028, 0.055)
            fy = ey + (-fl if ey < 0 else fl)
            P.tube(rope, [(fx, ey, 0.013), (fx + random.uniform(-0.006, 0.006), fy, 0.011)],
                   0.0035, sides=4, tile=0.2)
            P.sphere(rope, (fx, fy, 0.011), (0.007, 0.009, 0.005), subdiv=1, tile=0.2)


# ---------------------------------------------------------------------------------------
# wall shelf, rifle, hanging herbs
# ---------------------------------------------------------------------------------------

def build_wall_shelf(gs):
    wood = gs["wall"]
    iron = gs["iron_dark"]
    sx0, sx1, sz = -0.94, 0.36, 1.915
    P.box(wood, ((sx0 + sx1) * 0.5, BACK - 0.20, sz),
          (sx1 - sx0, 0.26, 0.038), bevel=0.006, seg=1, tile=1.0, grain="X")
    P.box(wood, ((sx0 + sx1) * 0.5, BACK - 0.065, sz - 0.07),
          (sx1 - sx0, 0.02, 0.12), bevel=0.004, tile=0.8, grain="X")
    for bx in (sx0 + 0.07, sx1 - 0.07):
        P.box(iron, (bx, BACK - 0.07, sz - 0.10), (0.045, 0.03, 0.16),
              bevel=0.003, tile=0.2)
        P.tube(iron, [(bx, BACK - 0.08, sz - 0.18), (bx, BACK - 0.20, sz - 0.13),
                      (bx, BACK - 0.34, sz - 0.01)], 0.008, sides=5, tile=0.2)

    z = sz + 0.019
    Q.jar(gs, (sx0 + 0.10, BACK - 0.20, z), radius=0.045, height=0.13, fill="paper")
    Q.jar(gs, (sx0 + 0.23, BACK - 0.22, z), radius=0.038, height=0.105, fill="label_green")
    Q.can(gs, (sx0 + 0.39, BACK - 0.18, z + 0.058), radius=0.032, height=0.084, label="label_red")
    Q.can(gs, (sx0 + 0.51, BACK - 0.20, z + 0.058), radius=0.030, height=0.08, label="label_cream")
    Q.book(gs, (sx0 + 0.70, BACK - 0.20, z + 0.020), size=(0.16, 0.22, 0.042),
           rot=(0, 0, radians(3)), cover="leather")
    Q.book(gs, (sx0 + 0.70, BACK - 0.20, z + 0.062), size=(0.15, 0.20, 0.036),
           rot=(0, 0, radians(-4)), cover="label_blue")
    Q.mug(gs, (sx0 + 0.92, BACK - 0.21, z), scale=0.95, rot=(0, 0, radians(-20)))
    Q.bottle(gs, (sx0 + 1.08, BACK - 0.20, z), radius=0.033, height=0.20, glass="glass_amber")
    Q.crate(gs, (sx0 + 1.24, BACK - 0.20, z + 0.075), size=(0.15, 0.14, 0.15))
    P.cylinder(gs["wax"], (sx0 + 1.17, BACK - 0.22, z + 0.05), 0.018, 0.10,
               segments=10, tile=0.1)
    P.sphere(gs["flame"], (sx0 + 1.17, BACK - 0.22, z + 0.107),
             (0.011, 0.011, 0.026), subdiv=1, tile=0.1)

    # lever rifle above the shelf
    Q.rifle(gs, (-0.28, BACK - 0.22, 2.315), rot=(0, radians(-4), radians(4)), scale=0.82)

    # dried herbs and a garlic braid hanging from a nail left of the window
    nail_x, nail_z = 0.45, 2.60
    P.cylinder(iron, (nail_x, BACK - 0.13, nail_z), 0.010, 0.10,
               rot=(pi * 0.5, 0, 0), segments=8, tile=0.1)
    _herb_bundle(gs, nail_x - 0.03, nail_z, 0.44, 0.0)
    _herb_bundle(gs, nail_x + 0.03, nail_z, 0.36, 0.7)
    _garlic_braid(gs, nail_x + 0.09, nail_z, 0.34)


def _herb_bundle(gs, x, z_top, length, phase):
    stem = gs["cord"]
    leaf = gs["pine"]
    dry = gs["burlap"]
    pts = [(x, BACK - 0.16, z_top), (x + 0.012, BACK - 0.18, z_top - length * 0.35),
           (x - 0.008, BACK - 0.17, z_top - length * 0.72),
           (x + 0.010, BACK - 0.16, z_top - length)]
    P.tube(stem, pts, 0.004, sides=4, tile=0.2)
    for i in range(9):
        t = 0.20 + 0.78 * i / 8.0
        px = x + 0.010 * sin(i * 2.3 + phase)
        pz = z_top - length * t
        rr = 0.020 + 0.012 * sin(i * 1.7)
        P.sphere(leaf if i % 3 else dry, (px, BACK - 0.19, pz),
                 (rr * 1.2, rr * 0.7, rr * 0.55), rot=(0, radians(20), radians(i * 47)),
                 subdiv=1, tile=0.3)
    P.tube(gs["rope"], [(x - 0.02, BACK - 0.16, z_top - 0.015),
                        (x + 0.03, BACK - 0.17, z_top - 0.025)], 0.006, sides=4, tile=0.1)


def _garlic_braid(gs, x, z_top, length):
    bone = gs["bone"]
    P.tube(gs["cord"], [(x, BACK - 0.16, z_top), (x, BACK - 0.17, z_top - length)],
           0.003, sides=4, tile=0.1)
    for i in range(9):
        pz = z_top - 0.03 - length * i / 10.0
        for side in (-1, 1):
            P.sphere(bone, (x + side * 0.020, BACK - 0.18, pz + side * 0.008),
                     (0.017, 0.015, 0.014), subdiv=1, tile=0.2)


# ---------------------------------------------------------------------------------------
# pendant lamp
# ---------------------------------------------------------------------------------------

PENDANT = (0.80, 1.62, 2.34)  # bulb centre, Blender space


def build_pendant(gs):
    x, y, z = PENDANT
    iron = gs["iron_dark"]
    brass = gs["brass"]
    P.cylinder(iron, (x, y, (CEIL + z + 0.30) * 0.5), 0.008, CEIL - z - 0.30,
               segments=8, tile=0.2)
    P.cylinder(iron, (x, y, CEIL - 0.035), 0.035, 0.05, segments=12, tile=0.2)
    # enamel shade, open at the bottom
    P.lathe(iron, [(0.235, 0.0), (0.245, 0.018), (0.205, 0.085),
                   (0.120, 0.145), (0.045, 0.175)],
            center=(x, y, z + 0.10), segments=28, tile=0.7)
    P.torus(brass, (x, y, z + 0.10), 0.238, 0.007, major_seg=28, minor_seg=5, tile=0.2)
    P.sphere(gs["lamp_glow"], (x, y, z), (0.052, 0.052, 0.075), subdiv=2, tile=0.2)
    P.sphere(gs["flame"], (x, y, z - 0.03), (0.020, 0.020, 0.050), subdiv=2, tile=0.2)
    P.cylinder(iron, (x, y, z + 0.085), 0.026, 0.06, segments=12, tile=0.2)


# ---------------------------------------------------------------------------------------
# workbench, stool, tools
# ---------------------------------------------------------------------------------------

def build_workbench(gs):
    wood = gs["wall"]
    iron = gs["iron_dark"]
    rust = gs["rust"]
    top_z = 0.92
    cx, cy = 1.10, 2.98
    P.box(wood, (cx, cy, top_z), (1.34, 0.54, 0.075), bevel=0.010, seg=2, tile=1.2, grain="X")
    P.box(wood, (cx, cy, top_z - 0.055), (1.20, 0.44, 0.05), bevel=0.006, tile=1.0, grain="X")
    for lx in (cx - 0.58, cx + 0.58):
        for ly in (cy - 0.19, cy + 0.19):
            P.box(wood, (lx, ly, top_z * 0.5 - 0.01), (0.075, 0.075, top_z - 0.05),
                  bevel=0.008, seg=1, tile=1.0, grain="Z")
    # stretchers and a lower shelf
    for ly in (cy - 0.19, cy + 0.19):
        P.box(wood, (cx, ly, 0.28), (1.16, 0.045, 0.05), bevel=0.004, tile=1.0, grain="X")
    P.box(wood, (cx, cy, 0.30), (1.14, 0.40, 0.04), bevel=0.005, tile=1.0, grain="X")
    # small iron vice
    P.box(rust, (cx - 0.53, cy - 0.29, 0.99), (0.13, 0.12, 0.09), bevel=0.008, tile=0.3)
    P.cylinder(iron, (cx - 0.53, cy - 0.36, 0.99), 0.014, 0.12,
               rot=(pi * 0.5, 0, 0), segments=8, tile=0.15)
    P.box(iron, (cx - 0.53, cy - 0.43, 0.99), (0.04, 0.06, 0.035), bevel=0.004, tile=0.2)

    z = top_z + 0.038
    Q.radio(gs, (cx - 0.30, cy - 0.02, z), rot=(0, 0, radians(4)), scale=0.85)
    Q.oil_can(gs, (cx + 0.10, cy + 0.02, z), scale=0.78, rot=(0, 0, radians(-10)))
    Q.mug(gs, (cx + 0.34, cy - 0.09, z), scale=0.9, rot=(0, 0, radians(30)))
    Q.can(gs, (cx + 0.23, cy + 0.13, z + 0.055), radius=0.030, height=0.08, label="label_green")
    Q.can(gs, (cx + 0.34, cy + 0.12, z + 0.055), radius=0.029, height=0.078, label="label_red")
    Q.crate(gs, (cx + 0.50, cy + 0.06, z + 0.085), size=(0.18, 0.17, 0.17))
    Q.plate(gs, (cx - 0.08, cy - 0.22, z), scale=0.8)
    Q.screwdriver(gs, (cx - 0.42, cy - 0.12, z + 0.012), rot=(0, 0, radians(-18)), length=0.17)
    Q.wrench(gs, (cx + 0.02, cy - 0.22, z + 0.014), rot=(0, 0, radians(72)), length=0.19)
    Q.hammer(gs, (cx + 0.45, cy - 0.18, z + 0.020), rot=(0, 0, radians(65)), length=0.26)
    # folded rag
    P.cloth(gs["burlap"], (cx - 0.62, cy - 0.18, z + 0.002), (0.22, 0, 0), (0, 0.16, 0),
            (0, 0, 1), 8, 7, 0.006,
            lambda u, v: 0.008 + 0.006 * sin(u * 9.0 + v * 4.0), uv_rect=(0.1, 0.1, 0.9, 0.9))

    # stool
    _stool(gs, 0.58, 2.24, 0.0)
    # saw leaning against the wall in the corner by the window
    _leaning_saw(gs, 1.66, 3.10, 1.0)


def _stool(gs, x, y, z):
    wood = gs["wall"]
    P.disk(gs["endgrain"], (x, y, z + 0.45), 0.165, segments=24, tile=0.8)
    P.cylinder(wood, (x, y, z + 0.42), 0.17, 0.05, segments=24, tile=0.8)
    for i in range(3):
        a = tau * i / 3.0 + 0.4
        px = x + cos(a) * 0.115
        py = y + sin(a) * 0.115
        P.cylinder(wood, ((px + x * 0.0) * 0.5 + x * 0.5, (py + y) * 0.5, z + 0.215),
                   0.019, 0.46, rot=(radians(7.0) * sin(a), radians(-7.0) * cos(a), 0),
                   segments=8, tile=0.6)


def _leaning_saw(gs, x, y, lean):
    steel = gs["steel"]
    wood = gs["wall"]
    pts = [(-0.02, 0.98), (0.30, 0.98), (0.30, 1.14), (0.02, 1.20), (-0.02, 1.14)]
    P.extrude_xz(steel, pts, y, 0.006, tile=0.3)
    for i in range(12):
        px = 0.01 + 0.28 * i / 11.0
        P.box(steel, (x + px, y, 0.972), (0.012, 0.007, 0.018),
              rot=(0, 0, radians(45)), tile=0.2)
    P.box(wood, (x + 0.02, y, 1.15), (0.06, 0.045, 0.12), bevel=0.008, tile=0.5)


# ---------------------------------------------------------------------------------------
# foreground clutter, crates, barrel, boots, backpack, stump, axe
# ---------------------------------------------------------------------------------------

def build_foreground(gs):
    Q.boots(gs, (-0.72, -0.42, 0.006), rot=(0, 0, radians(14)), scale=1.0, spread=0.17)
    Q.backpack(gs, (-1.22, 2.36, 0.30), rot=(0, 0, radians(-24)), scale=0.92)
    Q.barrel(gs, (-1.28, 1.30, 0.0), radius=0.28, height=0.84, rot=(0, 0, radians(8)))
    Q.barrel(gs, (1.42, 1.55, 0.0), radius=0.26, height=0.78, rot=(0, 0, radians(-14)))
    Q.crate(gs, (-1.86, -0.82, 0.24), size=(0.58, 0.48, 0.48), rot=(0, 0, radians(-7)))
    Q.crate(gs, (-1.92, -0.80, 0.64), size=(0.44, 0.38, 0.32), rot=(0, 0, radians(12)))
    Q.crate(gs, (1.50, 0.45, 0.22), size=(0.44, 0.38, 0.44), rot=(0, 0, radians(5)))
    # chopping block with the hatchet buried in it
    _stump(gs, 0.88, 1.52, 0.0)
    Q.hatchet(gs, (0.88, 1.52, 0.55), rot=(radians(8), radians(-16), radians(22)),
              length=0.34, scale=1.0)
    # scattered planing chips
    for i in range(18):
        a = random.uniform(0, tau)
        r = random.uniform(0.25, 0.75)
        P.box(gs["endgrain"], (0.88 + cos(a) * r, 1.52 + sin(a) * r, 0.012),
              (random.uniform(0.015, 0.045), random.uniform(0.008, 0.02), 0.006),
              rot=(0, 0, random.uniform(0, tau)), tile=0.15)
    # a couple of loose papers near the bench
    for (px, py, ang) in ((0.80, 0.86, 24.0), (0.72, 0.68, -11.0)):
        P.box(gs["paper_old"], (px, py, 0.006), (0.16, 0.21, 0.002),
              rot=(0, 0, radians(ang)), tile=0.4)
    # tin pail by the hearth
    P.lathe(gs["rust"], [(0.0, 0.0), (0.11, 0.0), (0.125, 0.02), (0.13, 0.24), (0.125, 0.25)],
            center=(-1.80, 2.36, 0.0), segments=20, tile=0.5)
    P.torus(gs["iron"], (-1.80, 2.36, 0.25), 0.128, 0.008,
            major_seg=20, minor_seg=5, tile=0.2)


def _stump(gs, x, y, z0):
    P.cylinder(gs["bark"], (x, y, z0 + 0.22), 0.165, 0.44, segments=18, tile=0.45)
    P.disk(gs["endgrain"], (x, y, z0 + 0.441), 0.158, segments=18, tile=0.5)
    for i in range(9):
        a = tau * i / 9.0
        P.cylinder(gs["bark"], (x + cos(a) * 0.155, y + sin(a) * 0.155, z0 + 0.22),
                   0.012, 0.40, segments=6, tile=0.3)


# ---------------------------------------------------------------------------------------
# side walls and the wide-shot details
# ---------------------------------------------------------------------------------------

def build_side_details(gs):
    wood = gs["wall"]
    iron = gs["iron_dark"]
    # left wall: a narrow shelf with ammo crates and a coat on a peg
    for z in (1.35, 1.85):
        P.box(wood, (-WALL_X + 0.24, 1.05, z), (0.42, 1.20, 0.045),
              bevel=0.006, tile=1.0, grain="Y")
        P.box(iron, (-WALL_X + 0.07, 1.72, z - 0.10), (0.04, 0.04, 0.15),
              bevel=0.003, tile=0.2)
    for i, (cy, cw, ch) in enumerate(((0.72, 0.34, 0.26), (1.10, 0.30, 0.22), (1.42, 0.38, 0.30))):
        P.box(wood, (-WALL_X + 0.24, cy, 1.37 + ch * 0.5),
              (0.32, cw, ch), bevel=0.008, tile=1.0, grain="X")
        P.box(iron, (-WALL_X + 0.24, cy, 1.37 + ch * 0.5), (0.34, 0.04, 0.04),
              bevel=0.002, tile=0.2)
    # peg rail with a heavy coat
    P.box(wood, (-WALL_X + 0.08, 2.35, 1.72), (0.06, 1.10, 0.10), bevel=0.006, tile=1.0, grain="Y")
    for i in range(4):
        P.cylinder(iron, (-WALL_X + 0.16, 1.92 + i * 0.28, 1.70), 0.012, 0.14,
                   rot=(0, pi * 0.5, 0), segments=8, tile=0.1)
    P.sphere(gs["leather"], (-WALL_X + 0.26, 2.20, 1.47), (0.17, 0.13, 0.30),
             rot=(0, radians(-6), radians(4)), subdiv=2, tile=0.5)
    P.sphere(gs["leather"], (-WALL_X + 0.27, 2.20, 1.20), (0.14, 0.11, 0.20),
             subdiv=2, tile=0.5)
    # right wall: stacked crates and a coil of rope
    for i, (cy, cz, s) in enumerate(((2.35, 0.25, 0.52), (2.30, 0.74, 0.42), (1.75, 0.22, 0.44))):
        Q.crate(gs, (WALL_X - 0.34, cy, cz), size=(s, s * 0.86, s), rot=(0, 0, radians(i * 9.0)))
    Q.rope_coil(gs, (WALL_X - 0.22, 1.15, 1.62), rot=(0, pi * 0.5, 0), loops=7, radius=0.15)
    # snowshoes hanging on the back wall, far left for the wide shot
    for i, sx in enumerate((-2.30, -2.05)):
        _snowshow(gs, sx, 3.16, 1.83 + i * 0.02)


def _snowshow(gs, x, y, z):
    wood = gs["wall"]
    cord = gs["cord"]
    frame = [(x, y - 0.02, z + 0.34), (x - 0.10, y - 0.02, z + 0.12),
             (x + 0.02, y - 0.02, z - 0.12), (x + 0.13, y - 0.02, z + 0.02),
             (x + 0.10, y - 0.02, z + 0.28), (x, y - 0.02, z + 0.34)]
    P.tube(wood, frame, 0.012, sides=5, tile=0.3)
    for i in range(5):
        t = i / 4.0
        P.tube(cord, [(x - 0.07 + 0.18 * t, y - 0.03, z - 0.02 + 0.34 * t),
                      (x + 0.08 - 0.14 * t, y - 0.03, z + 0.06 + 0.22 * (1.0 - t))],
               0.0025, sides=4, tile=0.1)


# ---------------------------------------------------------------------------------------
# assembly / export
# ---------------------------------------------------------------------------------------

def build_all(gs):
    R.build_floor(gs)
    R.build_back_wall(gs, [R.WINDOW])
    R.build_side_walls(gs)
    R.build_ceiling(gs)
    R.build_frame(gs)
    R.build_window(gs)
    R.build_fireplace(gs)
    R.build_cobwebs(gs)
    build_rug(gs)
    build_wall_shelf(gs)
    build_pendant(gs)
    build_workbench(gs)
    build_foreground(gs)
    build_side_details(gs)


def finish_groups(gs):
    objects = []
    for key, grp in gs.items():
        ob = grp.finish()
        objects.append(ob)
    return objects


def export_scene(gs):
    objects = finish_groups(gs)
    total_v = sum(len(o.data.vertices) for o in objects)
    total_t = sum(len(o.data.loop_triangles) for o in objects) if False else 0
    for o in objects:
        o.data.calc_loop_triangles()
        total_t += len(o.data.loop_triangles)
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    for o in objects:
        for c in o.bound_box:
            p = o.matrix_world @ Vector(c)
            for i in range(3):
                lo[i] = min(lo[i], p[i])
                hi[i] = max(hi[i], p[i])
    print("CABIN_OBJECTS", len(objects), "VERTS", total_v, "TRIS", total_t)
    print("CABIN_BOUNDS", tuple(round(v, 3) for v in lo), tuple(round(v, 3) for v in hi))
    print("CABIN_MATERIALS", len(objects))

    for ob in bpy.context.scene.objects:
        ob.select_set(ob.type == "MESH")
    bpy.ops.export_scene.gltf(
        filepath=P.OUT_GLB,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_cameras=False,
        export_lights=False,
        export_image_format="AUTO",
        export_texcoords=True,
        export_normals=True,
        export_materials="EXPORT",
    )
    bpy.ops.wm.save_as_mainfile(filepath=P.OUT_BLEND)
    size = os.path.getsize(P.OUT_GLB)
    print("CABIN_EXPORT_OK", P.OUT_GLB, round(size / (1024 * 1024), 2), "MB")

    # quick summary of the exported glTF materials / textures
    with open(P.OUT_GLB, "rb") as f:
        data = f.read()
    off = 12
    j = None
    while off < len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        if ctype == 0x4E4F534A:
            j = json.loads(data[off + 8:off + 8 + clen].decode("utf-8").rstrip("\x00 "))
            break
        off += 8 + clen
    if j:
        print("CABIN_GLTF_MESHES", len(j.get("meshes", [])), "MATERIALS", len(j.get("materials", [])),
              "IMAGES", len(j.get("images", [])))
