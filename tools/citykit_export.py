"""Export one named mesh from the CityMix kit as its own GLB, with the kit's albedo map."""
import bpy
import os
import sys

args = sys.argv[sys.argv.index("--") + 1:]
SRC, NAME, TEX, OUT = args[0], args[1], args[2], args[3]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=SRC)

target = bpy.data.objects.get(NAME)
if target is None:
    print("NO_OBJECT", NAME)
    raise SystemExit(1)

for o in list(bpy.context.scene.objects):
    if o is not target and o.type == "MESH":
        bpy.data.objects.remove(o, do_unlink=True)

bpy.ops.object.select_all(action="DESELECT")
target.select_set(True)
bpy.context.view_layer.objects.active = target
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

img = bpy.data.images.load(TEX) if TEX and os.path.exists(TEX) else None
if img is not None:
    # the kit atlas is 8k; a single street prop needs 1024 at most
    if img.size[0] > 1024 or img.size[1] > 1024:
        img.scale(1024, 1024)


# the kit uses one atlas for everything; every material samples the same albedo
for m in target.data.materials:
    if m is None:
        continue
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    for n in list(nt.nodes):
        if n.type == "TEX_IMAGE":
            nt.nodes.remove(n)
    if img is not None and bsdf is not None:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        tex.location = (-420, 220)
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        if bsdf.inputs["Alpha"] is not None and img.channels == 4:
            nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
            m.blend_method = "CLIP"

bpy.ops.export_scene.gltf(
    filepath=OUT,
    export_format="GLB",
    use_selection=True,
    export_animations=False,
    export_apply=False,
    export_image_format="JPEG",
    export_image_quality=88,
)
print("KIT_OK", NAME, len(target.data.polygons), "faces", os.path.getsize(OUT))
