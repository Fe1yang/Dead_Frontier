"""Shrink the textures inside the zombie GLBs.

Zombies are seen from a distance in a runner, so 512 px maps are plenty and save both memory and
the first-use upload hitch. Skinning and animation must survive the round trip, so the export keeps
animations and does not apply modifiers.
"""
import bpy
import glob
import os
import sys

TARGET = 512
files = sorted(glob.glob(r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\actors\*abolic*.glb"))

for path in files:
    base = os.path.basename(path)
    before = os.path.getsize(path)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=path)

    scaled = 0
    for img in bpy.data.images:
        w, h = img.size
        if max(w, h) > TARGET:
            k = TARGET / float(max(w, h))
            img.scale(max(1, int(w * k)), max(1, int(h * k)))
            scaled += 1

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        use_selection=True,
        export_apply=False,
        export_animations=True,
    )
    after = os.path.getsize(path)
    print("SLIM %s  %.1f -> %.1f MB  textures=%d" % (base, before / 1048576.0, after / 1048576.0, scaled))
