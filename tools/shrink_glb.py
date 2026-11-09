import bpy, os, sys
src=sys.argv[sys.argv.index("--")+1]
dst=sys.argv[sys.argv.index("--")+2]
size=int(sys.argv[sys.argv.index("--")+3])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for img in bpy.data.images:
    if img.size[0] > size or img.size[1] > size:
        img.scale(size, size)
        print("SCALED", img.name, "->", size)
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=False,
    export_animations=False, export_apply=False, export_image_format="JPEG", export_image_quality=82)
print("WROTE", dst, os.path.getsize(dst))
