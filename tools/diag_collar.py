import bpy
from pathlib import Path
from collections import Counter
ROOT = Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/models/actors/survivor_jian_universal.glb'))
mesh = max([o for o in bpy.data.objects if o.type=='MESH'], key=lambda o: len(o.data.vertices))
arm = next(o for o in bpy.data.objects if o.type=='ARMATURE')
act = bpy.data.actions.get('Run_Gun_Loop')
arm.animation_data_create(); arm.animation_data.action = act
if act.slots: arm.animation_data.action_slot = act.slots[0]
bpy.context.scene.frame_set(16); bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
ev = mesh.evaluated_get(dg); me = ev.to_mesh()
posed = [ev.matrix_world @ v.co for v in me.vertices]
import statistics
samples = {'clavicle_l':[], 'hand_l':[], 'upperarm_l':[]}
for i,w in enumerate(posed):
    if -0.05<w.x<0.30 and 1.42<w.z<1.62 and w.y<-0.10:
        gs = me.vertices[i].groups
        if not gs: continue
        g = max(gs, key=lambda g: g.weight)
        name = mesh.vertex_groups[g.group].name
        if name in samples and len(samples[name])<200:
            samples[name].append(mesh.data.vertices[i].co.copy())
for name, pts in samples.items():
    if not pts: continue
    xs=[p.x for p in pts]; ys=[p.y for p in pts]; zs=[p.z for p in pts]
    print('GROUP', name, 'n', len(pts),
          'x', round(min(xs),2), round(max(xs),2),
          'y', round(min(ys),2), round(max(ys),2),
          'z', round(min(zs),2), round(max(zs),2),
          'median', tuple(round(v,2) for v in statistics.median(pts)))
