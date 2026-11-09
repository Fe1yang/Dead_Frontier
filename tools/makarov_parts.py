"""The Makarov arrives as ONE mesh named 'Magazine' that also carries a spare mag / stock.
Split it into loose parts and report each part's bounds so the stray piece can be identified."""
import bpy

SRC = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\weapons\makarov.glb"

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
print("PARTS", len(parts))
for o in parts:
    co = [o.matrix_world @ v.co for v in o.data.vertices]
    if not co:
        continue
    xs = [p.x for p in co]
    ys = [p.y for p in co]
    zs = [p.z for p in co]
    print("   %-22s verts=%-6d  size=(%.3f, %.3f, %.3f)  centre=(%.3f, %.3f, %.3f)" % (
        o.name, len(co),
        max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs),
        (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2, (max(zs) + min(zs)) / 2))
