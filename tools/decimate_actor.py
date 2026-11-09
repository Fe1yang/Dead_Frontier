"""Decimate a skinned actor to a triangle budget, keeping the rig and its clips.

The mobile GPU budget is a few hundred thousand triangles per frame; the shipped actors were
100k-480k each, so the scene ran at roughly four times the budget and stuttered.

Run: blender -b -P decimate_actor.py -- <in.glb> <out.glb> <target_tris>
"""
import bpy, os, sys

args = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT, TARGET = args[0], args[1], int(args[2])

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)

meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
before = sum(len(o.data.polygons) for o in meshes)
if before == 0:
    print("NO_MESH", SRC)
    raise SystemExit(1)

for o in meshes:
    share = len(o.data.polygons) / float(before)
    want = max(200, int(TARGET * share))
    have = len(o.data.polygons)
    if have <= want:
        continue
    mod = o.modifiers.new("dec", "DECIMATE")
    mod.decimate_type = "COLLAPSE"
    mod.ratio = want / float(have)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier=mod.name)

after = sum(len(o.data.polygons) for o in meshes)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(
    filepath=OUT,
    export_format="GLB",
    use_selection=True,
    export_animations=True,
    export_apply=False,
    export_image_format="JPEG",
    export_image_quality=88,
)
print("DECIMATED", os.path.basename(SRC), before, "->", after, "bytes", os.path.getsize(OUT))
