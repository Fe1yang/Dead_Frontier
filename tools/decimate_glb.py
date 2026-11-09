import bpy, os, sys
args=sys.argv[sys.argv.index("--")+1:]
src,dst,tris=int(args[2]), None, 0
src=args[0]; dst=args[1]; target=int(args[2])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0]
if len(meshes)>1: bpy.ops.object.join()
body=bpy.context.view_layer.objects.active
before=len(body.data.polygons)
if before > target:
    m=body.modifiers.new("Dec","DECIMATE"); m.ratio=target/float(before)
    bpy.ops.object.modifier_apply(modifier=m.name)
for img in bpy.data.images:
    if img.size[0] > 1024 or img.size[1] > 1024: img.scale(1024,1024)
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True,
    export_animations=False, export_apply=False, export_image_format="JPEG", export_image_quality=85)
print("DECIMATED", src, before, "->", len(body.data.polygons), "bytes", os.path.getsize(dst))
