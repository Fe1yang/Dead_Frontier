import bpy
for label,glb in [("JIAN",r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_jian_scout_universal.glb"),("MASON",r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_male_universal.glb\left")]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=glb)
    for ob in bpy.context.scene.objects:
        if ob.type=="ARMATURE":
            for name in ["foot_l","ball_l","foot_r","ball_r","upperarm_r","upperarm_l"]:
                b=ob.pose.bones.get(name)
                if b:
                    print(label, name, "head", list(b.head), "tail", list(b.tail))
            print("---")
print("DONE")
