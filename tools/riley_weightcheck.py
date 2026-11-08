import bpy, os
from mathutils import Vector
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
LIB=os.path.join(ROOT,"assets","animation-library","ual1","UAL1_Standard.glb")
MESH=os.path.join(ROOT,"assets","models","generated","survivor_riley_hd.glb")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=LIB)
arm=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"][0]
for o in list(bpy.context.scene.objects):
    if o.type=="MESH": bpy.data.objects.remove(o, do_unlink=True)
before=set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=MESH)
body=[o for o in bpy.context.scene.objects if o not in before and o.type=="MESH"][0]
bpy.context.view_layer.update()
box=[body.matrix_world @ Vector(c) for c in body.bound_box]
lo=Vector((min(v.x for v in box),min(v.y for v in box),min(v.z for v in box)))
hi=Vector((max(v.x for v in box),max(v.y for v in box),max(v.z for v in box)))
sc=1.78/max(hi.z-lo.z,0.01)
body.scale=body.scale*sc
bpy.context.view_layer.update()
box=[body.matrix_world @ Vector(c) for c in body.bound_box]
lo=Vector((min(v.x for v in box),min(v.y for v in box),min(v.z for v in box)))
hi=Vector((max(v.x for v in box),max(v.y for v in box),max(v.z for v in box)))
body.location.x-=(lo.x+hi.x)*0.5; body.location.y-=(lo.y+hi.y)*0.5; body.location.z-=lo.z
bpy.ops.object.select_all(action="DESELECT"); body.select_set(True)
bpy.context.view_layer.objects.active=body
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active=arm
print("BEFORE groups:", len(body.vertex_groups))
bpy.ops.object.parent_set(type="ARMATURE_AUTO")
print("AFTER groups:", len(body.vertex_groups))
weighted=0; total=len(body.data.vertices)
maxw=0.0
for v in body.data.vertices:
    if v.groups:
        weighted+=1
        maxw=max(maxw, sum(g.weight for g in v.groups))
print("VERTICES", total, "with groups:", weighted, "max weight sum:", round(maxw,3))
print("modifiers:", [(m.type, getattr(m,'object',None).name if getattr(m,'object',None) else None) for m in body.modifiers])
print("WEIGHTCHECK_DONE")