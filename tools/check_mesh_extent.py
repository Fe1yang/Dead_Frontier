import bpy
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_riley_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
for ob in bpy.context.scene.objects:
    if ob.type=="MESH" and ob.name=="HighDetailCharacter":
        mesh=ob
        xs=[v.co.x for v in mesh.data.vertices]
        print("mesh x min",min(xs),"max",max(xs))
        # verts with x>0.7
        hi=[list(v.co) for v in mesh.data.vertices if v.co.x>0.7]
        print("x>0.7 count",len(hi),"sample",hi[:3])
print("DONE")
