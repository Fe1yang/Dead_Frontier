import bpy
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
argv = __import__('sys').argv
name = argv[argv.index('--')+1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/models/generated'/name))
mesh = max([o for o in bpy.data.objects if o.type=='MESH'], key=lambda o: len(o.data.vertices))
ws=[mesh.matrix_world @ v.co for v in mesh.data.vertices]
arm = next((o for o in bpy.data.objects if o.type=='ARMATURE'), None)
for side,sgn in [('l',1),('r',-1)]:
    cands=[w for w in ws if w.x*sgn>0.25 and w.z>1.0]
    if cands:
        w=max(cands,key=lambda w: abs(w.x))
        print('TPOSE',name,side,'extreme',tuple(round(v,3) for v in w),'count',len(cands))
if arm:
    for bn in ['upperarm_l','hand_l','upperarm_r','hand_r']:
        b=arm.data.bones.get(bn)
        if b: print('MANNEQUIN',bn,tuple(round(v,3) for v in b.head_local))
