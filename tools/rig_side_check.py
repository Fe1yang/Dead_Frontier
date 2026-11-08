import bpy
from mathutils import Vector
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ROOT+r"\assets\animation-library\ual1\UAL1_Standard.glb")
arm=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"][0]
for n in ("upperarm_l","upperarm_r","hand_l","hand_r"):
    b=arm.data.bones[n]
    print(n, "head", tuple(round(v,2) for v in b.head_local), "tail", tuple(round(v,2) for v in b.tail_local))