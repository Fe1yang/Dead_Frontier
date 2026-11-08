import bpy, os
from mathutils import Vector
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
SRC=os.path.join(ROOT,"assets","models","actors","survivor_riley_universal.glb")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
body=[o for o in bpy.context.scene.objects if o.type=="MESH"][0]
arm=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"][0]

def seg_dist(p,a,b):
    ab=b-a
    t=max(0.0,min(1.0,(p-a).dot(ab)/max(ab.length_squared,1e-9)))
    return (p-(a+ab*t)).length

segs={b.name:(b.head_local.copy(),b.tail_local.copy()) for b in arm.data.bones if b.name!="root"}
name_of={body.vertex_groups[i].index:body.vertex_groups[i].name for i in range(len(body.vertex_groups))}
outliers=[]
for v in body.data.vertices:
    g=max(v.groups,key=lambda g:g.weight)
    bn=name_of.get(g.group,"")
    if bn not in segs: continue
    d=seg_dist(v.co,*segs[bn])
    if d>0.15:
        outliers.append((v.index,d,bn))
print("OUTLIERS", len(outliers))
from collections import Counter
print("by bone", Counter(o[2] for o in outliers).most_common(6))
fixed=0
for idx,d,bn in outliers:
    v=body.data.vertices[idx]
    best=min(((seg_dist(v.co,a,b),n) for n,(a,b) in segs.items()))
    if best[0]>=d: continue
    for g in list(v.groups):
        body.vertex_groups[g.group].remove([idx])
    body.vertex_groups[best[1]].add([idx],1.0,"REPLACE")
    fixed+=1
print("REWEIGHTED", fixed)
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True); arm.select_set(True)
bpy.context.view_layer.objects.active=arm
bpy.ops.export_scene.gltf(filepath=SRC, export_format="GLB", use_selection=True,
    export_animations=True, export_animation_mode="ACTIONS", export_force_sampling=False, export_apply=False)
print("WROTE", os.path.getsize(SRC))