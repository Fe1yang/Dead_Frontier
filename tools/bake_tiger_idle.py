"""Bake the lion's dog-family clips onto the white tiger (they share the 19-bone quadruped rig).

The tiger ships with no animation data at all, so the lobby idle would leave it frozen. Both
models use the same bone names, so the clips can be re-expressed on the tiger's own rest pose.

Run: blender -b -P bake_tiger_idle.py
"""
import bpy, os
from mathutils import Quaternion

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
TIGER = ROOT + r"\assets\models\pets\white_tiger.glb"
LION = ROOT + r"\assets\models\pets\lion.glb"
CLIPS = ("Dog_Idle", "Dog_Run", "Dog_Bite")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=TIGER)
tiger = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"][0]

before = set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=LION)
lion = [o for o in bpy.context.scene.objects if o not in before and o.type == "ARMATURE"][0]

src_rest = {b.name: b.matrix_local.to_quaternion() for b in lion.data.bones}
tgt_rest = {b.name: b.matrix_local.to_quaternion() for b in tiger.data.bones}
shared = sorted(set(src_rest) & set(tgt_rest))
print("SHARED", len(shared))

if tiger.animation_data is None:
    tiger.animation_data_create()
if lion.animation_data is None:
    lion.animation_data_create()

for clip in CLIPS:
    act = bpy.data.actions.get(clip)
    if act is None:
        print("MISSING", clip)
        continue
    lion.animation_data.action = act
    try:
        if len(act.slots):
            lion.animation_data.action_slot = act.slots[0]
    except Exception:
        pass
    start, end = int(act.frame_range[0]), int(act.frame_range[1])
    new = bpy.data.actions.new(clip)
    tiger.animation_data.action = new
    try:
        if len(new.slots) == 0:
            new.slots.new("OBJECT", tiger.name)
        tiger.animation_data.action_slot = new.slots[0]
    except Exception:
        pass
    for f in range(start, end + 1):
        bpy.context.scene.frame_set(f)
        bpy.context.view_layer.update()
        for name in shared:
            ps = lion.pose.bones.get(name)
            pt = tiger.pose.bones.get(name)
            if ps is None or pt is None:
                continue
            qs = ps.matrix_basis.to_quaternion()
            qt = tgt_rest[name] @ (src_rest[name].inverted() @ qs)
            pt.rotation_mode = "QUATERNION"
            pt.rotation_quaternion = qt
            pt.keyframe_insert("rotation_quaternion", frame=f)
    new.use_fake_user = True
    print("BAKED", clip, start, end)

lion.animation_data.action = None
tiger.animation_data.action = None

for o in list(bpy.context.scene.objects):
    if o is not tiger and o.type in ("ARMATURE", "EMPTY"):
        bpy.data.objects.remove(o, do_unlink=True)

bpy.ops.object.select_all(action="DESELECT")
for o in bpy.context.scene.objects:
    if o.type == "MESH":
        o.select_set(True)
tiger.select_set(True)
bpy.context.view_layer.objects.active = tiger
bpy.ops.export_scene.gltf(
    filepath=TIGER,
    export_format="GLB",
    use_selection=True,
    export_animations=True,
    export_animation_mode="ACTIONS",
    export_force_sampling=False,
    export_apply=False,
)
print("EXPORTED", TIGER, os.path.getsize(TIGER))
