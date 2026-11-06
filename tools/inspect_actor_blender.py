import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LIBRARY=ROOT/'assets'/'animations'/'universal'/'Universal Animation Library[Standard]'/'Unreal-Godot'/'UAL1_Standard.glb'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(LIBRARY))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
for action_name in ['Pistol_Aim_Neutral','Pistol_Reload','Walk_Loop']:
    action=bpy.data.actions[action_name]
    rig.animation_data.action=action
    bpy.context.scene.frame_set(int(action.frame_range[1]))
    bpy.context.view_layer.update()
    print('\nPOSE',action_name,'frame',bpy.context.scene.frame_current)
    for name in ['spine_03','clavicle_l','upperarm_l','lowerarm_l','hand_l','middle_01_l','clavicle_r','upperarm_r','lowerarm_r','hand_r','middle_01_r']:
        pb=rig.pose.bones[name]
        print(name,'head',tuple(round(v,4) for v in pb.head),'tail',tuple(round(v,4) for v in pb.tail),'length',round(pb.length,4))
print('REST')
for name in ['upperarm_l','lowerarm_l','hand_l','upperarm_r','lowerarm_r','hand_r']:
    b=rig.data.bones[name]
    print(name,'head',tuple(round(v,4) for v in b.head_local),'tail',tuple(round(v,4) for v in b.tail_local))
