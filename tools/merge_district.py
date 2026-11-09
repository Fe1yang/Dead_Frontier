# Merge every mesh inside a district GLB into one object (materials kept as separate slots).
# Same triangles, same textures; only the submitted mesh count drops.
import bpy, os, sys
args = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = args[0], args[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
if not meshes:
    print("NO_MESHES", SRC)
    raise SystemExit(1)
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
if len(meshes) > 1:
    bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
print("MERGED", os.path.basename(SRC), len(meshes), "objects ->", len(body.data.polygons), "faces,", len(body.data.materials), "materials")
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True, export_animations=False, export_apply=False, export_image_format="JPEG", export_image_quality=88)
print("WROTE", OUT, os.path.getsize(OUT))