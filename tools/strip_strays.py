"""Delete thin stray slivers without splitting the mesh.

bmesh island scan: build connected components, measure each one's bbox, and delete only the
faces of components that are a thin strand (thinnest side < 12 mm, length 8..50 cm) and sit
near the head or shoulders. No separate/re-join, so the body mesh is never rebuilt.

Run: blender -b -P strip_strays.py -- <glb_in> <glb_out> [--dry]
"""
import bpy, bmesh, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SRC, OUT = argv[0], argv[1]
DRY = "--dry" in argv

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
objs = [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.name.startswith("Icosphere")]
bpy.ops.object.select_all(action="DESELECT")
for o in objs:
    o.select_set(True)
bpy.context.view_layer.objects.active = objs[0]
if len(objs) > 1:
    bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

me = body.data
bm = bmesh.new()
bm.from_mesh(me)
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()

seen = set()
islands = []
for f in bm.faces:
    if f.index in seen:
        continue
    stack = [f]
    comp = []
    seen.add(f.index)
    while stack:
        cur = stack.pop()
        comp.append(cur)
        for e in cur.edges:
            for nf in e.link_faces:
                if nf.index not in seen:
                    seen.add(nf.index)
                    stack.append(nf)
    islands.append(comp)

print("ISLANDS", len(islands))
kill_faces = []
for comp in islands:
    pts = [v.co for f in comp for v in f.verts]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    size = sorted([hi.x - lo.x, hi.y - lo.y, hi.z - lo.z])
    cz = (lo.z + hi.z) * 0.5
    if size[0] < 0.012 and 0.08 < size[2] < 0.50 and cz > 1.0:
        print("  STRAY size", [round(s, 3) for s in size], "centre_z", round(cz, 2), "faces", len(comp))
        kill_faces.extend(comp)

if kill_faces and not DRY:
    bmesh.ops.delete(bm, geom=kill_faces, context="FACES")
print("STRAYS", len(kill_faces), "faces" if not DRY else "faces (dry run)")

if not DRY:
    bm.to_mesh(me)
    me.update()
    bm.free()
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.export_scene.gltf(
        filepath=OUT,
        export_format="GLB",
        use_selection=True,
        export_animations=False,
        export_apply=False,
    )
    print("WROTE", OUT, os.path.getsize(OUT))
else:
    bm.free()
print("DONE")
