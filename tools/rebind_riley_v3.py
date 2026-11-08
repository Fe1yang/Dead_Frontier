"""Riley bind v3: proper arm-to-T-pose, knife removed, nearest-bone weights.

The previous pass rotated every vertex outboard of x=0.20, which folded chest/vest geometry
into the torso. This one rotates only the vertices that belong to the arm bones, using the
bones themselves as reference, and it deletes the knife (a tight cluster of small islands
around (-0.28, -0.11, 0.63) in metres).

Run: blender -b -P rebind_riley_v3.py
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

# fit to 1.78 m, feet on the floor, centred, transforms applied
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

# ---- knife: delete the small islands clustered around the blade grip
KX, KY, KZ = -0.28, -0.11, 0.63
dup = body.copy()
dup.data = body.data.copy()
bpy.context.collection.objects.link(dup)
bpy.ops.object.select_all(action="DESELECT")
dup.select_set(True)
bpy.context.view_layer.objects.active = dup
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.separate(type="LOOSE")
bpy.ops.object.mode_set(mode="OBJECT")
parts = [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name != body.name]
blade = []
for o in parts:
    b = [o.matrix_world @ Vector(c) for c in o.bound_box]
    l = Vector((min(v.x for v in b), min(v.y for v in b), min(v.z for v in b)))
    h = Vector((max(v.x for v in b), max(v.y for v in b), max(v.z for v in b)))
    c = (l + h) * 0.5
    if (c - Vector((KX, KY, KZ))).length < 0.13 and max(h - l) < 0.40:
        blade.append(o)
print("KNIFE_ISLANDS", len(blade), [o.name for o in blade])
blade_names = [o.name for o in blade]
all_names = [o.name for o in parts]      # snapshot BEFORE deleting anything
for name in all_names:
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)
print("KNIFE_REMOVED", len(blade_names))

# ---- arms into the rig's T-pose: rotate only the vertices that belong to the arm bones
def arms_to_tpose():
	"""Lift each arm to horizontal using the MESH itself: the rig's rest is already a T-pose,
	so the droop has to be measured from the vertices, not from the bones."""
	moved = 0
	for side, up_name, low_name, hand_name in ((1, "upperarm_l", "lowerarm_l", "hand_l"),
	                                           (-1, "upperarm_r", "lowerarm_r", "hand_r")):
		if up_name not in arm.data.bones or hand_name not in arm.data.bones:
			continue
		sh = arm.data.bones[up_name].head_local.copy()
		hand = arm.data.bones[hand_name]
		hand_a, hand_b = hand.head_local.copy(), hand.tail_local.copy()
		arm_bones = [arm.data.bones[n] for n in (up_name, low_name) if n in arm.data.bones]
		# vertices belonging to the arm chain
		cluster = []
		hand_pts = []
		for v in body.data.vertices:
			p = v.co
			near = min(seg_dist(p, b.head_local, b.tail_local) for b in arm_bones)
			near_hand = seg_dist(p, hand_a, hand_b)
			if min(near, near_hand) > 0.19:
				continue
			cluster.append(v)
			if near_hand <= near:
				hand_pts.append(p)
		if not cluster or not hand_pts:
			print("ARM", up_name, "no cluster")
			continue
		hand_c = sum(hand_pts, Vector()) / len(hand_pts)
		d = hand_c - sh
		ang = math.atan2(-d.z, abs(d.x))     # positive = drooping below horizontal
		if ang <= 0.10 or ang > 1.45:
			print("ARM", up_name, "no droop", round(math.degrees(ang), 1))
			continue
		rot = Matrix.Rotation(-side * ang, 4, "Y")
		for v in cluster:
			v.co = sh + (rot @ (v.co - sh))
			moved += 1
		print("ARM", up_name, "verts", len(cluster), "lift_deg", round(math.degrees(ang), 1))
	print("ARM_VERTS", moved)

arms_to_tpose()
bpy.context.view_layer.update()

# ---- nearest-bone weights
exclude = ("root",)
bones = [b for b in arm.data.bones if b.name not in exclude and not b.name.startswith("ball_leaf")]
segs = [(b.name, b.head_local.copy(), b.tail_local.copy()) for b in bones]
groups = {}
for name, _a, _b in segs:
    groups[name] = body.vertex_groups.get(name) or body.vertex_groups.new(name=name)

for v in body.data.vertices:
    best = sorted(((seg_dist(v.co, a, b), n) for n, a, b in segs))[:2]
    d1, n1 = best[0]
    d2, n2 = best[1]
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

# ---- pose render for a sanity check
if arm.animation_data is None:
    arm.animation_data_create()
for action in bpy.data.actions:
    if action.name == "Run_Gun_Loop":
        arm.animation_data.action = action
        break
bpy.context.scene.frame_set(10)
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
light.data.energy = 800
light.data.size = 3.0
light.location = (1.6, -2.2, 2.2)
light.rotation_euler = (Vector((0, 0, 1.0)) - Vector(light.location)).to_track_quat("-Z", "Y").to_euler()
scene.collection.objects.link(light)
cam_data = bpy.data.cameras.new("c")
cam_data.type = "ORTHO"
cam_data.ortho_scale = 2.1
cam = bpy.data.objects.new("c", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam.location = Vector((2.4, -2.8, 1.2))
cam.rotation_euler = (Vector((0, 0, 0.95)) - cam.location).to_track_quat("-Z", "Y").to_euler()
scene.render.filepath = os.path.join(ROOT, "assets", "models", "actors", "riley_pose_test2.png")
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
print("V3_EXPORTED", OUT, os.path.getsize(OUT))
