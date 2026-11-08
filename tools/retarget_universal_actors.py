import bpy
import math
import os
import sys
from pathlib import Path
from mathutils import Vector, Quaternion, Matrix

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / 'assets' / 'animation-library' / 'ual1' / 'UAL1_Standard.glb'
LIBRARY2 = ROOT / 'assets' / 'animation-library' / 'ual2' / 'UAL2_Standard.glb'
SOURCES = {
    'male': ('survivor_male_hd.glb', 'survivor_male_universal.glb', True, False),
    'female': ('survivor_female_hd.glb', 'survivor_female_universal.glb', True, True),
    'medic': ('survivor_medic_hd.glb', 'survivor_medic_universal.glb', True, False),
    'walker': ('zombie_walker_clean_hd.glb', 'zombie_walker_universal.glb', False, False),
    'female_zombie': ('zombie_female_hd.glb', 'zombie_female_universal.glb', False, False),
    'jockey': ('zombie_jockey_hd.glb', 'zombie_jockey_universal.glb', False, False),
    'juggernaut': ('zombie_juggernaut_hd.glb', 'zombie_juggernaut_universal.glb', False, False),
    'merchant': ('merchant_hd.glb', 'merchant_universal.glb', False, False),
    'bomber': ('zombie_bomber_hd.glb', 'zombie_bomber_universal.glb', False, False),
    'bomber_female': ('zombie_bomber_female_hd.glb', 'zombie_bomber_female_universal.glb', False, False),
    'riley': ('survivor_riley_hd.glb', 'survivor_riley_universal.glb', True, True),
    'maya': ('survivor_maya_hd.v3.bak.glb', 'survivor_maya_universal.glb', True, True),
    'maya_tactical': ('survivor_maya_hd.glb', 'survivor_maya_tactical_universal.glb', True, True),
    'jian': ('survivor_jian_hd.glb', 'survivor_jian_universal.glb', True, False),
    'jian_scout': ('survivor_jian_hd.v3quad.bak.glb', 'survivor_jian_scout_universal.glb', True, False),
}
selected = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['male']
UPPER_PREFIXES = ('spine_', 'neck_', 'head', 'clavicle_', 'upperarm_', 'lowerarm_', 'hand_', 'index_', 'middle_', 'pinky_', 'ring_', 'thumb_')

def bounds(obj):
    points = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    low = Vector(tuple(min(v[i] for v in points) for i in range(3)))
    high = Vector(tuple(max(v[i] for v in points) for i in range(3)))
    return low, high

def pose_snapshot(rig, action, frame):
    rig.animation_data.action = action
    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()
    return {pb.name: pb.matrix.copy() for pb in rig.pose.bones}

def set_pose_basis(rig, pose_matrices):
    for pb in rig.pose.bones:
        bone = pb.bone
        desired = pose_matrices[pb.name]
        if pb.parent:
            parent = pb.parent
            relative_rest = parent.bone.matrix_local.inverted() @ bone.matrix_local
            parent_pose = pose_matrices[parent.name]
            basis = (parent_pose @ relative_rest).inverted() @ desired
        else:
            basis = bone.matrix_local.inverted() @ desired
        loc, rot, scale = basis.decompose()
        pb.rotation_mode = 'QUATERNION'
        pb.location = loc
        pb.rotation_quaternion = rot
        pb.scale = scale

def basis_snapshot(rig, action, frame):
    rig.animation_data.action = action
    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()
    return {pb.name: pb.matrix_basis.copy() for pb in rig.pose.bones}

def extended_gun_pose(rig, pistol):
    scene = bpy.context.scene
    rig.animation_data.action = pistol
    scene.frame_set(int(pistol.frame_range[1]))
    targets = []
    # Keep both targets within the 0.55 m arm reach. The previous -0.69
    # forward target was unreachable and dragged both wrists to one side.
    grip_targets = {
        'l': (-0.035, -0.345, 1.355),
        'r': (-0.090, -0.390, 1.395),
    }
    for side, location in grip_targets.items():
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
        target = bpy.context.object
        target.name = 'TemporaryGripTarget_' + side
        constraint = rig.pose.bones['lowerarm_' + side].constraints.new('IK')
        constraint.target = target
        constraint.chain_count = 2
        constraint.iterations = 96
        constraint.use_stretch = False
        targets.append(target)
    scene.frame_set(scene.frame_current)
    bpy.context.view_layer.update()
    for side in ('l', 'r'):
        print('GRIP_IK', side, 'target', tuple(targets[0 if side == 'l' else 1].location), 'wrist', tuple(rig.pose.bones['hand_' + side].head))
    # Constraints change pb.matrix, not pb.matrix_basis. Convert the evaluated
    # world pose back to local basis before removing IK, or the fix is lost.
    evaluated_pose = {pb.name: pb.matrix.copy() for pb in rig.pose.bones}
    for side in ('l', 'r'):
        for constraint in list(rig.pose.bones['lowerarm_' + side].constraints):
            rig.pose.bones['lowerarm_' + side].constraints.remove(constraint)
    for target in targets:
        bpy.data.objects.remove(target, do_unlink=True)
    set_pose_basis(rig, evaluated_pose)
    bpy.context.view_layer.update()
    return {pb.name: pb.matrix_basis.copy() for pb in rig.pose.bones}

def finger_curl(rig, pb, degrees):
    # Derive the hinge from the actual skeleton instead of assuming that
    # every imported finger bends around its local X axis.
    side = '_r' if pb.name.endswith('_r') else '_l'
    direction = pb.bone.vector.normalized()
    across = (rig.pose.bones['pinky_01' + side].bone.head_local - rig.pose.bones['index_01' + side].bone.head_local).normalized()
    palm_normal = across.cross(direction).normalized()
    world_axis = direction.cross(palm_normal).normalized()
    local_axis = (pb.bone.matrix_local.to_3x3().inverted() @ world_axis).normalized()
    sign = -1.0 if side == '_r' else 1.0
    return Quaternion(local_axis, sign * math.radians(degrees))

def write_layered_frame(rig, action, frame, body_basis, arm_basis):
    rig.animation_data.action = action
    bpy.context.scene.frame_set(frame)
    for pb in rig.pose.bones:
        source = arm_basis[pb.name] if pb.name.startswith(UPPER_PREFIXES) else body_basis[pb.name]
        loc, rot, scale = source.decompose()
        # Keep the library's original curled finger pose. The high-detail hands
        # have different proportions from the UE mannequin, so an extra hinge
        # rotation opens and twists them instead of improving the grip.
        pb.rotation_mode = 'QUATERNION'
        pb.location = loc
        pb.rotation_quaternion = rot
        pb.scale = scale
        pb.keyframe_insert(data_path='location', frame=frame, group=pb.name)
        pb.keyframe_insert(data_path='rotation_quaternion', frame=frame, group=pb.name)
        pb.keyframe_insert(data_path='scale', frame=frame, group=pb.name)

def make_run_gun(rig, walk, pistol):
    start = int(walk.frame_range[0])
    end = int(round(walk.frame_range[1]))
    # Bake a true two-handed grip onto the stable, fully weighted body.
    arm_basis = extended_gun_pose(rig, pistol)
    action = bpy.data.actions.new('Run_Gun_Loop')
    for frame in range(start, end + 1):
        body_basis = basis_snapshot(rig, walk, frame)
        write_layered_frame(rig, action, frame, body_basis, arm_basis)
    print('RUN_GUN_BAKED', end - start + 1, 'frames with animated waist and legs')
    return action

def make_reload_gun(rig, walk, reload):
    reload_start = int(reload.frame_range[0])
    reload_end = int(round(reload.frame_range[1]))
    walk_start = int(walk.frame_range[0])
    walk_frames = int(round(walk.frame_range[1])) - walk_start + 1
    action = bpy.data.actions.new('Reload_Gun_Loop')
    for frame in range(reload_start, reload_end + 1):
        arm_basis = basis_snapshot(rig, reload, frame)
        walk_frame = walk_start + ((frame - reload_start) % walk_frames)
        body_basis = basis_snapshot(rig, walk, walk_frame)
        write_layered_frame(rig, action, frame, body_basis, arm_basis)
    print('RELOAD_GUN_BAKED', reload_end - reload_start + 1, 'frames with continuous leg motion')
    return action

# ---- Female movement variant -------------------------------------------------
# The UAL run was captured on a male performer: wide stance and a strong lateral
# hip/torso sway that reads as a side-bent spine ("脊柱侧弯") on the female
# characters. Bake a feminine variant per frame:
#   * thighs rotated a few degrees inward (narrower stance, knees together)
#   * pelvis/spine roll about the forward axis damped to ~60%
#   * pelvis sideways translation damped to ~60%
# Rotations are applied per-bone in absolute (armature) space, so the hierarchy
# never detaches and no mesh weights change.

def _character_axes(rig):
    bones = rig.data.bones
    up = (bones['Head'].head_local - bones['pelvis'].head_local).normalized()
    left = (bones['thigh_l'].head_local - bones['thigh_r'].head_local).normalized()
    toe = bones['ball_l'].head_local - bones['foot_l'].head_local
    fwd = (toe - toe.project(up)).normalized()
    left = fwd.cross(up).normalized()  # re-orthogonalize, keep right-handed frame
    return fwd, up, left

def _rot_about(matrix, pivot, axis, degrees):
    rot = Quaternion(axis, math.radians(degrees)).to_matrix().to_4x4()
    return Matrix.Translation(pivot) @ rot @ Matrix.Translation(-pivot) @ matrix

def _damp_roll(matrix, rest, fwd, left, rot_keep, pos_keep):
    q = matrix.to_quaternion()
    qr = rest.to_quaternion()
    delta = q @ qr.inverted()
    if delta.w < 0.0:
        delta = Quaternion((-delta.x, -delta.y, -delta.z, -delta.w))
    rv = delta.axis * delta.angle
    rv_f = rv.project(fwd)
    rv2 = (rv - rv_f) + rv_f * rot_keep
    damped = Quaternion(rv2.normalized(), rv2.length) if rv2.length > 1e-8 else Quaternion()
    q2 = damped @ qr
    t = matrix.translation
    t2 = t - (t - rest.translation).project(left) * (1.0 - pos_keep)
    return Matrix.Translation(t2) @ q2.to_matrix().to_4x4()

def make_female_variant(rig, source, new_name, adduct_deg=4.0, keep=0.6):
    fwd, up, left = _character_axes(rig)
    bones = rig.data.bones
    rest = {b.name: b.matrix_local.copy() for b in bones}
    damp_names = ('pelvis', 'spine_01', 'spine_02', 'spine_03')
    start, end = int(source.frame_range[0]), int(round(source.frame_range[1]))
    action = bpy.data.actions.new(new_name)
    for frame in range(start, end + 1):
        pose = pose_snapshot(rig, source, frame)
        # Narrower stance: rotate each thigh about the forward axis so the knee
        # moves toward the midline. The sign is chosen per side by testing which
        # direction actually reduces the knee's lateral offset.
        for side in ('l', 'r'):
            thigh = 'thigh_' + side
            pivot = pose[thigh].translation
            knee = pose['calf_' + side].translation
            midline = knee - knee.project(left)
            best = None
            for sign in (1.0, -1.0):
                candidate = _rot_about(pose[thigh], pivot, fwd, sign * adduct_deg)
                knee_new = (candidate @ pose[thigh].inverted() @ Matrix.Translation(knee)).translation
                score = (knee_new - midline).length
                if best is None or score < best[0]:
                    best = (score, candidate)
            pose[thigh] = best[1]
        for name in damp_names:
            pose[name] = _damp_roll(pose[name], rest[name], fwd, left, keep, keep)
        rig.animation_data.action = action
        set_pose_basis(rig, pose)
        for pb in rig.pose.bones:
            pb.keyframe_insert(data_path='location', frame=frame, group=pb.name)
            pb.keyframe_insert(data_path='rotation_quaternion', frame=frame, group=pb.name)
            pb.keyframe_insert(data_path='scale', frame=frame, group=pb.name)
    print('FEMALE_VARIANT_BAKED', new_name, end - start + 1, 'frames')
    return action


def segment_distance(point, bone):
    a = bone.head_local
    ab = bone.tail_local - a
    t = max(0.0, min(1.0, (point - a).dot(ab) / max(ab.length_squared, 0.000001)))
    return (point - (a + ab * t)).length

def refine_hand_weights(rig, target):
    # Surface-nearest transfer can borrow weights from a neighbouring finger.
    # Bind each hand vertex to its nearest anatomical bone segments instead.
    # Only verts BEYOND the wrist (toward the fingers) belong to the hand:
    # the reach sphere otherwise swallows cuff/forearm verts, which corrupts
    # both the deformation and the palm-direction detection in ArmsRelaxed.
    for side in ('l', 'r'):
        names = [b.name for b in rig.data.bones if b.name == 'hand_' + side or b.name.startswith(('index_', 'middle_', 'ring_', 'pinky_', 'thumb_')) and b.name.endswith('_' + side)]
        bones = [rig.data.bones[name] for name in names]
        wrist = rig.data.bones['hand_' + side].head_local
        hand_dir = (rig.data.bones['middle_01_' + side].head_local - wrist).normalized()
        reach = max((b.tail_local - wrist).length for b in bones) + 0.07
        changed = 0
        for vertex in target.data.vertices:
            point = target.matrix_world @ vertex.co
            if (point - wrist).length > reach:
                continue
            if (point - wrist).dot(hand_dir) < -0.035:
                continue
            ranked = sorted((segment_distance(point, bone), bone.name) for bone in bones)[:4]
            weights = [(name, 1.0 / max(distance, 0.002) ** 4) for distance, name in ranked]
            total = sum(weight for _, weight in weights)
            for group in target.vertex_groups:
                group.remove([vertex.index])
            for name, weight in weights:
                target.vertex_groups[name].add([vertex.index], weight / total, 'REPLACE')
            changed += 1
        print('HAND_WEIGHTS', side, changed)

def refine_head_weights(rig, target):
    # Hair strands and cheeks near the neck borrowed spine/clavicle weights from the
    # nearest-point transfer, so they tore across the face when the torso moved.
    # Everything in the head zone rides only the head and neck. The zone must stay
    # tight: the jacket collar lives at |x| up to ~0.19 around z~1.5, and grabbing
    # it makes the shoulders follow the head (516 collar verts on the old export).
    neck = rig.data.bones['neck_01']
    head = rig.data.bones['Head']
    bones = [neck, head]
    cutoff = head.head_local.z - 0.05
    inv = rig.matrix_world.inverted()
    changed = 0
    for vertex in target.data.vertices:
        point = inv @ (target.matrix_world @ vertex.co)
        if point.z < cutoff or abs(point.x) > 0.13:
            continue
        ranked = sorted((segment_distance(point, bone), bone.name) for bone in bones)[:2]
        weights = [(name, 1.0 / max(distance, 0.002) ** 4) for distance, name in ranked]
        total = sum(weight for _, weight in weights)
        for group in target.vertex_groups:
            group.remove([vertex.index])
        for name, weight in weights:
            target.vertex_groups[name].add([vertex.index], weight / total, 'REPLACE')
        changed += 1
    print('HEAD_WEIGHTS', changed)

def refine_armpit_weights(rig, target):
    # The Tripo jacket is a hollow shell: the underarm region was split across
    # clavicle / upperarm / spine / neck, so when ArmsRelaxed drops the arms the
    # panels separate and the hollow interior shows as holes. Pinning the whole band
    # 100% to spine_03 fixed the holes but smeared the fabric ("拉丝") whenever the
    # arm sweeps across the chest. Blend instead: torso side follows spine_03, arm
    # side takes up to 65% upperarm, so the band stretches gradually with the sleeve.
    spine = rig.data.bones['spine_03']
    inv = rig.matrix_world.inverted()
    changed = 0
    for side in ('l', 'r'):
        side_sign = 1.0 if side == 'l' else -1.0
        upper_name = 'upperarm_' + side
        for vertex in target.data.vertices:
            point = inv @ (target.matrix_world @ vertex.co)
            lateral = point.x * side_sign
            if lateral < 0.10 or lateral > 0.21:
                continue
            if point.z < 1.24 or point.z > 1.48:
                continue
            t = (lateral - 0.10) / 0.11
            t = t * t * (3.0 - 2.0 * t)
            w_arm = 0.65 * t
            for group in target.vertex_groups:
                group.remove([vertex.index])
            target.vertex_groups[spine.name].add([vertex.index], 1.0 - w_arm, 'REPLACE')
            if w_arm > 0.0:
                target.vertex_groups[upper_name].add([vertex.index], w_arm, 'REPLACE')
            changed += 1
    print('ARMPIT_WEIGHTS', changed)

def refine_arm_chain(rig, target):
    # Bulkier or narrower bodies fool the nearest-surface transfer: sleeve, wrist and
    # shoulder-cap verts land on the mannequin's neck/head/spine and the run pose then
    # drags the arms across the face. For every vert in the arm band where an arm-chain
    # bone is clearly the closest anatomy (closer than head/neck AND spine), strip the
    # foreign weights and rank among clavicle/upperarm/lowerarm/hand only. On bodies
    # that already transfer cleanly this is a no-op, so it runs for every survivor.
    inv = rig.matrix_world.inverted()
    head_bones = [rig.data.bones['Head'], rig.data.bones['neck_01']]
    spine_bones = [rig.data.bones['spine_02'], rig.data.bones['spine_03']]
    for side in ('l', 'r'):
        sign = 1.0 if side == 'l' else -1.0
        arm_bones = [rig.data.bones[n + '_' + side] for n in ('clavicle', 'upperarm', 'lowerarm', 'hand')]
        changed = 0
        for vertex in target.data.vertices:
            point = inv @ (target.matrix_world @ vertex.co)
            if abs(point.x) < 0.08 or not (1.10 < point.z < 1.66):
                continue
            if point.x * sign < 0.0:
                continue
            d_arm = min(segment_distance(point, b) for b in arm_bones)
            d_head = min(segment_distance(point, b) for b in head_bones)
            d_spine = min(segment_distance(point, b) for b in spine_bones)
            if not (d_arm < d_head and d_arm < d_spine + 0.02):
                continue
            ranked = sorted((segment_distance(point, bone), bone.name) for bone in arm_bones)[:3]
            weights = [(name, 1.0 / max(distance, 0.002) ** 4) for distance, name in ranked]
            total = sum(weight for _, weight in weights)
            for group in target.vertex_groups:
                group.remove([vertex.index])
            for name, weight in weights:
                target.vertex_groups[name].add([vertex.index], weight / total, 'REPLACE')
            changed += 1
        print('ARM_CHAIN', side, changed)

def refine_arm_weights(rig, target):
    # T-pose sleeves sit at head height; any weight they borrow from the neck/head or
    # torso leaves the sleeve hanging mid-air as a "wing" once the arms drop in the
    # run pose. Bind everything outboard at shoulder height to the arm chain.
    inv = rig.matrix_world.inverted()
    for side in ('l', 'r'):
        sign = 1.0 if side == 'l' else -1.0
        bones = [rig.data.bones[n + '_' + side] for n in ('clavicle', 'upperarm', 'lowerarm', 'hand')]
        changed = 0
        for vertex in target.data.vertices:
            point = inv @ (target.matrix_world @ vertex.co)
            if point.x * sign < 0.22 or point.z < 1.40:
                continue
            ranked = sorted((segment_distance(point, bone), bone.name) for bone in bones)[:3]
            weights = [(name, 1.0 / max(distance, 0.002) ** 4) for distance, name in ranked]
            total = sum(weight for _, weight in weights)
            for group in target.vertex_groups:
                group.remove([vertex.index])
            for name, weight in weights:
                target.vertex_groups[name].add([vertex.index], weight / total, 'REPLACE')
            changed += 1
        print('ARM_WEIGHTS', side, changed)

def refine_neckside_weights(rig, target):
    # Dense Tripo collars (Jian) transfer trapezius weights to the clavicle, and
    # the clavicle's aim rotation drags the whole side of the neck up over the
    # chin — "shoulder eats the face". Any clavicle-dominant vert inside the
    # neck column (neck+head height band, off-centre) belongs to neck/head/spine
    # instead. Deltoid verts are upperarm-dominant and stay untouched.
    neck = rig.data.bones['neck_01']
    head = rig.data.bones['Head']
    spine = rig.data.bones['spine_03']
    z_lo = neck.head_local.z - 0.03
    z_hi = head.tail_local.z + 0.01
    bones = [neck, head, spine]
    inv = rig.matrix_world.inverted()
    changed = 0
    for vertex in target.data.vertices:
        point = inv @ (target.matrix_world @ vertex.co)
        if point.z < z_lo or point.z > z_hi:
            continue
        if abs(point.x) < 0.055 or abs(point.x) > 0.34:
            continue
        if not vertex.groups:
            continue
        dominant = max(vertex.groups, key=lambda g: g.weight)
        if not target.vertex_groups[dominant.group].name.startswith('clavicle'):
            continue
        ranked = sorted((segment_distance(point, bone), bone.name) for bone in bones)[:3]
        weights = [(name, 1.0 / max(distance, 0.002) ** 4) for distance, name in ranked]
        total = sum(weight for _, weight in weights)
        for group in target.vertex_groups:
            group.remove([vertex.index])
        for name, weight in weights:
            target.vertex_groups[name].add([vertex.index], weight / total, 'REPLACE')
        changed += 1
    print('NECKSIDE_WEIGHTS', changed)


def refine_shoulder_weights(rig, target):
    # Shoulder/armpit verts that grabbed neck or torso weights droop and pinch when the
    # clavicle rotates. Lock the whole shoulder cap to the clavicle chain instead.
    # The head region is excluded: the clavicle sphere reaches the chin/jaw and must
    # never steal face verts from the head bones.
    spine = rig.data.bones['spine_03']
    head_cutoff = rig.data.bones['neck_01'].head_local.z - 0.02
    inv = rig.matrix_world.inverted()
    for side in ('l', 'r'):
        sign = 1.0 if side == 'l' else -1.0
        clav = rig.data.bones['clavicle_' + side]
        upper = rig.data.bones['upperarm_' + side]
        bones = [spine, clav, upper]
        center = clav.head_local
        radius = (upper.head_local - spine.head_local).length + 0.06
        changed = 0
        for vertex in target.data.vertices:
            point = inv @ (target.matrix_world @ vertex.co)
            if point.z > head_cutoff or point.x * sign < 0.045:
                continue
            if (point - center).length > radius:
                continue
            ranked = sorted((segment_distance(point, bone), bone.name) for bone in bones)[:3]
            weights = [(name, 1.0 / max(distance, 0.002) ** 4) for distance, name in ranked]
            total = sum(weight for _, weight in weights)
            for group in target.vertex_groups:
                group.remove([vertex.index])
            for name, weight in weights:
                target.vertex_groups[name].add([vertex.index], weight / total, 'REPLACE')
            changed += 1
        print('SHOULDER_WEIGHTS', side, changed)

def slim_female(rig, target):
    # Width-only slimming for the female survivors: narrows torso/hips/thighs along the
    # side axis (X), pulls the belly in along depth (Y), and shrinks the arm girth
    # toward the arm bone axis (thinner biceps/forearms, same length and hands).
    # Height, face, hands and feet keep their original shape, so skeleton binding
    # and animations are untouched.
    groups = {g.name: g.index for g in target.vertex_groups}
    torso_idx = [groups[n] for n in ('pelvis', 'spine_01', 'spine_02', 'spine_03') if n in groups]
    thigh_idx = [groups[n] for n in ('thigh_l', 'thigh_r') if n in groups]
    def wsum(v, idx):
        return min(1.0, sum(g.weight for g in v.groups if g.group in idx))
    def wone(v, gi):
        return sum(g.weight for g in v.groups if g.group == gi)
    arm_segments = []
    bones = rig.data.bones
    rw = rig.matrix_world
    pelvis_bone = bones.get('pelvis')
    waist_z = (rw @ pelvis_bone.head_local).z if pelvis_bone else 0.95
    for side in ('r', 'l'):
        up, lo, hd = (bones.get(n + side) for n in ('upperarm_', 'lowerarm_', 'hand_'))
        if up and lo:
            arm_segments.append((groups.get('upperarm_' + side), rw @ up.head_local, rw @ lo.head_local, 0.84))
        if lo and hd:
            arm_segments.append((groups.get('lowerarm_' + side), rw @ lo.head_local, rw @ hd.head_local, 0.88))
    changed = 0
    for v in target.data.vertices:
        co = v.co
        w_torso = wsum(v, torso_idx)
        w_thigh = wsum(v, thigh_idx)
        if w_thigh > 0.0:
            # Fade the thigh slim out above mid-thigh: the hip/crotch zone must slim
            # exactly like the shirt tail (spine/pelvis weighted) or the shirt pokes
            # through the pants.
            fade_leg = min(1.0, max(0.0, (0.88 - co.z) / 0.15))
            fade_leg = fade_leg * fade_leg * (3.0 - 2.0 * fade_leg)
            w_thigh *= fade_leg
        for gi, a, b, keep in arm_segments:
            if gi is None:
                continue
            w = wone(v, gi)
            if w <= 0.0:
                continue
            # Skip torso-blended verts (jacket/shirt side at the armpit): pulling them
            # toward the arm axis shears the fabric when the arm raises.
            if w_torso > 0.25:
                continue
            ab = b - a
            t = max(0.0, min(1.0, (co - a).dot(ab) / ab.length_squared))
            # Fade the slim in over the first 35% of the segment: the shoulder root
            # keeps its original girth so the sleeve seam stays aligned with the torso.
            fade = min(1.0, t / 0.35)
            fade = fade * fade * (3.0 - 2.0 * fade)
            pivot = a + ab * t
            co = pivot + (co - pivot) * (1.0 - (1.0 - keep) * w * fade)
        if w_torso > 0.0 or w_thigh > 0.0:
            co.x *= 1.0 - 0.11 * w_torso - 0.08 * w_thigh
            co.y *= 1.0 - 0.07 * w_torso
        if w_torso > 0.0 and co.z > waist_z:
            # Smooth ramp at the waist: a hard cutoff here showed as a horizontal
            # offset between the upper and lower torso when the waist twists.
            ramp = min(1.0, (co.z - waist_z) / 0.18)
            ramp = ramp * ramp * (3.0 - 2.0 * ramp)
            co.z = waist_z + (co.z - waist_z) * (1.0 - 0.06 * w_torso * ramp)
        if co != v.co:
            v.co = co
            changed += 1
    print('SLIM_FEMALE', target.name, changed, 'vertices narrowed')
    # The torso got 6% shorter above the waist: move the spine bones' rest positions
    # down by the same formula so the animation pivots stay inside the mesh they drive.
    # Pelvis, clavicles, neck and arms stay put — the mesh didn't move there either.
    waist_arm = pelvis_bone.head_local.z if pelvis_bone else None
    if waist_arm is not None:
        bpy.ops.object.select_all(action='DESELECT')
        rig.select_set(True)
        bpy.context.view_layer.objects.active = rig
        bpy.ops.object.mode_set(mode='EDIT')
        for eb in rig.data.edit_bones:
            if eb.name not in ('spine_01', 'spine_02', 'spine_03'):
                continue
            for attr in ('head', 'tail'):
                p = getattr(eb, attr)
                ramp = min(1.0, max(0.0, (p.z - waist_arm) / 0.18))
                ramp = ramp * ramp * (3.0 - 2.0 * ramp)
                p.z = waist_arm + (p.z - waist_arm) * (1.0 - 0.06 * ramp)
                setattr(eb, attr, p)
        bpy.ops.object.mode_set(mode='OBJECT')
        print('SLIM_FEMALE_RIG spine bones shortened 6%% toward waist z=%.3f' % waist_arm)

def weld_shards(target):
    # Tripo v3.1 quad-mode exports arrive as one object but hundreds of
    # unwelded shards (visually coincident boundaries, separate topologies).
    # At rest they look perfect; under animation each shard follows its own
    # nearest bone and the body shears apart ("hands at chin"). Weld first
    # with a tiny threshold — real geometry survives, shard-boundary
    # duplicates fuse — then drop any true stacked duplicate shells.
    import bmesh
    before = len(target.data.vertices)
    bm = bmesh.new()
    bm.from_mesh(target.data)
    merged = bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.0001)
    bm.to_mesh(target.data)
    bm.free()
    print('WELD_SHARDS', before, '->', len(target.data.vertices),
          'merged', len((merged or {}).get('target', [])))
    dedup_shells(target)


def dedup_shells(target):
    # Tripo's high-poly generations can contain several full copies of the body stacked
    # at (nearly) the same spot. Left alone, every copy receives noisy nearest-surface
    # weights and the copies slide apart in game — "stacked chunks of meat". Separate
    # loose parts, cluster them by bounds centre, and keep only the largest cluster;
    # genuinely separate accessories (pouches, bedroll) sit far apart and survive.
    before = len(target.data.vertices)
    snapshot = set(bpy.context.scene.objects)
    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True)
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.object.mode_set(mode='OBJECT')
    parts = [o for o in bpy.context.scene.objects if o not in snapshot and o.type == 'MESH']
    clusters = []  # [{'center': Vector, 'objs': [object]}]
    for o in sorted([target] + parts, key=lambda p: -len(p.data.vertices)):
        c = [o.matrix_world @ Vector(cor) for cor in o.bound_box]
        center = sum(c, Vector()) / 8.0
        placed = False
        for cl in clusters:
            if (cl['center'] - center).length < 0.025:
                cl['objs'].append(o)
                placed = True
                break
        if not placed:
            clusters.append({'center': center, 'objs': [o]})
    keep = max(clusters, key=lambda cl: sum(len(o.data.vertices) for o in cl['objs']))
    if target not in keep['objs']:
        # the container kept a junk layer: swap its geometry for a kept part
        main = keep['objs'][0]
        target.data = main.data
        bpy.data.objects.remove(main, do_unlink=True)
        keep['objs'] = [target] + [o for o in keep['objs'] if o != main]
    else:
        keep['objs'] = [o for o in keep['objs']]
    for cl in clusters:
        if cl is keep:
            continue
        for o in cl['objs']:
            bpy.data.objects.remove(o, do_unlink=True)
    rest = [o for o in keep['objs'] if o != target]
    if rest:
        bpy.ops.object.select_all(action='DESELECT')
        target.select_set(True)
        for o in rest:
            o.select_set(True)
        bpy.context.view_layer.objects.active = target
        bpy.ops.object.join()
    target.name = 'HighDetailCharacter'
    print('DEDUP_SHELLS', before, '->', len(target.data.vertices),
          'parts', len(parts) + 1, 'clusters', len(clusters),
          'kept', sum(len(o.data.vertices) for o in keep['objs']))


def match_tpose(rig, target):
    # Some generated bodies come with the arms hanging at the sides (A-pose/compact,
    # total width ~ body width). The nearest-surface weight transfer then maps sleeve
    # and hand verts onto the mannequin's chest/spine and the run pose drags the arms
    # across the face. Swing the arm bands up to the mannequin's T-pose BEFORE the
    # transfer: pivot at the upperarm head, wrist from the lowest far-lateral verts,
    # rotate every vert near the pivot->wrist line onto the mannequin hand direction.
    # T-pose bodies measure ~0-3 degrees here, so this is a no-op for them.
    for side, sgn in (('l', 1.0), ('r', -1.0)):
        pivot = rig.data.bones['upperarm_' + side].head_local.copy()
        wrist_man = rig.data.bones['hand_' + side].head_local.copy()
        band = [v.index for v in target.data.vertices
                if v.co.z > 0.6 and v.co.z < pivot.z + 0.08 and sgn * v.co.x > 0.08]
        print('TPOSE_PROBE', side, 'band', len(band), 'pivot', tuple(round(v, 3) for v in pivot))
        if not band:
            continue
        lat_max = max(sgn * target.data.vertices[i].co.x for i in band)
        lows = sorted(band, key=lambda i: target.data.vertices[i].co.z)[:max(6, len(band) // 20)]
        wrist_cur = sum((target.data.vertices[i].co for i in lows), Vector()) / len(lows)
        print('TPOSE_PROBE', side, 'lat_max', round(lat_max, 3), 'wrist_cur', tuple(round(v, 3) for v in wrist_cur))
        if sgn * wrist_cur.x < 0.35 * lat_max:  # nothing hanging out there: nothing to do
            continue
        v1 = wrist_cur - pivot
        v2 = wrist_man - pivot
        angle = v1.angle(v2)
        print('TPOSE_PROBE', side, 'angle_deg', round(math.degrees(angle), 2))
        if angle < math.radians(5.0):
            continue
        axis = v1.cross(v2)
        if axis.length < 1e-6:
            continue
        axis.normalize()
        rot = Quaternion(axis, angle).to_matrix().to_4x4()
        arm_dir = v1.normalized()
        changed = 0
        for i in band:
            co = target.data.vertices[i].co
            rel = co - pivot
            along = rel.dot(arm_dir)
            if along < -0.06 or along > v1.length + 0.18:
                continue
            perp = (rel - arm_dir * along).length
            if perp > 0.17:
                continue
            target.data.vertices[i].co = pivot + (rot @ rel)
            changed += 1
        print('TPOSE_MATCH', side, 'degrees', round(math.degrees(angle), 1), 'verts', changed)


def fix_stylized_proportions(target, low, high):
    # Tripo generations come out stylized: an oversized head and short legs next to
    # the realistic Mason body. Rebalance before skinning so Jian matches the cast:
    #   * everything below the waist stretches down ~8% (feet stay on the floor)
    #   * the head above the neck ring shrinks ~15% toward the neck axis, fading in
    #     over the lower head so the jawline does not pinch
    # Total height is then re-normalized, so the silhouette ends up with a smaller
    # head and longer legs at exactly the mannequin's height.
    height = high - low
    waist_z = low + height * 0.53
    neck_z = low + height * 0.80
    ring = [v.co for v in target.data.vertices if abs(v.co.z - neck_z) < height * 0.012]
    if ring:
        px = sum(c.x for c in ring) / len(ring)
        py = sum(c.y for c in ring) / len(ring)
    else:
        px = py = 0.0
    head_changed = leg_changed = 0
    for v in target.data.vertices:
        co = v.co
        if co.z < waist_z:
            co.z = low + (co.z - low) * 1.08
            leg_changed += 1
        if co.z > neck_z:
            t = min(1.0, (co.z - neck_z) / max(height * 0.18, 0.001))
            t = t * t * (3.0 - 2.0 * t)
            s = 1.0 - 0.15 * t
            co.x = px + (co.x - px) * s
            co.y = py + (co.y - py) * s
            head_changed += 1
    print('PROPORTIONS legs_stretched', leg_changed, 'head_shrunk', head_changed,
          'pivot', (round(px, 3), round(py, 3)), 'waist', round(waist_z, 3), 'neck', round(neck_z, 3))
    # Re-normalize: total height and the ground plane must match the mannequin again.
    t_low, t_high = bounds(target)
    s = (high - low) / max(t_high.z - t_low.z, 0.001)
    for v in target.data.vertices:
        v.co.x = (v.co.x - px) * s + px
        v.co.y = (v.co.y - py) * s + py
        v.co.z = low + (v.co.z - t_low.z) * s
    t_low, t_high = bounds(target)
    target.location += Vector((-(t_low.x + t_high.x) / 2 + px * 0.0, -(t_low.y + t_high.y) / 2, low - t_low.z))
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)


def transfer_mesh(rig, source_mesh, filename, slim=False):
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(ROOT / 'assets' / 'models' / 'generated' / filename))
    meshes = [o for o in bpy.context.scene.objects if o not in before and o.type == 'MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    target = bpy.context.object
    target.name = 'HighDetailCharacter'
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    target.rotation_mode = 'XYZ'
    target.rotation_euler.z = -math.pi / 2
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    if not os.environ.get('RETARGET_SKIP_DEDUP'):
        weld_shards(target)
    source_low, source_high = bounds(source_mesh)
    target_low, target_high = bounds(target)
    factor = (source_high.z - source_low.z) / (target_high.z - target_low.z)
    target.scale = (factor,) * 3
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    target_low, target_high = bounds(target)
    target.location += Vector((-(target_low.x + target_high.x) / 2, -(target_low.y + target_high.y) / 2, source_low.z - target_low.z))
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    if 'jian' in filename:
        fix_stylized_proportions(target, source_low.z, source_high.z)
    match_tpose(rig, target)
    # Decimation is OFF: ratio 0.32 collapsed face UV seams into thin sliver
    # triangles that rendered as black streaks in Godot. Keep the original
    # Tripo topology (~28k tris) — the slivers and shading asymmetry disappear.
    if os.environ.get('RETARGET_DECIMATE'):
        decimate = target.modifiers.new('Mobile geometry budget', 'DECIMATE')
        decimate.ratio = float(os.environ['RETARGET_DECIMATE'])
        bpy.ops.object.modifier_apply(modifier=decimate.name)
    for polygon in target.data.polygons:
        polygon.use_smooth = True
    for group in source_mesh.vertex_groups:
        target.vertex_groups.new(name=group.name)
    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True)
    bpy.context.view_layer.objects.active = target
    transfer = target.modifiers.new('Transfer Universal skin weights', 'DATA_TRANSFER')
    transfer.object = source_mesh
    transfer.use_vert_data = True
    transfer.data_types_verts = {'VGROUP_WEIGHTS'}
    # Stable full-body baseline: nearest mannequin weights never leave parts
    # of the realistic mesh unbound. Hand posing is handled separately below.
    transfer.vert_mapping = 'POLYINTERP_NEAREST'
    bpy.ops.object.datalayout_transfer(modifier=transfer.name)
    bpy.ops.object.modifier_apply(modifier=transfer.name)
    if 'survivor_' in filename:
        refine_hand_weights(rig, target)
        refine_shoulder_weights(rig, target)
        refine_head_weights(rig, target)
        refine_arm_weights(rig, target)
        refine_armpit_weights(rig, target)
        refine_arm_chain(rig, target)
        refine_neckside_weights(rig, target)
    if slim:
        slim_female(rig, target)
    missing = sum(1 for v in target.data.vertices if not v.groups)
    world = target.matrix_world.copy()
    target.parent = rig
    target.matrix_world = world
    armature = target.modifiers.new('Universal Armature', 'ARMATURE')
    armature.object = rig
    print('SKIN_TRANSFER', target.name, len(target.data.vertices), 'vertices; missing weights', missing)
    return target

for key in selected:
    source_name, output_name, is_survivor, is_female = SOURCES[key]
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)
    bpy.ops.import_scene.gltf(filepath=str(LIBRARY))
    rig = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
    source_mesh = bpy.data.objects.get('Mannequin')
    second_objects = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(LIBRARY2))
    for obj in set(bpy.context.scene.objects) - second_objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    rig.name = 'UniversalRig'
    rig.animation_data_create()
    target = transfer_mesh(rig, source_mesh, source_name, slim=is_female)
    run_gun = None
    if is_survivor:
        run_gun = make_run_gun(rig, bpy.data.actions['Walk_Loop'], bpy.data.actions['Pistol_Aim_Neutral'])
        make_reload_gun(rig, bpy.data.actions['Walk_Loop'], bpy.data.actions['Pistol_Reload'])
        keep = {'Run_Gun_Loop', 'Reload_Gun_Loop', 'Pistol_Shoot', 'Pistol_Reload', 'Pistol_Aim_Neutral', 'Death01', 'Hit_Chest'}
        if is_female:
            make_female_variant(rig, bpy.data.actions['Run_Gun_Loop'], 'Run_Gun_F_Loop')
            make_female_variant(rig, bpy.data.actions['Reload_Gun_Loop'], 'Reload_Gun_F_Loop')
            keep |= {'Run_Gun_F_Loop', 'Reload_Gun_F_Loop'}
    elif key == 'merchant':
        keep = {'Idle_FoldArms_Loop', 'Idle_Rail_Loop', 'Idle_Talking_Loop'}
    else:
        keep = {'Zombie_Walk_Fwd_Loop', 'Zombie_Idle_Loop', 'Zombie_Scratch', 'Hit_Knockback', 'Death01'}
    for action in list(bpy.data.actions):
        if action.name not in keep:
            bpy.data.actions.remove(action)
    for obj in list(bpy.context.scene.objects):
        if obj.type == 'MESH' and obj != target:
            bpy.data.objects.remove(obj, do_unlink=True)
    default_action = run_gun if run_gun else bpy.data.actions.get('Idle_FoldArms_Loop' if key == 'merchant' else 'Zombie_Walk_Fwd_Loop')
    for action in bpy.data.actions:
        action.use_fake_user = True
    rig.animation_data.action = default_action
    if default_action and default_action.slots:
        rig.animation_data.action_slot = default_action.slots[0]
    print('DEFAULT_ACTION', key, default_action.name if default_action else None)
    bpy.context.scene.frame_set(0)
    bpy.ops.object.select_all(action='DESELECT')
    rig.select_set(True)
    target.select_set(True)
    bpy.context.view_layer.objects.active = rig
    path = ROOT / 'assets' / 'models' / 'actors' / output_name
    bpy.ops.export_scene.gltf(
        filepath=str(path), export_format='GLB', use_selection=True,
        export_animations=True, export_animation_mode='ACTIONS',
        export_frame_range=False, export_force_sampling=True,
        export_apply=False,
    )
    print('UNIVERSAL_ACTOR_EXPORTED', key, path, 'actions', [a.name for a in bpy.data.actions])
    if os.environ.get('RETARGET_SAVE_BLEND'):
        blend = ROOT / 'diagnostics' / ('retarget_%s.blend' % key)
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        print('BLEND_SAVED', blend)
