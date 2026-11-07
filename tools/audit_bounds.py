import bpy
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
name = sys.argv[sys.argv.index('--')+1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/models/generated'/name))
for m in [o for o in bpy.data.objects if o.type=='MESH']:
    print('OBJ', m.name, 'rot', tuple(round(v,2) for v in m.rotation_euler), 'scale', tuple(round(v,2) for v in m.scale))
    pts=[m.matrix_world @ v.co for v in m.data.vertices]
    lo=[min(p[i] for p in pts) for i in range(3)]; hi=[max(p[i] for p in pts) for i in range(3)]
    print('BOUNDS', [round(a,2) for a in lo], [round(a,2) for a in hi])
    xs=sorted(pts,key=lambda w:-w.x)
    print('PLUS_X_EXTREME', tuple(round(v,2) for v in xs[0]))
    print('MINUS_X_EXTREME', tuple(round(v,2) for v in xs[-1]))
