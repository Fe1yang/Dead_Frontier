import bpy, sys
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'diagnostics' / 'retarget_jian.blend'))
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
print('MESH_OBJECTS', [(o.name, len(o.data.vertices)) for o in meshes])
t = bpy.data.objects['HighDetailCharacter']
print('SHAPE_KEYS', t.data.shape_keys.key_blocks.keys() if t.data.shape_keys else None)
if t.data.shape_keys:
    for kb in t.data.shape_keys.key_blocks:
        print('KEY', kb.name, 'value', kb.value, 'mute', kb.mute)
# evaluated (depsgraph) positions vs basis
deps = bpy.context.evaluated_depsgraph_get()
te = t.evaluated_get(deps)
me = te.to_mesh()
import statistics
dz = []
for i in range(0, len(t.data.vertices), 97):
    a = t.data.vertices[i].co
    b = me.vertices[i].co
    dz.append(round((a-b).length, 4))
print('BASIS_VS_EVAL_DELTA max', max(dz), 'median', statistics.median(dz))
te.to_mesh_clear()
# world bounds from evaluated mesh
zs = [ (te.matrix_world @ v.co).z for v in me.vertices ] if False else None
# check vertex groups vs armature bone names mismatch
bones = set(b.name for b in bpy.data.objects['UniversalRig'].data.bones)
groups = set(g.name for g in t.vertex_groups)
print('GROUPS_WITHOUT_BONE', sorted(groups - bones)[:10])
print('BONES_WITHOUT_GROUP', sorted(bones - groups)[:10])
print('MODIFIERS', [(m.name, m.type) for m in t.modifiers])
print('PARENT', t.parent.name if t.parent else None, 'matrix_world', [round(v,3) for row in t.matrix_world for v in row])
