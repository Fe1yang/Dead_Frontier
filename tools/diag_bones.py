import bpy, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
argv = sys.argv[sys.argv.index('--')+1:]
for model in argv:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/models/actors'/model))
    arm = next(o for o in bpy.data.objects if o.type=='ARMATURE')
    act = bpy.data.actions.get('Run_Gun_Loop')
    arm.animation_data_create(); arm.animation_data.action = act
    if act.slots: arm.animation_data.action_slot = act.slots[0]
    bpy.context.scene.frame_set(16); bpy.context.view_layer.update()
    row = []
    for b in ('clavicle_r','upperarm_r','lowerarm_r','hand_r','Head'):
        pb = arm.pose.bones[b]
        h = arm.matrix_world @ pb.head
        row.append('%s(%.2f,%.2f,%.2f)' % (b, h.x, h.y, h.z))
    print('BONES', model, ' '.join(row))
