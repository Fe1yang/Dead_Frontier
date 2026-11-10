"""Slim the supply crate: it is 17 MB and instantiating it mid-run costs ~150 ms.

Decimate the mesh and shrink every texture to 512, then export over the original.
"""
import bpy
import os

SRC = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\props\supply_case.glb"
OUT = SRC

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)

meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
print("MESHES", len(meshes))

bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    mod = o.modifiers.new(name="dec", type="DECIMATE")
    mod.ratio = 0.35

# shrink every image to 512 max
for img in bpy.data.images:
    if img.size[0] > 512 or img.size[1] > 512:
        scale = 512.0 / max(img.size[0], img.size[1])
        img.scale(int(img.size[0] * scale) or 1, int(img.size[1] * scale) or 1)
        print("TEX", img.name, img.size[:])

bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True,
                          export_apply=True, export_animations=False)
print("EXPORTED", os.path.getsize(OUT))
