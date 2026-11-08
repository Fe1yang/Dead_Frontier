import bpy
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=r"C:\Users\user\Downloads\gray wolf 3d model.glb")
arm=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"][0]
for b in arm.data.bones:
    h=arm.matrix_world @ b.head_local
    print("BONE %-28s head=(%.2f, %.2f, %.2f) parent=%s" % (b.name, h.x, h.y, h.z, b.parent.name if b.parent else "-"))
print("WOLFBONES_DONE")
