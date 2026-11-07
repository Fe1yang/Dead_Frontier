import bpy
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/models/actors/survivor_jian_universal.glb'))
mesh = max([o for o in bpy.data.objects if o.type=='MESH'], key=lambda o: len(o.data.vertices))
# bind pose weights: use original mesh data (no evaluation)
arm = next(o for o in bpy.data.objects if o.type=='ARMATURE')
mw = mesh.matrix_world
ws = [mw @ v.co for v in mesh.data.vertices]
def probe(label, pred):
    idx = [i for i,w in enumerate(ws) if pred(w)]
    if not idx:
        print(label, 'NO VERTS'); return
    i = idx[len(idx)//2]
    w = ws[i]
    tops = sorted(((g.weight, mesh.vertex_groups[g.group].name) for g in mesh.data.vertices[i].groups), reverse=True)[:4]
    print(label, tuple(round(v,3) for v in w), [(n, round(x,2)) for x,n in tops])
# left hand zone in bind pose: far +x, z~1.4-1.5
probe('L-hand ', lambda w: w.x>0.50 and 1.35<w.z<1.55)
probe('L-fore ', lambda w: 0.35<w.x<0.50 and 1.42<w.z<1.52)
probe('L-upper', lambda w: 0.22<w.x<0.34 and 1.44<w.z<1.56)
probe('R-hand ', lambda w: w.x<-0.50 and 1.35<w.z<1.55)
probe('R-fore ', lambda w: -0.50<w.x<-0.35 and 1.42<w.z<1.52)
probe('face   ', lambda w: abs(w.x)<0.10 and 1.60<w.z<1.75)
