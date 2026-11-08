"""Average the skin weights of coincident vertices across separate shells.

The Tripo characters are exported as many shells (body, vest, straps, hair) that share vertex
positions but not topology, so glTF keeps them as duplicated vertices. If the duplicates end
up weighted to different bones the shells pull apart and a black crack opens. Averaging the
weights of vertices that sit at the same point keeps the shells moving together without
touching a single vertex position.

Run: blender -b -P sync_weights.py -- <glb> [tolerance]
"""
import bpy, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
PATH = argv[0]
TOL = float(argv[1]) if len(argv) > 1 else 0.004

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=PATH)
arm = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"][0]
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()
body = bpy.context.view_layer.objects.active

names = {i: body.vertex_groups[i].name for i in range(len(body.vertex_groups))}
cell = max(TOL, 0.001)
buckets = {}
for v in body.data.vertices:
    key = (round(v.co.x / cell), round(v.co.y / cell), round(v.co.z / cell))
    buckets.setdefault(key, []).append(v.index)

pairs = 0
changes = 0
for key, ids in buckets.items():
    if len(ids) < 2:
        continue
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a = body.data.vertices[ids[i]]
            b = body.data.vertices[ids[j]]
            if (a.co - b.co).length > TOL:
                continue
            pairs += 1
            wa = {names[g.group]: g.weight for g in a.groups}
            wb = {names[g.group]: g.weight for g in b.groups}
            merged = {}
            for k in set(wa) | set(wb):
                merged[k] = (wa.get(k, 0.0) + wb.get(k, 0.0)) * 0.5
            total = sum(merged.values())
            if total <= 1e-5:
                continue
            if max(abs(wa.get(k, 0.0) - merged.get(k, 0.0)) for k in merged) < 0.02:
                continue
            for idx in (a.index, b.index):
                for g in list(body.data.vertices[idx].groups):
                    body.vertex_groups[g.group].remove([idx])
                for gname, w in merged.items():
                    if w <= 1e-4:
                        continue
                    vg = body.vertex_groups.get(gname) or body.vertex_groups.new(name=gname)
                    vg.add([idx], w / total, "REPLACE")
            changes += 1

print("COINCIDENT_PAIRS", pairs, "SYNCED", changes)

bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(
    filepath=PATH,
    export_format="GLB",
    use_selection=True,
    export_animations=True,
    export_animation_mode="ACTIONS",
    export_force_sampling=False,
    export_apply=False,
)
print("WROTE", PATH, os.path.getsize(PATH))
