"""Swap Maya (character 3) to the new rigged mechanic model.

The mechanic arrives already rigged by Tripo with the same UE5-Mannequin bone names the game's
animation library uses, so the clips apply directly: no re-binding, no weight painting. The
only work is normalising the empty hierarchy, scaling to game height, keeping the run/reload
clips and exporting. The thigh cloth is part of the mesh and rides the thigh bone with the
weights Tripo assigned.

Run: blender -b -P maya_from_tripo.py
"""
import bpy, os
from mathutils import Vector

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
NEW = r"C:\Users\user\Downloads\female mechanic 3d model (1).glb"
OLD = os.path.join(ROOT, "assets", "models", "generated", "survivor_maya_universal.old.glb")
OUT = os.path.join(ROOT, "assets", "models", "actors", "survivor_maya_universal.glb")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=NEW)
bpy.context.view_layer.update()

for o in list(bpy.context.scene.objects):
    if o.type == "MESH" and o.name.startswith("Icosphere"):
        bpy.data.objects.remove(o, do_unlink=True)

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

bpy.context.view_layer.update()
box = [body.matrix_world @ Vector(c) for c in body.bound_box]
lo = Vector((min(p.x for p in box), min(p.y for p in box), min(p.z for p in box)))
hi = Vector((max(p.x for p in box), max(p.y for p in box), max(p.z for p in box)))
factor = 1.75 / max(hi.z - lo.z, 0.01)
for o in (arm, body):
    o.scale = o.scale * factor
bpy.ops.object.select_all(action="SELECT")
bpy.context.view_layer.objects.active = arm
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.context.view_layer.update()
print("MAYA_FIT", round(factor, 3))

# feet on the floor, centred on x/y
bpy.context.view_layer.update()
box = [body.matrix_world @ Vector(c) for c in body.bound_box]
lo = Vector((min(p.x for p in box), min(p.y for p in box), min(p.z for p in box)))
hi = Vector((max(p.x for p in box), max(p.y for p in box), max(p.z for p in box)))
shift = Vector((-(lo.x + hi.x) * 0.5, -(lo.y + hi.y) * 0.5, -lo.z))
for o in (arm, body):
    o.location = o.location + shift
bpy.ops.object.select_all(action="SELECT")
bpy.context.view_layer.objects.active = arm
bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

# clips from the previous Maya export (same bone names)
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

# pose check
if arm.animation_data is None:
    arm.animation_data_create()
for a in bpy.data.actions:
    if a.name == "Run_Gun_Loop":
        arm.animation_data.action = a
        try:
            arm.animation_data.action_slot = a.slots[0]
        except Exception as exc:
            print("slot skipped:", exc)
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
scene.render.filepath = os.path.join(ROOT, "assets", "models", "actors", "maya_run_check.png")
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
print("MAYA_EXPORTED", OUT, os.path.getsize(OUT))
