import bpy, os
from mathutils import Vector
NEW=r"C:\Users\user\Downloads\female mechanic 3d model (1).glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=NEW)
bpy.context.view_layer.update()
for o in bpy.context.scene.objects:
    print("OBJ", o.name, o.type)
arm=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"]
body=[o for o in bpy.context.scene.objects if o.type=="MESH"]
print("ARMATURES", [a.name for a in arm], "MESHES", [(b.name, len(b.vertex_groups)) for b in body])
if arm:
    a=arm[0]
    names=[b.name for b in a.data.bones]
    print("BONES", len(names), names[:24])
print("DONE")