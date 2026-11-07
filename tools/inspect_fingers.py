import bpy
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_riley_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
for ob in bpy.context.scene.objects:
    if ob.type=="ARMATURE":
        for name in ["hand_l","index_01_l","index_02_l","index_03_l","middle_01_l","thumb_01_l","hand_r","index_01_r"]:
            b = ob.pose.bones.get(name)
            if b:
                print(name, "matrix_local", b.matrix)
                print("  head", list(b.head), "tail", list(b.tail))
                print("  local axes: X=", list(b.matrix.to_3x3().col[0]), "Y=", list(b.matrix.to_3x3().col[1]), "Z=", list(b.matrix.to_3x3().col[2]))
print("DONE")
