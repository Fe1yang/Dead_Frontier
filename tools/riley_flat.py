import bpy, os
from mathutils import Vector
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
MESH=os.path.join(ROOT,"assets","models","generated","survivor_riley_hd.glb")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=MESH)
bpy.context.view_layer.update()
ms=[o for o in bpy.context.scene.objects if o.type=="MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in ms: o.select_set(True)
bpy.context.view_layer.objects.active=ms[0]
if len(ms)>1: bpy.ops.object.join()
body=bpy.context.view_layer.objects.active
box=[body.matrix_world @ Vector(c) for c in body.bound_box]
lo=Vector((min(v.x for v in box),min(v.y for v in box),min(v.z for v in box)))
hi=Vector((max(v.x for v in box),max(v.y for v in box),max(v.z for v in box)))
body.scale=body.scale*(1.78/max(hi.z-lo.z,0.01))
bpy.context.view_layer.update()
box=[body.matrix_world @ Vector(c) for c in body.bound_box]
lo=Vector((min(v.x for v in box),min(v.y for v in box),min(v.z for v in box)))
hi=Vector((max(v.x for v in box),max(v.y for v in box),max(v.z for v in box)))
body.location.x-=(lo.x+hi.x)*0.5; body.location.y-=(lo.y+hi.y)*0.5; body.location.z-=lo.z
bpy.ops.object.select_all(action="DESELECT"); body.select_set(True)
bpy.context.view_layer.objects.active=body
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
dup=body.copy(); dup.data=body.data.copy(); bpy.context.collection.objects.link(dup)
bpy.ops.object.select_all(action="DESELECT"); dup.select_set(True); bpy.context.view_layer.objects.active=dup
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.separate(type="LOOSE"); bpy.ops.object.mode_set(mode="OBJECT")
parts=[o for o in bpy.context.scene.objects if o.type=="MESH" and o.name!=body.name]
print("PARTS", len(parts))
flat=[]
for o in parts:
    b=[o.matrix_world @ Vector(c) for c in o.bound_box]
    l=Vector((min(v.x for v in b),min(v.y for v in b),min(v.z for v in b)))
    h=Vector((max(v.x for v in b),max(v.y for v in b),max(v.z for v in b)))
    s=h-l; c=(l+h)*0.5
    dims=sorted([s.x,s.y,s.z])
    if dims[0]<0.020 and dims[2]>0.18 and dims[2]<0.55:
        flat.append((c,s,len(o.data.vertices),o.name))
flat.sort(key=lambda t:-t[1].x*t[1].z)
for c,s,n,name in flat[:12]:
    print("  FLAT %-30s v=%4d centre=(%.2f,%.2f,%.2f) size=(%.2f,%.2f,%.2f)"%(name,n,c.x,c.y,c.z,s.x,s.y,s.z))
print("FLAT_TOTAL", len(flat))