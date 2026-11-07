import bpy
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'diagnostics' / 'retarget_jian.blend'))
t = bpy.data.objects['HighDetailCharacter']
# pure datablock stats
co = [v.co for v in t.data.vertices]
xs=[c.x for c in co]; ys=[c.y for c in co]; zs=[c.z for c in co]
print('DATABLOCK x', round(min(xs),3), round(max(xs),3), 'y', round(min(ys),3), round(max(ys),3), 'z', round(min(zs),3), round(max(zs),3))
# evaluated
deps = bpy.context.evaluated_depsgraph_get()
te = t.evaluated_get(deps)
me = te.to_mesh()
wco = [te.matrix_world @ v.co for v in me.vertices]
xs=[c.x for c in wco]; ys=[c.y for c in wco]; zs=[c.z for c in wco]
print('EVALUATED_WORLD x', round(min(xs),3), round(max(xs),3), 'y', round(min(ys),3), round(max(ys),3), 'z', round(min(zs),3), round(max(zs),3))
print('N_VERTS', len(me.vertices), len(t.data.vertices))
# how many verts above z=1.2? (legs+torso+head should be ~55%)
hi = sum(1 for c in wco if c.z > 1.2)
mid = sum(1 for c in wco if 0.6 < c.z <= 1.2)
lo = sum(1 for c in wco if c.z <= 0.6)
print('VERT_Z_BANDS hi', hi, 'mid', mid, 'lo', lo)
te.to_mesh_clear()
