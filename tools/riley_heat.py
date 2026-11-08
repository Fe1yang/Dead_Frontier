"""Riley via the standard pipeline: weld the Tripo shards, bone-heat weights, then bake the
A-pose to T-pose with "apply pose as rest".

Everything before failed because the Tripo mesh arrives as ~2000 disconnected islands, which
makes Blender's bone-heat solver give up (0 weights) and makes any vertex-level hack deform
the clothing. Welding first is the fix.

Run: blender -b -P riley_heat.py
"""
import bpy, os, math
from mathutils import Vector, Matrix

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
LIB = os.path.join(ROOT, "assets", "animation-library", "ual1", "UAL1_Standard.glb")
MESH = os.path.join(ROOT, "assets", "models", "generated", "survivor_riley_hd.glb")
OLD = os.path.join(ROOT, "assets", "models", "generated", "survivor_riley_universal.old.glb")
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

# fit to 1.78 m and stand on the floor
bpy.context.view_layer.update()
box = [body.matrix_world @ Vector(c) for c in body.bound_box]
lo = Vector((min(p.x for p in box), min(p.y for p in box), min(p.z for p in box)))
hi = Vector((max(p.x for p in box), max(p.y for p in box), max(p.z for p in box)))
body.scale = body.scale * (1.78 / max(hi.z - lo.z, 0.01))
bpy.context.view_layer.update()
box = [body.matrix_world @ Vector(c) for c in body.bound_box]
lo = Vector((min(p.x for p in box), min(p.y for p in box), min(p.z for p in box)))
hi = Vector((max(p.x for p in box), max(p.y for p in box), max(p.z for p in box)))
body.location.x -= (lo.x + hi.x) * 0.5
body.location.y -= (lo.y + hi.y) * 0.5
body.location.z -= lo.z
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
print("VERTS_BEFORE", len(body.data.vertices), "islands-fixed by welding next")

# ---- weld the shards so bone heat has a chance
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.remove_doubles(threshold=0.0004)
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode="OBJECT")
print("VERTS_AFTER_WELD", len(body.data.vertices))

# ---- bone heat weights
weighted = 0
for attempt in range(2):
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    weighted = sum(1 for v in body.data.vertices if v.groups)
    print("WEIGHTED", attempt, weighted, "/", len(body.data.vertices))
    if weighted > len(body.data.vertices) * 0.9:
        break
    # second try: drop the existing groups and rebind after a light remesh
    for g in list(body.vertex_groups):
        body.vertex_groups.remove(g)
    body.parent = None
    for m in list(body.modifiers):
        body.modifiers.remove(m)

if weighted <= len(body.data.vertices) * 0.9:
    raise SystemExit("bone heat still failed")

# ---- knife: right-hand vertices that sit far from the palm
gi = body.vertex_groups["hand_r"].index
hand_pts = [v.co.copy() for v in body.data.vertices
            if any(g.group == gi and g.weight > 0.3 for g in v.groups)]
if hand_pts:
    hc = sum(hand_pts, Vector()) / len(hand_pts)
    blade = [v.index for v in body.data.vertices
             if any(g.group == gi and g.weight > 0.3 for g in v.groups) and (v.co - hc).length > 0.128]
    print("KNIFE_VERTS", len(blade), "palm", tuple(round(v, 2) for v in hc))
    if blade:
        bpy.ops.object.select_all(action="DESELECT")
        body.select_set(True)
        bpy.context.view_layer.objects.active = body
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.mode_set(mode="OBJECT")
        for i in blade:
            body.data.vertices[i].select = True
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.delete(type="VERT")
        bpy.ops.object.mode_set(mode="OBJECT")

# ---- A-pose -> T-pose: measure the droop from the geometry, rotate the upper arms, bake
def tip_of(side):
    best = None
    for v in body.data.vertices:
        p = v.co
        if p.z < 0.80 or p.z > 1.60:
            continue
        if side * p.x < 0.15:
            continue
        if best is None or abs(p.x) > abs(best.x):
            best = p.copy()
    return best

def hand_name_of(up_name):
	return "hand_l" if up_name.endswith("_l") else "hand_r"

bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="POSE")
for side, up in ((-1, "upperarm_r"), (1, "upperarm_l")):
    tip = tip_of(side)
    if tip is None:
        print("ARM", up, "no tip")
        continue
    sh = arm.data.bones[up].head_local.copy()
    dz = sh.z - tip.z
    dx = abs(tip.x - sh.x)
    if dz <= 0.03 or dx <= 1e-3:
        print("ARM", up, "already horizontal", round(dz, 3))
        continue
    ang = math.atan2(dz, dx)
    print("ARM", up, "tip", tuple(round(v, 2) for v in tip), "lift_deg", round(math.degrees(ang), 1))
    pb = arm.pose.bones[up]
    from mathutils import Quaternion
    pb.rotation_mode = "QUATERNION"
    pb.rotation_quaternion = Quaternion(Vector((0, 1, 0)), math.radians(-side * ang)) * pb.rotation_quaternion
    print("   posed", up, "hand before", tuple(round(v, 2) for v in arm.pose.bones[hand_name_of(up)].head))
bpy.context.view_layer.update()
bpy.ops.pose.select_all(action="SELECT")
bpy.ops.pose.armature_apply(selected=False)
for n in ("hand_l", "hand_r"):
	if n in arm.data.bones:
		print("AFTER_BAKE", n, tuple(round(v, 2) for v in arm.data.bones[n].head_local))
bpy.ops.object.mode_set(mode="OBJECT")
print("T_POSE_BAKED")

# ---- clips from the previous export (same bone names)
b2 = set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=OLD)
for o in [o for o in bpy.context.scene.objects if o not in b2]:
    bpy.data.objects.remove(o, do_unlink=True)
keep = {"Run_Gun_Loop", "Run_Gun_F_Loop", "Reload_Gun_Loop", "Reload_Gun_F_Loop",
        "Pistol_Aim_Neutral", "Pistol_Shoot", "Pistol_Reload", "Death01", "Hit_Chest"}
for action in list(bpy.data.actions):
    if action.name not in keep:
        bpy.data.actions.remove(action)

# ---- pose check render
if arm.animation_data is None:
    arm.animation_data_create()
for a in bpy.data.actions:
    if a.name == "Run_Gun_Loop":
        arm.animation_data.action = a
        try:
            arm.animation_data.action_slot = a.slots[0]
        except Exception as exc:
            print("slot assign skipped:", exc)
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
scene.render.filepath = os.path.join(ROOT, "assets", "models", "actors", "riley_heat_check.png")
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
print("HEAT_EXPORTED", OUT, os.path.getsize(OUT))
