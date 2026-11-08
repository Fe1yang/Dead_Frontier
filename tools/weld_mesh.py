"""Close the open seams in a Tripo character mesh before rigging.

The Tatical-female mesh arrives as ~1900 separate shells with 39k open boundary edges, so any
pose that pulls a seam apart shows a black crack. Merge coincident vertices and fill the small
remaining holes; big openings (neck, cuffs) are left alone.

Run: blender -b -P weld_mesh.py -- <glb_in> <glb_out> [merge_distance]
"""
import bpy, bmesh, os, sys

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SRC, OUT = argv[0], argv[1]
DIST = float(argv[2]) if len(argv) > 2 else 0.004

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.name.startswith("Icosphere")]
for o in list(bpy.context.scene.objects):
    if o.type == "ARMATURE":
        bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

bm = bmesh.new()
bm.from_mesh(body.data)
before_v = len(bm.verts)
before_b = len([e for e in bm.edges if len(e.link_faces) < 2])
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=DIST)
after_b = len([e for e in bm.edges if len(e.link_faces) < 2])

# fill only the little holes: walk closed boundary loops and cap the short ones
seen = set()
filled = 0
for e in [x for x in bm.edges if len(x.link_faces) < 2]:
    if e in seen:
        continue
    loop = [e]
    seen.add(e)
    stack = [e]
    while stack:
        cur = stack.pop()
        for v in cur.verts:
            for ne in v.link_edges:
                if len(ne.link_faces) < 2 and ne not in seen:
                    seen.add(ne)
                    stack.append(ne)
                    loop.append(ne)
    length = sum(x.calc_length() for x in loop)
    if length < 0.05 and len(loop) > 2:
        try:
            bmesh.ops.holes_fill(bm, edges=loop, sides=0)
            filled += 1
        except Exception:
            pass

after_b2 = len([x for x in bm.edges if len(x.link_faces) < 2])
bm.to_mesh(body.data)
body.data.update()
bm.free()
print("WELD verts %d -> %d" % (before_v, len(body.data.vertices)))
print("BOUNDARY %d -> %d -> %d  (filled loops %d)" % (before_b, after_b, after_b2, filled))

bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True,
                          export_animations=False, export_apply=False)
print("WROTE", OUT, os.path.getsize(OUT))
