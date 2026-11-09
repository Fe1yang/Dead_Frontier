"""Drop the spare magazine that ships beside the Makarov.

The model is 330 loose parts. The pistol and the spare mag are separated by a clear gap, so the
parts are sorted along the axis that shows the widest empty gap and only the denser side is kept.
A backup of the original is written first.
"""
import bpy
import shutil

SRC = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\weapons\makarov.glb"
BAK = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\weapons\makarov_original.glb"

shutil.copyfile(SRC, BAK)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)

obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.separate(type="LOOSE")
bpy.ops.object.mode_set(mode="OBJECT")

parts = [o for o in bpy.context.scene.objects if o.type == "MESH"]

def centre(o):
    co = [o.matrix_world @ v.co for v in o.data.vertices]
    if not co:
        return None
    return (sum(p.x for p in co) / len(co),
            sum(p.y for p in co) / len(co),
            sum(p.z for p in co) / len(co))

items = []
for o in parts:
    c = centre(o)
    if c is not None:
        items.append((o, c))
print("parts", len(items))

# find the axis with the single widest gap between neighbouring part centres
best = None
for axis in range(3):
    vals = sorted(items, key=lambda it: it[1][axis])
    for i in range(len(vals) - 1):
        gap = vals[i + 1][1][axis] - vals[i][1][axis]
        left = sum(len(v[0].data.vertices) for v in vals[:i + 1])
        right = sum(len(v[0].data.vertices) for v in vals[i + 1:])
        if left < 20 or right < 20:
            continue
        score = gap
        if best is None or score > best[0]:
            best = (score, axis, i, vals, left, right)

assert best is not None
score, axis, cut, vals, left, right = best
print("widest gap axis", axis, "size", round(score, 4), "left verts", left, "right verts", right)

keep_side = vals[:cut + 1] if left >= right else vals[cut + 1:]
keep = [v[0] for v in keep_side]
print("keeping", len(keep), "parts")

for o, _ in items:
    if o not in keep:
        bpy.data.objects.remove(o, do_unlink=True)

bpy.ops.object.select_all(action="DESELECT")
for o in keep:
    o.select_set(True)
bpy.context.view_layer.objects.active = keep[0]
if len(keep) > 1:
    bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
body.name = "Makarov"

bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=SRC, export_format="GLB", use_selection=True, export_animations=False, export_apply=False)
print("exported")
