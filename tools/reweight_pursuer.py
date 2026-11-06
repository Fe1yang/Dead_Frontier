import bpy
from pathlib import Path
from mathutils import Matrix

ROOT = Path(__file__).resolve().parents[1]
TARGET_BLEND = ROOT / 'assets/blender/pursuer_abomination.blend'
SOURCE_GLB = ROOT / 'assets/models/actors/boss_chaser.glb'
bpy.ops.wm.open_mainfile(filepath=str(TARGET_BLEND))
target_rig = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
target = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
target_rig.animation_data_clear()
for pb in target_rig.pose.bones:
    pb.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.update()

# Use only the old creature's clean skin weights, never its visible geometry.
# A fresh glTF import avoids carrying over the source file's animation state.
existing = set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=str(SOURCE_GLB))
imported = [o for o in bpy.context.scene.objects if o not in existing]
source_rig = next(o for o in imported if o.type == 'ARMATURE')
source = next(o for o in imported if o.type == 'MESH' and len(o.vertex_groups) > 0)
source_rig.name = 'WeightSourceRig'
source.name = 'WeightSourceMesh'
source_rig.animation_data_clear()
source_rig.matrix_world = Matrix.Identity(4)
bpy.context.view_layer.update()

# Pose every source bone onto the new creature's fitted rest joints. Scaling the
# local bone axis also aligns its length, so the weight donor follows the long arms.
bones = list(source_rig.data.bones)
def visit(bone):
    pb = source_rig.pose.bones[bone.name]
    target_bone = target_rig.data.bones[bone.name]
    desired = target_bone.matrix_local.copy()
    ratio = target_bone.length / max(bone.length, .0001)
    desired = desired @ Matrix.Diagonal((1.0, ratio, 1.0, 1.0))
    pb.matrix = desired
    bpy.context.view_layer.update()
    for child in bone.children:
        visit(child)
for bone in bones:
    if bone.parent is None:
        visit(bone)
bpy.context.view_layer.update()
print('WEIGHT_DONOR_FITTED', flush=True)

# Replace the failed heat weights with smooth interpolated weights from the fitted donor.
target.vertex_groups.clear()
for group in source.vertex_groups:
    target.vertex_groups.new(name=group.name)
bpy.ops.object.select_all(action='DESELECT')
target.select_set(True)
bpy.context.view_layer.objects.active = target
transfer = target.modifiers.new('Smooth fitted skin transfer', 'DATA_TRANSFER')
transfer.object = source
transfer.use_vert_data = True
transfer.data_types_verts = {'VGROUP_WEIGHTS'}
transfer.vert_mapping = 'POLYINTERP_NEAREST'
bpy.ops.object.datalayout_transfer(modifier=transfer.name)
bpy.ops.object.modifier_apply(modifier=transfer.name)
print('WEIGHTS_TRANSFERRED', flush=True)

# Limit to four normalized influences for Godot/mobile compatibility.
for vertex in target.data.vertices:
    weights = sorted(((g.group, min(1.0, max(0.0, g.weight))) for g in vertex.groups), key=lambda item: item[1], reverse=True)[:4]
    total = sum(weight for _, weight in weights)
    if total <= 0:
        target.vertex_groups['pelvis'].add([vertex.index], 1.0, 'REPLACE')
        continue
    for group_index, _ in weights:
        target.vertex_groups[group_index].remove([vertex.index])
    for group_index, weight in weights:
        target.vertex_groups[group_index].add([vertex.index], weight / total, 'REPLACE')
missing = sum(1 for v in target.data.vertices if not v.groups)
print('UNWEIGHTED_AFTER_TRANSFER', missing, flush=True)
bpy.data.objects.remove(source, do_unlink=True)
bpy.data.objects.remove(source_rig, do_unlink=True)
bpy.ops.object.select_all(action='DESELECT')
target_rig.select_set(True)
target.select_set(True)
bpy.context.view_layer.objects.active = target_rig
bpy.ops.wm.save_as_mainfile(filepath=str(TARGET_BLEND))
print('PURSUER_REWEIGHTED', TARGET_BLEND, flush=True)
