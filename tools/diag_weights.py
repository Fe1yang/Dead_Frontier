import bpy, sys
from pathlib import Path
from collections import Counter
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
name = sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'survivor_riley_universal.glb'

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets'/'models'/'actors'/name))

arm = next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
mesh_obj = max((o for o in bpy.context.scene.objects if o.type=='MESH'), key=lambda o: len(o.data.vertices))
me = mesh_obj.data
mw = mesh_obj.matrix_world
inv = arm.matrix_world.inverted()
gname = [g.name for g in mesh_obj.vertex_groups]

# --- 1) armpit wedge: which bones own the gap region (left side x>0) ---
print('--- ARMPIT WEIGHTS (|n.x| inward = web) ---')
for side, sign in (('l', 1.0), ('r', -1.0)):
    buckets = Counter()
    web = Counter()
    for v in me.vertices:
        p = inv @ (mw @ v.co)
        if p.x * sign < 0.10 or p.x * sign > 0.26: continue
        if p.z < 1.22 or p.z > 1.50: continue
        dom = max(v.groups, key=lambda g: g.weight).group if v.groups else -1
        bone = gname[dom] if dom >= 0 else 'NONE'
        n = v.normal
        inward = n.x * sign < -0.25   # normal points toward the midline -> web surface
        (web if inward else buckets)[bone] += 1
    print('SIDE', side, 'OUTER(panel):', dict(buckets.most_common(5)))
    print('SIDE', side, 'INNER(web)  :', dict(web.most_common(5)))

# --- 2) collar / shoulder: verts that head/neck own outside the head ---
print('--- HEAD-OWNED VERTS OUTSIDE HEAD ---')
hb = arm.data.bones['Head']
neck = arm.data.bones['neck_01']
head_z = hb.head_local.z
bad = 0
samples = []
for v in me.vertices:
    p = inv @ (mw @ v.co)
    if p.z < neck.head_local.z: continue
    hw = sum(g.weight for g in v.groups if gname[g.group] in ('Head','neck_01'))
    if hw < 0.5: continue
    if abs(p.x) > 0.13 or p.z < head_z - 0.06:   # outside a head-sized cylinder
        bad += 1
        if len(samples) < 8: samples.append(tuple(round(c,3) for c in p))
print('HEAD_NECK_OWNED_OUTSIDE', bad, 'samples', samples)

# --- 3) hand size vs mannequin hand ---
print('--- HAND SPAN ---')
for side, sign in (('l', 1.0), ('r', -1.0)):
    wrist = arm.data.bones['hand_'+side].head_local
    xs, ys, zs = [], [], []
    for v in me.vertices:
        p = inv @ (mw @ v.co)
        if (p - wrist).length > 0.22: continue
        hw = sum(g.weight for g in v.groups if gname[g.group].startswith(('hand','index','middle','ring','pinky','thumb')))
        if hw < 0.6: continue
        xs.append(p.x); ys.append(p.y); zs.append(p.z)
    if xs:
        print('HAND', side, 'span x %.3f y %.3f z %.3f' % (max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs)), 'verts', len(xs))
# mannequin bone lengths for comparison
for b in ('hand_l','middle_01_l','middle_02_l','middle_03_l'):
    bone = arm.data.bones[b]
    print('BONE', b, 'len %.3f' % (bone.tail_local - bone.head_local).length)
