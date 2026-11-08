import bpy, bmesh, os
from mathutils import Vector
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
SRC=os.path.join(ROOT,"assets","models","actors","survivor_riley_universal.glb")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
body=[o for o in bpy.context.scene.objects if o.type=="MESH"][0]
arm=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"][0]
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
target=None
for comp in islands:
    pts=[v.co for f in comp for v in f.verts]
    lo=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    hi=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    c=(lo+hi)*0.5; s=hi-lo
    if abs(c.x-0.14)<0.05 and abs(c.z-1.29)<0.06 and s.z>0.18 and s.x<0.03 and s.y<0.09:
        target=comp; break
print("TARGET_FACES", len(target) if target else 0)
if target:
    bmesh.ops.delete(bm, geom=target, context="FACES")
    bm.to_mesh(body.data); body.data.update()
bm.free()
print("VERTS_AFTER", len(body.data.vertices))
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True); arm.select_set(True)
bpy.context.view_layer.objects.active=arm
bpy.ops.export_scene.gltf(filepath=SRC, export_format="GLB", use_selection=True,
    export_animations=True, export_animation_mode="ACTIONS", export_force_sampling=False, export_apply=False)
print("WROTE", SRC, os.path.getsize(SRC))