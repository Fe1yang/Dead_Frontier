import bpy
for label,glb in [("RILEY",r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_riley_universal.glb"),("MASON",r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_male_universal.glb")]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=glb)
    mesh=None; arm=None
    for ob in bpy.context.scene.objects:
        if ob.type=="MESH" and "HighDetail" in ob.name or (ob.type=="MESH" and ob.name.startswith("mesh")): mesh=ob
        if ob.type=="ARMATURE": arm=ob
    print(label,"mesh",mesh.name,"arm",arm.name)
    print(" mesh matrix", list(mesh.matrix_world.translation), list(mesh.matrix_world.to_scale()))
    if arm:
        b=arm.pose.bones.get("index_01_l")
        print(" index head",list(b.head))
    # nearest mesh vert to index head
    import mathutils
    if arm:
        piv=b.head.copy()
        ds=sorted([(v.co-piv).length for v in mesh.data.vertices])[:5]
        print(" nearest dists",[round(x,4) for x in ds])
    print()
print("DONE")
