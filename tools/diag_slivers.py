import bpy, sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
rel = sys.argv[sys.argv.index('--')+1]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/rel))

mesh_obj = max((o for o in bpy.context.scene.objects if o.type=='MESH'), key=lambda o: len(o.data.vertices))
me = mesh_obj.data
mw = mesh_obj.matrix_world
uv = me.uv_layers[0].data if me.uv_layers else None

thin = 0
tiny = 0
worst = []
for p in me.polygons:
    pts = [mw @ me.vertices[i].co for i in p.vertices]
    n = len(pts)
    if n < 3: continue
    area = p.area  # local area, scale ~1
    longest = 0.0
    for i in range(n):
        d = (pts[i] - pts[(i+1)%n]).length
        longest = max(longest, d)
    if area < 1e-7: tiny += 1
    # altitude ~ 2*area/longest
    alt = 2.0*area/max(longest, 1e-12)
    ratio = longest / max(alt, 1e-12)
    if ratio > 30:
        thin += 1
        c = sum(pts, Vector()) / n
        uvc = sum((uv[l].uv for l in p.loop_indices), Vector((0.0, 0.0))) / n if uv else Vector((0,0))
        worst.append((ratio, tuple(round(v,3) for v in c), tuple(round(v,3) for v in uvc), len(p.vertices)))

print('POLYS', len(me.polygons), 'THIN(ratio>30)', thin, 'TINY(area<1e-7)', tiny)
worst.sort(reverse=True)
for w in worst[:15]:
    print('SLIVER ratio=%.0f center=%s uvc=%s sides=%d' % w)
