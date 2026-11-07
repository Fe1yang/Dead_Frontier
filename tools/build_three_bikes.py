"""Build three genuinely different motorcycles for Dead Frontier.

1. SCRAMBLER - army-green apocalypse scrambler with cargo box and knobby tires.
2. SPORT     - crimson full-fairing sport bike with gold forks and twin lamps.
3. CRUISER   - ivory V-twin cruiser with ape hangers, saddlebags and whitewalls.

Each bike is exported as its own GLB under assets/models/vehicles/ and a studio
line-up plus three close-ups are rendered into renders/.

Run:
  blender.exe --background --python tools/build_three_bikes.py
"""

import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

SKIP_RENDERS = "--no-render" in sys.argv

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets" / "models" / "vehicles"
RENDER_DIR = ROOT / "renders"
OUT_DIR.mkdir(parents=True, exist_ok=True)
RENDER_DIR.mkdir(parents=True, exist_ok=True)

TAU = math.tau

# ---------------------------------------------------------------------------
# scene reset
# ---------------------------------------------------------------------------
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for data in (bpy.data.meshes, bpy.data.materials, bpy.data.curves,
             bpy.data.lights, bpy.data.cameras):
    for block in list(data):
        if block.users == 0:
            data.remove(block)


# ---------------------------------------------------------------------------
# materials
# ---------------------------------------------------------------------------
def make_mat(name, color, rough=0.55, metal=0.0, coat=0.0,
             emit=None, emit_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")

    def put(keys, value):
        for key in keys:
            if key in bsdf.inputs:
                bsdf.inputs[key].default_value = value
                return

    put(["Base Color"], (*color, 1.0))
    put(["Roughness"], rough)
    put(["Metallic"], metal)
    if coat:
        put(["Coat Weight", "Clearcoat"], coat)
    if emit:
        put(["Emission Color", "Emission"], (*emit, 1.0))
        put(["Emission Strength"], emit_strength)
    return mat


TIRE = make_mat("rubber tire", (0.022, 0.022, 0.024), rough=0.94)
RUBBER = make_mat("rubber grip", (0.035, 0.032, 0.030), rough=0.88)
BLACK = make_mat("black steel", (0.028, 0.030, 0.033), rough=0.52, metal=0.45)
STEEL = make_mat("gun steel", (0.10, 0.11, 0.12), rough=0.42, metal=0.85)
DARK_STEEL = make_mat("dark steel", (0.055, 0.060, 0.065), rough=0.5, metal=0.7)
CHROME = make_mat("chrome", (0.78, 0.80, 0.83), rough=0.14, metal=1.0)
ALU = make_mat("aluminium", (0.46, 0.48, 0.50), rough=0.34, metal=1.0)
GOLD = make_mat("anodised gold", (0.66, 0.47, 0.15), rough=0.26, metal=1.0)
RUST = make_mat("rusty exhaust", (0.30, 0.15, 0.075), rough=0.82, metal=0.2)

OLIVE = make_mat("olive drab", (0.205, 0.240, 0.135), rough=0.52, metal=0.2, coat=0.45)
OLIVE_DARK = make_mat("olive dark", (0.125, 0.155, 0.095), rough=0.68, metal=0.15)
CREAM = make_mat("ivory paint", (0.78, 0.72, 0.57), rough=0.34, metal=0.25, coat=0.7)
CRIMSON = make_mat("crimson paint", (0.43, 0.025, 0.035), rough=0.22, metal=0.45, coat=1.0)
CARBON = make_mat("carbon black", (0.020, 0.021, 0.023), rough=0.30, metal=0.35, coat=0.6)
LEATHER = make_mat("black leather", (0.055, 0.042, 0.032), rough=0.86)
LEATHER_BROWN = make_mat("brown leather", (0.19, 0.105, 0.055), rough=0.78)
SMOKE = make_mat("smoked screen", (0.020, 0.026, 0.032), rough=0.10, metal=0.5)
LAMP_WARM = make_mat("headlight warm", (1.0, 0.86, 0.60), rough=0.2,
                     emit=(1.0, 0.86, 0.62), emit_strength=7.0)
LAMP_COOL = make_mat("headlight cool", (0.78, 0.88, 1.0), rough=0.2,
                     emit=(0.78, 0.90, 1.0), emit_strength=8.0)
TAIL_RED = make_mat("tail light", (0.7, 0.03, 0.02), rough=0.3,
                    emit=(1.0, 0.06, 0.03), emit_strength=5.0)
FLOOR = make_mat("studio floor", (0.017, 0.019, 0.022), rough=0.36, metal=0.25)
BACKDROP = make_mat("studio backdrop", (0.026, 0.030, 0.036), rough=0.7, metal=0.1)


# ---------------------------------------------------------------------------
# primitive helpers
# ---------------------------------------------------------------------------
def _finish(obj, mat, smooth=False, bevel=0.0):
    if mat is not None:
        obj.data.materials.append(mat)
    if bevel > 0.0:
        mod = obj.modifiers.new("edge bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = "ANGLE"
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.modifier_apply(modifier=mod.name)
    if smooth:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        try:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(38))
        except Exception:
            bpy.ops.object.shade_smooth()
    return obj


def cube(name, loc, dims, mat, rot=(0, 0, 0), bevel=0.012, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.scale = dims
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    _finish(obj, mat, bevel=bevel)
    if parent:
        obj.parent = parent
    return obj


def cyl(name, loc, radius, depth, mat, rot=(0, 0, 0), verts=24,
        parent=None, smooth=True, bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth,
                                        vertices=verts, location=loc,
                                        rotation=rot)
    obj = bpy.context.object
    obj.name = name
    _finish(obj, mat, smooth=smooth, bevel=bevel)
    if parent:
        obj.parent = parent
    return obj


def rod(name, start, end, radius, mat, verts=16, parent=None, smooth=True):
    a, b = Vector(start), Vector(end)
    delta = b - a
    if delta.length < 1e-6:
        delta = Vector((0, 0, 1e-3))
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=delta.length,
                                        vertices=verts,
                                        location=(a + b) * 0.5)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = delta.to_track_quat("Z", "Y").to_euler()
    _finish(obj, mat, smooth=smooth)
    if parent:
        obj.parent = parent
    return obj


def ball(name, loc, size, mat, parent=None, seg=24, rings=14, smooth=True):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings,
                                         radius=0.5, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = size
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    _finish(obj, mat, smooth=smooth)
    if parent:
        obj.parent = parent
    return obj


def torus(name, loc, major, minor, mat, rot=(0, 0, 0),
          parent=None, seg=28, rseg=10, smooth=True):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=seg, minor_segments=rseg,
                                     location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    _finish(obj, mat, smooth=smooth)
    if parent:
        obj.parent = parent
    return obj


def finned(name, start, end, radius, count, body_mat, fin_mat,
           parent=None):
    """V-twin style air-cooled cylinder with cooling fins."""
    a, b = Vector(start), Vector(end)
    delta = b - a
    rod(name + "_body", a, b, radius, body_mat, verts=20, parent=parent)
    quat = delta.to_track_quat("Z", "Y")
    for i in range(count):
        p = a + delta * ((i + 0.6) / count)
        bpy.ops.mesh.primitive_cylinder_add(radius=radius * 1.16,
                                            depth=0.011, vertices=20,
                                            location=p)
        fin = bpy.context.object
        fin.name = "%s_fin%d" % (name, i)
        fin.rotation_euler = quat.to_euler()
        _finish(fin, fin_mat, smooth=False)
        if parent:
            fin.parent = parent
    head = ball(name + "_head", b, (radius * 2.3, radius * 2.1, radius * 2.2),
                body_mat, parent=parent, seg=16, rings=10)
    return head


# ---------------------------------------------------------------------------
# wheels
# ---------------------------------------------------------------------------
def add_wheel(root, name, z, radius=0.34, width=0.085, style="spoke",
              knobby=False, tire_mat=TIRE, rim_mat=ALU, whitewall=False,
              disc=True):
    center = Vector((0.0, radius, z))
    parts = []
    # tire: for knobby wheels the carcass sits inside so the knobs define
    # the outer radius and the bike still touches the ground at y=0.
    carcass = radius - (0.030 if knobby else 0.0)
    parts.append(torus(name + "_tire", center, carcass - width, width, tire_mat,
                       rot=(0, math.pi / 2, 0), parent=root, seg=32, rseg=12))
    if style == "solid":
        parts.append(cyl(name + "_disc", center, radius * 0.60, width * 1.35,
                         rim_mat, rot=(0, math.pi / 2, 0), verts=32,
                         parent=root))
    else:
        parts.append(torus(name + "_rim", center, radius * 0.52, 0.022,
                           rim_mat, rot=(0, math.pi / 2, 0), parent=root,
                           seg=28, rseg=8))
        for i in range(5):
            angle = i * TAU / 5.0
            tip = Vector((0.0,
                          radius + math.cos(angle) * radius * 0.50,
                          z + math.sin(angle) * radius * 0.50))
            parts.append(rod("%s_spoke%d" % (name, i), center, tip, 0.011,
                             rim_mat, verts=8, parent=root))
    parts.append(cyl(name + "_hub", center, 0.056, width * 1.9, DARK_STEEL,
                     rot=(0, math.pi / 2, 0), verts=20, parent=root))
    parts.append(cyl(name + "_axle", center, 0.020, width * 2.6, CHROME,
                     rot=(0, math.pi / 2, 0), verts=12, parent=root))
    if disc:
        offset = width * 1.55
        parts.append(cyl(name + "_brake", (offset, radius, z),
                         radius * 0.56, 0.007, DARK_STEEL,
                         rot=(0, math.pi / 2, 0), verts=32, parent=root))
    if whitewall:
        for side in (-1.0, 1.0):
            parts.append(torus(name + "_wall%d" % int(side),
                               (side * width * 0.92, radius, z),
                               radius * 0.62, 0.013, CREAM,
                               rot=(0, math.pi / 2, 0), parent=root,
                               seg=24, rseg=6))
    if knobby:
        knob_ring = radius - 0.026
        for i in range(22):
            angle = i * TAU / 22.0
            knob = Vector((0.0,
                           radius + math.cos(angle) * knob_ring,
                           z + math.sin(angle) * knob_ring))
            parts.append(cube("%s_knob%d" % (name, i), knob,
                              (width * 1.5, 0.052, 0.062), tire_mat,
                              rot=(angle, 0, 0), bevel=0.008, parent=root))

    # Pivot at the axle so the game can spin the wheel by rotating this node.
    pivot_name = "WheelFrontPivot" if name.endswith("front") else "WheelRearPivot"
    pivot = bpy.data.objects.new(pivot_name, None)
    pivot.empty_display_type = "PLAIN_AXES"
    pivot.empty_display_size = 0.22
    pivot.location = center
    bpy.context.scene.collection.objects.link(pivot)
    pivot.parent = root
    for part in parts:
        part.parent = pivot
        part.matrix_parent_inverse = Matrix.Translation(-center)
    return pivot


def new_root(name):
    root = bpy.data.objects.new(name, None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.4
    bpy.context.scene.collection.objects.link(root)
    return root


# ---------------------------------------------------------------------------
# 1. SCRAMBLER
# ---------------------------------------------------------------------------
def build_scrambler():
    root = new_root("SCRAMBLER")
    add_wheel(root, "sc_front", -0.62, 0.34, 0.085, knobby=True,
              tire_mat=TIRE, rim_mat=DARK_STEEL)
    add_wheel(root, "sc_rear", 0.62, 0.34, 0.090, knobby=True,
              tire_mat=TIRE, rim_mat=DARK_STEEL)

    # frame
    rod("sc_backbone", (0, 0.88, -0.38), (0, 0.68, 0.24), 0.036, STEEL, parent=root)
    rod("sc_down", (0, 0.92, -0.42), (0, 0.40, 0.00), 0.036, STEEL, parent=root)
    for sx in (-0.07, 0.07):
        rod("sc_rail", (sx, 0.68, 0.24), (sx, 0.78, 0.60), 0.021, STEEL, parent=root)
        rod("sc_stay", (sx, 0.34, 0.62), (sx, 0.70, 0.28), 0.019, STEEL, parent=root)
        rod("sc_swing", (sx, 0.46, 0.24), (sx, 0.34, 0.62), 0.026, STEEL, parent=root)

    # forks and steering
    for sx in (-0.09, 0.09):
        rod("sc_fork", (sx, 0.34, -0.62), (sx, 0.96, -0.44), 0.028, CHROME, parent=root)
        rod("sc_fork_low", (sx, 0.34, -0.62), (sx, 0.66, -0.56), 0.036, DARK_STEEL, parent=root)
    cube("sc_clamp_top", (0, 0.94, -0.43), (0.27, 0.05, 0.10), STEEL, bevel=0.01, parent=root)
    cube("sc_clamp_low", (0, 0.80, -0.47), (0.27, 0.05, 0.10), STEEL, bevel=0.01, parent=root)
    rod("sc_bar", (-0.33, 1.02, -0.44), (0.33, 1.02, -0.44), 0.020, STEEL, parent=root)
    for sx in (-0.31, 0.31):
        rod("sc_grip", (sx, 1.02, -0.44), (sx, 1.02, -0.36), 0.030, RUBBER, parent=root)
        rod("sc_guard", (sx, 1.02, -0.36), (sx, 1.09, -0.36), 0.012, STEEL, parent=root)

    # headlight + flyscreen
    cyl("sc_lamp_can", (0, 0.88, -0.555), 0.098, 0.11, STEEL,
        rot=(math.pi / 2, 0, 0), verts=24, parent=root)
    torus("sc_lamp_ring", (0, 0.88, -0.608), 0.088, 0.012, CHROME,
          parent=root, seg=24, rseg=8)
    cyl("sc_lamp_lens", (0, 0.88, -0.615), 0.078, 0.012, LAMP_WARM,
        rot=(math.pi / 2, 0, 0), verts=24, parent=root)
    cube("sc_screen", (0, 1.03, -0.50), (0.30, 0.18, 0.012), SMOKE,
         rot=(0.38, 0, 0), bevel=0.006, parent=root)

    # tank + seat
    ball("sc_tank", (0, 0.78, -0.12), (0.30, 0.24, 0.52), OLIVE, parent=root)
    for sx in (-0.152, 0.152):
        cube("sc_tank_stripe", (sx, 0.79, -0.12), (0.012, 0.095, 0.34),
             CREAM, bevel=0.004, parent=root)
    cyl("sc_cap", (0, 0.905, -0.14), 0.036, 0.016, CHROME, verts=16, parent=root)
    cube("sc_seat", (0, 0.79, 0.28), (0.26, 0.075, 0.46), LEATHER,
         bevel=0.02, parent=root)
    cube("sc_seat_hump", (0, 0.835, 0.52), (0.26, 0.10, 0.11), LEATHER,
         bevel=0.02, parent=root)

    # rear rack + cargo box
    cube("sc_rack", (0, 0.83, 0.63), (0.31, 0.025, 0.29), STEEL,
         bevel=0.008, parent=root)
    cube("sc_cargo", (0, 0.95, 0.64), (0.30, 0.24, 0.32), OLIVE_DARK,
         bevel=0.02, parent=root)
    for zz in (0.55, 0.73):
        cube("sc_strap", (0, 1.01, zz), (0.31, 0.025, 0.030), LEATHER_BROWN,
             bevel=0.004, parent=root)
        cube("sc_buckle", (0.158, 1.01, zz), (0.012, 0.035, 0.045), CHROME,
             bevel=0.003, parent=root)
    cube("sc_tail", (0, 0.84, 0.795), (0.10, 0.045, 0.03), TAIL_RED,
         bevel=0.006, parent=root)

    # fenders
    ball("sc_fender_front", (0, 0.70, -0.64), (0.12, 0.055, 0.34), OLIVE, parent=root)
    ball("sc_fender_rear", (0, 0.70, 0.65), (0.14, 0.050, 0.38), OLIVE, parent=root)

    # engine
    cube("sc_engine", (0, 0.42, 0.00), (0.29, 0.30, 0.40), DARK_STEEL,
         bevel=0.02, parent=root)
    for i, yy in enumerate((0.33, 0.37, 0.41, 0.45)):
        cyl("sc_fin%d" % i, (0, yy, 0.00), 0.165, 0.014, DARK_STEEL,
            verts=20, parent=root)
    cube("sc_head", (0, 0.52, 0.01), (0.19, 0.10, 0.24), STEEL,
         bevel=0.015, parent=root)
    cube("sc_skid", (0, 0.235, 0.02), (0.34, 0.025, 0.44), STEEL,
         bevel=0.008, parent=root)

    # exhaust high on the right
    rod("sc_header", (0.09, 0.34, -0.16), (0.15, 0.34, 0.20), 0.042, RUST, parent=root)
    rod("sc_muffler", (0.15, 0.34, 0.20), (0.18, 0.46, 0.70), 0.050, RUST, parent=root)
    rod("sc_tip", (0.18, 0.46, 0.70), (0.18, 0.47, 0.79), 0.058, STEEL, parent=root)

    # crash bars
    for sx in (-1.0, 1.0):
        rod("sc_crash_a%.0f" % sx, (sx * 0.20, 0.62, -0.20), (sx * 0.30, 0.44, -0.12),
            0.020, STEEL, parent=root)
        rod("sc_crash_b%.0f" % sx, (sx * 0.30, 0.44, -0.12), (sx * 0.28, 0.38, 0.18),
            0.020, STEEL, parent=root)

    # pegs and kickstand
    for sx in (-0.20, 0.20):
        cyl("sc_peg%.0f" % sx, (sx, 0.44, 0.10), 0.022, 0.13, RUBBER,
            rot=(0, math.pi / 2, 0), verts=12, parent=root)
    rod("sc_kick", (-0.17, 0.42, 0.16), (-0.31, 0.01, 0.32), 0.016, STEEL, parent=root)
    return root


# ---------------------------------------------------------------------------
# 2. SPORT BIKE
# ---------------------------------------------------------------------------
def build_sport():
    root = new_root("SPORT")
    add_wheel(root, "sp_front", -0.66, 0.33, 0.075, style="star",
              rim_mat=GOLD, disc=True)
    add_wheel(root, "sp_rear", 0.60, 0.33, 0.115, style="star",
              rim_mat=GOLD, disc=False)

    # twin-spar frame
    for sx in (-0.115, 0.115):
        rod("sp_spar", (sx, 0.86, -0.44), (sx, 0.52, 0.22), 0.034, ALU, parent=root)
        rod("sp_subframe", (sx, 0.52, 0.22), (sx, 0.82, 0.54), 0.022, ALU, parent=root)
        rod("sp_swing", (sx, 0.52, 0.20), (sx, 0.33, 0.58), 0.036, ALU, parent=root)
    rod("sp_head", (0, 0.85, -0.46), (0, 0.97, -0.43), 0.060, STEEL, parent=root)

    # forks
    for sx in (-0.085, 0.085):
        rod("sp_fork_low", (sx, 0.33, -0.66), (sx, 0.80, -0.51), 0.031, GOLD, parent=root)
        rod("sp_fork_top", (sx, 0.80, -0.51), (sx, 0.95, -0.46), 0.024, GOLD, parent=root)
    cube("sp_clamp", (0, 0.93, -0.46), (0.25, 0.05, 0.12), STEEL,
         bevel=0.01, parent=root)
    for sx in (-1.0, 1.0):
        rod("sp_clip%.0f" % sx, (sx * 0.10, 0.94, -0.45), (sx * 0.29, 0.865, -0.37),
            0.017, STEEL, parent=root)
        rod("sp_grip%.0f" % sx, (sx * 0.29, 0.865, -0.37), (sx * 0.36, 0.85, -0.35),
            0.026, RUBBER, parent=root)

    # fairing
    ball("sp_nose", (0, 0.80, -0.56), (0.30, 0.27, 0.36), CRIMSON, parent=root)
    for sx in (-0.20, 0.20):
        ball("sp_side%.0f" % sx, (sx, 0.62, -0.16), (0.135, 0.27, 0.46),
             CRIMSON, parent=root)
        ball("sp_wing%.0f" % sx, (sx * 1.15, 0.70, -0.34), (0.09, 0.06, 0.20),
             CARBON, parent=root)
    cube("sp_belly", (0, 0.40, -0.05), (0.34, 0.17, 0.46), CARBON,
         bevel=0.03, parent=root)
    cube("sp_screen", (0, 1.03, -0.58), (0.31, 0.23, 0.010), SMOKE,
         rot=(0.55, 0, 0), bevel=0.005, parent=root)
    for sx in (-0.085, 0.085):
        cyl("sp_lamp%.0f" % sx, (sx, 0.82, -0.705), 0.056, 0.026, LAMP_COOL,
            rot=(math.pi / 2, 0, 0), verts=20, parent=root)
        torus("sp_lamp_ring%.0f" % sx, (sx, 0.82, -0.720), 0.058, 0.007,
              CHROME, parent=root, seg=20, rseg=6)

    # tank and seat
    ball("sp_tank", (0, 0.84, -0.16), (0.27, 0.19, 0.46), CRIMSON, parent=root)
    cube("sp_tank_stripe", (0, 0.935, -0.16), (0.055, 0.012, 0.34), BLACK,
         bevel=0.004, parent=root)
    cube("sp_seat", (0, 0.875, 0.20), (0.22, 0.055, 0.34), LEATHER,
         bevel=0.015, parent=root)
    ball("sp_tail", (0, 0.89, 0.47), (0.19, 0.11, 0.26), CRIMSON, parent=root)
    cube("sp_tail_light", (0, 0.905, 0.605), (0.10, 0.03, 0.02), TAIL_RED,
         bevel=0.004, parent=root)
    ball("sp_hugger", (0, 0.62, 0.60), (0.11, 0.035, 0.25), CARBON, parent=root)

    # exhaust
    rod("sp_header", (0.10, 0.40, -0.16), (0.15, 0.33, 0.10), 0.030, CHROME, parent=root)
    rod("sp_muffler", (0.15, 0.33, 0.10), (0.19, 0.46, 0.52), 0.056, CARBON, parent=root)
    rod("sp_muffler_tip", (0.19, 0.46, 0.52), (0.20, 0.47, 0.58), 0.060, STEEL, parent=root)

    # chain and pegs
    cube("sp_chain", (0.10, 0.355, 0.30), (0.016, 0.016, 0.32), DARK_STEEL,
         bevel=0.002, parent=root)
    for sx in (-0.19, 0.19):
        cyl("sp_peg%.0f" % sx, (sx, 0.47, 0.16), 0.019, 0.11, ALU,
            rot=(0, math.pi / 2, 0), verts=12, parent=root)
    rod("sp_kick", (-0.16, 0.44, 0.18), (-0.29, 0.01, 0.33), 0.014, ALU, parent=root)
    return root


# ---------------------------------------------------------------------------
# 3. CRUISER
# ---------------------------------------------------------------------------
def build_cruiser():
    root = new_root("CRUISER")
    add_wheel(root, "cr_front", -0.94, 0.34, 0.070, style="spoke",
              rim_mat=CHROME, whitewall=False)
    add_wheel(root, "cr_rear", 0.64, 0.34, 0.135, style="solid",
              rim_mat=CHROME, whitewall=True, disc=False)

    # frame
    rod("cr_backbone", (0, 0.94, -0.56), (0, 0.66, 0.26), 0.038, BLACK, parent=root)
    rod("cr_down", (0, 0.94, -0.58), (0, 0.36, -0.18), 0.036, BLACK, parent=root)
    for sx in (-0.075, 0.075):
        rod("cr_rail", (sx, 0.66, 0.26), (sx, 0.74, 0.68), 0.022, BLACK, parent=root)
        rod("cr_swing", (sx, 0.44, 0.30), (sx, 0.34, 0.64), 0.028, BLACK, parent=root)
        rod("cr_stay", (sx, 0.34, 0.64), (sx, 0.68, 0.32), 0.018, BLACK, parent=root)

    # raked fork
    for sx in (-0.10, 0.10):
        rod("cr_fork", (sx, 0.34, -0.94), (sx, 1.00, -0.52), 0.030, CHROME, parent=root)
        rod("cr_fork_shroud", (sx, 0.62, -0.735), (sx, 0.96, -0.555), 0.044,
            CHROME, parent=root)
    cube("cr_triple", (0, 1.00, -0.53), (0.29, 0.05, 0.115), CHROME,
         bevel=0.012, parent=root)

    # headlight
    cyl("cr_lamp_can", (0, 0.90, -0.70), 0.105, 0.13, CHROME,
        rot=(math.pi / 2, 0, 0), verts=24, parent=root)
    cyl("cr_lamp_lens", (0, 0.90, -0.765), 0.086, 0.012, LAMP_WARM,
        rot=(math.pi / 2, 0, 0), verts=24, parent=root)
    torus("cr_lamp_ring", (0, 0.90, -0.757), 0.096, 0.010, CHROME,
          parent=root, seg=24, rseg=8)

    # ape hangers
    for sx in (-0.10, 0.10):
        rod("cr_riser%.0f" % sx, (sx, 1.02, -0.52), (sx, 1.28, -0.45), 0.017,
            CHROME, parent=root)
        rod("cr_bar%.0f" % sx, (sx, 1.28, -0.45), (sx * 3.3, 1.25, -0.38), 0.016,
            CHROME, parent=root)
        rod("cr_grip%.0f" % sx, (sx * 3.3, 1.25, -0.38), (sx * 4.0, 1.23, -0.36),
            0.028, RUBBER, parent=root)
        # mirror
        rod("cr_mirror_stem%.0f" % sx, (sx * 2.4, 1.27, -0.40), (sx * 2.6, 1.40, -0.44),
            0.007, CHROME, parent=root)
        cyl("cr_mirror%.0f" % sx, (sx * 2.6, 1.41, -0.445), 0.045, 0.012, CHROME,
            rot=(0, math.pi / 2, 0), verts=16, parent=root)

    # teardrop tank
    ball("cr_tank", (0, 0.80, -0.14), (0.29, 0.23, 0.64), CREAM, parent=root)
    for sx in (-0.142, 0.142):
        cube("cr_tank_stripe", (sx, 0.80, -0.14), (0.008, 0.06, 0.40),
             BLACK, bevel=0.002, parent=root)
    cyl("cr_cap", (0, 0.923, -0.16), 0.040, 0.016, CHROME, verts=16, parent=root)

    # saddle + pillion
    cube("cr_saddle", (0, 0.695, 0.26), (0.31, 0.060, 0.42), LEATHER_BROWN,
         bevel=0.022, parent=root)
    ball("cr_saddle_nose", (0, 0.70, 0.02), (0.24, 0.075, 0.20), LEATHER_BROWN,
         parent=root)
    cube("cr_pillion", (0, 0.755, 0.58), (0.26, 0.055, 0.19), LEATHER_BROWN,
         bevel=0.018, parent=root)

    # sissy bar
    rod("cr_sissy", (0.0, 0.72, 0.80), (0.0, 1.27, 0.82), 0.018, CHROME, parent=root)
    rod("cr_sissy_top", (0.0, 1.27, 0.82), (0.0, 1.27, 0.92), 0.018, CHROME, parent=root)
    cube("cr_back_pad", (0, 1.06, 0.835), (0.25, 0.20, 0.06), LEATHER_BROWN,
         bevel=0.02, parent=root)

    # rear fender + saddlebags
    ball("cr_fender", (0, 0.62, 0.68), (0.18, 0.070, 0.46), CREAM, parent=root)
    for sx in (-1.0, 1.0):
        cube("cr_bag%.0f" % sx, (sx * 0.30, 0.58, 0.62), (0.15, 0.30, 0.34),
             LEATHER_BROWN, bevel=0.03, parent=root)
        cube("cr_bag_flap%.0f" % sx, (sx * 0.30, 0.58, 0.795), (0.16, 0.31, 0.055),
             LEATHER, bevel=0.018, parent=root)
        cube("cr_bag_strap%.0f" % sx, (sx * 0.375, 0.58, 0.62), (0.012, 0.33, 0.055),
             LEATHER, bevel=0.004, parent=root)
        cube("cr_bag_buckle%.0f" % sx, (sx * 0.383, 0.58, 0.62), (0.010, 0.045, 0.05),
             CHROME, bevel=0.003, parent=root)

    # V-twin engine
    cube("cr_crank", (0, 0.32, 0.02), (0.29, 0.25, 0.32), DARK_STEEL,
         bevel=0.025, parent=root)
    finned("cr_vfront", (0, 0.36, -0.18), (0, 0.64, -0.33), 0.115, 6,
           BLACK, CHROME, parent=root)
    finned("cr_vrear", (0, 0.36, 0.06), (0, 0.62, 0.18), 0.115, 6,
           BLACK, CHROME, parent=root)
    cube("cr_airbox", (0.22, 0.50, 0.00), (0.14, 0.18, 0.24), CHROME,
         bevel=0.03, parent=root)

    # exhaust: dual chrome pipes down the right side
    rod("cr_pipe_a", (0.12, 0.38, -0.22), (0.21, 0.27, 0.18), 0.038, CHROME, parent=root)
    rod("cr_pipe_b", (0.21, 0.27, 0.18), (0.22, 0.30, 0.78), 0.044, CHROME, parent=root)
    rod("cr_pipe_c", (0.12, 0.38, 0.06), (0.20, 0.25, 0.22), 0.034, CHROME, parent=root)
    rod("cr_pipe_d", (0.20, 0.25, 0.22), (0.20, 0.26, 0.72), 0.036, CHROME, parent=root)
    for zz in (0.74, 0.80):
        cyl("cr_tip%.2f" % zz, (0.22 if zz > 0.77 else 0.20, 0.30 if zz > 0.77 else 0.26,
                                zz), 0.050, 0.05, CHROME,
            rot=(math.pi / 2, 0, 0), verts=16, parent=root)

    # forward pegs
    for sx in (-0.24, 0.24):
        rod("cr_peg_arm%.0f" % sx, (sx * 0.6, 0.36, -0.20), (sx, 0.40, -0.38),
            0.014, CHROME, parent=root)
        cyl("cr_peg%.0f" % sx, (sx, 0.40, -0.38), 0.022, 0.13, RUBBER,
            rot=(0, math.pi / 2, 0), verts=12, parent=root)
    rod("cr_kick", (-0.18, 0.38, 0.14), (-0.33, 0.01, 0.30), 0.015, CHROME, parent=root)
    return root


# ---------------------------------------------------------------------------
# build + export
# ---------------------------------------------------------------------------
bikes = [
    ("bike_scrambler", build_scrambler()),
    ("bike_sport", build_sport()),
    ("bike_cruiser", build_cruiser()),
]


def export_bike(root, filename):
    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    for child in root.children_recursive:
        child.select_set(True)
    bpy.context.view_layer.objects.active = root
    path = OUT_DIR / filename
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB",
                              use_selection=True, export_apply=True,
                              export_yup=True)
    print("EXPORTED", path, path.stat().st_size)


for name, root in bikes:
    export_bike(root, name + ".glb")
    # verify ground contact and overall size
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    for child in root.children_recursive:
        if child.type != "MESH":
            continue
        for corner in child.bound_box:
            world = child.matrix_world @ Vector(corner)
            lo = Vector((min(lo.x, world.x), min(lo.y, world.y), min(lo.z, world.z)))
            hi = Vector((max(hi.x, world.x), max(hi.y, world.y), max(hi.z, world.z)))
    print("BOUNDS", name, "min", tuple(round(v, 3) for v in lo),
          "max", tuple(round(v, 3) for v in hi),
          "size", tuple(round(v, 3) for v in (hi - lo)))

if SKIP_RENDERS:
    print("SKIP_RENDERS: GLBs exported, quitting.")
    sys.stdout.flush()
    os._exit(0)

# ---------------------------------------------------------------------------
# studio set-up
# ---------------------------------------------------------------------------
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 48
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.02
scene.cycles.use_denoising = True
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False

scene.view_settings.view_transform = "AgX"
try:
    scene.view_settings.look = "AgX - Medium High Contrast"
except Exception:
    pass
scene.view_settings.exposure = 0.2

world = bpy.data.worlds.new("studio world")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.016, 0.019, 0.024, 1.0)
bg.inputs[1].default_value = 0.6

# floor: the bikes are modelled Y-up, so the ground plane is XZ at y=0
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0),
                                 rotation=(math.pi / 2, 0, 0))
floor = bpy.context.object
floor.name = "studio floor"
floor.data.materials.append(FLOOR)
# backdrop: vertical, behind the bikes (their tails point to +Z... camera +Z,
# so the backdrop goes on -Z), bottom edge resting on the floor.
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 9.0, -4.6))
back = bpy.context.object
back.name = "studio backdrop"
back.scale = (1.0, 0.45, 1.0)
back.data.materials.append(BACKDROP)


def area_light(name, loc, energy, size, color, target):
    light = bpy.data.lights.new(name, "AREA")
    light.energy = energy
    light.shape = "DISK"
    light.size = size
    light.color = color
    obj = bpy.data.objects.new(name, light)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return obj


area_light("key", (4.6, 5.0, 4.2), 900, 4.0, (1.0, 0.93, 0.84), (0, 0.6, 0))
area_light("fill", (-4.8, 3.2, 4.8), 380, 5.0, (0.72, 0.84, 1.0), (0, 0.6, 0))
area_light("rim_blue", (-4.5, 3.8, -4.4), 700, 3.0, (0.35, 0.65, 1.0), (0, 0.7, 0))
area_light("rim_amber", (4.5, 3.8, -4.4), 700, 3.0, (1.0, 0.52, 0.22), (0, 0.7, 0))
area_light("top", (0, 7.5, 0.6), 500, 6.0, (1.0, 1.0, 1.0), (0, 0.6, 0))

cam_data = bpy.data.cameras.new("camera")
cam_data.lens = 40
cam = bpy.data.objects.new("camera", cam_data)
bpy.context.scene.collection.objects.link(cam)
scene.camera = cam


def aim_camera(loc, target, lens):
    cam.location = loc
    cam_data.lens = lens
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()


def render_to(path, width, height):
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    print("RENDERED", path)


# ---------------------------------------------------------------------------
# individual beauty shots (each bike alone, front 3/4)
# ---------------------------------------------------------------------------
positions = {0: (-2.55, 0.0, 0.18), 1: (0.0, 0.0, 0.0), 2: (2.55, 0.0, 0.18)}
yaws = {0: math.pi + 0.85, 1: math.pi + 0.85, 2: math.pi + 0.85}


def set_bike_visible(root, shown):
    """Visibility is per-object: a hidden parent does not hide its meshes."""
    root.hide_render = not shown
    for child in root.children_recursive:
        child.hide_render = not shown


for index, (name, root) in enumerate(bikes):
    for other_index, (_, other) in enumerate(bikes):
        set_bike_visible(other, other_index == index)
        other.location = (0, 0, 0)
        other.rotation_euler = (0, 0, 0)
    root.location = (0, 0, 0)
    root.rotation_euler = (0, math.pi + 0.05, 0)
    aim_camera((3.05, 1.62, 3.85), (0, 0.64, 0.0), 52)
    render_to(RENDER_DIR / (name + ".png"), 900, 700)

# ---------------------------------------------------------------------------
# line-up hero shot
# ---------------------------------------------------------------------------
for index, (name, root) in enumerate(bikes):
    set_bike_visible(root, True)
    root.location = positions[index]
    root.rotation_euler = (0, yaws[index], 0)
    root.scale = (1, 1, 1)
aim_camera((0, 1.50, 8.6), (0, 0.66, 0.0), 38)
scene.render.resolution_x = 1500
scene.render.resolution_y = 850
scene.cycles.samples = 56
scene.render.filepath = str(RENDER_DIR / "three_bikes_lineup.png")
bpy.ops.render.render(write_still=True)
print("RENDERED", RENDER_DIR / "three_bikes_lineup.png")

bpy.ops.wm.save_as_mainfile(filepath=str(RENDER_DIR / "three_bikes.blend"))
print("SAVED", RENDER_DIR / "three_bikes.blend")
print("THREE_BIKES_DONE")
