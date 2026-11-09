"""Inspect the CityMix kit FBX: list every object with its size so we can pick props."""
import bpy
import os
import sys

args = sys.argv[sys.argv.index("--") + 1:]
SRC = args[0]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=SRC)

rows = []
for o in bpy.context.scene.objects:
    if o.type != "MESH":
        continue
    lo = [1e9, 1e9, 1e9]
    hi = [-1e9, -1e9, -1e9]
    for c in o.bound_box:
        w = o.matrix_world @ __import__("mathutils").Vector(c)
        for i in range(3):
            lo[i] = min(lo[i], w[i])
            hi[i] = max(hi[i], w[i])
    size = [round(hi[i] - lo[i], 2) for i in range(3)]
    rows.append((o.name, size, len(o.data.polygons)))

rows.sort()
for name, size, faces in rows:
    print("OBJ\t%s\t%s\t%s" % (name, size, faces))
print("COUNT", len(rows))
