"""Remove the stray spare-magazine/stock from the Makarov.

The gun is a single fragmented mesh (330 loose parts). The body is the densest cluster, so every
part whose centre falls well outside the body's bounds is dropped, then the rest is joined back
into one mesh. A backup of the original is written next to it.
"""
import bpy
import shutil

SRC = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\weapons\makarov.glb"
BAK = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\weapons\makarov_before_trim.glb"

shutil.copyfile(SRC, BAK)
print("backup written")

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
print("parts", len(parts))

# the body cluster = parts near the densest region (the slide + frame carry most vertices)
parts.sort(key=lambda o: -len(o.data.vertices))
core = parts[0]
cco = [core.matrix_world @ v.co for v in core.data.vertices]
lo = [min(p[i] for p in cco) for i in range(3)]
hi = [max(p[i] for p in cco) for i in range(3)]
span = [hi[i] - lo[i] for i in range(3)]
margin = [max(0.01, span[i] * 0.6) for i in range(3)]
print("core verts", len(cco), "span", [round(s, 3) for s in span])

keep = []
drop = 0
for o in parts:
    co = [o.matrix_world @ v.co for v in o.data.vertices]
    if not co:
        drop += 1
        continue
    c = [sum(p[i] for p in co) / len(co) for i in range(3)]
    inside = all(lo[i] - margin[i] <= c[i] <= hi[i] + margin[i] for i in range(3))
    if inside:
        keep.append(o)
    else:
        bpy.data.objects.remove(o, do_unlink=True)
        drop += 1

print("kept", len(keep), "dropped", drop)

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
print("exported", SRC)
