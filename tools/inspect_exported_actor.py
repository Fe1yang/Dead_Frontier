import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets'/'models'/'actors'/'survivor_male_universal.glb'))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
print('ACTIONS',[(a.name,tuple(a.frame_range)) for a in bpy.data.actions])
for action_name in ['Run_Gun_Loop','Pistol_Aim_Neutral']:
    action=bpy.data.actions[action_name]
    rig.animation_data.action=action
    if action.slots: rig.animation_data.action_slot=action.slots[0]
    bpy.context.scene.frame_set(9)
    bpy.context.view_layer.update()
    print('EXPORTED_POSE',action_name)
    for name in ['upperarm_l','lowerarm_l','hand_l','upperarm_r','lowerarm_r','hand_r']:
        print(name,'head',tuple(round(v,4) for v in rig.pose.bones[name].head),'basis',tuple(round(v,4) for row in rig.pose.bones[name].matrix_basis for v in row))
