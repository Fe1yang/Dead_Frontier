"""Riley bind v4: straighten both arms to the rig's T-pose with ONE rotation per arm.

Every earlier attempt either rotated each vertex by its own angle (which folded the chest into
the torso) or measured the droop from the rig, which is already a T-pose. This one takes the
arm cluster, finds the mesh's own arm tip, and rotates the whole cluster by that single angle
about the shoulder joint, so the arm becomes straight without distorting the torso.

Run: blender -b -P rebind_riley_v4.py
"""
import bpy, os, math
from mathutils import Vector, Matrix

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
LIB = os.path.join(ROOT, "assets", "animation-library", "ual1", "UAL1_Standard.glb")
MESH = os.path.join(ROOT, "assets", "models", "generated", "survivor_riley_hd.glb")
OUT = os.path.join(ROOT, "assets", "models", "actors", "survivor_riley_universal.glb")


def seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (p - (a + ab * t)).length


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

bpy.context.view_layer.update()
box = [body.matrix_world @ Vector(c) for c in body.bound_box]
lo = Vector((min(v.x for v in box), min(v.y for v in box), min(v.z for v in box)))
hi = Vector((max(v.x for v in box), max(v.y for v in box), max(v.z for v in box)))
body.scale = body.scale * (1.78 / max(hi.z - lo.z, 0.01))
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
print("MESH_FIT size", tuple(round(v, 3) for v in (hi - lo)))

# ---- arms: one rotation per side, about the shoulder joint
for side in (1, -1):
    sh = Vector((side * 0.19, 0.0, 1.44))       # shoulder joint from the rig's rest pose
    cluster = []
    for v in body.data.vertices:
        p = v.co
        if p.z < 0.85 or abs(p.x) < 0.20:
            continue
        if (p - sh).length > 0.85:
            continue
        if side * p.x < 0:                     # only this side
            continue
        cluster.append(v)
    if not cluster:
        print("ARM", side, "no cluster")
        continue
    tip = max(cluster, key=lambda v: (v.co - sh).length).co.copy()
    dx = abs(tip.x - sh.x)
    dz = sh.z - tip.z
    if dz <= 0.05 or dx <= 1e-3:
        print("ARM", side, "already horizontal", round(dz, 3))
        continue
    ang = math.atan2(dz, dx)
    rot = Matrix.Rotation(-side * ang, 4, "Y")
    for v in cluster:
        v.co = sh + (rot @ (v.co - sh))
    print("ARM", side, "verts", len(cluster), "lift_deg", round(math.degrees(ang), 1))
bpy.context.view_layer.update()

# ---- nearest-bone weights
bones = [b for b in arm.data.bones if b.name != "root" and not b.name.startswith("ball_leaf")]
segs = [(b.name, b.head_local.copy(), b.tail_local.copy()) for b in bones]
groups = {n: (body.vertex_groups.get(n) or body.vertex_groups.new(name=n)) for n, _a, _b in segs}
for v in body.data.vertices:
    d = sorted(((seg_dist(v.co, a, b), n) for n, a, b in segs))[:2]
    d1, n1 = d[0]
    d2, n2 = d[1]
    w1 = 1.0 / max(d1 * d1, 1e-6)
    w2 = 0.0 if d2 > d1 * 1.6 + 0.02 else 1.0 / max(d2 * d2, 1e-6)
    tot = w1 + w2
    groups[n1].add([v.index], w1 / tot, "REPLACE")
    if w2 > 0.0:
        groups[n2].add([v.index], w2 / tot, "REPLACE")
print("WEIGHTS_ASSIGNED")

mod = body.modifiers.new("Armature", "ARMATURE")
mod.object = arm
body.parent = arm

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

# ---- rest-pose render to check the T-pose bind
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 640
scene.render.resolution_y = 640
scene.render.film_transparent = True
world = bpy.data.worlds.new("W")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.55, 0.6, 1)
light = bpy.data.objects.new("k", bpy.data.lights.new("k", type="AREA"))
light.data.energy = 900
light.data.size = 3.0
light.location = (1.6, -2.4, 2.2)
light.rotation_euler = (Vector((0, 0, 1.0)) - Vector(light.location)).to_track_quat("-Z", "Y").to_euler()
scene.collection.objects.link(light)
cam_data = bpy.data.cameras.new("c")
cam_data.type = "ORTHO"
cam_data.ortho_scale = 2.3
cam = bpy.data.objects.new("c", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam.location = Vector((0.0, -3.2, 1.1))
cam.rotation_euler = (Vector((0, 0, 0.95)) - cam.location).to_track_quat("-Z", "Y").to_euler()
scene.render.filepath = os.path.join(ROOT, "assets", "models", "actors", "riley_tpose_check.png")
bpy.ops.render.render(write_still=True)
print("TPOSE_RENDERED")

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
print("V4_EXPORTED", OUT, os.path.getsize(OUT))
