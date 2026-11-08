import bpy, os
from mathutils import Vector
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
MESH=os.path.join(ROOT,"assets","models","generated","survivor_riley_hd.glb")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=MESH)
bpy.context.view_layer.update()
meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0]
if len(meshes)>1:
    bpy.ops.object.join()
body=bpy.context.view_layer.objects.active
print("MESH", body.name, "verts", len(body.data.vertices), "polys", len(body.data.polygons))
# split into loose parts in a COPY so we can inspect islands
dup=body.copy(); dup.data=body.data.copy()
bpy.context.collection.objects.link(dup)
bpy.ops.object.select_all(action="DESELECT")
dup.select_set(True); bpy.context.view_layer.objects.active=dup
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.separate(type="LOOSE")
bpy.ops.object.mode_set(mode="OBJECT")
parts=[o for o in bpy.context.scene.objects if o.type=="MESH" and o.name!=body.name]
print("ISLANDS", len(parts))
parts.sort(key=lambda o: -len(o.data.vertices))
for o in parts[:24]:
    box=[o.matrix_world @ Vector(c) for c in o.bound_box]
    lo=Vector((min(v.x for v in box),min(v.y for v in box),min(v.z for v in box)))
    hi=Vector((max(v.x for v in box),max(v.y for v in box),max(v.z for v in box)))
    c=(lo+hi)*0.5; s=hi-lo
    print("ISLAND %-28s verts=%5d centre=(%.2f,%.2f,%.2f) size=(%.2f,%.2f,%.2f)" % (
        o.name, len(o.data.vertices), c.x, c.y, c.z, s.x, s.y, s.z))
print("ISLANDS_DONE")