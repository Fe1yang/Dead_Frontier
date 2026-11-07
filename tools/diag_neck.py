import bpy
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/models/actors/survivor_jian_universal.glb'))
arm = next(o for o in bpy.data.objects if o.type=='ARMATURE')
for n in ('spine_03','neck_01','Head','clavicle_l','clavicle_r','upperarm_l'):
    b = arm.data.bones[n]
    print('BONE', n, 'head', tuple(round(v,3) for v in b.head_local), 'tail', tuple(round(v,3) for v in b.tail_local))
