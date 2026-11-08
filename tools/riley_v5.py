"""Riley from the new Tripo-rigged model: keep its weights, repair the outliers that drag the
legs, bake the arms into the game's T-pose, then bolt the game clips on.

The Tripo weights are mostly fine; the visible "leg pulled along" comes from a handful of
vertices weighted to an arm/hand bone while sitting on the thigh. Any vertex whose dominant
bone is farther than 10 cm away is re-weighted from the nearest two bones instead.

Run: blender -b -P riley_v5.py
"""
import bpy, os, math
from mathutils import Vector, Quaternion

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
NEW = r"C:\Users\user\Downloads\female combat character 3d model.glb"
OLD = os.path.join(ROOT, "assets", "models", "generated", "survivor_riley_universal.old.glb")
OUT = os.path.join(ROOT, "assets", "models", "actors", "survivor_riley_universal.glb")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=NEW)
bpy.context.view_layer.update()

for o in list(bpy.context.scene.objects):
    if o.type == "MESH" and o.name.startswith("Icosphere"):
        bpy.data.objects.remove(o, do_unlink=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
for o in list(bpy.context.scene.objects):
    if o.type == "EMPTY":
        bpy.data.objects.remove(o, do_unlink=True)

arm = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"][0]
arm.name = "UniversalRig"
arm.data.name = "UniversalRig"
body = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
bpy.ops.object.select_all(action="SELECT")
bpy.context.view_layer.objects.active = arm
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# scale to game height, feet on the floor
bpy.context.view_layer.update()
box = [body.matrix_world @ Vector(c) for c in body.bound_box]
lo = Vector((min(p.x for p in box), min(p.y for p in box), min(p.z for p in box)))
hi = Vector((max(p.x for p in box), max(p.y for p in box), max(p.z for p in box)))
factor = 1.78 / max(hi.z - lo.z, 0.01)
for o in (arm, body):
    o.scale = o.scale * factor
bpy.ops.object.select_all(action="SELECT")
bpy.context.view_layer.objects.active = arm
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.context.view_layer.update()
box = [body.matrix_world @ Vector(c) for c in body.bound_box]
lo = Vector((min(p.x for p in box), min(p.y for p in box), min(p.z for p in box)))
hi = Vector((max(p.x for p in box), max(p.y for p in box), max(p.z for p in box)))
shift = Vector((-(lo.x + hi.x) * 0.5, -(lo.y + hi.y) * 0.5, -lo.z))
for o in (arm, body):
    o.location = o.location + shift
bpy.ops.object.select_all(action="SELECT")
bpy.context.view_layer.objects.active = arm
bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

# ---- repair cross-bone outliers
segs = {}
for b in arm.data.bones:
    if b.name == "root" or b.name.startswith("ball_leaf"):
        continue
    segs[b.name] = (b.head_local.copy(), b.tail_local.copy())


def seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (p - (a + ab * t)).length


name_of = {body.vertex_groups[i].index: body.vertex_groups[i].name for i in range(len(body.vertex_groups))}
fixed = 0
for v in body.data.vertices:
    groups = [(g.weight, name_of.get(g.group, "")) for g in v.groups if g.weight > 0.0]
    if not groups:
        continue
    groups.sort(reverse=True)
    dom_name = groups[0][1]
    if dom_name not in segs:
        continue
    a, b = segs[dom_name]
    if seg_dist(v.co, a, b) <= 0.10:
        continue
    best = sorted(((seg_dist(v.co, sa, sb), n) for n, (sa, sb) in segs.items()))[:2]
    d1, n1 = best[0]
    d2, n2 = best[1]
    w1 = 1.0 / max(d1 * d1, 1e-6)
    w2 = 0.0 if d2 > d1 * 1.6 + 0.02 else 1.0 / max(d2 * d2, 1e-6)
    tot = w1 + w2
    for g in list(v.groups):
        body.vertex_groups[g.group].remove([v.index])
    body.vertex_groups[n1].add([v.index], w1 / tot, "REPLACE")
    if w2 > 0.0:
        body.vertex_groups[n2].add([v.index], w2 / tot, "REPLACE")
    fixed += 1
print("OUTLIERS_FIXED", fixed, "of", len(body.data.vertices))

# ---- A-pose to T-pose, baked into the rest pose (quaternions, verified below)
def tip_of(side):
    best = None
    for v in body.data.vertices:
        p = v.co
        if p.z < 0.80 or p.z > 1.60:
            continue
        if side * p.x < 0.10:
            continue
        if best is None or abs(p.x) > abs(best.x):
            best = p.copy()
    return best

bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="POSE")
for side, up, hand in ((-1, "upperarm_r", "hand_r"), (1, "upperarm_l", "hand_l")):
    tip = tip_of(side)
    if tip is None:
        print("ARM", up, "no tip"); continue
    sh = arm.data.bones[up].head_local.copy()
    dz = sh.z - tip.z
    dx = abs(tip.x - sh.x)
    if dz <= 0.03 or dx <= 1e-3:
        print("ARM", up, "already horizontal"); continue
    ang = math.atan2(dz, dx)
    pb = arm.pose.bones[up]
    pb.rotation_mode = "QUATERNION"
    pb.rotation_quaternion = Quaternion(Vector((0, 1, 0)), math.radians(-side * math.degrees(ang))) @ pb.rotation_quaternion
    print("ARM", up, "lift_deg", round(math.degrees(ang), 1))
bpy.context.view_layer.update()
bpy.ops.pose.select_all(action="SELECT")
bpy.ops.pose.armature_apply(selected=False)
bpy.ops.object.mode_set(mode="OBJECT")
for n in ("hand_l", "hand_r"):
    print("AFTER_BAKE", n, tuple(round(v, 2) for v in arm.data.bones[n].head_local))

# ---- game clips
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

# ---- pose check render
if arm.animation_data is None:
    arm.animation_data_create()
for a in bpy.data.actions:
    if a.name == "Run_Gun_Loop":
        arm.animation_data.action = a
        try:
            arm.animation_data.action_slot = a.slots[0]
        except Exception as exc:
            print("slot skipped:", exc)
        break
bpy.context.scene.frame_set(12)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 512
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
cam_data.ortho_scale = 2.1
cam = bpy.data.objects.new("c", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam.location = Vector((1.9, -2.9, 1.2))
cam.rotation_euler = (Vector((0, 0, 0.95)) - cam.location).to_track_quat("-Z", "Y").to_euler()
scene.render.filepath = os.path.join(ROOT, "assets", "models", "actors", "riley_v5_check.png")
bpy.ops.render.render(write_still=True)
print("CHECK_RENDERED")

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
print("V5_EXPORTED", OUT, os.path.getsize(OUT))
