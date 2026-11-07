import bpy, mathutils
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_riley_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
mesh=None
for ob in bpy.context.scene.objects:
    if ob.type=="MESH" and ob.name=="HighDetailCharacter":
        mesh=ob; break
print("mesh transforms", mesh.matrix_world.translation, mesh.matrix_world.to_scale())
# count per finger group via vertex_groups find
for side in ["l","r"]:
    for finger in ["index","middle","ring","pinky"]:
        for ph in [1,2,3]:
            gn=f"{finger}_{ph:02d}_{side}"
            g=mesh.vertex_groups.find(gn)
            if g is None: print("MISSING",gn)
            else:
                # count verts with this group
                cnt=sum(1 for v in mesh.data.vertices if any(vg.group==g.index for vg in v.groups))
                print(gn, "count", cnt)
print("DONE")
