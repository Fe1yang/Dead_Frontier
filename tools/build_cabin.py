"""Procedural survival cabin for the lobby: a low-poly bunker room with props.

Metres, Z-up, origin at the floor centre. The front (-Y in Blender -> +Z in glTF) is left
open so the lobby camera can look straight into the room.

Run: blender -b -P build_cabin.py -- <out.glb>
"""
import bpy, bmesh, math, os, sys, random
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0]
random.seed(3)

W, D, H = 8.0, 6.0, 3.4         # width, depth, height
T = 0.18                         # wall thickness

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def mat(name, color, rough=0.85, metal=0.0, emit=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emit:
        bsdf.inputs["Emission Color"].default_value = (*emit, 1)
        bsdf.inputs["Emission Strength"].default_value = 3.0
    return m


M = {
    "plaster": mat("CabinPlaster", (0.62, 0.61, 0.57), 0.95),
    "plaster_dark": mat("CabinPlasterDark", (0.40, 0.40, 0.38), 0.95),
    "floor": mat("CabinFloor", (0.30, 0.27, 0.24), 0.9),
    "wood": mat("CabinWood", (0.30, 0.19, 0.11), 0.8),
    "wood_dark": mat("CabinWoodDark", (0.17, 0.11, 0.07), 0.85),
    "steel": mat("CabinSteel", (0.34, 0.35, 0.36), 0.45, 0.85),
    "iron": mat("CabinIron", (0.12, 0.12, 0.13), 0.6, 0.7),
    "olive": mat("CabinOlive", (0.24, 0.26, 0.15), 0.85),
    "olive_dark": mat("CabinOliveDark", (0.15, 0.17, 0.10), 0.9),
    "canvas": mat("CabinCanvas", (0.42, 0.40, 0.30), 0.95),
    "sandbag": mat("CabinSandbag", (0.45, 0.40, 0.28), 0.95),
    "fabric": mat("CabinFabric", (0.35, 0.10, 0.10), 0.95),
    "paper": mat("CabinPaper", (0.78, 0.76, 0.68), 0.9),
    "glass": mat("CabinGlass", (0.35, 0.45, 0.5), 0.15),
    "lamp": mat("CabinLamp", (1.0, 0.85, 0.6), 0.4, 0.0, emit=(1.0, 0.78, 0.45)),
    "black": mat("CabinBlack", (0.05, 0.05, 0.05), 0.8),
    "red": mat("CabinRed", (0.45, 0.12, 0.10), 0.9),
}

parts = []


def box(name, loc, size, material, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(material)
    parts.append(ob)
    return ob


def cyl(name, loc, radius, depth, material, rot=(0, 0, 0), verts=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(material)
    parts.append(ob)
    return ob


def bevel(ob, width=0.01):
    m = ob.modifiers.new("bev", "BEVEL")
    m.width = width
    m.segments = 2
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier=m.name)


# ---------------- shell ----------------
box("Floor", (0, 0, -0.05), (W, D, 0.1), M["floor"])
box("Ceiling", (0, 0, H + 0.05), (W, D, 0.1), M["plaster_dark"])
box("WallBack", (0, -D / 2, H / 2), (W, T, H), M["plaster"])
box("WallLeft", (-W / 2, 0, H / 2), (T, D, H), M["plaster"])
box("WallRight", (W / 2, 0, H / 2), (T, D, H), M["plaster"])
# front wall with a door-sized opening on the right half
# Front is left OPEN (dollhouse view): only the header beam and two corner posts remain,
# otherwise the lobby camera would stare at a closed wall.
box("WallFrontHeader", (0, D / 2, H - 0.22), (W, T, 0.44), M["plaster"])
box("PostL", (-W / 2 + 0.12, D / 2, H / 2), (0.24, T, H), M["plaster"])
box("PostR", (W / 2 - 0.12, D / 2, H / 2), (0.24, T, H), M["plaster"])
# skirting + ceiling beams
for i in range(5):
    y = -D / 2 + 0.7 + i * (D - 1.4) / 4
    box("Beam%d" % i, (0, y, H - 0.14), (W - 0.1, 0.18, 0.22), M["wood_dark"])
box("SkirtingBack", (0, -D / 2 + 0.1, 0.08), (W - 0.2, 0.05, 0.16), M["wood_dark"])

# ---------------- window with sandbags (back-left) ----------------
box("WindowFrame", (-W * 0.28, -D / 2 + 0.1, 2.15), (2.4, 0.16, 1.2), M["wood_dark"])
box("WindowGlass", (-W * 0.28, -D / 2 + 0.12, 2.15), (2.15, 0.04, 0.95), M["glass"])
box("WindowSill", (-W * 0.28, -D / 2 + 0.22, 1.55), (2.5, 0.3, 0.1), M["wood"])
for i in range(7):
    for j in range(2):
        x = -W * 0.28 - 1.0 + i * 0.32 + (0.16 if j else 0)
        box("Sandbag_%d_%d" % (i, j), (x, -D / 2 + 0.34, 1.68 + j * 0.17),
            (0.34, 0.42, 0.18), M["sandbag"], rot=(0, 0, random.uniform(-0.08, 0.08)))

# ---------------- door (right of centre) ----------------
box("DoorFrame", (W * 0.10, D / 2 - 0.05, 1.05), (1.32, 0.16, 2.1), M["wood_dark"])
box("Door", (W * 0.10, D / 2 - 0.02, 1.02), (1.1, 0.08, 1.98), M["steel"])
box("DoorBar", (W * 0.10, D / 2 + 0.03, 1.02), (0.9, 0.05, 0.09), M["iron"])
box("DoorLamp", (W * 0.10, D / 2 - 0.12, 2.35), (0.16, 0.12, 0.16), M["lamp"])

# ---------------- notice board (back right) ----------------
box("BoardFrame", (W * 0.28, -D / 2 + 0.1, 1.78), (1.9, 0.1, 1.15), M["wood"])
box("Board", (W * 0.28, -D / 2 + 0.16, 1.78), (1.72, 0.04, 0.98), M["wood_dark"])
for i in range(6):
    px = W * 0.28 - 0.7 + (i % 3) * 0.5
    py = 1.95 if i < 3 else 1.62
    box("Paper%d" % i, (px, -D / 2 + 0.19, py), (0.32, 0.01, 0.24), M["paper"],
        rot=(0, 0, random.uniform(-0.05, 0.05)))
box("MapOnBoard", (W * 0.28 + 0.55, -D / 2 + 0.19, 1.78), (0.5, 0.01, 0.7), M["olive_dark"])

# ---------------- workbench + pegboard (left wall) ----------------
box("BenchTop", (-W / 2 + 0.45, -0.6, 1.02), (0.85, 2.6, 0.09), M["wood"])
box("BenchLegA", (-W / 2 + 0.45, -1.8, 0.5), (0.09, 0.09, 1.0), M["wood_dark"])
box("BenchLegB", (-W / 2 + 0.45, 0.6, 0.5), (0.09, 0.09, 1.0), M["wood_dark"])
box("ShelfLeft", (-W / 2 + 0.2, -0.6, 1.75), (0.3, 2.4, 0.07), M["wood"])
box("ShelfLeft2", (-W / 2 + 0.2, -0.6, 2.25), (0.3, 2.4, 0.07), M["wood"])
for i in range(5):
    box("Can%d" % i, (-W / 2 + 0.22, -1.6 + i * 0.42, 1.87), (0.13, 0.13, 0.22), M["olive"])
for i in range(3):
    box("Toolbox%d" % i, (-W / 2 + 0.45, -1.5 + i * 0.5, 1.12), (0.34, 0.2, 0.14), M["red"] if i == 1 else M["iron"])
# rifle on the wall
box("RifleBody", (-W / 2 + 0.16, 0.1, 1.95), (0.05, 0.95, 0.07), M["black"])
box("RifleMag", (-W / 2 + 0.16, 0.0, 1.85), (0.04, 0.12, 0.18), M["black"])
box("RifleStock", (-W / 2 + 0.16, 0.62, 1.95), (0.05, 0.22, 0.11), M["wood_dark"])

# ---------------- crates / barrels (right wall) ----------------
box("CrateBig", (W / 2 - 0.7, 1.4, 0.5), (0.9, 0.9, 1.0), M["olive"])
box("CrateLid", (W / 2 - 0.7, 1.4, 1.02), (0.94, 0.94, 0.06), M["olive_dark"])
box("CrateSmall", (W / 2 - 0.75, 0.55, 0.28), (0.62, 0.62, 0.56), M["olive"])
cyl("Barrel", (W / 2 - 1.55, 2.2, 0.46), 0.30, 0.92, M["red"])
cyl("BarrelRing", (W / 2 - 1.55, 2.2, 0.62), 0.315, 0.06, M["iron"])
box("SandbagRow", (W / 2 - 1.6, 0.9, 0.12), (1.2, 0.9, 0.24), M["sandbag"])

# ---------------- bed (back right corner) ----------------
box("BedBase", (W / 2 - 1.15, -D / 2 + 1.0, 0.28), (1.05, 2.1, 0.14), M["steel"])
box("Mattress", (W / 2 - 1.15, -D / 2 + 1.0, 0.40), (1.0, 2.0, 0.16), M["canvas"])
box("Pillow", (W / 2 - 1.15, -D / 2 + 1.8, 0.52), (0.55, 0.32, 0.14), M["paper"])
box("Blanket", (W / 2 - 1.15, -D / 2 + 0.55, 0.50), (1.02, 1.1, 0.09), M["fabric"])
for dx in (-0.45, 0.45):
    for dy in (-0.95, 0.95):
        box("BedLeg", (W / 2 - 1.15 + dx, -D / 2 + 1.0 + dy, 0.11), (0.08, 0.08, 0.22), M["steel"])

# ---------------- table + chairs (centre) ----------------
box("TableTop", (0.2, 0.3, 0.72), (1.5, 0.95, 0.08), M["wood"])
for dx in (-0.62, 0.62):
    for dy in (-0.36, 0.36):
        box("TableLeg", (0.2 + dx, 0.3 + dy, 0.34), (0.08, 0.08, 0.68), M["wood_dark"])
box("Mug", (0.05, 0.15, 0.82), (0.1, 0.1, 0.12), M["paper"])
box("Radio", (0.55, 0.2, 0.83), (0.26, 0.16, 0.14), M["black"])
box("Book1", (0.0, 0.55, 0.79), (0.32, 0.24, 0.05), M["red"])
box("Book2", (0.02, 0.55, 0.84), (0.30, 0.22, 0.04), M["olive"])
box("ChairSeat", (-0.95, 0.3, 0.46), (0.5, 0.5, 0.08), M["wood"])
box("ChairBack", (-0.95, 0.55, 0.72), (0.5, 0.07, 0.5), M["wood_dark"])

# ---------------- hanging lamp ----------------
cyl("LampCord", (0.2, 0.0, 2.55), 0.015, 1.7, M["black"], rot=(0, 0, 0))
cyl("LampShade", (0.2, 0.0, 1.78), 0.22, 0.22, M["iron"])
box("LampBulb", (0.2, 0.0, 1.66), (0.12, 0.12, 0.12), M["lamp"])

# ---------------- wall details ----------------
box("PipeA", (-W / 2 + 0.12, -2.5, 2.9), (0.1, D - 0.6, 0.1), M["steel"])
box("PipeB", (W / 2 - 0.12, 0.0, 3.0), (0.1, 0.1, 0.5), M["steel"])
box("VentGrill", (0, -D / 2 + 0.12, 2.95), (0.9, 0.06, 0.4), M["iron"])
box("Flag", (-W / 2 + 0.02, 1.9, 2.05), (0.02, 0.9, 1.2), M["fabric"])
box("Poster", (W / 2 - 0.02, -1.4, 2.2), (0.02, 0.6, 0.85), M["paper"])

# ---------------- join + export ----------------
bpy.ops.object.select_all(action="DESELECT")
for ob in parts:
    ob.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
cabin = bpy.context.object
cabin.name = "SurvivalCabin"
bpy.ops.object.shade_smooth()
bpy.ops.object.shade_flat()

bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True,
                          export_apply=True, export_yup=True)
print("CABIN_EXPORTED", OUT, os.path.getsize(OUT), "verts", len(cabin.data.vertices))
