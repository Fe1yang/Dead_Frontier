import bpy
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_riley_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
mesh=None; arm=None
for ob in bpy.context.scene.objects:
    if ob.type=="MESH" and ob.name=="HighDetailCharacter": mesh=ob
    if ob.type=="ARMATURE": arm=ob
print("arm world", list(arm.matrix_world.translation), list(arm.matrix_world.to_scale()))
print("mesh world", list(mesh.matrix_world.translation), list(mesh.matrix_world.to_scale()))
bone=arm.pose.bones.get("index_01_l")
world_head = arm.matrix_world @ bone.head
print("bone head local",list(bone.head),"world",list(world_head))
# nearest mesh vert in world
import mathutils
ds=[]
for v in mesh.data.vertices:
    w = mesh.matrix_world @ v.co
    ds.append((w-world_head).length)
ds.sort()
print("nearest world dists",[round(x,4) for x in ds[:5]])
print("DONE")
