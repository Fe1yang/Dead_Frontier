"""Shell of the survival cabin: floorboards, plank walls, timber frame, window and fireplace.

All coordinates are metres in Blender space (X right, Y away from the lobby camera, Z up).
The lobby camera sits near y=-4.15 looking at the origin, so y=+3.34 is the back wall and
y=-2.4 is the closest visible floorboard. Only roughly x in [-1.8, 1.75] makes it into the
portrait frame, so every hero detail is packed into that band while the rest of the room
still exists for wide shots, light bounces and future camera moves.
"""

import math
import random
from math import pi, sin, cos, tau, radians

import cabin_prims as P
import cabin_props as Q

BACK = 3.34          # inner face of the back wall
WALL_X = 2.62        # inner face of the side walls
CEIL = 2.94
FLOOR_Y0 = -2.5
FLOOR_Y1 = BACK

WINDOW = (0.60, 1.52, 1.24, 2.24)   # x0, x1, z0, z1 of the opening
FIRE_X = -1.30                      # centre of the hearth
FIRE_HALF = 0.56

rv = random.uniform


def rnd(a, b):
    return random.uniform(a, b)


# ---------------------------------------------------------------------------------------
# floor
# ---------------------------------------------------------------------------------------

def build_floor(gs):
    wood = gs["floor"]
    dark = gs["floor"]
    # sub-floor: closes every gap and gives the planks a dark bed
    P.box(dark, (-0.02, 0.45, -0.055), (5.6, FLOOR_Y1 - FLOOR_Y0 + 0.2, 0.08),
          bevel=0.0, tile=2.0, grain="Y")

    x = -WALL_X - 0.02
    while x < WALL_X + 0.02:
        w = rnd(0.165, 0.225)
        x1 = min(x + w, WALL_X + 0.02)
        # stagger the butt joints from column to column
        y = FLOOR_Y0 + rnd(-0.55, 0.55)
        if y > FLOOR_Y0:
            y = FLOOR_Y0
        while y < FLOOR_Y1 + 0.02:
            length = rnd(1.0, 1.8)
            y1 = min(y + length, FLOOR_Y1 + 0.02)
            P.box(wood,
                  ((x + x1) * 0.5, (y + y1) * 0.5, -0.019),
                  (max(0.05, x1 - x - 0.006), max(0.05, y1 - y - 0.006), 0.038),
                  bevel=0.004, seg=1, tile=1.35, grain="Y")
            y = y1 + rnd(0.002, 0.006)
        x = x1 + rnd(0.001, 0.004)

    # a couple of nails along the most visible joins, just enough to read as hand-laid boards
    nail = gs["iron_dark"]
    for ny in (-1.9, -1.25, -0.6, 0.05, 0.7, 1.35, 2.0, 2.65):
        for nx in (-1.45, -0.72, 0.02, 0.76, 1.5):
            if rnd(0.0, 1.0) < 0.55:
                P.cylinder(nail, (nx + rnd(-0.02, 0.02), ny + rnd(-0.02, 0.02), 0.0015),
                           0.006, 0.006, rot=(0, 0, 0), segments=6, tile=0.05)


# ---------------------------------------------------------------------------------------
# walls
# ---------------------------------------------------------------------------------------

def _holes_for_column(x0, x1, holes):
    """Vertical spans still available to boards in this column."""
    spans = [(0.0, CEIL)]
    for (hx0, hx1, hz0, hz1) in holes:
        if x1 <= hx0 or x0 >= hx1:
            continue
        new = []
        for (z0, z1) in spans:
            if hz1 <= z0 or hz0 >= z1:
                new.append((z0, z1))
            else:
                if hz0 > z0:
                    new.append((z0, hz0))
                if hz1 < z1:
                    new.append((hz1, z1))
        spans = new
    return spans


def build_back_wall(gs, holes):
    wood = gs["wall"]
    x = -WALL_X
    while x < WALL_X:
        w = rnd(0.155, 0.215)
        x1 = min(x + w, WALL_X)
        for (z0, z1) in _holes_for_column(x, x1, holes):
            z = z0
            while z < z1 - 0.02:
                h = min(rnd(0.85, 1.5), z1 - z)
                inset = rnd(0.0, 0.010)
                P.box(wood,
                      ((x + x1) * 0.5, BACK - 0.020 - inset, z + h * 0.5),
                      (max(0.03, x1 - x - 0.006), 0.036, max(0.03, h - 0.006)),
                      bevel=0.004, seg=1, tile=1.2, grain="Z")
                z += h + 0.004
        x = x1 + 0.003

    # skirting board
    P.box(wood, (0.0, BACK - 0.05, 0.075), (WALL_X * 2.0, 0.075, 0.15),
          bevel=0.008, seg=1, tile=1.1, grain="X")

    # wall plate at the top and a mid rail above the window
    for z, h in ((CEIL - 0.10, 0.20), (2.55, 0.16)):
        P.box(wood, (0.0, BACK - 0.075, z), (WALL_X * 2.0 + 0.06, 0.15, h),
              bevel=0.010, seg=1, tile=1.4, grain="X")

    # structural posts, proud of the boards
    for px, pw in ((-2.55, 0.17), (-1.94, 0.15), (0.52, 0.13), (1.68, 0.14), (2.55, 0.17)):
        P.box(wood, (px, BACK - 0.095, CEIL * 0.5), (pw, 0.19, CEIL),
              bevel=0.010, seg=1, tile=1.3, grain="Z")

    # little iron pegs and strap plates at the joints
    iron = gs["iron_dark"]
    for px in (-2.55, -1.94, 0.52, 1.68, 2.55):
        for pz in (0.32, 1.42, 2.46):
            P.box(iron, (px, BACK - 0.195, pz), (0.20, 0.012, 0.045),
                  bevel=0.002, tile=0.2)
            P.cylinder(iron, (px, BACK - 0.205, pz), 0.012, 0.018,
                       rot=(pi * 0.5, 0, 0), segments=10, tile=0.05)

    # diagonal braces in the upper corners
    for sx in (-1.0, 1.0):
        P.box(wood, (sx * 2.16, BACK - 0.085, 2.33), (0.46, 0.13, 0.12),
              rot=(0, radians(38.0) * sx, 0), bevel=0.008, tile=1.0, grain="X")


def build_side_walls(gs):
    wood = gs["wall"]
    for sx in (-1.0, 1.0):
        x = sx * WALL_X
        y = FLOOR_Y0
        while y < BACK:
            w = rnd(0.16, 0.22)
            y1 = min(y + w, BACK)
            P.box(wood, (x + sx * 0.02, (y + y1) * 0.5, CEIL * 0.5),
                  (0.045, y1 - y - 0.005, CEIL),
                  bevel=0.004, seg=1, tile=1.2, grain="Z")
            y = y1 + 0.003
        # corner post
        P.box(wood, (x - sx * 0.05, BACK - 0.19, CEIL * 0.5),
              (0.18, 0.18, CEIL), bevel=0.010, tile=1.2, grain="Z")
        # a pair of exposed ceiling beams running into the wall
        for by in (-1.55, 0.35, 2.25):
            P.box(wood, (x - sx * 0.08, by, CEIL - 0.16),
                  (0.16, 0.14, 0.27), bevel=0.008, tile=1.2, grain="Y")


def build_ceiling(gs):
    wood = gs["wall"]
    P.box(wood, (0.0, (FLOOR_Y0 + BACK) * 0.5, CEIL + 0.02),
          (WALL_X * 2.0, BACK - FLOOR_Y0, 0.05), tile=1.6, grain="Y")
    for by in (-1.5, -0.25, 1.0, 2.2):
        P.box(wood, (0.0, by, CEIL - 0.10), (WALL_X * 2.0 + 0.1, 0.16, 0.22),
              bevel=0.010, seg=1, tile=1.4, grain="X")


def build_frame(gs):
    """Heavy exposed timber framing on the back wall, split around the window."""
    wood = gs["wall"]
    iron = gs["iron_dark"]
    for px in (-1.94, 0.52, 1.68):
        P.box(wood, (px, BACK - 0.185, 1.32), (0.10, 0.10, 2.50),
              bevel=0.008, seg=1, tile=1.0, grain="Z")
    P.box(wood, (0.0, BACK - 0.19, 2.55), (WALL_X * 2.0, 0.11, 0.16),
          bevel=0.008, seg=1, tile=1.2, grain="X")
    for sx in (-1, 1):
        P.box(wood, (sx * 2.20, BACK - 0.16, 2.60), (0.44, 0.13, 0.10),
              rot=(0, radians(42.0) * sx, 0), bevel=0.007, tile=1.0, grain="X")
    for px in (-1.94, 0.52, 1.68):
        for pz in (0.30, 2.47):
            P.box(iron, (px, BACK - 0.245, pz), (0.16, 0.014, 0.06),
                  bevel=0.002, tile=0.2)


# ---------------------------------------------------------------------------------------
# window and the winter night outside
# ---------------------------------------------------------------------------------------

def build_window(gs):
    x0, x1, z0, z1 = WINDOW
    cx = (x0 + x1) * 0.5
    wood = gs["wall"]
    iron = gs["iron_dark"]
    glass = gs["glass"]
    night = gs["night"]
    snow = gs["snow"]
    bark = gs["bark"]

    # reveal / jamb lining set into the wall thickness. The casing is deliberately wide:
    # the plank wall stops on whole boards, so the trim has to cover the ragged opening edge.
    P.box(wood, (x0 - 0.15, BACK - 0.10, (z0 + z1) * 0.5), (0.30, 0.32, z1 - z0 + 0.18),
          bevel=0.008, tile=1.0, grain="Z")
    P.box(wood, (x1 + 0.15, BACK - 0.10, (z0 + z1) * 0.5), (0.30, 0.32, z1 - z0 + 0.18),
          bevel=0.008, tile=1.0, grain="Z")
    P.box(wood, (cx, BACK - 0.10, z1 + 0.11), (x1 - x0 + 0.60, 0.32, 0.22),
          bevel=0.008, tile=1.0, grain="X")
    # deep sill, worn smooth at the front edge
    P.box(wood, (cx, BACK - 0.19, z0 - 0.05), (x1 - x0 + 0.34, 0.44, 0.10),
          bevel=0.014, seg=2, tile=1.1, grain="X")
    P.box(wood, (cx, BACK - 0.40, z0 - 0.105), (x1 - x0 + 0.30, 0.06, 0.05),
          bevel=0.006, tile=1.0, grain="X")

    # outer casing, a little proud of the boards
    for zz, hh in ((z0 - 0.01, 0.10), (z1 + 0.01, 0.10)):
        P.box(wood, (cx, BACK - 0.035, zz), (x1 - x0 + 0.30, 0.06, hh),
              bevel=0.008, seg=1, tile=1.0, grain="X")
    for xx in (x0 - 0.01, x1 + 0.01):
        P.box(wood, (xx, BACK - 0.035, (z0 + z1) * 0.5), (0.10, 0.06, z1 - z0 + 0.20),
              bevel=0.008, seg=1, tile=1.0, grain="Z")

    # muntins and panes
    P.box(wood, (cx, BACK - 0.045, (z0 + z1) * 0.5), (0.035, 0.05, z1 - z0),
          bevel=0.004, seg=1, tile=1.0, grain="Z")
    P.box(wood, (cx, BACK - 0.045, (z0 + z1) * 0.5), (x1 - x0, 0.05, 0.032),
          bevel=0.004, seg=1, tile=1.0, grain="X")
    for gx in (x0 + (x1 - x0) * 0.25, x0 + (x1 - x0) * 0.75):
        P.box(glass, (gx, BACK - 0.015, (z0 + z1) * 0.5), ((x1 - x0) * 0.5 - 0.025, 0.012, z1 - z0 - 0.03),
              bevel=0.0, tile=0.5)
    # frost creeping up the bottom corners (small emissive-white shards)
    for i in range(7):
        fx = rnd(x0 + 0.03, x1 - 0.03)
        fz = z0 + rnd(0.0, 0.10)
        P.sphere(gs["paper"], (fx, BACK - 0.008, fz),
                 (rnd(0.018, 0.045), 0.002, rnd(0.012, 0.035)), subdiv=1, tile=0.2)

    # the winter night hangs a metre and a half beyond the glass
    ny = 4.85
    P.quad(night, [(x0 - 0.9, ny, z0 - 0.8), (x1 + 0.9, ny, z0 - 0.8),
                   (x1 + 0.9, ny, z1 + 0.9), (x0 - 0.9, ny, z1 + 0.9)],
           uv_rect=(0.02, 0.03, 0.98, 0.98))
    # moon glow through the pane
    P.sphere(gs["moon"], (x0 + 0.30, ny - 0.05, z1 - 0.18),
             (0.055, 0.012, 0.055), subdiv=2, tile=0.2)

    # snow bank and pines
    P.box(snow, (cx, 4.15, 0.82), (3.4, 1.5, 0.10), bevel=0.03, seg=1, tile=1.0)
    P.box(snow, (cx, 4.0, 0.87), (3.3, 0.6, 0.14), bevel=0.05, seg=2, tile=0.9)
    for i, (px, py, ph, pr) in enumerate((
            (0.15, 4.35, 2.55, 0.62), (0.65, 4.55, 3.05, 0.70),
            (1.15, 4.30, 2.35, 0.58), (1.62, 4.60, 2.85, 0.66),
            (1.95, 4.28, 2.10, 0.50), (-0.20, 4.52, 2.70, 0.60))):
        Q.pine(gs, (px, py, 0.86), height=ph, radius=pr, seed=90 + i)

    # iron curtain rod with wool curtains tied back at each side
    rod_z = z1 + 0.15
    P.cylinder(iron, (cx, BACK - 0.36, rod_z), 0.014, x1 - x0 + 0.62,
               rot=(0, pi * 0.5, 0), segments=12, tile=0.3)
    for ex in (x0 - 0.32, x1 + 0.32):
        P.sphere(iron, (ex, BACK - 0.36, rod_z), (0.030, 0.030, 0.030), subdiv=2, tile=0.2)
    for sx, xa in ((-1.0, x0 - 0.02), (1.0, x1 + 0.02)):
        P.torus(iron, (xa, BACK - 0.36, rod_z), 0.035, 0.007,
                rot=(0, pi * 0.5, 0), major_seg=16, minor_seg=6, tile=0.15)
        _curtain(gs, xa - sx * 0.10, z0 - 0.10, sx)

    # things on the sill: two jars, a candle stub and a little drift of snow
    Q.jar(gs, (x0 + 0.14, BACK - 0.21, z0 + 0.005), radius=0.042, height=0.10, fill="paper_old")
    Q.jar(gs, (x0 + 0.25, BACK - 0.21, z0 + 0.005), radius=0.033, height=0.075, fill="label_green")
    Q.can(gs, (x1 - 0.16, BACK - 0.21, z0 + 0.058), radius=0.032, height=0.082, label="label_cream")
    P.cylinder(gs["wax"], (x1 - 0.30, BACK - 0.21, z0 + 0.035), 0.018, 0.07,
               segments=12, tile=0.1)
    P.sphere(gs["flame"], (x1 - 0.30, BACK - 0.21, z0 + 0.082),
             (0.010, 0.010, 0.022), subdiv=1, tile=0.1)
    P.sphere(snow, (x1 - 0.55, BACK - 0.19, z0 + 0.006), (0.16, 0.10, 0.025), subdiv=2, tile=0.4)


def _curtain(gs, xa, z_bottom, side):
    width = 0.24
    top = WINDOW[3] + 0.13
    height = top - z_bottom
    origin = (xa - width * 0.5, BACK - 0.40, top)
    if side < 0:
        origin = (xa - width * 0.5, BACK - 0.40, top)

    def folds(u, v):
        return (0.012 + 0.055 * (v ** 1.5)) * (
            0.55 + 0.45 * sin(u * 13.0 + v * 1.5)) + 0.006 * sin(v * 22.0)

    P.cloth(gs["wool"], origin, (width, 0, 0), (0, 0, -height), (0, -1, 0),
            14, 20, 0.008, folds, uv_rect=(0.05, 0.05, 0.45, 1.0))
    # rope tie-back pinching the middle
    mid_z = z_bottom + height * 0.48
    pts = []
    for i in range(9):
        a = -pi * 0.5 + pi * i / 8.0
        pts.append((xa - 0.05 + 0.035 * sin(a) * side, BACK - 0.46 + 0.06 * cos(a), mid_z))
    P.tube(gs["rope"], pts, 0.009, sides=5, tile=0.2)


# ---------------------------------------------------------------------------------------
# fireplace
# ---------------------------------------------------------------------------------------

def _stones(g, x0, x1, z0, z1, depth=(0.12, 0.30), tile=0.55):
    z = z0
    course = 0
    while z < z1 - 0.02:
        h = min(rnd(0.125, 0.215), z1 - z)
        xx = x0
        while xx < x1 - 0.02:
            w = min(rnd(0.14, 0.30), x1 - xx)
            if x1 - xx - w < 0.11:
                w = x1 - xx
            d = rnd(depth[0], depth[1])
            P.box(g, (xx + w * 0.5 + rnd(-0.008, 0.008),
                      BACK - d * 0.5,
                      z + h * 0.5 + rnd(-0.008, 0.008)),
                  (max(0.04, w - 0.012), d, max(0.04, h - 0.012)),
                  rot=(rnd(-0.02, 0.02), rnd(-0.02, 0.02), rnd(-0.025, 0.025)),
                  bevel=0.009, seg=1, tile=tile, grain="X", jitter=0.002)
            xx += w
        z += h
    return


def build_fireplace(gs):
    stone = gs["stone"]
    soot = gs["char"]
    iron = gs["iron_dark"]
    wood = gs["wall"]
    bark = gs["bark"]
    ember = gs["ember"]
    flame = gs["flame"]
    hearth_z0, hearth_z1 = 0.0, 1.10
    x0, x1 = FIRE_X - FIRE_HALF, FIRE_X + FIRE_HALF

    # hearth slab and builder's course
    P.box(stone, (FIRE_X, BACK - 0.30, 0.035), (FIRE_HALF * 2.0 + 0.26, 0.62, 0.07),
          bevel=0.010, seg=1, tile=0.7, grain="X")
    _stones(stone, x0 - 0.12, x1 + 0.12, 0.07, 0.22, depth=(0.22, 0.36), tile=0.6)

    # side piers around the firebox
    _stones(stone, x0 - 0.12, x0 + 0.02, 0.22, hearth_z1, depth=(0.18, 0.34))
    _stones(stone, x1 - 0.02, x1 + 0.12, 0.22, hearth_z1, depth=(0.18, 0.34))
    # lintel and chimney breast
    _stones(stone, x0 - 0.12, x1 + 0.12, hearth_z1, hearth_z1 + 0.18, depth=(0.20, 0.36))
    _stones(stone, x0 - 0.04, x1 + 0.04, hearth_z1 + 0.18, 2.40, depth=(0.14, 0.26))

    # blackened firebox
    P.box(soot, (FIRE_X, BACK - 0.015, 0.66), (FIRE_HALF * 2.0 - 0.16, 0.05, 0.98),
          tile=0.6)
    P.box(stone, (x0 + 0.04, BACK - 0.11, 0.66), (0.10, 0.22, 0.88),
          bevel=0.008, tile=0.6, grain="Z")
    P.box(stone, (x1 - 0.04, BACK - 0.11, 0.66), (0.10, 0.22, 0.88),
          bevel=0.008, tile=0.6, grain="Z")
    P.box(soot, (FIRE_X, BACK - 0.12, 0.215), (FIRE_HALF * 2.0 - 0.18, 0.30, 0.07),
          bevel=0.01, tile=0.6)

    # iron grate
    for i in range(5):
        gy = BACK - 0.32 + i * 0.06
        P.cylinder(iron, (FIRE_X, gy, 0.17), 0.008, 0.80,
                   rot=(0, pi * 0.5, 0), segments=8, tile=0.1)
    for gx in (FIRE_X - 0.34, FIRE_X + 0.34):
        P.cylinder(iron, (gx, BACK - 0.24, 0.12), 0.010, 0.28,
                   rot=(pi * 0.5, 0, 0), segments=8, tile=0.1)

    # logs: a crossed pair plus two smaller ones
    logs = [(-1.30, 3.08, 0.205, 0.50, 0.052, 0.22),
            (-1.33, 3.17, 0.255, 0.46, 0.048, -0.18),
            (-1.36, 2.99, 0.145, 0.42, 0.042, 0.55),
            (-1.22, 3.20, 0.155, 0.38, 0.036, -0.45)]
    for (lx, ly, lz, ll, lr, ang) in logs:
        P.cylinder(bark, (lx, ly, lz), lr, ll, rot=(0, pi * 0.5, ang),
                   segments=14, tile=0.35)
        for ex in (-1.0, 1.0):
            P.disk(gs["endgrain"],
                   (lx + cos(ang) * ll * 0.5 * ex,
                    ly + sin(ang) * ll * 0.5 * ex, lz),
                   lr * 0.90, rot=(0, pi * 0.5 * ex, ang), segments=14, tile=0.3)

    # ember bed
    rng = random.Random(77)
    for i in range(26):
        ex = FIRE_X + rng.uniform(-0.38, 0.38)
        ey = BACK - 0.40 + rng.uniform(-0.14, 0.20)
        ez = 0.11 + rng.uniform(0.0, 0.055)
        r = rng.uniform(0.014, 0.038)
        P.sphere(ember, (ex, ey, ez), (r, r * 0.8, r * 0.6),
                 rot=(0, 0, rng.uniform(0, tau)), subdiv=1, tile=0.15)

    # flame tongues of different heights, all leaning slightly
    fire = [(-0.24, 0.00, 0.00, 1.00), (-0.12, 0.02, -0.03, 0.78),
            (0.00, -0.02, 0.01, 1.20), (0.11, 0.02, 0.02, 0.86),
            (0.22, -0.01, -0.02, 0.66), (-0.18, 0.07, 0.03, 0.55),
            (0.05, 0.09, -0.04, 0.60), (0.16, 0.06, 0.05, 0.48)]
    for (fx, fy, fz, fs) in fire:
        prof = [(0.0, 0.0), (0.075 * fs, 0.008), (0.070 * fs, 0.075 * fs),
                (0.050 * fs, 0.16 * fs), (0.028 * fs, 0.245 * fs),
                (0.0, 0.34 * fs)]
        P.lathe(flame, prof,
                center=(FIRE_X + fx, BACK - 0.34 + fy, 0.18 + fz),
                segments=14, rot=(radians(rnd(-7, 7)), radians(rnd(-7, 7)), rnd(0, tau)),
                tile=0.3)

    # mantel beam
    P.box(wood, (FIRE_X, BACK - 0.26, 1.385), (FIRE_HALF * 2.0 + 0.28, 0.38, 0.14),
          bevel=0.014, seg=2, tile=1.2, grain="X")
    for sx in (-1, 1):
        P.box(iron, (FIRE_X + sx * (FIRE_HALF + 0.08), BACK - 0.26, 1.30),
              (0.10, 0.30, 0.05), bevel=0.003, tile=0.2)

    # tools
    _poker(gs, -0.83, 2.99, 0.0)
    _shovel(gs, -1.80, 2.99, radians(12))
    # firewood stacked beside the hearth, ends toward the room
    _log_stack(gs, -2.28, 2.90, 0.0, rows=4, cols=3)

    # mantel clutter
    Q.lantern(gs, (FIRE_X - 0.30, BACK - 0.30, 1.455), scale=0.62, lit=True, hanging=False)
    Q.can(gs, (FIRE_X - 0.04, BACK - 0.40, 1.492), radius=0.031, height=0.082, label="label_green")
    Q.can(gs, (FIRE_X + 0.08, BACK - 0.35, 1.492), radius=0.029, height=0.075, label="label_red")
    Q.bottle(gs, (FIRE_X + 0.24, BACK - 0.38, 1.455), radius=0.032, height=0.17, glass="glass_amber")
    Q.book(gs, (FIRE_X + 0.40, BACK - 0.34, 1.47), size=(0.13, 0.18, 0.04),
           rot=(0, 0, radians(-6)), cover="leather")
    P.cylinder(gs["wax"], (FIRE_X + 0.48, BACK - 0.30, 1.49), 0.020, 0.09,
               segments=10, tile=0.1)
    Q.antlers(gs, (FIRE_X, BACK - 0.15, 1.92), rot=(0, 0, 0), scale=0.86)


def _poker(gs, x, y, ang):
    iron = gs["iron_dark"]
    P.tube(iron, [(x, y, 0.02), (x + 0.02, y - 0.02, 0.5), (x + 0.01, y - 0.05, 0.95),
                  (x - 0.04, y - 0.06, 1.06), (x - 0.08, y - 0.05, 1.02)],
           0.009, sides=6, tile=0.2)
    P.torus(iron, (x - 0.08, y - 0.05, 1.02), 0.028, 0.008,
            rot=(pi * 0.5, 0, 0), major_seg=12, minor_seg=5, tile=0.1)


def _shovel(gs, x, y, ang):
    iron = gs["iron_dark"]
    wood = gs["wall"]
    P.cylinder(wood, (x, y, 0.62), 0.014, 1.16, rot=(0, 0, ang), segments=10, tile=0.4)
    P.box(iron, (x + sin(ang) * -0.10, y - 0.03, 0.08), (0.19, 0.03, 0.22),
          rot=(0, 0, ang), bevel=0.008, tile=0.3)
    P.box(wood, (x, y, 1.18), (0.05, 0.035, 0.04), rot=(0, 0, ang), bevel=0.005, tile=0.3)


def _log_stack(gs, x, y, z0, rows=4, cols=3):
    bark = gs["bark"]
    end = gs["endgrain"]
    for row in range(rows):
        for col in range(cols):
            lx = x + col * 0.115 + (0.055 if row % 2 else 0.0)
            ly = y + rnd(-0.03, 0.03)
            lz = z0 + 0.065 + row * 0.105
            length = rnd(0.52, 0.62)
            radius = rnd(0.048, 0.058)
            P.cylinder(bark, (lx, ly + length * 0.5, lz), radius, length,
                       rot=(pi * 0.5, 0, 0), segments=12, tile=0.35)
            P.disk(end, (lx, ly + length + 0.001, lz), radius * 0.92,
                   rot=(pi * 0.5, 0, 0), segments=12, tile=0.3)


def build_cobwebs(gs):
    cord = gs["cord"]
    Q.cobweb(gs, (-2.55, BACK - 0.10, 2.86), (-2.55, BACK - 0.10, 2.20),
             (-1.75, BACK - 0.10, 2.86), n=7, rings=3, seed=4)
    Q.cobweb(gs, (1.62, BACK - 0.10, 2.40), (1.62, BACK - 0.10, 1.80),
             (1.05, BACK - 0.10, 2.40), n=6, rings=2, seed=9)
    Q.cobweb(gs, (2.55, BACK - 0.10, 2.80), (2.55, BACK - 0.10, 2.10),
             (1.85, BACK - 0.10, 2.80), n=6, rings=2, seed=12)
