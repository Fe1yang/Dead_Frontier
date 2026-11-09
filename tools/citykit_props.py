"""Export the street props we need from the CityMix kit, one GLB each, 1k atlas."""
import bpy
import os
import sys

args = sys.argv[sys.argv.index("--") + 1:]
KIT, TEX, OUTDIR = args[0], args[1], args[2]

# object name in the kit -> output file
WANTED = {
    "Can_Refreshment": "can_a",
    "Can_Refreshment1": "can_b",
    "Can_Refreshment2": "can_c",
    "Can_Refreshment3": "can_d",
    "Telephone_Cabin": "phone_booth",
    "ManHoleCover": "manhole",
    "Trash_Bin": "trash_bin",
    "Trash_Can": "trash_can",
    "Bemch": "bench",
    "Fire_Hydrant": "hydrant",
    "Lamp_Post_Modern": "lamp_modern",
    "Lamp_Post_Round": "lamp_round",
}

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=KIT)

img = bpy.data.images.load(TEX)
if img.size[0] > 1024 or img.size[1] > 1024:
    img.scale(1024, 1024)

for src_name, out_name in WANTED.items():
    obj = bpy.data.objects.get(src_name)
    if obj is None:
        print("MISSING", src_name)
        continue
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.duplicate()
    dup = bpy.context.view_layer.objects.active
    dup.name = out_name
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    for m in dup.data.materials:
        if m is None:
            continue
        m.use_nodes = True
        nt = m.node_tree
        bsdf = nt.nodes.get("Principled BSDF")
        for n in list(nt.nodes):
            if n.type == "TEX_IMAGE":
                nt.nodes.remove(n)
        if bsdf is not None:
            tex = nt.nodes.new("ShaderNodeTexImage")
            tex.image = img
            nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])

    bpy.ops.object.select_all(action="DESELECT")
    dup.select_set(True)
    bpy.context.view_layer.objects.active = dup
    out = os.path.join(OUTDIR, out_name + ".glb")
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True,
                              export_animations=False, export_apply=False,
                              export_image_format="JPEG", export_image_quality=88)
    print("PROP_OK", out_name, len(dup.data.polygons), os.path.getsize(out))
    bpy.data.objects.remove(dup, do_unlink=True)

print("PROPS_DONE")
