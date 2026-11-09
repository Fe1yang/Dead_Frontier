"""Give a rigged GLB the animation clips from another GLB that uses the same bone names.

Keeps the model's own skin weights (no rebinding), it only copies the actions across.

Run: blender -b -P attach_clips.py -- <model_glb> <clips_glb> <out_glb>
"""
import bpy, os, sys

argv = sys.argv[sys.argv.index("--") + 1:]
MODEL, CLIPS, OUT = argv[0], argv[1], argv[2]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=MODEL)
arm = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"][0]
print("MODEL bones", len(arm.data.bones), "meshes",
      len([o for o in bpy.context.scene.objects if o.type == "MESH"]))
if arm.animation_data:
    arm.animation_data.action = None

before = set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=CLIPS)
for o in [o for o in bpy.context.scene.objects if o not in before]:
    if o.type != "ARMATURE":
        continue
    bpy.data.objects.remove(o, do_unlink=True)
print("CLIPS", [a.name for a in bpy.data.actions])

bpy.ops.object.select_all(action="DESELECT")
for o in bpy.context.scene.objects:
    if o.type in ("MESH", "ARMATURE"):
        o.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True,
                          export_animations=True, export_animation_mode="ACTIONS",
                          export_force_sampling=False, export_apply=False)
print("EXPORTED", OUT, os.path.getsize(OUT))
