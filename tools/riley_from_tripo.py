"""Riley from the Tripo auto-rig: normalise transforms, put the right hand bone back on the
hand, cut the knife, and bolt the game's clips onto the Tripo skeleton.

The Tripo rig is UE5-Mannequin style, so its bone names already match the Universal Animation
Library clips (pelvis, spine_01..03, clavicle/upperarm/lowerarm/hand_l/r, thigh/calf/foot/ball).
Its right hand joint sat inside the thigh, which is why the gun hung at her hip.

Run: blender -b -P riley_from_tripo.py
"""
import bpy, os
from mathutils import Vector

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
NEW = r"C:\Users\user\Downloads\tactical female character 3d model (1).glb"
OLD = os.path.join(ROOT, "assets", "models", "generated", "survivor_riley_universal.old.glb")
OUT = os.path.join(ROOT, "assets", "models", "actors", "survivor_riley_universal.glb")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=NEW)
bpy.context.view_layer.update()

for o in list(bpy.context.scene.objects):
    if o.type == "MESH" and o.name.startswith("Icosphere"):
        bpy.data.objects.remove(o, do_unlink=True)

# flatten the empty hierarchy, bake transforms into the armature and mesh
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
for o in list(bpy.context.scene.objects):
    if o.type == "EMPTY":
        bpy.data.objects.remove(o, do_unlink=True)
arm = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"][0]
body = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
bpy.ops.object.select_all(action="SELECT")
bpy.context.view_layer.objects.active = arm
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# scale to game height
bpy.context.view_layer.update()
box = [body.matrix_world @ Vector(c) for c in body.bound_box]
lo = Vector((min(p.x for p in box), min(p.y for p in box), min(p.z for p in box)))
hi = Vector((max(p.x for p in box), max(p.y for p in box), max(p.z for p in box)))
factor = 1.78 / max(hi.z - lo.z, 0.01)
for o in (arm, body):
    o.scale = o.scale * factor
bpy.ops.object.select_all(action="SELECT")
bpy.context.view_layer.objects.active = arm
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.context.view_layer.update()

# ---- knife: vertices that belong to the right hand but sit far from it
gi = body.vertex_groups["hand_r"].index
hand_pts = []
for v in body.data.vertices:
    for g in v.groups:
        if g.group == gi and g.weight > 0.4:
            hand_pts.append(v.co.copy())
            break
if not hand_pts:
    raise SystemExit("no vertices weighted to hand_r")
hc = sum(hand_pts, Vector()) / len(hand_pts)
print("HAND_CENTROID", tuple(round(v, 3) for v in hc), "verts", len(hand_pts))
blade = [v.index for v in body.data.vertices
         if any(g.group == gi and g.weight > 0.35 for g in v.groups) and (v.co - hc).length > 0.13]
print("BLADE_VERTS", len(blade))

# ---- the hand bone: move it onto the actual hand, and drag its vertices with it so nothing
#      deforms; the gun then attaches where the hand really is
eb = arm.data.bones["hand_r"]
old_head = eb.head_local.copy()
delta = hc - old_head
print("HAND_DELTA", tuple(round(v, 3) for v in delta))
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
ebones = arm.data.edit_bones
ebones["hand_r"].head = ebones["hand_r"].head + delta
ebones["hand_r"].tail = ebones["hand_r"].tail + delta
bpy.ops.object.mode_set(mode="OBJECT")
for v in body.data.vertices:
    if any(g.group == gi and g.weight > 0.001 for g in v.groups):
        v.co = v.co + delta

# ---- remove the blade, then weld the leftovers
if blade:
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.mode_set(mode="OBJECT")
    for i in blade:
        body.data.vertices[i].select = True
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.delete(type="VERT")
    bpy.ops.object.mode_set(mode="OBJECT")
print("AFTER_DELETE verts", len(body.data.vertices))

# ---- the game's clips: same bone names, so they apply as-is
b2 = set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=OLD)
for o in [o for o in bpy.context.scene.objects if o not in b2]:
    bpy.data.objects.remove(o, do_unlink=True)
keep = {"Run_Gun_Loop", "Run_Gun_F_Loop", "Reload_Gun_Loop", "Reload_Gun_F_Loop",
        "Pistol_Aim_Neutral", "Pistol_Shoot", "Pistol_Reload", "Death01", "Hit_Chest"}
for action in list(bpy.data.actions):
    if action.name not in keep:
        bpy.data.actions.remove(action)
print("ACTIONS", [a.name for a in bpy.data.actions])

# ---- check render of a running frame
if arm.animation_data is None:
    arm.animation_data_create()
for a in bpy.data.actions:
    if a.name == "Run_Gun_Loop":
        arm.animation_data.action = a
        break
bpy.context.scene.frame_set(12)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 512
scene.render.resolution_y = 640
scene.render.film_transparent = True
world = bpy.data.worlds.new("W")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.55, 0.6, 1)
light = bpy.data.objects.new("k", bpy.data.lights.new("k", type="AREA"))
light.data.energy = 900
light.data.size = 3.0
light.location = (1.6, -2.4, 2.2)
light.rotation_euler = (Vector((0, 0, 1.0)) - Vector(light.location)).to_track_quat("-Z", "Y").to_euler()
scene.collection.objects.link(light)
cam_data = bpy.data.cameras.new("c")
cam_data.type = "ORTHO"
cam_data.ortho_scale = 2.1
cam = bpy.data.objects.new("c", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam.location = Vector((1.9, -2.9, 1.2))
cam.rotation_euler = (Vector((0, 0, 0.95)) - cam.location).to_track_quat("-Z", "Y").to_euler()
scene.render.filepath = os.path.join(ROOT, "assets", "models", "actors", "riley_tripo_check.png")
bpy.ops.render.render(write_still=True)
print("CHECK_RENDERED")

bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
arm.select_set(True)
bpy.ops.export_scene.gltf(
    filepath=OUT,
    export_format="GLB",
    use_selection=True,
    export_animations=True,
    export_animation_mode="ACTIONS",
    export_force_sampling=True,
    export_apply=False,
)
print("TRIPO_RIG_EXPORTED", OUT, os.path.getsize(OUT))
