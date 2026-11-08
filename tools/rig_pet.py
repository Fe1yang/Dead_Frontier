"""Rig a static creature onto the DOG skeleton so it uses Dog_Idle / Dog_Run / Dog_Bite.

Run: blender -b -P rig_pet.py -- <mesh_glb> <dog_glb> <out_glb> <length_m>
"""
import bpy, os, sys
from mathutils import Vector

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
argv = sys.argv[sys.argv.index("--") + 1:]
MESH, DOG, OUT, LENGTH = argv[0], argv[1], argv[2], float(argv[3])

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=DOG)
arm = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"][0]
print("DOG_RIG bones", len(arm.data.bones), "clips", [a.name for a in bpy.data.actions])
# drop the dog body, keep the armature and its actions
for o in list(bpy.context.scene.objects):
    if o.type == "MESH":
        bpy.data.objects.remove(o, do_unlink=True)

bpy.ops.import_scene.gltf(filepath=MESH)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
for o in list(bpy.context.scene.objects):
    if o.type in ("ARMATURE", "EMPTY") and o is not arm:
        bpy.data.objects.remove(o, do_unlink=True)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.name.startswith("Icosphere")]
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
body.name = "Lion"
for g in list(body.vertex_groups):
    body.vertex_groups.remove(g)
print("MESH verts", len(body.data.vertices))

bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.remove_doubles(threshold=0.0008)
bpy.ops.object.mode_set(mode="OBJECT")
if len(body.data.vertices) > 40000:
    dec = body.modifiers.new("dec", "DECIMATE")
    dec.ratio = 40000.0 / float(len(body.data.vertices))
    bpy.ops.object.modifier_apply(modifier=dec.name)
print("FINAL verts", len(body.data.vertices))

# scale to the pet length along its longest horizontal axis, feet on the floor
box = [body.matrix_world @ Vector(c) for c in body.bound_box]
lo = Vector((min(p.x for p in box), min(p.y for p in box), min(p.z for p in box)))
hi = Vector((max(p.x for p in box), max(p.y for p in box), max(p.z for p in box)))
longest = max(hi.x - lo.x, hi.y - lo.y)
k = LENGTH / max(longest, 0.01)
body.scale = body.scale * k
bpy.context.view_layer.update()
box = [body.matrix_world @ Vector(c) for c in body.bound_box]
lo = Vector((min(p.x for p in box), min(p.y for p in box), min(p.z for p in box)))
hi = Vector((max(p.x for p in box), max(p.y for p in box), max(p.z for p in box)))
body.location.z -= lo.z
body.location.x -= (lo.x + hi.x) * 0.5
body.location.y -= (lo.y + hi.y) * 0.5
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
print("SCALED length", LENGTH, "height", round(hi.z - lo.z, 2))

segs = [(b.name, b.head_local.copy(), b.tail_local.copy()) for b in arm.data.bones]
groups = {n: body.vertex_groups.new(name=n) for n, _, _ in segs}
inv = arm.matrix_world.inverted()
for v in body.data.vertices:
    p = inv @ (body.matrix_world @ v.co)
    best_name = segs[0][0]
    best_d = 1e9
    for n, a, b in segs:
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
        d = (p - (a + ab * t)).length
        if d < best_d:
            best_d = d
            best_name = n
    groups[best_name].add([v.index], 1.0, "REPLACE")
print("WEIGHTED", len(body.data.vertices), "bones used", len(segs))

mod = body.modifiers.new("Armature", "ARMATURE")
mod.object = arm
body.parent = arm

bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
arm.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True,
                          export_animations=True, export_animation_mode="ACTIONS",
                          export_force_sampling=False, export_apply=False)
print("EXPORTED", OUT, os.path.getsize(OUT))
