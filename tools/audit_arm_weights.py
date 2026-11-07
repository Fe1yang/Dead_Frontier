import bpy
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
for name in ['survivor_male_universal.glb','survivor_jian_universal.glb','survivor_riley_universal.glb']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/models/actors'/name))
    mesh = max([o for o in bpy.data.objects if o.type=='MESH'], key=lambda o: len(o.data.vertices))
    arm = next(o for o in bpy.data.objects if o.type=='ARMATURE')
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh.evaluated_get(dg); me = ev.to_mesh()
    # world-space verts
    ws = [ev.matrix_world @ v.co for v in me.vertices]
    # find wrist candidates: extreme |x| verts in upper half
    def probe(side):
        cands = [(w, i) for i, w in enumerate(ws) if (w.x*side)>0.30 and w.z>1.15]
        if not cands: return None
        w, i = max(cands, key=lambda t: abs(t[0].x))
        tops = sorted(((g.weight, mesh.vertex_groups[g.group].name) for g in me.vertices[i].groups), reverse=True)[:3]
        return tuple(round(v,3) for v in w), [(n, round(x,2)) for x, n in tops]
    print('WEIGHTS', name)
    for side, label in [(1,'L'),(-1,'R')]:
        print('  wrist', label, probe(side))
    # shoulder area probe
    cands = [(w, i) for i, w in enumerate(ws) if 0.10 < w.x < 0.20 and 1.35 < w.z < 1.50]
    if cands:
        w, i = cands[len(cands)//2]
        tops = sorted(((g.weight, mesh.vertex_groups[g.group].name) for g in me.vertices[i].groups), reverse=True)[:3]
        print('  shoulder', tuple(round(v,3) for v in w), [(n, round(x,2)) for x, n in tops])
