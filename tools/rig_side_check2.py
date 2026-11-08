import bpy
from mathutils import Vector
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ROOT+r"\assets\models\generated\survivor_riley_hd.glb")
ms=[o for o in bpy.context.scene.objects if o.type=="MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in ms: o.select_set(True)
bpy.context.view_layer.objects.active=ms[0]
if len(ms)>1: bpy.ops.object.join()
b=body=bpy.context.view_layer.objects.active
box=[b.matrix_world @ Vector(c) for c in b.bound_box]
lo=Vector((min(p.x for p in box),min(p.y for p in box),min(p.z for p in box)))
hi=Vector((max(p.x for p in box),max(p.y for p in box),max(p.z for p in box)))
print("RAW_BOX", tuple(round(v,2) for v in lo), tuple(round(v,2) for v in hi))
pos=sum(1 for v in b.data.vertices if v.co.x>0.05); neg=sum(1 for v in b.data.vertices if v.co.x<-0.05)
print("VERTS pos_x", pos, "neg_x", neg, "total", len(b.data.vertices))