import bpy
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
results={}
for name in ['survivor_male_universal.glb','survivor_jian_scout_universal.glb']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/models/actors'/name))
    arm = next(o for o in bpy.data.objects if o.type=='ARMATURE')
    act = bpy.data.actions.get('Run_Gun_Loop')
    arm.animation_data_create(); arm.animation_data.action = act
    if act.slots: arm.animation_data.action_slot = act.slots[0]
    bpy.context.scene.frame_set(16)
    bpy.context.view_layer.update()
    pos={}
    for bn in ['hand_l','hand_r','lowerarm_l','lowerarm_r','Head']:
        pb = arm.pose.bones.get(bn)
        w = arm.matrix_world @ pb.matrix.translation
        pos[bn]=tuple(round(v,3) for v in w)
    results[name]=pos
    print(name, pos)
