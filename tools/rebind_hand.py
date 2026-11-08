"""Rebind the hand/forearm skin on a rigged actor.

Jian's Tripo mesh leaves palm and forearm vertices under-weighted, so the visible hand lags
about 20 cm behind the hand bone and the weapon (which rides the bone) looks like it floats.
Only vertices physically inside the hand/forearm capsules are touched.

Run: blender -b -P rebind_hand.py -- <glb> [hand_radius forearm_radius]
"""
import bpy, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
PATH = argv[0]
HAND_R = float(argv[1]) if len(argv) > 1 else 0.075
FORE_R = float(argv[2]) if len(argv) > 2 else 0.075

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


def seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (p - (a + ab * t)).length


# the mesh and the armature do not share a space after a glTF import: bring the bones into
# the mesh's own coordinates before measuring distances, or nothing is ever in range
to_mesh = body.matrix_world.inverted() @ arm.matrix_world
bones = {}
for name in ("hand_l", "hand_r", "lowerarm_l", "lowerarm_r"):
    b = arm.data.bones.get(name)
    if b:
        bones[name] = (to_mesh @ b.head_local, to_mesh @ b.tail_local)
print("SPACE scale", round(to_mesh.to_scale().x, 4))

groups = {}
for name in bones:
    groups[name] = body.vertex_groups.get(name) or body.vertex_groups.new(name=name)

hand_hits = 0
fore_hits = 0
for v in body.data.vertices:
    best = None
    for name, (a, b) in bones.items():
        d = seg_dist(v.co, a, b)
        if best is None or d < best[0]:
            best = (d, name)
    if best is None:
        continue
    d, name = best
    is_hand = name.startswith("hand")
    limit = HAND_R if is_hand else FORE_R
    if d > limit:
        continue
    # keep whatever else is on the vertex, but give the arm chain the dominant share
    for g in list(v.groups):
        body.vertex_groups[g.group].remove([v.index])
    groups[name].add([v.index], 1.0, "REPLACE")
    if is_hand:
        hand_hits += 1
    else:
        fore_hits += 1

print("REBOUND hand=", hand_hits, " forearm=", fore_hits)
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
