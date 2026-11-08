import bpy, os
from mathutils import Vector
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
SRC=os.path.join(ROOT,"assets","models","actors","survivor_riley_universal.glb")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
body=[o for o in bpy.context.scene.objects if o.type=="MESH"][0]
arm=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"][0]
unw=[v.index for v in body.data.vertices if not v.groups]
print("UNWEIGHTED", len(unw), "of", len(body.data.vertices))
# also list vertices whose total weight is far from 1
bad=[v.index for v in body.data.vertices if abs(sum(g.weight for g in v.groups)-1.0)>0.15]
print("BAD_SUM", len(bad))
if unw:
    names=sorted({body.vertex_groups[g.group].name for i in unw[:2000] for g in body.data.vertices[i].groups})
    print("sample groups on unweighted:", names[:5])