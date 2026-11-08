import bpy, bmesh, sys, os
from mathutils import Vector
p=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=p)
meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0]
if len(meshes)>1: bpy.ops.object.join()
body=bpy.context.view_layer.objects.active
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bm=bmesh.new(); bm.from_mesh(body.data); bm.verts.ensure_lookup_table()
boundary=len([e for e in bm.edges if len(e.link_faces)<2])
# loose parts
seen=set(); parts=0
for f0 in bm.faces:
    if f0.index in seen: continue
    parts+=1; stack=[f0]; seen.add(f0.index)
    while stack:
        cur=stack.pop()
        for e in cur.edges:
            for nf in e.link_faces:
                if nf.index not in seen:
                    seen.add(nf.index); stack.append(nf)
box=[body.matrix_world @ Vector(c) for c in body.bound_box]
h=max(v.z for v in box)-min(v.z for v in box)
print("SHELLS", parts, "VERTS", len(bm.verts), "BOUNDARY", boundary, "HEIGHT", round(h,2))
bm.free()
print("INSPECT_DONE")
