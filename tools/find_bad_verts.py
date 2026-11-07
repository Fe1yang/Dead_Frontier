import bpy
from pathlib import Path
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
bind = [mesh.matrix_world @ v.co for v in mesh.data.vertices]
# chin region in posed space
bad = [i for i,w in enumerate(posed) if -0.05<w.x<0.30 and 1.42<w.z<1.62 and w.y<-0.10]
print('CHIN_REGION_VERTS', len(bad))
from collections import Counter
agg = Counter()
examples = []
for i in bad[:4000]:
    for g in me.vertices[i].groups:
        if g.weight>0.15: agg[mesh.vertex_groups[g.group].name]+=1
    if len(examples)<6:
        tops = sorted(((g.weight, mesh.vertex_groups[g.group].name) for g in me.vertices[i].groups), reverse=True)[:3]
        examples.append((tuple(round(v,2) for v in bind[i]), tuple(round(v,2) for v in posed[i]), [(n,round(x,2)) for x,n in tops]))
print('GROUP_HISTO', agg.most_common(10))
for e in examples: print('EX bind', e[0], 'posed', e[1], e[2])
