import bpy, sys
from mathutils import Vector
p=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\actors\survivor_jian_scout_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=p)
arm=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"][0]
body=[o for o in bpy.context.scene.objects if o.type=="MESH"][0]
def seg(p0,a,b):
    ab=b-a
    t=max(0.0,min(1.0,(p0-a).dot(ab)/max(ab.length_squared,1e-9)))
    return (p0-(a+ab*t)).length
for name in ("hand_r","lowerarm_r","hand_l"):
    b=arm.data.bones.get(name)
    if not b: continue
    a=b.head_local; t=b.tail_local
    best=(1e9,None)
    for v in body.data.vertices:
        d=seg(v.co,a,t)
        if d<best[0]: best=(d,v.co.copy())
    print("%s head=(%.3f,%.3f,%.3f) closest_vertex=%.3f m at (%.2f,%.2f,%.2f)" % (name,a.x,a.y,a.z,best[0],best[1].x,best[1].y,best[1].z))
print("CHECK_DONE")
