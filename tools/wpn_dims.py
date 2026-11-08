import bpy, os
from mathutils import Vector
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
for name,rel in (("smg","assets/models/weapons/smg.glb"),("rifle","assets/models/rifle.glb")):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT,rel.replace("/",os.sep)))
    lo=Vector((1e9,1e9,1e9)); hi=Vector((-1e9,-1e9,-1e9))
    for m in [o for o in bpy.context.scene.objects if o.type=="MESH"]:
        for c in m.bound_box:
            p=m.matrix_world @ Vector(c)
            lo=Vector((min(lo.x,p.x),min(lo.y,p.y),min(lo.z,p.z)))
            hi=Vector((max(hi.x,p.x),max(hi.y,p.y),max(hi.z,p.z)))
    print(name, "size", tuple(round(v,2) for v in (hi-lo)))