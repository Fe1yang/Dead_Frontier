import bpy, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets'/'models'/'actors'/'survivor_riley_universal.glb'))
for o in bpy.context.scene.objects:
    print('OBJ', o.name, o.type, 'data:', o.data.name if o.data else None,
          'parent:', o.parent.name if o.parent else None,
          'scale', tuple(round(s,4) for s in o.scale),
          'hide_render', o.hide_render,
          'visible_camera', o.visible_camera if hasattr(o,'visible_camera') else '?')
    if o.type == 'MESH' and len(o.data.vertices) < 100:
        zs = [ (o.matrix_world @ v.co) for v in o.data.vertices]
        print('  world z range', min(v.z for v in zs), max(v.z for v in zs))
