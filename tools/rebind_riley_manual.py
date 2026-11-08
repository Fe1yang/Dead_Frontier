"""Bind the new Riley mesh to the UAL skeleton with hand-written nearest-bone weights.

Blender's bone-heat solver fails on this Tripo mesh ("failed to find solution"), which left
every vertex unweighted: the actor stood still in game and the gun floated. This builds the
weights directly: pose the mesh into the rig's T-pose, give each vertex the two nearest bones
with an inverse-square blend, smooth the result, then export with the game's clips.

Run: blender -b -P rebind_riley_manual.py
"""
import bpy, os, math
from mathutils import Vector, Matrix

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
LIB = os.path.join(ROOT, "assets", "animation-library", "ual1", "UAL1_Standard.glb")
MESH = os.path.join(ROOT, "assets", "models", "generated", "survivor_riley_hd.glb")
OUT = os.path.join(ROOT, "assets", "models", "actors", "survivor_riley_universal.glb")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=LIB)
arm = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"][0]
arm.name = "UniversalRig"
arm.data.name = "UniversalRig"
for o in list(bpy.context.scene.objects):
    if o.type == "MESH":
        bpy.data.objects.remove(o, do_unlink=True)

before = set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=MESH)
new = [o for o in bpy.context.scene.objects if o not in before and o.type == "MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in new:
    o.select_set(True)
bpy.context.view_layer.objects.active = new[0]
if len(new) > 1:
    bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
body.name = "HighDetailCharacter"

# ---- fit to 1.78 m, feet on the floor, centred
bpy.context.view_layer.update()
box = [body.matrix_world @ Vector(c) for c in body.bound_box]
lo = Vector((min(v.x for v in box), min(v.y for v in box), min(v.z for v in box)))
hi = Vector((max(v.x for v in box), max(v.y for v in box), max(v.z for v in box)))
scale = 1.78 / max(hi.z - lo.z, 0.01)
body.scale = body.scale * scale
bpy.context.view_layer.update()
box = [body.matrix_world @ Vector(c) for c in body.bound_box]
lo = Vector((min(v.x for v in box), min(v.y for v in box), min(v.z for v in box)))
hi = Vector((max(v.x for v in box), max(v.y for v in box), max(v.z for v in box)))
body.location.x -= (lo.x + hi.x) * 0.5
body.location.y -= (lo.y + hi.y) * 0.5
body.location.z -= lo.z
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# ---- lift the arms toward the rig's T-pose (the mesh comes in an A-pose)
def to_tpose():
    moved = 0
    for v in body.data.vertices:
        p = v.co.copy()
        # arms: everything outboard of the shoulder and above the waist
        if abs(p.x) > 0.20 and p.z > 1.30:
            sign = -1.0 if p.x < 0 else 1.0
            pivot = Vector((sign * 0.20, 0.0, 1.44))
            rel = p - pivot
            ang = math.atan2(-rel.z, abs(rel.x))     # current droop
            if abs(rel.x) > 1e-4 and ang > 0.12:
                rot = Matrix.Rotation(sign * ang, 4, "Y")
                v.co = pivot + (rot @ rel)
                moved += 1
    print("TPOSE_VERTS", moved)

to_tpose()
bpy.context.view_layer.update()

# ---- nearest-bone weights (two bones, inverse square)
bones = [b for b in arm.data.bones if b.name not in ("root",) and not b.name.startswith("ball_leaf")]
segs = [(b.name, b.head_local.copy(), b.tail_local.copy()) for b in bones]
print("BONE_SEGMENTS", len(segs))

for name, _h, _t in segs:
    if name not in body.vertex_groups:
        body.vertex_groups.new(name=name)

def dist_to_seg(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (p - (a + ab * t)).length

groups = {name: body.vertex_groups[name] for name, _h, _t in segs}
for v in body.data.vertices:
    p = v.co
    best = []
    for name, a, b in segs:
        d = dist_to_seg(p, a, b)
        best.append((d, name))
    best.sort()
    d1, n1 = best[0]
    d2, n2 = best[1]
    w1 = 1.0 / max(d1 * d1, 1e-6)
    w2 = 0.0 if d2 > d1 * 1.6 + 0.02 else 1.0 / max(d2 * d2, 1e-6)
    total = w1 + w2
    groups[n1].add([v.index], w1 / total, "REPLACE")
    if w2 > 0.0:
        groups[n2].add([v.index], w2 / total, "REPLACE")

print("WEIGHTS_ASSIGNED")

# smooth the borders a little so knees/elbows do not tear
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
bpy.ops.object.vertex_group_smooth(group_select_mode="ALL", factor=0.5, repeat=2)
bpy.ops.object.mode_set(mode="OBJECT")

mod = body.modifiers.new("Armature", "ARMATURE")
mod.object = arm
body.parent = arm

# ---- bind the game's clips (the old export already has them on this rig)
OLD = os.path.join(ROOT, "assets", "models", "generated", "survivor_riley_universal.old.glb")
if os.path.exists(OLD):
    b2 = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=OLD)
    for o in [o for o in bpy.context.scene.objects if o not in b2]:
        bpy.data.objects.remove(o, do_unlink=True)

keep = {"Run_Gun_Loop", "Run_Gun_F_Loop", "Reload_Gun_Loop", "Reload_Gun_F_Loop",
        "Pistol_Aim_Neutral", "Pistol_Shoot", "Pistol_Reload", "Death01", "Hit_Chest"}
for action in list(bpy.data.actions):
    if action.name not in keep:
        bpy.data.actions.remove(action)
print("ACTIONS", [a.name for a in bpy.data.actions])

# ---- a test render of a running frame so the deformation can be judged
if arm.animation_data is None:
    arm.animation_data_create()
for action in bpy.data.actions:
    if action.name == "Run_Gun_Loop":
        arm.animation_data.action = action
        break
bpy.context.scene.frame_set(8)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 512
scene.render.resolution_y = 640
scene.render.film_transparent = True
world = bpy.data.worlds.new("W")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.55, 0.6, 1)
w_light = bpy.data.objects.new("k", bpy.data.lights.new("k", type="AREA"))
w_light.data.energy = 700
w_light.data.size = 3.0
w_light.location = (1.6, -2.2, 2.2)
w_light.rotation_euler = (Vector((0, 0, 1.0)) - Vector(w_light.location)).to_track_quat("-Z", "Y").to_euler()
scene.collection.objects.link(w_light)
cam_data = bpy.data.cameras.new("c")
cam_data.type = "ORTHO"
cam_data.ortho_scale = 2.2
cam = bpy.data.objects.new("c", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam.location = Vector((2.6, -2.6, 1.3))
cam.rotation_euler = (Vector((0, 0, 0.95)) - cam.location).to_track_quat("-Z", "Y").to_euler()
scene.render.filepath = os.path.join(ROOT, "assets", "models", "actors", "riley_pose_test.png")
bpy.ops.render.render(write_still=True)
print("POSE_RENDERED")

bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
arm.select_set(True)
bpy.ops.export_scene.gltf(
    filepath=OUT,
    export_format="GLB",
    use_selection=True,
    export_animations=True,
    export_animation_mode="ACTIONS",
    export_force_sampling=True,
    export_apply=False,
)
print("MANUAL_BIND_EXPORTED", OUT, os.path.getsize(OUT))
