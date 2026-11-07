import bpy
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_riley_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
mesh=None; arm=None
for ob in bpy.context.scene.objects:
    if ob.type=="MESH" and ob.name=="HighDetailCharacter": mesh=ob
    if ob.type=="ARMATURE": arm=ob
bone=arm.pose.bones.get("index_01_l")
piv=bone.head.copy()
ds=sorted([((v.co-piv).length, list(v.co)) for v in mesh.data.vertices])[:5]
for d,co in ds:
    print(round(d,4),[round(x,3) for x in co])
# also print vertex groups of that nearest vert
vmin=min(mesh.data.vertices, key=lambda v:(v.co-piv).length)
print("nearest vert groups", [(g.name, g.weight) for g in vmin.groups] if hasattr(g:=mesh.vertex_groups, '__len__') else "n/a")
for vg in vmin.groups:
    print(" group idx", vg.group, mesh.vertex_groups[vg.group].name, round(vg.weight,3))
print("DONE")
