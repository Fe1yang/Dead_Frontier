import bpy
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_riley_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
mesh=None; arm=None
for ob in bpy.context.scene.objects:
    if ob.type=="MESH" and ob.name=="HighDetailCharacter": mesh=ob
    if ob.type=="ARMATURE": arm=ob
for name in ["hand_l","index_01_l","thumb_01_l"]:
    b=arm.pose.bones.get(name)
    print(name,"head",list(b.head))
    ds=sorted([((v.co-b.head).length, list(v.co)) for v in mesh.data.vertices])[:3]
    for d,co in ds:
        print("  nearest",round(d,4),[round(x,3) for x in co])
print("DONE")
