import bpy, math
from mathutils import Vector, Matrix
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ROOT+r"\assets\animation-library\ual1\UAL1_Standard.glb")
arm=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"][0]
for o in list(bpy.context.scene.objects):
    if o.type=="MESH": bpy.data.objects.remove(o, do_unlink=True)
def axes(tag):
    b=arm.data.bones["upperarm_r"]
    print(tag, "head", tuple(round(v,2) for v in b.head_local), "tail", tuple(round(v,2) for v in b.tail_local))
    print(tag, "X", tuple(round(v,2) for v in b.x_axis), "Y", tuple(round(v,2) for v in b.y_axis), "Z", tuple(round(v,2) for v in b.z_axis), "roll_deg", round(math.degrees(b.matrix_local.to_euler().y),1))
axes("BEFORE")
bpy.context.view_layer.objects.active=arm
bpy.ops.object.mode_set(mode="EDIT")
eb=arm.data.edit_bones
sh=eb["upperarm_r"].head.copy()
ang=math.radians(87.0)
rot=Matrix.Rotation(-1*ang,3,"Y")
for n in ("upperarm_r","lowerarm_r","hand_r"):
    e=eb[n]
    e.head=sh+rot@(e.head-sh); e.tail=sh+rot@(e.tail-sh)
bpy.ops.object.mode_set(mode="OBJECT")
axes("AFTER_HEADTAIL_ONLY")