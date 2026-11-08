"""Retarget the game's clips onto a Tripo-rigged character, keeping its own skeleton.

This is what makes downloaded animations work on those models: the skeleton is NOT replaced,
the clips are re-expressed in the target skeleton's rest space (rest-relative conjugation,
the same math scripts/anim_library.gd uses at runtime).

q_target = R_t^-1 * (R_s * q_source * R_s^-1) * R_t

Run: blender -b -P retarget_keep_rig.py -- <rigged_glb> <clips_glb> <out_glb>
"""
import bpy, os, sys, math
from mathutils import Quaternion, Matrix

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
RIGGED, CLIPS, OUT = argv[0], argv[1], argv[2]
KEEP = ("Run_Gun_Loop", "Run_Gun_F_Loop", "Reload_Gun_Loop", "Reload_Gun_F_Loop",
        "Pistol_Aim_Neutral", "Pistol_Shoot", "Pistol_Reload", "Death01", "Hit_Chest")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=RIGGED)
tgt_arm = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"][0]
tgt_arm.name = "UniversalRig"
tgt_mesh = [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.name.startswith("Icosphere")]
for o in list(bpy.context.scene.objects):
    if o.type == "MESH" and o.name.startswith("Icosphere"):
        bpy.data.objects.remove(o, do_unlink=True)
bpy.context.view_layer.update()
# ---- unit normalisation, measured in the ARMATURE's own space (bone data, not world bbox:
# the rig node already carries a 0.01 parent scale, and using the world box scaled it twice)
rig_height = max((b.tail_local.z for b in tgt_arm.data.bones), default=1.8)
factor = 1.75 / rig_height
print("RIG_HEIGHT_BONE_SPACE", round(rig_height, 4), "factor", round(factor, 4))
if abs(factor - 1.0) > 0.01:
    for o in list(tgt_mesh) + [tgt_arm]:
        o.scale = o.scale * factor
    bpy.ops.object.select_all(action="DESELECT")
    for o in list(tgt_mesh) + [tgt_arm]:
        o.select_set(True)
    bpy.context.view_layer.objects.active = tgt_arm
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.context.view_layer.update()
print("NORMALISED factor", round(factor, 4))
src_tgt_scale = factor
print("TARGET bones", len(tgt_arm.data.bones))

# clips live on the library rig
b2 = set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=CLIPS)
src_arm = [o for o in bpy.context.scene.objects if o not in b2 and o.type == "ARMATURE"][0]
print("SOURCE bones", len(src_arm.data.bones))

def rel_rest(a):
    out = {}
    for b in a.data.bones:
        if b.parent is None:
            out[b.name] = b.matrix_local.to_quaternion()
        else:
            out[b.name] = (b.parent.matrix_local.inverted() @ b.matrix_local).to_quaternion()
    return out

# parent-relative rest: the pose basis is expressed relative to the parent bone, and the two
# rigs have different parent chains (the Tripo rig has extra twist bones)
src_rest = rel_rest(src_arm)
tgt_rest = rel_rest(tgt_arm)
shared = sorted(set(src_rest) & set(tgt_rest))
print("SHARED bones", len(shared))

clips = [a for a in bpy.data.actions if a.name in KEEP or a.name.startswith(tuple(k.replace("_Loop", "") for k in KEEP))]
if not clips:
    clips = list(bpy.data.actions)
print("CLIPS", [a.name for a in clips])

if tgt_arm.animation_data is None:
    tgt_arm.animation_data_create()

for clip in clips:
    # let the library rig evaluate the clip, then sample it per frame
    if src_arm.animation_data is None:
        src_arm.animation_data_create()
    src_arm.animation_data.action = clip
    try:
        if len(clip.slots):
            src_arm.animation_data.action_slot = clip.slots[0]
    except Exception:
        pass
    start, end = int(clip.frame_range[0]), int(clip.frame_range[1])
    new = bpy.data.actions.new(clip.name)
    tgt_arm.animation_data.action = new
    try:
        if len(new.slots) == 0:
            new.slots.new("OBJECT", tgt_arm.name)
        tgt_arm.animation_data.action_slot = new.slots[0]
    except Exception:
        pass
    for f in range(start, end + 1):
        bpy.context.scene.frame_set(f)
        bpy.context.view_layer.update()
        for name in shared:
            pb_s = src_arm.pose.bones.get(name)
            pb_t = tgt_arm.pose.bones.get(name)
            if pb_s is None or pb_t is None:
                continue
            q_s = pb_s.matrix_basis.to_quaternion()
            Rs = src_rest[name]
            Rt = tgt_rest[name]
            # exactly what scripts/anim_library.gd::borrow does at runtime
            q_t = Rt @ (Rs.inverted() @ q_s)
            pb_t.rotation_mode = "QUATERNION"
            pb_t.rotation_quaternion = q_t
            pb_t.keyframe_insert("rotation_quaternion", frame=f)
    new.use_fake_user = True
    print("RETARGETED", clip.name, "frames", start, end)

src_arm.animation_data.action = None
tgt_arm.animation_data.action = None

bpy.ops.object.select_all(action="DESELECT")
for o in tgt_mesh:
    o.select_set(True)
tgt_arm.select_set(True)
bpy.context.view_layer.objects.active = tgt_arm
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
