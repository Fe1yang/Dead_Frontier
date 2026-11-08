"""Weld coincident vertices that also share the same UV, keeping the original textures.

The Tripo mesh is many shells whose vertices sit at the same spot but on different UV islands.
Merging all of them would need a texture re-bake (which came out blank last time), so this
merges only the pairs whose UVs are identical: the surface becomes continuous there and the
texture stays exactly as authored.

Run: blender -b -P weld_same_uv.py -- <glb_in> <glb_out> [tolerance]
"""
import bpy, bmesh, os, sys

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SRC, OUT = argv[0], argv[1]
TOL = float(argv[2]) if len(argv) > 2 else 0.004

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
bm.verts.ensure_lookup_table()
uv_layer = bm.loops.layers.uv.active
before_v = len(bm.verts)
before_b = len([e for e in bm.edges if len(e.link_faces) < 2])


def uv_signature(v):
    if uv_layer is None:
        return ()
    sig = set()
    for loop in v.link_loops:
        uv = loop[uv_layer].uv
        sig.add((round(uv.x, 4), round(uv.y, 4)))
    return tuple(sorted(sig))


buckets = {}
for v in bm.verts:
    key = (round(v.co.x / TOL), round(v.co.y / TOL), round(v.co.z / TOL))
    buckets.setdefault(key, []).append(v)

targetmap = {}
for key, verts in buckets.items():
    if len(verts) < 2:
        continue
    for i in range(len(verts)):
        for j in range(i + 1, len(verts)):
            a, b = verts[i], verts[j]
            if b in targetmap:
                continue
            if (a.co - b.co).length > TOL:
                continue
            if uv_signature(a) != uv_signature(b):
                continue
            targetmap[b] = a

if targetmap:
    bmesh.ops.weld_verts(bm, targetmap=targetmap)
bm.verts.ensure_lookup_table()
after_b = len([e for e in bm.edges if len(e.link_faces) < 2])
bm.to_mesh(body.data)
body.data.update()
bm.free()
print("WELD_UV verts %d -> %d  merged %d" % (before_v, len(body.data.vertices), len(targetmap)))
print("BOUNDARY %d -> %d" % (before_b, after_b))

bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True,
                          export_animations=False, export_apply=False)
print("WROTE", OUT, os.path.getsize(OUT))
