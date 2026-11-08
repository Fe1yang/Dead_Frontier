import bpy, os
from mathutils import Vector
NEW=r"C:\Users\user\Downloads\tactical female character 3d model (1).glb"
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=NEW)
bpy.context.view_layer.update()
for o in bpy.context.scene.objects:
    print("OBJ", o.name, o.type, "parent", o.parent.name if o.parent else None)
arm=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"][0]
print("ARM", arm.name, "scale", tuple(round(v,3) for v in arm.matrix_world.to_scale()))
for n in ("pelvis","spine_01","head","clavicle_l","upperarm_l","lowerarm_l","hand_l","clavicle_r","upperarm_r","lowerarm_r","hand_r","thigh_l","calf_l","foot_l"):
    if n in arm.data.bones:
        b=arm.data.bones[n]
        print("BONE %-12s head=(%.3f,%.3f,%.3f) tail=(%.3f,%.3f,%.3f)" % (n, *b.head_local, *b.tail_local))
body=[o for o in bpy.context.scene.objects if o.type=="MESH"][0]
b=[body.matrix_world @ Vector(c) for c in body.bound_box]
lo=Vector((min(p.x for p in b),min(p.y for p in b),min(p.z for p in b)))
hi=Vector((max(p.x for p in b),max(p.y for p in b),max(p.z for p in b)))
print("MESH_BOX", tuple(round(v,3) for v in lo), tuple(round(v,3) for v in hi))
print("VGROUPS", len(body.vertex_groups))