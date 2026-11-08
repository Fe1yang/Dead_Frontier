"""Rig an A-pose character WITHOUT touching the mesh.

The conflict: the game's skeleton rests in a T-pose, the Tripo characters are modelled in an
A-pose, and no T-pose model is available. Rotating mesh vertices to fix that tore their
clothing. So nothing on the mesh is touched here:

1. the arm bones' REST is rotated down to meet the mesh (edit bones, no skinning yet),
2. the mesh is bound afterwards, so at bind time mesh and bones already agree (zero deform),
3. every clip's upper-arm rotation is pre-multiplied by the inverse of that rest change, so a
   T-authored animation still produces the pose it was authored for.

Run: blender -b -P rig_actor_apose.py -- <hd_glb> <old_universal_glb> <out_glb> <height|0> <human|zombie>
"""
import bpy, os, sys, math
from mathutils import Vector, Matrix, Quaternion

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
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
for o in list(bpy.context.scene.objects):
    kind = o.type
    if kind == "ARMATURE" and o is not arm:
        bpy.data.objects.remove(o, do_unlink=True)
    elif kind == "EMPTY":
        bpy.data.objects.remove(o, do_unlink=True)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.name.startswith("Icosphere")]
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
body.name = "HighDetailCharacter"
for o in list(bpy.context.scene.objects):
    if o.type == "MESH" and o is not body:
        bpy.data.objects.remove(o, do_unlink=True)
for g in list(body.vertex_groups):
    body.vertex_groups.remove(g)

# ---- scale ONLY the mesh, to the skeleton's own height
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
rig_height = max((b.tail_local.z for b in arm.data.bones), default=1.83)
if HEIGHT <= 0.0:
    HEIGHT = rig_height
box = [body.matrix_world @ Vector(c) for c in body.bound_box]
lo = Vector((min(p.x for p in box), min(p.y for p in box), min(p.z for p in box)))
hi = Vector((max(p.x for p in box), max(p.y for p in box), max(p.z for p in box)))
body.scale = body.scale * (HEIGHT / max(hi.z - lo.z, 0.01))
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
print("SCALED mesh to", round(HEIGHT, 2), "rig is", round(rig_height, 2))

# ---- rotate the arm bones' REST down to the mesh's A-pose (nothing is skinned yet)
ARM_BONES = ("upperarm_r", "lowerarm_r", "hand_r", "upperarm_l", "lowerarm_l", "hand_l")
rest_before = {}
rest_offsets = {}
if MODE == "human":
    rest_before = {n: arm.data.bones[n].matrix_local.to_3x3().copy() for n in ARM_BONES if n in arm.data.bones}
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.data.edit_bones
    for up, low, hand in (("upperarm_r", "lowerarm_r", "hand_r"),
                          ("upperarm_l", "lowerarm_l", "hand_l")):
        sh = eb[up].head.copy()
        sign = 1.0 if sh.x >= 0.0 else -1.0
        tip = None
        for v in body.data.vertices:
            p = v.co
            if p.z < 0.60 or sign * p.x < abs(sh.x) + 0.02:
                continue
            d = (p - sh).length
            if d < 0.10 or d > 0.95:
                continue
            if tip is None or d > (tip - sh).length:
                tip = p.copy()
        if tip is None:
            print("ARM", up, "no tip"); continue
        dz = sh.z - tip.z
        dx = abs(tip.x - sh.x)
        if dz <= 0.03 or dx <= 1e-3:
            print("ARM", up, "already horizontal"); continue
        ang = math.atan2(dz, dx)
        rot = Matrix.Rotation(-sign * ang, 3, "Y")
        for b in (up, low, hand):
            if b not in eb:
                continue
            e = eb[b]
            e.head = sh + rot @ (e.head - sh)
            e.tail = sh + rot @ (e.tail - sh)
        print("ARM", up, "rest rotated", round(math.degrees(ang), 1), "deg")
    bpy.ops.object.mode_set(mode="OBJECT")

def bind_heat(target):
    bpy.ops.object.select_all(action="DESELECT")
    target.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    return sum(1 for v in target.data.vertices if v.groups)

weighted = bind_heat(body)
print("HEAT", weighted, "/", len(body.data.vertices))
if weighted < len(body.data.vertices) * 0.9:
    for g in list(body.vertex_groups):
        body.vertex_groups.remove(g)
    body.parent = None
    for m in list(body.modifiers):
        body.modifiers.remove(m)
    proxy = None
    for voxel in (0.008, 0.015, 0.025, 0.04):
        cand = body.copy()
        cand.data = body.data.copy()
        bpy.context.collection.objects.link(cand)
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
        raise SystemExit("no weighting method worked")
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
    mod = body.modifiers.new("Armature", "ARMATURE")
    mod.object = arm
    body.parent = arm
print("BOUND", len(body.vertex_groups), sum(1 for v in body.data.vertices if v.groups))

# ---- the arm bones now sit inside the arms (the rest was rotated to match), so the arm skin
# can be assigned by distance with confidence. Without this the proxy transfer leaves arm
# vertices weighted to the chest: the BONES raise, the mesh does not.
if MODE == "human":
    def seg_dist(p, a, b):
        ab = b - a
        tt = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
        return (p - (a + ab * tt)).length

    arm_names = ["upperarm_l", "lowerarm_l", "hand_l", "upperarm_r", "lowerarm_r", "hand_r"]
    arm_segs = {n: (arm.data.bones[n].head_local.copy(), arm.data.bones[n].tail_local.copy())
                for n in arm_names if n in arm.data.bones}
    groups = {}
    for n in arm_names:
        if n in arm.data.bones:
            groups[n] = body.vertex_groups.get(n) or body.vertex_groups.new(name=n)
    forced = 0
    sh_l = arm.data.bones["upperarm_l"].head_local.copy()
    sh_r = arm.data.bones["upperarm_r"].head_local.copy()
    for v in body.data.vertices:
        best = None
        for n, (a, b) in arm_segs.items():
            d = seg_dist(v.co, a, b)
            if best is None or d < best[0]:
                best = (d, n)
        if best is None or best[0] > 0.16:
            continue
        # Blend at the shoulder instead of a hard 1.0: the heat weights keep the deltoid and
        # the jacket seam intact, the arm takes over further down. A hard pin here is what
        # tore the shoulders into a fan.
        sh = sh_l if best[1].endswith("_l") else sh_r
        d_sh = (v.co - sh).length
        if d_sh < 0.12:
            continue
        w = 1.0 if d_sh >= 0.22 else ((d_sh - 0.12) / 0.10)
        w = w * w * (3.0 - 2.0 * w)
        for g in list(v.groups):
            body.vertex_groups[g.group].add([v.index], g.weight * (1.0 - w), "REPLACE")
        groups[best[1]].add([v.index], w, "REPLACE")
        forced += 1
    print("ARM_WEIGHTS_FORCED", forced)



# ---- clips, then the parent-relative compensation verified by tools/abc_test.py
b2 = set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=OLD)
for o in [o for o in bpy.context.scene.objects if o not in b2]:
    bpy.data.objects.remove(o, do_unlink=True)
keep = HUMAN_CLIPS if MODE == "human" else ZOMBIE_CLIPS
alts = set()
for k in keep:
    alts.update({k, k.replace("_Loop", "") + "_Loop", k.replace("_Loop", "")})
for action in list(bpy.data.actions):
    if action.name not in alts:
        bpy.data.actions.remove(action)
print("ACTIONS_KEPT", sorted(a.name for a in bpy.data.actions))


def all_fcurves(action):
    if hasattr(action, "fcurves"):
        return list(action.fcurves)
    out = []
    for layer in action.layers:
        for strip in layer.strips:
            for cb in getattr(strip, "channelbags", []):
                out.extend(cb.fcurves)
    return out


PARENT = {"lowerarm_l": "upperarm_l", "lowerarm_r": "upperarm_r",
          "hand_l": "lowerarm_l", "hand_r": "lowerarm_r"}

if MODE == "human" and rest_before:
    rest_after = {n: arm.data.bones[n].matrix_local.to_3x3().copy() for n in rest_before}
    for n in rest_before:
        pn = PARENT.get(n)
        if pn is None or pn not in rest_before:
            A_old, A_new = rest_before[n], rest_after[n]
        else:
            A_old = rest_before[pn].inverted() @ rest_before[n]
            A_new = rest_after[pn].inverted() @ rest_after[n]
        C = (A_new.inverted() @ A_old).to_quaternion()
        if abs(C.angle) < 1e-5:
            continue
        path = 'pose.bones["%s"].rotation_quaternion' % n
        touched = 0
        for action in bpy.data.actions:
            pool = all_fcurves(action)
            curves = []
            for i in range(4):
                hit = next((c for c in pool if c.data_path == path and c.array_index == i), None)
                curves.append(hit)
            if any(c is None for c in curves):
                continue
            for kp in range(len(curves[0].keyframe_points)):
                q = Quaternion((curves[0].keyframe_points[kp].co[1],
                                curves[1].keyframe_points[kp].co[1],
                                curves[2].keyframe_points[kp].co[1],
                                curves[3].keyframe_points[kp].co[1]))
                qn = C @ q
                for i, c in enumerate(curves):
                    c.keyframe_points[kp].co[1] = qn[i]
            for c in curves:
                c.update()
            touched += 1
        print("COMPENSATED", n, "deg", round(math.degrees(C.angle), 2), "actions", touched)

print("CLIPS_COMPENSATED", len(bpy.data.actions))

bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
arm.select_set(True)
bpy.ops.export_scene.gltf(
    filepath=OUT,
    export_format="GLB",
    use_selection=True,
    export_animations=True,
    export_animation_mode="ACTIONS",
    export_force_sampling=False,
    export_apply=False,
)
print("EXPORTED", OUT, os.path.getsize(OUT))
