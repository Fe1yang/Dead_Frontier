import bpy
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'assets/models/generated/pursuer_abomination.glb'
BOSS = ROOT / 'assets/blender/boss_chaser.blend'
OUT_MODEL = ROOT / 'assets/models/actors/pursuer_abomination.glb'
OUT_BLEND = ROOT / 'assets/blender/pursuer_abomination.blend'
RENDER = ROOT / 'diagnostics/intro/pursuer-rest.png'
RENDER.parent.mkdir(parents=True, exist_ok=True)


def bounds(obj):
    points = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    low = Vector(tuple(min(v[i] for v in points) for i in range(3)))
    high = Vector(tuple(max(v[i] for v in points) for i in range(3)))
    return low, high


def set_bone(arm, name, head, tail):
    bone = arm.data.edit_bones[name]
    bone.head = head
    bone.tail = tail


bpy.ops.wm.open_mainfile(filepath=str(BOSS))
rig = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
rig.name = 'UniversalRig'
rig.animation_data_clear()
old_objects = set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))
meshes = [o for o in bpy.context.scene.objects if o not in old_objects and o.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')
for obj in meshes:
    obj.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = 'PursuerAbomination'
mesh.rotation_mode = 'XYZ'
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.context.view_layer.update()
low, high = bounds(mesh)
# This Tripo output stores height on Z, width on Y and depth on X.
# Turn its width onto Blender X so it shares the mannequin's forward -Y axis.
if high.y - low.y > high.x - low.x:
    mesh.rotation_euler.z = -math.pi / 2
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    bpy.context.view_layer.update()
low, high = bounds(mesh)
factor = 1.84 / (high.z - low.z)
mesh.scale = (factor,) * 3
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.context.view_layer.update()
low, high = bounds(mesh)
mesh.location += Vector((-(low.x + high.x) / 2, -(low.y + high.y) / 2, -low.z))
bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
bpy.context.view_layer.update()
print('NORMALIZED_BOUNDS', bounds(mesh), flush=True)
# Keep enough geometry for close-up organic muscle and facial detail.
decimate = mesh.modifiers.new('Game geometry budget', 'DECIMATE')
decimate.ratio = 0.042
if hasattr(decimate, 'use_collapse_triangulate'):
    decimate.use_collapse_triangulate = True
bpy.ops.object.modifier_apply(modifier=decimate.name)
for polygon in mesh.data.polygons:
    polygon.use_smooth = True
print('OPTIMIZED_MESH', len(mesh.data.vertices), 'vertices', len(mesh.data.polygons), 'polygons', flush=True)

# Fit the Universal skeleton to this creature's long-armed A-pose instead of
# transferring weights from a T-posed mannequin.
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='EDIT')
set_bone(rig, 'pelvis', (0, 0, .87), (0, 0, .99))
set_bone(rig, 'spine_01', (0, 0, .99), (0, 0, 1.13))
set_bone(rig, 'spine_02', (0, 0, 1.13), (0, 0, 1.30))
set_bone(rig, 'spine_03', (0, 0, 1.30), (0, 0, 1.47))
set_bone(rig, 'neck_01', (0, 0, 1.47), (0, -.005, 1.61))
set_bone(rig, 'Head', (0, -.005, 1.61), (0, -.01, 1.82))
old_hand_dirs = {}
new_hand_dirs = {}
for side, sign in [('l', 1), ('r', -1)]:
    shoulder = Vector((sign * .33, .015, 1.43))
    elbow = Vector((sign * .58, .015, 1.03))
    wrist = Vector((sign * .77, -.015, .72))
    palm = Vector((sign * .85, -.025, .56))
    set_bone(rig, 'clavicle_' + side, (sign * .025, -.01, 1.44), shoulder)
    set_bone(rig, 'upperarm_' + side, shoulder, elbow)
    set_bone(rig, 'lowerarm_' + side, elbow, wrist)
    old_hand = rig.data.edit_bones['hand_' + side]
    old_hand_dirs[side] = (old_hand.tail - old_hand.head).normalized()
    new_hand_dirs[side] = (palm - wrist).normalized()
    set_bone(rig, 'hand_' + side, wrist, palm)
    hip = Vector((sign * .15, .015, .89))
    knee = Vector((sign * .17, .015, .49))
    ankle = Vector((sign * .18, .015, .10))
    toe = Vector((sign * .18, -.15, .035))
    set_bone(rig, 'thigh_' + side, hip, knee)
    set_bone(rig, 'calf_' + side, knee, ankle)
    set_bone(rig, 'foot_' + side, ankle, toe)
    set_bone(rig, 'ball_' + side, toe, (sign * .18, -.24, .035))
    set_bone(rig, 'ball_leaf_' + side, (sign * .18, -.24, .035), (sign * .18, -.30, .035))
# Move finger rests rigidly with the new wrist and palm direction.
for side in ('l', 'r'):
    hand = rig.data.edit_bones['hand_' + side]
    rotation = old_hand_dirs[side].rotation_difference(new_hand_dirs[side])
    wrist = hand.head.copy()
    for bone in rig.data.edit_bones:
        if bone.name.endswith('_' + side) and bone.name.startswith(('index_', 'middle_', 'ring_', 'pinky_', 'thumb_')):
            # Original finger positions are relative to the old T-pose wrist.
            original = bpy.data.armatures.get(rig.data.name)
            # Use the current offset from the hand; these bones still retain their old rests.
            old_wrist = Vector((.7389 if side == 'l' else -.7389, .0654, 1.4408))
            head = wrist + rotation @ (bone.head - old_wrist)
            tail = wrist + rotation @ (bone.tail - old_wrist)
            bone.head = head
            bone.tail = tail
bpy.ops.object.mode_set(mode='OBJECT')

# Heat-bind the optimized original mesh to the fitted skeleton.
bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True)
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
print('HEAT_BIND_COMPLETE', len(mesh.vertex_groups), 'groups', flush=True)
unweighted = [v.index for v in mesh.data.vertices if not v.groups]
print('UNWEIGHTED_VERTICES', len(unweighted), flush=True)
if unweighted:
    mesh.vertex_groups['pelvis'].add(unweighted, 1.0, 'REPLACE')
# Clamp and normalize heat weights, retaining the four strongest influences.
for vertex in mesh.data.vertices:
    weights = sorted(((g.group, min(1.0, max(0.0, g.weight))) for g in vertex.groups), key=lambda item: item[1], reverse=True)[:4]
    total = sum(weight for _, weight in weights)
    if total <= 0:
        continue
    for group_index, _ in weights:
        mesh.vertex_groups[group_index].remove([vertex.index])
    for group_index, weight in weights:
        mesh.vertex_groups[group_index].add([vertex.index], weight / total, 'REPLACE')
mesh.data.validate(verbose=True)

# Remove every old mesh and export only the new creature and its fitted rig.
for obj in list(bpy.context.scene.objects):
    if obj.type == 'MESH' and obj != mesh:
        bpy.data.objects.remove(obj, do_unlink=True)
rig.animation_data_clear()
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
mesh.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))
bpy.ops.export_scene.gltf(filepath=str(OUT_MODEL), export_format='GLB', use_selection=True, export_animations=False, export_apply=False)
print('PURSUER_EXPORTED', OUT_MODEL, flush=True)

# Neutral three-quarter render for visual verification.
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.world = bpy.data.worlds.new('PursuerPreviewWorld')
scene.world.use_nodes = True
background = next((n for n in scene.world.node_tree.nodes if n.bl_idname == 'ShaderNodeBackground'), None)
if background is None:
    background = scene.world.node_tree.nodes.new('ShaderNodeBackground')
    output = next((n for n in scene.world.node_tree.nodes if n.bl_idname == 'ShaderNodeOutputWorld'), None)
    if output is None:
        output = scene.world.node_tree.nodes.new('ShaderNodeOutputWorld')
    scene.world.node_tree.links.new(background.outputs[0], output.inputs[0])
background.inputs[0].default_value = (.12, .14, .16, 1)
background.inputs[1].default_value = .65
for name, loc, power, size in [('Key', (2, -4, 4), 650, 4), ('Fill', (-3, -2, 2.5), 420, 3), ('Rim', (1, 2, 3.5), 650, 3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.shape = 'DISK'
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 1)) - light.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(2.6, -5.4, 2.45))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, 0, .95)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 2.35
scene.camera = camera
scene.render.resolution_x = 800
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(RENDER)
bpy.ops.render.render(write_still=True)
print('PURSUER_RENDERED', RENDER, flush=True)
