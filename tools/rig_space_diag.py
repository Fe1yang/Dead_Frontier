import bpy, math
from mathutils import Vector
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ROOT+r"\assets\animation-library\ual1\UAL1_Standard.glb")
arm=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"][0]
for o in list(bpy.context.scene.objects):
    if o.type=="MESH": bpy.data.objects.remove(o, do_unlink=True)
b=set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=ROOT+r"\assets\models\generated\survivor_riley_hd.glb")
new=[o for o in bpy.context.scene.objects if o not in b and o.type=="MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in new: o.select_set(True)
bpy.context.view_layer.objects.active=new[0]
if len(new)>1: bpy.ops.object.join()
body=bpy.context.view_layer.objects.active
bpy.ops.object.select_all(action="SELECT")
bpy.context.view_layer.objects.active=arm
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
box=[body.matrix_world @ Vector(c) for c in body.bound_box]
lo=Vector((min(p.x for p in box),min(p.y for p in box),min(p.z for p in box)))
hi=Vector((max(p.x for p in box),max(p.y for p in box),max(p.z for p in box)))
factor=1.72/max(hi.z-lo.z,0.01)
for o in (arm,body): o.scale=o.scale*factor
bpy.ops.object.select_all(action="SELECT"); bpy.context.view_layer.objects.active=arm
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.context.view_layer.update()
print("ARM matrix scale", tuple(round(v,3) for v in arm.matrix_world.to_scale()), "loc", tuple(round(v,2) for v in arm.matrix_world.translation))
print("BODY matrix", tuple(round(v,3) for v in body.matrix_world.to_scale()), "loc", tuple(round(v,2) for v in body.matrix_world.translation))
box=[body.matrix_world @ Vector(c) for c in body.bound_box]
lo=Vector((min(p.x for p in box),min(p.y for p in box),min(p.z for p in box)))
hi=Vector((max(p.x for p in box),max(p.y for p in box),max(p.z for p in box)))
print("BODY_BOX", tuple(round(v,2) for v in lo), tuple(round(v,2) for v in hi))
for n in ("upperarm_r","hand_r"):
    bb=arm.data.bones[n]
    print(n,"head_local",tuple(round(v,2) for v in bb.head_local),"world",tuple(round(v,2) for v in (arm.matrix_world @ bb.head_local)))