"""Assemble the safehouse interior and export assets/models/environment/safehouse_interior.glb.

Blender space: X right, Y away from the lobby camera, Z up. The room is x in
[-2.62, 2.62], y in [-2.55, 3.34], ceiling at 2.94.

The lobby camera is portrait and close, so only three bands of the room actually
reach the frame:
  * left  band  x -1.55..-0.56  -> blast door, sandbags, footlocker
  * right band  x  0.45..1.37   -> boarded window, workbench, stool
  * upper band  z  2.05..2.74   -> map board, rifle, pipes, damp
The survivor stands at Blender (x=-0.08, y=0), hiding the middle below ~2.0 m,
so nothing important is authored there. Wide shots still get a cot, shelving,
a stove and the generator in the wings.
"""

import json
import math
import os
import random
import struct
from math import pi, sin, cos, tau, radians

import bpy
from mathutils import Vector, Euler

import cabin_prims as P
import bunker_room as R
import cabin_props as Q
import bunker_props as B

BACK = R.BACK
WALL_X = R.WALL_X
CEIL = R.CEIL
FRONT = R.FRONT

DOOR_CX = -1.05
DOOR_W = 0.98
DOOR_H = 2.04

BENCH_CX = 0.95
BENCH_W = 1.00
BENCH_Y = 3.00
BENCH_D = 0.55
TOP = 0.94


class Groups(dict):
    """Lazily create one bmesh accumulator per material actually used."""

    def __missing__(self, key):
        grp = P.Group("Safe_" + key, P.MAT[key])
        self[key] = grp
        return grp


def rnd(a, b):
    return random.uniform(a, b)


# ---------------------------------------------------------------------------------------
# the blast door on the back wall (the strongest "this is a shelter" read)
# ---------------------------------------------------------------------------------------

def build_blast_door(gs):
    cx, w, h = DOOR_CX, DOOR_W, DOOR_H
    steel = gs["steel_dark"]
    iron = gs["iron"]
    rust = gs["rust"]

    # concrete reveal, a touch recessed and grimy
    P.box(gs["concrete_dark"], (cx, BACK - 0.012, h * 0.5),
          (w + 0.30, 0.035, h + 0.26), tile=0.9, grain="X")

    # heavy angle-iron frame
    for sx in (-1, 1):
        P.box(steel, (cx + sx * (w * 0.5 + 0.055), BACK - 0.060, h * 0.5),
              (0.11, 0.13, h + 0.20), bevel=0.006, tile=0.5, grain="Z")
        # bolt plates on the frame
        for bz in (0.18, 0.72, 1.30, 1.86):
            P.box(gs["galv"], (cx + sx * (w * 0.5 + 0.055), BACK - 0.128, bz),
                  (0.075, 0.012, 0.075), bevel=0.004, tile=0.2)
    P.box(steel, (cx, BACK - 0.060, h + 0.045), (w + 0.22, 0.13, 0.11),
          bevel=0.006, tile=0.5)

    # the slab itself
    P.box(steel, (cx, BACK - 0.125, h * 0.5), (w, 0.13, h),
          bevel=0.010, seg=2, tile=1.1, grain="Z")

    # rust blooms and scraped paint on the face
    for i in range(10):
        P.box(rust, (cx + rnd(-0.34, 0.34), BACK - 0.192, rnd(0.22, 1.88)),
              (rnd(0.04, 0.15), 0.004, rnd(0.03, 0.12)),
              rot=(0, 0, rnd(-0.4, 0.4)), tile=0.4)
    # painted stencil number: three bars and a block
    for i in range(3):
        P.box(gs["white_paint"], (cx - 0.20 + i * 0.055, BACK - 0.194, 1.90),
              (0.030, 0.004, 0.075), tile=0.1)
    P.box(gs["white_paint"], (cx + 0.03, BACK - 0.194, 1.90), (0.075, 0.004, 0.028), tile=0.1)
    P.box(gs["white_paint"], (cx + 0.03, BACK - 0.194, 1.855), (0.075, 0.004, 0.028), tile=0.1)

    # X brace
    for ang in (37.0, -37.0):
        P.box(gs["steel"], (cx, BACK - 0.196, 1.00), (0.038, 0.045, 1.66),
              rot=(0, radians(ang), 0), bevel=0.004, tile=0.8, grain="Z")
    P.box(iron, (cx, BACK - 0.212, 1.00), (0.16, 0.020, 0.16), bevel=0.006, tile=0.3)

    # rivet grid
    for row in range(7):
        for col in range(4):
            P.sphere(gs["steel"], (cx - 0.375 + col * 0.25, BACK - 0.192, 0.24 + row * 0.26),
                     (0.013, 0.008, 0.013), subdiv=1, tile=0.1)

    # hazard band along the bottom
    for i in range(9):
        col = gs["yellow"] if i % 2 == 0 else gs["black"]
        P.box(col, (cx - 0.42 + i * 0.105, BACK - 0.194, 0.19),
              (0.058, 0.005, 0.34), rot=(0, radians(30), 0), tile=0.3)

    # wheel handle
    hz = 1.16
    P.cylinder(iron, (cx, BACK - 0.225, hz), 0.050, 0.075,
               rot=(pi * 0.5, 0, 0), segments=14, tile=0.2)
    P.torus(gs["red"], (cx, BACK - 0.255, hz), 0.155, 0.017,
            rot=(pi * 0.5, 0, 0), major_seg=24, minor_seg=6, tile=0.2)
    for i in range(4):
        a = tau * i / 4.0 + 0.35
        P.box(gs["red"], (cx + cos(a) * 0.077, BACK - 0.255, hz + sin(a) * 0.077),
              (0.022, 0.020, 0.155), rot=(0, a, 0), tile=0.15)

    # hinges on the left edge
    for hzz in (0.34, 1.02, 1.70):
        P.cylinder(iron, (cx - w * 0.5 - 0.030, BACK - 0.150, hzz), 0.032, 0.22,
                   segments=10, tile=0.2)
        P.box(iron, (cx - w * 0.5 + 0.010, BACK - 0.150, hzz), (0.075, 0.055, 0.15),
              bevel=0.004, tile=0.2)

    # peephole, latch bar and a keypad
    P.cylinder(gs["chrome"], (cx + 0.26, BACK - 0.200, 1.66), 0.026, 0.030,
               rot=(pi * 0.5, 0, 0), segments=12, tile=0.1)
    P.disk(gs["soot"], (cx + 0.26, BACK - 0.216, 1.66), 0.017,
           rot=(pi * 0.5, 0, 0), segments=10, tile=0.1)
    P.box(iron, (cx + w * 0.5 - 0.09, BACK - 0.196, 1.66), (0.030, 0.045, 0.30),
          bevel=0.003, tile=0.2)
    P.box(gs["olive_dark"], (cx + w * 0.5 + 0.14, BACK - 0.150, 1.52),
          (0.10, 0.075, 0.22), bevel=0.005, tile=0.3)
    for row in range(3):
        for col in range(3):
            P.box(gs["black"], (cx + w * 0.5 + 0.155, BACK - 0.190, 1.575 - row * 0.040),
                  (0.017, 0.005, 0.024), tile=0.05)
    P.box(gs["led_green"], (cx + w * 0.5 + 0.155, BACK - 0.191, 1.63),
          (0.013, 0.004, 0.013), tile=0.05)

    # chain and padlock slung across the wheel
    Q.chain(gs, [(cx - 0.44, BACK - 0.225, 1.02), (cx - 0.10, BACK - 0.300, 0.86),
                 (cx + 0.26, BACK - 0.225, 1.02)], link=0.028, scale=1.0)
    P.box(gs["brass"], (cx + 0.30, BACK - 0.245, 0.92), (0.055, 0.075, 0.10),
          bevel=0.006, tile=0.2)
    P.torus(gs["brass"], (cx + 0.30, BACK - 0.245, 1.00), 0.032, 0.006,
            rot=(pi * 0.5, 0, 0), major_seg=10, minor_seg=4, tile=0.1)

    # red emergency lamp on the left of the frame
    lx, lz = cx - w * 0.5 - 0.16, 2.36
    P.box(gs["iron_dark"], (lx, BACK - 0.10, lz), (0.14, 0.10, 0.085),
          bevel=0.004, tile=0.3)
    P.sphere(gs["red"], (lx, BACK - 0.19, lz), (0.048, 0.030, 0.038),
             subdiv=2, tile=0.2)
    P.sphere(gs["led_red"], (lx, BACK - 0.205, lz), (0.030, 0.014, 0.024),
             subdiv=2, tile=0.1)
    P.box(gs["yellow"], (lx, BACK - 0.10, lz - 0.10), (0.10, 0.004, 0.055), tile=0.2)


# ---------------------------------------------------------------------------------------
# workbench under the boarded window
# ---------------------------------------------------------------------------------------

def build_bench(gs):
    cx, cy, w, d = BENCH_CX, BENCH_Y, BENCH_W, BENCH_D
    steel = gs["steel_dark"]
    iron = gs["iron"]

    # top: grey weathered planks on a steel frame
    P.box(gs["bench_wood"], (cx, cy, TOP - 0.0425), (w, d, 0.085),
          bevel=0.008, seg=2, tile=1.4, grain="X")
    P.box(steel, (cx, cy, TOP - 0.100), (w + 0.02, d + 0.02, 0.020), tile=0.6)
    for sx in (-1, 1):
        for sy in (-1, 1):
            P.box(steel, (cx + sx * (w * 0.5 - 0.055), cy + sy * (d * 0.5 - 0.055),
                          (TOP - 0.10) * 0.5),
                  (0.050, 0.050, TOP - 0.10), bevel=0.004, tile=0.4)
        P.box(iron, (cx + sx * (w * 0.5 - 0.055), cy, 0.30), (0.038, d - 0.12, 0.038), tile=0.3)
        P.box(iron, (cx + sx * (w * 0.5 - 0.055), cy, 0.63), (0.030, d - 0.12, 0.030), tile=0.3)
    P.box(steel, (cx, cy, 0.32), (w - 0.11, d - 0.11, 0.018), tile=0.6)
    # back riser so the bench meets the wall cleanly
    P.box(steel, (cx, BACK - 0.045, TOP + 0.07), (w, 0.05, 0.14), tile=0.5)

    # bench vice at the left end
    P.box(gs["rust"], (cx - 0.36, cy - 0.14, TOP + 0.075), (0.17, 0.16, 0.10),
          bevel=0.010, tile=0.3)
    P.box(gs["rust"], (cx - 0.36, cy - 0.24, TOP + 0.095), (0.14, 0.08, 0.065),
          bevel=0.006, tile=0.3)
    P.cylinder(gs["chrome"], (cx - 0.36, cy - 0.34, TOP + 0.095), 0.013, 0.16,
               rot=(pi * 0.5, 0, 0), segments=10, tile=0.1)
    P.box(gs["black"], (cx - 0.36, cy + 0.01, TOP + 0.095), (0.022, 0.09, 0.030), tile=0.1)

    # radio with its antenna — the lounge's one bit of tech
    Q.radio(gs, (cx - 0.16, cy + 0.06, TOP + 0.043), rot=(0, 0, radians(3)), scale=0.92)
    # tidy bench: lantern + mug + a closed book only. No clutter.
    Q.lantern(gs, (cx + 0.39, cy - 0.13, TOP), scale=0.92, rot=(0, 0, radians(12)), lit=True)
    Q.mug(gs, (cx + 0.10, cy - 0.10, TOP), scale=0.92, rot=(0, 0, radians(-35)))
    Q.book(gs, (cx + 0.02, cy + 0.23, TOP + 0.012), size=(0.15, 0.20, 0.028),
           rot=(0, 0, radians(9)), cover="label_blue")

    # one neat crate under the bench
    Q.crate(gs, (cx - 0.24, cy + 0.02, 0.34), size=(0.46, 0.38, 0.32),
            rot=(0, 0, radians(4)))


def build_window_dressing(gs):
    # blackout curtain bunched over the right half of the window
    x0, x1 = 0.99, 1.60
    ztop = 2.34
    y = BACK - 0.16
    P.cylinder(gs["galv"], ((0.55 + 1.66) * 0.5, y, ztop + 0.035), 0.011, 1.16,
               rot=(0, pi * 0.5, 0), segments=10, tile=0.3)
    for px in (0.56, 1.65):
        P.cylinder(gs["iron"], (px, y, ztop + 0.035), 0.017, 0.07,
                   rot=(0, pi * 0.5, 0), segments=8, tile=0.15)

    phase = 2.1

    def folds(u, v):
        return (0.040 * sin(u * 15.0 + phase) * (0.30 + 0.70 * v)
                + 0.018 * sin(u * 7.0 - phase) * v)

    P.cloth(gs["canvas"], (x0, y, ztop), (x1 - x0, 0, 0), (0, 0, -1.02),
            (0, -1, 0), 18, 14, 0.006, folds, uv_rect=(0.03, 0.03, 0.97, 0.97))
    # a couple of fold-ties
    for tz in (1.92, 1.52):
        P.torus(gs["cord"], ((x0 + x1) * 0.5, y - 0.02, tz), 0.055, 0.006,
                rot=(0, 0, 0), major_seg=12, minor_seg=4, tile=0.1)

    # cold night leaking through the gaps: use ONLY the night quad in bunker_room.
    # (The old window_glow card sat 3cm from it and flickered against the boards.)

    # sill: lantern + mug only — calm, not a pile.
    Q.lantern(gs, (0.70, BACK - 0.16, 1.122), scale=0.86, rot=(0, 0, radians(-12)), lit=True)
    Q.mug(gs, (1.32, BACK - 0.13, 1.122), scale=0.80, rot=(0, 0, radians(70)))


# ---------------------------------------------------------------------------------------
# things on the back wall
# ---------------------------------------------------------------------------------------

def build_map_board(gs):
    B.map_board(gs, (DOOR_CX, BACK - 0.055, 2.36), rot=(0, 0, 0), size=(0.78, 0.44), seed=5)
    # a felt-tip pen on a string and two spare pins
    P.box(gs["white_paint"], (DOOR_CX + 0.32, BACK - 0.075, 2.12), (0.09, 0.003, 0.05), tile=0.2)


def build_wall_kit(gs):
    # lever rifle over the window + one tidy shelf. Nothing dangling.
    Q.rifle(gs, (1.04, BACK - 0.055, 2.44), rot=(0, 0, radians(-2)), scale=0.66)
    P.box(gs["iron"], (1.04, BACK - 0.040, 2.58), (0.34, 0.03, 0.035), tile=0.2)

    # a shelf above the window on brackets
    P.box(gs["steel_dark"], (1.44, BACK - 0.12, 2.30), (0.62, 0.20, 0.022), tile=0.5, grain="X")
    for sx in (-1, 1):
        P.box(gs["iron"], (1.44 + sx * 0.24, BACK - 0.12, 2.24), (0.020, 0.20, 0.11),
              tile=0.2)
    Q.jar(gs, (1.30, BACK - 0.12, 2.312), radius=0.042, height=0.115, fill="label_cream")
    B.can_cluster(gs, (1.58, BACK - 0.12, 2.312), count=2, seed=21)


# ---------------------------------------------------------------------------------------
# left side: sandbags, footlocker, water
# ---------------------------------------------------------------------------------------

def build_lounge(gs):
    """Tidy rest corner: footlocker + closed jerrycans + one lantern. No sandbags,
    no tarps, no loose gear on the floor — this is where the survivor rests."""
    B.footlocker(gs, (-1.03, 1.62, 0.0), rot=(0, 0, radians(5)), size=(0.96, 0.54, 0.42))
    B.jerrycan(gs, (-1.20, 1.58, 0.43), rot=(0, 0, radians(6)), scale=0.94)
    B.jerrycan(gs, (-0.93, 1.55, 0.43), rot=(0, 0, radians(-8)), scale=0.92, body="olive_light", cap="yellow")
    Q.lantern(gs, (-1.06, 1.42, 0.43), scale=0.90, rot=(0, 0, radians(-14)), lit=True)

    # cot + sleeping bag along the right wall, shelf above — the "rest" read
    B.cot(gs, (2.02, 1.02, 0.0), rot=(0, 0, radians(90)))
    B.sleeping_bag(gs, (2.06, 1.28, 0.50), rot=(0, 0, radians(90)), color="wool", seed=3)
    B.shelf_unit(gs, (2.06, 2.98, 0.0), rot=(0, 0, 0), width=1.05, depth=0.40, height=1.86)
    for i in range(4):
        B.can_cluster(gs, (1.74 + i * 0.22, 3.02, 1.14), count=2, seed=40 + i)
    Q.crate(gs, (2.26, 3.00, 1.68), size=(0.30, 0.30, 0.26))
    B.ammo_box(gs, (1.76, 3.00, 0.63), size=(0.38, 0.24, 0.22))
    # locker on the left wall + pot stove in the back-left corner
    B.locker(gs, (-2.40, 1.72, 0.0), rot=(0, 0, radians(90)), width=0.56, depth=0.46, height=1.88)
    B.stove(gs, (-2.16, 2.80, 0.0), rot=(0, 0, radians(-14)))


# ---------------------------------------------------------------------------------------
# assembly / export
# ---------------------------------------------------------------------------------------

def build_all(gs):
    R.build_floor(gs)
    R.build_shell(gs)
    R.build_electrics(gs)
    R.build_ceiling_steel(gs)
    R.build_lights(gs)
    R.build_window(gs)
    R.build_door(gs)

    build_blast_door(gs)
    build_bench(gs)
    build_window_dressing(gs)
    build_map_board(gs)
    build_wall_kit(gs)
    build_lounge(gs)


def finish_groups(gs):
    objects = []
    for key, grp in gs.items():
        ob = grp.finish()
        objects.append(ob)
    return objects


def export_scene(gs):
    objects = finish_groups(gs)
    total_v = sum(len(o.data.vertices) for o in objects)
    total_t = 0
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
    print("SAFE_OBJECTS", len(objects), "VERTS", total_v, "TRIS", total_t)
    print("SAFE_BOUNDS", tuple(round(v, 3) for v in lo), tuple(round(v, 3) for v in hi))

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
    print("SAFE_EXPORT_OK", P.OUT_GLB, round(size / (1024 * 1024), 2), "MB")

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
        print("SAFE_GLTF_MESHES", len(j.get("meshes", [])), "MATERIALS", len(j.get("materials", [])),
              "IMAGES", len(j.get("images", [])))
