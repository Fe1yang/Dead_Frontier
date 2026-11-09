"""Convert an FBX prop from the Guns&Explosives pack into a GLB Godot can load.

The pack ships FBX + separate PBR maps; Godot 4 cannot import FBX, so this builds a textured GLB:
  blender -b -P fbx_to_glb.py -- <in.fbx> <base_color.png> <out.glb>
"""
import bpy
import os
import sys

args = sys.argv[sys.argv.index("--") + 1:]
SRC, TEX, OUT = args[0], args[1], args[2]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=SRC)

meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
if not meshes:
    print("NO_MESHES", SRC)
    raise SystemExit(1)

bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

img = None
if TEX and os.path.exists(TEX):
    img = bpy.data.images.load(TEX)

for m in body.data.materials:
    if m is None:
        continue
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    if img is not None:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        tex.location = (-420, 220)
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.55
        bsdf.inputs["Metallic"].default_value = 0.35

bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(
    filepath=OUT,
    export_format="GLB",
    use_selection=True,
    export_animations=False,
    export_apply=False,
)
print("FBX_OK", os.path.basename(OUT), len(body.data.polygons), "faces", os.path.getsize(OUT))
