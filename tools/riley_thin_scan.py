import bpy, bmesh, os
from mathutils import Vector
SRC=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\actors\survivor_riley_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
body=[o for o in bpy.context.scene.objects if o.type=="MESH"][0]
me=body.data
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
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
rows=[]
for comp in islands:
    pts=[v.co for f in comp for v in f.verts]
    lo=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    hi=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    s=sorted([hi.x-lo.x,hi.y-lo.y,hi.z-lo.z]); cz=(lo.z+hi.z)*0.5
    if s[0]<0.02 and s[2]>0.05:
        rows.append((s,cz,len(comp),round((lo.x+hi.x)/2,2)))
rows.sort(key=lambda r:-r[0][2])
for s,cz,n,cx in rows[:10]:
    print("  THIN size=(%.3f,%.3f,%.3f) cz=%.2f cx=%.2f faces=%d" % (s[0],s[1],s[2],cz,cx,n))
print("THIN_TOTAL", len(rows))