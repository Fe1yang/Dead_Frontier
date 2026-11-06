import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
PETS = ROOT / 'assets' / 'models' / 'pets'
SOURCE = ROOT / 'assets' / 'blender' / 'pets'
RENDERS = ROOT / 'renders' / 'pets' / 'animation'
RENDERS.mkdir(parents=True, exist_ok=True)
BREEDS = {'doberman': .82, 'german_shepherd': .78, 'czech_wolfdog': .82, 'tibetan_mastiff': .94}


def world_bounds(meshes):
    points = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
    lo = Vector(tuple(min(p[i] for p in points) for i in range(3)))
    hi = Vector(tuple(max(p[i] for p in points) for i in range(3)))
    return lo, hi


def segment_distance(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-8)))
    return (p - (a + ab * t)).length


def add_bone(edit, name, head, tail, parent=None):
    bone = edit.new(name)
    bone.head, bone.tail = head, tail
    if parent:
        bone.parent = edit[parent]
    bone.align_roll(Vector((0, 1, 0)))
    return bone


def make_action(arm, name, frames, pose_fn):
    action = bpy.data.actions.new(name)
    action.use_fake_user = True
    arm.animation_data_create()
    arm.animation_data.action = action
    for frame in frames:
        pose_fn(frame)
        for pb in arm.pose.bones:
            pb.keyframe_insert(data_path='rotation_quaternion', frame=frame, group=pb.name)
            pb.keyframe_insert(data_path='location', frame=frame, group=pb.name)
    # Blender 4.4+ stores channels in action layers.
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for key in fc.keyframe_points:
                        key.interpolation = 'BEZIER'
    track = arm.animation_data.nla_tracks.new()
    track.name = name
    strip = track.strips.new(name, 1, action)
    strip.name = name
    strip.action_frame_start = 1
    strip.action_frame_end = max(frames)
    track.mute = True
    arm.animation_data.action = None
    return action


report = {}
for breed, target_height in BREEDS.items():
    # Always begin with the untouched generated asset, so repeated rigging cannot accumulate
    # modifiers, old actions, parent transforms, or inspection cameras.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ROOT / 'assets' / 'models' / 'generated' / f'{breed}_raw.glb'))
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if not meshes:
        raise RuntimeError(f'No pet mesh: {breed}')
    bpy.context.view_layer.update()
    raw_lo, raw_hi = world_bounds(meshes)
    raw_size = raw_hi-raw_lo
    scale = target_height/raw_size.z
    centre = (raw_lo+raw_hi)*.5
    root = bpy.data.objects.new(f'{breed}_root', None)
    bpy.context.collection.objects.link(root)
    for obj in list(bpy.context.scene.objects):
        if obj != root and obj.parent is None:
            obj.parent = root
    root.scale = (scale, scale, scale)
    root.location = (-centre.x*scale, -centre.y*scale, -raw_lo.z*scale)
    root.rotation_euler.z = -math.pi/2
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.join()
    dog = bpy.context.object
    dog.name = f'{breed}_skin'
    # Bake the preparation root's world transform too. Keeping the old parent here would
    # leave mesh coordinates and armature coordinates in different spaces and tear the skin.
    world_matrix = dog.matrix_world.copy()
    dog.parent = None
    dog.matrix_world = world_matrix
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    lo, hi = world_bounds([dog])
    h = hi.z - lo.z
    length = hi.y - lo.y
    # The prepared dogs stand on z=0 and face Blender -Y / Godot +Z.
    dog.data.transform(__import__('mathutils').Matrix.Translation(Vector((0, 0, -lo.z))))
    dog.location = (0, 0, 0)
    bpy.context.view_layer.update()

    arm_data = bpy.data.armatures.new(f'{breed}_rig')
    arm = bpy.data.objects.new(f'{breed}_rig', arm_data)
    bpy.context.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')

    def v(x, y, z):
        return Vector((x * h, y * h, z * h))

    add_bone(arm_data.edit_bones, 'root', v(0, 0, 0), v(0, 0, .12))
    add_bone(arm_data.edit_bones, 'body', v(0, .15, .51), v(0, -.12, .58), 'root')
    add_bone(arm_data.edit_bones, 'chest', v(0, -.12, .58), v(0, -.28, .64), 'body')
    add_bone(arm_data.edit_bones, 'neck', v(0, -.28, .64), v(0, -.37, .75), 'chest')
    add_bone(arm_data.edit_bones, 'head', v(0, -.37, .75), v(0, -.54, .77), 'neck')
    add_bone(arm_data.edit_bones, 'tail_1', v(0, .27, .55), v(0, .43, .62), 'body')
    add_bone(arm_data.edit_bones, 'tail_2', v(0, .43, .62), v(0, .58, .66), 'tail_1')

    legs = {}
    for side, sx in [('L', 1), ('R', -1)]:
        for end, sy in [('F', -1), ('H', 1)]:
            prefix = f'{end}_{side}'
            if end == 'F':
                joints = [v(sx*.13, sy*.22, .57), v(sx*.13, sy*.19, .34), v(sx*.13, sy*.23, .13), v(sx*.13, sy*.29, .055)]
            else:
                joints = [v(sx*.14, sy*.22, .54), v(sx*.14, sy*.12, .34), v(sx*.14, sy*.28, .15), v(sx*.14, sy*.18, .055)]
            parent = 'chest' if end == 'F' else 'body'
            names = [f'{prefix}_upper', f'{prefix}_lower', f'{prefix}_paw']
            for i, name in enumerate(names):
                add_bone(arm_data.edit_bones, name, joints[i], joints[i+1], parent if i == 0 else names[i-1])
            legs[prefix] = (names, joints)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Heat-weight a closed voxel proxy, then transfer those smooth weights back to the
    # original textured mesh. This avoids both heat failures on open shells and boxy weights.
    for group in list(dog.vertex_groups):
        dog.vertex_groups.remove(group)
    for bone in arm.data.bones:
        dog.vertex_groups.new(name=bone.name)
    proxy = dog.copy()
    proxy.data = dog.data.copy()
    bpy.context.collection.objects.link(proxy)
    proxy.name = f'{breed}_weight_proxy'
    dog.scale = (10, 10, 10)
    proxy.scale = (10, 10, 10)
    arm.scale = (10, 10, 10)
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action='DESELECT')
    proxy.select_set(True)
    bpy.context.view_layer.objects.active = proxy
    remesh = proxy.modifiers.new('Closed weighting surface', 'REMESH')
    remesh.mode = 'VOXEL'
    remesh.voxel_size = .022*h*10
    remesh.use_smooth_shade = True
    bpy.ops.object.modifier_apply(modifier=remesh.name)
    smooth = proxy.modifiers.new('Smooth weighting surface', 'SMOOTH')
    smooth.factor = 1.2
    smooth.iterations = 4
    bpy.ops.object.modifier_apply(modifier=smooth.name)
    bpy.ops.object.select_all(action='DESELECT')
    proxy.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    bpy.ops.object.select_all(action='DESELECT')
    dog.select_set(True)
    bpy.context.view_layer.objects.active = dog
    transfer = dog.modifiers.new('Smooth proxy weights', 'DATA_TRANSFER')
    transfer.object = proxy
    transfer.use_vert_data = True
    transfer.data_types_verts = {'VGROUP_WEIGHTS'}
    transfer.vert_mapping = 'POLYINTERP_NEAREST'
    bpy.ops.object.datalayout_transfer(modifier=transfer.name)
    bpy.ops.object.modifier_apply(modifier=transfer.name)
    bpy.data.objects.remove(proxy, do_unlink=True)
    dog.parent = arm
    modifier = dog.modifiers.new('Quadruped skin', 'ARMATURE')
    modifier.object = arm
    modifier.use_deform_preserve_volume = True
    arm.show_in_front = True
    bpy.context.view_layer.update()

    def reset_pose():
        for pb in arm.pose.bones:
            pb.rotation_mode = 'QUATERNION'
            pb.rotation_quaternion = (1, 0, 0, 0)
            pb.location = (0, 0, 0)

    from mathutils import Quaternion

    def run_pose(frame):
        reset_pose()
        phase = (frame-1) / 12.0 * math.tau
        for prefix in legs:
            offset = 0.0 if prefix in {'F_L', 'H_R'} else math.pi
            s = math.sin(phase + offset)
            c = math.cos(phase + offset)
            arm.pose.bones[f'{prefix}_upper'].rotation_quaternion = Quaternion((1, 0, 0), .52*s)
            arm.pose.bones[f'{prefix}_lower'].rotation_quaternion = Quaternion((1, 0, 0), -.42*s + .12)
            arm.pose.bones[f'{prefix}_paw'].rotation_quaternion = Quaternion((1, 0, 0), -.10*s - .08)
        arm.pose.bones['body'].location.z = .022*h*(.5+.5*math.cos(phase*2))
        arm.pose.bones['neck'].rotation_quaternion = Quaternion((1, 0, 0), .035*math.sin(phase*2))
        arm.pose.bones['tail_1'].rotation_quaternion = Quaternion((0, 0, 1), .10*math.sin(phase))

    def idle_pose(frame):
        reset_pose()
        phase = (frame-1) / 60.0 * math.tau
        arm.pose.bones['chest'].rotation_quaternion = Quaternion((1, 0, 0), .014*math.sin(phase))
        arm.pose.bones['head'].rotation_quaternion = Quaternion((0, 0, 1), .025*math.sin(phase*.5))
        arm.pose.bones['tail_1'].rotation_quaternion = Quaternion((0, 0, 1), .10*math.sin(phase))

    def bite_pose(frame):
        reset_pose()
        phase = (frame-1) / 12.0
        amount = math.sin(phase*math.pi)
        arm.pose.bones['body'].rotation_quaternion = Quaternion((1, 0, 0), -.15*amount)
        arm.pose.bones['neck'].rotation_quaternion = Quaternion((1, 0, 0), -.34*amount)
        arm.pose.bones['head'].rotation_quaternion = Quaternion((1, 0, 0), -.24*amount)
        arm.pose.bones['body'].location = Vector((0, -.07*h*amount, .035*h*amount))
        for prefix in ['F_L', 'F_R']:
            arm.pose.bones[f'{prefix}_upper'].rotation_quaternion = Quaternion((1, 0, 0), -.40*amount)

    make_action(arm, 'Dog_Idle', range(1, 62, 3), idle_pose)
    make_action(arm, 'Dog_Run', range(1, 14), run_pose)
    make_action(arm, 'Dog_Bite', range(1, 14), bite_pose)

    bpy.ops.object.select_all(action='DESELECT')
    dog.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.export_scene.gltf(
        filepath=str(PETS / f'{breed}.glb'), export_format='GLB', use_selection=True,
        export_apply=True, export_animations=True, export_animation_mode='NLA_TRACKS',
        export_force_sampling=True, export_frame_range=False, export_skins=True,
        export_all_influences=False, export_def_bones=False,
    )
    # Leave the source in its neutral rest pose, with animation tracks available.
    reset_pose()
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE / f'{breed}.blend'))

    # Side-view action frame for visual inspection.
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.world = bpy.data.worlds.new(f'{breed}_inspection_world')
    scene.world.color = (.12, .12, .12)
    bpy.ops.object.camera_add(location=(2.4, 0, .75*h))
    camera = bpy.context.object
    camera.rotation_euler = (Vector((0, 0, .45*h))-camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = max(1.25, h*1.55)
    scene.camera = camera
    for name, loc, energy, size in [
        ('Key', (1.5, -2.0, 3.0), 450, 2.5),
        ('Fill', (-2.0, 1.0, 2.0), 300, 2.0),
    ]:
        data = bpy.data.lights.new(name, 'AREA')
        data.energy, data.size = energy, size
        obj = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(obj)
        obj.location = loc
        obj.rotation_euler = (Vector((0, 0, .45*h))-obj.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.resolution_x = 720
    scene.render.resolution_y = 540
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = str(RENDERS / f'{breed}-run.png')
    arm.animation_data.action = bpy.data.actions['Dog_Run']
    scene.frame_set(4)
    bpy.ops.render.render(write_still=True)
    report[breed] = {'height_m': h, 'vertices': len(dog.data.vertices), 'bones': len(arm.data.bones), 'clips': ['Dog_Idle', 'Dog_Run', 'Dog_Bite']}
    print('PET_RIGGED', breed, report[breed], flush=True)

(ROOT / 'diagnostics' / 'pet-animation-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('ALL_PETS_RIGGED', flush=True)
