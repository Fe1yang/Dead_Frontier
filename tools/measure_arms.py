import bpy, sys
from mathutils import Vector
src=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\generated\survivor_jian_hd.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0]
if len(meshes)>1: bpy.ops.object.join()
body=bpy.context.view_layer.objects.active
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
box=[body.matrix_world @ Vector(c) for c in body.bound_box]
h=max(v.z for v in box)-min(v.z for v in box)
tip=max(abs(v.co.x) for v in body.data.vertices)
print("MESH height=%.3f arm_tip_x=%.3f ratio_tip_to_height=%.3f" % (h, tip, tip/h))
# rig reference: hand bone x on the UAL rig is 0.74 for a 1.65 tall rig
print("RIG expected tip for same height: %.3f" % (0.74/1.65*h))
print("SCALE_TO_MATCH=%.4f" % ((0.74/1.65*h)/tip))
print("MEASURE_DONE")
