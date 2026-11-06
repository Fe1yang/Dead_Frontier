from pathlib import Path
import hashlib
import json
import shutil
import struct

import numpy as np
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'assets/models/actors/survivor_medic_universal.glb'
BACKUP = ROOT / 'work/survivor_medic_universal.before-arm-fix.glb'
if not BACKUP.exists():
    shutil.copy2(PATH, BACKUP)

raw = bytearray(PATH.read_bytes())
json_length = struct.unpack_from('<I', raw, 12)[0]
data = json.loads(raw[20:20 + json_length])
binary_start = 20 + json_length + 8
binary = memoryview(raw)[binary_start:]
primitive = data['meshes'][0]['primitives'][0]
skin = data['skins'][0]
joint_names = [data['nodes'][node].get('name', '') for node in skin['joints']]
name_to_joint = {name: index for index, name in enumerate(joint_names)}

COMPONENTS = {'VEC3': 3, 'VEC4': 4, 'MAT4': 16}
DTYPES = {5126: np.dtype('<f4'), 5121: np.dtype('u1'), 5123: np.dtype('<u2')}

def accessor(index):
    a = data['accessors'][index]
    view = data['bufferViews'][a['bufferView']]
    dtype = DTYPES[a['componentType']]
    count = a['count']
    width = COMPONENTS[a['type']]
    start = view.get('byteOffset', 0) + a.get('byteOffset', 0)
    stride = view.get('byteStride', width * dtype.itemsize)
    if stride == width * dtype.itemsize:
        return np.frombuffer(binary, dtype=dtype, count=count * width, offset=start).reshape(count, width)
    rows = [np.frombuffer(binary, dtype=dtype, count=width, offset=start + row * stride) for row in range(count)]
    return np.stack(rows)

def write_accessor(index, values):
    a = data['accessors'][index]
    view = data['bufferViews'][a['bufferView']]
    dtype = DTYPES[a['componentType']]
    width = COMPONENTS[a['type']]
    start = view.get('byteOffset', 0) + a.get('byteOffset', 0)
    stride = view.get('byteStride', width * dtype.itemsize)
    values = np.asarray(values, dtype=dtype)
    for row in range(a['count']):
        raw[binary_start + start + row * stride:binary_start + start + row * stride + width * dtype.itemsize] = values[row].tobytes()

positions = np.array(accessor(primitive['attributes']['POSITION']), dtype=np.float64)
joints = np.array(accessor(primitive['attributes']['JOINTS_0']), dtype=np.int64)
weights = np.array(accessor(primitive['attributes']['WEIGHTS_0']), dtype=np.float64)
ibm = np.array(accessor(skin['inverseBindMatrices']), dtype=np.float64).reshape(-1, 4, 4).transpose(0, 2, 1)
bone_transforms = np.linalg.inv(ibm)
bone_heads = {name: bone_transforms[index, :3, 3] for name, index in name_to_joint.items()}

def segment_distances(points, head, tail):
    ab = tail - head
    t = np.clip(((points - head) @ ab) / max(float(ab @ ab), 1e-9), 0.0, 1.0)
    closest = head + t[:, None] * ab
    return np.linalg.norm(points - closest, axis=1)

def current_side_weights(side):
    result = np.zeros(len(positions), dtype=np.float64)
    for name in ('clavicle_', 'upperarm_', 'lowerarm_', 'hand_'):
        joint = name_to_joint[name + side]
        mask = joints == joint
        result += (weights * mask).sum(axis=1)
    return result

changed = set()
for side, sign in [('r', -1.0), ('l', 1.0)]:
    x = positions[:, 0] * sign
    y = positions[:, 1]
    arm_weight = current_side_weights(side)
    candidates = np.flatnonzero(
        (x >= 0.17) & (x <= 0.745) & (y >= 1.28) & (y <= 1.60)
        & ((arm_weight > 0.08) | (x > 0.30))
    )
    points = positions[candidates]
    clavicle = bone_heads['clavicle_' + side]
    upper = bone_heads['upperarm_' + side]
    lower = bone_heads['lowerarm_' + side]
    hand = bone_heads['hand_' + side]
    finger_direction = (hand - lower) / np.linalg.norm(hand - lower)
    segments = [
        ('clavicle_' + side, clavicle, upper),
        ('upperarm_' + side, upper, lower),
        ('lowerarm_' + side, lower, hand),
        ('hand_' + side, hand, hand + finger_direction * 0.10),
    ]
    distances = np.stack([segment_distances(points, head, tail) for _, head, tail in segments], axis=1)
    influence = 1.0 / np.maximum(distances, 0.003) ** 4
    influence /= influence.sum(axis=1, keepdims=True)
    for row, vertex in enumerate(candidates):
        joints[vertex] = [name_to_joint[name] for name, _, _ in segments]
        weights[vertex] = influence[row]
        changed.add(int(vertex))
    print('ANATOMICAL_ARM', side, len(candidates), 'vertices', flush=True)

# The right inner rear shoulder contains torso surface mistakenly assigned wholly to
# upperarm_r. Copy the anatomically correct mirrored left-side binding where the source
# surface actually matches; do not touch the outer deltoid, hands, head or animation data.
left_points = positions.copy()
left_points[:, 0] *= -1.0
left_tree = cKDTree(left_points)
restored = 0
for vertex in range(len(positions)):
    p = positions[vertex]
    if not (-0.29 <= p[0] <= -0.16 and 1.28 <= p[1] <= 1.52 and p[2] < -0.02):
        continue
    distance, mirror = left_tree.query(p, k=1)
    if distance > 0.008:
        continue
    left_map = {}
    for joint, weight in zip(joints[mirror], weights[mirror]):
        if weight <= 0.0001:
            continue
        name = joint_names[int(joint)]
        mapped = name[:-2] + '_r' if name.endswith('_l') else name
        left_map[mapped] = left_map.get(mapped, 0.0) + float(weight)
    torso = sum(left_map.get(name, 0.0) for name in ('spine_02', 'spine_03', 'clavicle_r'))
    if torso < 0.35:
        continue
    ranked = sorted(left_map.items(), key=lambda item: item[1], reverse=True)[:4]
    total = sum(weight for _, weight in ranked)
    padded = ranked + [('', 0.0)] * (4 - len(ranked))
    joints[vertex] = [name_to_joint[name] if name else 0 for name, _ in padded]
    weights[vertex] = [weight / total for _, weight in padded]
    changed.add(vertex)
    restored += 1

assert len(changed) > 1000, 'No meaningful arm repair was made'
assert np.isfinite(weights).all()
assert np.max(np.abs(weights.sum(axis=1) - 1.0)) < 0.0002
assert restored > 0, 'The asymmetric rear-shoulder patch was not found'
write_accessor(primitive['attributes']['JOINTS_0'], joints)
write_accessor(primitive['attributes']['WEIGHTS_0'], weights)
PATH.write_bytes(raw)
print('RIGHT_REAR_SHOULDER_RESTORED', restored, 'vertices', flush=True)
print('DARIUS_ARM_WEIGHTS_FIXED', len(changed), 'vertices', flush=True)
print('ANIMATIONS_UNCHANGED', [a.get('name') for a in data.get('animations', [])], flush=True)
print('OUTPUT_SHA256', hashlib.sha256(raw).hexdigest(), flush=True)
