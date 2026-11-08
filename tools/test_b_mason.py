"""Minimal B test: Mason's left arm, Run_Gun_Loop, one frame, hand position before/after."""
import bpy, math
from mathutils import Vector, Matrix, Quaternion

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
LIB = ROOT + r"\assets\animation-library\ual1\UAL1_Standard.glb"
CLIPS = ROOT + r"\assets\models\generated\survivor_male_universal.old.glb"
FRAME = 12
CHAIN = ("upperarm_l", "lowerarm_l", "hand_l")
PARENT = {"lowerarm_l": "upperarm_l", "hand_l": "lowerarm_l"}

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=LIB)
arm = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"][0]
for o in list(bpy.context.scene.objects):
    if o.type == "MESH":
        bpy.data.objects.remove(o, do_unlink=True)
before = set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=CLIPS)
clip_arm = [o for o in bpy.context.scene.objects if o not in before and o.type == "ARMATURE"][0]
action = bpy.data.actions.get("Run_Gun_Loop") or list(bpy.data.actions)[0]
bpy.data.objects.remove(clip_arm, do_unlink=True)


def play(a, act):
    if a.animation_data is None:
        a.animation_data_create()
    cp = act.copy()
    a.animation_data.action = cp
    try:
        if len(cp.slots):
            a.animation_data.action_slot = cp.slots[0]
    except Exception:
        pass
    bpy.context.scene.frame_set(FRAME)
    bpy.context.view_layer.update()
    return a.pose.bones["hand_l"].matrix.translation.copy()


pos_before = play(arm, action)
print("BEFORE hand_l:", tuple(round(v, 4) for v in pos_before))

rest_old = {n: arm.data.bones[n].matrix_local.to_3x3().copy() for n in CHAIN}

# --- B: rotate the left arm rest down 87 deg about the shoulder
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
eb = arm.data.edit_bones
sh = eb["upperarm_l"].head.copy()
rot = Matrix.Rotation(math.radians(87.0), 3, "Y")
for n in CHAIN:
    e = eb[n]
    e.head = sh + rot @ (e.head - sh)
    e.tail = sh + rot @ (e.tail - sh)
bpy.ops.object.mode_set(mode="OBJECT")

rest_new = {n: arm.data.bones[n].matrix_local.to_3x3().copy() for n in CHAIN}


def rel(rest, n):
    pn = PARENT.get(n)
    return rest[n] if pn is None else rest[pn].inverted() @ rest[n]


for n in CHAIN:
    C = (rel(rest_new, n).inverted() @ rel(rest_old, n)).to_quaternion()
    path = 'pose.bones["%s"].rotation_quaternion' % n
    for act in bpy.data.actions:
        pool = list(act.fcurves) if hasattr(act, "fcurves") else [
            fc for layer in act.layers for strip in layer.strips
            for cb in getattr(strip, "channelbags", []) for fc in cb.fcurves]
        curves = [next((c for c in pool if c.data_path == path and c.array_index == i), None) for i in range(4)]
        if any(c is None for c in curves):
            continue
        for kp in range(len(curves[0].keyframe_points)):
            q = Quaternion([curves[i].keyframe_points[kp].co[1] for i in range(4)])
            qn = C @ q
            for i, c in enumerate(curves):
                c.keyframe_points[kp].co[1] = qn[i]
        for c in curves:
            c.update()

pos_after = play(arm, action)
print("AFTER  hand_l:", tuple(round(v, 4) for v in pos_after))
err = (pos_before - pos_after).length
print("POSITION_ERROR %.4f m  (threshold 0.02)" % err)
print("TEST_B_%s" % ("PASS" if err < 0.02 else "FAIL"))
