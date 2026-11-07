"""Shell of the safehouse: a damp concrete basement in a ruined city block.

Blender space: X right, Y away from the lobby camera, Z up. The back wall sits at
y = 3.34 and the camera hovers near y = -4.15, so only about x in [-1.8, 1.75] fits
the portrait frame. Every hero prop is packed into that band; the rest of the room
exists for the wide shots, for light bounces and for any later camera push.

Palette rules: concrete grey, cyan light, rust, olive drab, hazard yellow and a few
faded red/white accents. No all-over brown.
"""

import math
import random
from math import pi, sin, cos, tau, radians

from mathutils import Vector

import cabin_prims as P
import cabin_props as Q

BACK = 3.34
WALL_X = 2.62
CEIL = 2.94
FRONT = -2.55

WINDOW = (0.62, 1.46, 1.12, 2.18)      # x0, x1, z0, z1  (boarded-up window)
DOOR_Y = (0.58, 1.58)                   # left wall opening, along Y
DOOR_Z = 2.06

rv = random.uniform


def rnd(a, b):
    return random.uniform(a, b)


def _blob(cx, cz, rx, rz, n=26, seed=0, rough=0.13):
    rng = random.Random(seed)
    pts = []
    for i in range(n):
        a = tau * i / n
        r = 1.0 + rng.uniform(-rough, rough)
        pts.append((cx + rx * r * cos(a), cz + rz * r * sin(a)))
    return pts


def _crack(gs, start, steps=9, step=0.22, spread=0.55, radius=0.0035, seed=0):
    rng = random.Random(seed)
    x, y = start
    pts = [(x, y, 0.0025)]
    ang = rng.uniform(0, tau)
    for i in range(steps):
        ang += rng.uniform(-spread, spread)
        x += cos(ang) * step * rng.uniform(0.5, 1.4)
        y += sin(ang) * step * rng.uniform(0.5, 1.4)
        pts.append((x, y, 0.0025 + rng.uniform(0.0, 0.0012)))
        if rng.random() < 0.25:
            # small branch
            bx, by = pts[-1][0], pts[-1][1]
            bp = [(bx, by, 0.0025)]
            ba = ang + rng.uniform(-1.1, 1.1)
            for k in range(3):
                bx += cos(ba) * 0.10
                by += sin(ba) * 0.10
                bp.append((bx, by, 0.0025))
            P.tube(gs["soot"], bp, radius * 0.55, sides=3, tile=0.2)
    P.tube(gs["soot"], pts, radius, sides=3, tile=0.2)


# ---------------------------------------------------------------------------------------
# floor
# ---------------------------------------------------------------------------------------

def build_floor(gs):
    floor = gs["floor"]
    dark = gs["floor_dark"]
    # structural slab
    P.box(dark, (0.0, (FRONT + BACK) * 0.5, -0.075),
          (WALL_X * 2.0 + 0.3, BACK - FRONT + 0.3, 0.15), tile=2.4, grain="X")

    # clean concrete slabs only — this is a tidy rest lounge, no debris, no cables,
    # no papers, no cracks, no blood, no paint on the floor.
    x = -WALL_X - 0.02
    while x < WALL_X + 0.02:
        w = rnd(0.92, 1.18)
        x1 = min(x + w, WALL_X + 0.02)
        y = FRONT - 0.02
        while y < BACK + 0.02:
            d = rnd(0.92, 1.20)
            y1 = min(y + d, BACK + 0.02)
            P.box(floor,
                  ((x + x1) * 0.5, (y + y1) * 0.5, -0.020 + rnd(-0.0025, 0.0025)),
                  (max(0.1, x1 - x - 0.008), max(0.1, y1 - y - 0.008), 0.042),
                  bevel=0.004, seg=1, tile=1.55, grain="X")
            y = y1
        x = x1

    # a simple worn rug under the survivor's feet so the stage reads as a lounge
    P.box(gs["rug"], (0.0, 0.55, 0.006), (2.1, 1.7, 0.012), bevel=0.004, seg=1, tile=1.2)
    P.box(gs["rug"], (0.0, 0.55, 0.014), (1.7, 1.3, 0.004), tile=1.0)
    # drain, flush and neat against the left wall — no loose grate bars
    P.box(gs["steel_dark"], (-1.55, 0.86, 0.004), (0.34, 0.34, 0.008), bevel=0.003, tile=0.5)
    P.box(gs["soot"], (-1.55, 0.86, 0.007), (0.24, 0.24, 0.010), tile=0.4)


# ---------------------------------------------------------------------------------------
# shell: walls, ceiling, formwork seams, damp, plaster, brick
# ---------------------------------------------------------------------------------------

def build_shell(gs):
    conc = gs["concrete"]
    dark = gs["concrete_dark"]
    x0, x1, z0, z1 = WINDOW

    # back wall, built around the window opening
    pieces = [
        ((-WALL_X + x0) * 0.5, (x0 + WALL_X), CEIL * 0.5, CEIL),
        ((x1 + WALL_X) * 0.5, (WALL_X - x1), CEIL * 0.5, CEIL),
        ((x0 + x1) * 0.5, (x1 - x0), z0 * 0.5, z0),
        ((x0 + x1) * 0.5, (x1 - x0), (z1 + CEIL) * 0.5, CEIL - z1),
    ]
    for (cx, sx, cz, sz) in pieces:
        P.box(conc, (cx, BACK + 0.09, cz), (sx, 0.18, sz), tile=1.6, grain="X")

    # side walls and ceiling
    for sx in (-1.0, 1.0):
        P.box(conc, (sx * (WALL_X + 0.09), (FRONT + BACK) * 0.5, CEIL * 0.5),
              (0.18, BACK - FRONT, CEIL), tile=1.6, grain="Y")
    P.box(conc, (0.0, (FRONT + BACK) * 0.5, CEIL + 0.09),
          (WALL_X * 2.0 + 0.36, BACK - FRONT + 0.36, 0.18), tile=1.8, grain="X")

    # formwork seams: precast panel joints, slightly recessed and grubby
    for px in (-2.18, -1.42, -0.66, 0.14, 1.94, 2.36):
        if x0 - 0.05 < px < x1 + 0.05:
            continue
        P.box(dark, (px, BACK - 0.004, CEIL * 0.5), (0.018, 0.010, CEIL), tile=0.5)
    for pz in (1.46, 2.30):
        P.box(dark, (0.0, BACK - 0.004, pz), (WALL_X * 2.0, 0.010, 0.018), tile=0.5)
    for sx in (-1.0, 1.0):
        for py in (-1.55, -0.35, 0.85, 2.05):
            P.box(dark, (sx * (WALL_X - 0.004), py, CEIL * 0.5),
                  (0.010, 0.018, CEIL), tile=0.5)

    # tie-rod holes
    for px in (-2.28, -1.80, -1.10, -0.34, 0.30, 1.02, 1.78, 2.30):
        for pz in (0.62, 1.14, 2.02, 2.62):
            if x0 - 0.1 < px < x1 + 0.1 and z0 - 0.1 < pz < z1 + 0.1:
                continue
            P.disk(gs["soot"], (px, BACK - 0.002, pz), 0.020,
                   rot=(pi * 0.5, 0, 0), segments=10, tile=0.1)

    # clean concrete walls — panel seams and tie holes only, no damp, plaster or grime.
    # (Kept subtle so the room reads tidy, not ruined.)


# ---------------------------------------------------------------------------------------
# electrical panel, conduits, pipes and cables
# ---------------------------------------------------------------------------------------

def build_electrics(gs):
    steel = gs["steel_dark"]
    iron = gs["iron"]
    galv = gs["galv"]
    panel_x, panel_z = 1.98, 2.56
    # backboard and cabinet
    P.box(gs["black"], (panel_x, BACK - 0.035, panel_z), (0.40, 0.06, 0.52), tile=0.6)
    P.box(steel, (panel_x, BACK - 0.085, panel_z), (0.34, 0.10, 0.46), bevel=0.006, tile=0.5)
    P.box(gs["steel"], (panel_x, BACK - 0.145, panel_z), (0.30, 0.012, 0.42), bevel=0.002, tile=0.4)
    # breaker rows
    for r in range(3):
        for c in range(4):
            P.box(gs["black"], (panel_x - 0.10 + c * 0.066, BACK - 0.155, panel_z + 0.10 - r * 0.075),
                  (0.044, 0.016, 0.052), bevel=0.002, tile=0.15)
            if (r + c) % 3 == 0:
                P.box(gs["white_paint"], (panel_x - 0.10 + c * 0.066, BACK - 0.166, panel_z + 0.10 - r * 0.075),
                      (0.030, 0.008, 0.010), tile=0.1)
    # warning sticker and status LEDs
    P.box(gs["yellow"], (panel_x + 0.11, BACK - 0.155, panel_z + 0.17), (0.075, 0.004, 0.065), tile=0.2)
    P.box(gs["led_green"], (panel_x + 0.11, BACK - 0.159, panel_z + 0.17), (0.020, 0.004, 0.020), tile=0.1)
    P.box(gs["led_red"], (panel_x + 0.11, BACK - 0.159, panel_z + 0.12), (0.020, 0.004, 0.020), tile=0.1)

    # conduit: short vertical to the ceiling + ONE straight horizontal run.
    # No sagging bundles, no drooping drops — tidy lounge, not a workshop.
    P.cylinder(galv, (panel_x + 0.10, BACK - 0.06, (CEIL + panel_z + 0.26) * 0.5),
               0.015, CEIL - panel_z - 0.26, segments=10, tile=0.3)
    run_z = panel_z + 0.12
    P.cylinder(galv, ((panel_x - 0.10) * 0.5, BACK - 0.06, run_z), 0.014,
               panel_x + 0.10, rot=(0, pi * 0.5, 0), segments=10, tile=0.3)
    for bx in (0.42, 1.20):
        P.box(iron, (bx, BACK - 0.06, run_z), (0.05, 0.07, 0.09), bevel=0.003, tile=0.2)


# ---------------------------------------------------------------------------------------
# ceiling steel and light fittings
# ---------------------------------------------------------------------------------------

def build_ceiling_steel(gs):
    steel = gs["steel_dark"]
    iron = gs["iron"]
    for by in (-1.35, 0.32, 1.98):
        P.box(steel, (0.0, by, CEIL - 0.115), (WALL_X * 2.0, 0.155, 0.020), tile=1.4, grain="X")
        P.box(steel, (0.0, by, CEIL - 0.180), (WALL_X * 2.0, 0.030, 0.115), tile=1.4, grain="X")
        P.box(steel, (0.0, by, CEIL - 0.245), (WALL_X * 2.0, 0.155, 0.020), tile=1.4, grain="X")
        for px in (-2.2, -1.45, -0.7, 0.05, 0.8, 1.55, 2.3):
            for sy in (-1, 1):
                P.cylinder(iron, (px, by + sy * 0.045, CEIL - 0.130), 0.010, 0.014,
                           rot=(pi * 0.5, 0, 0), segments=6, tile=0.08)
        # end plates bolted into the concrete
        for sx in (-1, 1):
            P.box(steel, (sx * (WALL_X - 0.02), by, CEIL - 0.18), (0.10, 0.26, 0.30),
                  bevel=0.005, tile=0.4)


def build_lights(gs):
    iron = gs["iron"]
    steel = gs["steel"]
    # ---- twin fluorescent batten, hanging over the bench --------------------------
    fx, fy, fz = 0.95, 2.62, 2.56
    P.box(steel, (fx, fy, fz + 0.045), (1.26, 0.20, 0.07), bevel=0.005, tile=0.6, grain="X")
    for sy in (-1, 1):
        P.box(gs["galv"], (fx, fy + sy * 0.135, fz + 0.010), (1.26, 0.11, 0.055),
              rot=(radians(24) * sy, 0, 0), tile=0.5, grain="X")
    for sx in (-1, 1):
        P.box(gs["white_paint"], (fx + sx * 0.615, fy, fz + 0.010), (0.045, 0.20, 0.075), tile=0.3)
    for sy in (-1, 1):
        P.cylinder(gs["fluor"], (fx, fy + sy * 0.050, fz - 0.035), 0.016, 1.14,
                   rot=(0, pi * 0.5, 0), segments=12, tile=0.4)
        for sx in (-1, 1):
            P.cylinder(gs["galv"], (fx + sx * 0.575, fy + sy * 0.050, fz - 0.035), 0.020, 0.045,
                       rot=(0, pi * 0.5, 0), segments=12, tile=0.2)
    for sx in (-1, 1):
        P.cylinder(iron, (fx + sx * 0.48, fy, (CEIL + fz) * 0.5), 0.008,
                   CEIL - fz - 0.05, segments=6, tile=0.3)
        P.torus(iron, (fx + sx * 0.48, fy, CEIL - 0.05), 0.026, 0.006,
                rot=(0, 0, 0), major_seg=12, minor_seg=4, tile=0.1)
        # little pull chain
        for k in range(4):
            P.torus(iron, (fx + sx * 0.40, fy - 0.10, fz - 0.10 - k * 0.028), 0.011, 0.003,
                    rot=(pi * 0.5, 0, 0), major_seg=8, minor_seg=3, tile=0.05)

    # ---- caged trouble lamp over the window side ----------------------------------
    lx, ly, lz = 1.04, 2.30, 2.30
    P.tube(gs["cord"], [(lx, ly, CEIL - 0.06), (lx + 0.01, ly - 0.02, 2.55), (lx, ly, lz + 0.20)],
           0.007, sides=4, tile=0.2)
    P.cylinder(iron, (lx, ly, lz + 0.16), 0.026, 0.07, segments=10, tile=0.15)
    P.sphere(gs["fluor"], (lx, ly, lz), (0.055, 0.055, 0.070), subdiv=2, tile=0.2)
    # spring cage: vertical arcs and two rings
    for i in range(6):
        a = tau * i / 6.0
        pts = []
        for k in range(9):
            t = k / 8.0
            rr = 0.070 * (1.0 - 0.25 * t) * cos(pi * 0.5 * (t - 0.5) ** 2)
            pts.append((lx + cos(a) * rr, ly + sin(a) * rr, lz - 0.11 + t * 0.24))
        P.tube(iron, pts, 0.0035, sides=4, tile=0.1)
    for zz in (lz - 0.11, lz + 0.02, lz + 0.13):
        P.torus(iron, (lx, ly, zz), 0.066, 0.0035, rot=(0, 0, 0),
                major_seg=16, minor_seg=4, tile=0.08)

    # ---- clamp work lamp pointing at the bench ------------------------------------
    ax, ay, az = -1.44, 2.80, 1.34
    P.tube(iron, [(ax, ay, az), (ax + 0.10, ay - 0.10, az + 0.16),
                  (ax + 0.26, ay - 0.02, az + 0.12)], 0.010, sides=6, tile=0.2)
    P.box(iron, (ax, ay, az), (0.07, 0.06, 0.08), bevel=0.005, tile=0.2)
    P.lathe(gs["olive"], [(0.020, 0.0), (0.075, 0.045), (0.105, 0.11)],
            center=(ax + 0.28, ay - 0.02, az + 0.10),
            rot=(radians(118), 0, radians(28)), segments=18, tile=0.4)
    P.sphere(gs["fluor"], (ax + 0.33, ay - 0.05, az - 0.01),
             (0.032, 0.032, 0.032), subdiv=2, tile=0.15)

    # ---- red emergency lamp above the steel door (left wall) ----------------------
    dx, dy, dz = -WALL_X + 0.06, 1.08, 2.30
    P.box(gs["iron_dark"], (dx, dy, dz), (0.06, 0.20, 0.16), bevel=0.004, tile=0.3)
    P.lathe(gs["red"], [(0.03, 0.0), (0.055, 0.02), (0.045, 0.055)],
            center=(dx + 0.04, dy, dz - 0.02), rot=(0, pi * 0.5, 0), segments=12, tile=0.2)
    P.sphere(gs["led_red"], (dx + 0.055, dy, dz - 0.02), (0.030, 0.030, 0.020),
             rot=(0, pi * 0.5, 0), subdiv=2, tile=0.1)
    P.box(gs["led_green"], (dx + 0.035, dy - 0.20, 1.62), (0.012, 0.030, 0.030), tile=0.1)


# ---------------------------------------------------------------------------------------
# boarded window and the dead city outside
# ---------------------------------------------------------------------------------------

def build_window(gs):
    x0, x1, z0, z1 = WINDOW
    cx = (x0 + x1) * 0.5
    conc = gs["concrete"]
    wood = gs["wood"]
    wood_d = gs["wood_dark"]
    iron = gs["iron"]

    # reveal lining
    for (px, sx) in ((x0 - 0.045, 0.09), (x1 + 0.045, 0.09)):
        P.box(conc, (px, BACK + 0.02, (z0 + z1) * 0.5), (sx, 0.24, z1 - z0 + 0.18),
              bevel=0.004, tile=0.8)
    P.box(conc, (cx, BACK + 0.02, z1 + 0.045), (x1 - x0 + 0.18, 0.24, 0.09),
          bevel=0.004, tile=0.8)
    # deep concrete sill
    P.box(conc, (cx, BACK - 0.10, z0 - 0.055), (x1 - x0 + 0.34, 0.44, 0.115),
          bevel=0.010, seg=2, tile=0.9)

    # the outside: dead block silhouettes under a cold night
    P.quad(gs["night"], [(x0 - 1.4, 4.30, z0 - 1.4), (x1 + 1.4, 4.30, z0 - 1.4),
                         (x1 + 1.4, 4.30, z1 + 1.2), (x0 - 1.4, 4.30, z1 + 1.2)],
           uv_rect=(0.02, 0.02, 0.98, 0.98))
    rng = random.Random(51)
    for i in range(9):
        bx = x0 - 1.2 + i * 0.33
        bh = rng.uniform(0.7, 2.6)
        bw = rng.uniform(0.20, 0.34)
        P.box(gs["black"], (bx, 4.20, z0 - 1.2 + bh * 0.5), (bw, 0.05, bh),
              bevel=0.006, tile=0.4)
        for k in range(3):
            if rng.random() < 0.45:
                P.box(gs["led_amber"], (bx + rng.uniform(-0.08, 0.08), 4.17,
                                        z0 - 1.2 + rng.uniform(0.1, bh - 0.1)),
                      (0.014, 0.01, 0.018), tile=0.05)
    P.sphere(gs["moon"], (x0 - 0.35, 4.24, z1 + 0.45), (0.055, 0.012, 0.055),
             subdiv=2, tile=0.2)

    # No glass shards: the old shards sat 5mm from the wall face and z-fought
    # (flickered). The window is now just boards + cold night behind them.

    # boards nailed over the opening. Gaps of 4-9 cm let the cold light through.
    boards = [
        (z0 + 0.14, 0.17, 8.0, 0.010),
        (z0 + 0.36, 0.20, -6.0, -0.014),
        (z0 + 0.58, 0.16, 12.0, 0.008),
        (z0 + 0.78, 0.19, -9.0, 0.015),
        (z0 + 0.99, 0.15, 6.0, -0.010),
    ]
    for (bz, bh, ang, dy) in boards:
        P.box(wood, (cx + rnd(-0.03, 0.03), BACK - 0.055 + dy, bz),
              (x1 - x0 + rnd(0.06, 0.22), 0.030, bh),
              rot=(0, radians(ang), radians(rnd(-1.0, 1.0))),
              bevel=0.006, seg=1, tile=0.9, grain="X")
        # nails
        for sx in (-1, 1):
            P.cylinder(gs["rust_dark"],
                       (cx + sx * (x1 - x0) * 0.40, BACK - 0.073 + dy, bz + sin(radians(ang)) * sx * 0.30),
                       0.007, 0.012, rot=(pi * 0.5, 0, 0), segments=6, tile=0.05)
    # one long diagonal brace, split near the middle
    P.box(wood_d, (x0 + 0.34, BACK - 0.085, (z0 + z1) * 0.5 + 0.10),
          (0.86, 0.032, 0.17), rot=(0, radians(-38), 0), bevel=0.005, tile=0.9, grain="X")
    P.box(wood_d, (x1 - 0.27, BACK - 0.090, (z0 + z1) * 0.5 - 0.10),
          (0.80, 0.032, 0.16), rot=(0, radians(-38), 0), bevel=0.005, tile=0.9, grain="X")
    # a vertical batten on the left edge
    P.box(wood, (x0 + 0.06, BACK - 0.070, (z0 + z1) * 0.5), (0.10, 0.028, z1 - z0 - 0.08),
          bevel=0.004, tile=0.8, grain="Z")


# ---------------------------------------------------------------------------------------
# steel blast door on the left wall
# ---------------------------------------------------------------------------------------

def build_door(gs):
    y0, y1 = DOOR_Y
    z1 = DOOR_Z
    steel = gs["steel_dark"]
    iron = gs["iron"]
    rust = gs["rust"]
    x = -WALL_X + 0.02

    # frame: heavy angle iron around the opening
    for (cy, sy) in ((y0 - 0.06, 0.12), (y1 + 0.06, 0.12)):
        P.box(steel, (x, cy, z1 * 0.5 + 0.06), (0.14, sy, z1 + 0.12), bevel=0.006, tile=0.5)
    P.box(steel, (x, (y0 + y1) * 0.5, z1 + 0.06), (0.14, y1 - y0 + 0.24, 0.12),
          bevel=0.006, tile=0.5)
    P.box(gs["concrete_dark"], (x - 0.04, (y0 + y1) * 0.5, 0.015), (0.24, y1 - y0, 0.03), tile=0.6)

    # the slab itself, set into the frame
    P.box(steel, (x + 0.055, (y0 + y1) * 0.5, z1 * 0.5), (0.10, y1 - y0 - 0.03, z1 - 0.03),
          bevel=0.006, seg=1, tile=0.9, grain="Z")
    # rust blooms and scraped paint
    for i in range(8):
        P.box(rust, (x + 0.110, (y0 + y1) * 0.5 + rnd(-0.28, 0.28), rnd(0.25, 1.85)),
              (0.003, rnd(0.05, 0.16), rnd(0.04, 0.14)),
              rot=(rnd(-0.2, 0.2), 0, rnd(-0.2, 0.2)), tile=0.4)
    # X brace
    for ang in (38.0, -38.0):
        P.box(steel, (x + 0.118, (y0 + y1) * 0.5, 1.02), (0.030, 0.10, 1.55),
              rot=(radians(ang), 0, 0), bevel=0.004, tile=0.7, grain="Z")
    # rivet grid
    for r in range(7):
        for c in range(4):
            P.sphere(gs["steel"], (x + 0.112, y0 + 0.10 + c * 0.26, 0.20 + r * 0.28),
                     (0.012, 0.012, 0.012), subdiv=1, tile=0.1)
    # wheel handle
    P.cylinder(iron, (x + 0.16, (y0 + y1) * 0.5, 1.18), 0.045, 0.07,
               rot=(0, pi * 0.5, 0), segments=12, tile=0.2)
    P.torus(gs["red"], (x + 0.20, (y0 + y1) * 0.5, 1.18), 0.155, 0.017,
            rot=(0, pi * 0.5, 0), major_seg=22, minor_seg=6, tile=0.2)
    for i in range(4):
        a = tau * i / 4.0 + 0.4
        P.box(gs["red"], (x + 0.20, (y0 + y1) * 0.5 + cos(a) * 0.076, 1.18 + sin(a) * 0.076),
              (0.020, 0.150, 0.020), rot=(a, 0, 0), tile=0.1)
    # hinges, latch bars, peephole, keypad
    for hz in (0.48, 1.06, 1.66):
        P.cylinder(iron, (x + 0.08, y0 + 0.015, hz), 0.030, 0.20,
                   rot=(0, 0, 0), segments=10, tile=0.2)
        P.box(iron, (x + 0.10, y0 + 0.02, hz), (0.07, 0.05, 0.16), bevel=0.004, tile=0.2)
    P.box(iron, (x + 0.11, y1 - 0.14, 1.78), (0.035, 0.34, 0.05), bevel=0.003, tile=0.2)
    P.box(iron, (x + 0.11, y1 - 0.14, 0.34), (0.035, 0.34, 0.05), bevel=0.003, tile=0.2)
    P.cylinder(gs["chrome"], (x + 0.115, (y0 + y1) * 0.5 + 0.10, 1.58), 0.022, 0.025,
               rot=(0, pi * 0.5, 0), segments=12, tile=0.1)
    P.disk(gs["soot"], (x + 0.118, (y0 + y1) * 0.5 + 0.10, 1.58), 0.014,
           rot=(0, pi * 0.5, 0), segments=10, tile=0.1)
    P.box(gs["olive_dark"], (x + 0.10, y1 + 0.19, 1.50), (0.07, 0.14, 0.22), bevel=0.004, tile=0.3)
    for r in range(3):
        for c in range(3):
            P.box(gs["black"], (x + 0.135, y1 + 0.15 + c * 0.030, 1.56 - r * 0.035),
                  (0.008, 0.020, 0.022), tile=0.05)
    P.box(gs["led_green"], (x + 0.138, y1 + 0.22, 1.62), (0.006, 0.016, 0.016), tile=0.05)

    # hazard band across the bottom of the door
    for i in range(7):
        P.box(gs["yellow"], (x + 0.113, y0 + 0.10 + i * 0.12, 0.14),
              (0.004, 0.075, 0.24), rot=(radians(35), 0, 0), tile=0.3)

    # padlocked chain across the frame
    Q.chain(gs, [(-WALL_X + 0.10, y0 - 0.02, 1.10), (-WALL_X + 0.12, (y0 + y1) * 0.5, 0.98),
                 (-WALL_X + 0.10, y1 + 0.02, 1.10)], link=0.030, scale=1.0)
    P.box(gs["brass"], (x + 0.12, (y0 + y1) * 0.5 + 0.02, 0.93), (0.05, 0.075, 0.09),
          bevel=0.006, tile=0.2)
    P.torus(gs["brass"], (x + 0.12, (y0 + y1) * 0.5 + 0.02, 1.00), 0.032, 0.006,
            rot=(0, pi * 0.5, 0), major_seg=10, minor_seg=4, tile=0.1)
