import bpy
import math
from pathlib import Path
from mathutils import Vector, Quaternion, Matrix

ROOT = Path(__file__).resolve().parents[1]
BLEND = ROOT / 'assets/blender/pursuer_abomination.blend'
OUT = ROOT / 'assets/models/actors/pursuer_abomination.glb'
RENDER_DIR = ROOT / 'diagnostics/intro'
RENDER_DIR.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
rig = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
mesh = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
scene = bpy.context.scene

# The old donor weights attached parts of the lateral torso to the walking limbs. Keep the
# actual arms free, but bind the trunk's side muscles back to the spine so they stay put.
limb_prefixes = ('upperarm_', 'lowerarm_', 'hand_', 'index_', 'middle_', 'ring_', 'pinky_', 'thumb_', 'thigh_', 'calf_', 'foot_', 'ball_')
group_names = {g.index: g.name for g in mesh.vertex_groups}
fixed_vertices = 0
moved_weight = 0.0
for vertex in mesh.data.vertices:
    co = vertex.co
    side_limit = .32 if co.z > 1.35 else .36
    if not (.88 < co.z < 1.49 and abs(co.x) < side_limit):
        continue
    weights = {group_names[g.group]: g.weight for g in vertex.groups if g.weight > 0}
    limbs = [name for name in weights if name.startswith(limb_prefixes)]
    amount = sum(weights[name] for name in limbs)
    if amount <= .001:
        continue
    for name in limbs:
        weights.pop(name)
    target = 'spine_02' if co.z < 1.24 else 'spine_03'
    weights[target] = weights.get(target, 0.0) + amount
    total = sum(weights.values())
    if total <= 0:
        continue
    weights = dict(sorted(weights.items(), key=lambda item: item[1], reverse=True)[:4])
    total = sum(weights.values())
    for group in list(vertex.groups):
        mesh.vertex_groups[group.group].remove([vertex.index])
    for name, weight in weights.items():
        mesh.vertex_groups[name].add([vertex.index], weight/total, 'REPLACE')
    fixed_vertices += 1
    moved_weight += amount
print('TORSO_SIDE_WEIGHTS_FIXED', fixed_vertices, 'vertices', round(moved_weight, 3), 'weight', flush=True)

scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 33
rig.animation_data_clear()
# ACTIONS mode exports every datablock, including the retired sine-gait action.
# Remove it so Godot cannot accidentally play the old clip under the same name.
for old_action in list(bpy.data.actions):
    bpy.data.actions.remove(old_action)
rig.animation_data_create()
action = bpy.data.actions.new('Pursuer_Run')
rig.animation_data.action = action
if action.slots:
    rig.animation_data.action_slot = action.slots[0]
for pb in rig.pose.bones:
    pb.rotation_mode = 'QUATERNION'


def rotate_world_x(name, angle):
    bone = rig.data.bones[name]
    axis = (bone.matrix_local.to_3x3().inverted() @ Vector((1, 0, 0))).normalized()
    rig.pose.bones[name].rotation_quaternion = Quaternion(axis, angle)


def point_bone(name, head, target):
    rest = rig.data.bones[name]
    rest_dir = (rest.tail_local-rest.head_local).normalized()
    direction = (target-head).normalized()
    rotation = rest_dir.rotation_difference(direction).to_matrix() @ rest.matrix_local.to_3x3()
    rig.pose.bones[name].matrix = Matrix.Translation(head) @ rotation.to_4x4()
    bpy.context.view_layer.update()


def solve_leg(side, cycle):
    # The stance foot moves backwards at road speed; the swing foot lifts and returns.
    stride = .82
    stance = .58
    ankle_height = .10
    if cycle < stance:
        u = cycle/stance
        y = -stride/2+stride*u
        z = ankle_height
        pitch = 0.0
    else:
        u = (cycle-stance)/(1.0-stance)
        smooth = u*u*(3.0-2.0*u)
        y = stride/2-stride*smooth
        z = ankle_height+.18*math.sin(math.pi*u)
        pitch = -.13*math.sin(math.pi*u)
    thigh = rig.pose.bones['thigh_'+side]
    calf = rig.pose.bones['calf_'+side]
    foot = rig.pose.bones['foot_'+side]
    hip = thigh.head.copy()
    ankle = Vector((hip.x, y, z))
    l1 = rig.data.bones['thigh_'+side].length
    l2 = rig.data.bones['calf_'+side].length
    delta = ankle-hip
    distance = max(.001, delta.length)
    max_distance = (l1+l2)*.985
    if distance > max_distance:
        ankle = hip+delta*(max_distance/distance)
        delta = ankle-hip
        distance = max_distance
    along = delta/distance
    bend = Vector((0, -1, 0))
    bend = (bend-along*bend.dot(along)).normalized()
    a = (l1*l1-l2*l2+distance*distance)/(2.0*distance)
    h = math.sqrt(max(0.0, l1*l1-a*a))
    knee = hip+along*a+bend*h
    point_bone('thigh_'+side, hip, knee)
    point_bone('calf_'+side, knee, ankle)
    rest = rig.data.bones['foot_'+side]
    rotation = Matrix.Rotation(pitch, 3, 'X') @ rest.matrix_local.to_3x3()
    foot.matrix = Matrix.Translation(ankle) @ rotation.to_4x4()
    bpy.context.view_layer.update()


for frame in range(1, 34, 2):
    scene.frame_set(frame)
    unit = (frame-1)/32.0
    phase = unit*math.tau
    for pb in rig.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    # A heavy, slightly lowered centre of mass; the feet remain on the ground in stance.
    bob = -.13+.018*math.cos(phase*2)
    root = rig.pose.bones['root']
    root.location = rig.data.bones['root'].matrix_local.to_3x3().inverted() @ Vector((0, 0, bob))
    rotate_world_x('pelvis', -.035)
    rotate_world_x('spine_02', -.075)
    rotate_world_x('Head', .045)
    bpy.context.view_layer.update()
    for side, offset in [('l', 0.0), ('r', .5)]:
        swing = math.sin(phase+offset*math.tau)
        rotate_world_x('upperarm_'+side, -.18+swing*.30)
        rotate_world_x('lowerarm_'+side, -.32-max(0, -swing)*.14)
        rotate_world_x('hand_'+side, .08)
        solve_leg(side, (unit+offset) % 1.0)
    for pb in rig.pose.bones:
        pb.keyframe_insert(data_path='location', frame=frame, group=pb.name)
        pb.keyframe_insert(data_path='rotation_quaternion', frame=frame, group=pb.name)
        pb.keyframe_insert(data_path='scale', frame=frame, group=pb.name)

scene.frame_set(1)
bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
mesh.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.export_scene.gltf(filepath=str(OUT), export_format='GLB', use_selection=True, export_animations=True, export_animation_mode='ACTIONS', export_frame_range=True, export_force_sampling=True, export_apply=False)
print('PURSUER_RUN_EXPORTED', OUT, flush=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))

scene.render.engine = 'CYCLES'
scene.cycles.samples = 20
scene.cycles.use_denoising = True
scene.world = bpy.data.worlds.new('PursuerRunPreviewWorld')
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
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 1))-light.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(2.8, -5.2, 2.4))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, 0, .95))-camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 2.45
scene.camera = camera
scene.render.resolution_x = 700
scene.render.resolution_y = 700
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
for frame in (1, 9, 17, 25):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    path = RENDER_DIR / ('pursuer-run-%02d.png' % frame)
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    print('RUN_FRAME_RENDERED', frame, path, flush=True)
