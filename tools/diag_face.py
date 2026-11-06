import bpy, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets'/'models'/'actors'/'survivor_riley_universal.glb'))
mesh = next(o for o in bpy.context.scene.objects if o.type=='MESH')
groups = mesh.vertex_groups
shown = 0
for v in mesh.data.vertices:
    p = mesh.matrix_world @ v.co
    if p.z > 1.60 and abs(p.x) < 0.10 and p.y < -0.05:  # nose/cheek front area
        ws = {groups[g.group].name: round(g.weight,3) for g in v.groups}
        print('VERT', tuple(round(c,3) for c in p), ws)
        shown += 1
        if shown >= 8: break
print('SHOWN', shown)
