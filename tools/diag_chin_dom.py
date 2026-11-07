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
dom = Counter(); bindmap = {}
for i,w in enumerate(posed):
    if -0.05<w.x<0.30 and 1.42<w.z<1.62 and w.y<-0.10:
        gs = me.vertices[i].groups
        if not gs: continue
        g = max(gs, key=lambda g: g.weight)
        name = mesh.vertex_groups[g.group].name
        dom[name]+=1
        if name.startswith(('hand','lowerarm','upperarm')) and len(bindmap)<8:
            bindmap[i]=(tuple(round(v,2) for v in mesh.data.vertices[i].co), tuple(round(v,2) for v in w), name, round(g.weight,2))
print('DOMINANT_IN_BOX', dom.most_common(14))
for k,v in bindmap.items(): print('STRAY bind', v[0], 'posed', v[1], v[2], v[3])
