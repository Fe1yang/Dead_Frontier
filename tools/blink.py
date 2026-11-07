import bpy
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_riley_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
for ob in bpy.context.scene.objects:
    if ob.type == "ARMATURE":
        for b in ob.data.bones:
            if "Eye" in b.name or "eye" in b.name:
                print("eye bone", b.name)
print("done")
