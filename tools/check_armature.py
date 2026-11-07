import bpy, mathutils
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_riley_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
for ob in bpy.context.scene.objects:
    if ob.type=="MESH":
        print(ob.name, "mods", [(m.type, m.show_viewport) for m in ob.modifiers])
    if ob.type=="ARMATURE":
        print("arm", ob.name)
print("DONE")
