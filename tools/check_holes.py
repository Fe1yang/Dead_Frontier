import bpy, bmesh
from mathutils import Vector
p=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\actors\survivor_jian_scout_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=p)
body=[o for o in bpy.context.scene.objects if o.type=="MESH"][0]
bm=bmesh.new(); bm.from_mesh(body.data); bm.edges.ensure_lookup_table()
boundary=[e for e in bm.edges if len(e.link_faces)<2]
print("VERTS", len(bm.verts), "BOUNDARY_EDGES", len(boundary))
# group boundary edges into loops by walking
used=set(); loops=[]
for e in boundary:
    if e.index in used: continue
    stack=[e]; used.add(e.index); count=0; mn=Vector((1e9,1e9,1e9)); mx=Vector((-1e9,-1e9,-1e9))
    while stack:
        cur=stack.pop(); count+=1
        for v in cur.verts:
            for ne in v.link_edges:
                if ne in boundary and ne.index not in used:
                    used.add(ne.index); stack.append(ne)
            mn=Vector((min(mn.x,v.co.x),min(mn.y,v.co.y),min(mn.z,v.co.z)))
            mx=Vector((max(mx.x,v.co.x),max(mx.y,v.co.y),max(mx.z,v.co.z)))
    loops.append((count,(mx-mn).length))
loops.sort(key=lambda t:-t[0])
print("LOOPS", len(loops), "largest:", loops[:5])
print("HOLES_DONE")
