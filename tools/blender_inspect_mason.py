import bpy, sys
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_male_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
for ob in bpy.context.scene.objects:
    if ob.type=="ARMATURE":
        for bone in ob.pose.bones:
            if bone.name in ("thigh_l","thigh_r","calf_l","calf_r","foot_l","foot_r","hand_l","hand_r","lowerarm_l","lowerarm_r","clavicle_l","clavicle_r","pelvis"):
                print(f"  {bone.name}: head={tuple(round(v,3) for v in bone.head)} tail={tuple(round(v,3) for v in bone.tail)}")
print("DONE")
