import bpy
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_riley_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
for ob in bpy.context.scene.objects:
    if ob.type=="MESH" and ob.name=="HighDetailCharacter":
        print("groups:", [g.name for g in ob.vertex_groups][:80])
        # count verts per finger group
        for g in ob.vertex_groups:
            if "index" in g.name or "middle" in g.name or g.name.startswith("hand") or g.name.startswith("thumb"):
                print(g.name)
                break
print("DONE")
