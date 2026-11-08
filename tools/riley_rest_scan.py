import bpy, bmesh, os
from mathutils import Vector
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
SRC=os.path.join(ROOT,"assets","models","actors","survivor_riley_universal.glb")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
body=[o for o in bpy.context.scene.objects if o.type=="MESH"][0]
arm=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"][0]
arm.data.pose_position="REST"
bpy.context.view_layer.update()
bm=bmesh.new(); bm.from_mesh(body.data); bm.faces.ensure_lookup_table()
seen=set(); islands=[]
for f in bm.faces:
    if f.index in seen: continue
    stack=[f]; comp=[]; seen.add(f.index)
    while stack:
        cur=stack.pop(); comp.append(cur)
        for e in cur.edges:
            for nf in e.link_faces:
                if nf.index not in seen:
                    seen.add(nf.index); stack.append(nf)
    islands.append(comp)
print("ISLANDS", len(islands))
cands=[]
for comp in islands:
    pts=[v.co for f in comp for v in f.verts]
    lo=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    hi=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    c=(lo+hi)*0.5; s=hi-lo; dims=sorted([s.x,s.y,s.z])
    if c.z>1.45 and dims[0]<0.02 and dims[2]>0.08:
        cands.append((c,s,len(comp),comp))
cands.sort(key=lambda t:-t[1].z)
for c,s,n,comp in cands[:8]:
    print("REST_CAND centre=(%.2f,%.2f,%.2f) size=(%.3f,%.3f,%.3f) faces=%d" % (c.x,c.y,c.z,s.x,s.y,s.z,n))
print("REST_CAND_TOTAL", len(cands))
bm.free()