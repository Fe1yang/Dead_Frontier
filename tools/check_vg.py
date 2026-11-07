import bpy
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_riley_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
for ob in bpy.context.scene.objects:
    if ob.type=="MESH":
        v=ob.data.vertices[0]
        print("v.groups[0] type", type(v.groups[0]), v.groups[0])
        print("dir", dir(v.groups[0])[:20])
        print("first group index", ob.vertex_groups[0], ob.vertex_groups[0].index)
        break
print("DONE")
