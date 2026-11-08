import bpy, os
from mathutils import Vector
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
LIB=os.path.join(ROOT,"assets","animation-library","ual1","UAL1_Standard.glb")
MESH=os.path.join(ROOT,"assets","models","generated","survivor_riley_hd.glb")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=LIB)
arm=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"][0]
print("ARM_WORLD scale", tuple(round(v,4) for v in arm.matrix_world.to_scale()), "loc", tuple(round(v,3) for v in arm.matrix_world.translation))
for n in ("upperarm_l","lowerarm_l","hand_l","thigh_l","foot_l"):
    if n in arm.data.bones:
        b=arm.data.bones[n]
        print("BONE", n, "head_local", tuple(round(v,3) for v in b.head_local), "world", tuple(round(v,3) for v in (arm.matrix_world @ b.head_local)))
for o in list(bpy.context.scene.objects):
    if o.type=="MESH":
        b=[o.matrix_world @ Vector(c) for c in o.bound_box]
        print("LIB_MESH", o.name, "size", tuple(round(v,3) for v in (Vector((max(p.x for p in b),max(p.y for p in b),max(p.z for p in b)))-Vector((min(p.x for p in b),min(p.y for p in b),min(p.z for p in b))))))
print("DONE")