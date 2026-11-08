"""Rig an actor onto the game's Universal Animation Library skeleton.

Key idea (this is what fixes the collapsed shoulders): the mesh is posed into the rig's
T-pose FIRST, with a smooth falloff around each shoulder, and only then bound. Nothing is
rotated after the weights exist, so the skeleton keeps the library's T rest pose, the clips
apply as authored, and the shoulder line / neck / face are never sheared.

Run: blender -b -P rig_actor.py -- <hd_glb> <old_universal_glb> <out_glb> <height> <human|zombie>
"""
import bpy, os, sys, math, statistics
from mathutils import Vector, Matrix

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
LIB = os.path.join(ROOT, "assets", "animation-library", "ual1", "UAL1_Standard.glb")
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
HD, OLD, OUT, HEIGHT, MODE = argv[0], argv[1], argv[2], float(argv[3]), argv[4]

HUMAN_CLIPS = {"Run_Gun_Loop", "Run_Gun_F_Loop", "Reload_Gun_Loop", "Reload_Gun_F_Loop",
               "Pistol_Aim_Neutral", "Pistol_Shoot", "Pistol_Reload", "Death01", "Hit_Chest"}
ZOMBIE_CLIPS = {"Zombie_Walk_Fwd_Loop", "Zombie_Idle_Loop", "Zombie_Scratch", "Death01", "Hit_Knockback"}

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=LIB)
arm = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"][0]
arm.name = "UniversalRig"
arm.data.name = "UniversalRig"
for o in list(bpy.context.scene.objects):
    if o.type == "MESH":
        bpy.data.objects.remove(o, do_unlink=True)

before = set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=HD)
new = [o for o in bpy.context.scene.objects if o not in before]
meshes = [o for o in new if o.type == "MESH"]
# drop the source rig (Tripo's) and any stray helper meshes
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
for o in list(bpy.context.scene.objects):
    kind = o.type
    if kind == "ARMATURE" and o is not arm:
        bpy.data.objects.remove(o, do_unlink=True)
    elif kind == "EMPTY":
        bpy.data.objects.remove(o, do_unlink=True)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    if not o.name.startswith("Icosphere"):
        o.select_set(True)
bpy.context.view_layer.objects.active = [o for o in meshes if not o.name.startswith("Icosphere")][0]
if len([o for o in meshes if not o.name.startswith("Icosphere")]) > 1:
    bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
body.name = "HighDetailCharacter"
for o in list(bpy.context.scene.objects):
    if o.type == "MESH" and o is not body:
        bpy.data.objects.remove(o, do_unlink=True)
for g in list(body.vertex_groups):
    body.vertex_groups.remove(g)
bpy.ops.object.select_all(action="SELECT")
bpy.context.view_layer.objects.active = arm
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# ---- scale + place
bpy.context.view_layer.update()
box = [body.matrix_world @ Vector(c) for c in body.bound_box]
lo = Vector((min(p.x for p in box), min(p.y for p in box), min(p.z for p in box)))
hi = Vector((max(p.x for p in box), max(p.y for p in box), max(p.z for p in box)))
# match the LIBRARY rig's own height: the mesh has to line up with its bones, or the arm
# posing and the heat bind both work on the wrong geometry
rig_height = max((b.tail_local.z for b in arm.data.bones), default=1.83)
if HEIGHT <= 0.0:
    HEIGHT = rig_height
factor = HEIGHT / max(hi.z - lo.z, 0.01)
# ONLY the mesh: the library rig is already authored at real-world scale (~1.8 m). Scaling the
# armature too made the bones 1.7x too large, which is why the arm posing kept missing them.
body.scale = body.scale * factor
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.context.view_layer.update()
box = [body.matrix_world @ Vector(c) for c in body.bound_box]
lo = Vector((min(p.x for p in box), min(p.y for p in box), min(p.z for p in box)))
hi = Vector((max(p.x for p in box), max(p.y for p in box), max(p.z for p in box)))
shift = Vector((-(lo.x + hi.x) * 0.5, -(lo.y + hi.y) * 0.5, -lo.z))
body.location = body.location + shift
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
print("FIT", round(factor, 3), "height", HEIGHT)

# ---- drop thin stray slivers (a hair strand that sticks out of the head)
try:
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.separate(type="LOOSE")
    bpy.ops.object.mode_set(mode="OBJECT")
    parts = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    kill = []
    for o in parts:
        if o is body:
            continue
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
        size = Vector((max(v.x for v in bb) - min(v.x for v in bb),
                       max(v.y for v in bb) - min(v.y for v in bb),
                       max(v.z for v in bb) - min(v.z for v in bb)))
        center_z = sum(v.z for v in bb) / 8.0
        dims = sorted([size.x, size.y, size.z])
        if dims[0] < 0.012 and 0.08 < dims[2] < 0.50 and center_z > 1.15:
            kill.append(o.name)
    print("SLIVERS_DELETED", len(kill))
    for name in kill:
        obj = bpy.data.objects.get(name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)
    keep = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for o in keep:
        o.select_set(True)
    bpy.context.view_layer.objects.active = keep[0]
    if len(keep) > 1:
        bpy.ops.object.join()
    body = bpy.context.view_layer.objects.active
    body.name = "HighDetailCharacter"
except Exception as exc:
    print("SLIVER_PASS_SKIPPED", exc)

# ---- pose the mesh into the rig's T-pose (smooth shoulder falloff), humans only
if MODE == "human_apose":
    # The rig is a T-pose, so "near the arm bone" selects chest vertices, not the hanging arm.
    # Select the arm by region instead: outboard of the shoulder line, above the hip, and
    # within reach of the shoulder joint.
    for up, low, hand in (("upperarm_r", "lowerarm_r", "hand_r"),
                          ("upperarm_l", "lowerarm_l", "hand_l")):
        sh = arm.data.bones[up].head_local.copy()
        sign = 1.0 if sh.x >= 0.0 else -1.0
        cluster = []
        for v in body.data.vertices:
            p = v.co
            # only the arm itself: outboard of the deltoid, away from the chest shell
            if sign * p.x < abs(sh.x) + 0.04:
                continue
            if p.z < 0.72:
                continue
            d_from_sh = (p - sh).length
            if d_from_sh < 0.10 or d_from_sh > 0.85:
                continue
            cluster.append(v)
        if not cluster:
            print("ARM", up, "no cluster"); continue
        tip = max(cluster, key=lambda v: (v.co - sh).length).co.copy()
        dz = sh.z - tip.z
        dx = abs(tip.x - sh.x)
        if dz <= 0.03 or dx <= 1e-3:
            print("ARM", up, "already horizontal", round(dz, 3)); continue
        ang = math.atan2(dz, dx)
        moved = 0
        for v in cluster:
            d = (v.co - sh).length
            w = max(0.0, min(1.0, (d - 0.05) / 0.15))
            w = w * w * (3.0 - 2.0 * w)
            if w <= 0.0:
                continue
            v.co = sh + (Matrix.Rotation(-sign * ang * w, 4, "Y") @ (v.co - sh))
            moved += 1
        print("ARM", up, "lift_deg", round(math.degrees(ang), 1), "verts", moved)

# ---- weights: heat on a voxel proxy, transferred back so UVs survive
def bind_heat(target):
    bpy.ops.object.select_all(action="DESELECT")
    target.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    return sum(1 for v in target.data.vertices if v.groups)

proxy = None
for voxel in (0.008, 0.015, 0.025, 0.04):
    cand = body.copy()
    cand.data = body.data.copy()
    bpy.context.collection.objects.link(cand)
    cand.name = "WeightProxy"
    rem = cand.modifiers.new("Remesh", "REMESH")
    rem.mode = "VOXEL"
    rem.voxel_size = voxel
    bpy.ops.object.select_all(action="DESELECT")
    cand.select_set(True)
    bpy.context.view_layer.objects.active = cand
    bpy.ops.object.modifier_apply(modifier=rem.name)
    w = bind_heat(cand)
    print("PROXY", voxel, w, "/", len(cand.data.vertices))
    if w > len(cand.data.vertices) * 0.9:
        proxy = cand
        break
    bpy.data.objects.remove(cand, do_unlink=True)
if proxy is None:
    raise SystemExit("heat bind failed at every voxel size")

for g in list(body.vertex_groups):
    body.vertex_groups.remove(g)
dt = body.modifiers.new("WeightTransfer", "DATA_TRANSFER")
dt.object = proxy
dt.use_vert_data = True
dt.data_types_verts = {"VGROUP_WEIGHTS"}
dt.vert_mapping = "POLYINTERP_NEAREST"
dt.layers_vgroup_select_src = "ALL"
dt.layers_vgroup_select_dst = "NAME"
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.datalayout_transfer(modifier=dt.name)
bpy.ops.object.modifier_apply(modifier=dt.name)
bpy.data.objects.remove(proxy, do_unlink=True)
print("TRANSFERRED", len(body.vertex_groups), sum(1 for v in body.data.vertices if v.groups), "/", len(body.data.vertices))

bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
bpy.ops.object.vertex_group_smooth(group_select_mode="ALL", factor=0.5, repeat=4)
bpy.ops.object.mode_set(mode="OBJECT")
print("WEIGHTS_SMOOTHED")

mod = body.modifiers.new("Armature", "ARMATURE")
mod.object = arm
body.parent = arm

# ---- clips
b2 = set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=OLD)
for o in [o for o in bpy.context.scene.objects if o not in b2]:
    bpy.data.objects.remove(o, do_unlink=True)
keep = HUMAN_CLIPS if MODE.startswith("human") else ZOMBIE_CLIPS
alts = set()
for k in keep:
    alts.add(k)
    alts.add(k.replace("_Loop", "") + "_Loop")
    alts.add(k.replace("_Loop", ""))
for action in list(bpy.data.actions):
    if action.name not in alts:
        bpy.data.actions.remove(action)
print("ACTIONS", [a.name for a in bpy.data.actions])

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
print("EXPORTED", OUT, os.path.getsize(OUT))
