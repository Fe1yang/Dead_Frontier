import bpy, bmesh, os
from mathutils import Vector
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
SRC=os.path.join(ROOT,"assets","models","actors","survivor_riley_universal.glb")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
body=[o for o in bpy.context.scene.objects if o.type=="MESH"][0]
bm=bmesh.new(); bm.from_mesh(body.data); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
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
cands=[]
for comp in islands:
    pts=[v.co for f in comp for v in f.verts]
    lo=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    hi=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    c=(lo+hi)*0.5; s=hi-lo
    dims=sorted([s.x,s.y,s.z])
    if c.z>1.15 and dims[0]<0.03 and 0.06<dims[2]<0.45 and len(comp)>=8:
        cands.append((c,s,len(comp),comp))
cands.sort(key=lambda t:-t[1].z)
COLOURS=[(1,0,0),(0,1,0),(0,0.3,1),(1,1,0),(1,0,1),(0,1,1)]
# map face index -> colour
face_colour={}
legend=[]
for i,(c,s,n,comp) in enumerate(cands[:6]):
    col=COLOURS[i]
    for f in comp:
        face_colour[f.index]=col
    legend.append((i,col,c,s,n))
for x in legend:
    print("CAND %d colour=%s centre=(%.2f,%.2f,%.2f) size=(%.3f,%.3f,%.3f) faces=%d" % (x[0],str(x[1]),x[2].x,x[2].y,x[2].z,x[3].x,x[3].y,x[3].z,x[4]))
bm.to_mesh(body.data); bm.free()

# vertex colours per face
me=body.data
attr=me.color_attributes.new(name="cand", type="BYTE_COLOR", domain="CORNER")
for poly in me.polygons:
    col=face_colour.get(poly.index,(0.6,0.6,0.6,1.0))
    if len(col)==3: col=(col[0],col[1],col[2],1.0)
    for li in poly.loop_indices:
        attr.data[li].color=col
mat=bpy.data.materials.new("candmat"); mat.use_nodes=True
bsdf=mat.node_tree.nodes["Principled BSDF"]
vcol=mat.node_tree.nodes.new("ShaderNodeVertexColor"); vcol.layer_name="cand"
mat.node_tree.links.new(vcol.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Emission Color"].default_value=(0,0,0,1)
bsdf.inputs["Roughness"].default_value=0.5
body.data.materials.clear(); body.data.materials.append(mat)
for p in me.polygons:
    p.material_index=0

# render head + shoulders, front
sc=bpy.context.scene
sc.render.engine="BLENDER_EEVEE"; sc.render.resolution_x=700; sc.render.resolution_y=700
sc.render.film_transparent=False
w=bpy.data.worlds.new("W"); sc.world=w; w.use_nodes=True
w.node_tree.nodes["Background"].inputs[0].default_value=(0.35,0.38,0.42,1)
w.node_tree.nodes["Background"].inputs[1].default_value=1.0
L=bpy.data.objects.new("k",bpy.data.lights.new("k",type="AREA")); L.data.energy=500; L.data.size=3
L.location=(1.5,-2.2,2.0); L.rotation_euler=(Vector((0,0,1.4))-Vector(L.location)).to_track_quat("-Z","Y").to_euler()
sc.collection.objects.link(L)
cd=bpy.data.cameras.new("c"); cd.type="ORTHO"; cd.ortho_scale=0.85
cam=bpy.data.objects.new("c",cd); sc.collection.objects.link(cam); sc.camera=cam
cam.location=Vector((0,-3,1.45)); cam.rotation_euler=(Vector((0,0,1.42))-cam.location).to_track_quat("-Z","Y").to_euler()
sc.render.filepath=os.path.join(ROOT,"assets","models","actors","riley_candidates.png")
bpy.ops.render.render(write_still=True)
print("RENDERED")