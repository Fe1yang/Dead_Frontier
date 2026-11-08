"""Bind the new Riley mesh to the UAL skeleton with Blender's automatic weights.

The distance-based weighting in retarget_universal_actors.py mangled the legs of this Tripo
model (a stretched "skirt" from the hips to the floor), so this builds the actor the simple
way: the library armature IS the skeleton the game's clips are written for, so binding the
mesh to it with ARMATURE_AUTO needs no retarget math at all.

Run: blender -b -P rebind_riley.py
"""
import bpy, os
from mathutils import Vector

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
LIB = os.path.join(ROOT, "assets", "animation-library", "ual1", "UAL1_Standard.glb")
MESH = os.path.join(ROOT, "assets", "models", "generated", "survivor_riley_hd.glb")
OUT = os.path.join(ROOT, "assets", "models", "actors", "survivor_riley_universal.glb")

bpy.ops.wm.read_factory_settings(use_empty=True)

# 1) the animation library: its armature is the skeleton every clip targets
bpy.ops.import_scene.gltf(filepath=LIB)
armatures = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
if not armatures:
    raise SystemExit("no armature in the library")
arm = armatures[0]
# the game finds the rig by this name (gun grip, IK, animation retarget paths)
arm.name = "UniversalRig"
arm.data.name = "UniversalRig"
print("ARMATURE", arm.name, "bones", len(arm.data.bones))
# the library ships its own mannequin body: it must not end up in the actor file
for o in list(bpy.context.scene.objects):
	if o.type == "MESH":
		print("DELETING LIBRARY MESH", o.name)
		bpy.data.objects.remove(o, do_unlink=True)

# 2) the character mesh
before = set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=MESH)
new_objects = [o for o in bpy.context.scene.objects if o not in before]
meshes = [o for o in new_objects if o.type == "MESH"]
print("MESHES", [o.name for o in meshes])
# join every piece into one object
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
body.name = "HighDetailCharacter"

# 3) match the rig's height and put the feet on the floor
bpy.context.view_layer.update()
box = [body.matrix_world @ Vector(c) for c in body.bound_box]
lo = Vector((min(v.x for v in box), min(v.y for v in box), min(v.z for v in box)))
hi = Vector((max(v.x for v in box), max(v.y for v in box), max(v.z for v in box)))
height = hi.z - lo.z
print("MESH_BOX", tuple(round(v, 3) for v in lo), tuple(round(v, 3) for v in hi), "height", round(height, 3))
target = 1.78
scale = target / max(height, 0.01)
body.scale = body.scale * scale
bpy.context.view_layer.update()
box = [body.matrix_world @ Vector(c) for c in body.bound_box]
lo = Vector((min(v.x for v in box), min(v.y for v in box), min(v.z for v in box)))
hi = Vector((max(v.x for v in box), max(v.y for v in box), max(v.z for v in box)))
body.location.x -= (lo.x + hi.x) * 0.5
body.location.y -= (lo.y + hi.y) * 0.5
body.location.z -= lo.z
# the source faces -Y here; the rig faces -Y too, so no turn is needed
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# 4) automatic weights onto the library skeleton
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.parent_set(type="ARMATURE_AUTO")
print("BOUND with automatic weights")

# 4b) the run/reload clips the game asks for were built by the retarget pipeline, not by the
# library: take them from the previous export (same bone names, same rig rest).
OLD = os.path.join(ROOT, "assets", "models", "generated", "survivor_riley_universal.old.glb")
if os.path.exists(OLD):
	before2 = set(bpy.context.scene.objects)
	bpy.ops.import_scene.gltf(filepath=OLD)
	for o in [o for o in bpy.context.scene.objects if o not in before2]:
		bpy.data.objects.remove(o, do_unlink=True)

# 5) export the mesh + the library actions the game asks for
keep = {"Run_Gun_Loop", "Run_Gun_F_Loop", "Reload_Gun_Loop", "Reload_Gun_F_Loop",
        "Pistol_Aim_Neutral", "Pistol_Shoot", "Pistol_Reload", "Death01", "Hit_Chest",
        "Run_Gun", "Reload_Gun"}
for action in list(bpy.data.actions):
    if action.name not in keep:
        bpy.data.actions.remove(action)
print("ACTIONS", [a.name for a in bpy.data.actions])

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
print("REBOUND_EXPORTED", OUT, os.path.getsize(OUT))
