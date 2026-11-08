"""A/B/C experiment: can an A-pose mesh keep the game clips when the arm bones' rest is moved?

Reference: the untouched T-pose rig playing Run_Gun_Loop at one frame (Armature space).
A: head/tail only (what the current pipeline does).
B: head/tail + basis compensation q' = (R_new^-1 * R_old).to_quaternion() @ q.
C: head/tail + align_roll to the old local Z, then the same compensation.

For each version we report, for upperarm/forearm/hand: position error (cm) and rotation
error (deg) against the reference. Only the bone math is involved -- no mesh, no weights.

Run: blender -b -P abc_test.py
"""
import bpy, math
from mathutils import Vector, Matrix

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
LIB = ROOT + r"\assets\animation-library\ual1\UAL1_Standard.glb"
CLIPS = ROOT + r"\assets\models\generated\survivor_male_universal.old.glb"
FRAME = 12
BONES = ("upperarm_l", "lowerarm_l", "hand_l")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=LIB)
arm = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"][0]
arm.name = "UniversalRig"
for o in list(bpy.context.scene.objects):
    if o.type == "MESH":
        bpy.data.objects.remove(o, do_unlink=True)

before = set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=CLIPS)
for o in [o for o in bpy.context.scene.objects if o not in before]:
    if o.type != "ARMATURE":
        bpy.data.objects.remove(o, do_unlink=True)
clip_arm = [o for o in bpy.context.scene.objects if o.type == "ARMATURE" and o is not arm][0]
clip_action = {a.name: a for a in bpy.data.actions}
print("CLIPS", sorted(clip_action.keys())[:12])
bpy.data.objects.remove(clip_arm, do_unlink=True)

action = None
for name, act in clip_action.items():
    if name.startswith("Run_Gun") and "F" not in name:
        action = act
        break
if action is None:
    action = list(clip_action.values())[0]
print("USING_CLIP", action.name)


def sample(armature, action_touse):
    if armature.animation_data is None:
        armature.animation_data_create()
    act = action_touse.copy()
    armature.animation_data.action = act
    try:
        slots = act.slots
        if len(slots):
            armature.animation_data.action_slot = slots[0]
    except Exception:
        pass
    bpy.context.scene.frame_set(FRAME)
    bpy.context.view_layer.update()
    out = {}
    for n in BONES:
        pb = armature.pose.bones[n]
        m = pb.matrix.copy()
        out[n] = (m.to_translation(), m.to_quaternion())
    armature.animation_data.action = None
    return out


def clone_armature():
    dup = arm.copy()
    dup.data = arm.data.copy()
    bpy.context.collection.objects.link(dup)
    dup.name = "Test_" + str(len(bpy.data.objects))
    return dup


def move_rest(test_arm, do_align_roll):
    bpy.context.view_layer.objects.active = test_arm
    bpy.ops.object.mode_set(mode="EDIT")
    eb = test_arm.data.edit_bones
    sh = eb["upperarm_l"].head.copy()
    ang = math.radians(87.0)
    rot = Matrix.Rotation(1 * ang, 3, "Y")     # left side: +Y rotation hangs it down
    old_z = {}
    for n in ("upperarm_l", "lowerarm_l", "hand_l"):
        e = eb[n]
        old_z[n] = (e.matrix.to_quaternion() @ Vector((0, 0, 1))).normalized()
        e.head = sh + rot @ (e.head - sh)
        e.tail = sh + rot @ (e.tail - sh)
        if do_align_roll:
            e.align_roll(rot @ old_z[n])
    bpy.ops.object.mode_set(mode="OBJECT")
    return old_z


def compensate(test_arm, old_rest):
    """q' = (R_new^-1 R_old).to_quaternion() @ q, per bone."""
    # Compensation must be parent-relative: pose_child = pose_parent * (R_parent^-1 R_child) * basis
    # so a child whose PARENT also moved needs (A_new^-1 A_old), not the armature-space delta.
    parents = {"lowerarm_l": "upperarm_l", "hand_l": "lowerarm_l"}
    for n in ("upperarm_l", "lowerarm_l", "hand_l"):
        pn = parents.get(n)
        if pn is None:
            A_old = old_rest[n]
            A_new = test_arm.data.bones[n].matrix_local.to_3x3()
        else:
            A_old = old_rest[pn].inverted() @ old_rest[n]
            A_new = test_arm.data.bones[pn].matrix_local.to_3x3().inverted() @ test_arm.data.bones[n].matrix_local.to_3x3()
        C = (A_new.inverted() @ A_old).to_quaternion()
        path = 'pose.bones["%s"].rotation_quaternion' % n
        for act in bpy.data.actions:
            pool = []
            if hasattr(act, "fcurves"):
                pool = list(act.fcurves)
            else:
                for layer in act.layers:
                    for strip in layer.strips:
                        for cb in getattr(strip, "channelbags", []):
                            pool.extend(cb.fcurves)
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


from mathutils import Quaternion
old_rest = {n: arm.data.bones[n].matrix_local.to_3x3() for n in BONES}
reference = sample(arm, action)

results = {}
for label, align, comp in (("A", False, False), ("B", False, True), ("C", True, True)):
    test = clone_armature()
    move_rest(test, align)
    if comp:
        compensate(test, {n: m.copy() for n, m in old_rest.items()})
    got = sample(test, action)
    rows = []
    for n in BONES:
        pos_err = (got[n][0] - reference[n][0]).length * 100.0
        rot_err = math.degrees(reference[n][1].rotation_difference(got[n][1]).angle)
        rows.append((n, pos_err, rot_err))
    results[label] = rows
    bpy.data.objects.remove(test, do_unlink=True)

print("\nVERSION  BONE          pos_err_cm  rot_err_deg")
for label, rows in results.items():
    for n, p, r in rows:
        print("%-7s  %-12s  %8.2f  %10.2f" % (label, n, p, r))
print("ABC_DONE")
