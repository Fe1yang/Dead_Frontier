import bpy
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_riley_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
for ob in bpy.context.scene.objects:
    if ob.type=="MESH":
        mesh=ob
        break
for side in ["l","r"]:
    for finger in ["index","middle","ring","pinky"]:
        for ph in [1,2,3]:
            gn=f"{finger}_{ph:02d}_{side}"
            grp=mesh.vertex_groups[gn]
            cnt=sum(1 for v in mesh.data.vertices if any(elem.group==grp.index for elem in v.groups))
            print(gn, cnt)
print("DONE")
