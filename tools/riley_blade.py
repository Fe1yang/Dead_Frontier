import bpy, os, math
from mathutils import Vector
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
MESH=os.path.join(ROOT,"assets","models","generated","survivor_riley_hd.glb")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=MESH)
bpy.context.view_layer.update()
meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0]
if len(meshes)>1: bpy.ops.object.join()
body=bpy.context.view_layer.objects.active
bpy.context.view_layer.update()
box=[body.matrix_world @ Vector(c) for c in body.bound_box]
lo=Vector((min(v.x for v in box),min(v.y for v in box),min(v.z for v in box)))
hi=Vector((max(v.x for v in box),max(v.y for v in box),max(v.z for v in box)))
print("BODY", tuple(round(v,1) for v in lo), tuple(round(v,1) for v in hi))
# split a duplicate into islands and delete flat, blade-like ones near the right hand
dup=body.copy(); dup.data=body.data.copy(); bpy.context.collection.objects.link(dup)
bpy.ops.object.select_all(action="DESELECT"); dup.select_set(True); bpy.context.view_layer.objects.active=dup
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.separate(type="LOOSE"); bpy.ops.object.mode_set(mode="OBJECT")
parts=[o for o in bpy.context.scene.objects if o.type=="MESH" and o.name!=body.name]
cand=[]
for o in parts:
    b=[o.matrix_world @ Vector(c) for c in o.bound_box]
    l=Vector((min(v.x for v in b),min(v.y for v in b),min(v.z for v in b)))
    h=Vector((max(v.x for v in b),max(v.y for v in b),max(v.z for v in b)))
    s=h-l; c=(l+h)*0.5
    mx=max(s.x,s.y,s.z); mn=min(s.x,s.y,s.z)
    if mx>8 and mn/max(mx,1e-6)<0.22 and abs(c.x)>4 and 15<c.z<70:
        cand.append((o,c,s,len(o.data.vertices)))
print("CANDIDATES", len(cand))
for o,c,s,n in sorted(cand,key=lambda t:-max(t[2].x,t[2].y,t[2].z))[:12]:
    print("  %-30s verts=%4d centre=(%.1f,%.1f,%.1f) size=(%.1f,%.1f,%.1f)" % (o.name,n,c.x,c.y,c.z,s.x,s.y,s.z))
print("CAND_DONE")