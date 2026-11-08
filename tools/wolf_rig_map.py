"""Give the gray wolf the game's dog bone names and bake the dog clips onto it.

The pet system poses the rig procedurally by bone name (dog_gallop.gd) and plays Dog_Idle /
Dog_Run / Dog_Bite from the model. So the wolf's Tripo bones are renamed to the dog set and
the old dog's clips are retargeted by name (rest-relative, like scripts/anim_library.gd).

Run: blender -b -P wolf_rig_map.py
"""
import bpy, os
from mathutils import Quaternion, Vector

WOLF = r"C:\Users\user\Downloads\gray wolf 3d model.glb"
DOG = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\pets\czech_wolfdog_prev.glb"
OUT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\pets\czech_wolfdog.glb"
CLIPS = ("Dog_Idle", "Dog_Run", "Dog_Bite")

# wolf bone -> dog bone
MAP = {
    "tripo::Root": "root",
    "tripo::Spine_0": "body",
    "tripo::Spine_1": "chest",
    "tripo::Head_0": "neck",
    "tripo::Head_1": "head",
    "tripo::0_Left_Limb_0": "F_L_upper",
    "tripo::0_Left_Limb_1": "F_L_lower",
    "tripo::0_Left_Limb_2": "F_L_paw",
    "tripo::0_Left_Limb_3": "F_L_toe",
    "tripo::0_Right_Limb_0": "F_R_upper",
    "tripo::0_Right_Limb_1": "F_R_lower",
    "tripo::0_Right_Limb_2": "F_R_paw",
    "tripo::0_Right_Limb_3": "F_R_toe",
    "tripo::1_Left_Limb_0": "H_L_upper",
    "tripo::1_Left_Limb_1": "H_L_lower",
    "tripo::1_Left_Limb_2": "H_L_paw",
    "tripo::1_Left_Limb_3": "H_L_toe",
    "tripo::1_Right_Limb_0": "H_R_upper",
    "tripo::1_Right_Limb_1": "H_R_lower",
    "tripo::1_Right_Limb_2": "H_R_paw",
}

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=WOLF)
wolf = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"][0]
wolf.name = "UniversalRig"
WOLF_MESHES = {o.name for o in bpy.context.scene.objects if o.type == "MESH"}
print("WOLF_MESHES", len(WOLF_MESHES))

bpy.context.view_layer.objects.active = wolf
bpy.ops.object.mode_set(mode="EDIT")
eb = wolf.data.edit_bones
for old, new in MAP.items():
    if old in eb:
        eb[old].name = new
bpy.ops.object.mode_set(mode="OBJECT")
print("RENAMED", len(MAP))

# source clips
before = set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=DOG)
src = [o for o in bpy.context.scene.objects if o not in before and o.type == "ARMATURE"][0]
src_rest = {b.name: b.matrix_local.to_quaternion() for b in src.data.bones}
tgt_rest = {b.name: b.matrix_local.to_quaternion() for b in wolf.data.bones}
shared = sorted(set(src_rest) & set(tgt_rest))
print("SHARED", shared)

if wolf.animation_data is None:
    wolf.animation_data_create()
if src.animation_data is None:
    src.animation_data_create()

made = 0
for clip in CLIPS:
    act = bpy.data.actions.get(clip)
    if act is None:
        continue
    src.animation_data.action = act
    try:
        if len(act.slots):
            src.animation_data.action_slot = act.slots[0]
    except Exception:
        pass
    start, end = int(act.frame_range[0]), int(act.frame_range[1])
    new = bpy.data.actions.new(clip)
    wolf.animation_data.action = new
    try:
        if len(new.slots) == 0:
            new.slots.new("OBJECT", wolf.name)
        wolf.animation_data.action_slot = new.slots[0]
    except Exception:
        pass
    for f in range(start, end + 1):
        bpy.context.scene.frame_set(f)
        bpy.context.view_layer.update()
        for name in shared:
            ps = src.pose.bones.get(name)
            pt = wolf.pose.bones.get(name)
            if ps is None or pt is None:
                continue
            qs = ps.matrix_basis.to_quaternion()
            Rt = tgt_rest[name]
            Rs = src_rest[name]
            qt = Rt @ (Rs.inverted() @ qs)
            pt.rotation_mode = "QUATERNION"
            pt.rotation_quaternion = qt
            pt.keyframe_insert("rotation_quaternion", frame=f)
    new.use_fake_user = True
    made += 1
    print("BAKED", clip, start, end)

src.animation_data.action = None
wolf.animation_data.action = None
print("ACTIONS", [a.name for a in bpy.data.actions])

# drop everything that came from the dog file: its rig, its empties AND its meshes, otherwise
# the export carries the old dog alongside the wolf
for o in list(bpy.context.scene.objects):
    if o is wolf:
        continue
    if o.type in ("ARMATURE", "EMPTY") or (o.type == "MESH" and o.name not in WOLF_MESHES):
        bpy.data.objects.remove(o, do_unlink=True)

bpy.ops.object.select_all(action="DESELECT")
for o in bpy.context.scene.objects:
    if o.type == "MESH":
        o.select_set(True)
wolf.select_set(True)
bpy.context.view_layer.objects.active = wolf
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
